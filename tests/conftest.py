"""
Pytest configuration and fixtures for Brownie tests

FIXED: User fixtures now point to different accounts for proper multi-user testing
"""

import pytest
from brownie import accounts, ERC20, Vault, network, config


@pytest.fixture(scope="session", autouse=True)
def setup_accounts():
    """
    Setup accounts for non-development networks
    """
    active_network = network.show_active()
    if active_network not in ["development", "mainnet-fork", "hardhat", "hardhat-fork"]:
        if len(accounts) == 0:
            accounts.add(config["wallets"]["from_key"])


@pytest.fixture(scope="function", autouse=True)
def isolate():
    """
    Isolate each test function to ensure clean state
    """
    active_network = network.show_active()
    if active_network not in ["development", "mainnet-fork", "hardhat", "hardhat-fork"]:
        yield
        return
    from brownie.test.fixtures import fn_isolation
    yield from fn_isolation()


@pytest.fixture(scope="module")
def deployer():
    """
    Deployer account (account 0)
    """
    return accounts[0]


@pytest.fixture(scope="module")
def user1():
    """
    First test user account (account 1)
    FIXED: Now uses accounts[1] instead of accounts[0]
    """
    return accounts[1]


@pytest.fixture(scope="module")
def user2():
    """
    Second test user account (account 2)
    FIXED: Now uses accounts[2] instead of accounts[0]
    """
    return accounts[2]


@pytest.fixture(scope="module")
def user3():
    """
    Third test user account (account 3)
    """
    return accounts[3]


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


@pytest.fixture(scope="function")
def funded_user1(user1, token, deployer):
    """
    User1 with token balance for testing
    Using function scope for clean state in each test
    """
    amount = 10000 * 10**18  # 10,000 tokens
    token.transfer(user1, amount, {"from": deployer})
    return user1


@pytest.fixture(scope="function")
def funded_user2(user2, token, deployer):
    """
    User2 with token balance for testing
    """
    amount = 10000 * 10**18  # 10,000 tokens
    token.transfer(user2, amount, {"from": deployer})
    return user2


@pytest.fixture(scope="function")
def approved_vault_user1(funded_user1, token, vault):
    """
    User1 with approved token allowance for vault
    """
    amount = 10000 * 10**18
    token.approve(vault.address, amount, {"from": funded_user1})
    return funded_user1


@pytest.fixture(scope="function")
def approved_vault_user2(funded_user2, token, vault):
    """
    User2 with approved token allowance for vault
    """
    amount = 10000 * 10**18
    token.approve(vault.address, amount, {"from": funded_user2})
    return funded_user2
