"""
Test suite for Vault contract

Tests include:
- Basic deposit/withdraw functionality
- Virtual shares inflation attack protection
- Emergency withdraw state updates
- Multi-user scenarios
"""

import pytest
from brownie import Vault, ERC20, accounts, reverts

# Virtual shares constants (must match contract)
VIRTUAL_SHARES = 1000000000  # 1e9
VIRTUAL_ASSETS = 1  # 1 wei


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
def test_first_deposit(vault, token, approved_vault_user1):
    """
    Test first deposit with virtual shares
    """
    amount = 100 * 10**18
    
    initial_balance = token.balanceOf(approved_vault_user1)
    initial_vault_balance = token.balanceOf(vault.address)
    
    tx = vault.deposit(amount, {"from": approved_vault_user1})
    
    # Token transfer succeeded
    assert token.balanceOf(approved_vault_user1) == initial_balance - amount
    assert token.balanceOf(vault.address) == initial_vault_balance + amount
    
    # Shares calculated with virtual offset
    # shares = (amount * (0 + VIRTUAL_SHARES)) / (0 + VIRTUAL_ASSETS)
    expected_shares = (amount * VIRTUAL_SHARES) // VIRTUAL_ASSETS
    assert vault.shares(approved_vault_user1) == expected_shares
    assert vault.totalShares() == expected_shares
    assert vault.totalAssets() == amount
    
    # Check event
    assert "Deposit" in tx.events
    assert tx.events["Deposit"]["depositor"] == approved_vault_user1
    assert tx.events["Deposit"]["amount"] == amount


@pytest.mark.unit
def test_subsequent_deposit_multi_user(vault, token, deployer, approved_vault_user1, approved_vault_user2):
    """
    Test deposit after initial deposit with different users
    """
    # First deposit by user1
    amount1 = 100 * 10**18
    vault.deposit(amount1, {"from": approved_vault_user1})
    
    shares_after_first = vault.totalShares()
    assets_after_first = vault.totalAssets()
    
    # Second deposit by user2
    amount2 = 50 * 10**18
    vault.deposit(amount2, {"from": approved_vault_user2})
    
    # User2 should receive proportional shares with virtual offset
    expected_shares = (amount2 * (shares_after_first + VIRTUAL_SHARES)) // (assets_after_first + VIRTUAL_ASSETS)
    assert vault.shares(approved_vault_user2) == expected_shares
    
    # Total should be updated
    assert vault.totalShares() == shares_after_first + expected_shares
    assert vault.totalAssets() == assets_after_first + amount2


@pytest.mark.unit
def test_deposit_zero_amount(vault, approved_vault_user1):
    """
    Test deposit with zero amount
    """
    with reverts("Amount must be greater than 0"):
        vault.deposit(0, {"from": approved_vault_user1})


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
def test_withdraw(vault, token, approved_vault_user1):
    """
    Test withdraw functionality
    """
    # First deposit
    deposit_amount = 100 * 10**18
    vault.deposit(deposit_amount, {"from": approved_vault_user1})
    
    shares = vault.shares(approved_vault_user1)
    initial_balance = token.balanceOf(approved_vault_user1)
    initial_vault_balance = token.balanceOf(vault.address)
    
    # Withdraw half of shares
    withdraw_shares = shares // 2
    tx = vault.withdraw(withdraw_shares, {"from": approved_vault_user1})
    
    assert vault.shares(approved_vault_user1) == shares - withdraw_shares
    assert token.balanceOf(approved_vault_user1) > initial_balance
    assert token.balanceOf(vault.address) < initial_vault_balance
    
    # Check event
    assert "Withdraw" in tx.events
    assert tx.events["Withdraw"]["withdrawer"] == approved_vault_user1
    assert tx.events["Withdraw"]["shares"] == withdraw_shares


@pytest.mark.unit
def test_withdraw_all(vault, token, approved_vault_user1):
    """
    Test withdrawAll functionality
    """
    # Deposit
    deposit_amount = 100 * 10**18
    vault.deposit(deposit_amount, {"from": approved_vault_user1})
    
    shares = vault.shares(approved_vault_user1)
    assert shares > 0
    
    initial_balance = token.balanceOf(approved_vault_user1)
    
    # Withdraw all
    tx = vault.withdrawAll({"from": approved_vault_user1})
    
    assert vault.shares(approved_vault_user1) == 0
    assert vault.totalShares() == 0
    assert vault.totalAssets() == 0
    assert token.balanceOf(approved_vault_user1) > initial_balance


@pytest.mark.unit
def test_withdraw_insufficient_shares(vault, user1):
    """
    Test withdraw with insufficient shares
    """
    with reverts("Insufficient shares"):
        vault.withdraw(1, {"from": user1})


@pytest.mark.unit
def test_withdraw_zero_shares(vault, approved_vault_user1):
    """
    Test withdraw with zero shares
    """
    with reverts("Shares must be greater than 0"):
        vault.withdraw(0, {"from": approved_vault_user1})


