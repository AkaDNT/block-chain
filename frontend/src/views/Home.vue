<template>
  <div class="space-y-12">
    <!-- Hero Section -->
    <div class="relative overflow-hidden">
      <!-- Gradient Background -->
      <div class="absolute inset-0 bg-gradient-to-br from-blue-600 via-purple-600 to-indigo-700 opacity-5 rounded-xl"></div>

      <div class="relative text-center py-20 px-4">
        <div class="inline-block mb-4 px-4 py-2 bg-gradient-to-r from-blue-600 to-purple-600 rounded-full">
          <span class="text-white text-sm font-semibold">🚀 Powered by Blockchain Technology</span>
        </div>

        <h1 class="text-6xl font-black text-transparent bg-clip-text bg-gradient-to-r from-blue-600 via-purple-600 to-indigo-700 mb-6">
          Blockchain Stock Trading Platform
        </h1>

        <p class="text-xl text-gray-700 mb-10 max-w-3xl mx-auto leading-relaxed">
          Trade tokenized company shares through an automated market maker.
          Companies can IPO by issuing tokens, and investors can trade them with <span class="font-semibold text-purple-600">transparent pricing</span>.
        </p>

        <div class="flex gap-4 justify-center">
          <router-link v-if="!hasCompany" to="/register" class="group relative px-8 py-4 bg-gradient-to-r from-blue-600 to-purple-600 text-white font-bold rounded-xl shadow-xl hover:shadow-2xl transform hover:scale-105 transition-all duration-200">
            <span class="relative z-10">Register Your Company</span>
            <div class="absolute inset-0 bg-white opacity-0 group-hover:opacity-20 rounded-xl transition-opacity"></div>
          </router-link>
          <router-link to="/trade" class="px-8 py-4 bg-white text-purple-600 font-bold rounded-xl shadow-lg hover:shadow-xl border-2 border-purple-600 hover:bg-purple-50 transform hover:scale-105 transition-all duration-200">
            Start Trading
          </router-link>
        </div>
      </div>
    </div>

    <!-- Features Section -->
    <div class="grid md:grid-cols-3 gap-8 px-4">
      <div class="group relative bg-white rounded-2xl p-8 shadow-lg hover:shadow-2xl transition-all duration-300 border border-gray-100 hover:border-blue-200">
        <div class="absolute top-0 right-0 w-32 h-32 bg-gradient-to-br from-blue-400 to-blue-600 rounded-bl-full opacity-10"></div>
        <div class="relative">
          <div class="w-16 h-16 bg-gradient-to-br from-blue-500 to-blue-600 rounded-2xl flex items-center justify-center mx-auto mb-6 shadow-lg group-hover:scale-110 transition-transform">
            <svg class="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"></path>
            </svg>
          </div>
          <h3 class="text-xl font-bold mb-3 text-gray-900">Company Registration</h3>
          <p class="text-gray-600 leading-relaxed">
            Register your company on-chain with IPFS document storage for transparency and verification.
          </p>
        </div>
      </div>

      <div class="group relative bg-white rounded-2xl p-8 shadow-lg hover:shadow-2xl transition-all duration-300 border border-gray-100 hover:border-green-200">
        <div class="absolute top-0 right-0 w-32 h-32 bg-gradient-to-br from-green-400 to-green-600 rounded-bl-full opacity-10"></div>
        <div class="relative">
          <div class="w-16 h-16 bg-gradient-to-br from-green-500 to-green-600 rounded-2xl flex items-center justify-center mx-auto mb-6 shadow-lg group-hover:scale-110 transition-transform">
            <svg class="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6"></path>
            </svg>
          </div>
          <h3 class="text-xl font-bold mb-3 text-gray-900">AMM Trading</h3>
          <p class="text-gray-600 leading-relaxed">
            Trade tokens through our automated market maker with transparent pricing and low fees.
          </p>
        </div>
      </div>

      <div class="group relative bg-white rounded-2xl p-8 shadow-lg hover:shadow-2xl transition-all duration-300 border border-gray-100 hover:border-purple-200">
        <div class="absolute top-0 right-0 w-32 h-32 bg-gradient-to-br from-purple-400 to-purple-600 rounded-bl-full opacity-10"></div>
        <div class="relative">
          <div class="w-16 h-16 bg-gradient-to-br from-purple-500 to-purple-600 rounded-2xl flex items-center justify-center mx-auto mb-6 shadow-lg group-hover:scale-110 transition-transform">
            <svg class="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"></path>
            </svg>
          </div>
          <h3 class="text-xl font-bold mb-3 text-gray-900">Secure & Verified</h3>
          <p class="text-gray-600 leading-relaxed">
            All companies go through verification process with documents stored securely on IPFS.
          </p>
        </div>
      </div>
    </div>

    <!-- Stats Section -->
    <div class="relative bg-gradient-to-br from-blue-600 via-purple-600 to-indigo-700 rounded-3xl p-12 shadow-2xl mx-4">
      <div class="absolute inset-0 bg-black opacity-10 rounded-3xl"></div>
      <div class="relative">
        <h2 class="text-3xl font-black text-white text-center mb-12">Platform Statistics</h2>
        <div class="grid md:grid-cols-4 gap-8 text-center">
          <div class="bg-white bg-opacity-10 backdrop-blur-md rounded-2xl p-6 border border-white border-opacity-20 hover:bg-opacity-20 transition-all">
            <div class="text-5xl font-black text-white mb-3">{{ stats.totalCompanies }}</div>
            <div class="text-blue-100 font-semibold">Registered Companies</div>
          </div>
          <div class="bg-white bg-opacity-10 backdrop-blur-md rounded-2xl p-6 border border-white border-opacity-20 hover:bg-opacity-20 transition-all">
            <div class="text-5xl font-black text-white mb-3">{{ stats.totalVolume }}</div>
            <div class="text-blue-100 font-semibold">Trading Volume (BUSD)</div>
          </div>
          <div class="bg-white bg-opacity-10 backdrop-blur-md rounded-2xl p-6 border border-white border-opacity-20 hover:bg-opacity-20 transition-all">
            <div class="text-5xl font-black text-white mb-3">{{ stats.totalLiquidity }}</div>
            <div class="text-blue-100 font-semibold">Total Liquidity (BUSD)</div>
          </div>
          <div class="bg-white bg-opacity-10 backdrop-blur-md rounded-2xl p-6 border border-white border-opacity-20 hover:bg-opacity-20 transition-all">
            <div class="text-5xl font-black text-white mb-3">{{ stats.verifiedCompanies }}</div>
            <div class="text-blue-100 font-semibold">Verified Companies</div>
          </div>
        </div>
      </div>
    </div>

    <!-- Recent Companies -->
    <div class="card">
      <h2 class="text-2xl font-bold mb-6">Recently Registered Companies</h2>
      <div class="space-y-4">
        <div
          v-for="company in recentCompanies"
          :key="company.id"
          class="flex items-center justify-between p-4 border rounded-lg hover:bg-gray-50"
        >
          <div class="flex items-center space-x-4">
            <div class="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center">
              <span class="text-blue-600 font-semibold">{{ company.symbol.charAt(0) }}</span>
            </div>
            <div>
              <h3 class="font-semibold">{{ company.name }}</h3>
              <p class="text-sm text-gray-600">{{ company.symbol }}</p>
            </div>
          </div>
          <div class="text-right">
            <div class="flex items-center space-x-2">
              <span
                :class="company.verified ? 'text-green-600' : 'text-yellow-600'"
                class="text-sm font-medium"
              >
                {{ company.verified ? 'Verified' : 'Pending' }}
              </span>
              <div
                :class="company.verified ? 'bg-green-100' : 'bg-yellow-100'"
                class="w-2 h-2 rounded-full"
              ></div>
            </div>
            <p class="text-sm text-gray-500">{{ formatDate(company.createdAt) }}</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import blockchain from '../utils/blockchain.js'

