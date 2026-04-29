# Báo Cáo Project: Community Treasury DAO

## 1. Mô Tả Bài Toán

Project xây dựng một DAO quản trị quỹ cộng đồng. Các quyết định chi tiêu quỹ được tạo thành proposal công khai, thành viên dùng token CGT để bỏ phiếu, và smart contract tự động chuyển ETH từ treasury nếu proposal được thông qua.

Ví dụ demo: đề xuất chi `1 ETH` để mua thiết bị cho câu lạc bộ sinh viên.

## 2. Thiết Kế Hệ Thống

Thành phần chính:

- `GovernanceToken.sol`: ERC-20 token CGT đại diện quyền biểu quyết.
- `MembershipNFT.sol`: NFT CDM đại diện tư cách thành viên.
- `CommunityDAO.sol`: contract quản trị proposal, voting, quorum và execute treasury.
- `frontend/src/App.vue`: giao diện Proposal Board, Voting Portal, IPFS upload/retrieve.

Luật quản trị:

- Chỉ ví có NFT CDM được gọi `propose()`.
- Ví có CGT được gọi `vote()`.
- Phiếu bầu có trọng số theo số dư CGT.
- Quorum mặc định là `20%` tổng cung token.
- Voting period demo là `300 giây`.
- Execute chỉ chạy sau deadline và khi proposal đạt quorum, đa số thuận.

## 3. Đối Chiếu Rubric

### Tiêu chí 1: Hợp Đồng Thông Minh

Đã có logic Solidity:

- `propose()`: tạo proposal mới với recipient, amount, title, summary và 3 CID IPFS.
- `vote()`: vote thuận/chống dựa trên số CGT của voter.
- `execute()`: tự động giải ngân ETH nếu proposal passed.

Ràng buộc:

- Quorum: `quorumVotes() = totalSupply * quorumPercent / 100`.
- Thời gian: không vote sau `endTime`, không execute trước `endTime`.

### Tiêu chí 2: Web3.py / Frontend

Project dùng frontend Web3 bằng `ethers.js`, tương đương lớp kết nối Web3 để tương tác ví MetaMask.

- Proposal Board hiển thị danh sách proposal và thanh tiến độ.
- Voting Portal cho phép chọn `Vote For` hoặc `Vote Against`.
- Trước khi vote/propose, frontend đọc `balanceOf` CGT và NFT để bật/tắt quyền thao tác.
- Contract vẫn kiểm tra lại để tránh bypass frontend.

### Tiêu chí 3: IPFS

Khi tạo proposal, frontend upload 3 loại dữ liệu:

- Proposal Documentation: PDF/Markdown/txt.
- Financial Reports: PDF/CSV/JSON/txt.
- Governance Rules: JSON.

Smart contract chỉ lưu CID:

- `documentationCid`
- `financialReportCid`
- `governanceRulesCid`

Người dùng bấm xem chi tiết, frontend gọi gateway IPFS để retrieve nội dung.

### Tiêu chí 4: ERC-20 / NFT

Đã có:

- ERC-20 Governance Token: `GovernanceToken.sol`.
- NFT Membership Card: `MembershipNFT.sol`.
- Minting: owner mint CGT/NFT cho thành viên.
- Weighted Voting: DAO đọc số dư CGT để tính trọng số phiếu.

## 4. Quy Trình Demo

1. Chạy local node:

```bash
npm run node
```

2. Deploy:

```bash
npm run deploy:local
```

3. Chạy frontend:

```bash
npm run frontend
```

4. Trên giao diện:

- Connect MetaMask với account Hardhat.
- Tạo proposal chi `1 ETH`.
- Dùng 2-3 ví khác nhau vote.
- Chờ hết `300 giây`.
- Nhấn `Execute` và kiểm tra recipient nhận ETH.

## 5. Ý Nghĩa DAO

DAO giải quyết **Principal-Agent Problem** bằng cách thay niềm tin vào một người quản lý bằng luật tự động:

- Người quản lý không thể tự ý chi quỹ.
- Thành viên token holder cùng biểu quyết.
- Bằng chứng proposal lưu bằng IPFS CID.
- Smart contract tự quyết định proposal có hợp lệ hay không.
- Treasury tự giải ngân khi đủ điều kiện, không cần admin.
