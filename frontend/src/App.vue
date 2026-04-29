<template>
  <div class="min-h-screen bg-slate-50 text-slate-950">
    <header class="border-b border-slate-200 bg-white">
      <div class="mx-auto flex max-w-7xl flex-col gap-4 px-5 py-5 md:flex-row md:items-center md:justify-between">
        <div>
          <p class="text-sm font-semibold uppercase tracking-wide text-emerald-700">Community Treasury DAO</p>
          <h1 class="mt-1 text-2xl font-bold">Quản trị phi tập trung cho quỹ cộng đồng</h1>
        </div>
        <div class="flex flex-wrap items-center gap-2">
          <button v-if="!account" class="btn-primary" @click="connectWallet">Connect MetaMask</button>
          <button v-else class="btn-secondary" @click="loadAll">Refresh</button>
          <span v-if="account" class="rounded-md border border-slate-200 bg-slate-100 px-3 py-2 text-sm font-semibold">
            {{ shortAddress(account) }}
          </span>
        </div>
      </div>
    </header>

    <main class="mx-auto grid max-w-7xl gap-6 px-5 py-6 lg:grid-cols-[340px_1fr]">
      <aside class="space-y-4">
        <section class="panel">
          <h2 class="section-title">DAO Status</h2>
          <div class="mt-4 space-y-3 text-sm">
            <InfoRow label="Treasury" :value="`${fmt(stats.treasuryEth)} ETH`" />
            <InfoRow label="Quorum" :value="`${fmt(stats.quorumVotes)} CGT (${stats.quorumPercent || 0}%)`" />
            <InfoRow label="Voting period" :value="formatDuration(stats.votingPeriodSeconds)" />
            <InfoRow label="DAO" :value="shortAddress(stats.daoAddress)" />
            <InfoRow label="Token" :value="shortAddress(stats.tokenAddress)" />
            <InfoRow label="NFT" :value="shortAddress(stats.nftAddress)" />
          </div>
        </section>

        <section class="panel">
          <h2 class="section-title">Member Power</h2>
          <div class="mt-4 space-y-3 text-sm">
            <InfoRow label="Governance token" :value="`${fmt(profile.tokenBalanceFormatted)} CGT`" />
            <InfoRow label="Membership NFT" :value="profile.membershipBalance ? 'Owned' : 'Missing'" />
            <div class="rounded-md bg-slate-100 p-3 text-slate-700">
              NFT member mới được tạo đề xuất. Token CGT quyết định trọng số phiếu bầu theo mô hình 1 token = 1 vote.
            </div>
          </div>
        </section>

        <section class="panel">
          <h2 class="section-title">Demo Minting</h2>
          <div class="mt-4 space-y-3">
            <input v-model="mintAddress" class="input-field" placeholder="Member wallet address" />
            <div class="grid grid-cols-[1fr_96px] gap-2">
              <input v-model="mintAmount" class="input-field" placeholder="CGT amount" />
              <button class="btn-secondary" @click="mintTokens">Mint CGT</button>
            </div>
            <button class="btn-secondary w-full" @click="mintMembership">Mint membership NFT</button>
            <div class="grid grid-cols-[1fr_92px] gap-2">
              <input v-model="fundAmount" class="input-field" placeholder="Treasury ETH" />
              <button class="btn-secondary" @click="fundTreasury">Fund</button>
            </div>
          </div>
        </section>
      </aside>

      <section class="space-y-6">
        <section class="panel">
          <div class="flex flex-col gap-2 md:flex-row md:items-center md:justify-between">
            <div>
              <h2 class="section-title">Create Proposal</h2>
              <p class="mt-1 text-sm text-slate-600">Upload tài liệu lên IPFS, contract chỉ lưu CID để giảm gas.</p>
            </div>
            <span class="status-pill" :class="profile.canPropose ? 'status-ok' : 'status-warn'">
              {{ profile.canPropose ? "Can propose" : "NFT required" }}
            </span>
          </div>

          <form class="mt-5 grid gap-4" @submit.prevent="createProposal">
            <div class="grid gap-4 md:grid-cols-2">
              <input v-model="form.title" class="input-field" placeholder="Proposal title" required />
              <input v-model="form.recipient" class="input-field" placeholder="Recipient address" required />
            </div>
            <div class="grid gap-4 md:grid-cols-[1fr_160px]">
              <textarea v-model="form.summary" class="input-field min-h-24" placeholder="Short summary" required />
              <input v-model="form.amountEth" class="input-field" type="number" min="0" step="0.001" placeholder="ETH amount" required />
            </div>
            <div class="grid gap-4 md:grid-cols-3">
              <FileInput label="Proposal PDF/MD" accept=".pdf,.md,.txt" @change="form.documentationFile = $event" />
              <FileInput label="Financial report" accept=".pdf,.csv,.xlsx,.json,.txt" @change="form.financialFile = $event" />
              <FileInput label="Governance rules JSON" accept=".json" @change="form.rulesFile = $event" />
            </div>
            <button class="btn-primary w-full md:w-fit" :disabled="busy || !profile.canPropose">
              {{ busy ? "Submitting..." : "Upload to IPFS and Propose" }}
            </button>
          </form>
        </section>

        <section class="panel">
          <div class="flex items-center justify-between">
            <h2 class="section-title">Proposal Board</h2>
            <span class="text-sm text-slate-500">{{ proposals.length }} proposals</span>
          </div>

          <div v-if="proposals.length === 0" class="mt-5 rounded-md border border-dashed border-slate-300 p-8 text-center text-slate-600">
            Chưa có đề xuất. Hãy tạo proposal đầu tiên để demo DAO.
          </div>

          <div v-else class="mt-5 space-y-4">
            <article v-for="proposal in proposals" :key="proposal.id" class="proposal-card">
              <div class="flex flex-col gap-3 md:flex-row md:items-start md:justify-between">
                <div>
                  <div class="flex flex-wrap items-center gap-2">
                    <span class="status-pill">#{{ proposal.id }}</span>
                    <span class="status-pill" :class="stateClass(proposal.effectiveState || proposal.state)">{{ proposal.effectiveStateLabel || proposal.stateLabel }}</span>
                    <span v-if="proposal.hasVoted" class="status-pill status-ok">Voted</span>
                  </div>
                  <h3 class="mt-3 text-lg font-bold">{{ proposal.title }}</h3>
                  <p class="mt-1 text-sm text-slate-600">{{ proposal.summary }}</p>
                </div>
                <div class="text-left text-sm md:text-right">
                  <p class="font-semibold">{{ proposal.amountEth }} ETH</p>
                  <p class="text-slate-500">to {{ shortAddress(proposal.recipient) }}</p>
                </div>
              </div>

              <div class="mt-4 grid gap-3 md:grid-cols-3">
                <ProgressBar label="For" :value="proposal.forVotes" :max="proposal.totalVotes || 1" tone="emerald" />
                <ProgressBar label="Against" :value="proposal.againstVotes" :max="proposal.totalVotes || 1" tone="rose" />
                <ProgressBar label="Quorum" :value="proposal.totalVotes" :max="Number(stats.quorumVotes || 1)" tone="sky" />
              </div>

              <div class="mt-4 flex flex-wrap items-center gap-2 text-sm">
                <button class="btn-secondary" @click="viewCid(proposal.documentationCid, 'Proposal Documentation')">View documentation</button>
                <button class="btn-secondary" @click="viewCid(proposal.financialReportCid, 'Financial Report')">View financials</button>
                <button class="btn-secondary" @click="viewCid(proposal.governanceRulesCid, 'Governance Rules')">View rules</button>
                <span class="ml-auto text-slate-500">Ends {{ formatDate(proposal.endTime) }}</span>
              </div>

              <div class="mt-4 flex flex-wrap gap-2">
                <button class="btn-primary" :disabled="busy || !proposal.canVoteNow || proposal.hasVoted || !profile.canVote" @click="castVote(proposal.id, true)">
                  Vote For
                </button>
                <button class="btn-danger" :disabled="busy || !proposal.canVoteNow || proposal.hasVoted || !profile.canVote" @click="castVote(proposal.id, false)">
                  Vote Against
                </button>
                <button class="btn-secondary" :disabled="busy || !proposal.canExecuteNow" @click="executeProposal(proposal.id)">
                  Execute
                </button>
              </div>
            </article>
          </div>
        </section>
      </section>
    </main>

    <div v-if="detail.open" class="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/60 p-4" @click.self="detail.open = false">
      <div class="max-h-[82vh] w-full max-w-3xl overflow-auto rounded-lg bg-white p-5 shadow-xl">
        <div class="flex items-center justify-between gap-3">
          <h2 class="text-lg font-bold">{{ detail.title }}</h2>
          <button class="btn-secondary" @click="detail.open = false">Close</button>
        </div>
        <a class="mt-2 block text-sm font-semibold text-emerald-700" :href="detail.url" target="_blank" rel="noreferrer">
          {{ detail.cid }}
        </a>
        <pre v-if="detail.type === 'json' || detail.type === 'text'" class="mt-4 whitespace-pre-wrap rounded-md bg-slate-100 p-4 text-sm">{{ detail.content }}</pre>
        <p v-else class="mt-4 text-slate-700">File mở tốt nhất qua gateway ở link phía trên.</p>
      </div>
    </div>

    <div v-if="message" class="fixed bottom-4 left-1/2 z-50 w-[calc(100%-2rem)] max-w-2xl -translate-x-1/2 rounded-md bg-slate-950 px-4 py-3 text-sm font-semibold text-white shadow-lg">
      {{ message }}
    </div>
  </div>
