import { ethers } from 'ethers'
import toast from './toast.js'

// Contract ABIs (simplified - in production, these would be imported from build artifacts)
const ERC20_ABI = [
  "function name() view returns (string)",
  "function symbol() view returns (string)",
  "function decimals() view returns (uint8)",
  "function totalSupply() view returns (uint256)",
  "function balanceOf(address) view returns (uint256)",
  "function transfer(address to, uint256 amount) returns (bool)",
  "function approve(address spender, uint256 amount) returns (bool)",
  "function allowance(address owner, address spender) view returns (uint256)",
  "function transferFrom(address from, address to, uint256 amount) returns (bool)",
  // BaseToken specific functions
  "function mint(address to, uint256 amount)",
  "function minters(address) view returns (bool)",
  "function owner() view returns (address)",
  "function add_minter(address minter)",
  "function remove_minter(address minter)"
]

const STOCK_TOKEN_ABI = [
  ...ERC20_ABI,
  "function company_name() view returns (string)",
  "function ipfs_cid() view returns (string)",
  "function is_verified() view returns (bool)",
  "function owner() view returns (address)",
  "function set_verified(bool verified)",
  "function update_ipfs_cid(string new_cid)"
]

const AMM_ABI = [
  "function stock_token() view returns (address)",
  "function base_token() view returns (address)",
  "function stock_reserve() view returns (uint256)",
  "function base_reserve() view returns (uint256)",
  "function fee_rate() view returns (uint256)",
  "function is_initialized() view returns (bool)",
  "function init_pool(address stock_token, address base_token, uint256 initial_stock, uint256 initial_base)",
  "function swap_base_for_stock(uint256 amount_in, uint256 min_amount_out) returns (uint256)",
  "function swap_stock_for_base(uint256 amount_in, uint256 min_amount_out) returns (uint256)",
  "function add_liquidity(uint256 stock_amount, uint256 base_amount)",
  "function get_amount_out(uint256 amount_in, address token_in) view returns (uint256)",
  "function get_price() view returns (uint256)",
  "event Swap(address indexed trader, address indexed token_in, address indexed token_out, uint256 amount_in, uint256 amount_out)"
]

const REGISTRY_ABI = [
  "function admin() view returns (address)",
  "function company_count() view returns (uint256)",
  "function verifiers(address) view returns (bool)",
  "function register_company(string name, string symbol, string ipfs_prospectus, string ipfs_financials, string ipfs_logo) returns (uint256)",
  "function set_verified(uint256 company_id, bool verified)",
  "function update_ipfs_prospectus(uint256 company_id, string new_cid)",
  "function update_ipfs_financials(uint256 company_id, string new_cid)",
  "function update_ipfs_logo(uint256 company_id, string new_cid)",
  "function set_stock_token(uint256 company_id, address token_address)",
  "function set_amm_pool(uint256 company_id, address pool_address)",
  "function get_company(uint256 company_id) view returns (tuple(uint256 id, address owner, string name, string symbol, string ipfs_prospectus, string ipfs_financials, string ipfs_logo, bool is_verified, address stock_token, address amm_pool, uint256 created_at))",
  "function get_company_by_symbol(string symbol) view returns (tuple(uint256 id, address owner, string name, string symbol, string ipfs_prospectus, string ipfs_financials, string ipfs_logo, bool is_verified, address stock_token, address amm_pool, uint256 created_at))",
  "function get_company_by_owner(address owner) view returns (tuple(uint256 id, address owner, string name, string symbol, string ipfs_prospectus, string ipfs_financials, string ipfs_logo, bool is_verified, address stock_token, address amm_pool, uint256 created_at))"
]

const MINTER_REGISTRY_ABI = [
  "function admin() view returns (address)",
  "function base_token() view returns (address)",
  "function request_count() view returns (uint256)",
  "function approved_minters(address) view returns (bool)",
  "function request_minter(string reason, string full_name, string email, string ipfs_id_front, string ipfs_id_back, string ipfs_selfie) returns (uint256)",
  "function approve_request(uint256 request_id)",
  "function reject_request(uint256 request_id, string rejection_reason)",
  "function revoke_minter(address minter)",
  "function get_request(uint256 request_id) view returns (tuple(uint256 id, address requester, string reason, string full_name, string email, string ipfs_id_front, string ipfs_id_back, string ipfs_selfie, uint8 status, uint256 created_at, uint256 processed_at, address processed_by, string rejection_reason))",
  "function get_request_by_address(address requester) view returns (tuple(uint256 id, address requester, string reason, string full_name, string email, string ipfs_id_front, string ipfs_id_back, string ipfs_selfie, uint8 status, uint256 created_at, uint256 processed_at, address processed_by, string rejection_reason))",
  "function is_approved_minter(address) view returns (bool)"
]

const TRADER_REGISTRY_ABI = [
  "function admin() view returns (address)",
  "function kyc_count() view returns (uint256)",
  "function verified_traders(address) view returns (bool)",
  "function verifiers(address) view returns (bool)",
  "function submit_kyc(string full_name, string email, string country, string ipfs_id_document, string ipfs_selfie) returns (uint256)",
  "function verify_trader(uint256 kyc_id)",
  "function reject_trader(uint256 kyc_id, string rejection_reason)",
  "function revoke_trader(address trader)",
  "function get_kyc(uint256 kyc_id) view returns (tuple(uint256 id, address trader, string full_name, string email, string country, string ipfs_id_document, string ipfs_selfie, uint8 status, uint256 created_at, uint256 verified_at, address verified_by, string rejection_reason))",
  "function get_kyc_by_address(address trader) view returns (tuple(uint256 id, address trader, string full_name, string email, string country, string ipfs_id_document, string ipfs_selfie, uint8 status, uint256 created_at, uint256 verified_at, address verified_by, string rejection_reason))",
  "function is_verified_trader(address) view returns (bool)",
  "function add_verifier(address verifier)",
  "function remove_verifier(address verifier)"
]

