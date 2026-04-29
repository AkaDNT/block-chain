// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

interface IERC20VotesLike {
    function balanceOf(address account) external view returns (uint256);
    function totalSupply() external view returns (uint256);
}

interface IMembershipNFTLike {
    function balanceOf(address account) external view returns (uint256);
}

contract CommunityDAO {
    enum VoteChoice {
        Against,
        For
    }

    struct Proposal {
        uint256 id;
        address proposer;
        address payable recipient;
        uint256 amount;
        string title;
        string summary;
        string documentationCid;
        string financialReportCid;
        string governanceRulesCid;
        uint256 startTime;
        uint256 endTime;
        uint256 forVotes;
        uint256 againstVotes;
        bool executed;
    }

    IERC20VotesLike public immutable governanceToken;
    IMembershipNFTLike public immutable membershipNFT;
    uint256 public immutable quorumPercent;
    uint256 public immutable votingPeriod;
    uint256 public proposalCount;

    mapping(uint256 => Proposal) private proposals;
    mapping(uint256 => mapping(address => bool)) public hasVoted;
    mapping(uint256 => mapping(address => uint256)) public voteWeightOf;

    event ProposalCreated(
        uint256 indexed proposalId,
        address indexed proposer,
        address indexed recipient,
        uint256 amount,
        string title,
        uint256 startTime,
        uint256 endTime
    );
    event VoteCast(uint256 indexed proposalId, address indexed voter, bool support, uint256 weight);
    event ProposalExecuted(uint256 indexed proposalId, address indexed recipient, uint256 amount);
    event TreasuryFunded(address indexed sender, uint256 amount);

    modifier onlyMember() {
        require(membershipNFT.balanceOf(msg.sender) > 0, "MEMBERSHIP_REQUIRED");
        _;
    }

    constructor(address tokenAddress, address nftAddress, uint256 quorumPercent_, uint256 votingPeriod_) payable {
        require(tokenAddress != address(0), "TOKEN_REQUIRED");
        require(nftAddress != address(0), "NFT_REQUIRED");
        require(quorumPercent_ > 0 && quorumPercent_ <= 100, "BAD_QUORUM");
        require(votingPeriod_ >= 1 minutes, "VOTING_PERIOD_TOO_SHORT");

        governanceToken = IERC20VotesLike(tokenAddress);
        membershipNFT = IMembershipNFTLike(nftAddress);
        quorumPercent = quorumPercent_;
        votingPeriod = votingPeriod_;
    }

    receive() external payable {
        emit TreasuryFunded(msg.sender, msg.value);
    }

    function propose(
        address payable recipient,
        uint256 amount,
        string calldata title,
        string calldata summary,
        string calldata documentationCid,
        string calldata financialReportCid,
        string calldata governanceRulesCid
    ) external onlyMember returns (uint256 proposalId) {
        require(recipient != address(0), "RECIPIENT_REQUIRED");
        require(bytes(title).length > 0, "TITLE_REQUIRED");
        require(bytes(documentationCid).length > 0, "DOCUMENTATION_CID_REQUIRED");
        require(bytes(financialReportCid).length > 0, "FINANCIAL_CID_REQUIRED");
        require(bytes(governanceRulesCid).length > 0, "RULES_CID_REQUIRED");

        proposalId = ++proposalCount;
        Proposal storage proposal = proposals[proposalId];
        proposal.id = proposalId;
        proposal.proposer = msg.sender;
        proposal.recipient = recipient;
        proposal.amount = amount;
        proposal.title = title;
        proposal.summary = summary;
        proposal.documentationCid = documentationCid;
        proposal.financialReportCid = financialReportCid;
        proposal.governanceRulesCid = governanceRulesCid;
        proposal.startTime = block.timestamp;
        proposal.endTime = block.timestamp + votingPeriod;

        emit ProposalCreated(proposalId, msg.sender, recipient, amount, title, proposal.startTime, proposal.endTime);
    }

    function vote(uint256 proposalId, bool support) external {
        Proposal storage proposal = proposals[proposalId];
        require(proposal.id != 0, "PROPOSAL_NOT_FOUND");
        require(block.timestamp <= proposal.endTime, "VOTING_CLOSED");
        require(!hasVoted[proposalId][msg.sender], "ALREADY_VOTED");

        uint256 weight = governanceToken.balanceOf(msg.sender);
        require(weight > 0, "NO_VOTING_POWER");

        hasVoted[proposalId][msg.sender] = true;
        voteWeightOf[proposalId][msg.sender] = weight;

        if (support) {
            proposal.forVotes += weight;
        } else {
            proposal.againstVotes += weight;
        }

        emit VoteCast(proposalId, msg.sender, support, weight);
    }

    function execute(uint256 proposalId) external {
        Proposal storage proposal = proposals[proposalId];
        require(proposal.id != 0, "PROPOSAL_NOT_FOUND");
        require(block.timestamp > proposal.endTime, "VOTING_STILL_ACTIVE");
        require(!proposal.executed, "ALREADY_EXECUTED");
        require(state(proposalId) == 3, "PROPOSAL_NOT_PASSED");
        require(address(this).balance >= proposal.amount, "INSUFFICIENT_TREASURY");

        proposal.executed = true;
        (bool ok, ) = proposal.recipient.call{value: proposal.amount}("");
        require(ok, "TRANSFER_FAILED");

        emit ProposalExecuted(proposalId, proposal.recipient, proposal.amount);
    }

    function getProposal(uint256 proposalId) external view returns (Proposal memory) {
        require(proposals[proposalId].id != 0, "PROPOSAL_NOT_FOUND");
        return proposals[proposalId];
    }

    function getAllProposals() external view returns (Proposal[] memory result) {
        result = new Proposal[](proposalCount);
        for (uint256 i = 1; i <= proposalCount; i++) {
            result[i - 1] = proposals[i];
        }
    }

    function quorumVotes() public view returns (uint256) {
        return (governanceToken.totalSupply() * quorumPercent) / 100;
    }

    function state(uint256 proposalId) public view returns (uint8) {
        Proposal storage proposal = proposals[proposalId];
        require(proposal.id != 0, "PROPOSAL_NOT_FOUND");

        if (proposal.executed) return 4; // Executed
        if (block.timestamp <= proposal.endTime) return 1; // Active

        uint256 totalVotes = proposal.forVotes + proposal.againstVotes;
        if (totalVotes < quorumVotes()) return 2; // Defeated: no quorum
        if (proposal.forVotes <= proposal.againstVotes) return 2; // Defeated: majority against
        return 3; // Succeeded
    }
}
