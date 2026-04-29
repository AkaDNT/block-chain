import { ethers } from "ethers";

const DEV_AUTO_WALLET = import.meta.env.VITE_DEV_AUTO_WALLET === "true";
const DEV_RPC_URL = import.meta.env.VITE_DEV_RPC_URL || "http://127.0.0.1:8545";
const DEV_PRIVATE_KEY =
  import.meta.env.VITE_DEV_PRIVATE_KEY ||
  "0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80";

const DAO_ABI = [
  "function proposalCount() view returns (uint256)",
  "function quorumPercent() view returns (uint256)",
  "function votingPeriod() view returns (uint256)",
  "function quorumVotes() view returns (uint256)",
  "function getAllProposals() view returns (tuple(uint256 id,address proposer,address recipient,uint256 amount,string title,string summary,string documentationCid,string financialReportCid,string governanceRulesCid,uint256 startTime,uint256 endTime,uint256 forVotes,uint256 againstVotes,bool executed)[])",
  "function getProposal(uint256 proposalId) view returns (tuple(uint256 id,address proposer,address recipient,uint256 amount,string title,string summary,string documentationCid,string financialReportCid,string governanceRulesCid,uint256 startTime,uint256 endTime,uint256 forVotes,uint256 againstVotes,bool executed))",
  "function hasVoted(uint256 proposalId,address voter) view returns (bool)",
  "function state(uint256 proposalId) view returns (uint8)",
  "function propose(address recipient,uint256 amount,string title,string summary,string documentationCid,string financialReportCid,string governanceRulesCid) returns (uint256)",
  "function vote(uint256 proposalId,bool support)",
  "function execute(uint256 proposalId)",
  "receive() external payable",
  "event ProposalCreated(uint256 indexed proposalId,address indexed proposer,address indexed recipient,uint256 amount,string title,uint256 startTime,uint256 endTime)",
  "event VoteCast(uint256 indexed proposalId,address indexed voter,bool support,uint256 weight)",
  "event ProposalExecuted(uint256 indexed proposalId,address indexed recipient,uint256 amount)"
];

const ERC20_ABI = [
  "function name() view returns (string)",
  "function symbol() view returns (string)",
  "function decimals() view returns (uint8)",
  "function totalSupply() view returns (uint256)",
  "function balanceOf(address account) view returns (uint256)",
  "function transfer(address to,uint256 amount) returns (bool)",
  "function mint(address to,uint256 amount)",
  "function owner() view returns (address)"
];

const NFT_ABI = [
  "function name() view returns (string)",
  "function symbol() view returns (string)",
  "function balanceOf(address account) view returns (uint256)",
  "function mint(address to) returns (uint256)",
  "function owner() view returns (address)"
];

const STATES = ["Unknown", "Active", "Defeated", "Succeeded", "Executed"];

let deploymentCache = null;

async function loadDeployment() {
  if (deploymentCache) return deploymentCache;
  const response = await fetch("/deployment.json", { cache: "no-store" });
  if (!response.ok) {
    throw new Error("Missing frontend/public/deployment.json. Run npm run deploy:hardhat or npm run deploy:local first.");
  }
  deploymentCache = await response.json();
  return deploymentCache;
}

function getInjectedProvider() {
  if (typeof window === "undefined") return null;
  const ethereum = window.ethereum;
  if (!ethereum) return null;
  if (Array.isArray(ethereum.providers)) {
    return ethereum.providers.find((provider) => provider.isMetaMask) || ethereum.providers[0];
  }
  return ethereum;
}

function normalizeProposal(proposal, state = 0, account = null, voted = false) {
  const forVotes = Number(ethers.formatUnits(proposal.forVotes, 18));
  const againstVotes = Number(ethers.formatUnits(proposal.againstVotes, 18));
  const totalVotes = forVotes + againstVotes;

  return {
    id: Number(proposal.id),
    proposer: proposal.proposer,
    recipient: proposal.recipient,
    amountWei: proposal.amount,
    amountEth: ethers.formatEther(proposal.amount),
    title: proposal.title,
    summary: proposal.summary,
    documentationCid: proposal.documentationCid,
    financialReportCid: proposal.financialReportCid,
    governanceRulesCid: proposal.governanceRulesCid,
    startTime: Number(proposal.startTime),
    endTime: Number(proposal.endTime),
    forVotes,
    againstVotes,
    totalVotes,
    executed: proposal.executed,
    state,
    stateLabel: STATES[state] || "Unknown",
    hasVoted: Boolean(voted),
    canExecute: state === 3,
    isOwnProposal: account ? proposal.proposer.toLowerCase() === account.toLowerCase() : false
  };
}

class BlockchainService {
  constructor() {
    this.provider = null;
    this.signer = null;
    this.injectedProvider = null;
    this.deployment = null;
  }

  async initialize() {
    try {
      this.deployment = await loadDeployment();
    } catch (error) {
      console.warn(error.message);
    }
  }

  async connect() {
    this.deployment = await loadDeployment();

    if (DEV_AUTO_WALLET) {
      this.provider = new ethers.JsonRpcProvider(DEV_RPC_URL);
      this.signer = new ethers.Wallet(DEV_PRIVATE_KEY, this.provider);
      return true;
    }

    this.injectedProvider = getInjectedProvider();
    if (!this.injectedProvider) return false;

    const accounts = await this.injectedProvider.request({ method: "eth_requestAccounts" });
    this.provider = new ethers.BrowserProvider(this.injectedProvider);
    this.signer = await this.provider.getSigner(accounts[0]);
    return true;
  }

  disconnect() {
    this.signer = null;
  }

  getWalletProvider() {
    return this.injectedProvider || getInjectedProvider();
  }

