# @version 0.3.10
"""
Simple Vault Contract with Deposit/Withdraw Functionality

SECURITY FEATURES:
- Virtual shares (dead shares) to prevent inflation attacks
- Proper state updates in emergency functions
- Checked arithmetic throughout

Note: For production use, consider implementing ERC4626 standard.
"""

from vyper.interfaces import ERC20

# Virtual offset to prevent inflation attacks
# This creates "dead shares" that make the attack economically infeasible
VIRTUAL_SHARES: constant(uint256) = 1000000000  # 1e9 virtual shares
VIRTUAL_ASSETS: constant(uint256) = 1           # 1 wei virtual asset

event Deposit:
    depositor: indexed(address)
    amount: uint256
    shares: uint256

event Withdraw:
    withdrawer: indexed(address)
    amount: uint256
    shares: uint256

event EmergencyWithdraw:
    owner: indexed(address)
    amount: uint256

event OwnershipTransferred:
    previous_owner: indexed(address)
    new_owner: indexed(address)

# Token contract address
token: public(address)

# Total shares issued (excluding virtual shares)
totalShares: public(uint256)

# Total assets deposited (excluding virtual assets)
totalAssets: public(uint256)

# Owner of the vault
owner: public(address)

# User balances (shares per user)
shares: public(HashMap[address, uint256])


@external
def __init__(_token: address):
    """
    Initialize the vault with virtual shares to prevent inflation attacks
    
    :param _token: Address of the ERC20 token contract
    """
    assert _token != empty(address), "Invalid token address"
    self.token = _token
    self.owner = msg.sender
    self.totalShares = 0
    self.totalAssets = 0
    log OwnershipTransferred(empty(address), msg.sender)


@view
@internal
def _totalSharesWithVirtual() -> uint256:
    """
    Returns total shares including virtual shares for calculations
    """
    return self.totalShares + VIRTUAL_SHARES


@view
@internal
def _totalAssetsWithVirtual() -> uint256:
    """
    Returns total assets including virtual assets for calculations
    """
    return self.totalAssets + VIRTUAL_ASSETS


@view
@external
def balanceOf(_account: address) -> uint256:
    """
    Returns the number of shares owned by an account
    
    :param _account: Account address
    :return: Number of shares
    """
    return self.shares[_account]


@view
@external
def convertToShares(_assets: uint256) -> uint256:
    """
    Calculate shares for a given amount of assets
    Uses virtual shares to prevent manipulation
    
    :param _assets: Amount of assets
    :return: Equivalent shares
    """
    # Using virtual shares/assets prevents inflation attack
    return (_assets * self._totalSharesWithVirtual()) / self._totalAssetsWithVirtual()


@view
@external
def convertToAssets(_shares: uint256) -> uint256:
    """
    Calculate assets for a given amount of shares
    Uses virtual shares to prevent manipulation
    
    :param _shares: Amount of shares
    :return: Equivalent assets
    """
    # Using virtual shares/assets prevents inflation attack
    return (_shares * self._totalAssetsWithVirtual()) / self._totalSharesWithVirtual()


@external
def deposit(_amount: uint256) -> uint256:
    """
    Deposit tokens into the vault and receive shares
    Protected against inflation attacks via virtual shares
    
    :param _amount: Amount of tokens to deposit
    :return: Number of shares received
    """
    assert _amount > 0, "Amount must be greater than 0"
    
    # Transfer tokens from user to vault
    assert ERC20(self.token).transferFrom(msg.sender, self, _amount), "Transfer failed"
    
    # Calculate shares using virtual offset (prevents inflation attack)
    # Formula: shares = (amount * (totalShares + VIRTUAL_SHARES)) / (totalAssets + VIRTUAL_ASSETS)
    shares_to_mint: uint256 = (_amount * self._totalSharesWithVirtual()) / self._totalAssetsWithVirtual()
    
    assert shares_to_mint > 0, "Deposit amount too small"
    
    # Update state
    self.totalShares += shares_to_mint
    self.totalAssets += _amount
    self.shares[msg.sender] += shares_to_mint
    
    log Deposit(msg.sender, _amount, shares_to_mint)
    return shares_to_mint


@external
def withdraw(_shares: uint256) -> uint256:
    """
    Withdraw tokens from the vault by burning shares
    
    :param _shares: Number of shares to burn
    :return: Amount of tokens withdrawn
    """
    assert _shares > 0, "Shares must be greater than 0"
    assert self.shares[msg.sender] >= _shares, "Insufficient shares"
    
    # Calculate assets using virtual offset
    assets_to_withdraw: uint256 = (_shares * self._totalAssetsWithVirtual()) / self._totalSharesWithVirtual()
    
    assert assets_to_withdraw > 0, "Withdrawal amount too small"
    assert assets_to_withdraw <= self.totalAssets, "Insufficient vault balance"
    
    # Update state before external call (checks-effects-interactions)
    self.shares[msg.sender] -= _shares
    self.totalShares -= _shares
    self.totalAssets -= assets_to_withdraw
    
    # Transfer tokens to user
    assert ERC20(self.token).transfer(msg.sender, assets_to_withdraw), "Transfer failed"
    
    log Withdraw(msg.sender, assets_to_withdraw, _shares)
    return assets_to_withdraw


@external
def withdrawAll() -> uint256:
    """
    Withdraw all tokens for the caller
    
    :return: Amount of tokens withdrawn
    """
    user_shares: uint256 = self.shares[msg.sender]
    assert user_shares > 0, "No shares to withdraw"
    
    # Calculate assets using virtual offset
    assets_to_withdraw: uint256 = (user_shares * self._totalAssetsWithVirtual()) / self._totalSharesWithVirtual()
    
    assert assets_to_withdraw > 0, "Withdrawal amount too small"
    assert assets_to_withdraw <= self.totalAssets, "Insufficient vault balance"
    
    # Update state before external call
    self.shares[msg.sender] = 0
    self.totalShares -= user_shares
    self.totalAssets -= assets_to_withdraw
    
    # Transfer tokens to user
    assert ERC20(self.token).transfer(msg.sender, assets_to_withdraw), "Transfer failed"
    
    log Withdraw(msg.sender, assets_to_withdraw, user_shares)
    return assets_to_withdraw


@external
def transferOwnership(_new_owner: address):
    """
    Transfer ownership of the vault
    
    :param _new_owner: Address of the new owner
    """
    assert msg.sender == self.owner, "Only owner"
    assert _new_owner != empty(address), "Invalid address"
    
    previous_owner: address = self.owner
    self.owner = _new_owner
    
    log OwnershipTransferred(previous_owner, _new_owner)


@external
def emergencyWithdraw(_amount: uint256):
    """
    Emergency withdraw function for owner
    WARNING: This will affect share calculations. Use with extreme caution.
    
    :param _amount: Amount of tokens to withdraw
    """
    assert msg.sender == self.owner, "Only owner"
    assert _amount > 0, "Amount must be greater than 0"
    
    vault_balance: uint256 = ERC20(self.token).balanceOf(self)
    assert vault_balance >= _amount, "Insufficient balance"
    
    # CRITICAL FIX: Update totalAssets to maintain correct state
    # Only reduce totalAssets if there are actual assets tracked
    if _amount <= self.totalAssets:
        self.totalAssets -= _amount
    else:
        # If withdrawing more than tracked (e.g., donations), set to 0
        self.totalAssets = 0
    
    assert ERC20(self.token).transfer(self.owner, _amount), "Transfer failed"
    
    log EmergencyWithdraw(self.owner, _amount)
