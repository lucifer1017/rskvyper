"""
Pytest configuration and fixtures for Brownie tests
"""

import pytest
from brownie import accounts, ERC20, Vault, network


@pytest.fixture(scope="function", autouse=True)
def isolate(fn_isolation):
    """
    Isolate each test function to ensure clean state
    """
    pass


@pytest.fixture(scope="module")
def deployer():
    """
    Deployer account (first account)
    """
    return accounts[0]


@pytest.fixture(scope="module")
def user1():
    """
    First test user account
    """
    return accounts[1]


@pytest.fixture(scope="module")
def user2():
    """
    Second test user account
    """
    return accounts[2]


@pytest.fixture(scope="module")
def token(deployer):
    """
    Deploy ERC20 token for testing
    """
    name = "Rootstock Starter Token"
    symbol = "RST"
    decimals = 18
    initial_supply = 10_000_000 * 10**decimals  # 10 million tokens
    
    token = ERC20.deploy(name, symbol, decimals, initial_supply, {"from": deployer})
    return token


@pytest.fixture(scope="module")
def vault(deployer, token):
    """
    Deploy Vault contract for testing
    """
    vault = Vault.deploy(token.address, {"from": deployer})
    return vault


@pytest.fixture(scope="module")
def funded_user(user1, token, deployer):
    """
    User with token balance for testing
    """
    amount = 1000 * 10**18  # 1000 tokens
    token.transfer(user1, amount, {"from": deployer})
    return user1


@pytest.fixture(scope="module")
def approved_user(user1, token, vault):
    """
    User with approved token allowance for vault
    """
    amount = 1000 * 10**18  # 1000 tokens
    token.approve(vault.address, amount, {"from": user1})
    return user1

