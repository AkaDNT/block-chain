# Tong quan du an DAO

Du an hien la ban DAO toi gian nhung da du de demo quy cong dong cho nhom, cau lac bo hoac doanh nghiep nho. He thong gom smart contract, giao dien Vue, luong tai tai lieu len IPFS va cac script Hardhat de chay blockchain local.

## Thanh phan chinh

- `GovernanceToken.sol`: token CGT dung de tinh trong so bieu quyet.
- `MembershipNFT.sol`: the thanh vien, dung de cap quyen tao de xuat.
- `CommunityDAO.sol`: giu quy ETH, tao de xuat, nhan phieu, kiem tra ty le toi thieu hop le va thuc thi khoan chi.
- `frontend/src/App.vue`: giao dien tieng Viet cho nguoi dung tao de xuat, bo phieu, xem tai lieu va quan ly demo.
- `frontend/src/utils/blockchain.js`: lop ket noi MetaMask/Hardhat va goi smart contract.
- `frontend/src/utils/ipfs.js`: tai va doc tai lieu IPFS, co CID gia khi chua chay IPFS local.

## Mo hinh van hanh

1. Thanh vien co NFT moi duoc tao de xuat chi quy.
2. De xuat phai co dia chi nhan tien, so ETH, tom tat va 3 tai lieu: de xuat, bao cao tai chinh, quy che bieu quyet.
3. Nguoi co CGT duoc bo phieu. Quy tac hien tai: 1 CGT = 1 phieu.
4. De xuat chi duoc thuc thi sau khi het thoi gian bo phieu, dat ty le toi thieu hop le va phieu thuan lon hon phieu chong.
5. Khi thuc thi, ETH duoc chuyen tu contract `CommunityDAO` sang dia chi nguoi nhan.

## Nang cap moi cho chuan doanh nghiep nho

- Giao dien nguoi dung da duoc chuyen sang tieng Viet, bao gom nut, nhan trang thai, canh bao, thong bao loi va huong dan thao tac.
- Sua cac chuoi tieng Viet bi loi ma hoa tren giao dien DAO.
- Them khu "Tinh trang quy" de hien so du quy, ty le toi thieu hop le, thoi gian bo phieu va dia chi contract.
- Them khu "Quyen cua vi hien tai" de nguoi dung biet minh co duoc tao de xuat va bo phieu hay khong.
- Them bang kiem tra truoc khi tao de xuat: so du sau chi, so tep bat buoc da chon va tinh hop le cua dia chi nhan.
- Chan tao de xuat neu so ETH de nghi chi lon hon so du quy hien co.
- Yeu cau so ETH de nghi chi phai lon hon 0.
- Them xac nhan trinh duyet truoc cac hanh dong quan trong: tao de xuat, bo phieu va thuc thi chi quy.
- Hien thoi gian con lai hoac thoi diem het han cho tung de xuat.
- Doi nhan trang thai de xuat sang tieng Viet: Dang bo phieu, Khong dat, Da thong qua, Da thuc thi.
- Doi cac loi cau hinh blockchain/IPFS co kha nang hien tren giao dien sang tieng Viet.

## Thiet ke SaaS moi cho user non-tech

Frontend da duoc thiet ke lai thanh app nhieu trang, giong mot san pham co the ban cho khach hang. Ban moi bo sung trung tam dieu hanh va workflow nghiep vu ro rang:

- Trung tam dieu hanh: suc khoe quy, hanh dong tiep theo, workflow 6 buoc va de xuat gan day.
- Thiet lap: onboarding to chuc, ten don vi, nguoi phu trach, email, linh vuc va mo ta.
- De xuat chi quy: tao ho so, chon nguoi nhan, chon ngan sach, kiem tra tai lieu, gui proposal on-chain va xu ly dong y/tu choi/chi quy.
- Nguoi nhan: CRUD nha cung cap, nhan su, doi tac va dia chi nhan tien.
- Ngan sach: CRUD hang muc chi, han muc ETH, nguoi phu trach, trang thai va mo ta.
- Thanh vien: CRUD thanh vien, vai tro, email, vi va trang thai.
- Tai lieu: CRUD ho so tai lieu, loai tai lieu, nguoi phu trach va CID/link luu tru.
- Bao cao: tong hop so lieu van hanh de nguoi quan ly doc nhanh.
- Cai dat: cap quyen demo, nap quy va thong tin cau hinh san pham.
- Quan tri: trang backend/admin, audit log va xuat du lieu demo.

Workflow chuan:

```text
Thiet lap -> Danh ba -> Ngan sach -> Ho so de xuat -> Bieu quyet -> Chi quy
```

Ban moi bo sung:

- Dang nhap demo theo vai tro: Quan tri, Ke toan, Thanh vien.
- Wizard thiet lap 4 buoc trong trang `Thiet lap`.
- Frontend dong bo CRUD voi backend API, neu API chua chay thi fallback ve `localStorage`.
- Backend co endpoint `POST /api/auth/login` de demo dang nhap.

Backend da co API SaaS mau tai `backend/server.js`:

- `GET /health`
- `GET /api/saas/summary`
- `GET /api/saas/:resource`
- `GET /api/saas/:resource/:id`
- `POST /api/saas/:resource`
- `PUT /api/saas/:resource/:id`
- `DELETE /api/saas/:resource/:id`
- `POST /api/saas/reset`

Trong do `resource` gom: `organizations`, `recipients`, `budgets`, `members`, `documents`, `auditLogs`. Du lieu backend hien duoc luu vao file JSON de demo nhanh, co the thay bang PostgreSQL/Supabase/Firebase khi dua thanh san pham that.

## Pham vi phu hop hien tai

Ban hien tai phu hop cho:

- Demo noi bo ve DAO quan ly quy.
- Mo phong quy cong dong/doanh nghiep nho voi luong duyet chi minh bach.
- Bai thuyet trinh ve token bieu quyet, NFT thanh vien, quorum va IPFS.
- Kiem thu local tren Hardhat voi MetaMask.

Ban hien tai chua nen dung cho tien that/mainnet vi con thieu:

- Kiem toan bao mat smart contract.
- Phan quyen admin san xuat va co che thu hoi quyen.
- Lich su su kien/indexer rieng de bao cao day du.
- Co che quan ly tai lieu that, pin IPFS ben vung va sao luu.
- Kiem thu giao dien tu dong va quy trinh phat hanh.

## Mot cau tom tat

Du an la mot DAO quan ly quy bang smart contract: thanh vien tao de xuat, nguoi co CGT bo phieu, tai lieu duoc gan CID IPFS, va quy chi tien tu dong khi de xuat dat dieu kien.
