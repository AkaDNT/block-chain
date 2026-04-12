<template>
  <div id="app" class="min-h-screen bg-gray-50">
    <!-- Navigation -->
    <nav class="bg-white shadow-sm border-b border-gray-200">
      <div class="max-w-7xl mx-auto px-6">
        <div class="flex justify-between items-center h-16">
          <div class="flex items-center">
            <router-link
              to="/"
              class="flex items-center space-x-3 group logo-link"
            >
              <div class="relative">
                <img
                  :src="logo"
                  alt="DEXCK Logo"
                  class="relative h-10 w-10 transform group-hover:scale-105 transition-transform duration-200"
                />
              </div>
              <div class="flex flex-col">
                <span
                  class="text-l font-bold text-gray-900 tracking-tight pixel-font"
                  >DEXCK</span
                >
                <span class="text-xs text-gray-500 -mt-0.5"
                  >Decentralized Stock Exchange</span
                >
              </div>
            </router-link>
          </div>

          <div class="flex items-center space-x-1">
            <router-link
              to="/"
              v-if="!isAdmin"
              class="text-gray-600 hover:text-gray-900 px-4 py-2 rounded-md text-sm font-medium transition-colors duration-150"
            >
              Home
            </router-link>
            <router-link
              v-if="!isAdmin"
              to="/register"
              class="text-gray-600 hover:text-gray-900 px-4 py-2 rounded-md text-sm font-medium transition-colors duration-150"
            >
              My Company
            </router-link>
            <router-link
              v-if="!isAdmin"
              to="/trade"
              class="text-gray-600 hover:text-gray-900 px-4 py-2 rounded-md text-sm font-medium transition-colors duration-150"
            >
              Trade
            </router-link>
            <router-link
              to="/dashboard"
              class="text-gray-600 hover:text-gray-900 px-4 py-2 rounded-md text-sm font-medium transition-colors duration-150"
            >
              Dashboard
            </router-link>
            <router-link
              v-if="isAdmin"
              to="/admin"
              class="text-gray-600 hover:text-gray-900 px-4 py-2 rounded-md text-sm font-medium transition-colors duration-150"
            >
              Admin
            </router-link>

            <!-- Wallet Connection -->
            <button
              @click="connectWallet"
              v-if="!isConnected"
              class="ml-6 bg-blue-600 text-white hover:bg-blue-700 px-5 py-2 rounded-lg text-sm font-semibold shadow-sm hover:shadow transition-all duration-150"
            >
              Connect Wallet
            </button>

            <div v-else class="relative ml-6">
              <button
                @click="toggleDropdown"
                class="flex items-center space-x-2.5 bg-gray-50 hover:bg-gray-100 px-3.5 py-2 rounded-lg text-sm border border-gray-200 transition-all duration-150"
              >
                <div class="w-2 h-2 bg-green-500 rounded-full"></div>
                <div class="flex flex-col items-start">
                  <span class="text-gray-900 font-semibold text-xs">{{
                    shortAddress(account)
                  }}</span>
                  <span class="text-gray-500 text-xs">{{ balance }} ETH</span>
                </div>
                <svg
                  class="w-3.5 h-3.5 text-gray-500"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M19 9l-7 7-7-7"
                  ></path>
                </svg>
              </button>

              <!-- Portfolio Dropdown -->
              <div
                v-if="showDropdown"
                class="absolute right-0 mt-2 w-80 bg-white rounded-lg shadow-xl border border-gray-200 z-50"
              >
                <!-- Portfolio Header -->
                <div
                  class="px-4 py-3 bg-white rounded-t-lg border-b border-gray-200"
                >
                  <h3 class="text-black font-semibold text-sm">My Portfolio</h3>
                  <p class="text-gray-500 text-xs mt-1">
                    {{ shortAddress(account) }}
                  </p>
                </div>

                <!-- Balances Section -->
                <div class="p-4 space-y-3">
                  <!-- ETH Balance -->
                  <div
                    class="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
                  >
                    <div class="flex items-center space-x-3">
                      <div
                        class="w-8 h-8 bg-gradient-to-br from-purple-400 to-purple-600 rounded-full flex items-center justify-center"
                      >
                        <span class="text-white text-xs font-bold">Ξ</span>
                      </div>
                      <div>
                        <p class="text-xs text-gray-500">Ethereum</p>
                        <p class="text-sm font-bold text-gray-900">
                          {{ balance }} ETH
                        </p>
                      </div>
                    </div>
                    <button
                      @click="showDepositModal = true"
                      class="px-3 py-1.5 bg-green-600 text-white text-xs rounded-lg hover:bg-green-700 font-semibold"
                      title="Deposit ETH for BUSD"
                    >
                      Deposit
                    </button>
                  </div>

                  <!-- BUSD Balance -->
                  <div
                    class="flex items-center justify-between p-3 bg-yellow-50 rounded-lg"
                  >
                    <div class="flex items-center space-x-3">
                      <div
                        class="w-8 h-8 bg-gradient-to-br from-yellow-400 to-yellow-600 rounded-full flex items-center justify-center"
                      >
                        <span class="text-white text-xs font-bold">$</span>
                      </div>
                      <div>
                        <p class="text-xs text-gray-500">BUSD</p>
                        <p class="text-sm font-bold text-gray-900">
                          {{ formattedBusdBalance }} BUSD
                        </p>
                      </div>
                    </div>
                    <button
                      @click="showWithdrawModal = true"
                      class="px-3 py-1.5 bg-red-600 text-white text-xs rounded-lg hover:bg-red-700 font-semibold"
                      title="Withdraw BUSD for ETH"
                    >
                      Withdraw
                    </button>
                  </div>

                  <!-- Stock Token Holdings -->
                  <div
                    v-for="holding in stockHoldings"
                    :key="holding.symbol"
                    class="flex items-center justify-between p-3 bg-blue-50 rounded-lg"
                  >
                    <div class="flex items-center space-x-3">
                      <div
                        class="w-8 h-8 bg-gradient-to-br from-blue-400 to-blue-600 rounded-full flex items-center justify-center"
                      >
                        <span class="text-white text-xs font-bold">{{
                          holding.symbol?.charAt(0) || "S"
                        }}</span>
                      </div>
                      <div>
                        <p class="text-xs text-gray-500">
                          {{ holding.symbol || "Stock Token" }}
                        </p>
                        <p class="text-sm font-bold text-gray-900">
                          {{ holding.formattedBalance }} {{ holding.symbol }}
                        </p>
                      </div>
                    </div>
                  </div>

                  <!-- Refresh Button -->
                  <button
                    @click="refreshBalances"
                    class="w-full py-2 bg-gray-100 hover:bg-gray-200 text-gray-700 text-sm rounded-lg flex items-center justify-center space-x-2"
                  >
                    <svg
                      class="w-4 h-4"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        stroke-linecap="round"
                        stroke-linejoin="round"
                        stroke-width="2"
                        d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
                      ></path>
                    </svg>
                    <span>Refresh Balances</span>
                  </button>
                </div>

                <!-- Actions Section -->
                <div class="border-t border-gray-200 py-1">
                  <button
                    @click="switchAccount"
                    class="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 flex items-center space-x-2"
                  >
                    <svg
                      class="w-4 h-4"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        stroke-linecap="round"
                        stroke-linejoin="round"
                        stroke-width="2"
                        d="M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4"
                      ></path>
                    </svg>
                    <span>Switch Account</span>
                  </button>
                  <button
                    @click="copyAddress"
                    class="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 flex items-center space-x-2"
                  >
                    <svg
                      class="w-4 h-4"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        stroke-linecap="round"
                        stroke-linejoin="round"
                        stroke-width="2"
                        d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z"
                      ></path>
                    </svg>
                    <span>Copy Address</span>
                  </button>
                  <div class="border-t border-gray-200"></div>
                  <button
                    @click="disconnectWallet"
                    class="w-full text-left px-4 py-2 text-sm text-red-600 hover:bg-red-50 flex items-center space-x-2"
                  >
                    <svg
                      class="w-4 h-4"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        stroke-linecap="round"
                        stroke-linejoin="round"
                        stroke-width="2"
                        d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"
                      ></path>
                    </svg>
                    <span>Disconnect</span>
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </nav>

    <!-- Swap Modal -->
    <div
      v-if="showSwapModal"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
    >
      <div class="bg-white rounded-lg p-6 max-w-md w-full mx-4">
        <div class="flex justify-between items-center mb-4">
          <h3 class="text-xl font-bold">Swap ETH for BUSD</h3>
          <button
            @click="showSwapModal = false"
            class="text-gray-500 hover:text-gray-700"
          >
            <svg
              class="w-6 h-6"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M6 18L18 6M6 6l12 12"
              ></path>
            </svg>
          </button>
        </div>

        <div class="space-y-4">
          <!-- Exchange Rate Info -->
          <div class="p-3 bg-blue-50 rounded-lg">
            <p class="text-sm text-blue-800">
              <strong>Exchange Rate:</strong> 1 ETH = {{ swapRate }} BUSD
            </p>
          </div>

          <!-- From (ETH) -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2"
              >From</label
            >
            <div class="relative">
              <input
                v-model="swapAmount"
                type="number"
                step="0.001"
                min="0"
                :max="parseFloat(balance)"
                placeholder="0.0"
                class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
              <div class="absolute right-3 top-3 flex items-center space-x-2">
                <span class="text-gray-500 font-medium">ETH</span>
                <button
                  @click="swapAmount = balance"
                  class="text-xs text-blue-600 hover:text-blue-800"
                >
                  MAX
                </button>
              </div>
            </div>
            <p class="text-xs text-gray-500 mt-1">
              Available: {{ balance }} ETH
            </p>
          </div>

          <!-- Swap Icon -->
          <div class="flex justify-center">
            <div
              class="w-10 h-10 bg-gray-100 rounded-full flex items-center justify-center"
            >
              <svg
                class="w-5 h-5 text-gray-600"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M7 16V4m0 0L3 8m4-4l4 4m6 0v12m0 0l4-4m-4 4l-4-4"
                ></path>
              </svg>
            </div>
          </div>

          <!-- To (BUSD) -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2"
              >To (estimated)</label
            >
            <div class="relative">
              <input
                :value="estimatedBUSD"
                readonly
                placeholder="0.0"
                class="w-full px-4 py-3 border border-gray-300 rounded-lg bg-gray-50"
              />
              <div class="absolute right-3 top-3">
                <span class="text-gray-500 font-medium">BUSD</span>
              </div>
            </div>
          </div>

          <!-- Swap Button -->
          <button
            @click="executeSwap"
            :disabled="
              !swapAmount ||
              parseFloat(swapAmount) <= 0 ||
              parseFloat(swapAmount) > parseFloat(balance)
            "
            class="w-full py-3 bg-blue-600 text-white rounded-lg font-semibold hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Swap
          </button>

          <!-- Info -->
          <p class="text-xs text-gray-500 text-center">
            This swap uses a simple 1:{{ swapRate }} rate for testing. In
            production, use a DEX like Uniswap.
          </p>
        </div>
      </div>
    </div>

    <!-- Deposit Modal -->
    <div
      v-if="showDepositModal"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
      @click.self="isDepositing ? null : (showDepositModal = false)"
    >
      <div class="bg-white rounded-lg shadow-xl max-w-md w-full mx-4 p-6">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-xl font-bold text-gray-900">Deposit ETH for BUSD</h3>
          <button
            @click="showDepositModal = false"
            :disabled="isDepositing"
            class="text-gray-500 hover:text-gray-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <svg
              class="w-6 h-6"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M6 18L18 6M6 6l12 12"
              ></path>
            </svg>
          </button>
        </div>

        <div class="space-y-4">
          <!-- Exchange Rate Info -->
          <div class="p-3 bg-green-50 rounded-lg">
            <p class="text-sm text-green-800">
              <strong>Exchange Rate:</strong> 1 ETH = {{ ethToBusdRate }} BUSD
            </p>
          </div>

          <!-- From (ETH) -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2"
              >Deposit Amount</label
            >
            <div class="relative">
              <input
                v-model="depositAmount"
                type="number"
                step="0.001"
                min="0.001"
                :max="parseFloat(balance)"
                placeholder="0.0"
                :disabled="isDepositing"
                @input="calculateDepositOutput"
                class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent disabled:bg-gray-100 disabled:cursor-not-allowed"
              />
              <div class="absolute right-3 top-3 flex items-center space-x-2">
                <span class="text-gray-500 font-medium">ETH</span>
                <button
                  @click="
                    depositAmount = balance;
                    calculateDepositOutput();
                  "
                  :disabled="isDepositing"
                  class="text-xs text-green-600 hover:text-green-800 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  MAX
                </button>
              </div>
            </div>
            <p class="text-xs text-gray-500 mt-1">
              Available: {{ balance }} ETH
            </p>
          </div>

          <!-- Arrow Icon -->
          <div class="flex justify-center">
            <div
              class="w-10 h-10 bg-green-100 rounded-full flex items-center justify-center"
            >
              <svg
                class="w-5 h-5 text-green-600"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M19 14l-7 7m0 0l-7-7m7 7V3"
                ></path>
              </svg>
            </div>
          </div>

          <!-- To (BUSD) -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2"
              >You will receive</label
            >
            <div class="relative">
              <input
                :value="estimatedDepositBUSD"
                readonly
                placeholder="0.0"
                class="w-full px-4 py-3 border border-gray-300 rounded-lg bg-gray-50"
              />
              <div class="absolute right-3 top-3">
                <span class="text-gray-500 font-medium">BUSD</span>
              </div>
            </div>
          </div>

          <!-- Deposit Button -->
          <button
            @click="executeDeposit"
            :disabled="
              isDepositing ||
              !depositAmount ||
              parseFloat(depositAmount) <= 0 ||
              parseFloat(depositAmount) > parseFloat(balance)
            "
            class="w-full py-3 bg-green-600 text-white rounded-lg font-semibold hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <span v-if="isDepositing" class="flex items-center justify-center">
              <svg
                class="animate-spin -ml-1 mr-2 h-5 w-5 text-white"
                fill="none"
                viewBox="0 0 24 24"
              >
                <circle
                  class="opacity-25"
                  cx="12"
                  cy="12"
                  r="10"
                  stroke="currentColor"
                  stroke-width="4"
                ></circle>
                <path
                  class="opacity-75"
                  fill="currentColor"
                  d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                ></path>
              </svg>
              Processing...
            </span>
            <span v-else>Deposit ETH</span>
          </button>

          <!-- Info -->
          <div class="p-3 bg-blue-50 rounded-lg">
            <p class="text-xs text-blue-800">
              <strong>ℹ️ Info:</strong> Your ETH is held as collateral. You can
              withdraw your BUSD anytime to get your ETH back.
            </p>
          </div>
        </div>
      </div>
    </div>

    <!-- Withdraw Modal -->
    <div
      v-if="showWithdrawModal"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
      @click.self="isWithdrawing ? null : (showWithdrawModal = false)"
    >
      <div class="bg-white rounded-lg shadow-xl max-w-md w-full mx-4 p-6">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-xl font-bold text-gray-900">Withdraw BUSD for ETH</h3>
          <button
            @click="showWithdrawModal = false"
            :disabled="isWithdrawing"
            class="text-gray-500 hover:text-gray-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <svg
              class="w-6 h-6"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M6 18L18 6M6 6l12 12"
              ></path>
            </svg>
          </button>
        </div>

        <div class="space-y-4">
          <!-- Exchange Rate Info -->
          <div class="p-3 bg-red-50 rounded-lg">
            <p class="text-sm text-red-800">
              <strong>Exchange Rate:</strong> 1 ETH = {{ ethToBusdRate }} BUSD
            </p>
          </div>

          <!-- From (BUSD) -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2"
              >Withdraw Amount</label
            >
            <div class="relative">
              <input
                v-model="withdrawAmount"
                type="number"
                step="1"
                min="1"
                :max="parseFloat(busdBalance)"
                placeholder="0.0"
                :disabled="isWithdrawing"
                @input="calculateWithdrawOutput"
                class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent disabled:bg-gray-100 disabled:cursor-not-allowed"
              />
              <div class="absolute right-3 top-3 flex items-center space-x-2">
                <span class="text-gray-500 font-medium">BUSD</span>
                <button
                  @click="
                    withdrawAmount = busdBalance;
                    calculateWithdrawOutput();
                  "
                  :disabled="isWithdrawing"
                  class="text-xs text-red-600 hover:text-red-800 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  MAX
                </button>
              </div>
            </div>
            <p class="text-xs text-gray-500 mt-1">
              Available: {{ formattedBusdBalance }} BUSD
            </p>
          </div>

          <!-- Arrow Icon -->
          <div class="flex justify-center">
            <div
              class="w-10 h-10 bg-red-100 rounded-full flex items-center justify-center"
            >
              <svg
                class="w-5 h-5 text-red-600"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M5 10l7-7m0 0l7 7m-7-7v18"
                ></path>
              </svg>
            </div>
          </div>

          <!-- To (ETH) -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2"
              >You will receive</label
            >
            <div class="relative">
              <input
                :value="estimatedWithdrawETH"
                readonly
                placeholder="0.0"
                class="w-full px-4 py-3 border border-gray-300 rounded-lg bg-gray-50"
              />
              <div class="absolute right-3 top-3">
                <span class="text-gray-500 font-medium">ETH</span>
              </div>
            </div>
          </div>

          <!-- Withdraw Button -->
          <button
            @click="executeWithdraw"
            :disabled="
              isWithdrawing ||
              !withdrawAmount ||
              parseFloat(withdrawAmount) <= 0 ||
              parseFloat(withdrawAmount) > parseFloat(busdBalance)
            "
            class="w-full py-3 bg-red-600 text-white rounded-lg font-semibold hover:bg-red-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <span v-if="isWithdrawing" class="flex items-center justify-center">
              <svg
                class="animate-spin -ml-1 mr-2 h-5 w-5 text-white"
                fill="none"
                viewBox="0 0 24 24"
              >
                <circle
                  class="opacity-25"
                  cx="12"
                  cy="12"
                  r="10"
                  stroke="currentColor"
                  stroke-width="4"
                ></circle>
                <path
                  class="opacity-75"
                  fill="currentColor"
                  d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                ></path>
              </svg>
              Processing...
            </span>
            <span v-else>Withdraw BUSD</span>
          </button>

          <!-- Info -->
          <div class="p-3 bg-blue-50 rounded-lg">
            <p class="text-xs text-blue-800">
              <strong>ℹ️ Info:</strong> Your BUSD will be burned and you'll
              receive your ETH collateral back.
            </p>
          </div>
        </div>
      </div>
    </div>

    <!-- Main Content -->
    <main class="max-w-7xl mx-auto py-6 px-4">
      <router-view />
    </main>

    <!-- Footer -->
    <footer class="bg-white border-t mt-2">
      <div class="max-w-7xl mx-auto py-4 px-4 text-center text-gray-600"></div>
    </footer>

    <!-- Toast Notifications -->
    <Toast />

    <!-- Confirmation Modal -->
    <ConfirmModal />
  </div>