</template>

<script setup>
import { computed, h, reactive, ref } from "vue";
import blockchain from "./utils/blockchain.js";
import { ethers } from "./utils/blockchain.js";
import { retrieveFromIPFS, uploadToIPFS, uploadJsonToIPFS } from "./utils/ipfs.js";

const account = ref("");
const busy = ref(false);
const message = ref("");
const stats = reactive({
  treasuryEth: "0",
  quorumVotes: "0",
  quorumPercent: 0,
  votingPeriodSeconds: 0,
  daoAddress: "",
  tokenAddress: "",
  nftAddress: ""
});
const profile = reactive({
  tokenBalanceFormatted: "0",
  membershipBalance: 0,
  totalSupplyFormatted: "0",
  canPropose: false,
  canVote: false
});
const proposals = ref([]);
const mintAddress = ref("");
const mintAmount = ref("100");
const fundAmount = ref("1");
const form = reactive({
  title: "",
  summary: "",
  recipient: "",
  amountEth: "1",
  documentationFile: null,
  financialFile: null,
  rulesFile: null
});
const detail = reactive({
  open: false,
  title: "",
  cid: "",
  url: "",
  type: "",
  content: ""
});

const setMessage = (text) => {
  message.value = text;
  window.clearTimeout(setMessage.timer);
  setMessage.timer = window.setTimeout(() => {
    message.value = "";
  }, 4500);
};

