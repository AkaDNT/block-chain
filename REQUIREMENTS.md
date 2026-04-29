# Requirements & Run Guide

File này ghi toàn bộ những gì cần để chạy project DAO trên máy Windows.

## 1. Trạng Thái Đã Chuẩn Bị

Môi trường trên máy hiện tại đã có:

- Node.js: `v24.15.0`
- npm: `11.12.1`
- Git: `2.54.0.windows.1`
- Root dependencies: đã chạy `npm install`
- Frontend dependencies: đã chạy `npm install` trong thư mục `frontend`
- Smart contract tests: đã chạy thành công `2 passing`
- Frontend build: đã build thành công

## 2. Phần Cần Làm Thủ Công Một Lần

### Cài MetaMask

Cài extension MetaMask trên Chrome hoặc Edge:

```text
https://metamask.io/download/
```

Không dùng ví thật/mainnet cho project này. Chỉ dùng ví test local của Hardhat.

### IPFS

IPFS là phần tùy chọn.

Project vẫn chạy được nếu chưa cài IPFS, vì frontend sẽ tạo mock CID để demo luồng tạo proposal. Nếu muốn upload/retrieve IPFS thật, cài Kubo/IPFS:

```text
https://docs.ipfs.tech/install/
```

Sau khi cài, chạy:

```powershell
ipfs daemon
```

## 3. Cách Chạy Project Mỗi Lần Demo

Mở 2 terminal PowerShell.

### Terminal 1: Chạy Blockchain Local

```powershell
cd G:\App\block-chain
npm run node
```

Để terminal này chạy nguyên, không tắt.

Hardhat sẽ mở RPC tại:

```text
http://127.0.0.1:8545
```

### Terminal 2: Deploy Contract

```powershell
cd G:\App\block-chain
npm run deploy:local
```

Lệnh này deploy:

- `GovernanceToken`
- `MembershipNFT`
- `CommunityDAO`

Và tự tạo file:

```text
frontend/public/deployment.json
```

### Terminal 2: Chạy Frontend

Sau khi deploy xong:

```powershell
npm run frontend
```

Mở trình duyệt:

```text
http://127.0.0.1:3000/
```

## 4. Cấu Hình MetaMask

Thêm network local:

```text
Network name: Hardhat Local
RPC URL: http://127.0.0.1:8545
Chain ID: 31337
Currency symbol: ETH
```

Import các ví test sau vào MetaMask.

Account #0, dùng để deploy/admin demo:

```text
Address:
0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266

Private key:
0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80
```

Account #1, dùng làm member vote:

```text
Address:
0x70997970C51812dc3A010C7d01b50e0d17dc79C8

Private key:
0x59c6995e998f97a5a0044966f0945389dc9e86dae88c7a8412f4603b6b78690d
```

Account #2, dùng làm member vote:

```text
Address:
0x3C44CdDdB6a900fa2b585dd299e03d12FA4293BC

Private key:
0x5de4111afa1a4b94908f83103eb1f1706367c2e68ca870fc3fb9a804cdab365a
```

Account #3, dùng làm recipient nhận tiền treasury:

```text
Address:
0x90F79bf6EB2c4f870365E785982E1f101E93b906

Private key:
0x7c852118294e51e653712a81e05800f419141751be58f605c371e15141b007a6
```

Cảnh báo: Đây là private key công khai của Hardhat, chỉ dùng local. Không gửi tiền thật vào các ví này.

## 5. Demo Theo Rubric

### Bước 1: Connect ví

- Mở `http://127.0.0.1:3000/`
- Chọn network `Hardhat Local` trong MetaMask
- Bấm `Connect MetaMask`

### Bước 2: Tạo Proposal

Dùng Account #0 hoặc Account #1 vì các ví này đã được cấp NFT membership khi deploy.

Điền:

