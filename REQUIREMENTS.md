# Yeu cau va cach chay du an

Tai lieu nay ghi cac thanh phan can co de chay ban demo DAO tren Windows.

## Moi truong can co

- Node.js va npm.
- Git.
- MetaMask tren Chrome hoac Edge.
- Dependency o thu muc goc: chay `npm install`.
- Dependency frontend: chay `npm --prefix frontend install`.
- Hardhat local blockchain.

Khong dung vi that hoac tien that cho ban demo local. Cac private key Hardhat trong du an chi dung de kiem thu.

## Tuy chon IPFS

Du an van chay duoc neu chua cai IPFS. Khi khong ket noi duoc IPFS local, frontend tao CID gia de demo luong tao de xuat.

Neu muon tai va doc tep that qua IPFS local, cai Kubo/IPFS va chay:

```powershell
ipfs daemon
```

Frontend dang thu cac cong IPFS sau:

```text
http://localhost:5001/api/v0/add
http://localhost:8080/ipfs/<CID>
http://localhost:8081/ipfs/<CID>
https://ipfs.io/ipfs/<CID>
https://gateway.pinata.cloud/ipfs/<CID>
```

## Cach chay moi lan demo

Mo terminal 1:

```powershell
cd G:\App\block-chain
npm run node
```

Mo terminal 2 va deploy contract:

```powershell
cd G:\App\block-chain
npm run deploy:local
```

Sau do chay frontend:

```powershell
npm run frontend
```

Neu muon chay API backend SaaS mau:

```powershell
npm run backend
```

Backend mac dinh chay tai:

```text
http://127.0.0.1:3002
```

Tai khoan dang nhap demo:

```text
admin@fundflow.local / demo123    -> Quan tri
finance@fundflow.local / demo123  -> Ke toan
member@fundflow.local / demo123   -> Thanh vien
```

Mo trinh duyet:

```text
http://127.0.0.1:3000/
```

## Cau hinh MetaMask

Them mang local:

```text
Network name: Hardhat Local
RPC URL: http://127.0.0.1:8545
Chain ID: 31337
Currency symbol: ETH
```

Import cac vi test Hardhat can dung:

```text
Account #0
Address: 0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266
Private key: 0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80

Account #1
Address: 0x70997970C51812dc3A010C7d01b50e0d17dc79C8
Private key: 0x59c6995e998f97a5a0044966f0945389dc9e86dae88c7a8412f4603b6b78690d

Account #2
Address: 0x3C44CdDdB6a900fa2b585dd299e03d12FA4293BC
Private key: 0x5de4111afa1a4b94908f83103eb1f1706367c2e68ca870fc3fb9a804cdab365a

Account #3
Address: 0x90F79bf6EB2c4f870365E785982E1f101E93b906
Private key: 0x7c852118294e51e653712a81e05800f419141751be58f605c371e15141b007a6
```

## Dieu kien de tao de xuat trong giao dien moi

Giao dien da them cac kiem tra phu hop cho doanh nghiep nho. De tao de xuat thanh cong, can:

- Vi dang ket noi co the thanh vien NFT.
- Dia chi nhan tien la dia chi vi day du dang `0x...`.
- So ETH de nghi chi lon hon 0.
- So ETH de nghi chi khong vuot qua so du quy hien co.
- Chon du 3 tep: tai lieu de xuat, bao cao tai chinh, quy che bieu quyet.
- Xac nhan hop thoai trinh duyet truoc khi gui giao dich.
- Xac nhan giao dich trong MetaMask.

## Cac trang SaaS va flow cho user non-tech

Frontend hien duoc thiet ke thanh app nhieu trang co flow ro rang:

- `Trung tam dieu hanh`: dashboard, hanh dong tiep theo va workflow 6 buoc.
- `Thiet lap`: cau hinh to chuc.
- `De xuat chi quy`: tao ho so, kiem tra dieu kien, gui proposal on-chain, bo phieu va chi quy.
- `Nguoi nhan`: CRUD nha cung cap, nhan su, doi tac hoac dia chi nhan tien khac.
- `Ngan sach`: CRUD hang muc chi, han muc ETH, nguoi phu trach, trang thai va mo ta.
- `Thanh vien`: CRUD user noi bo, vai tro, email, vi va trang thai.
- `Tai lieu`: CRUD ho so, loai tai lieu va CID/link luu tru.
- `Bao cao`: tong hop so lieu van hanh.
- `Cai dat`: cap quyen demo va nap quy.
- `Quan tri`: audit log va xuat du lieu demo.

Workflow chuan tren giao dien:

```text
Thiet lap -> Danh ba -> Ngan sach -> Ho so de xuat -> Bieu quyet -> Chi quy
```

Trang `Thiet lap` co wizard 4 buoc:

```text
Ho so to chuc -> Danh ba nhan tien -> Ke hoach ngan sach -> Quyen van hanh
```

Frontend se uu tien dong bo CRUD voi backend API. Neu backend chua chay, app tu dong fallback sang `localStorage` de demo khong bi dung.

Proposal da gui len blockchain khong co chuc nang sua/xoa truc tiep. Neu can thay doi noi dung sau khi gui, tao proposal moi va bo phieu lai.

## API backend SaaS mau

Backend co cac endpoint:

```text
GET    /health
POST   /api/auth/login
GET    /api/saas/summary
GET    /api/saas/:resource
GET    /api/saas/:resource/:id
POST   /api/saas/:resource
PUT    /api/saas/:resource/:id
DELETE /api/saas/:resource/:id
POST   /api/saas/reset
```

Gia tri `resource` hop le:

```text
organizations
recipients
budgets
members
documents
auditLogs
```

Du lieu backend hien duoc luu tai:

```text
backend/data/saas-db.json
```

Day la backend demo de ban san pham cho user non-tech. Khi dua len production nen thay bang database that, dang nhap, phan quyen user, audit log bat bien va backup.

## Luong demo de xuat va bo phieu

1. Bam `Ket noi vi`.
2. Kiem tra khu `Quyen cua vi hien tai`.
3. Nhap ten de xuat, tom tat, dia chi nhan tien va so ETH.
4. Chon du 3 tep bat buoc.
5. Bam `Tai len IPFS va tao de xuat`.
6. Doi MetaMask sang vi co CGT de bo phieu.
7. Bam `Bo phieu thuan` hoac `Bo phieu chong`.
8. Sau khi het thoi gian bo phieu, neu de xuat dat dieu kien, bam `Thuc thi chi quy`.

## Lenh kiem tra

Kiem tra smart contract:

```powershell
cd G:\App\block-chain
npm test
```

Build frontend:

```powershell
cd G:\App\block-chain
npm run build
```

## Loi thuong gap

### Thieu deployment.json

Chay lai:

```powershell
cd G:\App\block-chain
npm run deploy:local
```

### MetaMask sai mang

Kiem tra MetaMask dang chon:

```text
Hardhat Local
RPC URL: http://127.0.0.1:8545
Chain ID: 31337
```

Neu van loi, xoa mang Hardhat Local trong MetaMask, tao lai dung RPC va refresh trang.

### Khong doc duoc CID IPFS

Neu dang dung CID gia, tep se khong mo duoc qua gateway cong khai. Muon doc tep that, chay:

```powershell
ipfs daemon
```

Sau do tao de xuat moi de tep duoc tai len IPFS that.

### Khong tao duoc de xuat vi vuot quy

Giao dien moi khong cho tao de xuat co so ETH lon hon so du quy. Hay giam so ETH can chi hoac dung khu `Cap quyen demo` de nap them ETH vao quy.