async function connectWallet() {
  try {
    const ok = await blockchain.connect();
    if (!ok) {
      setMessage("Không tìm thấy MetaMask hoặc ví EVM tương thích.");
      return;
    }
    account.value = await blockchain.getAccount();
    mintAddress.value = account.value;
    await loadAll();

    const walletProvider = blockchain.getWalletProvider();
    walletProvider?.on?.("accountsChanged", () => window.location.reload());
    walletProvider?.on?.("chainChanged", () => window.location.reload());
  } catch (error) {
    setMessage(error.message);
  }
}

async function loadAll() {
  if (!blockchain.provider && !blockchain.signer) return;
  try {
    Object.assign(stats, await blockchain.getDaoStats());
    if (account.value) {
      Object.assign(profile, await blockchain.getMemberProfile(account.value));
    }
    const loadedProposals = await blockchain.getProposals(account.value);
    proposals.value = loadedProposals.map(applyLocalDeadlineState);
  } catch (error) {
    setMessage(error.message);
  }
}

function applyLocalDeadlineState(proposal) {
  const now = Math.floor(Date.now() / 1000);
  const quorumReached = proposal.totalVotes >= Number(stats.quorumVotes || 0);
  const majorityFor = proposal.forVotes > proposal.againstVotes;
  const deadlinePassed = now > proposal.endTime;

  const decorated = {
    ...proposal,
    canVoteNow: proposal.state === 1 && !deadlinePassed
  };

  if (proposal.executed || proposal.state === 4) {
    decorated.effectiveState = 4;
    decorated.effectiveStateLabel = "Executed";
    decorated.canExecuteNow = false;
    return decorated;
  }

  if (deadlinePassed && quorumReached && majorityFor) {
    decorated.effectiveState = 3;
    decorated.effectiveStateLabel = "Succeeded";
    decorated.canExecuteNow = true;
    return decorated;
  }

  if (deadlinePassed) {
    decorated.effectiveState = 2;
    decorated.effectiveStateLabel = "Defeated";
    decorated.canExecuteNow = false;
    return decorated;
  }

  decorated.effectiveState = proposal.state;
  decorated.effectiveStateLabel = proposal.stateLabel;
  decorated.canExecuteNow = proposal.canExecute;
  return decorated;
}

