# Tích hợp IPFS (IPFS Integration)

## Mục lục
1. [Tổng quan](#1-tổng-quan)
2. [Kiến trúc hệ thống](#2-kiến-trúc-hệ-thống)
3. [Các thành phần chính](#3-các-thành-phần-chính)
4. [Flow triển khai](#4-flow-triển-khai)
5. [Mã hóa và bảo mật](#5-mã-hóa-và-bảo-mật)
6. [Smart Contract - EncryptedDocRegistry](#6-smart-contract---encrypteddocregistry)
7. [Hướng dẫn cài đặt](#7-hướng-dẫn-cài-đặt)
8. [API Reference](#8-api-reference)

---

## 1. Tổng quan

Hệ thống sử dụng **IPFS (InterPlanetary File System)** để lưu trữ phi tập trung các tài liệu quan trọng của công ty như:
- **Prospectus** (Bản cáo bạch)
- **Financial Statements** (Báo cáo tài chính)
- **Company Logo** (Logo công ty)
- **KYC Documents** (Tài liệu xác minh danh tính)

### Đặc điểm chính:
- **Lưu trữ phi tập trung**: Tài liệu được lưu trên mạng IPFS, không phụ thuộc vào server trung tâm
- **Mã hóa end-to-end**: Tài liệu được mã hóa AES-256-GCM trước khi upload
- **Kiểm soát truy cập on-chain**: Khóa mã hóa được lưu trên blockchain, chỉ người được ủy quyền mới giải mã được
- **Content-addressable**: Mỗi file có CID (Content Identifier) duy nhất dựa trên nội dung

---

## 2. Kiến trúc hệ thống

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              IPFS INTEGRATION ARCHITECTURE                   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌──────────────┐     ┌──────────────────┐     ┌──────────────────────────┐ │
│  │   Frontend   │────▶│  Encryption      │────▶│   IPFS Node (Docker)     │ │
│  │   (Vue.js)   │     │  Layer           │     │   - API: localhost:5001  │ │
│  └──────────────┘     └──────────────────┘     │   - Gateway: :8081       │ │
│         │                     │                └──────────────────────────┘ │
│         │                     │                              │               │
│         ▼                     ▼                              ▼               │
│  ┌──────────────┐     ┌──────────────────┐     ┌──────────────────────────┐ │
│  │  Blockchain  │◀───▶│ EncryptedDoc     │     │   Public IPFS Gateways   │ │
│  │  (Ethereum)  │     │ Registry.vy      │     │   - ipfs.io              │ │
│  └──────────────┘     └──────────────────┘     │   - pinata.cloud         │ │
│                                                 │   - cloudflare-ipfs.com  │ │
│                                                 └──────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Luồng dữ liệu:

```
┌─────────┐    ┌───────────┐    ┌──────────┐    ┌──────────┐    ┌───────────┐
│  User   │───▶│  Encrypt  │───▶│  Upload  │───▶│  Store   │───▶│  Register │
│  File   │    │  (AES+    │    │  to IPFS │    │  CID on  │    │  Keys on  │
│         │    │  ECIES)   │    │          │    │  IPFS    │    │  Chain    │
└─────────┘    └───────────┘    └──────────┘    └──────────┘    └───────────┘
```

---

## 3. Các thành phần chính

### 3.1. Frontend IPFS Utilities

#### `frontend/src/utils/ipfs.js`
Module cơ bản để upload file lên IPFS:

```javascript
// Upload file to IPFS
export async function uploadToIPFS(file) {
  const formData = new FormData()
  formData.append('file', file)

  const response = await fetch('http://localhost:5001/api/v0/add', {
    method: 'POST',
    body: formData
  })

  const result = await response.json()
  return result.Hash  // Returns IPFS CID
}

// Verify CID accessibility
export async function verifyCID(cid) { ... }

// Get IPFS gateway URL
export function getIPFSUrl(cid, gateway = 'ipfs.io') { ... }
```

#### `frontend/src/utils/encryptedIPFS.js`
Module upload file đã mã hóa:

```javascript
// Upload encrypted file to IPFS
export async function uploadEncryptedToIPFS(file, recipients, options = {}) {
  // 1. Encrypt file for all recipients
  const { encryptedFile, encryptedKeys, ... } = await encryptFileForRecipients(file, recipients)

  // 2. Upload encrypted file to IPFS
  const response = await fetch(`${IPFS_API_URL}/add`, {
    method: 'POST',
    body: formData
  })

  return { cid, encryptedKeys, metadata }
}

// Download and decrypt from IPFS
export async function downloadAndDecryptFromIPFS(cid, encryptedKey, privateKey, metadata) { ... }
```

### 3.2. Python IPFS Uploader

#### `scripts/ipfs_upload.py`
Script Python để upload file/JSON lên IPFS:

```python
class IPFSUploader:
    def __init__(self, api_url="http://127.0.0.1:5001"):
        self.api_url = api_url

    def upload_file(self, file_path):
        """Upload a file to IPFS, returns CID"""
        with open(file_path, 'rb') as f:
            files = {'file': f}
            response = requests.post(f"{self.api_url}/api/v0/add", files=files)
            return response.json()['Hash']

    def upload_json(self, data):
        """Upload JSON data to IPFS"""
        json_str = json.dumps(data, indent=2)
        files = {'file': ('data.json', json_str, 'application/json')}
        response = requests.post(f"{self.api_url}/api/v0/add", files=files)
        return response.json()['Hash']

    def get_file(self, cid, output_path=None):
        """Retrieve a file from IPFS"""
        response = requests.get(f"{self.api_url}/api/v0/cat?arg={cid}")
        return response.content
```

### 3.3. Smart Contract - EncryptedDocRegistry

#### `contracts/EncryptedDocRegistry.vy`
Vyper smart contract lưu trữ metadata và khóa mã hóa:

```vyper
struct DocumentMetadata:
    id: uint256
    uploader: address
    cid: String[64]              # IPFS CID
    doc_type: String[32]         # e.g., "kyc", "prospectus"
    original_name: String[128]
    original_size: uint256
    uploaded_at: uint256
    is_revoked: bool
    company_id: uint256

struct EncryptedKey:
    ephemeral_public_key: String[132]
    iv: String[32]
    ciphertext: String[128]
    mac: String[66]
```

---

## 4. Flow triển khai

### 4.1. Upload Document Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         ENCRYPTED DOCUMENT UPLOAD FLOW                       │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  Step 1: Generate AES Key                                                    │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │  const aesKey = await crypto.subtle.generateKey(                        ││
│  │    { name: 'AES-GCM', length: 256 }, true, ['encrypt', 'decrypt']       ││
│  │  )                                                                       ││
│  └─────────────────────────────────────────────────────────────────────────┘│
│                                      │                                       │
│                                      ▼                                       │
│  Step 2: Encrypt File with AES-256-GCM                                       │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │  const iv = crypto.getRandomValues(new Uint8Array(12))                  ││
│  │  const ciphertext = await crypto.subtle.encrypt(                        ││
│  │    { name: 'AES-GCM', iv }, aesKey, fileData                            ││
│  │  )                                                                       ││
│  └─────────────────────────────────────────────────────────────────────────┘│
│                                      │                                       │
│                                      ▼                                       │
│  Step 3: Encrypt AES Key with ECIES for Each Recipient                       │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │  for (const recipient of recipients) {                                  ││
│  │    const encryptedKey = await encryptECIES(rawAESKey, recipient.pubKey) ││
│  │    encryptedKeys.push({ recipient: recipient.address, encryptedKey })   ││
│  │  }                                                                       ││
│  └─────────────────────────────────────────────────────────────────────────┘│
│                                      │                                       │
│                                      ▼                                       │
│  Step 4: Upload Encrypted File to IPFS                                       │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │  POST http://localhost:5001/api/v0/add                                  ││
│  │  Body: FormData with encrypted file                                     ││
│  │  Response: { Hash: "Qm..." }  // IPFS CID                               ││
│  └─────────────────────────────────────────────────────────────────────────┘│
│                                      │                                       │
│                                      ▼                                       │
│  Step 5: Register Document On-Chain                                          │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │  await registry.upload_document(cid, docType, name, size, companyId)    ││
│  │  // Returns: docId                                                       ││
│  └─────────────────────────────────────────────────────────────────────────┘│
│                                      │                                       │
│                                      ▼                                       │
│  Step 6: Store Encrypted Keys On-Chain                                       │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │  await registry.add_recipients_batch(                                   ││
│  │    docId, addresses, ephemeralKeys, ivs, ciphertexts, macs              ││
│  │  )                                                                       ││
│  └─────────────────────────────────────────────────────────────────────────┘│
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 4.2. Download & Decrypt Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       ENCRYPTED DOCUMENT DOWNLOAD FLOW                       │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  Step 1: Get Document Metadata from Blockchain                               │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │  const doc = await registry.get_document(docId)                         ││
│  │  // Returns: { cid, original_name, is_revoked, ... }                    ││
│  └─────────────────────────────────────────────────────────────────────────┘│
│                                      │                                       │
│                                      ▼                                       │
│  Step 2: Get Encrypted Key for Current User                                  │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │  const encryptedKey = await registry.get_encrypted_key(docId, address)  ││
│  │  // Returns: { ephemeral_public_key, iv, ciphertext, mac }              ││
│  └─────────────────────────────────────────────────────────────────────────┘│
│                                      │                                       │
│                                      ▼                                       │
│  Step 3: Fetch Encrypted File from IPFS Gateway                              │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │  const response = await fetch(`http://localhost:8081/ipfs/${cid}`)      ││
│  │  const encryptedData = await response.arrayBuffer()                     ││
│  └─────────────────────────────────────────────────────────────────────────┘│
│                                      │                                       │
│                                      ▼                                       │
│  Step 4: Decrypt AES Key using ECIES                                         │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │  const rawAESKey = await decryptECIES(encryptedKey, privateKey)         ││
│  │  const aesKey = await importAESKey(rawAESKey)                           ││
│  └─────────────────────────────────────────────────────────────────────────┘│
│                                      │                                       │
│                                      ▼                                       │
│  Step 5: Decrypt File with AES-GCM                                           │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │  const iv = encryptedData.slice(0, 12)                                  ││
│  │  const ciphertext = encryptedData.slice(12)                             ││
│  │  const decrypted = await crypto.subtle.decrypt(                         ││
│  │    { name: 'AES-GCM', iv }, aesKey, ciphertext                          ││
│  │  )                                                                       ││
│  └─────────────────────────────────────────────────────────────────────────┘│
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 5. Mã hóa và bảo mật

### 5.1. Encryption Stack

| Layer | Algorithm | Purpose |
|-------|-----------|---------|
| File Encryption | AES-256-GCM | Mã hóa nội dung file |
| Key Encryption | ECIES (secp256k1) | Mã hóa AES key cho từng recipient |
| Key Derivation | HKDF-SHA256 | Derive encryption key từ shared secret |
| MAC | Keccak256 | Xác thực tính toàn vẹn |

### 5.2. ECIES Implementation

```javascript
// frontend/src/utils/encryption.js

// Encrypt data using ECIES
export async function encryptECIES(data, recipientPublicKey) {
  // 1. Generate ephemeral keypair
  const ephemeralWallet = ethers.Wallet.createRandom()

  // 2. Derive shared secret using ECDH
  const signingKey = new ethers.SigningKey(ephemeralPrivateKey)
  const sharedPoint = signingKey.computeSharedSecret(recipientPublicKey)
  const sharedSecret = ethers.getBytes(sharedPoint).slice(1, 33)

  // 3. Derive encryption key using HKDF
  const encryptionKey = await deriveKeyFromSecret(sharedSecret, ephemeralPublicKey)

  // 4. Encrypt with AES-GCM
  const ciphertext = await crypto.subtle.encrypt(
    { name: 'AES-GCM', iv }, encryptionKey, data
  )

  // 5. Compute MAC
  const mac = ethers.keccak256(ethers.concat([ephemeralPublicKey, iv, ciphertext]))

  return { ephemeralPublicKey, iv, ciphertext, mac }
}
```

### 5.3. Access Control

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           ACCESS CONTROL MATRIX                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  Document Owner (Uploader):                                                  │
│  ├── ✅ Upload document                                                      │
│  ├── ✅ Add recipients                                                       │
│  ├── ✅ Remove recipients                                                    │
│  └── ✅ Revoke document                                                      │
│                                                                              │
│  Admin:                                                                      │
│  ├── ✅ Add recipients                                                       │
│  ├── ✅ Remove recipients                                                    │
│  └── ✅ Revoke document                                                      │
│                                                                              │
│  Authorized Recipient:                                                       │
│  ├── ✅ Download & decrypt document                                          │
│  └── ❌ Cannot share access                                                  │
│                                                                              │
│  Unauthorized User:                                                          │
│  └── ❌ Cannot access document (no encrypted key)                            │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 6. Smart Contract - EncryptedDocRegistry

### 6.1. Contract Address
```
EncryptedDocRegistry: 0xc63b13636bFAb8c92abd1Dd442AA239A85acce46
```

### 6.2. Key Functions

| Function | Description | Access |
|----------|-------------|--------|
| `upload_document()` | Đăng ký document mới | Anyone |
| `add_recipient()` | Thêm recipient với encrypted key | Owner/Admin |
| `add_recipients_batch()` | Thêm nhiều recipients | Owner/Admin |
| `remove_recipient()` | Xóa quyền truy cập | Owner/Admin |
| `revoke_document()` | Thu hồi document | Owner/Admin |
| `get_document()` | Lấy metadata | Anyone |
| `get_encrypted_key()` | Lấy encrypted key | Anyone |
| `can_access()` | Kiểm tra quyền truy cập | Anyone |

### 6.3. Events

```vyper
event DocumentUploaded:
    doc_id: indexed(uint256)
    uploader: indexed(address)
    cid: String[64]
    doc_type: String[32]

event RecipientAdded:
    doc_id: indexed(uint256)
    recipient: indexed(address)

event RecipientRemoved:
    doc_id: indexed(uint256)
    recipient: indexed(address)

event DocumentRevoked:
    doc_id: indexed(uint256)
    revoked_by: indexed(address)
```

---

## 7. Hướng dẫn cài đặt

### 7.1. Khởi động IPFS Node (Docker)

```bash
# Pull IPFS image
docker pull ipfs/kubo:latest

# Run IPFS container
docker run -d --name ipfs-node \
  -p 4001:4001 \
  -p 5001:5001 \
  -p 8080:8080 \
  -p 8081:8081 \
  ipfs/kubo:latest

# Verify IPFS is running
curl http://localhost:5001/api/v0/id
```

### 7.2. Cấu hình CORS cho IPFS

```bash
# Enable CORS for frontend access
docker exec ipfs-node ipfs config --json API.HTTPHeaders.Access-Control-Allow-Origin '["*"]'
docker exec ipfs-node ipfs config --json API.HTTPHeaders.Access-Control-Allow-Methods '["PUT", "POST", "GET"]'

# Restart container
docker restart ipfs-node
```

### 7.3. Environment Variables

```env
# Frontend (.env)
VITE_IPFS_API_URL=http://localhost:5001
VITE_IPFS_GATEWAY_URL=http://localhost:8081

# Optional: Pinata (for production)
VITE_PINATA_API_KEY=your_api_key
VITE_PINATA_SECRET_KEY=your_secret_key

# Optional: Web3.Storage
VITE_WEB3_STORAGE_TOKEN=your_token
```

---

## 8. API Reference

### 8.1. IPFS HTTP API

#### Upload File
```http
POST http://localhost:5001/api/v0/add
Content-Type: multipart/form-data

Response:
{
  "Name": "filename.pdf",
  "Hash": "QmXoypizjW3WknFiJnKLwHCnL72vedxjQkDDP1mXWo6uco",
  "Size": "12345"
}
```

#### Get File
```http
GET http://localhost:8081/ipfs/{CID}

Response: File content
```

#### Copy to MFS
```http
POST http://localhost:5001/api/v0/files/cp?arg=/ipfs/{CID}&arg=/path/to/file
```

### 8.2. Frontend API

```javascript
import { uploadToIPFS, verifyCID, getIPFSUrl } from './utils/ipfs.js'
import { uploadEncryptedToIPFS, downloadAndDecryptFromIPFS } from './utils/encryptedIPFS.js'

// Basic upload
const cid = await uploadToIPFS(file)

// Encrypted upload with access control
const { cid, encryptedKeys, metadata } = await uploadEncryptedToIPFS(file, [
  { address: '0x...', publicKey: '0x04...' }
])

// Download and decrypt
const { data, blob, url, filename } = await downloadAndDecryptFromIPFS(
  cid, encryptedKey, privateKey, metadata
)
```

### 8.3. Blockchain API

```javascript
import blockchain from './utils/blockchain.js'

// Upload document metadata
const docId = await blockchain.uploadEncryptedDocument(
  cid, docType, originalName, originalSize, companyId
)

// Add recipient
await blockchain.addDocumentRecipient(docId, recipientAddress, encryptedKey)

// Get document
const doc = await blockchain.getEncryptedDocument(docId)

// Check access
const canAccess = await blockchain.canAccessDocument(docId, address)
```

---

## Tài liệu tham khảo

- [IPFS Documentation](https://docs.ipfs.tech/)
- [IPFS HTTP API Reference](https://docs.ipfs.tech/reference/kubo/rpc/)
- [Web Crypto API](https://developer.mozilla.org/en-US/docs/Web/API/Web_Crypto_API)
- [ECIES Encryption](https://cryptobook.nakov.com/asymmetric-key-ciphers/ecies-public-key-encryption)
- [Vyper Documentation](https://docs.vyperlang.org/)