- Title: ví dụ `Buy club equipment`
- Recipient: dùng address Account #3
- ETH amount: ví dụ `1`
- Proposal PDF/MD: chọn file bất kỳ `.md`, `.txt`, hoặc `.pdf`
- Financial report: chọn file bất kỳ `.pdf`, `.csv`, `.json`, hoặc `.txt`
- Governance rules JSON: chọn file `.json`

Bấm:

```text
Upload to IPFS and Propose
```

### Bước 3: Vote

Dùng MetaMask chuyển qua Account #1 hoặc Account #2.

Trên proposal vừa tạo:

- Bấm `Vote For` để tán thành
- Hoặc `Vote Against` để phản đối

Trọng số phiếu = số CGT token ví đang nắm giữ.

### Bước 4: Execute

Voting period mặc định là `300 giây`.

Sau khi hết 5 phút, nếu proposal:

- Đạt quorum 20%
- Phiếu thuận lớn hơn phiếu chống
- Treasury đủ ETH

Thì bấm:

```text
Execute
```

Contract sẽ tự chuyển ETH từ DAO treasury sang recipient.

## 6. Lệnh Kiểm Tra

Chạy test smart contract:

```powershell
cd G:\App\block-chain
npm test
```

Build frontend:

```powershell
cd G:\App\block-chain\frontend
npm run build
```

## 7. Lỗi Hay Gặp

### Lỗi `npm.ps1 cannot be loaded`

Không dùng:

```powershell
npm install
```

Dùng:

```powershell
npm install
```

### MetaMask không connect được

Kiểm tra:

- Hardhat node đang chạy ở terminal 1.
- MetaMask đang chọn network `Hardhat Local`.
- RPC URL là `http://127.0.0.1:8545`.
- Chain ID là `31337`.

### Frontend báo thiếu deployment

Chạy lại:

```powershell
cd G:\App\block-chain
npm run deploy:local
```

### Lỗi `could not decode result data`, `BAD_DATA`, hoặc `quorumVotes()`

Lỗi này nghĩa là frontend đang gọi địa chỉ contract nhưng trên network MetaMask đang chọn không có contract ở địa chỉ đó.

Cách sửa nhanh:

1. Kiểm tra terminal Hardhat node vẫn đang chạy:

```powershell
cd G:\App\block-chain
npm run node
```

2. Mở terminal khác và deploy lại:

```powershell
cd G:\App\block-chain
npm run deploy:local
```

3. Trong MetaMask chọn đúng network:

```text
Network: Hardhat Local
RPC URL: http://127.0.0.1:8545
Chain ID: 31337
```

Nếu bạn đã có network tên `Hardhat Local` nhưng vẫn lỗi, hãy xóa network đó trong MetaMask rồi tạo lại. Quan trọng là dùng đúng RPC:

```text
http://127.0.0.1:8545
```

Không dùng nhầm các RPC khác như:

```text
http://localhost:7545
http://127.0.0.1:7545
Sepolia
Ethereum Mainnet
```

4. Refresh lại trình duyệt ở:

```text
http://127.0.0.1:3000/
```

Nếu vẫn lỗi, vào MetaMask:

```text
Settings -> Advanced -> Clear activity and nonce data
```

Rồi refresh trang.

### IPFS không retrieve được file

Nếu chưa chạy IPFS thật, mock CID sẽ không mở được qua gateway. Để retrieve thật:

```powershell
ipfs daemon
```

Sau đó tạo proposal mới để file được upload thật.

### Lỗi `network does not support ENS`

Lỗi này thường xuất hiện khi ô địa chỉ ví không đúng định dạng. Hardhat local không hỗ trợ ENS name, nên không nhập tên kiểu:

```text
alice.eth
Account #3
recipient
private key
```

Ở ô `Recipient address`, hãy nhập **address**, ví dụ:

```text
0x90F79bf6EB2c4f870365E785982E1f101E93b906
```

Không nhập private key. Private key chỉ dùng để import ví vào MetaMask.