const ENCRYPTED_DOC_REGISTRY_ABI = [
  "function upload_document(string _cid, string _doc_type, string _original_name, uint256 _original_size, uint256 _company_id) external returns (uint256)",
  "function add_recipient(uint256 _doc_id, address _recipient, string _ephemeral_public_key, string _iv, string _ciphertext, string _mac) external",
  "function add_recipients_batch(uint256 _doc_id, address[] _recipients, string[] _ephemeral_public_keys, string[] _ivs, string[] _ciphertexts, string[] _macs) external",
  "function remove_recipient(uint256 _doc_id, address _recipient) external",
  "function revoke_document(uint256 _doc_id) external",
  "function get_document(uint256 _doc_id) external view returns (tuple(uint256 id, address uploader, string cid, string doc_type, string original_name, uint256 original_size, uint256 uploaded_at, bool is_revoked, uint256 company_id))",
  "function get_encrypted_key(uint256 _doc_id, address _recipient) external view returns (tuple(string ephemeral_public_key, string iv, string ciphertext, string mac))",
  "function can_access(uint256 _doc_id, address _recipient) external view returns (bool)",
  "function get_uploader_documents(address _uploader) external view returns (uint256[])",
  "function get_accessible_documents(address _recipient) external view returns (uint256[])",
  "function document_count() external view returns (uint256)",
  "event DocumentUploaded(uint256 indexed doc_id, address indexed uploader, string cid, string doc_type)",
  "event RecipientAdded(uint256 indexed doc_id, address indexed recipient)"
]

const DEPOSIT_CONTRACT_ABI = [
  "function base_token() view returns (address)",
  "function admin() view returns (address)",
  "function eth_to_busd_rate() view returns (uint256)",
  "function total_eth_deposited() view returns (uint256)",
  "function total_busd_minted() view returns (uint256)",
  "function deposit() payable returns (uint256)",
  "function withdraw(uint256 busd_amount) returns (uint256)",
  "function update_rate(uint256 new_rate)",
  "function add_liquidity() payable",
  "function get_deposit_amount(uint256 eth_amount) view returns (uint256)",
  "function get_withdrawal_amount(uint256 busd_amount) view returns (uint256)",
  "function get_contract_balance() view returns (uint256)"
]

// Contract addresses - will be loaded from deployment.json
let CONTRACT_ADDRESSES = {
  BASE_TOKEN: null,
  REGISTRY: null,
  MINTER_REGISTRY: null,
  TRADER_REGISTRY: null,
  DEPOSIT_CONTRACT: null,
  ENCRYPTED_DOC_REGISTRY: null
}

// Load contract addresses from deployment.json
async function loadContractAddresses() {
  try {
    const response = await fetch('/deployment.json')
    const deployment = await response.json()
    CONTRACT_ADDRESSES.BASE_TOKEN = deployment.contracts.BaseToken
    CONTRACT_ADDRESSES.REGISTRY = deployment.contracts.Registry
    CONTRACT_ADDRESSES.MINTER_REGISTRY = deployment.contracts.MinterRegistry || null
    CONTRACT_ADDRESSES.TRADER_REGISTRY = deployment.contracts.TraderRegistry || null
    CONTRACT_ADDRESSES.DEPOSIT_CONTRACT = deployment.contracts.DepositContract || null
    CONTRACT_ADDRESSES.ENCRYPTED_DOC_REGISTRY = deployment.contracts.EncryptedDocRegistry || null
    console.log('📝 Loaded contract addresses:', CONTRACT_ADDRESSES)
    return true
  } catch (error) {
    console.error('❌ Failed to load deployment.json:', error)
    return false
  }
}

class BlockchainService {
  constructor() {
    this.provider = null
    this.signer = null
  }

  async connect() {
    if (typeof window.ethereum !== 'undefined') {
      // Load contract addresses first
      await loadContractAddresses()

      // Request account access - this will show MetaMask popup to select account
      const accounts = await window.ethereum.request({ method: 'eth_requestAccounts' })

      this.provider = new ethers.BrowserProvider(window.ethereum)
      // Get signer for the first account returned (the selected one)
      this.signer = await this.provider.getSigner(accounts[0])
      return true
    }
    return false
  }

  disconnect() {
    // Clear signer but keep provider for read-only operations
    this.signer = null
  }

  async getNetwork() {
    if (!this.provider) return null
    return await this.provider.getNetwork()
  }

  async getBalance(address) {
    if (!this.provider) return '0'
    const balance = await this.provider.getBalance(address)
    return ethers.formatEther(balance)
  }

  // Contract factory methods
  getContract(address, abi, requireSigner = false) {
    // Don't cache contracts - always create with current signer/provider
    // This ensures contracts always use the latest connection state
    const runner = this.signer || this.provider

    if (requireSigner && !this.signer) {
      throw new Error('Signer required but wallet not connected')
    }

    if (!runner) {
      throw new Error('Provider not initialized')
    }

    return new ethers.Contract(address, abi, runner)
  }

  getBaseToken(address = CONTRACT_ADDRESSES.BASE_TOKEN) {
    return this.getContract(address, ERC20_ABI)
  }

  getStockToken(address) {
    return this.getContract(address, STOCK_TOKEN_ABI)
  }

  getAMM(address) {
    return this.getContract(address, AMM_ABI)
  }

  getRegistry(address = CONTRACT_ADDRESSES.REGISTRY) {
    return this.getContract(address, REGISTRY_ABI)
  }

  // Token operations
  async getTokenBalance(tokenAddress, accountAddress) {
    /**
     * Get token balance for an account
     * @param {string} tokenAddress - Token contract address
     * @param {string} accountAddress - Account address to check
     * @returns {Promise<string>} - Balance in human-readable format
     */
    try {
      const token = this.getStockToken(tokenAddress)
      const balance = await token.balanceOf(accountAddress)
      const decimals = await token.decimals()
      return ethers.formatUnits(balance, decimals)
    } catch (error) {
      console.error('Error getting token balance:', error)
      return '0'
    }
  }

