# DAO Project Summary

File này giải thích toàn bộ project DAO từ góc nhìn người mới bắt đầu blockchain.

## 1. Blockchain Là Gì?

Blockchain là một cuốn sổ cái công khai. Mỗi hành động như deploy contract, mint token, tạo proposal, vote, execute hoặc chuyển ETH đều là một giao dịch được ghi lại trên blockchain.

Trong project này ta dùng **Hardhat local blockchain**, tức blockchain giả lập chạy trên máy cá nhân:

```text
http://127.0.0.1:8545
```

Các account Hardhat như Account #0, #1, #2, #3 đều là ví test có sẵn ETH giả. Không dùng các ví này trên mainnet.

## 2. Smart Contract Là Gì?

Smart contract là chương trình chạy trên blockchain. Sau khi deploy, contract có một địa chỉ riêng.

Project có 3 smart contract chính:

```text
GovernanceToken.sol
MembershipNFT.sol
CommunityDAO.sol
```

Người dùng tương tác với contract thông qua MetaMask và frontend, thay vì gọi server truyền thống.

## 3. DAO Là Gì?

DAO là viết tắt của:

```text
Decentralized Autonomous Organization
```

Hiểu đơn giản: DAO là một tổ chức vận hành bằng luật trong smart contract.

Ví dụ tổ chức truyền thống:

```text
CLB có quỹ chung.
Chủ nhiệm hoặc thủ quỹ tự quyết định chi tiền.
Thành viên phải tin người quản lý.
```

DAO:

```text
Quỹ nằm trong smart contract.
Ai muốn chi tiền phải tạo proposal.
Thành viên bỏ phiếu.
Nếu đủ điều kiện, smart contract tự chuyển tiền.
Không cần admin duyệt thủ công.
```

## 4. Treasury Là Gì?

Treasury là kho quỹ của DAO.

Trong project này, treasury chính là ETH đang nằm trong contract `CommunityDAO`.

Khi deploy, script nạp vào DAO:

```text
3 ETH
```

Nếu proposal chi 1 ETH được execute:

```text
DAO treasury: 3 ETH -> 2 ETH
Recipient: tăng thêm 1 ETH
```

Lưu ý: tiền không chuyển từ Account #0 sang recipient lúc execute. Tiền chuyển từ **DAO contract** sang recipient.

## 5. Governance Token Là Gì?

Governance token là token dùng để biểu quyết.

Trong project:

```text
Token name: Community Governance Token
Symbol: CGT
```

Luật biểu quyết:

```text
1 CGT = 1 vote
```

Ví dụ:

```text
Account #1 có 3000 CGT
Account #2 có 2000 CGT
```

Nếu cả hai vote for:

```text
For votes = 5000 CGT
```

Đây gọi là **weighted voting**, tức phiếu bầu có trọng số theo số token.

## 6. Membership NFT Là Gì?

NFT trong project này là thẻ thành viên.

```text
MembershipNFT / CDM
```

Luật:

```text
Chỉ ví có Membership NFT mới được tạo proposal.
```

Mục đích:

```text
Người có token CGT: có quyền vote.
Người có NFT CDM: là thành viên chính thức, có quyền tạo proposal.
```

## 7. Quorum Là Gì?

Quorum là ngưỡng tham gia tối thiểu để proposal có hiệu lực.

Nếu không có quorum, một lượng phiếu rất nhỏ cũng có thể quyết định tiền của cả DAO.

Trong project:

```text
Quorum = 20% tổng cung CGT
Tổng cung CGT = 10000
Quorum cần = 2000 CGT
```

Proposal chỉ hợp lệ nếu:

```text
For votes + Against votes >= 2000 CGT
```

## 8. Proposal Là Gì?

Proposal là một đề xuất quản trị.

Ví dụ:

```text
Chi 1 ETH để mua thiết bị cho câu lạc bộ.
```

Trong project, proposal gồm:

```text
title
summary
recipient
amount ETH
documentation CID
financial report CID
governance rules CID
start time
end time
for votes
against votes
executed hay chưa
```

