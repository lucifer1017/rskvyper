import pytest
from brownie import accounts, ERC20, Vault, network, config


@pytest.fixture(scope="session", autouse=True)
def setup_accounts():
    active_network = network.show_active()
    if active_network not in ["development", "mainnet-fork", "hardhat", "hardhat-fork"]:
        if len(accounts) == 0:
            accounts.add(config["wallets"]["from_key"])


@pytest.fixture(scope="function", autouse=True)
def isolate():
    active_network = network.show_active()
    if active_network not in ["development", "mainnet-fork", "hardhat", "hardhat-fork"]:
        yield
        return
    from brownie.test.fixtures import fn_isolation
    yield from fn_isolation()


@pytest.fixture(scope="module")
def deployer():
    return accounts[0]


@pytest.fixture(scope="module")
def user1():
    return accounts[0]


@pytest.fixture(scope="module")
def user2():
    return accounts[0]


@pytest.fixture(scope="module")
def token(deployer):
    name = "Rootstock Starter Token"
    symbol = "RST"
    decimals = 18
    initial_supply = 10_000_000 * 10**decimals
    token = ERC20.deploy(name, symbol, decimals, initial_supply, {"from": deployer})
    return token


@pytest.fixture(scope="module")
def vault(deployer, token):
    vault = Vault.deploy(token.address, {"from": deployer})
    return vault


@pytest.fixture(scope="module")
def funded_user(user1, token, deployer):
    amount = 1000 * 10**18
    token.transfer(user1, amount, {"from": deployer})
    return user1


@pytest.fixture(scope="module")
def approved_user(user1, token, vault):
    amount = 1000 * 10**18
    token.approve(vault.address, amount, {"from": user1})
    return user1
