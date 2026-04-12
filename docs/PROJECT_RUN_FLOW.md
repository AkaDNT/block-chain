# Project Run Flow (Toan bo he thong)

Tai lieu nay mo ta luong chay end-to-end cua project va chi ro moi buoc dang dung file nao.

## 1. Tong quan thanh phan

- Smart contracts (Vyper): `contracts/*.vy`
- Script deploy/test voi Ape: `scripts/*.py`, cau hinh trong `ape-config.yaml`
- Backend API deploy/init contract: `backend/server.js`
- Frontend Vue app: `frontend/src/*`
- Tai lieu tham khao chi tiet:
  - `CONTRACTS.md`
  - `docs/BACKEND_SERVICE.md`
  - `docs/FRONTEND_APPLICATION.md`
  - `docs/IPFS_INTEGRATION.md`

## 2. Flow khoi dong toan bo project (developer flow)

### Buoc 0 - Chuan bi moi truong

- Muc tieu: co Python + Node + Ape + geth + ipfs.
- File lien quan:
  - `scripts/setup.py` (kiem tra prerequisite, cai Ape plugin, cai npm frontend)
  - `Makefile` (target `setup`, `install`, `status`)
  - `ape-config.yaml` (network local, version vyper)
  - `.env.example` (bien moi truong tong quan)

### Buoc 1 - Cai dependencies

- Python side:
  - `pip install eth-ape`
  - `ape plugins install vyper geth`
- Frontend side:
  - `cd frontend && npm install`
- Backend side:
  - `cd backend && npm install`
- File lien quan:
  - `scripts/setup.py`
  - `frontend/package.json`
  - `backend/package.json`

### Buoc 2 - Compile contracts

- Lenh: `ape compile`
- File duoc su dung:
  - `contracts/BaseToken.vy`
  - `contracts/StockToken.vy`
  - `contracts/StockAMM.vy`
  - `contracts/Registry.vy`
  - `contracts/MinterRegistry.vy`
  - `contracts/TraderRegistry.vy`
  - `contracts/DepositContract.vy`
  - `contracts/EncryptedDocRegistry.vy`
  - `contracts/AMMFactory.vy`
- Cau hinh compile:
  - `ape-config.yaml` (vyper 0.4.3)

### Buoc 3 - Deploy core contracts

- Lenh chinh: `ape run deploy --network ethereum:local:geth-dev`
- Script thuc thi: `scripts/deploy.py`
- Script nay deploy theo thu tu:
  1. BaseToken
  2. Registry
  3. MinterRegistry
  4. TraderRegistry
  5. DepositContract
  6. Cap quyen minter cho DepositContract
  7. StockToken mau (AAPL)
  8. StockAMM
  9. Init pool AAPL/BUSD
  10. EncryptedDocRegistry
  11. Register company mau vao Registry
- Output tao ra:
  - `deployment.json` (root)
  - `frontend/public/deployment.json` (frontend doc contract address)

### Buoc 4 - Export ABI/bytecode cho backend

- Lenh: `ape run export_contracts --network ethereum:local:geth-dev`
- Script: `scripts/export_contracts.py`
- Output:
  - `backend/contracts/StockToken.json`
  - `backend/contracts/StockAMM.json`
  - `backend/contracts/Registry.json`
  - `backend/contracts/BaseToken.json`

### Buoc 5 - Cau hinh backend

- Copy va sua bien moi truong:
  - tu `backend/.env.example` sang `backend/.env`
- Bien can dung:
  - `DEPLOYER_PRIVATE_KEY`
  - `RPC_URL`
  - `REGISTRY_ADDRESS`
  - `BASE_TOKEN_ADDRESS`
  - `PORT`
- File backend su dung bien nay:
  - `backend/server.js`

### Buoc 6 - Start backend

- Lenh: `cd backend && npm start`
- Entrypoint:
  - `backend/server.js`
- Cac endpoint chinh:
  - `GET /health`
  - `POST /api/deploy/token`
  - `POST /api/deploy/amm`
  - `POST /api/initialize/pool`
  - `GET /api/deployer/balance`

### Buoc 7 - Start frontend

- Lenh: `cd frontend && npm run dev`
- Entrypoint:
  - `frontend/src/main.js`
- Root UI:
  - `frontend/src/App.vue`
- Router/pages:
  - `frontend/src/views/Home.vue`
  - `frontend/src/views/Register.vue`
  - `frontend/src/views/Trade.vue`
  - `frontend/src/views/Dashboard.vue`
  - `frontend/src/views/CompanyDashboard.vue`
  - `frontend/src/views/Admin.vue`

## 3. Runtime flow trong ung dung (nguoi dung thao tac)

## 3.1 Flow connect wallet + load blockchain service

1. Frontend mount app trong `frontend/src/main.js`.
2. Goi `blockchain.initialize()` trong `frontend/src/utils/blockchain.js`.
3. Service load contract addresses tu `frontend/public/deployment.json`.
4. App hien navigation/trang thai wallet trong `frontend/src/App.vue`.

## 3.2 Flow dang ky cong ty

1. User vao trang `frontend/src/views/Register.vue`.
2. Upload file prospectus/financial/logo len IPFS:
   - `frontend/src/utils/ipfs.js` (plain upload)
   - `frontend/src/utils/encryptedIPFS.js` (encrypted upload)