export default {
  name: 'Home',
  setup() {
    const stats = ref({
      totalCompanies: 0,
      totalVolume: '0',
      totalLiquidity: '0',
      verifiedCompanies: 0
    })

    const recentCompanies = ref([])
    const loading = ref(true)
    const hasCompany = ref(false)

    const formatDate = (date) => {
      return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
      })
    }

    const checkUserCompany = async () => {
      try {
        if (blockchain.signer) {
          const address = await blockchain.signer.getAddress()
          const company = await blockchain.getCompanyByOwner(address)
          hasCompany.value = !!company
        }
      } catch (error) {
        // User doesn't have a company - this is expected
        hasCompany.value = false
      }
    }

    const loadStats = async () => {
      try {
        loading.value = true

        // Check if user has a company
        await checkUserCompany()

        // Load all companies from blockchain
        const companies = await blockchain.getAllCompanies()

        // Update stats
        stats.value.totalCompanies = companies.length
        stats.value.verifiedCompanies = companies.filter(c => c.isVerified).length

        // Calculate total liquidity from AMM pools
        let totalLiquidity = 0
        for (const company of companies) {
          if (company.ammPool && company.ammPool !== '0x0000000000000000000000000000000000000000') {
            try {
              const reserves = await blockchain.getAMMReserves(company.ammPool)
              totalLiquidity += parseFloat(reserves.base)
            } catch (err) {
              console.warn(`Could not get reserves for ${company.symbol}:`, err)
            }
          }
        }

        stats.value.totalLiquidity = totalLiquidity > 0 ? `${(totalLiquidity / 1000000).toFixed(1)}M` : '0'
        stats.value.totalVolume = '0' // Volume tracking would need events/indexing

        // Map companies for display
        recentCompanies.value = companies.map(c => ({
          id: c.id,
          name: c.name,
          symbol: c.symbol,
          verified: c.isVerified,
          createdAt: c.createdAt
        })).sort((a, b) => b.createdAt - a.createdAt).slice(0, 5)

      } catch (error) {
        console.error('Error loading stats:', error)
        // Fallback to mock data if blockchain not available
        stats.value = {
          totalCompanies: 0,
          totalVolume: '0',
          totalLiquidity: '0',
          verifiedCompanies: 0
        }
      } finally {
        loading.value = false
      }
    }

    onMounted(() => {
      loadStats()
    })

    return {
      stats,
      recentCompanies,
      formatDate,
      loading,
      hasCompany
    }
  }
}
</script>
