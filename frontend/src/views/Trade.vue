<template>
  <div class="max-w-7xl mx-auto px-4 min-h-[calc(100vh-8rem)]">
    <!-- Show Revoked Notice -->
    <div v-if="!checkingTrader && traderKycStatus === 'REVOKED'" class="max-w-2xl mx-auto">
      <div class="bg-red-50 border border-red-200 rounded-lg p-8 text-center">
        <svg class="w-16 h-16 mx-auto text-red-500 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M18.364 18.364A9 9 0 005.636 5.636m12.728 12.728A9 9 0 015.636 5.636m12.728 12.728L5.636 5.636"></path>
        </svg>
        <h2 class="text-2xl font-bold text-red-900 mb-2">Trading Access Revoked</h2>
        <p class="text-red-700 mb-4">
          Your trading privileges have been revoked by an administrator.
        </p>
        <p class="text-sm text-red-600">
          If you believe this is an error, please contact support for assistance.
        </p>
      </div>
    </div>

    <!-- Show Trader KYC Notice if not verified -->
    <div v-else-if="!isVerifiedTrader && !checkingTrader" class="max-w-4xl mx-auto">
      <TraderKYC @kyc-submitted="refreshTraderStatus" />
    </div>

    <!-- Loading State -->
    <div v-else-if="checkingTrader" class="flex items-center justify-center h-full">
      <div class="text-center">
        <svg class="animate-spin h-12 w-12 mx-auto text-blue-600 mb-4" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
        <p class="text-gray-600">Checking trader status...</p>
      </div>
    </div>

    <!-- 3 Column Layout (only shown if user is verified trader) -->
    <div v-else-if="isVerifiedTrader" class="grid grid-cols-12 gap-3 h-full">
      <!-- Column 1: Stock List + Portfolio -->
      <div class="col-span-3 flex flex-col gap-2">
        <!-- Portfolio Section -->
        <div class="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
          <div class="px-3 py-1.5 border-b border-gray-200 bg-gradient-to-r from-blue-50 to-indigo-50">
            <div class="flex items-center justify-between">
              <h2 class="text-xs font-bold text-gray-900 flex items-center gap-1">
                <svg class="w-3.5 h-3.5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 13.255A23.931 23.931 0 0112 15c-3.183 0-6.22-.62-9-1.745M16 6V4a2 2 0 00-2-2h-4a2 2 0 00-2 2v2m4 6h.01M5 20h14a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"></path>
                </svg>
                My Portfolio
              </h2>
              <div class="flex items-center gap-1 bg-yellow-100 px-2 py-0.5 rounded-full">
                <span class="text-xs font-bold text-yellow-700">{{ parseFloat(busdBalance).toFixed(2) }}</span>
                <span class="text-xs text-yellow-600">BUSD</span>
              </div>
            </div>
          </div>
          <div class="max-h-32 overflow-y-auto">
            <div v-if="Object.keys(portfolio).length === 0" class="p-3 text-center">
              <p class="text-xs text-gray-500">No stock holdings yet</p>
            </div>
            <div v-else class="divide-y divide-gray-100">
              <div v-for="(holding, symbol) in portfolio" :key="symbol" class="p-2 hover:bg-gray-50">
                <div class="flex items-center justify-between">
                  <div class="flex items-center gap-2">
                    <div class="w-6 h-6 bg-gradient-to-br from-green-500 to-emerald-600 rounded flex items-center justify-center">
                      <span class="text-white font-bold text-xs">{{ symbol.charAt(0) }}</span>
                    </div>
                    <span class="text-xs font-semibold text-gray-900">{{ symbol }}</span>
                  </div>
                  <div class="text-right">
                    <div class="text-xs font-bold text-gray-900">{{ parseFloat(holding.balance).toFixed(4) }}</div>
                    <div class="text-xs text-gray-500">{{ (parseFloat(holding.balance) * holding.price).toFixed(2) }} BUSD</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Markets List -->
        <div class="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden flex-1 flex flex-col">
          <div class="px-3 py-1.5 border-b border-gray-200 bg-gray-50">
            <h2 class="text-xs font-bold text-gray-900">Markets</h2>
            <p class="text-xs text-gray-500">{{ companies.length }} tokens available</p>
          </div>
          <div class="flex-1 overflow-y-auto">
          <div class="divide-y divide-gray-100">
            <div
              v-for="company in companies"
              :key="company.id"
              @click="selectCompany(company)"
              :class="selectedCompany?.id === company.id ? 'bg-blue-50 border-l-3 border-blue-600' : 'hover:bg-gray-50 border-l-3 border-transparent'"
              class="p-2 cursor-pointer transition-all duration-150"
            >
              <div class="flex items-center justify-between">
                <div class="flex items-center gap-2">
                  <div class="w-8 h-8 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-lg flex items-center justify-center flex-shrink-0">
                    <span class="text-white font-bold text-xs">{{ company.symbol.charAt(0) }}</span>
                  </div>
                  <div class="min-w-0">
                    <h3 class="font-bold text-gray-900 text-xs">{{ company.symbol }}</h3>
                    <p class="text-xs text-gray-500 truncate">{{ company.name }}</p>
                  </div>
                </div>
                <div class="text-right flex-shrink-0 ml-2">
                  <div class="font-bold text-gray-900 text-xs">{{ company.price.toFixed(4) }}</div>
                  <div :class="company.change >= 0 ? 'text-green-600' : 'text-red-600'" class="text-xs font-semibold">
                    {{ company.change >= 0 ? '▲' : '▼' }} {{ company.change >= 0 ? '+' : '' }}{{ company.change.toFixed(2) }}%
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
        </div>
      </div>

      <!-- Column 2: Chart -->
      <div class="col-span-6 flex flex-col gap-2">
        <!-- Price Header with Flip Card -->
        <div v-if="selectedCompany" class="relative" style="perspective: 1000px;">
          <div
            class="transition-transform duration-500 relative"
            :style="{ transformStyle: 'preserve-3d', transform: showCompanyDetails ? 'rotateY(180deg)' : 'rotateY(0deg)' }"
          >
            <!-- Front Side - Stock Overview -->
            <div
              class="bg-white rounded-lg shadow-sm border border-gray-200 p-3"
              :style="{ backfaceVisibility: 'hidden' }"
            >
              <div class="flex items-center justify-between">
                <div class="flex items-center gap-3">
                  <div class="w-12 h-12 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-xl flex items-center justify-center">
                    <span class="text-white font-bold text-lg">{{ selectedCompany.symbol.charAt(0) }}</span>
                  </div>
                  <div>
                    <h1 class="text-xl font-bold text-gray-900">{{ selectedCompany.symbol }}</h1>
                    <p class="text-xs text-gray-500">{{ selectedCompany.name }}</p>
                  </div>
                </div>
                <div class="flex items-center gap-3">
                  <div class="text-right">
                    <div class="text-2xl font-bold text-gray-900">{{ selectedCompany.price.toFixed(4) }} <span class="text-base text-gray-500">BUSD</span></div>
                    <div class="flex items-center justify-end gap-1 mt-0.5">
                      <div :class="selectedCompany.change >= 0 ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'" class="px-2 py-0.5 rounded-full flex items-center gap-0.5 text-xs font-semibold">
                        <span v-if="selectedCompany.change >= 0">▲</span>
                        <span v-else>▼</span>
                        <span>{{ selectedCompany.change >= 0 ? '+' : '' }}{{ selectedCompany.change.toFixed(2) }}%</span>
                      </div>
                    </div>
                  </div>
                  <button
                    @click="showCompanyDetails = true"
                    class="p-2 rounded-lg bg-gray-100 hover:bg-gray-200 transition-colors text-gray-600 hover:text-gray-800"
                    title="View Company Details"
                  >
                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                    </svg>
                  </button>
                </div>
              </div>

              <!-- Stats Grid -->
              <div class="grid grid-cols-4 gap-3 mt-3 pt-3 border-t border-gray-200">
                <div class="text-center">
                  <div class="text-xs text-gray-500 mb-0.5">Current Price</div>
                  <div class="text-sm font-bold text-gray-900">{{ selectedCompany.price.toFixed(4) }}</div>
                  <div :class="selectedCompany.change >= 0 ? 'text-green-600' : 'text-red-600'" class="text-xs font-semibold">
                    {{ selectedCompany.change >= 0 ? '▲' : '▼' }} 0.89%
                  </div>
                </div>
                <div class="text-center">
                  <div class="text-xs text-gray-500 mb-0.5">24h High</div>
                  <div class="text-sm font-bold text-green-600">{{ (selectedCompany.price * 1.015).toFixed(4) }}</div>
                </div>
                <div class="text-center">
                  <div class="text-xs text-gray-500 mb-0.5">24h Low</div>
                  <div class="text-sm font-bold text-red-600">{{ (selectedCompany.price * 0.985).toFixed(4) }}</div>
                </div>
                <div class="text-center">
                  <div class="text-xs text-gray-500 mb-0.5">Liquidity</div>
                  <div class="text-sm font-bold text-blue-600">{{ (selectedCompany.liquidity / 1000).toFixed(0) }}K BUSD</div>
                </div>
              </div>
            </div>

            <!-- Back Side - Company Details -->
            <div
              class="bg-white rounded-lg shadow-sm border border-gray-200 p-3 absolute inset-0 flex-1"
              :style="{ backfaceVisibility: 'hidden', transform: 'rotateY(180deg)' }"
            >
              <div class="flex items-center justify-between">
                <div class="flex items-center gap-3 flex-1">
                  <div class="w-12 h-12 bg-gradient-to-br from-purple-500 to-indigo-600 rounded-xl flex items-center justify-center">
                    <img v-if="selectedCompany.ipfsLogo" :src="getCompanyLogo(selectedCompany.ipfsLogo)" alt="Company Logo" class="text-white">
                    <svg v-else class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"></path>
                    </svg>
                  </div>
                  <div>
                    <h1 class="text-xl font-bold text-gray-900">{{ selectedCompany.name }}</h1>
                    <p class="text-xs text-gray-500">Company Details</p>
                  </div>
                  <!-- Company Info Grid -->
                  <div class="grid grid-cols-2 gap-3 flex-1 ml-10">
                    <div>
                      <div class="text-xs text-gray-500 mb-1">Symbol</div>
                      <div class="text-sm font-bold text-gray-900">{{ selectedCompany.symbol }}</div>
                    </div>
                    <div>
                      <div class="text-xs text-gray-500 mb-1">IPO Date</div>
                      <div class="text-sm font-bold text-gray-900">{{ formatIPODate(selectedCompany.createdAt) }}</div>
                    </div>
                  </div>
                </div>
                <button
                  @click="showCompanyDetails = false"
                  class="p-2 rounded-lg bg-gray-100 hover:bg-gray-200 transition-colors text-gray-600 hover:text-gray-800"
                  title="Back to Stock Overview"
                >
                  <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18"></path>
                  </svg>
                </button>
              </div>

              <!-- Company Documents Section (Bottom Right) -->
              <div class="bottom-3 max-w-xs mt-6">
                <div class="text-xs text-gray-500 mb-2 text-left">Company Documents</div>

                <div v-if="loadingEncryptedDocs" class="flex items-center justify-end gap-2 text-xs text-gray-400">
                  <svg class="animate-spin w-4 h-4" fill="none" viewBox="0 0 24 24">
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  Loading...
                </div>

                <div v-else-if="encryptedDocuments.length === 0" class="text-xs text-gray-400 italic text-right">
                  No documents available
                </div>

                <div v-else class="flex flex-wrap gap-2 justify-start">
                  <button
                    v-for="doc in encryptedDocuments"
                    :key="doc.id"
                    @click="downloadEncryptedDocument(doc)"
                    :disabled="downloadingDocId === doc.id"
                    :class="getDocTypeButtonClass(doc.docType)"
                    class="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-colors disabled:opacity-50"
                  >
                    <svg v-if="downloadingDocId === doc.id" class="animate-spin w-4 h-4" fill="none" viewBox="0 0 24 24">
                      <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                      <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    <svg v-else class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
                    </svg>
                    {{ downloadingDocId === doc.id ? 'Decrypting...' : formatDocType(doc.docType) }}
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Chart -->
        <div v-if="selectedCompany" class="flex-1 min-h-0">
          <TokenPriceChart
            :token-symbol="selectedCompany.symbol"
            :initial-price="selectedCompany.price"
            :amm-pool="selectedCompany.ammPool"
          />
        </div>
        <div v-else class="h-full bg-white rounded-lg shadow-sm border border-gray-200 flex items-center justify-center">
          <div class="text-center">
            <div class="w-16 h-16 bg-gray-100 rounded-xl flex items-center justify-center mx-auto mb-3">
              <svg class="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 12l3-3 3 3 4-4M8 21l4-4 4 4M3 4h18M4 4h16v12a1 1 0 01-1 1H5a1 1 0 01-1-1V4z"></path>
              </svg>
            </div>
            <p class="text-gray-900 font-semibold text-base mb-1">Select a Token</p>
            <p class="text-gray-500 text-sm">Choose a token from the list to start trading</p>
          </div>
        </div>
      </div>

      <!-- Column 3: Trading Panel -->
      <div class="col-span-3 flex flex-col space-y-2">
        <!-- Trading Form -->
        <div v-if="selectedCompany" class="bg-white rounded-lg shadow-sm border border-gray-200 p-3 flex-shrink-0">
          <div class="flex space-x-1.5 mb-3 bg-gray-100 p-1 rounded-lg">
            <button
              @click="tradeType = 'buy'"
              :class="tradeType === 'buy' ? 'bg-green-600 text-white' : 'bg-transparent text-gray-600 hover:bg-white'"
              class="flex-1 py-1.5 px-3 rounded-md font-semibold transition-all duration-150 text-sm"
            >
              <span class="flex items-center justify-center gap-1">
                <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 3h2l.4 2M7 13h10l4-8H5.4M7 13L5.4 5M7 13l-2.293 2.293c-.63.63-.184 1.707.707 1.707H17m0 0a2 2 0 100 4 2 2 0 000-4zm-8 2a2 2 0 11-4 0 2 2 0 014 0z"></path>
                </svg>
                Buy
              </span>
            </button>
            <button
              @click="tradeType = 'sell'"
              :class="tradeType === 'sell' ? 'bg-red-600 text-white' : 'bg-transparent text-gray-600 hover:bg-white'"
              class="flex-1 py-1.5 px-3 rounded-md font-semibold transition-all duration-150 text-sm"
            >
              <span class="flex items-center justify-center gap-1">
                <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                </svg>
                Sell
              </span>
            </button>
          </div>

          <form @submit.prevent="executeTrade" class="space-y-2.5">
            <div>
              <label class="block text-xs font-medium text-gray-600 mb-1">
                {{ tradeType === 'buy' ? 'Amount to Spend' : 'Amount to Sell' }}
              </label>
              <div class="relative">
                <input
                  v-model="tradeForm.amount"
                  type="number"
                  class="w-full px-3 py-2 text-lg font-bold border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
                  :placeholder="0.00"
                  step="0.01"
                  min="0"
                  required
                />
                <div class="absolute right-3 top-1/2 -translate-y-1/2 bg-gray-100 px-2 py-1 rounded">
                  <span class="font-bold text-gray-700 text-xs">{{ tradeType === 'buy' ? 'BUSD' : selectedCompany.symbol }}</span>
                </div>
              </div>
            </div>

            <div v-if="tradeForm.amount && expectedOutput" class="p-2.5 bg-gradient-to-br from-blue-50 to-indigo-50 rounded-lg border border-blue-200">
              <!-- Main Output Display -->
              <div class="mb-1.5 pb-1.5 border-b border-blue-200">
                <div class="text-xs font-medium text-gray-600 mb-0.5">You will receive</div>
                <div class="text-lg font-bold text-gray-900">
                  {{ expectedOutput.toFixed(4) }}
                  <span class="text-xs text-blue-600 ml-1">{{ tradeType === 'buy' ? selectedCompany.symbol : 'BUSD' }}</span>
                </div>
              </div>

              <!-- Details Grid -->
              <div class="space-y-1.5">
                <div class="flex justify-between items-center text-xs">
                  <span class="text-gray-600">Price per token</span>
                  <span class="font-semibold text-gray-900">{{ effectivePrice.toFixed(4) }} BUSD</span>
                </div>
                <div class="flex justify-between items-center text-xs">
                  <span class="text-gray-600">Trading fee (0.3%)</span>
                  <span class="font-semibold text-gray-900">{{ tradingFee.toFixed(4) }} BUSD</span>
                </div>
                <div class="flex justify-between items-center text-xs">
                  <span class="text-gray-600">Price impact</span>
                  <span :class="priceImpact > 5 ? 'bg-red-100 text-red-700' : priceImpact > 1 ? 'bg-yellow-100 text-yellow-700' : 'bg-green-100 text-green-700'" class="font-semibold px-1.5 py-0.5 rounded text-xs">
                    {{ priceImpact.toFixed(2) }}%
                  </span>
                </div>
              </div>

              <!-- Slippage Info Section -->
              <div class="mt-2 pt-2 border-t border-blue-200 space-y-1.5">
                <div class="flex justify-between items-center text-xs">
                  <span class="text-gray-600 flex items-center gap-1">
                    <svg class="w-3 h-3 text-amber-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path>
                    </svg>
                    Minimum received
                  </span>
                  <span class="font-semibold text-amber-700">
                    {{ minimumReceived.toFixed(4) }} {{ tradeType === 'buy' ? selectedCompany.symbol : 'BUSD' }}
                  </span>
                </div>
                <div class="flex justify-between items-center text-xs">
                  <span class="text-gray-600">Max price after slippage</span>
                  <span class="font-semibold text-gray-900">{{ maxPriceAfterSlippage.toFixed(4) }} BUSD</span>
                </div>
              </div>
            </div>

            <div>
              <label class="block text-xs font-medium text-gray-600 mb-1 flex items-center gap-1">
                <svg class="w-3.5 h-3.5 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                </svg>
                Slippage Tolerance
              </label>
              <select v-model="tradeForm.slippage" class="w-full px-3 py-1.5 border border-gray-300 rounded-lg font-medium text-sm text-gray-900 bg-white cursor-pointer focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all">
                <option value="0.5">0.5% - Low</option>
                <option value="1">1% - Recommended ⭐</option>
                <option value="3">3% - High</option>
                <option value="5">5% - Very High</option>
              </select>
            </div>

            <button
              type="submit"
              :disabled="!canTrade || isTrading"
              :class="tradeType === 'buy' ? 'bg-green-600 hover:bg-green-700' : 'bg-red-600 hover:bg-red-700'"
              class="w-full text-white font-bold py-2.5 px-4 rounded-lg transition-all duration-150 disabled:opacity-50 disabled:cursor-not-allowed shadow hover:shadow-md"
            >
              <span v-if="isTrading" class="flex items-center justify-center text-sm">
                <svg class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Processing...
              </span>
              <span v-else class="flex items-center justify-center gap-2 text-sm">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path>
                </svg>
                {{ tradeType === 'buy' ? 'Buy' : 'Sell' }} {{ selectedCompany.symbol }}
              </span>
            </button>
          </form>
        </div>
        <div v-else class="bg-white rounded-lg shadow-sm border border-gray-200 p-4 text-center">
          <div class="w-10 h-10 bg-gray-100 rounded-lg flex items-center justify-center mx-auto mb-2">
            <svg class="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path>
            </svg>
          </div>
          <p class="text-gray-900 font-semibold text-xs mb-0.5">Ready to Trade?</p>
          <p class="text-gray-500 text-xs">Select a token</p>
        </div>

        <!-- Recent Trades -->
        <div class="bg-white rounded-lg shadow-sm border border-gray-200 flex-1 overflow-hidden flex flex-col">
          <div class="px-3 py-2 border-b border-gray-200 bg-gray-50">
            <div class="flex items-center justify-between">
              <h3 class="text-sm font-bold text-gray-900 flex items-center gap-1.5">
                <svg class="w-4 h-4 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"></path>
                </svg>
                Recent Trades
              </h3>
              <span class="text-xs font-semibold text-gray-500">{{ recentTrades.length }}</span>
            </div>
          </div>
          <div class="flex-1 overflow-y-auto">
            <!-- Loading State -->
            <div v-if="loadingTrades" class="p-4 text-center">
              <svg class="animate-spin h-6 w-6 mx-auto text-blue-600 mb-2" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              <p class="text-xs text-gray-500">Loading trades...</p>
            </div>
            <!-- Empty State -->
            <div v-else-if="recentTrades.length === 0" class="p-4 text-center">
              <div class="w-10 h-10 bg-gray-100 rounded-lg flex items-center justify-center mx-auto mb-2">
                <svg class="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"></path>
                </svg>
              </div>
              <p class="text-gray-900 font-semibold text-xs mb-0.5">No Trades Yet</p>
              <p class="text-gray-500 text-xs">{{ selectedCompany ? 'No trades for this token' : 'Select a token to see trades' }}</p>
            </div>
            <div v-else class="divide-y divide-gray-100">
              <div
                v-for="trade in recentTrades.slice(0, 10)"
                :key="trade.id"
                @click="showTradeDetail(trade)"
                class="p-2.5 hover:bg-gray-50 transition-colors cursor-pointer"
              >
                <div class="flex items-center justify-between mb-1">
                  <div class="flex items-center gap-2">
                    <div :class="trade.type === 'buy' ? 'bg-green-500 text-white' : 'bg-red-500 text-white'" class="w-6 h-6 rounded flex items-center justify-center text-xs font-bold">
                      {{ trade.type === 'buy' ? '↑' : '↓' }}
                    </div>
                    <div>
                      <span class="text-xs font-semibold text-gray-900 block">{{ trade.symbol }}</span>
                      <span class="text-xs text-gray-500">{{ formatTime(trade.timestamp) }}</span>
                    </div>
                  </div>
                  <div :class="trade.type === 'buy' ? 'bg-green-100 text-green-600' : 'bg-red-100 text-red-600'" class="px-1.5 py-0.5 rounded text-xs font-semibold">
                    {{ trade.type.toUpperCase() }}
                  </div>
                </div>
                <div class="flex items-center justify-between pl-8 text-xs">
                  <span class="text-gray-600">{{ trade.quantity.toFixed(4) }} tokens</span>
                  <span class="font-semibold text-gray-900">{{ trade.amount.toFixed(2) }} BUSD</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- Trade Detail Modal -->
  <div v-if="selectedTrade" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50" @click.self="selectedTrade = null">
    <div class="bg-white rounded-xl shadow-2xl max-w-md w-full mx-4 overflow-hidden">
      <!-- Modal Header -->
      <div :class="selectedTrade.type === 'buy' ? 'bg-gradient-to-r from-green-500 to-emerald-600' : 'bg-gradient-to-r from-red-500 to-rose-600'" class="px-6 py-4">
        <div class="flex items-center justify-between">
          <div class="flex items-center gap-3">
            <div class="w-12 h-12 bg-white/20 rounded-xl flex items-center justify-center">
              <span class="text-white text-2xl font-bold">{{ selectedTrade.type === 'buy' ? '↑' : '↓' }}</span>
            </div>
            <div>
              <h3 class="text-white font-bold text-lg">{{ selectedTrade.type === 'buy' ? 'Buy' : 'Sell' }} Order</h3>
              <p class="text-white/80 text-sm">{{ selectedTrade.symbol }}</p>
            </div>
          </div>
          <button @click="selectedTrade = null" class="text-white/80 hover:text-white transition">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
            </svg>
          </button>
        </div>
      </div>

      <!-- Modal Body -->
      <div class="p-6 space-y-4">
        <!-- Trade Summary -->
        <div class="grid grid-cols-2 gap-4">
          <div class="bg-gray-50 rounded-lg p-3">
            <p class="text-xs text-gray-500 mb-1">Quantity</p>
            <p class="text-lg font-bold text-gray-900">{{ selectedTrade.quantity.toFixed(4) }}</p>
            <p class="text-xs text-gray-500">{{ selectedTrade.symbol }} tokens</p>
          </div>
          <div class="bg-gray-50 rounded-lg p-3">
            <p class="text-xs text-gray-500 mb-1">Total Value</p>
            <p class="text-lg font-bold text-gray-900">{{ selectedTrade.amount.toFixed(4) }}</p>
            <p class="text-xs text-gray-500">BUSD</p>
          </div>
        </div>

        <!-- Trade Details -->
        <div class="space-y-3">
          <div class="flex items-center justify-between py-2 border-b border-gray-100">
            <span class="text-sm text-gray-500">Price per Token</span>
            <span class="text-sm font-semibold text-gray-900">{{ (selectedTrade.amount / selectedTrade.quantity).toFixed(4) }} BUSD</span>
          </div>
          <div class="flex items-center justify-between py-2 border-b border-gray-100">
            <span class="text-sm text-gray-500">Trade Type</span>
            <span :class="selectedTrade.type === 'buy' ? 'text-green-600' : 'text-red-600'" class="text-sm font-semibold">{{ selectedTrade.type.toUpperCase() }}</span>
          </div>
          <div class="flex items-center justify-between py-2 border-b border-gray-100">
            <span class="text-sm text-gray-500">Time</span>
            <span class="text-sm font-semibold text-gray-900">{{ formatDate(selectedTrade.timestamp) }}</span>
          </div>
          <div class="flex items-center justify-between py-2">
            <span class="text-sm text-gray-500">Transaction Hash</span>
            <a
              :href="`https://etherscan.io/tx/${selectedTrade.txHash}`"
              target="_blank"
              class="text-sm font-mono text-blue-600 hover:text-blue-800 flex items-center gap-1"
            >
              {{ selectedTrade.txHash ? selectedTrade.txHash.slice(0, 8) + '...' + selectedTrade.txHash.slice(-6) : 'N/A' }}
              <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"></path>
              </svg>
            </a>
          </div>
        </div>
      </div>

      <!-- Modal Footer -->
      <div class="px-6 py-4 bg-gray-50 border-t border-gray-200">
        <button
          @click="selectedTrade = null"
          class="w-full py-2.5 bg-gray-700 text-white font-semibold rounded-lg hover:bg-gray-800 transition"
        >
          Close
        </button>
      </div>
    </div>
  </div>

  <!-- Document Preview Modal -->
  <div v-if="showPreviewModal && documentPreview" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
    <div class="bg-white rounded-lg p-6 max-w-4xl w-full mx-4 max-h-[90vh] flex flex-col">
      <div class="flex justify-between items-center mb-4">
        <h3 class="text-xl font-bold">{{ documentPreview.filename }}</h3>
        <button @click="closePreview" class="text-gray-500 hover:text-gray-700">
          <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
          </svg>
        </button>
      </div>
      <div class="flex-1 overflow-auto bg-gray-100 rounded-lg p-4 min-h-[400px]">
        <iframe v-if="documentPreview.type === 'application/pdf'" :src="documentPreview.url" class="w-full h-full min-h-[500px] rounded"></iframe>
        <img v-else-if="documentPreview.type.startsWith('image/')" :src="documentPreview.url" :alt="documentPreview.filename" class="max-w-full max-h-full mx-auto rounded" />
        <div v-else class="text-center py-12">
          <p class="text-gray-600 mb-2">Preview not available</p>
          <p class="text-sm text-gray-500">Click download to save the file</p>
        </div>
      </div>
      <div class="flex gap-3 mt-4">
        <button @click="closePreview" class="flex-1 px-4 py-2 bg-gray-200 text-gray-800 rounded-lg font-semibold hover:bg-gray-300">Close</button>
        <button @click="downloadDecryptedFile" class="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg font-semibold hover:bg-blue-700">Download</button>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, watch, onMounted } from 'vue'