  async getBaseTokenBalance(accountAddress) {
    /**
     * Get base token (BUSD) balance for an account
     * @param {string} accountAddress - Account address to check
     * @returns {Promise<string>} - Balance in human-readable format
     */
    try {
      const token = this.getBaseToken()
      const balance = await token.balanceOf(accountAddress)
      return ethers.formatUnits(balance, 18)
    } catch (error) {
      console.error('Error getting base token balance:', error)
      return '0'
    }
  }

  async approveToken(tokenAddress, spenderAddress, amount) {
    try {
      const token = this.getContract(tokenAddress, ERC20_ABI)
      const decimals = await token.decimals()
      const symbol = await token.symbol()
      const amountWei = ethers.parseUnits(amount.toString(), decimals)

      toast.txStep(`Approve ${amount} ${symbol}`, `Allow the contract to spend your ${symbol} tokens`)
      const tx = await token.approve(spenderAddress, amountWei)

      toast.txPending(`Approving ${symbol}`)
      const receipt = await tx.wait()
      toast.txConfirmed(`${symbol} approved`, `You can now proceed with the transaction`)
      return receipt
    } catch (error) {
      console.error('Error approving token:', error)
      throw error
    }
  }

  // AMM operations
  async getAMMPrice(ammAddress) {
    try {
      const amm = this.getAMM(ammAddress)
      const price = await amm.get_price()
      return ethers.formatUnits(price, 18)
    } catch (error) {
      console.error('Error getting AMM price:', error)
      return '0'
    }
  }

  async getAMMReserves(ammAddress) {
    try {
      const amm = this.getAMM(ammAddress)
      const [stockReserve, baseReserve] = await Promise.all([
        amm.stock_reserve(),
        amm.base_reserve()
      ])

      return {
        stock: ethers.formatUnits(stockReserve, 18),
        base: ethers.formatUnits(baseReserve, 18)
      }
    } catch (error) {
      console.error('Error getting AMM reserves:', error)
      return { stock: '0', base: '0' }
    }
  }

  async getSwapOutput(ammAddress, amountIn, tokenInAddress) {
    try {
      const amm = this.getAMM(ammAddress)
      const amountInWei = ethers.parseUnits(amountIn.toString(), 18)
      const output = await amm.get_amount_out(amountInWei, tokenInAddress)
      return ethers.formatUnits(output, 18)
    } catch (error) {
      console.error('Error getting swap output:', error)
      return '0'
    }
  }

  async swapTokens(ammAddress, amountIn, minAmountOut, isBaseForStock = true) {
    try {
      const amm = this.getAMM(ammAddress)
      const amountInWei = ethers.parseUnits(amountIn.toString(), 18)
      const minAmountOutWei = ethers.parseUnits(minAmountOut.toString(), 18)

      const action = isBaseForStock ? 'Buy Stock Tokens' : 'Sell Stock Tokens'
      const details = isBaseForStock
        ? `Swap ${amountIn} BUSD for stock tokens (min: ${minAmountOut.toFixed(4)})`
        : `Swap ${amountIn} stock tokens for BUSD (min: ${minAmountOut.toFixed(4)})`

      toast.txStep(action, details)

      let tx
      if (isBaseForStock) {
        tx = await amm.swap_base_for_stock(amountInWei, minAmountOutWei)
      } else {
        tx = await amm.swap_stock_for_base(amountInWei, minAmountOutWei)
      }

      toast.txPending('Executing swap')
      const receipt = await tx.wait()
      toast.txConfirmed('Swap completed', `Transaction hash: ${receipt.hash.slice(0, 10)}...`)
      return receipt
    } catch (error) {
      console.error('Error swapping tokens:', error)
      throw error
    }
  }

  async getRecentTrades(ammAddress, traderAddress = null, limit = 20) {
    try {
      const amm = this.getAMM(ammAddress)

      // Get the current block number
      const currentBlock = await this.provider.getBlockNumber()
      // Look back more blocks to find trades (local dev chains have fewer blocks)
      const fromBlock = Math.max(0, currentBlock - 50000)

      console.log(`📊 Fetching trades from block ${fromBlock} to ${currentBlock} for AMM ${ammAddress}`)

      // Create filter for Swap events - filter by trader if provided
      // The Swap event has: trader (indexed), token_in (indexed), token_out (indexed), amount_in, amount_out
      let filter
      if (traderAddress) {
        filter = amm.filters.Swap(traderAddress)
      } else {
        filter = amm.filters.Swap()
      }

      const events = await amm.queryFilter(filter, fromBlock, currentBlock)
      console.log(`📊 Found ${events.length} swap events`)

      if (events.length === 0) {
        return []
      }

      // Get base token address to determine trade type
      const baseToken = await amm.base_token()

      // Parse events into trade objects
      const trades = await Promise.all(events.slice(-limit).reverse().map(async (event) => {
        try {
          const block = await event.getBlock()
          const isBuy = event.args.token_in.toLowerCase() === baseToken.toLowerCase()

          return {
            id: event.transactionHash,
            type: isBuy ? 'buy' : 'sell',
            trader: event.args.trader,
            amountIn: ethers.formatUnits(event.args.amount_in, 18),
            amountOut: ethers.formatUnits(event.args.amount_out, 18),
            timestamp: new Date(block.timestamp * 1000),
            txHash: event.transactionHash
          }
        } catch (err) {
          console.warn('Error parsing trade event:', err)
          return null
        }
      }))

      // Filter out any null entries from failed parses
      return trades.filter(t => t !== null)
    } catch (error) {
      console.error('Error fetching recent trades:', error)
      return []
    }
  }

