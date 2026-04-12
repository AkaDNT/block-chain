# Stock Market Blockchain - Smart Contracts Documentation

This document provides a comprehensive overview of all smart contracts in the Stock Market Blockchain system. All contracts are written in **Vyper 0.4.3**.

---

## Table of Contents

1. [System Overview](#system-overview)
2. [Token Contracts](#token-contracts)
   - [BaseToken](#basetoken)
   - [StockToken](#stocktoken)
3. [Trading Contracts](#trading-contracts)
   - [StockAMM](#stockamm)
   - [AMMFactory](#ammfactory)
4. [Registry Contracts](#registry-contracts)
   - [Registry](#registry)
   - [TraderRegistry](#traderregistry)
   - [MinterRegistry](#minterregistry)
   - [EncryptedDocRegistry](#encrypteddocregistry)
5. [Utility Contracts](#utility-contracts)
   - [DepositContract](#depositcontract)
6. [Contract Relationships](#contract-relationships)
7. [Access Control Summary](#access-control-summary)

---

## System Overview

The Stock Market Blockchain is a decentralized platform for tokenizing and trading company stocks. The system consists of:

- **Token Layer**: ERC-20 tokens representing USD (BUSD) and company stocks
- **Trading Layer**: AMM (Automated Market Maker) pools for trading
- **Registry Layer**: KYC/verification systems for companies and traders
- **Document Layer**: Encrypted document storage with IPFS integration

```
┌─────────────────────────────────────────────────────────────────┐
│                        USER INTERFACES                          │
├─────────────────────────────────────────────────────────────────┤
│  Company Dashboard  │  Trade Dashboard  │  Admin Dashboard      │
└─────────┬───────────┴────────┬──────────┴──────────┬────────────┘
          │                    │                     │
          ▼                    ▼                     ▼
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────────┐
│    Registry     │  │    StockAMM     │  │   TraderRegistry    │
│  (Companies)    │  │   (Trading)     │  │      (KYC)          │
└────────┬────────┘  └────────┬────────┘  └─────────────────────┘
         │                    │
         ▼                    ▼
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────────┐
│   StockToken    │  │    BaseToken    │  │EncryptedDocRegistry │
│  (Shares ERC20) │  │   (BUSD ERC20)  │  │   (Documents)       │
└─────────────────┘  └─────────────────┘  └─────────────────────┘
```

---

## Token Contracts

### BaseToken

**File**: `contracts/BaseToken.vy`

The base currency token (BUSD - Base USD Token) used for all trading operations on the platform. Functions as a stablecoin equivalent.

#### Key Features
- Standard ERC-20 implementation
- Mintable by authorized minters (admin, DepositContract, verified companies)
- 18 decimals

#### State Variables

| Variable | Type | Description |
|----------|------|-------------|
| `name` | `String[64]` | Token name ("Base USD Token") |
| `symbol` | `String[32]` | Token symbol ("BUSD") |
| `decimals` | `uint8` | Decimal places (18) |
| `totalSupply` | `uint256` | Total tokens in circulation |
| `balanceOf` | `HashMap[address, uint256]` | Balance per address |
| `allowance` | `HashMap[address, HashMap[address, uint256]]` | Spending allowances |
| `owner` | `address` | Contract owner |
| `minters` | `HashMap[address, bool]` | Authorized minters |

#### Functions

| Function | Access | Description |
|----------|--------|-------------|
| `transfer(to, value)` | Public | Transfer tokens |
| `approve(spender, value)` | Public | Approve spending |
| `transferFrom(from, to, value)` | Public | Transfer with allowance |
| `mint(to, value)` | Minters Only | Create new tokens |
| `add_minter(minter)` | Owner Only | Add minter address |
| `remove_minter(minter)` | Owner Only | Remove minter address |

#### Events
- `Transfer(sender, receiver, value)`
- `Approval(owner, spender, value)`
- `Mint(to, value)`

---

### StockToken

**File**: `contracts/StockToken.vy`

ERC-20 token representing shares of a registered company. Each company deploys their own StockToken contract.

#### Key Features
- Standard ERC-20 implementation
- Company metadata storage
- IPFS document reference
- Verification status tracking

#### State Variables

| Variable | Type | Description |
|----------|------|-------------|
| `name` | `String[64]` | Token name (e.g., "Apple Inc Stock") |
| `symbol` | `String[32]` | Token symbol (e.g., "AAPL") |
| `decimals` | `uint8` | Decimal places |
| `totalSupply` | `uint256` | Total shares issued |
| `company_name` | `String[128]` | Company name |
| `ipfs_cid` | `String[64]` | IPFS CID for company documents |
| `is_verified` | `bool` | Admin verification status |
| `owner` | `address` | Company owner address |

#### Constructor Parameters

```vyper
def __init__(
    _name: String[64],           # Token name
    _symbol: String[32],         # Token symbol
    _decimals: uint8,            # Decimals (usually 18)
    _total_supply: uint256,      # Total supply
    _company_name: String[128],  # Company name
    _ipfs_cid: String[64]        # IPFS document CID
)
```

#### Functions

| Function | Access | Description |
|----------|--------|-------------|
| `transfer(to, value)` | Public | Transfer shares |
| `approve(spender, value)` | Public | Approve spending |
| `transferFrom(from, to, value)` | Public | Transfer with allowance |
| `set_verified(verified)` | Owner Only | Set verification status |
| `update_ipfs_cid(new_cid)` | Owner Only | Update document reference |

---

## Trading Contracts

### StockAMM

**File**: `contracts/StockAMM.vy`

Automated Market Maker implementing the **constant product formula** (x * y = k) for trading stock tokens against base tokens.

#### Key Features
- Constant product AMM (similar to Uniswap V2)
- Configurable fee rate (in basis points)
- Slippage protection
- Liquidity provision support

#### State Variables

| Variable | Type | Description |
|----------|------|-------------|
| `stock_token` | `address` | Stock token address |
| `base_token` | `address` | Base token (BUSD) address |
| `stock_reserve` | `uint256` | Stock tokens in pool |
| `base_reserve` | `uint256` | Base tokens in pool |
| `fee_rate` | `uint256` | Fee in basis points (30 = 0.3%) |
| `is_initialized` | `bool` | Pool initialization status |
| `liquidity_providers` | `HashMap[address, uint256]` | LP share tracking |
| `total_liquidity_shares` | `uint256` | Total LP shares |

#### Price Formula

```
Price = base_reserve / stock_reserve

Output Amount = (amount_in * (10000 - fee_rate) * reserve_out) /
                (reserve_in * 10000 + amount_in * (10000 - fee_rate))
```

#### Functions

| Function | Access | Description |
|----------|--------|-------------|
| `init_pool(stock_token, base_token, initial_stock, initial_base)` | Public | Initialize pool with liquidity |
| `swap_base_for_stock(amount_in, min_amount_out)` | Public | Buy stock with BUSD |
| `swap_stock_for_base(amount_in, min_amount_out)` | Public | Sell stock for BUSD |
| `add_liquidity(stock_amount, base_amount)` | Public | Add liquidity to pool |
| `get_amount_out(amount_in, token_in)` | View | Calculate expected output |
| `get_price()` | View | Get current price (18 decimals) |

#### Events
- `PoolInitialized(stock_token, base_token, initial_stock, initial_base)`
- `Swap(trader, token_in, token_out, amount_in, amount_out)`
- `LiquidityAdded(provider, stock_amount, base_amount)`
- `LiquidityRemoved(provider, stock_amount, base_amount)`

---

### AMMFactory

**File**: `contracts/AMMFactory.vy`

Factory contract for registering and tracking AMM pools across the platform.

#### Key Features
- Central registry for all AMM pools
- Prevents duplicate pools for same token pair
- Pool lookup by tokens or ID

#### State Variables

| Variable | Type | Description |
|----------|------|-------------|
| `admin` | `address` | Factory admin |
| `pool_count` | `uint256` | Total registered pools |
| `pools` | `HashMap[uint256, address]` | Pool ID → address mapping |
| `pool_by_tokens` | `HashMap[address, HashMap[address, address]]` | Token pair → pool mapping |

#### Functions

| Function | Access | Description |
|----------|--------|-------------|
| `register_pool(stock_token, base_token, pool_address)` | Public | Register new AMM pool |
| `get_pool(stock_token, base_token)` | View | Get pool by token pair |
| `get_pool_by_id(pool_id)` | View | Get pool by ID |

---

## Registry Contracts

### Registry

**File**: `contracts/Registry.vy`

Central registry for company registrations, verification, and contract address management.

#### Key Features
- Company registration with KYC documents
- Admin verification workflow
- Stock token and AMM pool linkage
- IPFS document management

#### Company Struct

```vyper
struct Company:
    id: uint256
    owner: address
    name: String[128]
    symbol: String[32]
    ipfs_prospectus: String[64]
    ipfs_financials: String[64]
    ipfs_logo: String[64]
    is_verified: bool
    stock_token: address
    amm_pool: address
    created_at: uint256
```

#### State Variables

| Variable | Type | Description |
|----------|------|-------------|
| `companies` | `HashMap[uint256, Company]` | Company data |
| `company_count` | `uint256` | Total companies |
| `owner_to_company` | `HashMap[address, uint256]` | Owner → company ID |
| `symbol_to_company` | `HashMap[String[32], uint256]` | Symbol → company ID |
| `admin` | `address` | Registry admin |
| `verifiers` | `HashMap[address, bool]` | Authorized verifiers |

#### Functions

| Function | Access | Description |
|----------|--------|-------------|
| `register_company(name, symbol, ipfs_*)` | Public | Register new company |
| `set_verified(company_id, verified)` | Verifiers Only | Verify/unverify company |
| `update_ipfs_prospectus(company_id, new_cid)` | Owner Only | Update prospectus |
| `update_ipfs_financials(company_id, new_cid)` | Owner Only | Update financials |
| `update_ipfs_logo(company_id, new_cid)` | Owner Only | Update logo |
| `set_stock_token(company_id, token_address)` | Owner Only | Link stock token |
| `set_amm_pool(company_id, pool_address)` | Owner Only | Link AMM pool |
| `add_verifier(verifier)` | Admin Only | Add verifier |
| `remove_verifier(verifier)` | Admin Only | Remove verifier |
| `remove_company(company_id)` | Owner/Admin | Remove company (dev only) |
| `get_company(company_id)` | View | Get company by ID |
| `get_company_by_symbol(symbol)` | View | Get company by symbol |
| `get_company_by_owner(owner)` | View | Get company by owner |

#### Events
- `CompanyRegistered(company_id, owner, name, symbol, ipfs_*)`
- `CompanyVerified(company_id, verified_by)`
- `IPFSUpdated(company_id, document_type, old_cid, new_cid)`

---

### TraderRegistry

**File**: `contracts/TraderRegistry.vy`

KYC registry for individual traders who want to trade on the platform.

#### Key Features
- Simplified KYC for traders
- ID document and selfie verification
- Verification status tracking
- Revocation capability

#### TraderKYC Struct

```vyper
struct TraderKYC:
    id: uint256
    trader: address
    full_name: String[128]
    email: String[128]
    country: String[64]
    ipfs_id_document: String[64]  # ID/passport
    ipfs_selfie: String[64]       # Selfie with ID
    status: VerificationStatus    # PENDING/VERIFIED/REJECTED/REVOKED
    created_at: uint256
    verified_at: uint256
    verified_by: address
    rejection_reason: String[256]
```

#### Verification Status Enum

```vyper
enum VerificationStatus:
    PENDING    # 0 - Awaiting review
    VERIFIED   # 1 - Approved
    REJECTED   # 2 - Denied
    REVOKED    # 3 - Access removed
```

#### Functions

| Function | Access | Description |
|----------|--------|-------------|
| `submit_kyc(full_name, email, country, ipfs_id, ipfs_selfie)` | Public | Submit KYC |
| `verify_trader(kyc_id)` | Verifiers Only | Approve trader |
| `reject_trader(kyc_id, reason)` | Verifiers Only | Reject with reason |
| `revoke_trader(trader)` | Admin Only | Revoke verification |
| `add_verifier(verifier)` | Admin Only | Add verifier |
| `remove_verifier(verifier)` | Admin Only | Remove verifier |
| `get_kyc(kyc_id)` | View | Get KYC by ID |
| `get_kyc_by_address(trader)` | View | Get KYC by address |
| `is_verified_trader(address)` | View | Check verification |

#### Events
- `TraderRegistered(trader, request_id, full_name)`
- `TraderVerified(trader, verified_by, request_id)`
- `TraderRejected(trader, rejected_by, request_id, rejection_reason)`
- `TraderRevoked(trader, revoked_by)`

---

### MinterRegistry

**File**: `contracts/MinterRegistry.vy`

Heavy KYC registry for companies requesting BUSD minting privileges.

#### Key Features
- Extended KYC with front/back ID photos
- Company-level verification
- Minter privilege management

#### MinterRequest Struct

```vyper
struct MinterRequest:
    id: uint256
    requester: address
    reason: String[256]
    full_name: String[128]
    email: String[128]
    ipfs_id_front: String[64]
    ipfs_id_back: String[64]
    ipfs_selfie: String[64]
    status: RequestStatus
    created_at: uint256
    processed_at: uint256
    processed_by: address
    rejection_reason: String[256]
```

#### Functions

| Function | Access | Description |
|----------|--------|-------------|
| `request_minter(reason, full_name, email, ipfs_*)` | Public | Submit minter request |
| `approve_request(request_id)` | Admin Only | Approve minter |
| `reject_request(request_id, reason)` | Admin Only | Reject with reason |
| `revoke_minter(minter)` | Admin Only | Revoke privileges |
| `get_request(request_id)` | View | Get request by ID |
| `get_request_by_address(requester)` | View | Get request by address |
| `is_approved_minter(address)` | View | Check minter status |

---

### EncryptedDocRegistry

**File**: `contracts/EncryptedDocRegistry.vy`

Registry for encrypted document metadata and access control keys. Supports client-side encryption with ECIES.

#### Key Features
- Encrypted document metadata storage
- Per-recipient encrypted AES keys (ECIES)
- Access control management
- Document revocation

#### Data Structures

```vyper
struct EncryptedKey:
    ephemeral_public_key: String[132]  # ECIES ephemeral key
    iv: String[32]                      # Initialization vector
    ciphertext: String[128]             # Encrypted AES key
    mac: String[66]                     # Message authentication code

struct DocumentMetadata:
    id: uint256
    uploader: address
    cid: String[64]                     # IPFS CID
    doc_type: String[32]                # Document type
    original_name: String[128]
    original_size: uint256
    uploaded_at: uint256
    is_revoked: bool
    company_id: uint256                 # Optional company link
```

#### Functions

| Function | Access | Description |
|----------|--------|-------------|
| `upload_document(cid, doc_type, name, size, company_id)` | Public | Register document |
| `add_recipient(doc_id, recipient, encrypted_key_*)` | Uploader/Admin | Grant access |
| `add_recipients_batch(doc_id, recipients[], keys[])` | Uploader/Admin | Batch grant |
| `remove_recipient(doc_id, recipient)` | Uploader/Admin | Revoke access |
| `revoke_document(doc_id)` | Uploader/Admin | Revoke entire document |
| `get_document(doc_id)` | View | Get document metadata |
| `get_encrypted_key(doc_id, recipient)` | View | Get decryption key |
| `can_access(doc_id, recipient)` | View | Check access |
| `get_uploader_documents(uploader)` | View | Get uploader's docs |
| `get_accessible_documents(recipient)` | View | Get accessible docs |
| `transfer_admin(new_admin)` | Admin Only | Transfer admin role |

#### Encryption Flow

```
1. Client generates AES-256 key
2. Client encrypts file with AES-256-GCM
3. Client uploads encrypted file to IPFS
4. For each recipient:
   - Derive shared secret via ECDH
   - Encrypt AES key with shared secret
   - Store encrypted key on-chain
5. Recipient retrieves encrypted key from contract
6. Recipient decrypts AES key with their private key
7. Recipient decrypts file from IPFS
```

---

## Utility Contracts

### DepositContract

**File**: `contracts/DepositContract.vy`

Gateway for converting ETH to BUSD and vice versa. Acts as an on-ramp for the trading platform.

#### Key Features
- ETH → BUSD deposits (mints BUSD)
- BUSD → ETH withdrawals
- Configurable exchange rate
- Admin liquidity management

#### State Variables

| Variable | Type | Description |
|----------|------|-------------|
| `base_token` | `address` | BUSD token address |
| `admin` | `address` | Contract admin |
| `eth_to_busd_rate` | `uint256` | Exchange rate (18 decimals) |
| `total_eth_deposited` | `uint256` | Total ETH deposited |
| `total_busd_minted` | `uint256` | Total BUSD minted |

#### Constants

```vyper
MIN_DEPOSIT: constant(uint256) = 10**15    # 0.001 ETH
MIN_WITHDRAWAL: constant(uint256) = 10**18  # 1 BUSD
```

#### Functions

| Function | Access | Description |
|----------|--------|-------------|
| `deposit()` | Payable | Deposit ETH, receive BUSD |
| `withdraw(busd_amount)` | Public | Return BUSD, receive ETH |
| `update_rate(new_rate)` | Admin Only | Update exchange rate |
| `add_liquidity()` | Admin Only | Add ETH liquidity |
| `emergency_withdraw_eth(amount)` | Admin Only | Emergency withdrawal |
| `get_deposit_amount(eth_amount)` | View | Calculate BUSD for ETH |
| `get_withdrawal_amount(busd_amount)` | View | Calculate ETH for BUSD |
| `get_contract_balance()` | View | Get ETH balance |

#### Events
- `Deposit(user, eth_amount, busd_amount)`
- `Withdrawal(user, busd_amount, eth_amount)`

---

## Contract Relationships

```
┌──────────────────────────────────────────────────────────────────────┐
│                          ADMIN / DEPLOYER                            │
└──────────────────────────────────────────────────────────────────────┘
                                    │
           ┌────────────────────────┼────────────────────────┐
           │                        │                        │
           ▼                        ▼                        ▼
    ┌─────────────┐          ┌─────────────┐          ┌─────────────┐
    │  BaseToken  │◄─────────│   Deposit   │          │  Registry   │
    │   (BUSD)    │  mints   │  Contract   │          │ (Companies) │
    └──────┬──────┘          └─────────────┘          └──────┬──────┘
           │                                                  │
           │  ┌───────────────────────────────────────────────┘
           │  │
           ▼  ▼
    ┌─────────────┐          ┌─────────────┐          ┌─────────────┐
    │  StockAMM   │◄─────────│ StockToken  │◄─────────│  Company    │
    │  (Trading)  │  trades  │  (Shares)   │  deploys │   Owner     │
    └─────────────┘          └─────────────┘          └─────────────┘
           ▲
           │ trades
    ┌──────┴──────┐
    │   Trader    │◄───────── TraderRegistry (KYC)
    │   (User)    │
    └─────────────┘

    ┌─────────────┐          ┌─────────────┐
    │   Minter    │◄─────────│   Minter    │
    │  Registry   │  verifies│  (Company)  │
    └─────────────┘          └─────────────┘

    ┌─────────────┐
    │  Encrypted  │◄───────── All document uploads
    │ DocRegistry │           (KYC docs, prospectus, etc.)
    └─────────────┘
```

---

## Access Control Summary

### Admin Roles

| Contract | Admin Capabilities |
|----------|-------------------|
| BaseToken | Add/remove minters |
| Registry | Add/remove verifiers, verify companies |
| TraderRegistry | Add/remove verifiers, verify/revoke traders |
| MinterRegistry | Approve/reject/revoke minter requests |
| DepositContract | Update rate, add liquidity, emergency withdraw |
| EncryptedDocRegistry | Transfer admin, manage any document |

### Verifier Roles

| Contract | Verifier Capabilities |
|----------|----------------------|
| Registry | Verify/unverify companies |
| TraderRegistry | Verify/reject trader KYC |

### Public Access

| Action | Contract | Requirements |
|--------|----------|--------------|
| Register Company | Registry | Unique symbol, prospectus CID |
| Submit Trader KYC | TraderRegistry | Not already registered |
| Request Minter | MinterRegistry | Full KYC documents |
| Trade | StockAMM | Valid tokens, sufficient balance |
| Deposit ETH | DepositContract | Min 0.001 ETH |
| Upload Document | EncryptedDocRegistry | Valid CID |

---

## Deployment Order

1. **BaseToken** - Deploy first (no dependencies)
2. **Registry** - Deploy (no dependencies)
3. **TraderRegistry** - Deploy (no dependencies)
4. **MinterRegistry** - Deploy with BaseToken address
5. **DepositContract** - Deploy with BaseToken address, add as minter
6. **EncryptedDocRegistry** - Deploy (no dependencies)
7. **AMMFactory** - Deploy (no dependencies)

For each company:
1. Register in Registry
2. Admin verifies company
3. Deploy StockToken
4. Deploy StockAMM
5. Register AMM in AMMFactory
6. Initialize pool with liquidity

---

## Function Validations

This section documents all validation checks (assertions) in each contract function to ensure data integrity and prevent unauthorized access.

### BaseToken Validations

| Function | Validation | Error Message |
|----------|------------|---------------|
| `transfer` | `_to != empty(address)` | "Cannot transfer to zero address" |
| `transfer` | `balanceOf[msg.sender] >= _value` | "Insufficient balance" |
| `approve` | `_spender != empty(address)` | "Cannot approve zero address" |
| `transferFrom` | `_from != empty(address)` | "Cannot transfer from zero address" |
| `transferFrom` | `_to != empty(address)` | "Cannot transfer to zero address" |
| `transferFrom` | `balanceOf[_from] >= _value` | "Insufficient balance" |
| `transferFrom` | `allowance[_from][msg.sender] >= _value` | "Insufficient allowance" |
| `mint` | `minters[msg.sender]` | "Only minters can mint" |
| `mint` | `_to != empty(address)` | "Cannot mint to zero address" |
| `add_minter` | `msg.sender == owner` | "Only owner can add minters" |
| `add_minter` | `_minter != empty(address)` | "Cannot add zero address as minter" |
| `remove_minter` | `msg.sender == owner` | "Only owner can remove minters" |

---

### StockToken Validations

| Function | Validation | Error Message |
|----------|------------|---------------|
| `transfer` | `_to != empty(address)` | "Cannot transfer to zero address" |
| `transfer` | `balanceOf[msg.sender] >= _value` | "Insufficient balance" |
| `approve` | `_spender != empty(address)` | "Cannot approve zero address" |
| `transferFrom` | `_from != empty(address)` | "Cannot transfer from zero address" |
| `transferFrom` | `_to != empty(address)` | "Cannot transfer to zero address" |
| `transferFrom` | `balanceOf[_from] >= _value` | "Insufficient balance" |
| `transferFrom` | `allowance[_from][msg.sender] >= _value` | "Insufficient allowance" |
| `set_verified` | `msg.sender == owner` | "Only owner can set verification" |
| `update_ipfs_cid` | `msg.sender == owner` | "Only owner can update CID" |

---

### StockAMM Validations

| Function | Validation | Error Message |
|----------|------------|---------------|
| `__init__` | `_fee_rate <= 1000` | "Fee rate cannot exceed 10%" |
| `init_pool` | `not is_initialized` | "Pool already initialized" |
| `init_pool` | `_stock_token != empty(address)` | "Invalid stock token address" |
| `init_pool` | `_base_token != empty(address)` | "Invalid base token address" |
| `init_pool` | `_stock_token != _base_token` | "Tokens must be different" |
| `init_pool` | `_initial_stock > 0` | "Initial stock must be positive" |
| `init_pool` | `_initial_base > 0` | "Initial base must be positive" |
| `swap_base_for_stock` | `is_initialized` | "Pool not initialized" |
| `swap_base_for_stock` | `_amount_in > 0` | "Amount must be positive" |
| `swap_base_for_stock` | `amount_out >= _min_amount_out` | "Insufficient output amount" |
| `swap_base_for_stock` | `amount_out < stock_reserve` | "Insufficient liquidity" |
| `swap_stock_for_base` | `is_initialized` | "Pool not initialized" |
| `swap_stock_for_base` | `_amount_in > 0` | "Amount must be positive" |
| `swap_stock_for_base` | `amount_out >= _min_amount_out` | "Insufficient output amount" |
| `swap_stock_for_base` | `amount_out < base_reserve` | "Insufficient liquidity" |
| `add_liquidity` | `is_initialized` | "Pool not initialized" |
| `add_liquidity` | `_stock_amount > 0` | "Stock amount must be positive" |
| `add_liquidity` | `_base_amount > 0` | "Base amount must be positive" |
| `_get_amount_out` | `_amount_in > 0` | "Amount must be positive" |
| `_get_amount_out` | `_reserve_in > 0 and _reserve_out > 0` | "Insufficient liquidity" |
| `get_amount_out` | `is_initialized` | "Pool not initialized" |
| `get_price` | `is_initialized` | "Pool not initialized" |
| `get_price` | `stock_reserve > 0` | "No stock liquidity" |

---

### Registry Validations

| Function | Validation | Error Message |
|----------|------------|---------------|
| `register_company` | `len(_name) > 0` | "Company name cannot be empty" |
| `register_company` | `len(_symbol) > 0` | "Company symbol cannot be empty" |
| `register_company` | `len(_ipfs_prospectus) > 0` | "Prospectus IPFS CID cannot be empty" |
| `register_company` | `owner_to_company[msg.sender] == 0` | "Address already has a company" |
| `register_company` | `symbol_to_company[_symbol] == 0` | "Symbol already taken" |
| `set_verified` | `verifiers[msg.sender]` | "Only verifiers can set verification" |
| `set_verified` | `_company_id > 0 and _company_id <= company_count` | "Invalid company ID" |
| `update_ipfs_prospectus` | `_company_id > 0 and _company_id <= company_count` | "Invalid company ID" |
| `update_ipfs_prospectus` | `msg.sender == company.owner` | "Only company owner can update CID" |
| `update_ipfs_prospectus` | `len(_new_cid) > 0` | "IPFS CID cannot be empty" |
| `update_ipfs_financials` | `_company_id > 0 and _company_id <= company_count` | "Invalid company ID" |
| `update_ipfs_financials` | `msg.sender == company.owner` | "Only company owner can update CID" |
| `update_ipfs_financials` | `len(_new_cid) > 0` | "IPFS CID cannot be empty" |
| `update_ipfs_logo` | `_company_id > 0 and _company_id <= company_count` | "Invalid company ID" |
| `update_ipfs_logo` | `msg.sender == company.owner` | "Only company owner can update CID" |
| `update_ipfs_logo` | `len(_new_cid) > 0` | "IPFS CID cannot be empty" |
| `set_stock_token` | `_company_id > 0 and _company_id <= company_count` | "Invalid company ID" |
| `set_stock_token` | `msg.sender == company.owner` | "Only company owner can set token" |
| `set_stock_token` | `_token_address != empty(address)` | "Invalid token address" |
| `set_amm_pool` | `_company_id > 0 and _company_id <= company_count` | "Invalid company ID" |
| `set_amm_pool` | `msg.sender == company.owner` | "Only company owner can set pool" |
| `set_amm_pool` | `_pool_address != empty(address)` | "Invalid pool address" |
| `add_verifier` | `msg.sender == admin` | "Only admin can add verifiers" |
| `add_verifier` | `_verifier != empty(address)` | "Invalid verifier address" |
| `remove_verifier` | `msg.sender == admin` | "Only admin can remove verifiers" |
| `remove_company` | `_company_id > 0 and _company_id <= company_count` | "Invalid company ID" |
| `remove_company` | `msg.sender == company.owner or msg.sender == admin` | "Only owner or admin can remove company" |
| `get_company` | `_company_id > 0 and _company_id <= company_count` | "Invalid company ID" |
| `get_company_by_symbol` | `company_id > 0` | "Company not found" |
| `get_company_by_owner` | `company_id > 0` | "Company not found" |

---

### TraderRegistry Validations

| Function | Validation | Error Message |
|----------|------------|---------------|
| `submit_kyc` | `len(_full_name) > 0` | "Full name cannot be empty" |
| `submit_kyc` | `len(_email) > 0` | "Email cannot be empty" |
| `submit_kyc` | `len(_country) > 0` | "Country cannot be empty" |
| `submit_kyc` | `len(_ipfs_id_document) > 0` | "ID document required" |
| `submit_kyc` | `len(_ipfs_selfie) > 0` | "Selfie required" |
| `submit_kyc` | `address_to_kyc[msg.sender] == 0` | "Already has a KYC request" |
| `submit_kyc` | `not verified_traders[msg.sender]` | "Already verified" |
| `verify_trader` | `verifiers[msg.sender]` | "Only verifiers can verify traders" |
| `verify_trader` | `_kyc_id > 0 and _kyc_id <= kyc_count` | "Invalid KYC ID" |
| `verify_trader` | `kyc.status == VerificationStatus.PENDING` | "KYC is not pending" |
| `reject_trader` | `verifiers[msg.sender]` | "Only verifiers can reject traders" |
| `reject_trader` | `_kyc_id > 0 and _kyc_id <= kyc_count` | "Invalid KYC ID" |
| `reject_trader` | `len(_rejection_reason) > 0` | "Rejection reason cannot be empty" |
| `reject_trader` | `kyc.status == VerificationStatus.PENDING` | "KYC is not pending" |
| `revoke_trader` | `msg.sender == admin` | "Only admin can revoke traders" |
| `revoke_trader` | `verified_traders[_trader]` | "Address is not a verified trader" |
| `add_verifier` | `msg.sender == admin` | "Only admin can add verifiers" |
| `add_verifier` | `_verifier != empty(address)` | "Invalid verifier address" |
| `remove_verifier` | `msg.sender == admin` | "Only admin can remove verifiers" |
| `get_kyc` | `_kyc_id > 0 and _kyc_id <= kyc_count` | "Invalid KYC ID" |
| `get_kyc_by_address` | `kyc_id > 0` | "No KYC found for this address" |

---

### MinterRegistry Validations

| Function | Validation | Error Message |
|----------|------------|---------------|
| `request_minter` | `len(_reason) > 0` | "Reason cannot be empty" |
| `request_minter` | `len(_full_name) > 0` | "Full name cannot be empty" |
| `request_minter` | `len(_email) > 0` | "Email cannot be empty" |
| `request_minter` | `len(_ipfs_id_front) > 0` | "ID front photo required" |
| `request_minter` | `len(_ipfs_id_back) > 0` | "ID back photo required" |
| `request_minter` | `len(_ipfs_selfie) > 0` | "Selfie photo required" |
| `request_minter` | `address_to_request[msg.sender] == 0` | "Already has a pending or approved request" |
| `request_minter` | `not approved_minters[msg.sender]` | "Already an approved minter" |
| `approve_request` | `msg.sender == admin` | "Only admin can approve requests" |
| `approve_request` | `_request_id > 0 and _request_id <= request_count` | "Invalid request ID" |
| `approve_request` | `request.status == RequestStatus.PENDING` | "Request is not pending" |
| `reject_request` | `msg.sender == admin` | "Only admin can reject requests" |
| `reject_request` | `_request_id > 0 and _request_id <= request_count` | "Invalid request ID" |
| `reject_request` | `len(_rejection_reason) > 0` | "Rejection reason cannot be empty" |
| `reject_request` | `request.status == RequestStatus.PENDING` | "Request is not pending" |
| `revoke_minter` | `msg.sender == admin` | "Only admin can revoke minters" |
| `revoke_minter` | `approved_minters[_minter]` | "Address is not an approved minter" |
| `get_request` | `_request_id > 0 and _request_id <= request_count` | "Invalid request ID" |
| `get_request_by_address` | `request_id > 0` | "No request found for this address" |

---

### DepositContract Validations

| Function | Validation | Error Message |
|----------|------------|---------------|
| `__init__` | `_base_token != empty(address)` | "Invalid base token address" |
| `__init__` | `_initial_rate > 0` | "Rate must be positive" |
| `deposit` | `msg.value >= MIN_DEPOSIT` (0.001 ETH) | "Deposit amount too small" |
| `deposit` | `busd_amount > 0` | "BUSD amount too small" |
| `withdraw` | `_busd_amount >= MIN_WITHDRAWAL` (1 BUSD) | "Withdrawal amount too small" |
| `withdraw` | `eth_amount > 0` | "ETH amount too small" |
| `withdraw` | `eth_amount <= self.balance` | "Insufficient ETH in contract" |
| `withdraw` | `user_balance >= _busd_amount` | "Insufficient BUSD balance" |
| `update_rate` | `msg.sender == admin` | "Only admin can update rate" |
| `update_rate` | `_new_rate > 0` | "Rate must be positive" |
| `add_liquidity` | `msg.sender == admin` | "Only admin can add liquidity" |
| `add_liquidity` | `msg.value > 0` | "Must send ETH" |
| `emergency_withdraw_eth` | `msg.sender == admin` | "Only admin can emergency withdraw" |
| `emergency_withdraw_eth` | `_amount <= self.balance` | "Insufficient balance" |

---

### EncryptedDocRegistry Validations

| Function | Validation | Error Message |
|----------|------------|---------------|
| `upload_document` | `len(_cid) > 0` | "CID cannot be empty" |
| `add_recipient` | `_doc_id > 0 and _doc_id <= document_count` | "Invalid document ID" |
| `add_recipient` | `msg.sender == doc.uploader or msg.sender == admin` | "Only uploader or admin" |
| `add_recipient` | `not doc.is_revoked` | "Document is revoked" |
| `add_recipient` | `_recipient != empty(address)` | "Invalid recipient" |
| `add_recipients_batch` | `_doc_id > 0 and _doc_id <= document_count` | "Invalid document ID" |
| `add_recipients_batch` | `msg.sender == doc.uploader or msg.sender == admin` | "Only uploader or admin" |
| `add_recipients_batch` | `not doc.is_revoked` | "Document is revoked" |
| `add_recipients_batch` | `len(_recipients) == len(_ephemeral_public_keys)` | "Array length mismatch" |
| `add_recipients_batch` | `len(_recipients) == len(_ivs)` | "Array length mismatch" |
| `add_recipients_batch` | `len(_recipients) == len(_ciphertexts)` | "Array length mismatch" |
| `add_recipients_batch` | `len(_recipients) == len(_macs)` | "Array length mismatch" |
| `add_recipients_batch` | `recipient != empty(address)` (per item) | "Invalid recipient" |
| `remove_recipient` | `_doc_id > 0 and _doc_id <= document_count` | "Invalid document ID" |
| `remove_recipient` | `msg.sender == doc.uploader or msg.sender == admin` | "Only uploader or admin" |
| `revoke_document` | `_doc_id > 0 and _doc_id <= document_count` | "Invalid document ID" |
| `revoke_document` | `msg.sender == doc.uploader or msg.sender == admin` | "Only uploader or admin" |
| `get_document` | `_doc_id > 0 and _doc_id <= document_count` | "Invalid document ID" |
| `get_encrypted_key` | `_doc_id > 0 and _doc_id <= document_count` | "Invalid document ID" |
| `get_encrypted_key` | `not doc.is_revoked` | "Document is revoked" |
| `get_encrypted_key` | `len(key.ciphertext) > 0` | "No access for this recipient" |
| `transfer_admin` | `msg.sender == admin` | "Only admin" |
| `transfer_admin` | `_new_admin != empty(address)` | "Invalid address" |

---

### AMMFactory Validations

| Function | Validation | Error Message |
|----------|------------|---------------|
| `register_pool` | `_stock_token != empty(address)` | "Invalid stock token" |
| `register_pool` | `_base_token != empty(address)` | "Invalid base token" |
| `register_pool` | `_pool_address != empty(address)` | "Invalid pool address" |
| `register_pool` | `_stock_token != _base_token` | "Tokens must be different" |
| `register_pool` | `pool_by_tokens[_stock_token][_base_token] == empty(address)` | "Pool already exists" |
| `get_pool_by_id` | `_pool_id > 0 and _pool_id <= pool_count` | "Invalid pool ID" |

---

## Validation Categories

### 1. Access Control Validations
These ensure only authorized users can execute certain functions:

```vyper
# Admin-only
assert msg.sender == admin, "Only admin can..."

# Owner-only
assert msg.sender == owner, "Only owner can..."

# Verifier-only
assert verifiers[msg.sender], "Only verifiers can..."

# Minter-only
assert minters[msg.sender], "Only minters can..."

# Uploader or Admin
assert msg.sender == doc.uploader or msg.sender == admin, "Only uploader or admin"
```

### 2. Input Validations
These ensure function parameters are valid:

```vyper
# Non-empty strings
assert len(_name) > 0, "Name cannot be empty"

# Non-zero addresses
assert _to != empty(address), "Cannot transfer to zero address"

# Positive amounts
assert _amount > 0, "Amount must be positive"

# Within bounds
assert _id > 0 and _id <= count, "Invalid ID"
```

### 3. State Validations
These ensure the contract is in the correct state for the operation:

```vyper
# Pool must be initialized
assert is_initialized, "Pool not initialized"

# Pool must NOT be initialized
assert not is_initialized, "Pool already initialized"

# Status checks
assert kyc.status == VerificationStatus.PENDING, "KYC is not pending"

# Document not revoked
assert not doc.is_revoked, "Document is revoked"
```

### 4. Balance Validations
These ensure sufficient funds for operations:

```vyper
# Token balance
assert balanceOf[msg.sender] >= _value, "Insufficient balance"

# Allowance
assert allowance[_from][msg.sender] >= _value, "Insufficient allowance"

# Contract balance
assert eth_amount <= self.balance, "Insufficient ETH in contract"

# Liquidity
assert amount_out < stock_reserve, "Insufficient liquidity"
```

### 5. Uniqueness Validations
These prevent duplicates:

```vyper
# One company per address
assert owner_to_company[msg.sender] == 0, "Address already has a company"

# Unique symbols
assert symbol_to_company[_symbol] == 0, "Symbol already taken"

# One KYC per address
assert address_to_kyc[msg.sender] == 0, "Already has a KYC request"

# No duplicate pools
assert pool_by_tokens[_stock_token][_base_token] == empty(address), "Pool already exists"
```

### 6. Slippage Protection
These protect users from price manipulation:

```vyper
# Minimum output amount
assert amount_out >= _min_amount_out, "Insufficient output amount"
```

---

## Security Considerations

1. **Access Control**: All sensitive functions have proper access modifiers
2. **Reentrancy**: External calls are made after state changes
3. **Integer Overflow**: Vyper 0.4.3 has built-in overflow protection
4. **Slippage Protection**: AMM swaps have `min_amount_out` parameter
5. **Document Encryption**: Client-side encryption ensures privacy
6. **Key Management**: Encrypted keys stored on-chain, private keys never exposed

---

## License

All contracts are proprietary to the Stock Trading System project.