3. Dang ky cong ty on-chain qua `blockchain.registerCompany(...)`:
   - logic trong `frontend/src/utils/blockchain.js`
   - contract dich: `contracts/Registry.vy`
4. Neu dung encrypted docs:
   - ma hoa trong `frontend/src/utils/encryption.js`
   - quan ly key trong `frontend/src/utils/keyManager.js`
   - ghi metadata + encrypted keys on-chain vao `contracts/EncryptedDocRegistry.vy`.

## 3.3 Flow verify + deploy token/amm cho company

Co 2 cach:

- Cach A (qua Backend API):
  1. Admin thao tac tren `frontend/src/views/Admin.vue`.
  2. Frontend goi `http://localhost:3001/api/deploy/token` va `.../api/deploy/amm`.
  3. Backend xu ly trong `backend/server.js` bang `ethers.ContractFactory`.
  4. Backend cap nhat `Registry` qua `set_stock_token` va `set_amm_pool`.
  5. Frontend goi `.../api/initialize/pool` de init liquidity pool.

- Cach B (deploy truc tiep tu frontend wallet):
  1. Company thao tac tren `frontend/src/views/CompanyDashboard.vue` hoac `frontend/src/views/Register.vue`.
  2. Goi helper trong `frontend/src/utils/contractDeployer.js` (deploy StockToken/StockAMM).
  3. Update Registry qua `frontend/src/utils/blockchain.js`.

## 3.4 Flow trade (buy/sell)

1. User vao `frontend/src/views/Trade.vue`.
2. Lay ds company + pool gia qua `blockchain.getAllCompanies()`, `getAMMPrice()`, `getAMMReserves()`.
3. Truoc khi swap, frontend approve token qua `approveToken(...)` trong `frontend/src/utils/blockchain.js`.
4. Swap qua AMM:
   - `swap_base_for_stock`
   - `swap_stock_for_base`
   - contract: `contracts/StockAMM.vy`
5. Lich su trade lay tu event `Swap` (queryFilter) trong `frontend/src/utils/blockchain.js`.

## 3.5 Flow KYC trader/minter

- Trader KYC:
  - UI: `frontend/src/components/TraderKYC.vue`, `frontend/src/views/Trade.vue`
  - Contract: `contracts/TraderRegistry.vy`
  - Service call: `frontend/src/utils/blockchain.js`

- Minter request/admin review:
  - UI: `frontend/src/components/MinterRequestNotice.vue`, `frontend/src/views/Admin.vue`
  - Contract: `contracts/MinterRegistry.vy`
  - Service call: `frontend/src/utils/blockchain.js`

## 3.6 Flow encrypted document

1. Upload UI:
   - `frontend/src/components/EncryptedDocumentUpload.vue`
2. List/download UI:
   - `frontend/src/components/EncryptedDocumentList.vue`
3. Encrypt/decrypt:
   - `frontend/src/utils/encryptedIPFS.js`
   - `frontend/src/utils/encryption.js`
4. On-chain ACL + encrypted key metadata:
   - `contracts/EncryptedDocRegistry.vy`
5. IPFS integration doc:
   - `docs/IPFS_INTEGRATION.md`

## 4. Flow script CLI ho tro (ngoai UI)

- Full setup: `scripts/setup.py`
- Full deploy all-in-one: `scripts/deploy.py`
- Export ABI backend: `scripts/export_contracts.py`
- Init lai AMM pool thu cong: `scripts/init_pool.py`
- Cap ETH cho account khac: `scripts/fund_account.py`
- Mua co phieu qua CLI: `scripts/buy_stock.py`
- Ban co phieu qua CLI: `scripts/sell_stock.py`
- Test slippage/front-running: `scripts/test_slippage.py`
- Deploy rieng encrypted registry: `scripts/deploy_encrypted_doc_registry.py`
- Redeploy registry: `scripts/redeploy_registry.py`
- IPFS test:
  - `scripts/test_ipfs.py`
  - `scripts/test_ipfs.js`

## 5. Flow test

- Chay tat ca contract tests: `ape test`
- File test:
  - `tests/test_amm.py`
  - `tests/test_tokens.py`
  - `tests/test_registry.py`
  - `tests/test_minter_registry.py`
  - `tests/test_trader_registry.py`
  - `tests/test_deposit_contract.py`
  - `tests/test_encrypted_doc_registry.py`

## 6. Trinh tu chay de xai ngay (de xuat)

1. Start blockchain node va IPFS daemon.
2. `ape compile`
3. `ape run deploy --network ethereum:local:geth-dev`
4. `ape run export_contracts --network ethereum:local:geth-dev`
5. Cap nhat `backend/.env` theo address moi trong `deployment.json`.
6. `cd backend && npm start`
7. `cd frontend && npm run dev`
8. Mo app, connect wallet, test flow register -> verify/deploy -> init pool -> trade.

## 7. Luu y quan trong

- `start-backend.sh` dang hard-code path virtualenv theo may cu, can chinh lai neu dung script nay.
- `Makefile` chu yeu cho Linux/macOS (dung `pgrep`, `pkill`, shell syntax). Tren Windows, nen chay lenh thu cong tung buoc bang PowerShell.
- Trong `Makefile`, target `start` co typo `bakcend`, khong nen dung target nay neu chua sua.