  async getPriceHistory(ammAddress, limit = 50) {
    /**
     * Get price history from swap events
     * Returns array of { price, timestamp, volume } objects
     */
    try {
      const amm = this.getAMM(ammAddress)
      const currentBlock = await this.provider.getBlockNumber()
      const fromBlock = Math.max(0, currentBlock - 100000)

      // Get all swap events
      const filter = amm.filters.Swap()
      const events = await amm.queryFilter(filter, fromBlock, currentBlock)

      if (events.length === 0) {
        // No trades yet, return current price as single point
        const currentPrice = await this.getAMMPrice(ammAddress)
        return [{
          price: parseFloat(currentPrice),
          timestamp: new Date(),
          volume: 0
        }]
      }

      const baseToken = await amm.base_token()
      const priceHistory = []

      // Process events to calculate price after each trade
      for (const event of events.slice(-limit)) {
        try {
          const block = await event.getBlock()
          const isBuy = event.args.token_in.toLowerCase() === baseToken.toLowerCase()

          // Calculate effective price from the swap
          const amountIn = parseFloat(ethers.formatUnits(event.args.amount_in, 18))
          const amountOut = parseFloat(ethers.formatUnits(event.args.amount_out, 18))

          // Price = base amount / stock amount
          let price
          if (isBuy) {
            // Buying stock: paid base, received stock
            price = amountIn / amountOut
          } else {
            // Selling stock: paid stock, received base
            price = amountOut / amountIn
          }

          priceHistory.push({
            price,
            timestamp: new Date(block.timestamp * 1000),
            volume: isBuy ? amountIn : amountOut,
            type: isBuy ? 'buy' : 'sell'
          })
        } catch (err) {
          console.warn('Error parsing price event:', err)
        }
      }

      // Add current price as the latest point
      const currentPrice = await this.getAMMPrice(ammAddress)
      priceHistory.push({
        price: parseFloat(currentPrice),
        timestamp: new Date(),
        volume: 0
      })

      return priceHistory
    } catch (error) {
      console.error('Error fetching price history:', error)
      return []
    }
  }

  async get24hPriceChange(ammAddress) {
    /**
     * Calculate 24h price change percentage
     */
    try {
      const priceHistory = await this.getPriceHistory(ammAddress, 100)

      if (priceHistory.length < 2) {
        return 0
      }

      const now = Date.now()
      const oneDayAgo = now - 24 * 60 * 60 * 1000

      // Find the oldest price within 24h
      const oldPrice = priceHistory.find(p => p.timestamp.getTime() >= oneDayAgo)?.price || priceHistory[0].price
      const currentPrice = priceHistory[priceHistory.length - 1].price

      if (oldPrice === 0) return 0
      return ((currentPrice - oldPrice) / oldPrice) * 100
    } catch (error) {
      console.error('Error calculating 24h price change:', error)
      return 0
    }
  }

  async get24hVolume(ammAddress) {
    /**
     * Calculate 24h trading volume in base token
     */
    try {
      const priceHistory = await this.getPriceHistory(ammAddress, 1000)

      const now = Date.now()
      const oneDayAgo = now - 24 * 60 * 60 * 1000

      const volume = priceHistory
        .filter(p => p.timestamp.getTime() >= oneDayAgo)
        .reduce((sum, p) => sum + (p.volume || 0), 0)

      return volume
    } catch (error) {
      console.error('Error calculating 24h volume:', error)
      return 0
    }
  }

  // Registry operations
  async registerCompany(name, symbol, ipfsProspectus, ipfsFinancials, ipfsLogo) {
    try {
      const registry = this.getRegistry()

      toast.txStep('Register Company', `Registering ${name} (${symbol}) on the blockchain`)
      const tx = await registry.register_company(
        name,
        symbol,
        ipfsProspectus || '',
        ipfsFinancials || '',
        ipfsLogo || ''
      )

      toast.txPending('Registering company')
      const receipt = await tx.wait()
      toast.txConfirmed('Company registered', `${name} has been registered on-chain`)

      // Extract company ID from events
      const event = receipt.logs.find(log => {
        try {
          const parsed = registry.interface.parseLog(log)
          return parsed.name === 'CompanyRegistered'
        } catch {
          return false
        }
      })

      if (event) {
        const parsed = registry.interface.parseLog(event)
        return parsed.args.company_id
      }

      return null
    } catch (error) {
      console.error('Error registering company:', error)
      throw error
    }
  }

  async getCompany(companyId) {
    try {
      const registry = this.getRegistry()
      const company = await registry.get_company(companyId)
      return {
        id: company.id.toString(),
        owner: company.owner,
        name: company.name,
        symbol: company.symbol,
        ipfsProspectus: company.ipfs_prospectus,
        ipfsFinancials: company.ipfs_financials,
        ipfsLogo: company.ipfs_logo,
        isVerified: company.is_verified,
        stockToken: company.stock_token,
        ammPool: company.amm_pool,
        createdAt: new Date(Number(company.created_at) * 1000)
      }
    } catch (error) {
      console.error('Error getting company:', error)
      return null
    }
  }

  async getCompanyBySymbol(symbol) {
    try {
      const registry = this.getRegistry()
      const company = await registry.get_company_by_symbol(symbol)
      return {
        id: company.id.toString(),
        owner: company.owner,
        name: company.name,
        symbol: company.symbol,
        ipfsProspectus: company.ipfs_prospectus,
        ipfsFinancials: company.ipfs_financials,
        ipfsLogo: company.ipfs_logo,
        isVerified: company.is_verified,
        stockToken: company.stock_token,
        ammPool: company.amm_pool,
        createdAt: new Date(Number(company.created_at) * 1000)
      }
    } catch (error) {
      console.error('Error getting company by symbol:', error)
      return null
    }
  }

