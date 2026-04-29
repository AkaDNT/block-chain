# DAO Blockchain Project

Project này hiện thực mô hình **Community Treasury DAO**: thành viên sở hữu token quản trị CGT bỏ phiếu cho các đề xuất chi tiêu quỹ; ví có Membership NFT mới được tạo đề xuất; khi đề xuất đạt quorum và hết thời gian biểu quyết, smart contract tự chuyển ETH từ treasury đến người nhận.

## Luật Chơi DAO

- **Governance Token**: `Community Governance Token (CGT)`, ERC-20.
- **Membership Card**: `Community DAO Membership (CDM)`, NFT dùng để định danh thành viên chính thức.
- **Quyền tạo đề xuất**: ví phải sở hữu ít nhất 1 NFT CDM.
- **Quyền bỏ phiếu**: ví phải sở hữu CGT.
- **Weighted Voting**: 1 CGT = 1 phiếu.
- **Quorum**: tổng phiếu `For + Against` phải đạt ít nhất `20%` tổng cung CGT.
- **Voting Period**: mặc định `300 giây` để dễ demo; có thể tăng trong `scripts/deploy-dao.js`.
- **Execute**: chỉ được gọi sau khi hết hạn biểu quyết, đề xuất đạt quorum, phiếu thuận lớn hơn phiếu chống, và treasury đủ ETH.

## Smart Contracts

### `contracts/GovernanceToken.sol`

ERC-20 tối giản cho quyền biểu quyết.

Nghiệp vụ chính:

- `mint(address to, uint256 amount)`: cấp CGT cho thành viên khi đóng góp công sức hoặc tài chính.
- `balanceOf(address account)`: frontend/Web3 dùng để kiểm tra quyền bỏ phiếu.
- `totalSupply()`: DAO dùng để tính quorum.

### `contracts/MembershipNFT.sol`

NFT thành viên chính thức.

Nghiệp vụ chính:

- `mint(address to)`: cấp membership card cho thành viên.
- `balanceOf(address account)`: DAO kiểm tra điều kiện `propose()`.

### `contracts/CommunityDAO.sol`

Contract quản trị trung tâm, giữ treasury ETH và tự thực thi đề xuất.

Nghiệp vụ chính:

- `propose(...)`: tạo đề xuất công khai, gồm người nhận, số ETH, tiêu đề, mô tả và 3 CID IPFS.
- `vote(uint256 proposalId, bool support)`: bỏ phiếu thuận/chống theo số CGT đang nắm giữ.
- `execute(uint256 proposalId)`: tự động chuyển ETH nếu đề xuất đã qua.

Ràng buộc logic:

- `onlyMember`: chỉ NFT holder mới tạo proposal.
- `block.timestamp <= endTime`: không cho vote sau hạn.
- `block.timestamp > endTime`: không cho execute sớm.
- `totalVotes >= quorumVotes()`: phải đạt quorum.
- `forVotes > againstVotes`: đa số phải tán thành.
- `hasVoted[proposalId][voter]`: mỗi ví chỉ bỏ phiếu một lần.

IPFS fields lưu trong proposal:

- `documentationCid`: Proposal Documentation, ví dụ PDF/Markdown mô tả lý do và kế hoạch.
- `financialReportCid`: Financial Reports, ví dụ báo cáo tài chính hoặc minh chứng chi tiêu.
- `governanceRulesCid`: Governance Rules, file JSON chứa hiến pháp/quy định DAO.

## Frontend

Frontend Vue nằm ở `frontend/src/App.vue`.

Các màn hình đáp ứng rubric:

- **Proposal Board**: danh sách proposal, trạng thái, deadline, người nhận, số ETH và progress bar `For`, `Against`, `Quorum`.
- **Voting Portal**: nút `Vote For`, `Vote Against`, ký giao dịch qua MetaMask.
- **IPFS Retrieve**: các nút `View documentation`, `View financials`, `View rules` tải dữ liệu từ gateway IPFS.
- **Minting Demo**: cấp CGT/NFT và fund treasury để demo trên local chain.

Web3 security/fairness:

- Frontend gọi `getMemberProfile()` trong `frontend/src/utils/blockchain.js` để đọc `balanceOf` CGT và NFT trước khi bật propose/vote.
- Contract vẫn là lớp bảo vệ cuối cùng: không có CGT sẽ revert `NO_VOTING_POWER`, không có NFT sẽ revert `MEMBERSHIP_REQUIRED`.

## Workflow Demo

1. Cài dependencies:

```bash
npm install
npm --prefix frontend install
```

2. Chạy local blockchain:

```bash
npm run node
```

3. Mở terminal khác, deploy contract:

```bash
npm run deploy:local
```

Lệnh này tạo `deployment.json` ở root và `frontend/public/deployment.json`.

4. Chạy frontend:

```bash
npm run frontend
```

5. Demo trên MetaMask:

- Import 2-3 private key từ Hardhat node.
- Ví deployer đã có CGT, NFT và DAO treasury có ETH.
- Tạo proposal chi `1 ETH` cho một ví nhận.
- Dùng 2-3 ví vote thuận/chống.
- Sau `300 giây`, nhấn `Execute`; ETH được chuyển tự động từ DAO contract.

## IPFS

Frontend ưu tiên upload qua local IPFS API:

- API: `http://localhost:5001/api/v0/add`
- Gateway: `http://localhost:8080/ipfs/{cid}` hoặc `http://localhost:8081/ipfs/{cid}`

Nếu chưa chạy IPFS, frontend tạo mock CID để vẫn demo được luồng giao dịch. Để demo retrieve thật, cần chạy IPFS daemon:

```bash
ipfs daemon
```

## Principal-Agent Problem

Trong tổ chức truyền thống, người sở hữu quỹ phải tin người quản lý sẽ hành động đúng lợi ích chung. Đây là **Principal-Agent Problem**: người đại diện có thể chi tiêu sai mục đích, trì hoãn minh bạch, hoặc ưu tiên lợi ích cá nhân.

DAO trong project này giảm phụ thuộc vào cá nhân lãnh đạo bằng cách:

- Mọi đề xuất chi tiêu đều công khai trên chain.
- Nội dung dài và bằng chứng tài chính được lưu trên IPFS bằng CID không thể tùy tiện thay đổi.
- Quyền quyết định thuộc về token holders, không phải admin.
- Smart contract tự kiểm tra quorum, deadline, đa số phiếu và tự execute.
- Treasury chỉ chuyển tiền khi các điều kiện quản trị được thỏa mãn.

Kết quả là quyền quản lý quỹ được thay bằng luật minh bạch trong smart contract.