  isDevAutoWalletEnabled() {
    return DEV_AUTO_WALLET;
  }

  getAddress(name) {
    if (!this.deployment?.contracts?.[name]) {
      throw new Error(`${name} address is not configured in deployment.json`);
    }
    return this.deployment.contracts[name];
  }

  getDao(readOnly = false) {
    const runner = readOnly ? this.provider : this.signer;
    return new ethers.Contract(this.getAddress("CommunityDAO"), DAO_ABI, runner);
  }

  getToken(readOnly = false) {
    const runner = readOnly ? this.provider : this.signer;
    return new ethers.Contract(this.getAddress("GovernanceToken"), ERC20_ABI, runner);
  }

  getMembership(readOnly = false) {
    const runner = readOnly ? this.provider : this.signer;
    return new ethers.Contract(this.getAddress("MembershipNFT"), NFT_ABI, runner);
  }

  async validateDeployment() {
    const network = await this.provider.getNetwork();
    const connectedChainId = Number(network.chainId);
    const expectedChainId = Number(this.deployment?.chainId || 31337);

    if (connectedChainId !== expectedChainId) {
      throw new Error(
        `Wrong network selected in MetaMask. Connected chainId is ${connectedChainId}, expected ${expectedChainId}. Select Hardhat Local with RPC http://127.0.0.1:8545, then refresh.`
      );
    }

    const required = ["GovernanceToken", "MembershipNFT", "CommunityDAO"];
    for (const name of required) {
      const address = this.getAddress(name);
      const code = await this.provider.getCode(address);
      if (!code || code === "0x") {
        throw new Error(
          `${name} is not deployed at ${address} on the selected MetaMask network chainId ${connectedChainId}. Your local RPC http://127.0.0.1:8545 may be correct, but MetaMask is likely pointing to another RPC. Delete and recreate the Hardhat Local network with RPC http://127.0.0.1:8545, chainId 31337, then refresh.`
        );
      }
    }
  }

  async getAccount() {
    if (!this.signer) return "";
    return this.signer.getAddress();
  }

  async getEthBalance(address) {
    const balance = await this.provider.getBalance(address);
    return ethers.formatEther(balance);
  }

  async getMemberProfile(address) {
    const token = this.getToken(true);
    const nft = this.getMembership(true);
    const [tokenBalance, membershipBalance, totalSupply] = await Promise.all([
      token.balanceOf(address),
      nft.balanceOf(address),
      token.totalSupply()
    ]);
    return {
      tokenBalance,
      tokenBalanceFormatted: ethers.formatUnits(tokenBalance, 18),
      membershipBalance: Number(membershipBalance),
      totalSupplyFormatted: ethers.formatUnits(totalSupply, 18),
      canPropose: Number(membershipBalance) > 0,
      canVote: tokenBalance > 0n
    };
  }

  async getDaoStats() {
    await this.validateDeployment();
    const dao = this.getDao(true);
    const daoAddress = this.getAddress("CommunityDAO");
    const [treasury, quorumVotes, quorumPercent, votingPeriod] = await Promise.all([
      this.provider.getBalance(daoAddress),
      dao.quorumVotes(),
      dao.quorumPercent(),
      dao.votingPeriod()
    ]);
    return {
      daoAddress,
      tokenAddress: this.getAddress("GovernanceToken"),
      nftAddress: this.getAddress("MembershipNFT"),
      treasuryEth: ethers.formatEther(treasury),
      quorumVotes: ethers.formatUnits(quorumVotes, 18),
      quorumPercent: Number(quorumPercent),
      votingPeriodSeconds: Number(votingPeriod)
    };
  }

  async getProposals(account = null) {
    const dao = this.getDao(true);
    const raw = await dao.getAllProposals();
    const enriched = await Promise.all(
      raw.map(async (proposal) => {
        const proposalId = Number(proposal.id);
        const [state, voted] = await Promise.all([
          dao.state(proposalId),
          account ? dao.hasVoted(proposalId, account) : Promise.resolve(false)
        ]);
        return normalizeProposal(proposal, Number(state), account, voted);
      })
    );
    return enriched.sort((a, b) => b.id - a.id);
  }

  async propose(payload) {
    if (!ethers.isAddress(payload.recipient)) {
      throw new Error("Invalid recipient address. Use a full 0x wallet address, not an ENS name or private key.");
    }

    const dao = this.getDao();
    const tx = await dao.propose(
      payload.recipient.trim(),
      ethers.parseEther(payload.amountEth || "0"),
      payload.title,
      payload.summary,
      payload.documentationCid,
      payload.financialReportCid,
      payload.governanceRulesCid
    );
    return tx.wait();
  }

  async vote(proposalId, support) {
    const dao = this.getDao();
    const tx = await dao.vote(proposalId, support);
    return tx.wait();
  }

  async execute(proposalId) {
    const dao = this.getDao();
    const tx = await dao.execute(proposalId);
    return tx.wait();
  }

  async mintTokens(to, amount) {
    if (!ethers.isAddress(to)) {
      throw new Error("Invalid token recipient address.");
    }
    const token = this.getToken();
    const tx = await token.mint(to.trim(), ethers.parseUnits(amount, 18));
    return tx.wait();
  }

  async mintMembership(to) {
    if (!ethers.isAddress(to)) {
      throw new Error("Invalid membership recipient address.");
    }
    const nft = this.getMembership();
    const tx = await nft.mint(to.trim());
    return tx.wait();
  }

  async fundTreasury(amountEth) {
    const tx = await this.signer.sendTransaction({
      to: this.getAddress("CommunityDAO"),
      value: ethers.parseEther(amountEth)
    });
    return tx.wait();
  }
}

export { ethers, STATES };
export default new BlockchainService();