  async getCompanyByOwner(ownerAddress) {
    try {
      const registry = this.getRegistry()
      const company = await registry.get_company_by_owner(ownerAddress)

      // Check if AMM pool is initialized
      let isInitialized = false
      if (company.amm_pool && company.amm_pool !== '0x0000000000000000000000000000000000000000') {
        try {
          const amm = this.getAMM(company.amm_pool)
          isInitialized = await amm.is_initialized()
        } catch (error) {
          console.warn('Could not check AMM initialization status:', error)
        }
      }

      return {
        id: company.id.toString(),
        owner: company.owner,
        name: company.name,
        symbol: company.symbol,
        ipfsProspectus: company.ipfs_prospectus,
        ipfsFinancials: company.ipfs_financials,
        ipfsLogo: company.ipfs_logo,
        isVerified: company.is_verified,
        stockToken: company.stock_token,
        ammPool: company.amm_pool,
        isInitialized: isInitialized,
        createdAt: new Date(Number(company.created_at) * 1000)
      }
    } catch (error) {
      // "Company not found" is expected when address has no company - don't log as error
      if (!error.message?.includes('Company not found')) {
        console.error('Error getting company by owner:', error)
      }
      throw error // Re-throw so caller can handle it
    }
  }

  async getAllCompanies() {
    try {
      const registry = this.getRegistry()
      const count = await registry.company_count()
      const companies = []

      for (let i = 1; i <= count; i++) {
        const company = await this.getCompany(i)
        if (company) {
          companies.push(company)
        }
      }

      return companies
    } catch (error) {
      console.error('Error getting all companies:', error)
      return []
    }
  }

  // Utility methods
  formatAddress(address) {
    if (!address) return ''
    return `${address.slice(0, 6)}...${address.slice(-4)}`
  }

  async waitForTransaction(txHash) {
    if (!this.provider) throw new Error('Provider not connected')
    return await this.provider.waitForTransaction(txHash)
  }

  // Load contract addresses from deployment file
  async loadContractAddresses() {
    try {
      const response = await fetch('/deployment.json')
      const deployment = await response.json()

      CONTRACT_ADDRESSES.BASE_TOKEN = deployment.contracts.BaseToken
      CONTRACT_ADDRESSES.REGISTRY = deployment.contracts.Registry
      CONTRACT_ADDRESSES.MINTER_REGISTRY = deployment.contracts.MinterRegistry || null
      CONTRACT_ADDRESSES.TRADER_REGISTRY = deployment.contracts.TraderRegistry || null
      CONTRACT_ADDRESSES.DEPOSIT_CONTRACT = deployment.contracts.DepositContract || null
      CONTRACT_ADDRESSES.ENCRYPTED_DOC_REGISTRY = deployment.contracts.EncryptedDocRegistry || null

      console.log('Loaded contract addresses:', CONTRACT_ADDRESSES)
      return deployment
    } catch (error) {
      console.warn('Could not load deployment.json:', error)
      return null
    }
  }

  // ========== TRADER REGISTRY METHODS ==========

  getTraderRegistry() {
    if (!CONTRACT_ADDRESSES.TRADER_REGISTRY) {
      console.warn('⚠️ TraderRegistry address not configured. Please ensure deployment.json includes TraderRegistry.')
      throw new Error('TraderRegistry address not configured')
    }
    return this.getContract(CONTRACT_ADDRESSES.TRADER_REGISTRY, TRADER_REGISTRY_ABI)
  }

  async submitTraderKYC(kycData) {
    const registry = this.getTraderRegistry()

    toast.txStep('Submit KYC', 'Submit your identity verification for trading access')
    const tx = await registry.submit_kyc(
      kycData.fullName,
      kycData.email,
      kycData.country,
      kycData.ipfsIdDocument,
      kycData.ipfsSelfie
    )

    toast.txPending('Submitting KYC')
    await tx.wait()
    toast.txConfirmed('KYC submitted', 'Your verification request is pending review')
    return tx
  }

  // Helper method to map Vyper enum status values to strings
  // Vyper 0.4.x enums are bit flags: PENDING=1, VERIFIED=2, REJECTED=4, REVOKED=8
  _mapTraderStatus(statusValue) {
    const statusNum = Number(statusValue)
    switch (statusNum) {
      case 1: return 'PENDING'
      case 2: return 'VERIFIED'
      case 4: return 'REJECTED'
      case 8: return 'REVOKED'
      default:
        console.warn('Unknown trader status value:', statusNum)
        return 'UNKNOWN'
    }
  }

  async getTraderKYC(address) {
    const registry = this.getTraderRegistry()
    try {
      const kyc = await registry.get_kyc_by_address(address)
      const verifiedOnChain = await registry.is_verified_trader(address)
      console.log('🔍 KYC raw status from contract:', kyc.status, 'verifiedOnChain:', verifiedOnChain)
      return {
        id: kyc.id.toString(),
        trader: kyc.trader,
        fullName: kyc.full_name,
        email: kyc.email,
        country: kyc.country,
        ipfsIdDocument: kyc.ipfs_id_document,
        ipfsSelfie: kyc.ipfs_selfie,
        status: this._mapTraderStatus(kyc.status),
        verifiedOnChain,
        createdAt: new Date(Number(kyc.created_at) * 1000),
        verifiedAt: kyc.verified_at > 0 ? new Date(Number(kyc.verified_at) * 1000) : null,
        verifiedBy: kyc.verified_by,
        rejectionReason: kyc.rejection_reason
      }
    } catch (error) {
      if (error.message?.includes('No KYC found')) {
        return null
      }
      throw error
    }
  }