@pytest.mark.unit
def test_convert_to_shares(vault, token, approved_vault_user1):
    """
    Test convertToShares function with virtual offset
    """
    # Before any deposits, uses virtual offset
    test_amount = 100 * 10**18
    expected_before = (test_amount * VIRTUAL_SHARES) // VIRTUAL_ASSETS
    assert vault.convertToShares(test_amount) == expected_before
    
    # After deposit
    deposit_amount = 100 * 10**18
    vault.deposit(deposit_amount, {"from": approved_vault_user1})
    
    # Should calculate with virtual offset
    assets = 50 * 10**18
    total_shares_with_virtual = vault.totalShares() + VIRTUAL_SHARES
    total_assets_with_virtual = vault.totalAssets() + VIRTUAL_ASSETS
    expected_shares = (assets * total_shares_with_virtual) // total_assets_with_virtual
    assert vault.convertToShares(assets) == expected_shares


@pytest.mark.unit
def test_convert_to_assets(vault, token, approved_vault_user1):
    """
    Test convertToAssets function with virtual offset
    """
    # Before any deposits
    test_shares = 100 * 10**18
    expected_before = (test_shares * VIRTUAL_ASSETS) // VIRTUAL_SHARES
    assert vault.convertToAssets(test_shares) == expected_before
    
    # After deposit
    deposit_amount = 100 * 10**18
    vault.deposit(deposit_amount, {"from": approved_vault_user1})
    
    shares = vault.shares(approved_vault_user1)
    total_shares_with_virtual = vault.totalShares() + VIRTUAL_SHARES
    total_assets_with_virtual = vault.totalAssets() + VIRTUAL_ASSETS
    expected_assets = (shares * total_assets_with_virtual) // total_shares_with_virtual
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
    assert "OwnershipTransferred" in tx.events
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
def test_emergency_withdraw_updates_state(vault, token, deployer, approved_vault_user1):
    """
    Test emergency withdraw properly updates totalAssets
    """
    # Deposit some tokens
    deposit_amount = 100 * 10**18
    vault.deposit(deposit_amount, {"from": approved_vault_user1})
    
    initial_total_assets = vault.totalAssets()
    vault_balance = token.balanceOf(vault.address)
    owner_balance = token.balanceOf(deployer)
    
    emergency_amount = 50 * 10**18
    tx = vault.emergencyWithdraw(emergency_amount, {"from": deployer})
    
    # Token balances updated
    assert token.balanceOf(vault.address) == vault_balance - emergency_amount
    assert token.balanceOf(deployer) == owner_balance + emergency_amount
    
    # CRITICAL: totalAssets should be updated
    assert vault.totalAssets() == initial_total_assets - emergency_amount
    
    # Check event
    assert "EmergencyWithdraw" in tx.events


@pytest.mark.unit
def test_emergency_withdraw_only_owner(vault, user1):
    """
    Test emergency withdraw by non-owner
    """
    with reverts("Only owner"):
        vault.emergencyWithdraw(1, {"from": user1})


@pytest.mark.integration
def test_inflation_attack_protection(vault, token, deployer, user1, user2):
    """
    Test that vault is protected against inflation attacks
    
    Attack scenario (without protection):
    1. Attacker deposits 1 wei
    2. Attacker sends large amount directly to contract
    3. Victim deposits, gets 0 shares due to rounding
    4. Attacker withdraws all
    
    With virtual shares, this attack is not profitable
    """
    # Setup attacker (user1) and victim (user2)
    attacker = user1
    victim = user2
    
    attacker_amount = 1000 * 10**18
    victim_amount = 100 * 10**18
    
    token.transfer(attacker, attacker_amount, {"from": deployer})
    token.transfer(victim, victim_amount, {"from": deployer})
    
    token.approve(vault.address, attacker_amount, {"from": attacker})
    token.approve(vault.address, victim_amount, {"from": victim})
    
    # Attacker makes first deposit of 1 wei
    vault.deposit(1, {"from": attacker})
    attacker_shares_initial = vault.shares(attacker)
    
    # Attacker sends tokens directly to vault (donation)
    donation_amount = 1000 * 10**18 - 1
    token.transfer(vault.address, donation_amount, {"from": attacker})
    
    # Victim deposits - with virtual shares, they should still get meaningful shares
    vault.deposit(victim_amount, {"from": victim})
    victim_shares = vault.shares(victim)
    
    # CRITICAL: Victim should have received shares (> 0)
    assert victim_shares > 0, "Victim should receive shares due to virtual share protection"
    
    # Victim should be able to withdraw their funds
    vault.withdrawAll({"from": victim})
    victim_final_balance = token.balanceOf(victim)
    
    # Victim should recover most of their deposit
    # (may lose small amount due to attacker's donation, but not everything)
    assert victim_final_balance > 0, "Victim should recover funds"


@pytest.mark.integration
def test_full_workflow_multi_user(vault, token, deployer, user1, user2):
    """
    Integration test: Full deposit/withdraw workflow with multiple users
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
    user1_shares = vault.shares(user1)
    assert user1_shares > 0
    
    # User2 deposits
    vault.deposit(amount2, {"from": user2})
    user2_shares = vault.shares(user2)
    assert user2_shares > 0
    
    # Both users have different share amounts
    assert user1_shares != user2_shares
    
    # User1 withdraws half
    vault.withdraw(user1_shares // 2, {"from": user1})
    assert vault.shares(user1) > 0
    
    # User2 withdraws all
    vault.withdrawAll({"from": user2})
    assert vault.shares(user2) == 0
    
    # User1 still has shares and assets remain
    assert vault.totalAssets() > 0
    assert vault.totalShares() > 0
