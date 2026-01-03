"""
Test suite for Vault contract
"""

import pytest
from brownie import Vault, accounts, reverts


@pytest.mark.unit
def test_vault_deployment(vault, token, deployer):
    """
    Test vault deployment
    """
    assert vault.token() == token.address
    assert vault.owner() == deployer
    assert vault.totalShares() == 0
    assert vault.totalAssets() == 0


@pytest.mark.unit
def test_first_deposit(vault, token, funded_user, approved_user):
    """
    Test first deposit (1:1 share ratio)
    """
    amount = 100 * 10**18
    
    initial_balance = token.balanceOf(funded_user)
    initial_vault_balance = token.balanceOf(vault.address)
    
    tx = vault.deposit(amount, {"from": funded_user})
    
    assert token.balanceOf(funded_user) == initial_balance - amount
    assert token.balanceOf(vault.address) == initial_vault_balance + amount
    assert vault.shares(funded_user) == amount
    assert vault.totalShares() == amount
    assert vault.totalAssets() == amount
    
    # Check event
    assert len(tx.events) == 1
    assert tx.events["Deposit"]["depositor"] == funded_user
    assert tx.events["Deposit"]["amount"] == amount
    assert tx.events["Deposit"]["shares"] == amount


@pytest.mark.unit
def test_subsequent_deposit(vault, token, deployer, user1, user2):
    """
    Test deposit after initial deposit (proportional shares)
    """
    # First deposit by user1
    amount1 = 100 * 10**18
    token.transfer(user1, amount1 * 2, {"from": deployer})
    token.approve(vault.address, amount1 * 2, {"from": user1})
    
    vault.deposit(amount1, {"from": user1})
    
    # Second deposit by user2
    amount2 = 50 * 10**18
    token.transfer(user2, amount2, {"from": deployer})
    token.approve(vault.address, amount2, {"from": user2})
    
    shares_before = vault.totalShares()
    assets_before = vault.totalAssets()
    
    tx = vault.deposit(amount2, {"from": user2})
    
    # User2 should receive proportional shares
    expected_shares = (amount2 * shares_before) / assets_before
    assert vault.shares(user2) == expected_shares
    assert vault.totalShares() == shares_before + expected_shares
    assert vault.totalAssets() == assets_before + amount2


@pytest.mark.unit
def test_deposit_zero_amount(vault, funded_user):
    """
    Test deposit with zero amount
    """
    with reverts("Amount must be greater than 0"):
        vault.deposit(0, {"from": funded_user})


@pytest.mark.unit
def test_deposit_insufficient_allowance(vault, token, user1, deployer):
    """
    Test deposit without approval
    """
    amount = 100 * 10**18
    token.transfer(user1, amount, {"from": deployer})
    # Don't approve
    
    with reverts():
        vault.deposit(amount, {"from": user1})


@pytest.mark.unit
def test_withdraw(vault, token, funded_user, approved_user):
    """
    Test withdraw functionality
    """
    # First deposit
    deposit_amount = 100 * 10**18
    vault.deposit(deposit_amount, {"from": funded_user})
    
    shares = vault.shares(funded_user)
    initial_balance = token.balanceOf(funded_user)
    initial_vault_balance = token.balanceOf(vault.address)
    
    # Withdraw half
    withdraw_shares = shares / 2
    tx = vault.withdraw(withdraw_shares, {"from": funded_user})
    
    assert vault.shares(funded_user) == shares - withdraw_shares
    assert token.balanceOf(funded_user) > initial_balance
    assert token.balanceOf(vault.address) < initial_vault_balance
    
    # Check event
    assert len(tx.events) == 1
    assert tx.events["Withdraw"]["withdrawer"] == funded_user
    assert tx.events["Withdraw"]["shares"] == withdraw_shares


@pytest.mark.unit
def test_withdraw_all(vault, token, funded_user, approved_user):
    """
    Test withdrawAll functionality
    """
    # Deposit
    deposit_amount = 100 * 10**18
    vault.deposit(deposit_amount, {"from": funded_user})
    
    shares = vault.shares(funded_user)
    assert shares > 0
    
    # Withdraw all
    tx = vault.withdrawAll({"from": funded_user})
    
    assert vault.shares(funded_user) == 0
    assert vault.totalShares() == 0
    assert vault.totalAssets() == 0