  async getAllTraderKYCs() {
    const registry = this.getTraderRegistry()
    const count = await registry.kyc_count()
    const kycs = []

    for (let i = 1; i <= count; i++) {
      try {
        const kyc = await registry.get_kyc(i)
        const verifiedOnChain = await registry.is_verified_trader(kyc.trader)
        kycs.push({
          id: kyc.id.toString(),
          trader: kyc.trader,
          fullName: kyc.full_name,
          email: kyc.email,
          country: kyc.country,
          ipfsIdDocument: kyc.ipfs_id_document,
          ipfsSelfie: kyc.ipfs_selfie,
          status: this._mapTraderStatus(kyc.status),
          verifiedOnChain,
          createdAt: new Date(Number(kyc.created_at) * 1000),
          verifiedAt: kyc.verified_at > 0 ? new Date(Number(kyc.verified_at) * 1000) : null,
          verifiedBy: kyc.verified_by,
          rejectionReason: kyc.rejection_reason
        })
      } catch (error) {
        console.warn(`Could not fetch KYC ${i}:`, error)
      }
    }

    return kycs
  }

  async verifyTraderKYC(kycId) {
    const registry = this.getTraderRegistry()

    toast.txStep('Verify Trader', `Approving trader KYC #${kycId}`)
    const tx = await registry.verify_trader(kycId)

    toast.txPending('Verifying trader')
    await tx.wait()
    toast.txConfirmed('Trader verified', 'Trader can now access trading features')
    return tx
  }

  async rejectTraderKYC(kycId, reason) {
    const registry = this.getTraderRegistry()

    toast.txStep('Reject KYC', `Rejecting trader KYC #${kycId}`)
    const tx = await registry.reject_trader(kycId, reason)

    toast.txPending('Rejecting KYC')
    await tx.wait()
    toast.txConfirmed('KYC rejected', 'Trader has been notified')
    return tx
  }

  async revokeTrader(traderAddress) {
    const registry = this.getTraderRegistry()

    toast.txStep('Revoke Trader', 'Revoking trader access')
    const tx = await registry.revoke_trader(traderAddress)

    toast.txPending('Revoking access')
    await tx.wait()
    toast.txConfirmed('Access revoked', 'Trader can no longer trade')
    return tx
  }

  async isVerifiedTrader(address) {
    try {
      const registry = this.getTraderRegistry()
      const isVerified = await registry.is_verified_trader(address)
      console.log('🔍 TraderRegistry.is_verified_trader:', isVerified)
      return isVerified
    } catch (error) {
      console.error('Error checking trader verification:', error)
      return false
    }
  }

  // ========== DEPOSIT CONTRACT METHODS ==========

  getDepositContract() {
    if (!CONTRACT_ADDRESSES.DEPOSIT_CONTRACT) {
      console.warn('⚠️ DepositContract address not configured. Please ensure deployment.json includes DepositContract.')
      throw new Error('DepositContract address not configured')
    }
    return this.getContract(CONTRACT_ADDRESSES.DEPOSIT_CONTRACT, DEPOSIT_CONTRACT_ABI)
  }

  async depositETH(ethAmount) {
    const depositContract = this.getDepositContract()

    toast.txStep('Deposit ETH', `Convert ${ethAmount} ETH to BUSD`)
    const tx = await depositContract.deposit({ value: ethers.parseEther(ethAmount.toString()) })

    toast.txPending('Processing deposit')
    const receipt = await tx.wait()
    toast.txConfirmed('Deposit successful', `${ethAmount} ETH converted to BUSD`)
    return receipt
  }

  async withdrawBUSD(busdAmount) {
    const depositContract = this.getDepositContract()
    const busdAmountWei = ethers.parseUnits(busdAmount.toString(), 18)

    // First approve the deposit contract to spend BUSD
    const baseToken = this.getBaseToken()
    toast.txStep('Approve BUSD', `Allow withdrawal of ${busdAmount} BUSD`)
    const approveTx = await baseToken.approve(CONTRACT_ADDRESSES.DEPOSIT_CONTRACT, busdAmountWei)

    toast.txPending('Approving BUSD')
    await approveTx.wait()
    toast.txConfirmed('BUSD approved')

    // Then withdraw
    toast.txStep('Withdraw BUSD', `Convert ${busdAmount} BUSD to ETH`)
    const tx = await depositContract.withdraw(busdAmountWei)

    toast.txPending('Processing withdrawal')
    const receipt = await tx.wait()
    toast.txConfirmed('Withdrawal successful', `${busdAmount} BUSD converted to ETH`)
    return receipt
  }

  async getDepositAmount(ethAmount) {
    try {
      const depositContract = this.getDepositContract()
      const ethAmountWei = ethers.parseEther(ethAmount.toString())
      const busdAmount = await depositContract.get_deposit_amount(ethAmountWei)
      return ethers.formatUnits(busdAmount, 18)
    } catch (error) {
      console.error('Error calculating deposit amount:', error)
      return '0'
    }
  }

  async getWithdrawalAmount(busdAmount) {
    try {
      const depositContract = this.getDepositContract()
      const busdAmountWei = ethers.parseUnits(busdAmount.toString(), 18)
      const ethAmount = await depositContract.get_withdrawal_amount(busdAmountWei)
      return ethers.formatEther(ethAmount)
    } catch (error) {
      console.error('Error calculating withdrawal amount:', error)
      return '0'
    }
  }

  async getETHtoBUSDRate() {
    try {
      const depositContract = this.getDepositContract()
      const rate = await depositContract.eth_to_busd_rate()
      return ethers.formatUnits(rate, 18)
    } catch (error) {
      console.error('Error getting ETH to BUSD rate:', error)
      return '0'
    }
  }

  getMinterRegistry() {
    if (!CONTRACT_ADDRESSES.MINTER_REGISTRY) {
      console.warn('⚠️ MinterRegistry address not configured. Please ensure deployment.json includes MinterRegistry.')
      throw new Error('MinterRegistry address not configured')
    }
    return this.getContract(CONTRACT_ADDRESSES.MINTER_REGISTRY, MINTER_REGISTRY_ABI)
  }

