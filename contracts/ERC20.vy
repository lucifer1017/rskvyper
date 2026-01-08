# @version 0.3.10
"""
Standard ERC20 Token Implementation with Security Enhancements

SECURITY FEATURES:
- Zero address validation on transfers
- increaseAllowance/decreaseAllowance to prevent front-running
- Checked arithmetic (Vyper built-in)

Based on EIP-20 Token Standard
"""

from vyper.interfaces import ERC20

implements: ERC20

event Transfer:
    sender: indexed(address)
    receiver: indexed(address)
    value: uint256

event Approval:
    owner: indexed(address)
    spender: indexed(address)
    value: uint256

name: public(String[64])
symbol: public(String[32])
decimals: public(uint8)
totalSupply: public(uint256)
balanceOf: public(HashMap[address, uint256])
allowance: public(HashMap[address, HashMap[address, uint256]])


@external
def __init__(_name: String[64], _symbol: String[32], _decimals: uint8, _initial_supply: uint256):
    """
    Initialize the ERC20 token
    
    :param _name: Token name
    :param _symbol: Token symbol
    :param _decimals: Number of decimals
    :param _initial_supply: Initial token supply (in smallest unit)
    """
    self.name = _name
    self.symbol = _symbol
    self.decimals = _decimals
    self.totalSupply = _initial_supply
    self.balanceOf[msg.sender] = _initial_supply
    
    log Transfer(empty(address), msg.sender, _initial_supply)


@external
def transfer(_to: address, _value: uint256) -> bool:
    """
    Transfer tokens to a specified address
    
    :param _to: Address to transfer to (cannot be zero address)
    :param _value: Amount of tokens to transfer
    :return: True if transfer succeeds
    """
    # SECURITY: Prevent burning tokens by sending to zero address
    assert _to != empty(address), "Cannot transfer to zero address"
    assert self.balanceOf[msg.sender] >= _value, "Insufficient balance"
    
    self.balanceOf[msg.sender] -= _value
    self.balanceOf[_to] += _value
    
    log Transfer(msg.sender, _to, _value)
    return True


@external
def transferFrom(_from: address, _to: address, _value: uint256) -> bool:
    """
    Transfer tokens from one address to another using allowance
    
    :param _from: Address to transfer from
    :param _to: Address to transfer to (cannot be zero address)
    :param _value: Amount of tokens to transfer
    :return: True if transfer succeeds
    """
    # SECURITY: Prevent burning tokens by sending to zero address
    assert _to != empty(address), "Cannot transfer to zero address"
    assert self.allowance[_from][msg.sender] >= _value, "Insufficient allowance"
    assert self.balanceOf[_from] >= _value, "Insufficient balance"
    
    self.allowance[_from][msg.sender] -= _value
    self.balanceOf[_from] -= _value
    self.balanceOf[_to] += _value
    
    log Transfer(_from, _to, _value)
    return True


@external
def approve(_spender: address, _value: uint256) -> bool:
    """
    Approve a spender to transfer tokens on behalf of the caller
    
    WARNING: This function is vulnerable to front-running attacks.
    Use increaseAllowance() and decreaseAllowance() for safer approval changes.
    
    :param _spender: Address to approve
    :param _value: Amount of tokens to approve
    :return: True if approval succeeds
    """
    # SECURITY: Prevent approving zero address
    assert _spender != empty(address), "Cannot approve zero address"
    
    self.allowance[msg.sender][_spender] = _value
    log Approval(msg.sender, _spender, _value)
    return True


@external
def increaseAllowance(_spender: address, _added_value: uint256) -> bool:
    """
    Atomically increases the allowance granted to spender by the caller
    
    This is an alternative to approve() that mitigates front-running attacks.
    
    :param _spender: Address to increase allowance for
    :param _added_value: Amount to increase allowance by
    :return: True if operation succeeds
    """
    assert _spender != empty(address), "Cannot approve zero address"
    
    new_allowance: uint256 = self.allowance[msg.sender][_spender] + _added_value
    self.allowance[msg.sender][_spender] = new_allowance
    
    log Approval(msg.sender, _spender, new_allowance)
    return True


@external
def decreaseAllowance(_spender: address, _subtracted_value: uint256) -> bool:
    """
    Atomically decreases the allowance granted to spender by the caller
    
    This is an alternative to approve() that mitigates front-running attacks.
    
    :param _spender: Address to decrease allowance for
    :param _subtracted_value: Amount to decrease allowance by
    :return: True if operation succeeds
    """
    assert _spender != empty(address), "Cannot approve zero address"
    
    current_allowance: uint256 = self.allowance[msg.sender][_spender]
    assert current_allowance >= _subtracted_value, "Decreased allowance below zero"
    
    new_allowance: uint256 = current_allowance - _subtracted_value
    self.allowance[msg.sender][_spender] = new_allowance
    
    log Approval(msg.sender, _spender, new_allowance)
    return True
