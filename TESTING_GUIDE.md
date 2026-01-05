# Testing Guide - Verify Project Completion

This guide will help you verify that the project is set up correctly and all components are working.

## 🚀 Quick Verification

Run the verification script to check everything at once:

```bash
python scripts/verify_setup.py
```

This will check:
- ✅ All files and directories exist
- ✅ Required tools are installed
- ✅ Python packages are available
- ✅ Project structure is correct

## 📋 Step-by-Step Testing

### Step 1: Verify Project Structure

Check that all directories and files exist:

```bash
# Check directories
ls contracts/
ls tests/
ls scripts/

# Check key files
ls brownie-config.yaml
ls requirements.txt
ls README.md
```

**Expected output:**
- `contracts/` should contain: `ERC20.vy`, `Vault.vy`
- `tests/` should contain: `conftest.py`, `test_erc20.py`, `test_vault.py`
- `scripts/` should contain: `deploy.py`, `verify.py`, `setup_networks.py`, `analyze.py`

### Step 2: Install Dependencies

```bash
# Install all Python packages
pip install -r requirements.txt
```

**Verify installation:**
```bash
# Check Brownie
brownie --version

# Check Vyper
vyper --version

# Check Pytest
pytest --version
```

**Expected:** All commands should show version numbers without errors.

### Step 3: Compile Contracts

```bash
# Compile all contracts
brownie compile
```

**Expected output:**
```
Compiling contracts...
  Vyper version: 0.3.10
  Compiling contracts/ERC20.vy...
  Compiling contracts/Vault.vy...
```

**Check for errors:**
- ✅ No compilation errors
- ✅ Build artifacts created in `build/` directory

### Step 4: Register Networks (First Time Only)

```bash
brownie networks add Ethereum rootstock-testnet host=https://public-node.testnet.rsk.co chainid=31
brownie networks add Ethereum rootstock-mainnet host=https://public-node.rsk.co chainid=30
```

Verify with:
```bash
brownie networks list
```

### Step 5: Run Tests

```bash
# Run all tests on testnet
brownie test --network rootstock-testnet
```

**Expected output:**
```
================================ test session starts ================================
tests/test_erc20.py::test_deployment PASSED
tests/test_erc20.py::test_transfer PASSED
...
tests/test_vault.py::test_vault_deployment PASSED
...
============================= X passed in Y seconds ==============================
```

**Verify:**
- ✅ All tests pass (20+ test cases)
- ✅ No test failures
- ✅ Coverage report (if using --coverage)

**Run specific test files:**
```bash
# Test only ERC20
brownie test tests/test_erc20.py --network rootstock-testnet

# Test only Vault
brownie test tests/test_vault.py --network rootstock-testnet

# Run with verbose output
brownie test -v --network rootstock-testnet
```

### Step 6: Security Analysis

```bash
# Run security analysis
python scripts/analyze.py
```

**Expected output:**
- ✅ Vyper compiler checks pass
- ✅ Slither analysis runs (with note about Vyper limitations)
- ✅ No critical security issues

### Step 7: Test Deployment (Testnet)

**⚠️ Only do this if you have testnet RBTC and want to test real deployment**

1. **Set up environment:**
   ```bash
   # Create .env file
   echo "PRIVATE_KEY=your_testnet_private_key_here" > .env
   ```

2. **Deploy to testnet:**
   ```bash
   brownie run scripts/deploy --network rootstock-testnet
   ```

3. **Verify deployment:**
   - Check `deployments/rootstock-testnet.json` for addresses
   - Verify contracts on explorer

**Expected:**
- ✅ Deployment succeeds
- ✅ Transaction confirmed on testnet
- ✅ Deployment info saved to JSON file

### Step 8: Verify Contracts (Optional)

```bash
# Run verification script
brownie run scripts/verify --network rootstock-testnet
```

**Note:** Automatic verification may require manual steps via explorer UI.

## ✅ Completion Checklist

Use this checklist to verify everything is working:

### Project Structure
- [ ] All directories exist (contracts/, tests/, scripts/)
- [ ] All contract files present (ERC20.vy, Vault.vy)
- [ ] All test files present
- [ ] All configuration files present