import blockchain from '../utils/blockchain.js'
import toast from '../utils/toast.js'
import TokenPriceChart from '../components/TokenPriceChart.vue'
import TraderKYC from '../components/TraderKYC.vue'
import { downloadAndDecryptFromIPFS, triggerDownload } from '../utils/encryptedIPFS.js'
import { getOrPromptKey, getKeyAddress } from '../utils/keyManager.js'

export default {
  name: 'Trade',
  components: {
    TokenPriceChart,
    TraderKYC
  },
  setup() {
    const loading = ref(true)
    const userAddress = ref('')
    const companies = ref([])
    const isVerifiedTrader = ref(false)
    const checkingTrader = ref(true)
    const traderKycStatus = ref(null)

    const selectedCompany = ref(null)
    const tradeType = ref('buy')
    const isTrading = ref(false)

    const tradeForm = ref({
      amount: '',
      slippage: '1'
    })

    const recentTrades = ref([])
    const expectedOutput = ref(0)
    const portfolio = ref({})
    const busdBalance = ref('0')
    const loadingTrades = ref(false)
    const selectedTrade = ref(null)
    const showCompanyDetails = ref(false)
    const encryptedDocuments = ref([])
    const loadingEncryptedDocs = ref(false)
    const downloadingDocId = ref(null)
    const showPreviewModal = ref(false)
    const documentPreview = ref(null)

    const showTradeDetail = (trade) => {
      selectedTrade.value = trade
    }

    const formatIPODate = (date) => {
      if (!date) return 'N/A'
      return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
      })
    }

    const getCompanyLogo = (cid) => {
      return getIPFSUrl(cid)
    }

    const getIPFSUrl = (cid) => {
      if (!cid) return '#'
      return `http://localhost:8081//ipfs/${cid}`
    }

    // Calculate expected output when inputs change
    const calculateExpectedOutput = async () => {
      if (!selectedCompany.value || !tradeForm.value.amount || !selectedCompany.value.ammPool) {
        expectedOutput.value = 0
        return
      }

      try {
        const amount = parseFloat(tradeForm.value.amount)
        const tokenIn = tradeType.value === 'buy' ? selectedCompany.value.baseToken : selectedCompany.value.stockToken
        const output = await blockchain.getSwapOutput(selectedCompany.value.ammPool, amount, tokenIn)
        expectedOutput.value = parseFloat(output)
      } catch (error) {
        console.error('Error calculating output:', error)
        expectedOutput.value = 0
      }
    }

    // Watch for changes and recalculate
    watch([() => tradeForm.value.amount, tradeType, selectedCompany], () => {
      calculateExpectedOutput()
    })

    const effectivePrice = computed(() => {
      if (!expectedOutput.value || !tradeForm.value.amount) return 0
      const amount = parseFloat(tradeForm.value.amount)

      if (tradeType.value === 'buy') {
        return amount / expectedOutput.value
      } else {
        return expectedOutput.value / amount
      }
    })

    const tradingFee = computed(() => {
      if (!tradeForm.value.amount) return 0
      return parseFloat(tradeForm.value.amount) * 0.003
    })

    const priceImpact = computed(() => {
      if (!selectedCompany.value || !tradeForm.value.amount) return 0
      const amount = parseFloat(tradeForm.value.amount)
      const basePrice = selectedCompany.value.price

      return Math.abs((effectivePrice.value - basePrice) / basePrice) * 100
    })

    const minimumReceived = computed(() => {
      if (!expectedOutput.value || !tradeForm.value.slippage) return 0
      const slippagePercent = parseFloat(tradeForm.value.slippage) / 100
      return expectedOutput.value * (1 - slippagePercent)
    })

    const maxPriceAfterSlippage = computed(() => {
      if (!effectivePrice.value || !tradeForm.value.slippage) return 0
      const slippagePercent = parseFloat(tradeForm.value.slippage) / 100
      if (tradeType.value === 'buy') {
        // When buying, max price = effective price * (1 + slippage)
        return effectivePrice.value * (1 + slippagePercent)
      } else {
        // When selling, min price = effective price * (1 - slippage)
        return effectivePrice.value * (1 - slippagePercent)
      }
    })

    const canTrade = computed(() => {
      if (!selectedCompany.value || !tradeForm.value.amount) return false
      const amount = parseFloat(tradeForm.value.amount)
      return amount > 0
    })

    const selectCompany = async (company) => {
      selectedCompany.value = company
      showCompanyDetails.value = false // Reset to stock overview when selecting new company
      // Load recent trades for this company
      await loadRecentTrades(company)
      // Load encrypted documents for this company
      await loadEncryptedDocuments(company)
    }

    const loadEncryptedDocuments = async (company) => {
      if (!company?.id) return

      loadingEncryptedDocs.value = true
      encryptedDocuments.value = []

      try {
        const docs = await blockchain.getCompanyEncryptedDocuments(parseInt(company.id))
        encryptedDocuments.value = docs
        console.log('📄 Loaded encrypted documents:', docs)
      } catch (error) {
        console.warn('Could not load encrypted documents:', error)
      } finally {
        loadingEncryptedDocs.value = false
      }
    }

    const downloadEncryptedDocument = async (doc) => {
      if (!blockchain.signer) {
        toast.error('Please connect your wallet first')
        return
      }

      // Logo is NOT encrypted - open directly
      if (doc.docType === 'logo') {
        window.open(`http://localhost:8081/ipfs/${doc.ipfsCid || doc.cid}`, '_blank')
        return
      }

      downloadingDocId.value = doc.id

      try {
        // Use global key address for encrypted document access
        const globalAddress = getKeyAddress()

        // Check if global key can access this document
        const canAccess = await blockchain.canAccessDocument(doc.id, globalAddress)
        if (!canAccess) {
          toast.error('You do not have access to this document')
          return
        }

        // Get encrypted key for global key address
        const encryptedKey = await blockchain.getEncryptedKey(doc.id, globalAddress)

        if (!encryptedKey || !encryptedKey.ciphertext || encryptedKey.ciphertext === '0x' || encryptedKey.ciphertext === '') {
          toast.error('You do not have access to this document')
          return
        }

        // Get private key from key manager (prompts once per session)
        const privateKey = getOrPromptKey()

        if (!privateKey) {
          toast.warning('Decryption cancelled')
          return
        }

        toast.info('Decrypting document...', 'Please wait')

        // Download and decrypt from IPFS
        const result = await downloadAndDecryptFromIPFS(
          doc.ipfsCid || doc.cid,
          encryptedKey,
          privateKey,
          {
            originalName: doc.originalName,
            originalType: guessContentType(doc.originalName)
          }
        )

        // Show preview modal instead of direct download
        documentPreview.value = {
          url: result.url,
          blob: result.blob,
          filename: result.filename,
          type: guessContentType(doc.originalName),
          doc
        }
        showPreviewModal.value = true
        toast.success('Document decrypted!')

      } catch (error) {
        console.error('Error viewing encrypted document:', error)
        toast.error(`Failed to decrypt: ${error.message}`)
      } finally {
        downloadingDocId.value = null
      }
    }

    const closePreview = () => {
      if (documentPreview.value?.url) {
        URL.revokeObjectURL(documentPreview.value.url)
      }
      documentPreview.value = null
      showPreviewModal.value = false
    }

    const downloadDecryptedFile = () => {
      if (!documentPreview.value) return
      triggerDownload(documentPreview.value.url, documentPreview.value.filename)
    }

    const guessContentType = (filename) => {
      const ext = filename?.split('.').pop()?.toLowerCase()
      const types = {
        'pdf': 'application/pdf',
        'png': 'image/png',
        'jpg': 'image/jpeg',
        'jpeg': 'image/jpeg',
        'doc': 'application/msword',
        'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'xls': 'application/vnd.ms-excel',
        'xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
      }
      return types[ext] || 'application/octet-stream'
    }

    const loadRecentTrades = async (company) => {
      if (!company?.ammPool || !blockchain.signer) return

      loadingTrades.value = true
      try {
        const address = await blockchain.signer.getAddress()
        const trades = await blockchain.getRecentTrades(company.ammPool, address, 10)

        // Map trades to display format
        recentTrades.value = trades.map(trade => ({
          id: trade.id,
          type: trade.type,
          symbol: company.symbol,
          amount: parseFloat(trade.type === 'buy' ? trade.amountIn : trade.amountOut),
          quantity: parseFloat(trade.type === 'buy' ? trade.amountOut : trade.amountIn),
          timestamp: trade.timestamp,
          txHash: trade.txHash
        }))

        console.log('📈 Loaded recent trades:', recentTrades.value)
      } catch (error) {
        console.error('Error loading recent trades:', error)
      } finally {
        loadingTrades.value = false
      }
    }

    const executeTrade = async () => {
      if (!canTrade.value) return

      isTrading.value = true

      try {
        const amount = parseFloat(tradeForm.value.amount)
        const minOutput = expectedOutput.value * (1 - parseFloat(tradeForm.value.slippage) / 100)

        // Approve token spending first
        const tokenToApprove = tradeType.value === 'buy' ? selectedCompany.value.baseToken : selectedCompany.value.stockToken
        console.log('Approving token...', tokenToApprove)
        await blockchain.approveToken(tokenToApprove, selectedCompany.value.ammPool, amount)

        // Execute swap
        console.log('Executing swap...')
        const receipt = await blockchain.swapTokens(
          selectedCompany.value.ammPool,
          amount,
          minOutput,
          tradeType.value === 'buy'
        )

        console.log('Trade successful:', receipt)

        // Add to recent trades
        recentTrades.value.unshift({
          id: Date.now(),
          type: tradeType.value,
          symbol: selectedCompany.value.symbol,
          amount: amount,
          quantity: expectedOutput.value,
          timestamp: new Date()
        })

        // Refresh portfolio balances and recent trades
        await loadPortfolio()
        if (selectedCompany.value) {
          await loadRecentTrades(selectedCompany.value)
        }

        // Reset form
        tradeForm.value.amount = ''

        toast.success(`Successfully ${tradeType.value === 'buy' ? 'bought' : 'sold'} ${selectedCompany.value.symbol}!`, 'Trade Complete')

      } catch (error) {
        console.error('Trade error:', error)
        toast.txError(error, 'Trade Failed', 'Failed to execute trade')
      } finally {
        isTrading.value = false
      }
    }

    const formatTime = (timestamp) => {
      return timestamp.toLocaleTimeString('en-US', {
        hour: '2-digit',
        minute: '2-digit'
      })
    }

    const checkTraderStatus = async () => {
      checkingTrader.value = true
      console.log('🔍 Checking trader verification status...')

      try {
        if (!blockchain.signer) {
          console.log('❌ No signer available')
          isVerifiedTrader.value = false
          traderKycStatus.value = null
          checkingTrader.value = false
          return
        }

        const address = await blockchain.signer.getAddress()
        console.log('👤 Checking address:', address)

        // Get full KYC status to check if revoked
        const kycData = await blockchain.getTraderKYC(address)
        if (kycData) {
          traderKycStatus.value = kycData.status
          console.log('📋 KYC Status:', kycData.status)
        } else {
          traderKycStatus.value = null
        }

        const traderStatus = await blockchain.isVerifiedTrader(address)
        console.log('✅ Trader verification status:', traderStatus)
        isVerifiedTrader.value = traderStatus
      } catch (error) {
        console.error('❌ Error checking trader status:', error)
        isVerifiedTrader.value = false
        traderKycStatus.value = null
      } finally {
        checkingTrader.value = false
        console.log('✓ Trader check complete. isVerifiedTrader:', isVerifiedTrader.value, 'kycStatus:', traderKycStatus.value)
      }
    }

    const refreshTraderStatus = async () => {
      await checkTraderStatus()
    }

    const loadPortfolio = async () => {
      if (!blockchain.signer) return

      try {
        const address = await blockchain.signer.getAddress()
        const newPortfolio = {}

        for (const company of companies.value) {
          if (company.stockToken && company.stockToken !== '0x0000000000000000000000000000000000000000') {
            try {
              const balance = await blockchain.getTokenBalance(company.stockToken, address)
              if (parseFloat(balance) > 0) {
                newPortfolio[company.symbol] = {
                  balance: balance,
                  price: company.price,
                  tokenAddress: company.stockToken
                }
              }
            } catch (err) {
              console.error(`Error fetching balance for ${company.symbol}:`, err)
            }
          }
        }

        portfolio.value = newPortfolio

        // Also load BUSD balance
        const busd = await blockchain.getBaseTokenBalance(address)
        busdBalance.value = busd

        console.log('📊 Portfolio loaded:', portfolio.value, 'BUSD:', busdBalance.value)
      } catch (error) {
        console.error('Error loading portfolio:', error)
      }
    }

    const formatDate = (date) => {
      if (!date) return 'N/A'
      return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      })
    }

    const formatDocType = (docType) => {
      const typeMap = {
        'prospectus': 'Prospectus',
        'financials': 'Financials',
        'logo': 'Logo',
        'encrypted': 'Confidential'
      }
      return typeMap[docType] || docType
    }

    const getDocTypeButtonClass = (docType) => {
      const classMap = {
        'prospectus': 'bg-blue-50 text-blue-700 hover:bg-blue-100',
        'financials': 'bg-green-50 text-green-700 hover:bg-green-100',
        'logo': 'bg-purple-50 text-purple-700 hover:bg-purple-100',
        'encrypted': 'bg-amber-50 text-amber-700 hover:bg-amber-100'
      }
      return classMap[docType] || 'bg-gray-50 text-gray-700 hover:bg-gray-100'
    }

    const loadCompanies = async () => {
      try {
        const allCompanies = await blockchain.getAllCompanies()

        // Only show companies with AMM pools
        const tradableCompanies = []
        for (const company of allCompanies) {
          if (company.ammPool && company.ammPool !== '0x0000000000000000000000000000000000000000') {
            try {
              const price = await blockchain.getAMMPrice(company.ammPool)
              const reserves = await blockchain.getAMMReserves(company.ammPool)

              // Get actual 24h price change and volume from blockchain
              const priceChange = await blockchain.get24hPriceChange(company.ammPool)
              const volume24h = await blockchain.get24hVolume(company.ammPool)

              tradableCompanies.push({
                id: company.id,
                name: company.name,
                symbol: company.symbol,
                price: parseFloat(price),
                change: priceChange, // Actual 24h price change
                liquidity: parseFloat(reserves.base),
                volume24h: volume24h, // Actual 24h volume
                stockToken: company.stockToken,
                baseToken: await blockchain.getAMM(company.ammPool).base_token(),
                ammPool: company.ammPool,
                ipfsProspectus: company.ipfsProspectus,
                ipfsFinancials: company.ipfsFinancials,
                ipfsLogo: company.ipfsLogo,
                createdAt: company.createdAt
              })
            } catch (err) {
              console.warn(`Could not load data for ${company.symbol}:`, err)
            }
          }
        }

        companies.value = tradableCompanies

        // Auto-select first company
        if (companies.value.length > 0) {
          selectedCompany.value = companies.value[0]
        }
      } catch (error) {
        console.error('Error loading companies:', error)
      }
    }

    onMounted(async () => {
      console.log('🚀 Trade view mounted')

      try {
        // Ensure blockchain is initialized and contracts are loaded
        if (!blockchain.provider) {
          console.log('⚠️ Blockchain not initialized, initializing...')
          await blockchain.initialize()
        } else {
          // Even if provider exists, ensure contract addresses are loaded
          console.log('🔄 Ensuring contract addresses are loaded...')
          await blockchain.loadContractAddresses()
        }

        // Check trader verification status first
        await checkTraderStatus()

        // Load companies if user is verified trader
        if (isVerifiedTrader.value) {
          console.log('📊 Loading companies...')
          loading.value = true
          await loadCompanies()
          await loadPortfolio()
          loading.value = false
        }
      } catch (error) {
        console.error('❌ Error in Trade view mount:', error)
        checkingTrader.value = false
        loading.value = false
      }
    })

    return {
      companies,
      selectedCompany,
      tradeType,
      tradeForm,
      recentTrades,
      isTrading,
      loading,
      isVerifiedTrader,
      checkingTrader,
      traderKycStatus,
      portfolio,
      busdBalance,
      loadingTrades,
      expectedOutput,
      effectivePrice,
      tradingFee,
      priceImpact,
      minimumReceived,
      maxPriceAfterSlippage,
      canTrade,
      selectCompany,
      executeTrade,
      formatTime,
      formatDate,
      refreshTraderStatus,
      loadPortfolio,
      loadRecentTrades,
      selectedTrade,
      showTradeDetail,
      showCompanyDetails,
      formatIPODate,
      getIPFSUrl,
      getCompanyLogo,
      encryptedDocuments,
      loadingEncryptedDocs,
      downloadingDocId,
      downloadEncryptedDocument,
      showPreviewModal,
      documentPreview,
      closePreview,
      downloadDecryptedFile,
      formatDocType,
      getDocTypeButtonClass
    }
  }
}
</script>