@pytest.mark.unit
def test_withdraw_insufficient_shares(vault, token, user1):
    """
    Test withdraw with insufficient shares
    """
    with reverts("Insufficient shares"):
        vault.withdraw(1, {"from": user1})


@pytest.mark.unit
def test_withdraw_zero_shares(vault, funded_user):
    """
    Test withdraw with zero shares
    """
    with reverts("Shares must be greater than 0"):
        vault.withdraw(0, {"from": funded_user})


@pytest.mark.unit
def test_convert_to_shares(vault, token, funded_user, approved_user):
    """
    Test convertToShares function
    """
    # Before any deposits
    assert vault.convertToShares(100 * 10**18) == 100 * 10**18
    
    # After deposit
    deposit_amount = 100 * 10**18
    vault.deposit(deposit_amount, {"from": funded_user})
    
    # Should calculate proportional shares
    assets = 50 * 10**18
    expected_shares = (assets * vault.totalShares()) / vault.totalAssets()
    assert vault.convertToShares(assets) == expected_shares


@pytest.mark.unit
def test_convert_to_assets(vault, token, funded_user, approved_user):
    """
    Test convertToAssets function
    """
    # Before any deposits
    assert vault.convertToAssets(100 * 10**18) == 0
    
    # After deposit
    deposit_amount = 100 * 10**18
    vault.deposit(deposit_amount, {"from": funded_user})
    
    shares = vault.shares(funded_user)
    expected_assets = (shares * vault.totalAssets()) / vault.totalShares()
    assert vault.convertToAssets(shares) == expected_assets


@pytest.mark.unit
def test_ownership_transfer(vault, deployer, user1):
    """
    Test ownership transfer
    """
    assert vault.owner() == deployer
    
    tx = vault.transferOwnership(user1, {"from": deployer})
    
    assert vault.owner() == user1
    
    # Check event
    assert len(tx.events) == 1
    assert tx.events["OwnershipTransferred"]["previous_owner"] == deployer
    assert tx.events["OwnershipTransferred"]["new_owner"] == user1


@pytest.mark.unit
def test_ownership_transfer_only_owner(vault, user1, user2):
    """
    Test ownership transfer by non-owner
    """
    with reverts("Only owner"):
        vault.transferOwnership(user2, {"from": user1})


@pytest.mark.unit
def test_emergency_withdraw(vault, token, deployer, funded_user, approved_user):
    """
    Test emergency withdraw by owner
    """
    # Deposit some tokens
    deposit_amount = 100 * 10**18
    vault.deposit(deposit_amount, {"from": funded_user})
    
    vault_balance = token.balanceOf(vault.address)
    owner_balance = token.balanceOf(deployer)
    
    emergency_amount = 50 * 10**18
    vault.emergencyWithdraw(emergency_amount, {"from": deployer})
    
    assert token.balanceOf(vault.address) == vault_balance - emergency_amount
    assert token.balanceOf(deployer) == owner_balance + emergency_amount


@pytest.mark.unit
def test_emergency_withdraw_only_owner(vault, token, user1):
    """
    Test emergency withdraw by non-owner
    """
    with reverts("Only owner"):
        vault.emergencyWithdraw(1, {"from": user1})


@pytest.mark.integration
def test_full_workflow(vault, token, deployer, user1, user2):
    """
    Integration test: Full deposit/withdraw workflow
    """
    # Setup: Fund users
    amount1 = 1000 * 10**18
    amount2 = 500 * 10**18
    
    token.transfer(user1, amount1, {"from": deployer})
    token.transfer(user2, amount2, {"from": deployer})
    
    token.approve(vault.address, amount1, {"from": user1})
    token.approve(vault.address, amount2, {"from": user2})
    
    # User1 deposits
    vault.deposit(amount1, {"from": user1})
    assert vault.shares(user1) == amount1
    
    # User2 deposits
    vault.deposit(amount2, {"from": user2})
    assert vault.shares(user2) > 0
    
    # User1 withdraws half
    user1_shares = vault.shares(user1)
    vault.withdraw(user1_shares / 2, {"from": user1})
    
    # User2 withdraws all
    vault.withdrawAll({"from": user2})
    assert vault.shares(user2) == 0
    
    # Final state
    assert vault.totalAssets() > 0
    assert vault.totalShares() > 0

