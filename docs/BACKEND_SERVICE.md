# Hiện thực Backend Service (Backend Service Implementation)

## Mục lục
1. [Tổng quan](#1-tổng-quan)
2. [Kiến trúc hệ thống](#2-kiến-trúc-hệ-thống)
3. [Cấu trúc thư mục](#3-cấu-trúc-thư-mục)
4. [Cấu hình và Environment](#4-cấu-hình-và-environment)
5. [API Endpoints](#5-api-endpoints)
6. [Smart Contracts](#6-smart-contracts)
7. [Flow triển khai](#7-flow-triển-khai)
8. [Hướng dẫn cài đặt](#8-hướng-dẫn-cài-đặt)
9. [Scripts hỗ trợ](#9-scripts-hỗ-trợ)

---

## 1. Tổng quan

Backend Service là một **Express.js API server** đóng vai trò trung gian giữa Frontend và Blockchain, chịu trách nhiệm:

- **Deploy Smart Contracts**: Triển khai StockToken và StockAMM contracts
- **Khởi tạo Liquidity Pool**: Initialize AMM pools với initial liquidity
- **Quản lý Registry**: Cập nhật thông tin token/AMM vào Registry contract
- **Xử lý giao dịch đặc quyền**: Các giao dịch cần deployer wallet

### Tech Stack

| Component | Technology | Version |
|-----------|------------|---------|
| Runtime | Node.js | 18+ |
| Framework | Express.js | 4.18.2 |
| Blockchain | Ethers.js | 6.9.0 |
| Environment | dotenv | 16.3.1 |
| CORS | cors | 2.8.5 |

---

## 2. Kiến trúc hệ thống

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         BACKEND SERVICE ARCHITECTURE                         │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌──────────────┐         ┌──────────────────┐         ┌──────────────────┐ │
│  │   Frontend   │────────▶│  Backend Service │────────▶│   Blockchain     │ │
│  │   (Vue.js)   │  HTTP   │  (Express.js)    │  RPC    │   (Ethereum)     │ │
│  │   Port 3000  │         │  Port 3001       │         │   Port 8545      │ │
│  └──────────────┘         └──────────────────┘         └──────────────────┘ │
│                                    │                            │            │
│                                    │                            │            │
│                                    ▼                            ▼            │
│                           ┌──────────────────┐         ┌──────────────────┐ │
│                           │  Contract ABIs   │         │  Smart Contracts │ │
│                           │  (JSON files)    │         │  (Vyper)         │ │
│                           └──────────────────┘         └──────────────────┘ │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Request Flow

```
┌─────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌───────────┐
│ Frontend│───▶│  Backend │───▶│  Create  │───▶│  Deploy  │───▶│  Update   │
│ Request │    │  API     │    │  Contract│    │  to      │    │  Registry │
│         │    │          │    │  Factory │    │  Chain   │    │           │
└─────────┘    └──────────┘    └──────────┘    └──────────┘    └───────────┘
```

---

## 3. Cấu trúc thư mục

```
backend/
├── server.js              # Main Express server
├── package.json           # Dependencies
├── .env                   # Environment variables
├── .env.example           # Environment template
└── contracts/             # Contract ABIs
    ├── BaseToken.json     # ERC20 token ABI
    ├── Registry.json      # Company registry ABI
    ├── StockAMM.json      # AMM pool ABI
    └── StockToken.json    # Stock token ABI
```

### File Details

| File | Purpose |
|------|---------|
| `server.js` | Express server với tất cả API endpoints |
| `contracts/*.json` | ABI và bytecode của smart contracts |
| `.env` | Cấu hình RPC URL, private key, contract addresses |

---

## 4. Cấu hình và Environment

### 4.1. Environment Variables

```env
# .env file
PORT=3001
RPC_URL=http://127.0.0.1:8545
DEPLOYER_PRIVATE_KEY=0x...your_private_key...
REGISTRY_ADDRESS=0x56c48E2a6fBB9Ecc42d45E262Bf3E3c03724f6cC
BASE_TOKEN_ADDRESS=0xA24574B1d05abb5b07c9F8Eb83E2b69889607A7E
```

### 4.2. Server Initialization

```javascript
// server.js
import express from 'express'
import cors from 'cors'
import { ethers } from 'ethers'
import dotenv from 'dotenv'

dotenv.config()

const app = express()
const PORT = process.env.PORT || 3001

// Middleware
app.use(cors())
app.use(express.json())

// Setup provider and wallet
const provider = new ethers.JsonRpcProvider(process.env.RPC_URL)
const wallet = new ethers.Wallet(process.env.DEPLOYER_PRIVATE_KEY, provider)

console.log('🔗 Connected to:', process.env.RPC_URL)
console.log('👤 Deployer address:', wallet.address)
```

### 4.3. Contract Loading

```javascript
// Load contract artifacts
function loadContract(name) {
  const contractPath = path.join(__dirname, 'contracts', `${name}.json`)
  const contractData = JSON.parse(fs.readFileSync(contractPath, 'utf8'))
  return contractData
}

const StockTokenArtifact = loadContract('StockToken')
const StockAMMArtifact = loadContract('StockAMM')
const RegistryArtifact = loadContract('Registry')

// Get Registry contract instance
function getRegistry() {
  return new ethers.Contract(
    process.env.REGISTRY_ADDRESS,
    RegistryArtifact.abi,
    wallet
  )
}
```

---

## 5. API Endpoints

### 5.1. Health Check

```http
GET /health
```

**Response:**
```json
{
  "status": "ok",
  "deployer": "0x0BB312e97DD972ad7bfBFBDE86eBab599f80d15D",
  "network": "http://127.0.0.1:8545"
}
```

### 5.2. Deploy Stock Token

```http
POST /api/deploy/token
Content-Type: application/json

{
  "companyId": 1,
  "name": "Apple Inc",
  "symbol": "AAPL",
  "totalSupply": "1000000000000000000000000"
}
```

**Response:**
```json
{
  "success": true,
  "tokenAddress": "0x3921D338D334f3d3f1d2A88ccF8efE193228855b",
  "transactionHash": "0x..."
}
```

**Flow:**
```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          DEPLOY TOKEN FLOW                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  1. Validate Request                                                         │
│     ├── Check companyId, name, symbol, totalSupply                          │
│     └── Return 400 if missing                                                │
│                                                                              │
│  2. Create Contract Factory                                                  │
│     const StockTokenFactory = new ethers.ContractFactory(                    │
│       StockTokenArtifact.abi,                                                │
│       StockTokenArtifact.bytecode,                                           │
│       wallet                                                                 │
│     )                                                                        │
│                                                                              │
│  3. Deploy Contract                                                          │
│     const stockToken = await StockTokenFactory.deploy(                       │
│       symbol,        // _name                                                │
│       symbol,        // _symbol                                              │
│       18,            // _decimals                                            │
│       totalSupply,   // _total_supply                                        │
│       name,          // _company_name                                        │
│       'QmDefault'    // _ipfs_cid (placeholder)                              │
│     )                                                                        │
│                                                                              │
│  4. Wait for Deployment                                                      │
│     await stockToken.waitForDeployment()                                     │
│     const tokenAddress = await stockToken.getAddress()                       │
│                                                                              │
│  5. Update Registry                                                          │
│     const registry = getRegistry()                                           │
│     await registry.set_stock_token(companyId, tokenAddress)                  │
│                                                                              │
│  6. Return Response                                                          │
│     { success: true, tokenAddress, transactionHash }                         │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 5.3. Deploy AMM Pool

```http
POST /api/deploy/amm
Content-Type: application/json

{
  "companyId": 1
}
```

**Response:**
```json
{
  "success": true,
  "ammAddress": "0xc7F4Ea9b0719aA3ca2411666497092a63261A3e4",
  "transactionHash": "0x..."
}
```

**Implementation:**
```javascript
app.post('/api/deploy/amm', async (req, res) => {
  try {
    const { companyId } = req.body

    // Create contract factory
    const StockAMMFactory = new ethers.ContractFactory(
      StockAMMArtifact.abi,
      StockAMMArtifact.bytecode,
      wallet
    )

    // Deploy contract with 0.3% fee
    const feeRate = 30 // 0.3% in basis points
    const amm = await StockAMMFactory.deploy(feeRate)
    await amm.waitForDeployment()
    const ammAddress = await amm.getAddress()

    // Update registry
    const registry = getRegistry()
    const tx = await registry.set_amm_pool(companyId, ammAddress)
    await tx.wait()

    res.json({ success: true, ammAddress, transactionHash: tx.hash })
  } catch (error) {
    res.status(500).json({ error: error.message })
  }
})
```

### 5.4. Initialize Pool

```http
POST /api/initialize/pool
Content-Type: application/json

{
  "ammAddress": "0xc7F4Ea9b0719aA3ca2411666497092a63261A3e4",
  "stockTokenAddress": "0x3921D338D334f3d3f1d2A88ccF8efE193228855b",
  "baseTokenAddress": "0xA24574B1d05abb5b07c9F8Eb83E2b69889607A7E",
  "initialStock": "100000000000000000000000",
  "initialBase": "1000000000000000000000000"
}
```

**Response:**
```json
{
  "success": true,
  "transactionHash": "0x...",
  "price": "10.0"
}
```

**Flow:**
```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        INITIALIZE POOL FLOW                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  Step 1: Get Contract Instances                                              │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │  const amm = new ethers.Contract(ammAddress, StockAMMArtifact.abi)      ││
│  │  const stockToken = new ethers.Contract(stockTokenAddress, ...)         ││
│  │  const baseToken = new ethers.Contract(baseTokenAddress, ...)           ││
│  └─────────────────────────────────────────────────────────────────────────┘│
│                                      │                                       │
│                                      ▼                                       │
│  Step 2: Approve Stock Token                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │  await stockToken.approve(ammAddress, initialStock)                     ││
│  └─────────────────────────────────────────────────────────────────────────┘│
│                                      │                                       │
│                                      ▼                                       │
│  Step 3: Approve Base Token                                                  │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │  await baseToken.approve(ammAddress, initialBase)                       ││
│  └─────────────────────────────────────────────────────────────────────────┘│
│                                      │                                       │
│                                      ▼                                       │
│  Step 4: Initialize Pool                                                     │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │  await amm.init_pool(stockTokenAddress, baseTokenAddress,               ││
│  │                      initialStock, initialBase)                         ││
│  └─────────────────────────────────────────────────────────────────────────┘│
│                                      │                                       │
│                                      ▼                                       │
│  Step 5: Get Initial Price                                                   │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │  const price = await amm.get_price()                                    ││
│  │  // price = initialBase / initialStock                                  ││
│  └─────────────────────────────────────────────────────────────────────────┘│
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 5.5. Get Deployer Balance

```http
GET /api/deployer/balance
```

**Response:**
```json
{
  "address": "0x0BB312e97DD972ad7bfBFBDE86eBab599f80d15D",
  "balance": "99.5",
  "balanceWei": "99500000000000000000"
}
```

---

## 6. Smart Contracts

### 6.1. Contract Overview

| Contract | Address | Purpose |
|----------|---------|---------|
| BaseToken | 0xA24574B1d05abb5b07c9F8Eb83E2b69889607A7E | BUSD stablecoin |
| Registry | 0x56c48E2a6fBB9Ecc42d45E262Bf3E3c03724f6cC | Company registry |
| MinterRegistry | 0x76E6C15461dF40Eacb3AB62aF01E0CA6212C91F5 | Minter KYC |
| TraderRegistry | 0xF40725bF0995F00885C4226A103AB59706275e2d | Trader KYC |
| DepositContract | 0xa8e9b094aAda774ab6a28cCC5021c99CcdDFb19F | ETH/BUSD exchange |
| EncryptedDocRegistry | 0xc63b13636bFAb8c92abd1Dd442AA239A85acce46 | Encrypted documents |

### 6.2. StockToken Contract

```vyper
# contracts/StockToken.vy
@deploy
def __init__(
    _name: String[64],
    _symbol: String[32],
    _decimals: uint8,
    _total_supply: uint256,
    _company_name: String[128],
    _ipfs_cid: String[64]
):
    self.name = _name
    self.symbol = _symbol
    self.decimals = _decimals
    self.totalSupply = _total_supply
    self.company_name = _company_name
    self.ipfs_cid = _ipfs_cid
    self.balanceOf[msg.sender] = _total_supply
```

### 6.3. StockAMM Contract

```vyper
# contracts/StockAMM.vy
@external
def init_pool(
    _stock_token: address,
    _base_token: address,
    _initial_stock: uint256,
    _initial_base: uint256
):
    """Initialize the AMM pool with initial liquidity"""
    assert not self.is_initialized, "Already initialized"

    self.stock_token = _stock_token
    self.base_token = _base_token

    # Transfer tokens to pool
    ERC20(_stock_token).transferFrom(msg.sender, self, _initial_stock)
    ERC20(_base_token).transferFrom(msg.sender, self, _initial_base)

    self.stock_reserve = _initial_stock
    self.base_reserve = _initial_base
    self.is_initialized = True

@view
@external
def get_price() -> uint256:
    """Get current price (base per stock)"""
    return (self.base_reserve * 10**18) / self.stock_reserve
```

### 6.4. Registry Contract

```vyper
# contracts/Registry.vy
@external
def set_stock_token(_company_id: uint256, _token_address: address):
    """Set stock token address for a company (admin only)"""
    assert msg.sender == self.admin or self.verifiers[msg.sender], "Unauthorized"
    assert _company_id > 0 and _company_id <= self.company_count, "Invalid company"

    self.companies[_company_id].stock_token = _token_address

@external
def set_amm_pool(_company_id: uint256, _pool_address: address):
    """Set AMM pool address for a company (admin only)"""
    assert msg.sender == self.admin or self.verifiers[msg.sender], "Unauthorized"
    assert _company_id > 0 and _company_id <= self.company_count, "Invalid company"

    self.companies[_company_id].amm_pool = _pool_address
```

---

## 7. Flow triển khai

### 7.1. Complete Deployment Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    COMPLETE COMPANY DEPLOYMENT FLOW                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  Phase 1: Company Registration (Frontend → Blockchain)                       │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │  1. User fills company form                                             ││
│  │  2. Upload documents to IPFS → Get CIDs                                 ││
│  │  3. Call Registry.register_company(name, symbol, cids...)               ││
│  │  4. Get companyId from event                                            ││
│  └─────────────────────────────────────────────────────────────────────────┘│
│                                      │                                       │
│                                      ▼                                       │
│  Phase 2: Admin Verification (Admin Panel)                                   │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │  1. Admin reviews company documents                                     ││
│  │  2. Call Registry.set_verified(companyId, true)                         ││
│  └─────────────────────────────────────────────────────────────────────────┘│
│                                      │                                       │
│                                      ▼                                       │
│  Phase 3: Token Deployment (Frontend → Backend → Blockchain)                 │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │  1. Frontend: POST /api/deploy/token                                    ││
│  │  2. Backend: Deploy StockToken contract                                 ││
│  │  3. Backend: Update Registry.set_stock_token()                          ││
│  │  4. Return tokenAddress to frontend                                     ││
│  └─────────────────────────────────────────────────────────────────────────┘│
│                                      │                                       │
│                                      ▼                                       │
│  Phase 4: AMM Deployment (Frontend → Backend → Blockchain)                   │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │  1. Frontend: POST /api/deploy/amm                                      ││
│  │  2. Backend: Deploy StockAMM contract                                   ││
│  │  3. Backend: Update Registry.set_amm_pool()                             ││
│  │  4. Return ammAddress to frontend                                       ││
│  └─────────────────────────────────────────────────────────────────────────┘│
│                                      │                                       │
│                                      ▼                                       │
│  Phase 5: Pool Initialization (Frontend → Backend → Blockchain)              │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │  1. Frontend: POST /api/initialize/pool                                 ││
│  │  2. Backend: Approve tokens for AMM                                     ││
│  │  3. Backend: Call AMM.init_pool()                                       ││
│  │  4. Return initial price to frontend                                    ││
│  └─────────────────────────────────────────────────────────────────────────┘│
│                                      │                                       │
│                                      ▼                                       │
│  Phase 6: Trading Enabled                                                    │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │  Company is now tradeable on the platform!                              ││
│  │  Users can buy/sell stock tokens via AMM                                ││
│  └─────────────────────────────────────────────────────────────────────────┘│
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 7.2. Error Handling

```javascript
// Centralized error handling
app.post('/api/deploy/token', async (req, res) => {
  try {
    // ... deployment logic
  } catch (error) {
    console.error('❌ Error deploying token:', error)
    res.status(500).json({
      error: error.message,
      details: error.reason || error.data?.message
    })
  }
})
```

---

## 8. Hướng dẫn cài đặt

### 8.1. Prerequisites

```bash
# Node.js 18+
node --version  # v18.x.x

# npm or yarn
npm --version   # 9.x.x
```

### 8.2. Installation

```bash
# Navigate to backend directory
cd backend

# Install dependencies
npm install

# Copy environment file
cp .env.example .env

# Edit .env with your configuration
nano .env
```

### 8.3. Configuration

```env
# .env
PORT=3001
RPC_URL=http://127.0.0.1:8545
DEPLOYER_PRIVATE_KEY=0x...
REGISTRY_ADDRESS=0x56c48E2a6fBB9Ecc42d45E262Bf3E3c03724f6cC
BASE_TOKEN_ADDRESS=0xA24574B1d05abb5b07c9F8Eb83E2b69889607A7E
```

### 8.4. Running the Server

```bash
# Development mode (with auto-reload)
npm run dev

# Production mode
npm start

# Expected output:
# 🔗 Connected to: http://127.0.0.1:8545
# 👤 Deployer address: 0x0BB312e97DD972ad7bfBFBDE86eBab599f80d15D
# 🚀 Backend server running on http://localhost:3001
# 📋 Registry: 0x56c48E2a6fBB9Ecc42d45E262Bf3E3c03724f6cC
# 💵 Base Token: 0xA24574B1d05abb5b07c9F8Eb83E2b69889607A7E
```

### 8.5. Using start-backend.sh

```bash
# From project root
chmod +x start-backend.sh
./start-backend.sh
```

---

## 9. Scripts hỗ trợ

### 9.1. Deploy Script (Python)

```python
# scripts/deploy.py
from ape import accounts, project

def deploy_all():
    deployer = accounts.load("deployer")

    # Deploy BaseToken
    base_token = project.BaseToken.deploy("BUSD", "BUSD", 18, sender=deployer)

    # Deploy Registry
    registry = project.Registry.deploy(sender=deployer)

    # Deploy MinterRegistry
    minter_registry = project.MinterRegistry.deploy(base_token.address, sender=deployer)

    # Deploy TraderRegistry
    trader_registry = project.TraderRegistry.deploy(sender=deployer)

    # Deploy DepositContract
    deposit_contract = project.DepositContract.deploy(
        base_token.address,
        2000 * 10**18,  # ETH to BUSD rate
        sender=deployer
    )

    # Deploy EncryptedDocRegistry
    encrypted_doc_registry = project.EncryptedDocRegistry.deploy(sender=deployer)

    return {
        "BaseToken": base_token.address,
        "Registry": registry.address,
        "MinterRegistry": minter_registry.address,
        "TraderRegistry": trader_registry.address,
        "DepositContract": deposit_contract.address,
        "EncryptedDocRegistry": encrypted_doc_registry.address
    }
```

### 9.2. Export Contracts Script

```python
# scripts/export_contracts.py
import json
from pathlib import Path

def export_contracts():
    """Export contract ABIs to backend/contracts/"""
    contracts = ["BaseToken", "Registry", "StockToken", "StockAMM"]

    for contract_name in contracts:
        # Load from .build/
        build_path = Path(f".build/{contract_name}.json")
        contract_data = json.loads(build_path.read_text())

        # Export to backend/contracts/
        output_path = Path(f"backend/contracts/{contract_name}.json")
        output_path.write_text(json.dumps(contract_data, indent=2))

        print(f"✅ Exported {contract_name}")
```

### 9.3. Test IPFS Script

```javascript
// scripts/test_ipfs.js
import fetch from 'node-fetch'

async function testIPFS() {
  // Test upload
  const formData = new FormData()
  formData.append('file', new Blob(['Hello IPFS!'], { type: 'text/plain' }))

  const response = await fetch('http://localhost:5001/api/v0/add', {
    method: 'POST',
    body: formData
  })

  const result = await response.json()
  console.log('Uploaded CID:', result.Hash)

  // Test retrieve
  const content = await fetch(`http://localhost:8081/ipfs/${result.Hash}`)
  console.log('Content:', await content.text())
}

testIPFS()
```

---

## Tài liệu tham khảo

- [Express.js Documentation](https://expressjs.com/)
- [Ethers.js v6 Documentation](https://docs.ethers.org/v6/)
- [Vyper Documentation](https://docs.vyperlang.org/)
- [Ape Framework](https://docs.apeworx.io/)