  async requestMinter(kycData) {
    const registry = this.getMinterRegistry()

    toast.txStep('Submit Minter Request', 'Submit your KYC information for minter approval')
    const tx = await registry.request_minter(
      kycData.reason,
      kycData.fullName,
      kycData.email,
      kycData.ipfsIdFront,
      kycData.ipfsIdBack,
      kycData.ipfsSelfie
    )

    toast.txPending('Submitting request')
    await tx.wait()
    toast.txConfirmed('Request submitted', 'Your minter request is pending admin approval')
    return tx
  }

  // Helper method to map Vyper enum status values to strings
  // Vyper enums are bit flags: PENDING=1, APPROVED=2, REJECTED=4, REVOKED=8
  _mapMinterStatus(statusValue) {
    const statusNum = Number(statusValue)
    switch (statusNum) {
      case 1: return 'PENDING'
      case 2: return 'APPROVED'
      case 4: return 'REJECTED'
      case 8: return 'REVOKED'
      default:
        console.warn('Unknown minter status value:', statusNum)
        return 'UNKNOWN'
    }
  }

  async getMinterRequest(address) {
    const registry = this.getMinterRegistry()
    try {
      const request = await registry.get_request_by_address(address)
      return {
        id: request.id.toString(),
        requester: request.requester,
        reason: request.reason,
        fullName: request.full_name,
        email: request.email,
        ipfsIdFront: request.ipfs_id_front,
        ipfsIdBack: request.ipfs_id_back,
        ipfsSelfie: request.ipfs_selfie,
        status: this._mapMinterStatus(request.status),
        createdAt: new Date(Number(request.created_at) * 1000),
        processedAt: request.processed_at > 0 ? new Date(Number(request.processed_at) * 1000) : null,
        processedBy: request.processed_by,
        rejectionReason: request.rejection_reason
      }
    } catch (error) {
      if (error.message?.includes('No request found')) {
        return null
      }
      throw error
    }
  }

  async getAllMinterRequests() {
    const registry = this.getMinterRegistry()
    const count = await registry.request_count()
    const requests = []

    for (let i = 1; i <= count; i++) {
      try {
        const request = await registry.get_request(i)
        requests.push({
          id: request.id.toString(),
          requester: request.requester,
          reason: request.reason,
          fullName: request.full_name,
          email: request.email,
          ipfsIdFront: request.ipfs_id_front,
          ipfsIdBack: request.ipfs_id_back,
          ipfsSelfie: request.ipfs_selfie,
          status: this._mapMinterStatus(request.status),
          createdAt: new Date(Number(request.created_at) * 1000),
          processedAt: request.processed_at > 0 ? new Date(Number(request.processed_at) * 1000) : null,
          processedBy: request.processed_by,
          rejectionReason: request.rejection_reason
        })
      } catch (error) {
        console.warn(`Could not fetch request ${i}:`, error)
      }
    }

    return requests
  }

  async approveMinterRequest(requestId) {
    const registry = this.getMinterRegistry()

    // First approve in registry
    toast.txStep('Approve Minter Request', `Approving minter request #${requestId}`)
    const tx = await registry.approve_request(requestId)
    toast.txPending('Approving request')
    await tx.wait()
    toast.txConfirmed('Request approved')

    // Get the requester address
    const request = await registry.get_request(requestId)

    // Add minter to BaseToken
    const baseToken = this.getBaseToken()
    toast.txStep('Grant Minter Permission', 'Adding minter to BaseToken contract')
    const tx2 = await baseToken.add_minter(request.requester)
    toast.txPending('Granting permission')
    await tx2.wait()
    toast.txConfirmed('Minter permission granted', 'User can now mint BUSD')

    return tx
  }

  async rejectMinterRequest(requestId, reason) {
    const registry = this.getMinterRegistry()

    toast.txStep('Reject Minter Request', `Rejecting minter request #${requestId}`)
    const tx = await registry.reject_request(requestId, reason)

    toast.txPending('Rejecting request')
    await tx.wait()
    toast.txConfirmed('Request rejected', 'Requester has been notified')
    return tx
  }

  async revokeMinter(minterAddress) {
    const registry = this.getMinterRegistry()

    // Revoke in registry
    toast.txStep('Revoke Minter', 'Revoking minter status in registry')
    const tx = await registry.revoke_minter(minterAddress)
    toast.txPending('Revoking in registry')
    await tx.wait()
    toast.txConfirmed('Registry updated')

    // Remove from BaseToken
    const baseToken = this.getBaseToken()
    toast.txStep('Remove Minter Permission', 'Removing from BaseToken contract')
    const tx2 = await baseToken.remove_minter(minterAddress)
    toast.txPending('Removing permission')
    await tx2.wait()
    toast.txConfirmed('Minter revoked', 'User can no longer mint BUSD')

    return tx
  }

  async isMinter(address) {
    try {
      // Check MinterRegistry for approved minters (KYC-based system)
      const registry = this.getMinterRegistry()
      const isApproved = await registry.is_approved_minter(address)
      console.log('🔍 MinterRegistry.is_approved_minter:', isApproved)

      // Also check BaseToken for backward compatibility
      const baseToken = this.getBaseToken()
      const isBaseTokenMinter = await baseToken.minters(address)
      console.log('🔍 BaseToken.minters:', isBaseTokenMinter)

      // User is a minter if approved in either system
      return isApproved || isBaseTokenMinter
    } catch (error) {
      console.error('Error checking minter status:', error)
      // Fallback to BaseToken check if MinterRegistry not available
      try {
        const baseToken = this.getBaseToken()
        return await baseToken.minters(address)
      } catch (e) {
        return false
      }
    }
  }

  // ========== ENCRYPTED DOCUMENT REGISTRY METHODS ==========

  getEncryptedDocRegistry() {
    if (!CONTRACT_ADDRESSES.ENCRYPTED_DOC_REGISTRY) {
      console.warn('⚠️ EncryptedDocRegistry address not configured.')
      throw new Error('EncryptedDocRegistry address not configured')
    }
    return this.getContract(CONTRACT_ADDRESSES.ENCRYPTED_DOC_REGISTRY, ENCRYPTED_DOC_REGISTRY_ABI)
  }

