# @version 0.3.10
"""
Simple Vault Contract with Deposit/Withdraw Functionality

Users can deposit ERC20 tokens and receive shares proportional to their deposit.
Shares can be redeemed for underlying tokens at any time.

Note: For production use, consider implementing ERC4626 standard for tokenized vaults.
"""

from vyper.interfaces import ERC20

event Deposit:
    depositor: indexed(address)
    amount: uint256
    shares: uint256

event Withdraw:
    withdrawer: indexed(address)
    amount: uint256
    shares: uint256

event OwnershipTransferred:
    previous_owner: indexed(address)
    new_owner: indexed(address)

# Token contract address
token: public(address)

# Total shares issued
totalShares: public(uint256)

# Total tokens deposited
totalAssets: public(uint256)

# Owner of the vault
owner: public(address)

# User balances (shares per user)
shares: public(HashMap[address, uint256])


@external
def __init__(_token: address):
    """
    Initialize the vault
    
    :param _token: Address of the ERC20 token contract
    """
    self.token = _token
    self.owner = msg.sender
    self.totalShares = 0
    self.totalAssets = 0
    
    log OwnershipTransferred(empty(address), msg.sender)


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
def totalAssets() -> uint256:
    """
    Returns the total amount of tokens deposited in the vault
    
    :return: Total assets
    """
    return self.totalAssets


@view
@external
def convertToShares(_assets: uint256) -> uint256:
    """
    Calculate shares for a given amount of assets
    
    :param _assets: Amount of assets
    :return: Equivalent shares
    """
    if self.totalShares == 0:
        return _assets
    # Checked arithmetic: Vyper prevents overflow
    return (_assets * self.totalShares) / self.totalAssets


@view
@external
def convertToAssets(_shares: uint256) -> uint256:
    """
    Calculate assets for a given amount of shares
    
    :param _shares: Amount of shares
    :return: Equivalent assets
    """
    if self.totalShares == 0:
        return 0
    # Checked arithmetic: Vyper prevents overflow
    return (_shares * self.totalAssets) / self.totalShares


@external
def deposit(_amount: uint256) -> uint256:
    """
    Deposit tokens into the vault and receive shares
    
    :param _amount: Amount of tokens to deposit
    :return: Number of shares received
    """
    assert _amount > 0, "Amount must be greater than 0"
    
    # Transfer tokens from user to vault
    # Checked arithmetic: transferFrom will revert if insufficient balance/allowance
    assert ERC20(self.token).transferFrom(msg.sender, self, _amount), "Transfer failed"
    
    # Calculate shares to mint
    shares_to_mint: uint256 = 0
    if self.totalShares == 0:
        # First deposit: 1:1 ratio
        shares_to_mint = _amount
    else:
        # Checked arithmetic: Vyper prevents overflow
        shares_to_mint = (_amount * self.totalShares) / self.totalAssets
    
    assert shares_to_mint > 0, "Shares calculation error"
    
    # Update state with checked arithmetic
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
    
    # Calculate assets to withdraw
    # Checked arithmetic: Vyper prevents overflow
    assets_to_withdraw: uint256 = (_shares * self.totalAssets) / self.totalShares
    
    assert assets_to_withdraw > 0, "Assets calculation error"
    assert assets_to_withdraw <= self.totalAssets, "Insufficient vault balance"
    
    # Update state with checked arithmetic
    self.shares[msg.sender] -= _shares
    self.totalShares -= _shares
    self.totalAssets -= assets_to_withdraw
    
    # Transfer tokens to user
    # Checked arithmetic: transfer will revert if vault has insufficient balance
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
    return self.withdraw(user_shares)


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
    Emergency withdraw function for owner (use with caution)
    
    :param _amount: Amount of tokens to withdraw
    """
    assert msg.sender == self.owner, "Only owner"
    assert _amount > 0, "Amount must be greater than 0"
    
    # Checked arithmetic: ensure vault has enough balance
    assert ERC20(self.token).balanceOf(self) >= _amount, "Insufficient balance"
    
    assert ERC20(self.token).transfer(self.owner, _amount), "Transfer failed"

