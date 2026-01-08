"""
Test suite for ERC20 token contract

Tests include:
- Basic ERC20 functionality
- Zero address validation
- increaseAllowance/decreaseAllowance functions
- Multi-user scenarios
"""

import pytest
from brownie import ERC20, accounts, reverts, ZERO_ADDRESS


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
    assert "Transfer" in tx.events
    assert tx.events["Transfer"]["sender"] == deployer
    assert tx.events["Transfer"]["receiver"] == user1
    assert tx.events["Transfer"]["value"] == amount


@pytest.mark.unit
def test_transfer_to_zero_address(token, deployer):
    """
    Test that transfer to zero address is blocked
    """
    amount = 100 * 10**18
    
    with reverts("Cannot transfer to zero address"):
        token.transfer(ZERO_ADDRESS, amount, {"from": deployer})


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
    assert "Approval" in tx.events
    assert tx.events["Approval"]["owner"] == deployer
    assert tx.events["Approval"]["spender"] == user1
    assert tx.events["Approval"]["value"] == amount


@pytest.mark.unit
def test_approve_zero_address(token, deployer):
    """
    Test that approving zero address is blocked
    """
    amount = 50 * 10**18
    
    with reverts("Cannot approve zero address"):
        token.approve(ZERO_ADDRESS, amount, {"from": deployer})


@pytest.mark.unit
def test_transferFrom(token, deployer, user1, user2):
    """
    Test transferFrom functionality with different users
    """
    amount = 75 * 10**18
    
    # Approve user1 to spend deployer's tokens
    token.approve(user1, amount, {"from": deployer})
    
    initial_balance_deployer = token.balanceOf(deployer)
    initial_balance_user2 = token.balanceOf(user2)
    
    # user1 transfers from deployer to user2
    tx = token.transferFrom(deployer, user2, amount, {"from": user1})
    
    assert token.balanceOf(deployer) == initial_balance_deployer - amount
    assert token.balanceOf(user2) == initial_balance_user2 + amount
    assert token.allowance(deployer, user1) == 0
    
    # Check event
    assert "Transfer" in tx.events
    assert tx.events["Transfer"]["sender"] == deployer
    assert tx.events["Transfer"]["receiver"] == user2
    assert tx.events["Transfer"]["value"] == amount


@pytest.mark.unit
def test_transferFrom_to_zero_address(token, deployer, user1):
    """
    Test that transferFrom to zero address is blocked
    """
    amount = 50 * 10**18
    
    token.approve(user1, amount, {"from": deployer})
    
    with reverts("Cannot transfer to zero address"):
        token.transferFrom(deployer, ZERO_ADDRESS, amount, {"from": user1})


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
def test_increase_allowance(token, deployer, user1):
    """
    Test increaseAllowance functionality
    """
    initial_allowance = 50 * 10**18
    increase_amount = 25 * 10**18
    
    # Set initial allowance
    token.approve(user1, initial_allowance, {"from": deployer})
    assert token.allowance(deployer, user1) == initial_allowance
    
    # Increase allowance
    tx = token.increaseAllowance(user1, increase_amount, {"from": deployer})
    
    expected_allowance = initial_allowance + increase_amount
    assert token.allowance(deployer, user1) == expected_allowance
    
    # Check event
    assert "Approval" in tx.events
    assert tx.events["Approval"]["value"] == expected_allowance


@pytest.mark.unit
def test_decrease_allowance(token, deployer, user1):
    """
    Test decreaseAllowance functionality
    """
    initial_allowance = 100 * 10**18
    decrease_amount = 25 * 10**18
    
    # Set initial allowance
    token.approve(user1, initial_allowance, {"from": deployer})
    assert token.allowance(deployer, user1) == initial_allowance
    
    # Decrease allowance
    tx = token.decreaseAllowance(user1, decrease_amount, {"from": deployer})
    
    expected_allowance = initial_allowance - decrease_amount
    assert token.allowance(deployer, user1) == expected_allowance
    
    # Check event
    assert "Approval" in tx.events
    assert tx.events["Approval"]["value"] == expected_allowance


@pytest.mark.unit
def test_decrease_allowance_below_zero(token, deployer, user1):
    """
    Test decreaseAllowance fails when result would be negative
    """
    initial_allowance = 50 * 10**18
    decrease_amount = 100 * 10**18  # More than allowed
    
    token.approve(user1, initial_allowance, {"from": deployer})
    
    with reverts("Decreased allowance below zero"):
        token.decreaseAllowance(user1, decrease_amount, {"from": deployer})


@pytest.mark.unit
def test_increase_allowance_zero_address(token, deployer):
    """
    Test increaseAllowance fails for zero address
    """
    with reverts("Cannot approve zero address"):
        token.increaseAllowance(ZERO_ADDRESS, 100, {"from": deployer})


@pytest.mark.unit
def test_decrease_allowance_zero_address(token, deployer):
    """
    Test decreaseAllowance fails for zero address
    """
    with reverts("Cannot approve zero address"):
        token.decreaseAllowance(ZERO_ADDRESS, 100, {"from": deployer})


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


@pytest.mark.integration
def test_multi_user_transfers(token, deployer, user1, user2, user3):
    """
    Integration test: Multi-user transfer scenarios
    """
    # Deployer sends to user1
    amount1 = 1000 * 10**18
    token.transfer(user1, amount1, {"from": deployer})
    assert token.balanceOf(user1) == amount1
    
    # User1 sends to user2
    amount2 = 500 * 10**18
    token.transfer(user2, amount2, {"from": user1})
    assert token.balanceOf(user1) == amount1 - amount2
    assert token.balanceOf(user2) == amount2
    
    # User2 approves user3, user3 transfers to user1
    amount3 = 200 * 10**18
    token.approve(user3, amount3, {"from": user2})
    token.transferFrom(user2, user1, amount3, {"from": user3})
    
    assert token.balanceOf(user2) == amount2 - amount3
    assert token.balanceOf(user1) == (amount1 - amount2) + amount3
