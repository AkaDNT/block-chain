<template>
  <div class="space-y-8">
    <div class="text-center">
      <h1 class="text-3xl font-bold text-gray-900 mb-4">Dashboard</h1>
      <p class="text-gray-600">Monitor your portfolio and market activity</p>
    </div>

    <!-- Loading State -->
    <div v-if="isLoading" class="flex items-center justify-center py-12">
      <svg class="animate-spin h-12 w-12 text-blue-600" fill="none" viewBox="0 0 24 24">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
      </svg>
    </div>

    <template v-else>
    <!-- Portfolio Overview -->
    <div class="grid md:grid-cols-4 gap-6">
      <div class="card text-center">
        <div class="text-3xl font-bold text-blue-600 mb-2">{{ totalValue.toFixed(2) }} <span class="text-lg">BUSD</span></div>
        <div class="text-gray-600">Total Portfolio Value</div>
        <div class="text-sm text-gray-500 mt-1">Holdings + Cash</div>
      </div>

      <div class="card text-center">
        <div class="text-3xl font-bold text-green-600 mb-2">{{ cashBalance.toFixed(2) }} <span class="text-lg">BUSD</span></div>
        <div class="text-gray-600">Cash Balance</div>
        <div class="text-sm text-gray-500 mt-1">Available for trading</div>
      </div>

      <div class="card text-center">
        <div class="text-3xl font-bold text-purple-600 mb-2">{{ totalTrades }}</div>
        <div class="text-gray-600">Total Trades</div>
        <div class="text-sm text-gray-500 mt-1">All time</div>
      </div>

      <div class="card text-center">
        <div class="text-3xl font-bold text-orange-600 mb-2">{{ holdings.length }}</div>
        <div class="text-gray-600">Token Holdings</div>
        <div class="text-sm text-gray-500 mt-1">Different tokens</div>
      </div>
    </div>

    <!-- Holdings and Performance -->
    <div class="grid lg:grid-cols-2 gap-8">
      <!-- Current Holdings -->
      <div class="card">
        <h2 class="text-xl font-semibold mb-6">Current Holdings</h2>
        <div class="space-y-4">
          <div
            v-for="holding in holdings"
            :key="holding.symbol"
            class="flex items-center justify-between p-4 border rounded-lg hover:bg-gray-50"
          >
            <div class="flex items-center space-x-4">
              <div class="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center">
                <span class="text-blue-600 font-semibold">{{ holding.symbol.charAt(0) }}</span>
              </div>
              <div>
                <h3 class="font-semibold">{{ holding.name }}</h3>
                <p class="text-sm text-gray-600">{{ holding.symbol }}</p>
              </div>
            </div>
            <div class="text-right">
              <div class="font-semibold">{{ (holding.amount * holding.currentPrice).toFixed(2) }} BUSD</div>
              <div class="text-sm text-gray-600">{{ holding.amount.toFixed(4) }} tokens</div>
              <div class="text-sm text-gray-500">@ {{ holding.currentPrice.toFixed(4) }} BUSD</div>
            </div>
          </div>
          <div v-if="holdings.length === 0" class="text-center py-8 text-gray-500">
            <svg class="w-12 h-12 mx-auto mb-4 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4"></path>
            </svg>
            <p>No token holdings yet</p>
            <p class="text-sm">Start trading to build your portfolio</p>
          </div>
        </div>
      </div>

      <!-- Performance Chart Placeholder -->
      <div class="card">
        <h2 class="text-xl font-semibold mb-6">Portfolio Performance</h2>
        <div class="h-64 bg-gray-100 rounded-lg flex items-center justify-center">
          <div class="text-center text-gray-500">
            <svg class="w-12 h-12 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path>
            </svg>
            <p>Performance chart will be displayed here</p>
            <p class="text-sm">Connect to view historical data</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Transaction History -->
    <div class="card">
      <div class="flex justify-between items-center mb-6">
        <h2 class="text-xl font-semibold">Transaction History</h2>
        <div class="flex space-x-2">
          <select v-model="filterType" class="px-3 py-1 border rounded-md text-sm">
            <option value="all">All Types</option>
            <option value="buy">Buy Orders</option>
            <option value="sell">Sell Orders</option>
          </select>
          <select v-model="filterSymbol" class="px-3 py-1 border rounded-md text-sm">
            <option value="all">All Symbols</option>
            <option v-for="symbol in uniqueSymbols" :key="symbol" :value="symbol">{{ symbol }}</option>
          </select>
        </div>
      </div>

      <div class="overflow-x-auto">
        <table class="w-full">
          <thead>
            <tr class="border-b">
              <th class="text-left py-3 px-4">Date & Time</th>
              <th class="text-left py-3 px-4">Type</th>
              <th class="text-left py-3 px-4">Symbol</th>
              <th class="text-right py-3 px-4">Quantity</th>
              <th class="text-right py-3 px-4">Price</th>
              <th class="text-right py-3 px-4">Total</th>
              <th class="text-right py-3 px-4">Status</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="transaction in filteredTransactions"
              :key="transaction.id"
              class="border-b hover:bg-gray-50"
            >
              <td class="py-3 px-4">
                <div class="text-sm">{{ formatDateTime(transaction.timestamp) }}</div>
              </td>
              <td class="py-3 px-4">
                <span
                  :class="transaction.type === 'buy' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'"
                  class="px-2 py-1 rounded-full text-xs font-medium uppercase"
                >
                  {{ transaction.type }}
                </span>
              </td>
              <td class="py-3 px-4 font-medium">{{ transaction.symbol }}</td>
              <td class="py-3 px-4 text-right">{{ transaction.quantity.toFixed(4) }}</td>
              <td class="py-3 px-4 text-right">{{ transaction.price.toFixed(4) }} BUSD</td>
              <td class="py-3 px-4 text-right font-semibold">{{ transaction.total.toFixed(2) }} BUSD</td>
              <td class="py-3 px-4 text-right">
                <span
                  :class="getStatusColor(transaction.status)"
                  class="px-2 py-1 rounded-full text-xs font-medium"
                >
                  {{ transaction.status }}
                </span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <div v-if="filteredTransactions.length === 0" class="text-center py-8 text-gray-500">
        No transactions found matching your filters.
      </div>
    </div>

    <!-- Market Overview -->
    <div class="card">
      <h2 class="text-xl font-semibold mb-6">Market Overview</h2>
      <div class="grid md:grid-cols-3 gap-6">
        <div
          v-for="market in marketData"
          :key="market.symbol"
          class="p-4 border rounded-lg"
        >
          <div class="flex justify-between items-start mb-2">
            <div>
              <h3 class="font-semibold">{{ market.name }}</h3>
              <p class="text-sm text-gray-600">{{ market.symbol }}</p>
            </div>
            <div class="text-right">
              <div class="font-semibold">{{ market.price.toFixed(4) }} BUSD</div>
            </div>
          </div>
          <div class="text-sm text-gray-600 space-y-1">
            <div class="flex justify-between">
              <span>Liquidity:</span>
              <span>{{ (market.liquidity / 1000).toFixed(0) }}K BUSD</span>
            </div>
          </div>
        </div>
      </div>
      <div v-if="marketData.length === 0" class="col-span-3 text-center py-8 text-gray-500">
        <p>No markets available</p>
      </div>
    </div>
    </template>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import blockchain from '../utils/blockchain.js'

