import express from "express";
import cors from "cors";
import { ethers } from "ethers";
import dotenv from "dotenv";
import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

dotenv.config();

const app = express();
const PORT = process.env.PORT || 3001;

// Middleware
app.use(cors());
app.use(express.json());

function getWallet(provider) {
  const rawPrivateKey = (process.env.DEPLOYER_PRIVATE_KEY || "").trim();
  const normalizedPrivateKey = rawPrivateKey.startsWith("0x")
    ? rawPrivateKey
    : `0x${rawPrivateKey}`;

  if (/^0x[0-9a-fA-F]{64}$/.test(normalizedPrivateKey)) {
    return new ethers.Wallet(normalizedPrivateKey, provider);
  }

  const mnemonic =
    process.env.TEST_MNEMONIC ||
    "test test test test test test test test test test test junk";
  console.warn(
    "DEPLOYER_PRIVATE_KEY is missing or invalid, falling back to test mnemonic account #0",
  );
  return ethers.Wallet.fromPhrase(mnemonic).connect(provider);
}

// Setup provider and wallet
const provider = new ethers.JsonRpcProvider(process.env.RPC_URL);
const wallet = getWallet(provider);

console.log("🔗 Connected to:", process.env.RPC_URL);
console.log("👤 Deployer address:", wallet.address);

// Load contract artifacts
function loadContract(name) {
  const contractPath = path.join(__dirname, "contracts", `${name}.json`);
  const contractData = JSON.parse(fs.readFileSync(contractPath, "utf8"));
  return contractData;
}

const StockTokenArtifact = loadContract("StockToken");
const StockAMMArtifact = loadContract("StockAMM");
const RegistryArtifact = loadContract("Registry");

// Get Registry contract instance
function getRegistry() {
  return new ethers.Contract(
    process.env.REGISTRY_ADDRESS,
    RegistryArtifact.abi,
    wallet,
  );
}

// Health check
app.get("/health", (req, res) => {
  res.json({
    status: "ok",
    deployer: wallet.address,
    network: process.env.RPC_URL,
  });
});

// Deploy StockToken
app.post("/api/deploy/token", async (req, res) => {
  try {
    const { companyId, name, symbol, totalSupply } = req.body;

    if (!companyId || !name || !symbol || !totalSupply) {
      return res.status(400).json({
        error: "Missing required fields: companyId, name, symbol, totalSupply",
      });
    }

    console.log(`📝 Deploying StockToken for ${name} (${symbol})...`);

    // Create contract factory
    const StockTokenFactory = new ethers.ContractFactory(
      StockTokenArtifact.abi,
      StockTokenArtifact.bytecode,
      wallet,
    );

    // Deploy contract
    // StockToken constructor: _name, _symbol, _decimals, _total_supply, _company_name, _ipfs_cid
    const stockToken = await StockTokenFactory.deploy(
      symbol, // _name (token name, use symbol)
      symbol, // _symbol
      18, // _decimals
      totalSupply, // _total_supply
      name, // _company_name
      "QmDefault", // _ipfs_cid (placeholder)
    );

    await stockToken.waitForDeployment();
    const tokenAddress = await stockToken.getAddress();

    console.log(`✅ StockToken deployed at: ${tokenAddress}`);

    // Update registry (admin can do this)
    console.log("📝 Updating registry...");
    const registry = getRegistry();
    const tx = await registry.set_stock_token(companyId, tokenAddress);
    await tx.wait();

    console.log("✅ Registry updated!");

    res.json({
      success: true,
      tokenAddress,
      transactionHash: tx.hash,
    });
  } catch (error) {
    console.error("❌ Error deploying token:", error);
    res.status(500).json({
      error: error.message,
      details: error.reason || error.data?.message,
    });
  }
});

// Deploy StockAMM
app.post("/api/deploy/amm", async (req, res) => {
  try {
    const { companyId } = req.body;

    if (!companyId) {
      return res.status(400).json({ error: "Missing companyId" });
    }

    console.log(`📝 Deploying StockAMM for company #${companyId}...`);

    // Create contract factory
    const StockAMMFactory = new ethers.ContractFactory(
      StockAMMArtifact.abi,
      StockAMMArtifact.bytecode,
      wallet,
    );

    // Deploy contract
    // StockAMM constructor: _fee_rate (in basis points, e.g., 30 = 0.3%)
    const feeRate = 30; // 0.3% fee
    const amm = await StockAMMFactory.deploy(feeRate);
    await amm.waitForDeployment();
    const ammAddress = await amm.getAddress();

    console.log(`✅ StockAMM deployed at: ${ammAddress}`);

    // Update registry (admin can do this)
    console.log("📝 Updating registry...");
    const registry = getRegistry();
    const tx = await registry.set_amm_pool(companyId, ammAddress);
    await tx.wait();

    console.log("✅ Registry updated!");

    res.json({
      success: true,
      ammAddress,
      transactionHash: tx.hash,
    });
  } catch (error) {
    console.error("❌ Error deploying AMM:", error);
    res.status(500).json({
      error: error.message,
      details: error.reason || error.data?.message,
    });
  }
});

// Initialize AMM Pool
app.post("/api/initialize/pool", async (req, res) => {
  try {
    const {
      ammAddress,
      stockTokenAddress,
      baseTokenAddress,
      initialStock,
      initialBase,
    } = req.body;

    if (
      !ammAddress ||
      !stockTokenAddress ||
      !baseTokenAddress ||
      !initialStock ||
      !initialBase
    ) {
      return res.status(400).json({
        error: "Missing required fields",
      });
    }

    console.log(`📝 Initializing pool at ${ammAddress}...`);

    // Get contract instances
    const amm = new ethers.Contract(ammAddress, StockAMMArtifact.abi, wallet);
    const stockToken = new ethers.Contract(
      stockTokenAddress,
      StockTokenArtifact.abi,
      wallet,
    );
    const baseToken = new ethers.Contract(
      baseTokenAddress,
      StockTokenArtifact.abi,
      wallet,
    );

    // Approve tokens
    console.log("📝 Approving tokens...");
    let tx = await stockToken.approve(ammAddress, initialStock);
    await tx.wait();

    tx = await baseToken.approve(ammAddress, initialBase);
    await tx.wait();

    // Initialize pool
    console.log("📝 Initializing pool...");
    tx = await amm.init_pool(
      stockTokenAddress,
      baseTokenAddress,
      initialStock,
      initialBase,
    );
    await tx.wait();

    console.log("✅ Pool initialized!");

    // Get price
    const price = await amm.get_price();
    const priceFormatted = ethers.formatEther(price);

    res.json({
      success: true,
      transactionHash: tx.hash,
      price: priceFormatted,
    });
  } catch (error) {
    console.error("❌ Error initializing pool:", error);
    res.status(500).json({
      error: error.message,
      details: error.reason || error.data?.message,
    });
  }
});

// Get deployer balance
app.get("/api/deployer/balance", async (req, res) => {
  try {
    const balance = await provider.getBalance(wallet.address);
    res.json({
      address: wallet.address,
      balance: ethers.formatEther(balance),
      balanceWei: balance.toString(),
    });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Start server
app.listen(PORT, () => {
  console.log(`🚀 Backend server running on http://localhost:${PORT}`);
  console.log(`📋 Registry: ${process.env.REGISTRY_ADDRESS}`);
  console.log(`💵 Base Token: ${process.env.BASE_TOKEN_ADDRESS}`);
});
