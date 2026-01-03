# @version 0.3.10
"""
Standard ERC20 Token Implementation with Checked Arithmetic
Based on EIP-20 Token Standard

This implementation uses Vyper's built-in checked arithmetic which automatically
prevents overflow/underflow without needing SafeMath libraries.
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


@view
@external
def total_supply() -> uint256:
    """
    Returns the total token supply
    """
    return self.totalSupply


@view
@external
def balance_of(_owner: address) -> uint256:
    """
    Returns the balance of the specified address
    
    :param _owner: Address to query balance for
    """
    return self.balanceOf[_owner]


@external
def transfer(_to: address, _value: uint256) -> bool:
    """
    Transfer tokens to a specified address
    
    :param _to: Address to transfer to
    :param _value: Amount of tokens to transfer
    :return: True if transfer succeeds
    """
    # Checked arithmetic: Vyper automatically checks for underflow
    # This assert ensures sender has enough balance
    assert self.balanceOf[msg.sender] >= _value, "Insufficient balance"
    
    # Checked arithmetic: Vyper prevents overflow/underflow automatically
    self.balanceOf[msg.sender] -= _value
    self.balanceOf[_to] += _value
    
    log Transfer(msg.sender, _to, _value)
    return True


@external
def transferFrom(_from: address, _to: address, _value: uint256) -> bool:
    """
    Transfer tokens from one address to another using allowance
    
    :param _from: Address to transfer from
    :param _to: Address to transfer to
    :param _value: Amount of tokens to transfer
    :return: True if transfer succeeds
    """
    # Checked arithmetic: ensure sufficient allowance
    assert self.allowance[_from][msg.sender] >= _value, "Insufficient allowance"
    # Checked arithmetic: ensure sender has enough balance
    assert self.balanceOf[_from] >= _value, "Insufficient balance"
    
    # Checked arithmetic: prevent overflow/underflow
    self.allowance[_from][msg.sender] -= _value
    self.balanceOf[_from] -= _value
    self.balanceOf[_to] += _value
    
    log Transfer(_from, _to, _value)
    return True


@external
def approve(_spender: address, _value: uint256) -> bool:
    """
    Approve a spender to transfer tokens on behalf of the caller
    
    :param _spender: Address to approve
    :param _value: Amount of tokens to approve
    :return: True if approval succeeds
    """
    self.allowance[msg.sender][_spender] = _value
    log Approval(msg.sender, _spender, _value)
    return True


@view
@external
def allowance(_owner: address, _spender: address) -> uint256:
    """
    Returns the amount of tokens that a spender is allowed to transfer
    
    :param _owner: Token owner address
    :param _spender: Spender address
    :return: Allowance amount
    """
    return self.allowance[_owner][_spender]

