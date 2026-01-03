"""
Verification script for deployed contracts on Rootstock explorer
Usage: brownie run scripts/verify --network rootstock-testnet
"""

import json
import requests
from pathlib import Path
from brownie import network, config


def load_deployment_info(network_name):
    """
    Load deployment information from file
    """
    deployment_file = Path("deployments") / f"{network_name}.json"
    
    if not deployment_file.exists():
        print(f"❌ Deployment file not found: {deployment_file}")
        print("   Please deploy contracts first using: brownie run scripts/deploy")
        return None
    
    with open(deployment_file, "r") as f:
        return json.load(f)


def get_explorer_api_url(network_name):
    """
    Get explorer API URL for the network
    """
    if network_name == "rootstock-testnet":
        return "https://explorer.testnet.rsk.co/api"
    elif network_name == "rootstock-mainnet":
        return "https://blockscout.com/rsk/mainnet/api"
    else:
        return None


def verify_contract(contract_address, contract_name, network_name):
    """
    Verify contract on Blockscout explorer
    Note: This is a placeholder - actual verification requires contract source code
    and constructor arguments to be submitted via explorer UI or API
    """
    explorer_url = get_explorer_api_url(network_name)
    
    if not explorer_url:
        print(f"⚠️  No explorer API configured for {network_name}")
        return False
    
    print(f"\n{'=' * 60}")
    print(f"Verifying {contract_name}")
    print(f"{'=' * 60}")
    print(f"Address: {contract_address}")
    print(f"Network: {network_name}")
    print(f"Explorer API: {explorer_url}")
    
    # Check if contract is already verified
    try:
        api_url = f"{explorer_url}?module=contract&action=getsourcecode&address={contract_address}"
        response = requests.get(api_url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "1" and data.get("result"):
                result = data["result"][0]
                if result.get("SourceCode"):
                    print(f"✅ Contract is already verified!")
                    print(f"   Contract Name: {result.get('ContractName', 'N/A')}")
                    return True
                else:
                    print(f"ℹ️  Contract found but not verified")
            else:
                print(f"ℹ️  Contract not found in explorer")
    except Exception as e:
        print(f"⚠️  Error checking verification status: {e}")
    
    # Provide manual verification instructions
    print(f"\n📝 Manual Verification Instructions:")
    print(f"   1. Go to the Rootstock explorer:")
    if network_name == "rootstock-testnet":
        print(f"      https://explorer.testnet.rsk.co/address/{contract_address}")
    elif network_name == "rootstock-mainnet":
        print(f"      https://blockscout.com/rsk/mainnet/address/{contract_address}")
    
    print(f"   2. Click 'Verify and Publish'")
    print(f"   3. Select:")
    print(f"      - Compiler: Vyper")
    print(f"      - Version: 0.3.10")
    print(f"      - Optimization: No")
    print(f"   4. Paste the contract source code from contracts/{contract_name}.vy")
    print(f"   5. Enter constructor arguments (if any)")
    print(f"   6. Submit for verification")
    
    return False


def main():
    """
    Main verification function
    """
    network_name = network.show_active()
    
    print("\n🔍 Contract Verification")
    print("=" * 60)
    print(f"Network: {network_name}")
    
    # Load deployment info
    deployments = load_deployment_info(network_name)
    
    if not deployments:
        return
    
    # Verify each contract
    verified_count = 0
    total_count = len(deployments)
    
    for contract_name, info in deployments.items():
        contract_address = info["address"]
        is_verified = verify_contract(contract_address, contract_name, network_name)
        if is_verified:
            verified_count += 1
    
    # Summary
    print("\n" + "=" * 60)
    print("📋 Verification Summary")
    print("=" * 60)
    print(f"Total Contracts: {total_count}")
    print(f"Verified: {verified_count}")
    print(f"Pending: {total_count - verified_count}")
    print("=" * 60)
    
    if verified_count < total_count:
        print("\n💡 Tip: Use the manual verification instructions above")
        print("   or use the explorer's API for automated verification")
    else:
        print("\n✅ All contracts verified!")

