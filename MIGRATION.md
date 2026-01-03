# Solidity → Vyper Migration Cheat Sheet

A quick reference guide for migrating Solidity code to Vyper.

## Table of Contents
- [Basic Syntax](#basic-syntax)
- [Data Types](#data-types)
- [Functions](#functions)
- [Events](#events)
- [Interfaces](#interfaces)
- [Storage & Memory](#storage--memory)
- [Common Patterns](#common-patterns)
- [Gotchas](#gotchas)

---

## Basic Syntax

### Contract Declaration

**Solidity:**
```solidity
pragma solidity ^0.8.0;

contract MyContract {
    // ...
}
```

**Vyper:**
```vyper
# @version 0.3.10

@external
def __init__():
    # ...
```

### Version Declaration

**Solidity:**
```solidity
pragma solidity ^0.8.0;
```

**Vyper:**
```vyper
# @version 0.3.10
```

---

## Data Types

### Integer Types

**Solidity:**
```solidity
uint256 amount;
uint8 decimals;
int256 signed;
```

**Vyper:**
```vyper
amount: uint256
decimals: uint8
signed: int256
```

**Key Difference:** Vyper uses `uint256` explicitly (no `uint` alias). All integers are checked for overflow/underflow by default.

### Address Type

**Solidity:**
```solidity
address owner;
address payable recipient;
```

**Vyper:**
```vyper
owner: address
recipient: address  # All addresses can receive ETH
```

**Key Difference:** In Vyper, all addresses can receive ETH (no `payable` keyword needed).

### Boolean

**Solidity:**
```solidity
bool isActive;
```

**Vyper:**
```vyper
isActive: bool
```

### String & Bytes

**Solidity:**
```solidity
string name;
bytes32 hash;
bytes data;
```

**Vyper:**
```vyper
name: String[64]  # Fixed length string
hash: bytes32
data: Bytes[100]  # Fixed length bytes
```

**Key Difference:** Vyper requires fixed-length strings and bytes arrays.

### Arrays

**Solidity:**
```solidity
uint256[] dynamicArray;
uint256[10] fixedArray;
```

**Vyper:**
```vyper
dynamicArray: DynArray[uint256, 100]  # Max length required
fixedArray: uint256[10]
```

**Key Difference:** Dynamic arrays require a maximum length in Vyper.

### Mappings

**Solidity:**
```solidity
mapping(address => uint256) balances;
mapping(address => mapping(address => uint256)) allowances;
```

**Vyper:**
```vyper
balances: HashMap[address, uint256]
allowances: HashMap[address, HashMap[address, uint256]]
```

**Key Difference:** Vyper uses `HashMap` instead of `mapping`.

---

## Functions

### Visibility

**Solidity:**
```solidity
function publicFunction() public { }
function externalFunction() external { }
function internalFunction() internal { }
function privateFunction() private { }
```

**Vyper:**
```vyper
@external
def external_function():  # Can be called from outside
    pass

@internal
def internal_function():  # Can only be called internally
    pass
```

**Key Differences:**
- Vyper has only `@external` and `@internal` (no `public`/`private`)
- `@external` functions are callable from outside
- `@internal` functions are only callable from within the contract

### State Mutability

**Solidity:**
```solidity
function viewFunction() public view returns (uint256) { }
function pureFunction() public pure returns (uint256) { }
function payableFunction() public payable { }
```

**Vyper:**
```vyper
@view
@external
def view_function() -> uint256:
    return 0

@pure
@external
def pure_function() -> uint256:
    return 0

@payable
@external
def payable_function():
    pass
```

**Key Difference:** Decorators come before `@external`/`@internal`.

### Return Values

**Solidity:**
```solidity
function getValue() public view returns (uint256) {
    return 100;
}
```

**Vyper:**
```vyper
@view
@external
def get_value() -> uint256:
    return 100
```

**Key Difference:** Return type uses `->` instead of `returns()`.

### Constructor

**Solidity:**
```solidity
constructor(uint256 _initialSupply) {
    totalSupply = _initialSupply;
}
```

**Vyper:**
```vyper
@external
def __init__(_initial_supply: uint256):
    self.totalSupply = _initial_supply
```

**Key Difference:** Constructor is `__init__` in Vyper.

---

## Events

**Solidity:**
```solidity
event Transfer(address indexed from, address indexed to, uint256 value);

function transfer(address to, uint256 value) public {
    emit Transfer(msg.sender, to, value);
}
```

**Vyper:**
```vyper
event Transfer:
    sender: indexed(address)
    receiver: indexed(address)
    value: uint256

@external
def transfer(_to: address, _value: uint256):
    log Transfer(msg.sender, _to, _value)
```

**Key Differences:**
- Events declared at contract level
- Use `log` instead of `emit`
- Indexed parameters use `indexed` keyword

---

## Interfaces

**Solidity:**
```solidity
interface IERC20 {
    function transfer(address to, uint256 amount) external returns (bool);
    function balanceOf(address account) external view returns (uint256);
}
```

**Vyper:**
```vyper
interface IERC20:
    def transfer(_to: address, _amount: uint256) -> bool: nonpayable
    def balanceOf(_account: address) -> uint256: view
```

**Key Differences:**
- Use `interface` keyword
- Functions must specify mutability (`nonpayable`, `view`, `pure`)
- Return types use `->`

### Implementing Interfaces

**Solidity:**
```solidity
contract MyToken is IERC20 {
    // ...
}
```

**Vyper:**
```vyper
from vyper.interfaces import ERC20

implements: ERC20

# Or custom interface
implements: IERC20
```

---

## Storage & Memory

### Storage Variables

**Solidity:**
```solidity
uint256 public totalSupply;
mapping(address => uint256) public balances;
```

**Vyper:**
```vyper
totalSupply: public(uint256)
balances: public(HashMap[address, uint256])
```

**Key Difference:** Use `public()` wrapper for public state variables.

### Local Variables

**Solidity:**
```solidity
function calculate() public {
    uint256 local = 100;
    // ...
}
```

**Vyper:**
```vyper
@external
def calculate():
    local: uint256 = 100
    # ...
```

**Key Difference:** Type annotation comes before variable name.

---

## Common Patterns

### SafeMath (Not Needed!)

**Solidity:**
```solidity
using SafeMath for uint256;
uint256 result = a.add(b);
```

**Vyper:**
```vyper
# Checked arithmetic is built-in!
result: uint256 = a + b  # Automatically checks overflow
```

**Key Difference:** Vyper has built-in checked arithmetic - no SafeMath needed!

### Require Statements

**Solidity:**
```solidity
require(amount > 0, "Amount must be greater than 0");
require(balance >= amount, "Insufficient balance");
```

**Vyper:**
```vyper
assert amount > 0, "Amount must be greater than 0"
assert self.balance >= amount, "Insufficient balance"
```

**Key Difference:** Use `assert` instead of `require`.

### Modifiers

**Solidity:**
```solidity
modifier onlyOwner() {
    require(msg.sender == owner, "Not owner");
    _;
}

function withdraw() public onlyOwner {
    // ...
}
```

**Vyper:**
```vyper
@internal
def only_owner():
    assert msg.sender == self.owner, "Not owner"

@external
def withdraw():
    self.only_owner()
    # ...
```

**Key Difference:** Modifiers are internal functions that must be called explicitly.

### Structs

**Solidity:**
```solidity
struct User {
    uint256 balance;
    bool active;
}

User public user;
```

**Vyper:**
```vyper
struct User:
    balance: uint256
    active: bool

user: User
```

**Key Difference:** Struct syntax uses colons instead of semicolons.

---

## Gotchas

### 1. **No Inheritance**
Vyper doesn't support inheritance. Use composition instead.

### 2. **No Assembly**
Vyper doesn't support inline assembly.

### 3. **No Modifiers**
Use internal functions instead of modifiers.

### 4. **Fixed-Length Arrays**
Dynamic arrays require a maximum length.

### 5. **No Fallback Functions**
Vyper doesn't have fallback functions (use `@payable` external functions).

### 6. **Strict Type Checking**
Vyper is stricter about types - no implicit conversions.

### 7. **No Function Overloading**
Each function must have a unique name.

### 8. **Checked Arithmetic by Default**
All arithmetic operations check for overflow/underflow automatically.

### 9. **No `this` Keyword**
Use the contract's address directly if needed.

### 10. **String Length Required**
Strings must have a fixed maximum length: `String[64]`.

---

## Quick Reference Table

| Feature | Solidity | Vyper |
|---------|----------|-------|
| Version | `pragma solidity ^0.8.0;` | `# @version 0.3.10` |
| Public var | `uint256 public x;` | `x: public(uint256)` |
| Function | `function f() public {}` | `@external\ndef f():` |
| View | `function f() public view {}` | `@view\n@external\ndef f():` |
| Constructor | `constructor() {}` | `@external\ndef __init__():` |
| Require | `require(x > 0, "msg");` | `assert x > 0, "msg"` |
| Event | `emit Transfer(a, b, c);` | `log Transfer(a, b, c)` |
| Mapping | `mapping(k => v)` | `HashMap[k, v]` |
| Interface | `interface I {}` | `interface I:\ndef f():` |
| SafeMath | `a.add(b)` | `a + b` (auto-checked) |

---

## Resources

- [Vyper Documentation](https://vyper.readthedocs.io/)
- [Vyper Examples](https://github.com/vyperlang/vyper/tree/master/examples)
- [Solidity Documentation](https://docs.soliditylang.org/)

---

**Happy Migrating! 🚀**

