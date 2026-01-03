"""
Test suite for ERC20 token contract
"""

import pytest
from brownie import ERC20, accounts, reverts


@pytest.mark.unit
def test_deployment(deployer):
    """
    Test ERC20 token deployment
    """
    name = "Rootstock Starter Token"
    symbol = "RST"
    decimals = 18
    initial_supply = 10_000_000 * 10**decimals
    
    token = ERC20.deploy(name, symbol, decimals, initial_supply, {"from": deployer})
    
    assert token.name() == name
    assert token.symbol() == symbol
    assert token.decimals() == decimals
    assert token.totalSupply() == initial_supply
    assert token.balanceOf(deployer) == initial_supply


@pytest.mark.unit
def test_transfer(token, deployer, user1):
    """
    Test token transfer functionality
    """
    amount = 100 * 10**18  # 100 tokens
    
    initial_balance_deployer = token.balanceOf(deployer)
    initial_balance_user1 = token.balanceOf(user1)
    
    tx = token.transfer(user1, amount, {"from": deployer})
    
    assert token.balanceOf(deployer) == initial_balance_deployer - amount
    assert token.balanceOf(user1) == initial_balance_user1 + amount
    
    # Check event
    assert len(tx.events) == 1
    assert tx.events["Transfer"]["sender"] == deployer
    assert tx.events["Transfer"]["receiver"] == user1
    assert tx.events["Transfer"]["value"] == amount


@pytest.mark.unit
def test_transfer_insufficient_balance(token, user1, user2):
    """
    Test transfer with insufficient balance
    """
    amount = 100 * 10**18
    user1_balance = token.balanceOf(user1)
    
    with reverts("Insufficient balance"):
        token.transfer(user2, user1_balance + 1, {"from": user1})


@pytest.mark.unit
def test_approve(token, deployer, user1):
    """
    Test approve functionality
    """
    amount = 50 * 10**18
    
    tx = token.approve(user1, amount, {"from": deployer})
    
    assert token.allowance(deployer, user1) == amount
    
    # Check event
    assert len(tx.events) == 1
    assert tx.events["Approval"]["owner"] == deployer
    assert tx.events["Approval"]["spender"] == user1
    assert tx.events["Approval"]["value"] == amount


@pytest.mark.unit
def test_transferFrom(token, deployer, user1, user2):
    """
    Test transferFrom functionality
    """
    amount = 75 * 10**18
    
    # Approve first
    token.approve(user1, amount, {"from": deployer})
    
    initial_balance_deployer = token.balanceOf(deployer)
    initial_balance_user2 = token.balanceOf(user2)
    
    tx = token.transferFrom(deployer, user2, amount, {"from": user1})
    
    assert token.balanceOf(deployer) == initial_balance_deployer - amount
    assert token.balanceOf(user2) == initial_balance_user2 + amount
    assert token.allowance(deployer, user1) == 0
    
    # Check event
    assert len(tx.events) == 1
    assert tx.events["Transfer"]["sender"] == deployer
    assert tx.events["Transfer"]["receiver"] == user2
    assert tx.events["Transfer"]["value"] == amount


@pytest.mark.unit
def test_transferFrom_insufficient_allowance(token, deployer, user1, user2):
    """
    Test transferFrom with insufficient allowance
    """
    amount = 50 * 10**18
    approved_amount = 25 * 10**18
    
    token.approve(user1, approved_amount, {"from": deployer})
    
    with reverts("Insufficient allowance"):
        token.transferFrom(deployer, user2, amount, {"from": user1})


@pytest.mark.unit
def test_transferFrom_insufficient_balance(token, deployer, user1, user2):
    """
    Test transferFrom with insufficient balance
    """
    deployer_balance = token.balanceOf(deployer)
    amount = deployer_balance + 1
    
    token.approve(user1, amount, {"from": deployer})
    
    with reverts("Insufficient balance"):
        token.transferFrom(deployer, user2, amount, {"from": user1})


@pytest.mark.unit
def test_transfer_zero_amount(token, deployer, user1):
    """
    Test transfer with zero amount
    """
    initial_balance = token.balanceOf(user1)
    
    token.transfer(user1, 0, {"from": deployer})
    
    assert token.balanceOf(user1) == initial_balance


@pytest.mark.unit
def test_allowance_view(token, deployer, user1):
    """
    Test allowance view function
    """
    amount = 100 * 10**18
    
    assert token.allowance(deployer, user1) == 0
    
    token.approve(user1, amount, {"from": deployer})
    
    assert token.allowance(deployer, user1) == amount


@pytest.mark.unit
def test_total_supply(token):
    """
    Test total supply view function
    """
    total_supply = token.totalSupply()
    assert total_supply > 0
    assert total_supply == 10_000_000 * 10**18

