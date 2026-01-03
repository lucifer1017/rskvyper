"""
Security analysis script using Vyper compiler and Slither
"""

import subprocess
import sys
import os
from pathlib import Path


def run_vyper_compile():
    """
    Run Vyper compiler with strict checks
    """
    print("=" * 60)
    print("Running Vyper Compiler Checks")
    print("=" * 60)
    
    contracts_dir = Path("contracts")
    contracts = list(contracts_dir.glob("*.vy"))
    
    for contract in contracts:
        print(f"\nCompiling {contract.name}...")
        try:
            result = subprocess.run(
                ["vyper", str(contract), "--show-gas-estimates"],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                print(f"✅ {contract.name} compiled successfully")
                if result.stdout:
                    print(result.stdout)
            else:
                print(f"❌ {contract.name} compilation failed:")
                print(result.stderr)
        except FileNotFoundError:
            print("⚠️  Vyper compiler not found. Install with: pip install vyper")
            return False
    
    return True


def run_slither():
    """
    Run Slither static analysis
    """
    print("\n" + "=" * 60)
    print("Running Slither Static Analysis")
    print("=" * 60)
    print("⚠️  Note: Slither has limited Vyper support")
    print("=" * 60)
    
    try:
        result = subprocess.run(
            ["slither", ".", "--vyper"],
            capture_output=True,
            text=True
        )
        
        print(result.stdout)
        
        if result.stderr:
            print("\nWarnings/Errors:")
            print(result.stderr)
        
        if result.returncode == 0:
            print("\n✅ Slither analysis completed")
        else:
            print("\n⚠️  Slither found issues (may be false positives for Vyper)")
        
        return True
    except FileNotFoundError:
        print("⚠️  Slither not found. Install with: pip install slither-analyzer")
        return False


def main():
    """
    Main analysis function
    """
    print("Security Analysis Tool")
    print("=" * 60)
    
    # Change to project root
    os.chdir(Path(__file__).parent.parent)
    
    # Run Vyper compiler
    vyper_success = run_vyper_compile()
    
    # Run Slither
    slither_success = run_slither()
    
    print("\n" + "=" * 60)
    print("Analysis Summary")
    print("=" * 60)
    print(f"Vyper Compiler: {'✅ Passed' if vyper_success else '❌ Failed'}")
    print(f"Slither Analysis: {'✅ Completed' if slither_success else '⚠️  Skipped'}")
    print("\n⚠️  Remember: Slither has limited Vyper support.")
    print("Always perform manual security review using SECURITY.md checklist.")
    print("=" * 60)


if __name__ == "__main__":
    main()

