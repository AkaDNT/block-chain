# Xây dựng ứng dụng Frontend (Frontend Application)

## Mục lục
1. [Tổng quan](#1-tổng-quan)
2. [Kiến trúc hệ thống](#2-kiến-trúc-hệ-thống)
3. [Cấu trúc thư mục](#3-cấu-trúc-thư-mục)
4. [Tech Stack](#4-tech-stack)
5. [Routing và Navigation](#5-routing-và-navigation)
6. [Blockchain Service](#6-blockchain-service)
7. [Components](#7-components)
8. [Views (Pages)](#8-views-pages)
9. [Utilities](#9-utilities)
10. [Flow triển khai](#10-flow-triển-khai)
11. [Hướng dẫn cài đặt](#11-hướng-dẫn-cài-đặt)
12. [State Management](#12-state-management)

---

## 1. Tổng quan

Frontend là một **Single Page Application (SPA)** được xây dựng bằng **Vue.js 3** với các tính năng chính:

- **Kết nối Wallet**: Tích hợp MetaMask để xác thực và ký giao dịch
- **Đăng ký công ty**: Form đăng ký với upload tài liệu lên IPFS
- **Giao dịch cổ phiếu**: Mua/bán token qua AMM với biểu đồ giá real-time
- **Quản lý KYC**: Xác minh danh tính cho trader và minter
- **Admin Panel**: Quản lý công ty, xác minh, và phê duyệt yêu cầu
- **Dashboard**: Theo dõi portfolio và lịch sử giao dịch

### Đặc điểm nổi bật:
- **Responsive Design**: Tương thích đa thiết bị với TailwindCSS
- **Real-time Updates**: Cập nhật giá và balance tự động
- **Transaction Toasts**: Thông báo trạng thái giao dịch
- **Encrypted Documents**: Mã hóa end-to-end cho tài liệu nhạy cảm

---

## 2. Kiến trúc hệ thống

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        FRONTEND ARCHITECTURE                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │                           Vue.js 3 Application                          ││
│  ├─────────────────────────────────────────────────────────────────────────┤│
│  │                                                                          ││
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ ││
│  │  │    Views     │  │  Components  │  │   Utilities  │  │   Assets     │ ││
│  │  ├──────────────┤  ├──────────────┤  ├──────────────┤  ├──────────────┤ ││
│  │  │ Home.vue     │  │ PriceChart   │  │ blockchain.js│  │ style.css    │ ││
│  │  │ Register.vue │  │ TraderKYC    │  │ ipfs.js      │  │ logo.svg     │ ││
│  │  │ Trade.vue    │  │ Toast        │  │ encryption.js│  │              │ ││
│  │  │ Dashboard.vue│  │ ConfirmModal │  │ toast.js     │  │              │ ││
│  │  │ Admin.vue    │  │ ...          │  │ ...          │  │              │ ││
│  │  └──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘ ││
│  │                                                                          ││
│  └─────────────────────────────────────────────────────────────────────────┘│
│                                      │                                       │
│                                      ▼                                       │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │                         External Services                                ││
│  ├─────────────────────────────────────────────────────────────────────────┤│
│  │                                                                          ││
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ ││
│  │  │   MetaMask   │  │  Blockchain  │  │    IPFS      │  │   Backend    │ ││
│  │  │   Wallet     │  │  (Ethereum)  │  │    Node      │  │   API        │ ││
│  │  │              │  │  Port 8545   │  │  Port 5001   │  │  Port 3001   │ ││
│  │  └──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘ ││
│  │                                                                          ││
│  └─────────────────────────────────────────────────────────────────────────┘│
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Data Flow

```
┌─────────┐    ┌───────────┐    ┌──────────────┐    ┌──────────────┐
│  User   │───▶│  Vue      │───▶│  Blockchain  │───▶│  Smart       │
│  Action │    │  Component│    │  Service     │    │  Contract    │
└─────────┘    └───────────┘    └──────────────┘    └──────────────┘
                    │                   │                   │
                    │                   │                   │
                    ▼                   ▼                   ▼
              ┌───────────┐    ┌──────────────┐    ┌──────────────┐
              │  Update   │◀───│  Parse       │◀───│  Event       │
              │  UI State │    │  Response    │    │  Emitted     │
              └───────────┘    └──────────────┘    └──────────────┘
```

---

## 3. Cấu trúc thư mục

```
frontend/
├── index.html                 # Entry HTML
├── package.json               # Dependencies
├── vite.config.js             # Vite configuration
├── tailwind.config.js         # TailwindCSS config
├── postcss.config.js          # PostCSS config
├── .env                       # Environment variables
├── public/                    # Static assets
└── src/
    ├── main.js                # App entry point
    ├── App.vue                # Root component
    ├── assets/
    │   ├── style.css          # Global styles
    │   └── logo.svg           # App logo
    ├── components/
    │   ├── ConfirmModal.vue   # Confirmation dialog
    │   ├── EncryptedDocumentList.vue
    │   ├── EncryptedDocumentUpload.vue
    │   ├── MinterRequestNotice.vue
    │   ├── PriceChart.vue     # Price chart component
    │   ├── Toast.vue          # Toast notifications
    │   ├── TokenPriceChart.vue
    │   └── TraderKYC.vue      # Trader KYC form
    ├── contracts/
    │   ├── EncryptedDocRegistry.json
    │   ├── StockAMM.json
    │   └── StockToken.json
    ├── utils/
    │   ├── blockchain.js      # Blockchain service
    │   ├── confirm.js         # Confirmation utility
    │   ├── contractDeployer.js
    │   ├── encryptedIPFS.js   # Encrypted IPFS
    │   ├── encryption.js      # Crypto utilities
    │   ├── ipfs.js            # IPFS utilities
    │   ├── keyManager.js      # Key management
    │   ├── toast.js           # Toast service
    │   └── useEncryptedDocuments.js
    └── views/
        ├── Home.vue           # Landing page
        ├── Register.vue       # Company registration
        ├── Trade.vue          # Trading interface
        ├── Dashboard.vue      # User dashboard
        ├── Admin.vue          # Admin panel
        ├── AdminMinterRequests.vue
        └── CompanyDashboard.vue
```

---

## 4. Tech Stack

### 4.1. Core Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| vue | ^3.3.0 | UI Framework |
| vue-router | ^4.2.0 | Client-side routing |
| ethers | ^6.8.0 | Blockchain interaction |
| axios | ^1.5.0 | HTTP client |
| chart.js | ^4.5.1 | Charts |
| vue-chartjs | ^5.3.3 | Vue Chart.js wrapper |

### 4.2. Dev Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| vite | ^4.4.0 | Build tool |
| @vitejs/plugin-vue | ^4.4.0 | Vue plugin for Vite |
| tailwindcss | ^3.3.0 | CSS framework |
| autoprefixer | ^10.4.0 | CSS vendor prefixes |
| postcss | ^8.4.0 | CSS processing |

### 4.3. UI Components

| Package | Version | Purpose |
|---------|---------|---------|
| @headlessui/vue | ^1.7.0 | Accessible UI components |
| @heroicons/vue | ^2.0.0 | Icon library |

---

## 5. Routing và Navigation

### 5.1. Route Configuration

```javascript
// src/main.js
import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  { path: '/', name: 'Home', component: Home },
  { path: '/register', name: 'Register', component: Register },
  { path: '/trade', name: 'Trade', component: Trade },
  { path: '/dashboard', name: 'Dashboard', component: Dashboard },
  { path: '/company', name: 'CompanyDashboard', component: CompanyDashboard },
  { path: '/admin', name: 'Admin', component: Admin }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})
```

### 5.2. Navigation Structure

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           NAVIGATION STRUCTURE                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │                              Navbar                                      ││
│  │  ┌──────┐ ┌──────┐ ┌────────────┐ ┌───────┐ ┌───────────┐ ┌───────────┐ ││
│  │  │ Logo │ │ Home │ │ My Company │ │ Trade │ │ Dashboard │ │  Wallet   │ ││
│  │  └──────┘ └──────┘ └────────────┘ └───────┘ └───────────┘ └───────────┘ ││
│  └─────────────────────────────────────────────────────────────────────────┘│
│                                                                              │
│  Routes:                                                                     │
│  ├── /              → Home.vue (Landing page)                                │
│  ├── /register      → Register.vue (Company registration/management)        │
│  ├── /trade         → Trade.vue (Trading interface)                         │
│  ├── /dashboard     → Dashboard.vue (User portfolio)                        │
│  ├── /company       → CompanyDashboard.vue (Company owner view)             │
│  └── /admin         → Admin.vue (Admin panel - conditional)                 │
│                                                                              │
│  Conditional Navigation:                                                     │
│  ├── Admin link: Only visible if user is admin                              │
│  ├── Trade: Requires verified trader KYC                                    │
│  └── My Company: Shows company details if registered                        │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 5.3. App.vue Navigation

```vue
<!-- src/App.vue -->
<nav class="bg-white shadow-sm border-b border-gray-200">
  <div class="max-w-7xl mx-auto px-6">
    <div class="flex justify-between items-center h-16">
      <!-- Logo -->
      <router-link to="/" class="flex items-center space-x-3">
        <img :src="logo" alt="DEXCK Logo" class="h-10 w-10" />
        <span class="text-l font-bold">DEXCK</span>
      </router-link>

      <!-- Navigation Links -->
      <div class="flex items-center space-x-1">
        <router-link to="/" v-if="!isAdmin">Home</router-link>
        <router-link to="/register" v-if="!isAdmin">My Company</router-link>
        <router-link to="/trade" v-if="!isAdmin">Trade</router-link>
        <router-link to="/dashboard">Dashboard</router-link>
        <router-link to="/admin" v-if="isAdmin">Admin</router-link>

        <!-- Wallet Connection -->
        <button @click="connectWallet" v-if="!isConnected">
          Connect Wallet
        </button>
        <div v-else class="relative">
          <!-- Portfolio Dropdown -->
        </div>
      </div>
    </div>
  </div>
</nav>
```

---

## 6. Blockchain Service

### 6.1. Service Overview

`blockchain.js` là service chính để tương tác với blockchain, cung cấp:

- **Wallet Connection**: Kết nối MetaMask
- **Contract Instances**: Tạo contract objects
- **Token Operations**: Balance, approve, transfer
- **AMM Operations**: Swap, get price, get reserves
- **Registry Operations**: Register company, get company
- **KYC Operations**: Trader/Minter verification

### 6.2. Initialization

```javascript
// src/utils/blockchain.js
class BlockchainService {
  constructor() {
    this.provider = null
    this.signer = null
  }

  async connect() {
    if (typeof window.ethereum !== 'undefined') {
      // Load contract addresses
      await loadContractAddresses()

      // Request account access
      const accounts = await window.ethereum.request({
        method: 'eth_requestAccounts'
      })

      this.provider = new ethers.BrowserProvider(window.ethereum)
      this.signer = await this.provider.getSigner(accounts[0])
      return true
    }
    return false
  }

  async initialize() {
    await this.loadContractAddresses()

    if (typeof window.ethereum !== 'undefined') {
      this.provider = new ethers.BrowserProvider(window.ethereum)

      const accounts = await window.ethereum.request({ method: 'eth_accounts' })
      if (accounts.length > 0) {
        this.signer = await this.provider.getSigner(accounts[0])
      }
    }
    return true
  }
}

export const blockchain = new BlockchainService()
export default blockchain
```

### 6.3. Contract ABIs

```javascript
// Contract ABIs defined in blockchain.js
const ERC20_ABI = [
  "function name() view returns (string)",
  "function symbol() view returns (string)",
  "function decimals() view returns (uint8)",
  "function balanceOf(address) view returns (uint256)",
  "function transfer(address to, uint256 amount) returns (bool)",
  "function approve(address spender, uint256 amount) returns (bool)",
  // ...
]

const REGISTRY_ABI = [
  "function register_company(string name, string symbol, ...) returns (uint256)",
  "function get_company(uint256 company_id) view returns (tuple(...))",
  "function set_verified(uint256 company_id, bool verified)",
  // ...
]

const AMM_ABI = [
  "function swap_base_for_stock(uint256 amount_in, uint256 min_out) returns (uint256)",
  "function swap_stock_for_base(uint256 amount_in, uint256 min_out) returns (uint256)",
  "function get_price() view returns (uint256)",
  // ...
]
```

### 6.4. Key Methods

```javascript
// Token Operations
async getTokenBalance(tokenAddress, accountAddress) { ... }
async getBaseTokenBalance(accountAddress) { ... }
async approveToken(tokenAddress, spenderAddress, amount) { ... }

// AMM Operations
async getAMMPrice(ammAddress) { ... }
async getAMMReserves(ammAddress) { ... }
async swapTokens(ammAddress, amountIn, minAmountOut, isBaseForStock) { ... }
async getRecentTrades(ammAddress, traderAddress, limit) { ... }
async getPriceHistory(ammAddress, limit) { ... }

// Registry Operations
async registerCompany(name, symbol, ipfsProspectus, ipfsFinancials, ipfsLogo) { ... }
async getCompany(companyId) { ... }
async getCompanyByOwner(ownerAddress) { ... }
async getAllCompanies() { ... }

// Trader KYC
async submitTraderKYC(kycData) { ... }
async getTraderKYC(address) { ... }
async verifyTraderKYC(kycId) { ... }
async isVerifiedTrader(address) { ... }

// Minter KYC
async requestMinter(kycData) { ... }
async getMinterRequest(address) { ... }
async approveMinterRequest(requestId) { ... }
async isMinter(address) { ... }

// Deposit/Withdraw
async depositETH(ethAmount) { ... }
async withdrawBUSD(busdAmount) { ... }

// Encrypted Documents
async uploadEncryptedDocument(cid, docType, originalName, originalSize, companyId) { ... }
async addDocumentRecipient(docId, recipient, encryptedKey) { ... }
async getEncryptedDocument(docId) { ... }
async canAccessDocument(docId, address) { ... }
```

---

## 7. Components

### 7.1. Component Overview

| Component | Purpose | Location |
|-----------|---------|----------|
| `Toast.vue` | Transaction notifications | Global |
| `ConfirmModal.vue` | Confirmation dialogs | Global |
| `PriceChart.vue` | Price chart visualization | Trade |
| `TokenPriceChart.vue` | Token price history | Trade |
| `TraderKYC.vue` | Trader verification form | Trade |
| `MinterRequestNotice.vue` | Minter KYC status | Register |
| `EncryptedDocumentUpload.vue` | Encrypted file upload | Register |
| `EncryptedDocumentList.vue` | Document list view | Register |

### 7.2. Toast Component

```vue
<!-- src/components/Toast.vue -->
<template>
  <div class="fixed bottom-4 right-4 z-50 space-y-2">
    <TransitionGroup name="toast">
      <div
        v-for="toast in toasts"
        :key="toast.id"
        :class="toastClasses(toast.type)"
        class="p-4 rounded-lg shadow-lg max-w-sm"
      >
        <div class="flex items-start">
          <component :is="getIcon(toast.type)" class="w-5 h-5 mr-3" />
          <div>
            <p class="font-semibold">{{ toast.title }}</p>
            <p class="text-sm opacity-90">{{ toast.message }}</p>
          </div>
        </div>
      </div>
    </TransitionGroup>
  </div>
</template>
```

### 7.3. TraderKYC Component

```vue
<!-- src/components/TraderKYC.vue -->
<template>
  <div class="bg-white rounded-lg shadow-sm border p-6">
    <h2 class="text-xl font-bold mb-4">Trader Verification</h2>

    <!-- KYC Status Display -->
    <div v-if="kycStatus" class="mb-6">
      <div :class="statusClasses">
        {{ kycStatus }}
      </div>
    </div>

    <!-- KYC Form -->
    <form v-else @submit.prevent="submitKYC">
      <div class="space-y-4">
        <input v-model="form.fullName" placeholder="Full Name" required />
        <input v-model="form.email" type="email" placeholder="Email" required />
        <select v-model="form.country" required>
          <option value="">Select Country</option>
          <!-- Country options -->
        </select>

        <!-- Document Upload -->
        <div>
          <label>ID Document</label>
          <input type="file" @change="uploadIdDocument" accept="image/*,.pdf" />
        </div>

        <div>
          <label>Selfie with ID</label>
          <input type="file" @change="uploadSelfie" accept="image/*" />
        </div>

        <button type="submit" :disabled="isSubmitting">
          {{ isSubmitting ? 'Submitting...' : 'Submit KYC' }}
        </button>
      </div>
    </form>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import blockchain from '../utils/blockchain.js'
import { uploadToIPFS } from '../utils/ipfs.js'

const form = ref({
  fullName: '',
  email: '',
  country: '',
  ipfsIdDocument: '',
  ipfsSelfie: ''
})

async function uploadIdDocument(event) {
  const file = event.target.files[0]
  form.value.ipfsIdDocument = await uploadToIPFS(file)
}

async function submitKYC() {
  await blockchain.submitTraderKYC(form.value)
  emit('kyc-submitted')
}
</script>
```

### 7.4. PriceChart Component

```vue
<!-- src/components/PriceChart.vue -->
<template>
  <div class="bg-white rounded-lg p-4">
    <Line :data="chartData" :options="chartOptions" />
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { Line } from 'vue-chartjs'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
} from 'chart.js'

ChartJS.register(
  CategoryScale, LinearScale, PointElement, LineElement,
  Title, Tooltip, Legend, Filler
)

const props = defineProps({
  priceHistory: { type: Array, default: () => [] }
})

const chartData = computed(() => ({
  labels: props.priceHistory.map(p => formatTime(p.timestamp)),
  datasets: [{
    label: 'Price (BUSD)',
    data: props.priceHistory.map(p => p.price),
    borderColor: '#3B82F6',
    backgroundColor: 'rgba(59, 130, 246, 0.1)',
    fill: true,
    tension: 0.4
  }]
}))

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: { display: false }
  },
  scales: {
    y: { beginAtZero: false }
  }
}
</script>
```

---

## 8. Views (Pages)

### 8.1. Home.vue

**Purpose**: Landing page với thông tin tổng quan về platform

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              HOME PAGE                                       │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │                           Hero Section                                   ││
│  │  "Decentralized Stock Exchange"                                         ││
│  │  [Get Started] [Learn More]                                             ││
│  └─────────────────────────────────────────────────────────────────────────┘│
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │                          Features Grid                                   ││
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐    ││
│  │  │ Decentralized│  │ Transparent │  │ Low Fees   │  │ Secure     │    ││
│  │  │ Trading     │  │ Pricing     │  │ AMM        │  │ KYC        │    ││
│  │  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘    ││
│  └─────────────────────────────────────────────────────────────────────────┘│
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │                        Market Overview                                   ││
│  │  Top Gainers | Top Losers | Most Active                                 ││
│  └─────────────────────────────────────────────────────────────────────────┘│
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 8.2. Register.vue

**Purpose**: Đăng ký công ty mới hoặc quản lý công ty đã đăng ký

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           REGISTER PAGE                                      │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  If No Company Registered:                                                   │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │                      Registration Form                                   ││
│  │  ┌─────────────────────────────────────────────────────────────────────┐││
│  │  │ Company Name: [________________]                                    │││
│  │  │ Symbol:       [____]                                                │││
│  │  │ Prospectus:   [Upload PDF] → IPFS                                   │││
│  │  │ Financials:   [Upload PDF] → IPFS                                   │││
│  │  │ Logo:         [Upload Image] → IPFS                                 │││
│  │  │                                                                      │││
│  │  │ [Register Company]                                                   │││
│  │  └─────────────────────────────────────────────────────────────────────┘││
│  └─────────────────────────────────────────────────────────────────────────┘│
│                                                                              │
│  If Company Exists:                                                          │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │  ┌─────────────────────┐  ┌─────────────────────────────────────────┐  ││
│  │  │ Company Info        │  │ Deployment Status                       │  ││
│  │  │ - Name: Apple Inc   │  │ ✅ Stock Token: 0x3921...               │  ││
│  │  │ - Symbol: AAPL      │  │ ✅ AMM Pool: 0xc7F4...                  │  ││
│  │  │ - Status: Verified  │  │ ✅ Initial Liquidity: Initialized       │  ││
│  │  └─────────────────────┘  └─────────────────────────────────────────┘  ││
│  │                                                                          ││
│  │  ┌─────────────────────────────────────────────────────────────────────┐││
│  │  │ Documents                                                           │││
│  │  │ - Prospectus: Qm... [View]                                          │││
│  │  │ - Financials: Qm... [View]                                          │││
│  │  │ - Logo: Qm... [View]                                                │││
│  │  │ [Update Documents]                                                   │││
│  │  └─────────────────────────────────────────────────────────────────────┘││
│  └─────────────────────────────────────────────────────────────────────────┘│
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 8.3. Trade.vue

**Purpose**: Giao diện giao dịch cổ phiếu

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                            TRADE PAGE                                        │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌───────────────┐  ┌─────────────────────────────────┐  ┌────────────────┐ │
│  │ Markets List  │  │         Price Chart             │  │  Order Form    │ │
│  │               │  │                                 │  │                │ │
│  │ ┌───────────┐ │  │     ╭────────────────────╮     │  │ [Buy] [Sell]   │ │
│  │ │ AAPL      │ │  │    ╱                      ╲    │  │                │ │
│  │ │ $10.50    │ │  │   ╱                        ╲   │  │ Amount:        │ │
│  │ │ +2.5%     │ │  │  ╱                          ╲  │  │ [__________]   │ │
│  │ └───────────┘ │  │ ╱                            ╲ │  │                │ │
│  │ ┌───────────┐ │  │╱                              ╲│  │ Slippage: 0.5% │ │
│  │ │ GOOGL     │ │  │                                │  │                │ │
│  │ │ $15.20    │ │  │ Price: 10.50 BUSD              │  │ You receive:   │ │
│  │ │ -1.2%     │ │  │ 24h Change: +2.5%              │  │ ~95.23 AAPL    │ │
│  │ └───────────┘ │  │ Volume: 125K BUSD              │  │                │ │
│  │               │  │                                 │  │ [Swap]         │ │
│  │ Portfolio:    │  └─────────────────────────────────┘  └────────────────┘ │
│  │ BUSD: 1000    │                                                          │
│  │ AAPL: 50      │  ┌─────────────────────────────────────────────────────┐ │
│  │               │  │              Recent Trades                          │ │
│  └───────────────┘  │ Buy  | 100 BUSD → 9.52 AAPL | 2 min ago            │ │
│                     │ Sell | 50 AAPL → 520 BUSD  | 5 min ago             │ │
│                     └─────────────────────────────────────────────────────┘ │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 8.4. Admin.vue

**Purpose**: Admin panel để quản lý platform

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                            ADMIN PAGE                                        │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  Tabs: [Companies] [Trader KYC] [Minter Requests] [Settings]                 │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │                        Companies Tab                                     ││
│  │  ┌─────────────────────────────────────────────────────────────────────┐││
│  │  │ ID │ Name      │ Symbol │ Status    │ Token    │ Actions           │││
│  │  ├────┼───────────┼────────┼───────────┼──────────┼───────────────────┤││
│  │  │ 1  │ Apple Inc │ AAPL   │ ✅ Verified│ 0x3921..│ [Deploy] [View]   │││
│  │  │ 2  │ Google    │ GOOGL  │ ⏳ Pending │ -        │ [Verify] [Reject] │││
│  │  └─────────────────────────────────────────────────────────────────────┘││
│  └─────────────────────────────────────────────────────────────────────────┘│
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │                       Trader KYC Tab                                     ││
│  │  ┌─────────────────────────────────────────────────────────────────────┐││
│  │  │ ID │ Trader    │ Name     │ Status  │ Documents │ Actions          │││
│  │  ├────┼───────────┼──────────┼─────────┼───────────┼──────────────────┤││
│  │  │ 1  │ 0xABC...  │ John Doe │ Pending │ [View]    │ [Approve][Reject]│││
│  │  └─────────────────────────────────────────────────────────────────────┘││
│  └─────────────────────────────────────────────────────────────────────────┘│
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 9. Utilities

### 9.1. Toast Service

```javascript
// src/utils/toast.js
import { ref } from 'vue'

const toasts = ref([])
let toastId = 0

export function showToast(type, title, message, duration = 5000) {
  const id = ++toastId
  toasts.value.push({ id, type, title, message })

  setTimeout(() => {
    toasts.value = toasts.value.filter(t => t.id !== id)
  }, duration)
}

export default {
  success: (title, message) => showToast('success', title, message),
  error: (title, message) => showToast('error', title, message),
  warning: (title, message) => showToast('warning', title, message),
  info: (title, message) => showToast('info', title, message),

  // Transaction-specific toasts
  txStep: (title, message) => showToast('info', title, message),
  txPending: (message) => showToast('warning', 'Transaction Pending', message),
  txConfirmed: (title, message) => showToast('success', title, message),

  toasts
}
```

### 9.2. Confirm Utility

```javascript
// src/utils/confirm.js
import { ref } from 'vue'

const confirmState = ref({
  isOpen: false,
  title: '',
  message: '',
  confirmText: 'Confirm',
  cancelText: 'Cancel',
  resolve: null
})

export function confirm(options) {
  return new Promise((resolve) => {
    confirmState.value = {
      isOpen: true,
      title: options.title || 'Confirm',
      message: options.message || 'Are you sure?',
      confirmText: options.confirmText || 'Confirm',
      cancelText: options.cancelText || 'Cancel',
      resolve
    }
  })
}

export function handleConfirm() {
  confirmState.value.resolve(true)
  confirmState.value.isOpen = false
}

export function handleCancel() {
  confirmState.value.resolve(false)
  confirmState.value.isOpen = false
}

export { confirmState }
```

### 9.3. Encryption Utilities

```javascript
// src/utils/encryption.js

// AES-256-GCM for file encryption
export async function generateAESKey() {
  return await crypto.subtle.generateKey(
    { name: 'AES-GCM', length: 256 },
    true,
    ['encrypt', 'decrypt']
  )
}

export async function encryptAES(data, key) {
  const iv = crypto.getRandomValues(new Uint8Array(12))
  const ciphertext = await crypto.subtle.encrypt(
    { name: 'AES-GCM', iv },
    key,
    data
  )
  return { ciphertext: new Uint8Array(ciphertext), iv }
}

// ECIES for key encryption
export async function encryptECIES(data, recipientPublicKey) {
  const ephemeralWallet = ethers.Wallet.createRandom()
  const sharedSecret = deriveSharedSecret(recipientPublicKey, ephemeralPrivateKey)
  const encryptionKey = await deriveKeyFromSecret(sharedSecret, ephemeralPublicKey)

  const ciphertext = await crypto.subtle.encrypt(
    { name: 'AES-GCM', iv },
    encryptionKey,
    data
  )

  return { ephemeralPublicKey, iv, ciphertext, mac }
}

// High-level function
export async function encryptFileForRecipients(file, recipients) {
  const aesKey = await generateAESKey()
  const rawAESKey = await exportAESKey(aesKey)
  const { ciphertext, iv } = await encryptAES(fileData, aesKey)

  const encryptedKeys = []
  for (const recipient of recipients) {
    const encryptedKey = await encryptECIES(rawAESKey, recipient.publicKey)
    encryptedKeys.push({ recipient: recipient.address, encryptedKey })
  }

  return { encryptedFile, encryptedKeys, originalName, originalType, originalSize }
}
```

---

## 10. Flow triển khai

### 10.1. Wallet Connection Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        WALLET CONNECTION FLOW                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  1. User clicks "Connect Wallet"                                             │
│     └── App.vue: connectWallet()                                             │
│                                                                              │
│  2. Request accounts from MetaMask                                           │
│     └── ethereum.request({ method: 'eth_requestAccounts' })                  │
│                                                                              │
│  3. Create BrowserProvider and Signer                                        │
│     └── blockchain.connect()                                                 │
│                                                                              │
│  4. Load contract addresses from deployment.json                             │
│     └── loadContractAddresses()                                              │
│                                                                              │
│  5. Update UI state                                                          │
│     └── isConnected = true, account = address, balance = ETH                 │
│                                                                              │
│  6. Check user roles                                                         │
│     └── isAdmin, isMinter, isVerifiedTrader                                  │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 10.2. Trading Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           TRADING FLOW                                       │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  Step 1: Check Trader Verification                                           │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │  const isVerified = await blockchain.isVerifiedTrader(address)          ││
│  │  if (!isVerified) → Show TraderKYC component                            ││
│  └─────────────────────────────────────────────────────────────────────────┘│
│                                      │                                       │
│                                      ▼                                       │
│  Step 2: Select Token & Enter Amount                                         │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │  User selects company from market list                                  ││
│  │  User enters amount to buy/sell                                         ││
│  │  Calculate expected output with slippage                                ││
│  └─────────────────────────────────────────────────────────────────────────┘│
│                                      │                                       │
│                                      ▼                                       │
│  Step 3: Approve Token (if selling)                                          │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │  await blockchain.approveToken(tokenAddress, ammAddress, amount)        ││
│  │  Toast: "Approving tokens..."                                           ││
│  └─────────────────────────────────────────────────────────────────────────┘│
│                                      │                                       │
│                                      ▼                                       │
│  Step 4: Execute Swap                                                        │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │  await blockchain.swapTokens(ammAddress, amountIn, minOut, isBuy)       ││
│  │  Toast: "Swap completed!"                                               ││
│  └─────────────────────────────────────────────────────────────────────────┘│
│                                      │                                       │
│                                      ▼                                       │
│  Step 5: Update UI                                                           │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │  Refresh balances                                                       ││
│  │  Update price chart                                                     ││
│  │  Add to recent trades                                                   ││
│  └─────────────────────────────────────────────────────────────────────────┘│
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 10.3. Company Registration Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      COMPANY REGISTRATION FLOW                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  Step 1: Fill Registration Form                                              │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │  - Company Name                                                         ││
│  │  - Symbol (unique)                                                      ││
│  │  - Upload Prospectus PDF                                                ││
│  │  - Upload Financial Statements PDF                                      ││
│  │  - Upload Company Logo                                                  ││
│  └─────────────────────────────────────────────────────────────────────────┘│
│                                      │                                       │
│                                      ▼                                       │
│  Step 2: Upload Documents to IPFS                                            │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │  For each document:                                                     ││
│  │  1. Encrypt with AES-256-GCM                                            ││
│  │  2. Encrypt AES key with ECIES for recipients (owner + admin)           ││
│  │  3. Upload encrypted file to IPFS → Get CID                             ││
│  │  4. Register on EncryptedDocRegistry                                    ││
│  └─────────────────────────────────────────────────────────────────────────┘│
│                                      │                                       │
│                                      ▼                                       │
│  Step 3: Register Company On-Chain                                           │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │  await blockchain.registerCompany(                                      ││
│  │    name, symbol, ipfsProspectus, ipfsFinancials, ipfsLogo               ││
│  │  )                                                                       ││
│  │  → Returns companyId                                                    ││
│  └─────────────────────────────────────────────────────────────────────────┘│
│                                      │                                       │
│                                      ▼                                       │
│  Step 4: Wait for Admin Verification                                         │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │  Company status: PENDING                                                ││
│  │  Admin reviews documents and verifies                                   ││
│  │  Company status: VERIFIED                                               ││
│  └─────────────────────────────────────────────────────────────────────────┘│
│                                      │                                       │
│                                      ▼                                       │
│  Step 5: Deploy Token & AMM (via Backend)                                    │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │  POST /api/deploy/token → Deploy StockToken                             ││
│  │  POST /api/deploy/amm → Deploy StockAMM                                 ││
│  │  POST /api/initialize/pool → Initialize with liquidity                  ││
│  └─────────────────────────────────────────────────────────────────────────┘│
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 11. Hướng dẫn cài đặt

### 11.1. Prerequisites

```bash
# Node.js 18+
node --version  # v18.x.x

# npm
npm --version   # 9.x.x
```

### 11.2. Installation

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Copy environment file
cp .env.example .env
```

### 11.3. Environment Configuration

```env
# .env
VITE_IPFS_API_URL=http://localhost:5001
VITE_IPFS_GATEWAY_URL=http://localhost:8081
VITE_BACKEND_URL=http://localhost:3001
```

### 11.4. Development Server

```bash
# Start development server
npm run dev

# Server runs at http://localhost:3000
```

### 11.5. Production Build

```bash
# Build for production
npm run build

# Preview production build
npm run preview
```

### 11.6. Deployment Configuration

```javascript
// vite.config.js
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  server: {
    port: 3000,
    host: true
  },
  define: {
    global: 'globalThis'
  }
})
```

---

## 12. State Management

### 12.1. Reactive State in App.vue

```javascript
// App.vue <script setup>
import { ref, computed, onMounted, watch } from 'vue'
import blockchain from './utils/blockchain.js'

// Wallet state
const isConnected = ref(false)
const account = ref('')
const balance = ref('0')
const busdBalance = ref('0')

// User roles
const isAdmin = ref(false)
const isMinter = ref(false)
const isVerifiedTrader = ref(false)

// UI state
const showDropdown = ref(false)
const showDepositModal = ref(false)
const showWithdrawModal = ref(false)

// Portfolio
const stockHoldings = ref([])

// Computed
const shortAddress = computed(() =>
  `${account.value.slice(0, 6)}...${account.value.slice(-4)}`
)

// Methods
async function connectWallet() {
  const connected = await blockchain.connect()
  if (connected) {
    isConnected.value = true
    account.value = await blockchain.signer.getAddress()
    await refreshBalances()
    await checkUserRoles()
  }
}

async function refreshBalances() {
  balance.value = await blockchain.getBalance(account.value)
  busdBalance.value = await blockchain.getBaseTokenBalance(account.value)
  await loadStockHoldings()
}

async function checkUserRoles() {
  // Check if admin
  const registry = blockchain.getRegistry()
  const adminAddress = await registry.admin()
  isAdmin.value = account.value.toLowerCase() === adminAddress.toLowerCase()

  // Check if minter
  isMinter.value = await blockchain.isMinter(account.value)

  // Check if verified trader
  isVerifiedTrader.value = await blockchain.isVerifiedTrader(account.value)
}
```

### 12.2. Component Communication

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       COMPONENT COMMUNICATION                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  App.vue (Root)                                                              │
│  ├── Provides: account, isConnected, isAdmin, refreshBalances               │
│  │                                                                           │
│  ├── Home.vue                                                                │
│  │   └── Uses: blockchain service directly                                   │
│  │                                                                           │
│  ├── Register.vue                                                            │
│  │   ├── Uses: blockchain.registerCompany()                                  │
│  │   └── Emits: company-registered                                           │
│  │                                                                           │
│  ├── Trade.vue                                                               │
│  │   ├── Uses: blockchain.swapTokens()                                       │
│  │   ├── Child: TraderKYC.vue                                                │
│  │   │   └── Emits: kyc-submitted                                            │
│  │   └── Child: PriceChart.vue                                               │
│  │       └── Props: priceHistory                                             │
│  │                                                                           │
│  └── Admin.vue                                                               │
│      ├── Uses: blockchain.verifyTraderKYC()                                  │
│      └── Uses: blockchain.approveMinterRequest()                             │
│                                                                              │
│  Global Services:                                                            │
│  ├── blockchain.js → Singleton, imported where needed                        │
│  ├── toast.js → Reactive toasts array, used by Toast.vue                     │
│  └── confirm.js → Reactive state, used by ConfirmModal.vue                   │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Tài liệu tham khảo

- [Vue.js 3 Documentation](https://vuejs.org/)
- [Vue Router](https://router.vuejs.org/)
- [Ethers.js v6](https://docs.ethers.org/v6/)
- [TailwindCSS](https://tailwindcss.com/)
- [Chart.js](https://www.chartjs.org/)
- [Vite](https://vitejs.dev/)
- [HeadlessUI Vue](https://headlessui.com/vue/menu)