### Dependencies
- [ ] Python 3.8+ installed
- [ ] All packages from requirements.txt installed
- [ ] Brownie installed and working
- [ ] Vyper compiler installed
- [ ] Pytest installed

### Compilation
- [ ] Contracts compile without errors
- [ ] Build artifacts created
- [ ] No compilation warnings

### Testing
- [ ] All tests pass (20+ test cases)
- [ ] No test failures
- [ ] Test coverage is good

### Security
- [ ] Security analysis script runs
- [ ] No critical vulnerabilities
- [ ] Security checklist reviewed

### Deployment
- [ ] Networks configured correctly
- [ ] Deployment script works (tested locally)
- [ ] Verification script works

### Documentation
- [ ] README.md is complete
- [ ] MIGRATION.md is helpful
- [ ] SECURITY.md is comprehensive

## 🐛 Troubleshooting

### Issue: "Command not found: brownie"
**Solution:**
```bash
pip install eth-brownie
```

### Issue: "Vyper compiler not found"
**Solution:**
```bash
pip install vyper
```

### Issue: "Compilation errors"
**Solution:**
- Check Vyper version: `vyper --version` (should be 0.3.10)
- Verify contract syntax
- Check for typos in contract files

### Issue: "Test failures"
**Solution:**
- Run tests with verbose output: `brownie test -v`
- Check test error messages
- Verify fixtures in conftest.py

### Issue: "Network connection errors"
**Solution:**
- Check RPC endpoints in brownie-config.yaml
- Verify network is accessible
- Try alternative RPC endpoints

### Issue: "Deployment fails"
**Solution:**
- Verify PRIVATE_KEY is set in .env
- Check account has sufficient balance
- Verify network is correct

## 📊 Expected Test Results

When all tests pass, you should see:

```
tests/test_erc20.py::test_deployment PASSED
tests/test_erc20.py::test_transfer PASSED
tests/test_erc20.py::test_transfer_insufficient_balance PASSED
tests/test_erc20.py::test_approve PASSED
tests/test_erc20.py::test_transferFrom PASSED
tests/test_erc20.py::test_transferFrom_insufficient_allowance PASSED
tests/test_erc20.py::test_transferFrom_insufficient_balance PASSED
tests/test_erc20.py::test_transfer_zero_amount PASSED
tests/test_erc20.py::test_allowance_view PASSED
tests/test_erc20.py::test_total_supply PASSED
tests/test_vault.py::test_vault_deployment PASSED
tests/test_vault.py::test_first_deposit PASSED
tests/test_vault.py::test_subsequent_deposit PASSED
tests/test_vault.py::test_deposit_zero_amount PASSED
tests/test_vault.py::test_deposit_insufficient_allowance PASSED
tests/test_vault.py::test_withdraw PASSED
tests/test_vault.py::test_withdraw_all PASSED
tests/test_vault.py::test_withdraw_insufficient_shares PASSED
tests/test_vault.py::test_withdraw_zero_shares PASSED
tests/test_vault.py::test_convert_to_shares PASSED
tests/test_vault.py::test_convert_to_assets PASSED
tests/test_vault.py::test_ownership_transfer PASSED
tests/test_vault.py::test_ownership_transfer_only_owner PASSED
tests/test_vault.py::test_emergency_withdraw PASSED
tests/test_vault.py::test_emergency_withdraw_only_owner PASSED
tests/test_vault.py::test_full_workflow PASSED

============================= 25 passed in X.XXs ==============================
```

## 🎯 Success Criteria

Your project is complete and working if:

1. ✅ Verification script passes all checks
2. ✅ Contracts compile without errors
3. ✅ All tests pass (25+ test cases)
4. ✅ Security analysis runs successfully
5. ✅ Deployment script works (at least locally)
6. ✅ All documentation is present and helpful

## 🚀 Next Steps After Verification

Once everything is verified:

1. **Customize contracts** (if needed)
2. **Add more tests** (if needed)
3. **Deploy to testnet** (when ready)
4. **Get security audit** (for production)
5. **Deploy to mainnet** (after thorough testing)

---

**Happy Testing! 🧪**