</template>

<script>
import { ref, computed, onMounted, getCurrentInstance } from "vue";
import { ethers } from "ethers";
import blockchain from "./utils/blockchain.js";
import Toast from "./components/Toast.vue";
import ConfirmModal from "./components/ConfirmModal.vue";
import toast from "./utils/toast.js";
import { confirm } from "./utils/confirm.js";
import logoUrl from "./assets/images/logo.svg";

export default {
  name: "App",
  setup() {
    // Logo
    const logo = logoUrl;

    const isConnected = ref(false);
    const account = ref("");
    const balance = ref("0.00");
    const busdBalance = ref("0");
    const stockTokenBalance = ref(null);
    const stockSymbol = ref(null);
    const stockHoldings = ref([]); // Array of all stock token holdings
    const showDropdown = ref(false);
    const isAdmin = ref(false);
    const isMinter = ref(false);

    // Swap state
    const showSwapModal = ref(false);
    const swapAmount = ref("");
    const swapRate = ref(2000); // 1 ETH = 2000 BUSD (example rate)

    const estimatedBUSD = computed(() => {
      if (!swapAmount.value || parseFloat(swapAmount.value) <= 0) return "0.0";
      return (parseFloat(swapAmount.value) * swapRate.value).toFixed(2);
    });

    // Deposit/Withdraw state
    const showDepositModal = ref(false);
    const showWithdrawModal = ref(false);
    const depositAmount = ref("");
    const withdrawAmount = ref("");
    const ethToBusdRate = ref("2000");
    const estimatedDepositBUSD = ref("0.0");
    const estimatedWithdrawETH = ref("0.0");
    const isDepositing = ref(false);
    const isWithdrawing = ref(false);

    // Computed properties for formatted display
    const formattedBusdBalance = computed(() => {
      if (!busdBalance.value) return "0";
      return parseFloat(busdBalance.value).toLocaleString("en-US", {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2,
      });
    });

    const formattedStockBalance = computed(() => {
      if (!stockTokenBalance.value) return null;
      return parseFloat(stockTokenBalance.value).toLocaleString("en-US", {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2,
      });
    });

    const updateBalance = async () => {
      if (account.value && blockchain.provider) {
        try {
          const bal = await blockchain.getBalance(account.value);
          balance.value = parseFloat(bal).toFixed(4);
        } catch (error) {
          console.error("Error fetching balance:", error);
          balance.value = "0.00";
        }
      }
    };

    const checkAdminAccess = async () => {
      try {
        if (!blockchain.signer) {
          isAdmin.value = false;
          return;
        }

        const registry = blockchain.getRegistry();
        const address = await blockchain.signer.getAddress();

        // Check if user is admin or verifier
        const admin = await registry.admin();
        const isVerifier = await registry.verifiers(address);

        isAdmin.value =
          address.toLowerCase() === admin.toLowerCase() || isVerifier;
      } catch (error) {
        console.error("Error checking admin access:", error);
        isAdmin.value = false;
      }
    };

    const connectWallet = async () => {
      try {
        const connected = await blockchain.connect();
        if (connected) {
          account.value = await blockchain.signer.getAddress();
          isConnected.value = true;
          await updateBalance();
          await checkAdminAccess();

          console.log("Connected to wallet:", account.value);

          if (blockchain.isUsingDevWallet()) {
            toast.info(
              "Connected in Dev Wallet mode (no MetaMask confirmation required).",
            );
          }

          const walletProvider = blockchain.getWalletProvider();

          // Listen for account changes - reload page to refresh all component states
          if (walletProvider?.on) {
            walletProvider.on("accountsChanged", async (accounts) => {
              if (accounts.length === 0) {
                disconnectWallet();
              } else {
                // Reload the page to ensure all components refresh with new account
                window.location.reload();
              }
            });

            // Listen for chain changes
            walletProvider.on("chainChanged", () => {
              window.location.reload();
            });
          }
        } else {
          toast.warning(
            "No EVM wallet detected. Install MetaMask/Rabby or enable VITE_DEV_AUTO_WALLET=true for local testing.",
            "Wallet Not Found",
          );
        }
      } catch (error) {
        console.error("Error connecting wallet:", error);
        toast.txError(error, "Connection Failed", "Error connecting to wallet");
      }
    };

    const toggleDropdown = async () => {
      showDropdown.value = !showDropdown.value;
      if (showDropdown.value) {
        await refreshBalances();
      }
    };

    const refreshBalances = async () => {
      if (!blockchain.signer) return;

      try {
        const address = await blockchain.signer.getAddress();

        // Get ETH balance
        await updateBalance();

        // Get BUSD balance
        const busd = await blockchain.getBaseTokenBalance(address);
        busdBalance.value = parseFloat(busd).toFixed(2);

        // Check if user is a minter
        try {
          const baseToken = blockchain.getBaseToken();
          isMinter.value = await baseToken.minters(address);
        } catch (error) {
          isMinter.value = false;
        }

        // Get all stock token holdings from all companies
        try {
          const allCompanies = await blockchain.getAllCompanies();
          const holdings = [];

          for (const company of allCompanies) {
            if (
              company.stockToken &&
              company.stockToken !==
                "0x0000000000000000000000000000000000000000"
            ) {
              try {
                const balance = await blockchain.getTokenBalance(
                  company.stockToken,
                  address,
                );
                const balanceNum = parseFloat(balance);
                if (balanceNum > 0) {
                  holdings.push({
                    symbol: company.symbol,
                    balance: balanceNum,
                    formattedBalance: balanceNum.toLocaleString("en-US", {
                      minimumFractionDigits: 2,
                      maximumFractionDigits: 4,
                    }),
                    tokenAddress: company.stockToken,
                  });
                }
              } catch (err) {
                console.warn(
                  `Could not fetch balance for ${company.symbol}:`,
                  err,
                );
              }
            }
          }

          stockHoldings.value = holdings;
          console.log("📊 Stock holdings loaded:", holdings);
        } catch (error) {
          console.error("Error loading stock holdings:", error);
          stockHoldings.value = [];
        }
      } catch (error) {
        console.error("Error refreshing balances:", error);
      }
    };

    const mintBUSD = async () => {
      const confirmed = await confirm({
        title: "Mint Test BUSD",
        message: "Mint 10,000 BUSD tokens for testing?",
        details:
          "This is a test token for development. In production, you would need real BUSD.",
        type: "info",
        confirmText: "Mint",
        cancelText: "Cancel",
      });

      if (!confirmed) {
        showDropdown.value = false;
        return;
      }

      try {
        const baseToken = blockchain.getBaseToken();
        const address = await blockchain.signer.getAddress();

        // Check if user is a minter
        const isMinter = await baseToken.minters(address);

        if (!isMinter) {
          // Try to add user as minter (will only work if user is owner)
          try {
            toast.txStep("Add Minter", "Adding you as a minter to mint BUSD");
            const addTx = await baseToken.add_minter(address);
            toast.txPending("Adding minter");
            await addTx.wait();
            toast.txConfirmed("Added as minter");
          } catch (addError) {
            // If not owner, show helpful error
            toast.warning(
              "You need to be added as a minter first. Contact the contract owner.",
              "Not a Minter",
            );
            return;
          }
        }

        const amount = ethers.parseUnits("10000", 18);

        toast.txStep("Mint BUSD", "Mint 10,000 BUSD tokens to your wallet");
        const tx = await baseToken.mint(address, amount);
        toast.txPending("Minting BUSD");
        await tx.wait();

        toast.txConfirmed("BUSD minted", "10,000 BUSD added to your wallet");
        await refreshBalances();
      } catch (error) {
        console.error("Error minting BUSD:", error);
        toast.txError(error, "Mint Failed", "Failed to mint BUSD");
      }
    };

    const executeSwap = async () => {
      if (!swapAmount.value || parseFloat(swapAmount.value) <= 0) {
        toast.warning("Please enter a valid amount");
        return;
      }

      const confirmed = await confirm({
        title: "Confirm Swap",
        message: `Swap ${swapAmount.value} ETH for ${estimatedBUSD.value} BUSD?`,
        details: `Exchange rate: 1 ETH = ${swapRate.value} BUSD`,
        type: "info",
        confirmText: "Swap",
        cancelText: "Cancel",
      });

      if (!confirmed) {
        showSwapModal.value = false;
        return;
      }

      try {
        const baseToken = blockchain.getBaseToken();
        const address = await blockchain.signer.getAddress();

        // Check if user is a minter
        const isMinter = await baseToken.minters(address);

        if (!isMinter) {
          // Try to add user as minter (will only work if user is owner)
          try {
            toast.txStep("Add Minter", "Adding you as a minter first");
            const addTx = await baseToken.add_minter(address);
            toast.txPending("Adding minter");
            await addTx.wait();
            toast.txConfirmed("Added as minter");
          } catch (addError) {
            // If not owner, show helpful error
            toast.warning(
              "You need to be added as a minter first. Contact the contract owner.",
              "Not a Minter",
            );
            showSwapModal.value = false;
            return;
          }
        }

        // Calculate BUSD amount to mint
        const busdAmount = ethers.parseUnits(estimatedBUSD.value, 18);

        toast.txStep(
          "Swap ETH for BUSD",
          `Convert ${swapAmount.value} ETH to ${estimatedBUSD.value} BUSD`,
        );

        // In a real DEX, you would:
        // 1. Send ETH to a liquidity pool
        // 2. Receive BUSD from the pool
        // For testing, we'll just mint BUSD and keep the ETH
        const tx = await baseToken.mint(address, busdAmount);
        toast.txPending("Processing swap");
        await tx.wait();

        toast.txConfirmed(
          "Swap successful",
          `${swapAmount.value} ETH → ${estimatedBUSD.value} BUSD`,
        );

        // Reset and refresh
        swapAmount.value = "";
        showSwapModal.value = false;
        await refreshBalances();
      } catch (error) {
        console.error("Error executing swap:", error);
        toast.txError(error, "Swap Failed", "Swap failed");
      }
    };

    const loadETHToBUSDRate = async () => {
      try {
        const rate = await blockchain.getETHtoBUSDRate();
        ethToBusdRate.value = rate;
        console.log("ETH to BUSD rate:", rate);
      } catch (error) {
        console.error("Error loading ETH to BUSD rate:", error);
        ethToBusdRate.value = "2000"; // Fallback rate
      }
    };

    const calculateDepositOutput = async () => {
      if (!depositAmount.value || parseFloat(depositAmount.value) <= 0) {
        estimatedDepositBUSD.value = "0.0";
        return;
      }
      try {
        const output = await blockchain.getDepositAmount(depositAmount.value);
        estimatedDepositBUSD.value = parseFloat(output).toFixed(2);
      } catch (error) {
        console.error("Error calculating deposit output:", error);
        estimatedDepositBUSD.value = (
          parseFloat(depositAmount.value) * parseFloat(ethToBusdRate.value)
        ).toFixed(2);
      }
    };

    const calculateWithdrawOutput = async () => {
      if (!withdrawAmount.value || parseFloat(withdrawAmount.value) <= 0) {
        estimatedWithdrawETH.value = "0.0";
        return;
      }
      try {
        const output = await blockchain.getWithdrawalAmount(
          withdrawAmount.value,
        );
        estimatedWithdrawETH.value = parseFloat(output).toFixed(6);
      } catch (error) {
        console.error("Error calculating withdraw output:", error);
        estimatedWithdrawETH.value = (
          parseFloat(withdrawAmount.value) / parseFloat(ethToBusdRate.value)
        ).toFixed(6);
      }
    };

    const executeDeposit = async () => {
      if (!blockchain.signer) {
        toast.warning("Please connect your wallet first!");
        return;
      }

      if (isDepositing.value) {
        return; // Prevent spam clicks
      }

      const confirmed = await confirm(
        "Confirm Deposit",
        `You will deposit ${depositAmount.value} ETH and receive approximately ${estimatedDepositBUSD.value} BUSD. Your ETH will be held as collateral.`,
      );

      if (!confirmed) {
        return;
      }

      isDepositing.value = true;

      try {
        toast.info("Processing deposit... Please confirm in MetaMask");

        await blockchain.depositETH(depositAmount.value);

        toast.success(
          `Deposited ${depositAmount.value} ETH for ${estimatedDepositBUSD.value} BUSD!`,
          "Deposit Successful",
        );

        // Reset and refresh
        depositAmount.value = "";
        estimatedDepositBUSD.value = "0.0";
        showDepositModal.value = false;
        await refreshBalances();
      } catch (error) {
        console.error("Error executing deposit:", error);
        toast.txError(error, "Deposit Failed", "Deposit failed");
      } finally {
        isDepositing.value = false;
      }
    };

    const executeWithdraw = async () => {
      if (!blockchain.signer) {
        toast.warning("Please connect your wallet first!");
        return;
      }

      if (isWithdrawing.value) {
        return; // Prevent spam clicks
      }

      const confirmed = await confirm(
        "Confirm Withdrawal",
        `You will withdraw ${withdrawAmount.value} BUSD and receive approximately ${estimatedWithdrawETH.value} ETH. Your BUSD will be burned.`,
      );

      if (!confirmed) {
        return;
      }

      isWithdrawing.value = true;

      try {
        toast.info("Processing withdrawal... Please confirm in MetaMask");

        await blockchain.withdrawBUSD(withdrawAmount.value);

        toast.success(
          `Withdrew ${withdrawAmount.value} BUSD for ${estimatedWithdrawETH.value} ETH!`,
          "Withdrawal Successful",
        );

        // Reset and refresh
        withdrawAmount.value = "";
        estimatedWithdrawETH.value = "0.0";
        showWithdrawModal.value = false;
        await refreshBalances();
      } catch (error) {
        console.error("Error executing withdrawal:", error);
        toast.txError(error, "Withdrawal Failed", "Withdrawal failed");
      } finally {
        isWithdrawing.value = false;
      }
    };

    const switchAccount = async () => {
      showDropdown.value = false;
      try {
        if (blockchain.isUsingDevWallet()) {
          toast.info(
            "Dev Wallet mode uses a fixed local test account. Disable VITE_DEV_AUTO_WALLET to switch via MetaMask.",
          );
          return;
        }

        // Request accounts again - this will show MetaMask with current account
        // User needs to manually click on MetaMask extension and switch accounts
        const walletProvider = blockchain.getWalletProvider();
        if (!walletProvider) {
          toast.warning(
            "No wallet provider found. Reconnect wallet and try again.",
          );
          return;
        }

        await walletProvider.request({
          method: "wallet_requestPermissions",
          params: [{ eth_accounts: {} }],
        });

        // After permission is granted, reconnect to get new account
        await blockchain.connect();
        account.value = await blockchain.signer.getAddress();
        await updateBalance();
        console.log("Switched to account:", account.value);
      } catch (error) {
        if (error.code === 4001) {
          // User rejected the request
          console.log("Account switch cancelled by user");
        } else {
          console.error("Error switching account:", error);
          toast.txError(
            error,
            "Switch Failed",
            "Error switching account. Please try manually switching in MetaMask.",
          );
        }
      }
    };

    const copyAddress = async () => {
      showDropdown.value = false;
      try {
        await navigator.clipboard.writeText(account.value);
        toast.success("Address copied to clipboard!", "");
      } catch (error) {
        console.error("Error copying address:", error);
        // Fallback for older browsers
        const textArea = document.createElement("textarea");
        textArea.value = account.value;
        document.body.appendChild(textArea);
        textArea.select();
        document.execCommand("copy");
        document.body.removeChild(textArea);
        toast.success("Address copied to clipboard!", "");
      }
    };

    const disconnectWallet = () => {
      showDropdown.value = false;
      blockchain.disconnect();
      isConnected.value = false;
      account.value = "";
      balance.value = "0.00";
      isAdmin.value = false;
    };

    const shortAddress = (address) => {
      if (!address) return "";
      return `${address.slice(0, 6)}...${address.slice(-4)}`;
    };

    // Close dropdown when clicking outside
    const handleClickOutside = (event) => {
      if (showDropdown.value && !event.target.closest(".relative")) {
        showDropdown.value = false;
      }
    };

    // Check if already connected on page load
    onMounted(async () => {
      if (blockchain.isDevAutoWalletEnabled()) {
        try {
          await connectWallet();
        } catch (error) {
          console.error("Error auto-connecting dev wallet:", error);
        }
      }

      const walletProvider = blockchain.getWalletProvider();
      if (walletProvider && !blockchain.isDevAutoWalletEnabled()) {
        try {
          const accounts = await walletProvider.request({
            method: "eth_accounts",
          });
          if (accounts.length > 0) {
            await connectWallet();
          }
        } catch (error) {
          console.error("Error checking wallet connection:", error);
        }
      }

      // Load ETH to BUSD rate
      await loadETHToBUSDRate();

      // Add click outside listener
      document.addEventListener("click", handleClickOutside);
    });

    return {
      logo,
      isConnected,
      account,
      balance,
      busdBalance,
      formattedBusdBalance,
      stockTokenBalance,
      formattedStockBalance,
      stockSymbol,
      stockHoldings,
      showDropdown,
      isAdmin,
      isMinter,
      showSwapModal,
      swapAmount,
      swapRate,
      estimatedBUSD,
      showDepositModal,
      showWithdrawModal,
      depositAmount,
      withdrawAmount,
      ethToBusdRate,
      estimatedDepositBUSD,
      estimatedWithdrawETH,
      isDepositing,
      isWithdrawing,
      connectWallet,
      toggleDropdown,
      refreshBalances,
      mintBUSD,
      executeSwap,
      calculateDepositOutput,
      calculateWithdrawOutput,
      executeDeposit,
      executeWithdraw,
      switchAccount,
      copyAddress,
      disconnectWallet,
      shortAddress,
    };
  },
  components: {
    Toast,
    ConfirmModal,
  },
};
</script>
