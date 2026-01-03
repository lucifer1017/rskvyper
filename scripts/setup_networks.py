"""
Setup script to register Rootstock networks with Brownie
"""

from brownie import network
import sys


def setup_networks():
    """
    Register Rootstock testnet and mainnet with Brownie
    """
    print("Setting up Rootstock networks...")
    
    try:
        # Add Rootstock Testnet
        network.add_network(
            name="rootstock-testnet",
            id="rootstock-testnet",
            host="https://public-node.testnet.rsk.co",
            chain_id=31,
            explorer="https://explorer.testnet.rsk.co/api"
        )
        print("✅ Rootstock Testnet added")
    except Exception as e:
        if "already exists" in str(e).lower():
            print("ℹ️  Rootstock Testnet already configured")
        else:
            print(f"⚠️  Error adding testnet: {e}")
    
    try:
        # Add Rootstock Mainnet
        network.add_network(
            name="rootstock-mainnet",
            id="rootstock-mainnet",
            host="https://public-node.rsk.co",
            chain_id=30,
            explorer="https://blockscout.com/rsk/mainnet/api"
        )
        print("✅ Rootstock Mainnet added")
    except Exception as e:
        if "already exists" in str(e).lower():
            print("ℹ️  Rootstock Mainnet already configured")
        else:
            print(f"⚠️  Error adding mainnet: {e}")
    
    print("\n✅ Network setup complete!")
    print("\nAvailable networks:")
    print("  - rootstock-testnet (Chain ID: 31)")
    print("  - rootstock-mainnet (Chain ID: 30)")
    print("\nNote: Networks are also configured in brownie-config.yaml")


if __name__ == "__main__":
    setup_networks()