Nếu proposal pass, DAO sẽ chuyển `amount` ETH từ treasury tới `recipient`.

## 9. IPFS Là Gì?

Blockchain lưu dữ liệu rất đắt, nên không nên lưu file PDF hoặc tài liệu dài trực tiếp lên chain.

IPFS là hệ thống lưu file phi tập trung. Khi upload file, ta nhận được một mã gọi là CID.

Smart contract chỉ lưu CID, không lưu cả file.

Project dùng 3 loại dữ liệu IPFS:

```text
Proposal Documentation
Financial Reports
Governance Rules
```

Flow:

```text
Upload file lên IPFS
Nhận CID
Lưu CID vào proposal trên smart contract
Người dùng bấm View để đọc lại file từ IPFS
```

Nếu chưa chạy IPFS thật, frontend tạo mock CID để demo luồng hoạt động.

## 10. Các Contract Trong Project

### GovernanceToken.sol

Vai trò:

```text
Tạo token CGT.
Lưu số dư token của từng ví.
Cho phép mint token demo.
DAO đọc balanceOf để tính trọng số phiếu.
```

Hàm quan trọng:

```text
mint(address to, uint256 amount)
balanceOf(address account)
totalSupply()
transfer(address to, uint256 amount)
```

### MembershipNFT.sol

Vai trò:

```text
Tạo NFT thẻ thành viên.
Lưu ví nào đang sở hữu NFT.
DAO kiểm tra NFT để cho phép propose.
```

Hàm quan trọng:

```text
mint(address to)
balanceOf(address account)
ownerOf(uint256 tokenId)
```

### CommunityDAO.sol

Vai trò:

```text
Giữ treasury ETH.
Tạo proposal.
Nhận vote.
Kiểm tra quorum và deadline.
Execute proposal để chuyển ETH.
```

Hàm quan trọng:

```text
propose(...)
vote(uint256 proposalId, bool support)
execute(uint256 proposalId)
quorumVotes()
state(uint256 proposalId)
getAllProposals()
```

## 11. Flow Chạy Project Từ Đầu Đến Cuối

### Bước 1: Chạy blockchain local

Chạy:

```powershell
npm.cmd run node
```

Hardhat tạo blockchain local và các ví test.

Các ví thường dùng:

```text
Account #0: deployer/admin demo
Account #1: member vote
Account #2: member vote
Account #3: recipient nhận tiền
```

### Bước 2: Deploy contract

Chạy:

```powershell
npm.cmd run deploy:local
```

Script deploy:

```text
GovernanceToken
MembershipNFT
CommunityDAO
```

Đồng thời script làm sẵn:

```text
Mint 10000 CGT cho Account #0
Transfer 3000 CGT cho Account #1
Transfer 2000 CGT cho Account #2
Mint NFT membership cho Account #0, #1, #2
Nạp 3 ETH vào DAO treasury
```

Sau deploy:

```text
Account #0: có CGT, có NFT
Account #1: có 3000 CGT, có NFT
Account #2: có 2000 CGT, có NFT
Account #3: là người nhận tiền demo
DAO treasury: có 3 ETH
```

### Bước 3: Chạy frontend

Chạy:

```powershell
npm.cmd run frontend
```

Mở:

```text
http://127.0.0.1:3000/
```

Frontend đọc `frontend/public/deployment.json` để biết địa chỉ contract.

### Bước 4: Connect MetaMask

MetaMask cần chọn đúng network:

```text
Network name: Hardhat Local
RPC URL: http://127.0.0.1:8545
Chain ID: 31337
Currency symbol: ETH
```

Sau đó import các account Hardhat để demo.

### Bước 5: Tạo proposal

Dùng Account #0, #1 hoặc #2 vì các account này có NFT membership.

Ví dụ nhập:

```text
Title: Buy club equipment
Recipient: 0x90F79bf6EB2c4f870365E785982E1f101E93b906
Amount: 1 ETH
```

Chọn đủ 3 file:

```text
Proposal Documentation
Financial Report
Governance Rules JSON
```

Khi bấm propose:

```text
File được upload lên IPFS hoặc mock IPFS
Frontend nhận CID
CID được gửi vào smart contract
Proposal được tạo trên blockchain
```

Proposal lúc này có trạng thái:

```text
Active
```

### Bước 6: Vote

Chuyển MetaMask sang Account #1.

Account #1 có:

```text
3000 CGT
```

Bấm:

```text
Vote For
```

Contract ghi:

```text
For votes += 3000
```

Chuyển sang Account #2.

Account #2 có:

```text
2000 CGT
```

Bấm:

```text
Vote For
```

Contract ghi:

```text
For votes += 2000
```

Tổng:

```text
For votes = 5000
Against votes = 0
Total votes = 5000
```

Quorum cần:

```text
2000
```

Vậy proposal đủ quorum và đa số thuận.

### Bước 7: Chờ hết voting period

Voting period mặc định:

```text
300 giây = 5 phút
```

Trong thời gian này:

```text
Vẫn có thể vote.
Không được execute sớm.
```

Sau khi hết hạn:

```text
Không được vote nữa.
Có thể execute nếu proposal pass.
```

### Bước 8: Execute

Dùng account nào cũng có thể execute:

```text
Account #0
Account #1
Account #2
Account #3
```

Contract kiểm tra:

```text
Đã hết thời gian chưa?
Proposal đã execute chưa?
Tổng vote có đạt quorum không?
For votes có lớn hơn Against votes không?
DAO treasury có đủ ETH không?
```

Nếu tất cả đúng:

```text
DAO chuyển ETH cho recipient
proposal.executed = true
```

Ví dụ proposal chi 1 ETH cho Account #3:

```text
DAO treasury: 3 ETH -> 2 ETH
Account #3: 10000 ETH -> 10001 ETH
```

## 12. Trạng Thái Proposal

Các trạng thái chính:

```text
Active
Defeated
Succeeded
Executed
```

Ý nghĩa:

```text
Active: đang trong thời gian vote
Defeated: hết hạn nhưng không đạt quorum hoặc phiếu thuận không thắng
Succeeded: hết hạn, đạt quorum, phiếu thuận thắng
Executed: proposal đã thực thi và tiền đã chuyển
```

## 13. Ai Được Làm Gì?

```text
Account #0
- Deploy project
- Có CGT
- Có NFT
- Có thể propose, vote, execute

Account #1
- Có 3000 CGT
- Có NFT
- Có thể propose, vote, execute

Account #2
- Có 2000 CGT
- Có NFT
- Có thể propose, vote, execute

Account #3
- Người nhận tiền demo
- Không cần CGT
- Không cần NFT
- Vẫn có thể execute nếu muốn, vì execute không bị giới hạn
```

## 14. Principal-Agent Problem

Trong tổ chức truyền thống, người sở hữu quỹ phải tin người quản lý sẽ hành động đúng lợi ích chung.

Vấn đề:

```text
Người quản lý có thể chi tiêu sai mục đích.
Thành viên không kiểm soát được quyết định.
Thông tin có thể thiếu minh bạch.
```

Đây là **Principal-Agent Problem**.

DAO giải quyết bằng cách:

```text
Mọi proposal công khai trên blockchain.
Tài liệu proposal lưu bằng CID IPFS.
Token holders trực tiếp vote.
Smart contract tự kiểm tra điều kiện.
Treasury chỉ chuyển tiền khi proposal pass.
Không cần phụ thuộc vào một admin tập quyền.
```

Kết luận:

```text
DAO thay niềm tin vào cá nhân bằng luật minh bạch trong smart contract.
```

## 15. Một Câu Tóm Tắt Project

Project này là một quỹ cộng đồng tự vận hành:

```text
Thành viên có NFT được tạo đề xuất.
Người có token CGT được bỏ phiếu.
Proposal phải đạt quorum và đa số thuận.
Sau deadline, smart contract tự chuyển ETH từ DAO treasury cho người nhận.
```
