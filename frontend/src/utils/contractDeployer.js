import { ethers } from 'ethers'
import StockTokenArtifact from '../contracts/StockToken.json'
import StockAMMArtifact from '../contracts/StockAMM.json'

/**
 * Deploy a new StockToken contract
 * @param {Object} signer - Ethers signer
 * @param {Object} params - Token parameters
 * @returns {Promise<string>} - Deployed token address
 */
export async function deployStockToken(signer, params) {
  const { name, symbol, decimals, totalSupply, companyName, ipfsCid } = params

  // Convert total supply to wei format (with decimals)
  // e.g., 1000000 tokens with 18 decimals = 1000000 * 10^18
  const totalSupplyWei = ethers.parseUnits(totalSupply.toString(), decimals)

  // Create contract factory
  const factory = new ethers.ContractFactory(
    StockTokenArtifact.abi,
    StockTokenArtifact.bytecode,
    signer
  )

  // Deploy contract
  const contract = await factory.deploy(
    name,              // _name (token name)
    symbol,            // _symbol
    decimals,          // _decimals
    totalSupplyWei,    // _total_supply (in wei format)
    companyName,       // _company_name
    ipfsCid            // _ipfs_cid
  )

  await contract.waitForDeployment()
  const address = await contract.getAddress()

  return address
}

/**
 * Deploy a new StockAMM contract
 * @param {Object} signer - Ethers signer
 * @param {number} feeRate - Fee rate in basis points (e.g., 30 = 0.3%)
 * @returns {Promise<string>} - Deployed AMM address
 */
export async function deployStockAMM(signer, feeRate = 30) {
  // Create contract factory
  const factory = new ethers.ContractFactory(
    StockAMMArtifact.abi,
    StockAMMArtifact.bytecode,
    signer
  )

  // Deploy contract
  const contract = await factory.deploy(feeRate)

  await contract.waitForDeployment()
  const address = await contract.getAddress()

  return address
}

/**
 * Check if user has enough ETH for deployment
 * @param {Object} signer - Ethers signer
 * @param {number} estimatedGas - Estimated gas needed
 * @returns {Promise<boolean>}
 */
export async function checkDeploymentBalance(signer, estimatedGas = 3000000) {
  const address = await signer.getAddress()
  const provider = signer.provider

  const balance = await provider.getBalance(address)
  const gasPrice = (await provider.getFeeData()).gasPrice

  const estimatedCost = gasPrice * BigInt(estimatedGas)

  return balance >= estimatedCost
}

/**
 * Estimate gas for token deployment
 * @param {Object} signer - Ethers signer
 * @param {Object} params - Token parameters
 * @returns {Promise<bigint>}
 */
export async function estimateTokenDeploymentGas(signer, params) {
  const { name, symbol, decimals, totalSupply, companyName, ipfsCid } = params

  const factory = new ethers.ContractFactory(
    StockTokenArtifact.abi,
    StockTokenArtifact.bytecode,
    signer
  )

  const deployTx = await factory.getDeployTransaction(
    name, symbol, decimals, totalSupply, companyName, ipfsCid
  )

  const gasEstimate = await signer.estimateGas(deployTx)
  return gasEstimate
}

export default {
  deployStockToken,
  deployStockAMM,
  checkDeploymentBalance,
  estimateTokenDeploymentGas
}