async function createProposal() {
  const recipient = form.recipient.trim();

  if (!ethers.isAddress(recipient)) {
    setMessage("Recipient address không hợp lệ. Hãy nhập địa chỉ ví dạng 0x..., ví dụ 0x90F79bf6EB2c4f870365E785982E1f101E93b906.");
    return;
  }

  if (!form.documentationFile || !form.financialFile || !form.rulesFile) {
    setMessage("Vui lòng chọn đủ 3 loại dữ liệu IPFS: proposal, financial report, governance rules.");
    return;
  }

  busy.value = true;
  try {
    setMessage("Uploading proposal data to IPFS...");
    const documentationCid = await uploadToIPFS(form.documentationFile);
    const financialReportCid = await uploadToIPFS(form.financialFile);
    const governanceRulesCid =
      form.rulesFile.type === "application/json"
        ? await uploadToIPFS(form.rulesFile)
        : await uploadJsonToIPFS({ title: form.title, summary: form.summary });

    setMessage("Please confirm proposal transaction in wallet...");
    await blockchain.propose({
      ...form,
      recipient,
      title: form.title.trim(),
      summary: form.summary.trim(),
      documentationCid,
      financialReportCid,
      governanceRulesCid
    });

    Object.assign(form, {
      title: "",
      summary: "",
      recipient: "",
      amountEth: "1",
      documentationFile: null,
      financialFile: null,
      rulesFile: null
    });
    setMessage("Proposal created successfully.");
    await loadAll();
  } catch (error) {
    setMessage(error.shortMessage || error.message);
  } finally {
    busy.value = false;
  }
}

async function castVote(proposalId, support) {
  busy.value = true;
  try {
    setMessage("Checking token balance and submitting vote...");
    if (!profile.canVote) throw new Error("Ví này không có CGT nên không thể bỏ phiếu.");
    await blockchain.vote(proposalId, support);
    setMessage("Vote submitted.");
    await loadAll();
  } catch (error) {
    setMessage(error.shortMessage || error.message);
  } finally {
    busy.value = false;
  }
}

async function executeProposal(proposalId) {
  busy.value = true;
  try {
    await blockchain.execute(proposalId);
    setMessage("Proposal executed. Treasury payment has been sent.");
    await loadAll();
  } catch (error) {
    setMessage(error.shortMessage || error.message);
  } finally {
    busy.value = false;
  }
}

async function mintTokens() {
  const to = mintAddress.value.trim();
  if (!ethers.isAddress(to)) {
    setMessage("Member wallet address không hợp lệ. Hãy nhập địa chỉ dạng 0x...");
    return;
  }
  if (!mintAmount.value) return;
  busy.value = true;
  try {
    await blockchain.mintTokens(to, mintAmount.value);
    setMessage("CGT minted.");
    await loadAll();
  } catch (error) {
    setMessage(error.shortMessage || error.message);
  } finally {
    busy.value = false;
  }
}