  async uploadEncryptedDocument(cid, docType, originalName, originalSize, companyId = 0) {
    const registry = this.getEncryptedDocRegistry()

    toast.txStep('Register Encrypted Document', `Registering ${docType} document on-chain`)
    const tx = await registry.upload_document(cid, docType, originalName, originalSize, companyId)

    toast.txPending('Registering document')
    const receipt = await tx.wait()
    toast.txConfirmed('Document registered', `${docType} metadata stored on-chain`)

    // Extract document ID from event
    const event = receipt.logs.find(log => {
      try {
        const parsed = registry.interface.parseLog(log)
        return parsed.name === 'DocumentUploaded'
      } catch {
        return false
      }
    })

    if (event) {
      const parsed = registry.interface.parseLog(event)
      return Number(parsed.args.doc_id)
    }
    return null
  }

  async addDocumentRecipient(docId, recipient, encryptedKey) {
    const registry = this.getEncryptedDocRegistry()

    toast.txStep('Add Document Recipient', `Grant access to document #${docId}`)
    const tx = await registry.add_recipient(
      docId,
      recipient,
      encryptedKey.ephemeralPublicKey,
      encryptedKey.iv,
      encryptedKey.ciphertext,
      encryptedKey.mac
    )

    toast.txPending('Adding recipient')
    await tx.wait()
    toast.txConfirmed('Recipient added', 'Access granted successfully')
    return tx
  }

  async addDocumentRecipientsBatch(docId, recipients, encryptedKeys) {
    const registry = this.getEncryptedDocRegistry()

    toast.txStep('Add Recipients Batch', `Grant access to ${recipients.length} recipients`)
    const tx = await registry.add_recipients_batch(
      docId,
      recipients,
      encryptedKeys.map(k => k.ephemeralPublicKey),
      encryptedKeys.map(k => k.iv),
      encryptedKeys.map(k => k.ciphertext),
      encryptedKeys.map(k => k.mac)
    )

    toast.txPending('Adding recipients')
    await tx.wait()
    toast.txConfirmed('Recipients added', `${recipients.length} users granted access`)
    return tx
  }

  async getEncryptedDocument(docId) {
    const registry = this.getEncryptedDocRegistry()
    const doc = await registry.get_document(docId)
    return {
      id: Number(doc.id),
      uploader: doc.uploader,
      cid: doc.cid,
      docType: doc.doc_type,
      originalName: doc.original_name,
      originalSize: Number(doc.original_size),
      uploadedAt: new Date(Number(doc.uploaded_at) * 1000),
      isRevoked: doc.is_revoked,
      companyId: Number(doc.company_id)
    }
  }

  async getEncryptedKey(docId, recipientAddress) {
    const registry = this.getEncryptedDocRegistry()
    const key = await registry.get_encrypted_key(docId, recipientAddress)
    return {
      ephemeralPublicKey: key.ephemeral_public_key,
      iv: key.iv,
      ciphertext: key.ciphertext,
      mac: key.mac
    }
  }

  async canAccessDocument(docId, recipientAddress) {
    const registry = this.getEncryptedDocRegistry()
    return await registry.can_access(docId, recipientAddress)
  }

  async getEncryptedDocCount() {
    const registry = this.getEncryptedDocRegistry()
    const count = await registry.document_count()
    return Number(count)
  }

  async getCompanyEncryptedDocuments(companyId) {
    const registry = this.getEncryptedDocRegistry()
    const docCount = await registry.document_count()
    console.log('📊 Total document count in registry:', Number(docCount))
    const docs = []

    for (let i = 1; i <= docCount; i++) {
      try {
        const doc = await this.getEncryptedDocument(i)
        console.log(`📄 Document ${i}:`, doc.companyId, 'vs', companyId, '| revoked:', doc.isRevoked)
        if (doc.companyId === companyId && !doc.isRevoked) {
          docs.push(doc)
        }
      } catch (e) {
        console.warn(`⚠️ Could not load document ${i}:`, e.message)
      }
    }
    console.log('✅ Found', docs.length, 'documents for company', companyId)
    return docs
  }

  async getMyUploadedDocuments() {
    const registry = this.getEncryptedDocRegistry()
    const address = await this.signer.getAddress()
    const docIds = await registry.get_uploader_documents(address)

    const docs = await Promise.all(
      docIds.map(id => this.getEncryptedDocument(Number(id)))
    )
    return docs
  }

  async getMyAccessibleDocuments() {
    const registry = this.getEncryptedDocRegistry()
    const address = await this.signer.getAddress()
    const docIds = await registry.get_accessible_documents(address)

    const docs = await Promise.all(
      docIds.map(id => this.getEncryptedDocument(Number(id)))
    )
    return docs
  }

  async revokeEncryptedDocument(docId) {
    const registry = this.getEncryptedDocRegistry()

    toast.txStep('Revoke Document', `Revoking access to document #${docId}`)
    const tx = await registry.revoke_document(docId)

    toast.txPending('Revoking document')
    await tx.wait()
    toast.txConfirmed('Document revoked', 'All access has been removed')
    return tx
  }

  // Initialize the blockchain service
  async initialize() {
    try {
      // Load contract addresses first
      await this.loadContractAddresses()

      // Initialize provider for read-only operations
      if (typeof window.ethereum !== 'undefined') {
        this.provider = new ethers.BrowserProvider(window.ethereum)

        // Try to connect signer if wallet is already connected
        const accounts = await window.ethereum.request({ method: 'eth_accounts' })
        if (accounts.length > 0) {
          // Use the first connected account
          this.signer = await this.provider.getSigner(accounts[0])
        }
      }

      return true
    } catch (error) {
      console.error('Error initializing blockchain service:', error)
      return false
    }
  }
}

// Export singleton instance
export const blockchain = new BlockchainService()
export default blockchain
