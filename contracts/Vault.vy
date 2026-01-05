# @version 0.3.10

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

token: public(address)
totalShares: public(uint256)
totalAssets: public(uint256)
owner: public(address)
shares: public(HashMap[address, uint256])


@external
def __init__(_token: address):
    self.token = _token
    self.owner = msg.sender
    self.totalShares = 0
    self.totalAssets = 0
    log OwnershipTransferred(empty(address), msg.sender)


@view
@external
def balanceOf(_account: address) -> uint256:
    return self.shares[_account]


@view
@external
def convertToShares(_assets: uint256) -> uint256:
    if self.totalShares == 0:
        return _assets
    return (_assets * self.totalShares) / self.totalAssets


@view
@external
def convertToAssets(_shares: uint256) -> uint256:
    if self.totalShares == 0:
        return 0
    return (_shares * self.totalAssets) / self.totalShares


@external
def deposit(_amount: uint256) -> uint256:
    assert _amount > 0, "Amount must be greater than 0"
    assert ERC20(self.token).transferFrom(msg.sender, self, _amount), "Transfer failed"
    
    shares_to_mint: uint256 = 0
    if self.totalShares == 0:
        shares_to_mint = _amount
    else:
        shares_to_mint = (_amount * self.totalShares) / self.totalAssets
    
    assert shares_to_mint > 0, "Shares calculation error"
    self.totalShares += shares_to_mint
    self.totalAssets += _amount
    self.shares[msg.sender] += shares_to_mint
    
    log Deposit(msg.sender, _amount, shares_to_mint)
    return shares_to_mint


@external
def withdraw(_shares: uint256) -> uint256:
    assert _shares > 0, "Shares must be greater than 0"
    assert self.shares[msg.sender] >= _shares, "Insufficient shares"
    
    assets_to_withdraw: uint256 = (_shares * self.totalAssets) / self.totalShares
    
    assert assets_to_withdraw > 0, "Assets calculation error"
    assert assets_to_withdraw <= self.totalAssets, "Insufficient vault balance"
    
    self.shares[msg.sender] -= _shares
    self.totalShares -= _shares
    self.totalAssets -= assets_to_withdraw
    
    assert ERC20(self.token).transfer(msg.sender, assets_to_withdraw), "Transfer failed"
    log Withdraw(msg.sender, assets_to_withdraw, _shares)
    return assets_to_withdraw


@external
def withdrawAll() -> uint256:
    user_shares: uint256 = self.shares[msg.sender]
    assert user_shares > 0, "No shares to withdraw"
    
    assets_to_withdraw: uint256 = (user_shares * self.totalAssets) / self.totalShares
    
    assert assets_to_withdraw > 0, "Assets calculation error"
    assert assets_to_withdraw <= self.totalAssets, "Insufficient vault balance"
    
    self.shares[msg.sender] -= user_shares
    self.totalShares -= user_shares
    self.totalAssets -= assets_to_withdraw
    
    assert ERC20(self.token).transfer(msg.sender, assets_to_withdraw), "Transfer failed"
    log Withdraw(msg.sender, assets_to_withdraw, user_shares)
    return assets_to_withdraw


@external
def transferOwnership(_new_owner: address):
    assert msg.sender == self.owner, "Only owner"
    assert _new_owner != empty(address), "Invalid address"
    
    previous_owner: address = self.owner
    self.owner = _new_owner
    log OwnershipTransferred(previous_owner, _new_owner)


@external
def emergencyWithdraw(_amount: uint256):
    assert msg.sender == self.owner, "Only owner"
    assert _amount > 0, "Amount must be greater than 0"
    assert ERC20(self.token).balanceOf(self) >= _amount, "Insufficient balance"
    assert ERC20(self.token).transfer(self.owner, _amount), "Transfer failed"