async function mintMembership() {
  const to = mintAddress.value.trim();
  if (!ethers.isAddress(to)) {
    setMessage("Member wallet address không hợp lệ. Hãy nhập địa chỉ dạng 0x...");
    return;
  }
  busy.value = true;
  try {
    await blockchain.mintMembership(to);
    setMessage("Membership NFT minted.");
    await loadAll();
  } catch (error) {
    setMessage(error.shortMessage || error.message);
  } finally {
    busy.value = false;
  }
}

async function fundTreasury() {
  if (!fundAmount.value) return;
  busy.value = true;
  try {
    await blockchain.fundTreasury(fundAmount.value);
    setMessage("Treasury funded.");
    await loadAll();
  } catch (error) {
    setMessage(error.shortMessage || error.message);
  } finally {
    busy.value = false;
  }
}

async function viewCid(cid, title) {
  detail.open = true;
  detail.title = title;
  detail.cid = cid;
  detail.url = "";
  detail.type = "";
  detail.content = "Loading from IPFS...";
  try {
    const result = await retrieveFromIPFS(cid);
    detail.url = result.url;
    detail.type = result.type;
    detail.content = result.type === "json" ? JSON.stringify(result.content, null, 2) : result.content || "";
  } catch (error) {
    detail.content = error.message;
  }
}

function shortAddress(address) {
  if (!address) return "-";
  return `${address.slice(0, 6)}...${address.slice(-4)}`;
}

function fmt(value) {
  const number = Number(value || 0);
  return number.toLocaleString("en-US", { maximumFractionDigits: 4 });
}

function formatDuration(seconds) {
  if (!seconds) return "-";
  if (seconds < 3600) return `${Math.round(seconds / 60)} minutes`;
  return `${Math.round(seconds / 3600)} hours`;
}

function formatDate(timestamp) {
  return new Date(timestamp * 1000).toLocaleString();
}

function stateClass(state) {
  return {
    1: "status-live",
    2: "status-warn",
    3: "status-ok",
    4: "status-done"
  }[state];
}

const InfoRow = (props) =>
  h("div", { class: "flex items-center justify-between gap-3 border-b border-slate-100 pb-2 last:border-b-0" }, [
    h("span", { class: "text-slate-500" }, props.label),
    h("span", { class: "break-all text-right font-semibold" }, props.value || "-")
  ]);
InfoRow.props = ["label", "value"];

const FileInput = (props, { emit }) =>
  h("label", { class: "block" }, [
    h("span", { class: "mb-2 block text-sm font-semibold text-slate-700" }, props.label),
    h("input", {
      class: "input-field file:mr-3 file:rounded-md file:border-0 file:bg-slate-200 file:px-3 file:py-2 file:text-sm file:font-semibold",
      type: "file",
      accept: props.accept,
      onChange: (event) => emit("change", event.target.files?.[0] || null)
    })
  ]);
FileInput.props = ["label", "accept"];
FileInput.emits = ["change"];

const ProgressBar = (props) => {
  const percent = computed(() => Math.min(100, Math.round((Number(props.value || 0) / Number(props.max || 1)) * 100)));
  return h("div", { class: "rounded-md border border-slate-200 bg-white p-3" }, [
    h("div", { class: "mb-2 flex justify-between text-sm" }, [
      h("span", { class: "font-semibold" }, props.label),
      h("span", { class: "text-slate-500" }, fmt(props.value))
    ]),
    h("div", { class: "h-2 overflow-hidden rounded bg-slate-100" }, [
      h("div", { class: `h-full progress-${props.tone}`, style: { width: `${percent.value}%` } })
    ])
  ]);
};
ProgressBar.props = ["label", "value", "max", "tone"];

if (blockchain.isDevAutoWalletEnabled()) {
  connectWallet();
}
</script>