export default {
  name: 'Dashboard',
  setup() {
    const isLoading = ref(true)
    const filterType = ref('all')
    const filterSymbol = ref('all')

    const holdings = ref([])
    const transactions = ref([])
    const marketData = ref([])
    const cashBalance = ref(0)
    const totalTrades = ref(0)

    const totalValue = computed(() => {
      let total = cashBalance.value
      holdings.value.forEach(holding => {
        total += holding.amount * holding.currentPrice
      })
      return total
    })

    const uniqueSymbols = computed(() => {
      return [...new Set(transactions.value.map(t => t.symbol))]
    })

    const filteredTransactions = computed(() => {
      return transactions.value.filter(transaction => {
        const typeMatch = filterType.value === 'all' || transaction.type === filterType.value
        const symbolMatch = filterSymbol.value === 'all' || transaction.symbol === filterSymbol.value
        return typeMatch && symbolMatch
      })
    })

    const formatDateTime = (date) => {
      return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      })
    }

    const getStatusColor = (status) => {
      switch (status) {
        case 'completed':
          return 'bg-green-100 text-green-800'
        case 'pending':
          return 'bg-yellow-100 text-yellow-800'
        case 'failed':
          return 'bg-red-100 text-red-800'
        default:
          return 'bg-gray-100 text-gray-800'
      }
    }

    const loadDashboardData = async () => {
      isLoading.value = true

      try {
        if (!blockchain.signer) {
          console.log('⚠️ Wallet not connected')
          isLoading.value = false
          return
        }

        const address = await blockchain.signer.getAddress()
        console.log('📊 Loading dashboard data for:', address)

        // Load BUSD balance
        const busd = await blockchain.getBaseTokenBalance(address)
        cashBalance.value = parseFloat(busd)

        // Load all companies to get market data and holdings
        const allCompanies = await blockchain.getAllCompanies()
        const holdingsData = []
        const marketsData = []
        const allTransactions = []
        let tradeCount = 0

        for (const company of allCompanies) {
          // Only process companies with AMM pools
          if (company.ammPool && company.ammPool !== '0x0000000000000000000000000000000000000000') {
            try {
              const price = await blockchain.getAMMPrice(company.ammPool)
              const reserves = await blockchain.getAMMReserves(company.ammPool)

              // Add to market data
              marketsData.push({
                symbol: company.symbol,
                name: company.name,
                price: parseFloat(price),
                change: 0, // Would need historical data
                liquidity: parseFloat(reserves.base)
              })

              // Check if user has holdings
              if (company.stockToken && company.stockToken !== '0x0000000000000000000000000000000000000000') {
                const balance = await blockchain.getTokenBalance(company.stockToken, address)
                const balanceNum = parseFloat(balance)

                if (balanceNum > 0) {
                  holdingsData.push({
                    symbol: company.symbol,
                    name: company.name,
                    amount: balanceNum,
                    currentPrice: parseFloat(price)
                  })
                }
              }

              // Load trades for this AMM
              const trades = await blockchain.getRecentTrades(company.ammPool, address, 20)
              tradeCount += trades.length

              for (const trade of trades) {
                allTransactions.push({
                  id: trade.txHash,
                  timestamp: trade.timestamp,
                  type: trade.type,
                  symbol: company.symbol,
                  quantity: parseFloat(trade.type === 'buy' ? trade.amountOut : trade.amountIn),
                  price: parseFloat(trade.type === 'buy' ? trade.amountIn : trade.amountOut) / parseFloat(trade.type === 'buy' ? trade.amountOut : trade.amountIn),
                  total: parseFloat(trade.type === 'buy' ? trade.amountIn : trade.amountOut),
                  status: 'completed',
                  txHash: trade.txHash
                })
              }
            } catch (err) {
              console.warn(`Could not load data for ${company.symbol}:`, err)
            }
          }
        }

        // Sort transactions by timestamp (newest first)
        allTransactions.sort((a, b) => b.timestamp - a.timestamp)

        holdings.value = holdingsData
        marketData.value = marketsData
        transactions.value = allTransactions
        totalTrades.value = tradeCount

        console.log('📊 Dashboard loaded:', {
          holdings: holdingsData.length,
          markets: marketsData.length,
          transactions: allTransactions.length,
          cashBalance: cashBalance.value
        })

      } catch (error) {
        console.error('Error loading dashboard data:', error)
      } finally {
        isLoading.value = false
      }
    }

    onMounted(async () => {
      // Ensure blockchain is initialized
      if (!blockchain.provider) {
        await blockchain.initialize()
      }
      await loadDashboardData()
    })

    return {
      isLoading,
      holdings,
      transactions,
      marketData,
      cashBalance,
      totalTrades,
      totalValue,
      filterType,
      filterSymbol,
      uniqueSymbols,
      filteredTransactions,
      formatDateTime,
      getStatusColor
    }
  }
}
</script>
