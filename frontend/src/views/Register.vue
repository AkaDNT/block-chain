<template>
  <div>
    <!-- Loading State -->
    <div v-if="isLoading" class="card text-center py-12">
      <svg class="animate-spin h-12 w-12 mx-auto text-blue-600 mb-4" fill="none" viewBox="0 0 24 24">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
      </svg>
      <p class="text-gray-600">Loading company information...</p>
    </div>

    <!-- Company Details View -->
    <div v-else-if="existingCompany" class="h-100">
      <div class="grid grid-cols-12 gap-3 h-full">
        <!-- Left Column: Company Information (70%) -->
        <div class="col-span-8 space-y-3">
          <!-- Company Header -->
          <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-5">
            <div class="flex items-center justify-between mb-4">
              <div class="flex items-center gap-4">
                <div class="w-16 h-16 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-xl flex items-center justify-center">
                  <span class="text-white font-bold text-3xl">{{ existingCompany.symbol.charAt(0) }}</span>
                </div>
                <div>
                  <h1 class="text-3xl font-bold text-gray-900">{{ existingCompany.name }}</h1>
                  <p class="text-base text-gray-500">{{ existingCompany.symbol }}</p>
                </div>
              </div>
              <span
                :class="existingCompany.isVerified ? 'bg-green-100 text-green-700 border-green-300' : 'bg-yellow-100 text-yellow-700 border-yellow-300'"
                class="px-4 py-2 rounded-lg text-sm font-semibold border flex items-center gap-2"
              >
                <svg v-if="existingCompany.isVerified" class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"></path>
                </svg>
                <svg v-else class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                </svg>
                {{ existingCompany.isVerified ? 'Verified' : 'Pending Verification' }}
              </span>
            </div>

            <!-- Company Info Grid -->
            <div class="grid grid-cols-2 gap-4 pt-4 border-t border-gray-200">
              <div>
                <label class="text-sm font-medium text-gray-500">Company ID</label>
                <p class="text-base font-semibold text-gray-900 mt-1">#{{ existingCompany.id }}</p>
              </div>
              <div>
                <label class="text-sm font-medium text-gray-500">Created</label>
                <p class="text-base font-semibold text-gray-900 mt-1">{{ formatDate(existingCompany.createdAt) }}</p>
              </div>
              <div class="col-span-2">
                <label class="text-sm font-medium text-gray-500">Owner Address</label>
                <p class="text-sm font-mono text-gray-900 mt-1 bg-gray-50 px-3 py-2 rounded">{{ existingCompany.owner }}</p>
              </div>
            </div>
          </div>

          <!-- Deployment Status -->
          <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-5">
            <h2 class="text-base font-bold text-gray-900 mb-4 flex items-center gap-2">
              <svg class="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
              </svg>
              Deployment Status
            </h2>
            <div class="space-y-2">
              <!-- Stock Token -->
              <div class="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <div class="flex items-center gap-2.5">
                  <div :class="hasToken ? 'bg-green-500' : 'bg-gray-300'" class="w-2.5 h-2.5 rounded-full"></div>
                  <span class="text-sm font-medium text-gray-700">Stock Token</span>
                </div>
                <span v-if="hasToken" class="text-sm font-mono text-gray-600">{{ formatAddress(existingCompany.stockToken) }}</span>
                <span v-else class="text-sm text-gray-500">Not Deployed</span>
              </div>
              <!-- AMM Pool -->
              <div class="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <div class="flex items-center gap-2.5">
                  <div :class="hasAMM ? 'bg-green-500' : 'bg-gray-300'" class="w-2.5 h-2.5 rounded-full"></div>
                  <span class="text-sm font-medium text-gray-700">AMM Pool</span>
                </div>
                <span v-if="hasAMM" class="text-sm font-mono text-gray-600">{{ formatAddress(existingCompany.ammPool) }}</span>
                <span v-else class="text-sm text-gray-500">Not Deployed</span>
              </div>
              <!-- Liquidity -->
              <div class="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <div class="flex items-center gap-2.5">
                  <div :class="existingCompany.isInitialized ? 'bg-green-500' : 'bg-gray-300'" class="w-2.5 h-2.5 rounded-full"></div>
                  <span class="text-sm font-medium text-gray-700">Initial Liquidity</span>
                </div>
                <span :class="existingCompany.isInitialized ? 'text-green-600' : 'text-gray-500'" class="text-sm font-semibold">
                  {{ existingCompany.isInitialized ? 'Initialized' : 'Pending' }}
                </span>
              </div>
            </div>
          </div>

          <!-- IPFS Documents -->
          <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-5">
            <div class="flex items-center justify-between mb-4">
              <h2 class="text-base font-bold text-gray-900 flex items-center gap-2">
                <svg class="w-5 h-5 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z"></path>
                </svg>
                Company Documents
              </h2>
              <button
                v-if="!isEditMode"
                @click="enableEditMode"
                class="px-3 py-1.5 bg-blue-600 text-white text-xs font-semibold rounded-lg hover:bg-blue-700 transition flex items-center gap-1.5"
              >
                <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"></path>
                </svg>
                Update
              </button>
              <button
                v-else
                @click="cancelEdit"
                class="px-3 py-1.5 bg-gray-100 text-gray-700 text-xs font-semibold rounded-lg hover:bg-gray-200 transition flex items-center gap-1.5"
              >
                <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                </svg>
                Cancel
              </button>
            </div>
            <!-- Document List View -->
            <div v-if="!isEditMode" class="space-y-2">
              <div class="flex items-center justify-between p-2.5 bg-purple-50 rounded-lg border border-purple-100">
                <div class="flex items-center gap-2 flex-1 min-w-0">
                  <svg class="w-4 h-4 text-purple-600 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
                  </svg>
                  <div class="flex-1 min-w-0">
                    <p class="text-xs font-semibold text-gray-700">Prospectus</p>
                    <p class="font-mono text-xs text-gray-500 truncate">{{ existingCompany.ipfsProspectus || 'Not uploaded' }}</p>
                  </div>
                </div>
                <button
                  v-if="existingCompany.ipfsProspectus"
                  @click="viewEncryptedDocument('prospectus', existingCompany.ipfsProspectus)"
                  :disabled="viewingDoc === 'prospectus'"
                  class="ml-2 px-2 py-1 bg-purple-600 text-white text-xs rounded hover:bg-purple-700 flex-shrink-0 disabled:opacity-50"
                >
                  {{ viewingDoc === 'prospectus' ? 'Decrypting...' : 'View' }}
                </button>
              </div>
              <div class="flex items-center justify-between p-2.5 bg-indigo-50 rounded-lg border border-indigo-100">
                <div class="flex items-center gap-2 flex-1 min-w-0">
                  <svg class="w-4 h-4 text-indigo-600 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
                  </svg>
                  <div class="flex-1 min-w-0">
                    <p class="text-xs font-semibold text-gray-700">Financial Statements</p>
                    <p class="font-mono text-xs text-gray-500 truncate">{{ existingCompany.ipfsFinancials || 'Not uploaded' }}</p>
                  </div>
                </div>
                <button
                  v-if="existingCompany.ipfsFinancials"
                  @click="viewEncryptedDocument('financials', existingCompany.ipfsFinancials)"
                  :disabled="viewingDoc === 'financials'"
                  class="ml-2 px-2 py-1 bg-indigo-600 text-white text-xs rounded hover:bg-indigo-700 flex-shrink-0 disabled:opacity-50"
                >
                  {{ viewingDoc === 'financials' ? 'Decrypting...' : 'View' }}
                </button>
              </div>
              <div class="flex items-center justify-between p-2.5 bg-pink-50 rounded-lg border border-pink-100">
                <div class="flex items-center gap-2 flex-1 min-w-0">
                  <svg class="w-4 h-4 text-pink-600 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"></path>
                  </svg>
                  <div class="flex-1 min-w-0">
                    <p class="text-xs font-semibold text-gray-700">Company Logo</p>
                    <p class="font-mono text-xs text-gray-500 truncate">{{ existingCompany.ipfsLogo || 'Not uploaded' }}</p>
                  </div>
                </div>
                <button
                  v-if="existingCompany.ipfsLogo"
                  @click="viewEncryptedDocument('logo', existingCompany.ipfsLogo)"
                  :disabled="viewingDoc === 'logo'"
                  class="ml-2 px-2 py-1 bg-pink-600 text-white text-xs rounded hover:bg-pink-700 flex-shrink-0 disabled:opacity-50"
                >
                  {{ viewingDoc === 'logo' ? 'Decrypting...' : 'View' }}
                </button>
              </div>
            </div>

            <!-- Document Update Form -->
            <div v-else class="space-y-3">
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1.5">Document Type</label>
                <select v-model="editForm.documentType" class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent" required>
                  <option value="prospectus">Prospectus (PDF)</option>
                  <option value="financials">Financial Statements (PDF)</option>
                  <option value="logo">Company Logo (Image)</option>
                </select>
              </div>

              <div>
                <label class="block text-sm font-medium text-gray-700 mb-1.5">Upload New File</label>
                <input
                  @change="handleEditFileUpload"
                  type="file"
                  class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  :accept="editForm.documentType === 'logo' ? 'image/*' : '.pdf'"
                  required
                />
                <p class="text-xs text-gray-500 mt-1">
                  {{ editForm.documentType === 'logo' ? 'Upload an image file for your company logo' : 'Upload a PDF document' }}
                </p>
              </div>

              <!-- Upload Progress -->
              <div v-if="editForm.uploadStatus" class="bg-gray-50 p-3 rounded-lg">
                <div class="flex items-center justify-between mb-1.5">
                  <span class="text-sm font-semibold">{{ editForm.fileName }}</span>
                  <span
                    :class="{
                      'text-blue-600': editForm.uploadStatus === 'uploading',
                      'text-green-600': editForm.uploadStatus === 'completed',
                      'text-red-600': editForm.uploadStatus === 'error'
                    }"
                    class="text-sm"
                  >
                    {{ editForm.uploadStatus === 'uploading' ? 'Uploading...' :
                       editForm.uploadStatus === 'completed' ? '✓ Uploaded' :
                       '✗ Failed' }}
                  </span>
                </div>
                <div v-if="editForm.ipfsCid" class="text-xs font-mono text-gray-600 break-all">
                  CID: {{ editForm.ipfsCid }}
                </div>
              </div>

              <button
                @click="updateCompany"
                :disabled="isSubmitting || !editForm.ipfsCid"
                class="w-full py-2 bg-blue-600 text-white text-sm font-semibold rounded-lg hover:bg-blue-700 transition disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <span v-if="isSubmitting">Updating...</span>
                <span v-else>Update Document</span>
              </button>
            </div>
          </div>
        </div>

        <!-- Right Column: Deployment & Liquidity (30%) -->
        <div class="col-span-4 space-y-3 flex flex-col">
          <!-- Deployment Section -->
          <div v-if="existingCompany.isVerified" class="bg-white rounded-lg shadow-sm border border-gray-200 p-5 h-fit">
            <h2 class="text-base font-bold text-gray-900 mb-4 flex items-center gap-2">
              <svg class="w-5 h-5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path>
              </svg>
              Deployment
            </h2>

            <!-- Step 1: Deploy Token -->
            <div class="mb-4 pb-4 border-b border-gray-200">
              <div class="flex items-center justify-between mb-2.5">
                <div>
                  <div class="flex items-center justify-between w-full">
                    <h3 class="text-sm font-bold text-gray-900">1. Stock Token</h3>
                    <button
                      @click="redeployToken"
                      class="w-2/12 bg-white text-blue-600 text-xs font-semibold rounded-lg hover:bg-blue-50 transition"
                      :disabled="isSubmitting"
                    >
                      <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path>
                      </svg>
                    </button>
                  </div>
                  <p class="text-xs text-gray-500 mt-0.5">Deploy ERC-20 token</p>
                </div>
                <span v-if="hasToken" class="text-green-600 text-sm font-semibold flex items-center gap-1">
                  <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"></path>
                  </svg>
                  Complete
                </span>
              </div>
              <button
                v-if="!hasToken"
                @click="showTokenModal = true"
                class="w-full py-2 bg-blue-600 text-white text-xs font-semibold rounded-lg hover:bg-blue-700 transition"
              >
                Deploy Token
              </button>
              <div v-else class="space-y-1.5">
                <div class="bg-green-50 p-2 rounded-lg border border-green-200">
                  <p class="text-xs text-green-800 font-mono break-all">{{ existingCompany.stockToken }}</p>
                </div>
              </div>
            </div>

            <!-- Step 2: Deploy AMM -->
            <div class="mb-3 pb-3 border-b border-gray-200">
              <div class="flex items-center justify-between mb-2">
                <div>
                  <div class="flex items-center justify-between w-full">
                  <h3 class="text-sm font-bold text-gray-900 w-10/12">2. AMM Pool</h3>
                  <button
                    @click="redeployAMM"
                    class="w-2/12 bg-white text-blue-600 text-xs font-semibold rounded-lg hover:bg-blue-50 transition"
                    :disabled="isSubmitting"
                  >
                  <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path>
                  </svg>
                  </button>
                  </div>
                    <p class="text-xs text-gray-500 mt-0.5">Create trading pool</p>
                  </div>
                  <span v-if="hasAMM" class="text-green-600 text-xs font-semibold flex items-center gap-1">
                    <svg class="w-3.5 h-3.5" fill="currentColor" viewBox="0 0 20 20">
                      <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"></path>
                    </svg>
                    Complete
                  </span>
              </div>
              <button
                v-if="hasToken && !hasAMM"
                @click="showAMMModal = true"
                class="w-full py-2 bg-blue-600 text-white text-xs font-semibold rounded-lg hover:bg-blue-700 transition"
              >
                Deploy AMM
              </button>
              <button v-else-if="!hasToken" disabled class="w-full py-2 bg-gray-300 text-gray-500 text-xs font-semibold rounded-lg cursor-not-allowed">
                Deploy Token First
              </button>
              <div v-else class="space-y-1.5">
                <div class="bg-green-50 p-2 rounded-lg border border-green-200">
                  <p class="text-xs text-green-800 font-mono break-all">{{ existingCompany.ammPool }}</p>
                </div>
              </div>
            </div>

            <!-- Step 3: Initialize Pool -->
            <div>
              <div class="flex items-center justify-between mb-2">
                <div>
                  <h3 class="text-xs font-bold text-gray-900">3. Initial Liquidity</h3>
                  <p class="text-xs text-gray-500 mt-0.5">Set starting price</p>
                </div>
                <span v-if="existingCompany.isInitialized" class="text-green-600 text-xs font-semibold flex items-center gap-1">
                  <svg class="w-3.5 h-3.5" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"></path>
                  </svg>
                  Complete
                </span>
              </div>
              <button
                v-if="hasToken && hasAMM && !existingCompany.isInitialized"
                @click="showLiquidityModal = true"
                class="w-full py-2 bg-green-600 text-white text-xs font-semibold rounded-lg hover:bg-green-700 transition"
              >
                Add Liquidity
              </button>
              <button v-else-if="!hasAMM" disabled class="w-full py-2 bg-gray-300 text-gray-500 text-xs font-semibold rounded-lg cursor-not-allowed">
                Deploy AMM First
              </button>
              <div v-else-if="existingCompany.isInitialized" class="bg-green-50 p-2.5 rounded-lg border border-green-200">
                <p class="text-xs text-green-800 font-semibold flex items-center gap-1.5">
                  <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"></path>
                  </svg>
                  Ready for Trading!
                </p>
              </div>
            </div>
          </div>

          <!-- Recent Trades Section -->
          <div v-if="existingCompany.isInitialized" class="bg-white rounded-lg shadow-sm border border-gray-200 p-4 h-1/2">
            <h2 class="text-sm font-bold text-gray-900 mb-3 flex items-center gap-2">
              <svg class="w-4 h-4 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path>
              </svg>
              Recent Trades
            </h2>
            <div class="space-y-2">
              <div v-if="recentTrades.length === 0" class="text-center py-4">
                <div class="w-10 h-10 bg-gray-100 rounded-lg flex items-center justify-center mx-auto mb-2">
                  <svg class="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"></path>
                  </svg>
                </div>
                <p class="text-xs text-gray-500">No trades yet</p>
              </div>
              <div v-else>
                <div
                  v-for="trade in recentTrades.slice(0, 5)"
                  :key="trade.id"
                  class="flex items-center justify-between p-2 bg-gray-50 rounded-lg hover:bg-gray-100 transition"
                >
                  <div class="flex items-center gap-2">
                    <div :class="trade.type === 'buy' ? 'bg-green-500' : 'bg-red-500'" class="w-5 h-5 rounded flex items-center justify-center text-white text-xs font-bold">
                      {{ trade.type === 'buy' ? '↑' : '↓' }}
                    </div>
                    <div>
                      <p class="text-xs font-semibold text-gray-900">{{ trade.quantity.toFixed(2) }} {{ existingCompany.symbol }}</p>
                      <p class="text-xs text-gray-500">{{ formatTradeTime(trade.timestamp) }}</p>
                    </div>
                  </div>
                  <div class="text-right">
                    <p class="text-xs font-semibold text-gray-900">{{ trade.amount.toFixed(2) }} BUSD</p>
                    <p :class="trade.type === 'buy' ? 'text-green-600' : 'text-red-600'" class="text-xs font-semibold">
                      {{ trade.type.toUpperCase() }}
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Waiting for Verification -->
          <div v-else class="bg-yellow-50 rounded-lg shadow-sm border border-yellow-200 p-4">
            <div class="flex items-start gap-2">
              <svg class="w-5 h-5 text-yellow-600 flex-shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <div>
                <h3 class="text-sm font-bold text-yellow-900 mb-1">Awaiting Verification</h3>
                <p class="text-xs text-yellow-800">
                  Your company is pending admin verification. Once verified, you'll be able to deploy your stock token and AMM pool.
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Registration Form (shown when no existing company) -->
    <div v-else class="card">
      <h1 class="text-3xl font-bold text-center mb-8">Register Your Company</h1>

      <form @submit.prevent="registerCompany" class="space-y-6">
        <!-- Company Information -->
        <div>
          <h2 class="text-xl font-semibold mb-4">Company Information</h2>

          <div class="grid md:grid-cols-2 gap-4">
            <div>
              <label class="label">Company Name</label>
              <input
                v-model="form.companyName"
                type="text"
                class="input-field"
                placeholder="e.g., Apple Inc"
                required
              />
            </div>

            <div>
              <label class="label">Stock Symbol</label>
              <input
                v-model="form.symbol"
                type="text"
                class="input-field"
                placeholder="e.g., AAPL"
                maxlength="10"
                required
              />
            </div>
          </div>

          <div>
            <label class="label">Description</label>
            <textarea
              v-model="form.description"
              class="input-field"
              rows="3"
              placeholder="Brief description of your company..."
              required
            ></textarea>
          </div>
        </div>

        <!-- Token Information -->
        <div>
          <h2 class="text-xl font-semibold mb-4">Token Information</h2>

          <div class="grid md:grid-cols-2 gap-4">
            <div>
              <label class="label">Token Name</label>
              <input
                v-model="form.tokenName"
                type="text"
                class="input-field"
                placeholder="e.g., Apple Inc Stock"
                required
              />
            </div>

            <div>
              <label class="label">Total Supply</label>
              <input
                v-model="form.totalSupply"
                type="number"
                class="input-field"
                placeholder="e.g., 1000000"
                min="1"
                required
              />
            </div>
          </div>
        </div>

        <!-- Document Upload -->
        <div>
          <h2 class="text-xl font-semibold mb-4">Company Documents</h2>

          <div class="space-y-4">
            <div>
              <label class="label">Company Prospectus (PDF)</label>
              <input
                @change="handleFileUpload($event, 'prospectus')"
                type="file"
                class="input-field"
                accept=".pdf"
                required
              />
              <p class="text-sm text-gray-500 mt-1">Upload your company prospectus or business plan</p>
            </div>

            <div>
              <label class="label">Financial Statements (PDF)</label>
              <input
                @change="handleFileUpload($event, 'financials')"
                type="file"
                class="input-field"
                accept=".pdf"
              />
              <p class="text-sm text-gray-500 mt-1">Optional: Latest financial statements</p>
            </div>

            <div>
              <label class="label">Company Logo (Image)</label>
              <input
                @change="handleFileUpload($event, 'logo')"
                type="file"
                class="input-field"
                accept="image/*"
              />
              <p class="text-sm text-gray-500 mt-1">Optional: Company logo for display</p>
            </div>
          </div>
        </div>
        <!-- Upload Progress -->
        <div v-if="uploadProgress.length > 0" class="space-y-2">
          <h3 class="font-semibold">Upload Progress</h3>
          <div
            v-for="(upload, index) in uploadProgress"
            :key="`${upload.name}-${index}`"
            class="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
          >
            <div class="flex-1">
              <span class="text-sm font-medium">{{ upload.name }}</span>
              <div v-if="upload.type" class="text-xs text-gray-500 capitalize">{{ upload.type }}</div>
            </div>
            <div class="flex items-center space-x-2">
              <div v-if="upload.status === 'uploading'" class="text-blue-600 flex items-center space-x-1">
                <svg class="animate-spin h-4 w-4" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                <span class="text-xs">Uploading...</span>
              </div>
              <div v-else-if="upload.status === 'completed'" class="text-green-600 flex items-center space-x-1">
                <svg class="h-4 w-4" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"></path>
                </svg>
                <span class="text-xs font-mono">{{ upload.cid }}</span>
              </div>
              <div v-else-if="upload.status === 'error'" class="text-red-600 flex items-center space-x-1">
                <svg class="h-4 w-4" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd"></path>
                </svg>
                <span class="text-xs">{{ upload.error }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Submit Button -->
        <div class="pt-6">
          <button
            type="submit"
            :disabled="isSubmitting || !canSubmit"
            class="w-full btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <span v-if="isSubmitting" class="flex items-center justify-center">
              <svg class="animate-spin -ml-1 mr-3 h-5 w-5 text-white" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              Registering Company...
            </span>
            <span v-else>Register Company</span>
          </button>
        </div>
      </form>
    </div>

    <!-- Deploy Token Modal -->
    <div v-if="showTokenModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg p-6 max-w-md w-full mx-4">
        <h3 class="text-xl font-bold mb-4">Deploy Stock Token</h3>

        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium mb-1">Token Name</label>
            <input
              v-model="tokenForm.name"
              type="text"
              class="w-full px-3 py-2 border rounded-lg"
              placeholder="e.g., HVYCOM Token"
            />
          </div>

          <div>
            <label class="block text-sm font-medium mb-1">Token Symbol</label>
            <input
              v-model="tokenForm.symbol"
              type="text"
              class="w-full px-3 py-2 border rounded-lg"
              placeholder="e.g., HVC"
            />
          </div>

          <div>
            <label class="block text-sm font-medium mb-1">Total Supply</label>
            <input
              v-model="tokenForm.totalSupply"
              type="number"
              class="w-full px-3 py-2 border rounded-lg"
              placeholder="e.g., 1000000"
            />
          </div>

          <div>
            <label class="block text-sm font-medium mb-1">Decimals</label>
            <input
              v-model="tokenForm.decimals"
              type="number"
              class="w-full px-3 py-2 border rounded-lg"
              value="18"
              disabled
            />
            <p class="text-xs text-gray-500 mt-1">Standard ERC-20 decimals (18)</p>
          </div>
        </div>

        <div class="flex gap-3 mt-6">
          <button
            @click="showTokenModal = false"
            :disabled="isSubmitting"
            class="flex-1 px-4 py-2 bg-gray-200 text-gray-800 rounded-lg font-semibold hover:bg-gray-300"
          >
            Cancel
          </button>
          <button
            @click="deployToken"
            :disabled="isSubmitting || !tokenForm.name || !tokenForm.symbol || !tokenForm.totalSupply"
            class="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg font-semibold hover:bg-blue-700 disabled:opacity-50"
          >
            <span v-if="isSubmitting">Deploying...</span>
            <span v-else>Deploy Token</span>
          </button>
        </div>
      </div>
    </div>

    <!-- Deploy AMM Modal -->
    <div v-if="showAMMModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg p-6 max-w-md w-full mx-4">
        <h3 class="text-xl font-bold mb-4">Deploy AMM Pool</h3>

        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium mb-1">Trading Fee (%)</label>
            <input
              v-model="ammForm.feeRate"
              type="number"
              step="0.1"
              class="w-full px-3 py-2 border rounded-lg"
              placeholder="0.3"
            />
            <p class="text-xs text-gray-500 mt-1">Recommended: 0.3% (30 basis points)</p>
          </div>

          <div class="bg-blue-50 p-3 rounded-lg">
            <p class="text-sm text-blue-800">
              <strong>Note:</strong> This creates your AMM pool contract. You'll add liquidity in the next step.
            </p>
          </div>
        </div>

        <div class="flex gap-3 mt-6">
          <button
            @click="showAMMModal = false"
            :disabled="isSubmitting"
            class="flex-1 px-4 py-2 bg-gray-200 text-gray-800 rounded-lg font-semibold hover:bg-gray-300"
          >
            Cancel
          </button>
          <button
            @click="deployAMM"
            :disabled="isSubmitting"
            class="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg font-semibold hover:bg-blue-700 disabled:opacity-50"
          >
            <span v-if="isSubmitting">Deploying...</span>
            <span v-else>Deploy AMM</span>
          </button>
        </div>
      </div>
    </div>

    <!-- Initialize Liquidity Modal -->
    <div v-if="showLiquidityModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg p-6 max-w-md w-full mx-4">
        <h3 class="text-xl font-bold mb-4">Add Initial Liquidity</h3>

        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium mb-1">Stock Tokens ({{ existingCompany.symbol }})</label>
            <input
              v-model="liquidityForm.stockAmount"
              type="number"
              class="w-full px-3 py-2 border rounded-lg"
              placeholder="e.g., 100000"
            />
          </div>

          <div>
            <label class="block text-sm font-medium mb-1">Base Tokens (BUSD)</label>
            <input
              v-model="liquidityForm.baseAmount"
              type="number"
              class="w-full px-3 py-2 border rounded-lg"
              placeholder="e.g., 1000000"
            />
          </div>

          <div v-if="liquidityForm.stockAmount && liquidityForm.baseAmount" class="bg-green-50 p-3 rounded-lg">
            <p class="text-sm text-green-800">
              <strong>Initial Price:</strong> {{ initialPrice }} BUSD per {{ existingCompany.symbol }}
            </p>
          </div>

          <div class="bg-yellow-50 p-3 rounded-lg">
            <p class="text-sm text-yellow-800">
              <strong>Warning:</strong> Make sure you have enough tokens in your wallet before proceeding.
            </p>
          </div>
        </div>

        <div class="flex gap-3 mt-6">
          <button
            @click="showLiquidityModal = false"
            :disabled="isSubmitting"
            class="flex-1 px-4 py-2 bg-gray-200 text-gray-800 rounded-lg font-semibold hover:bg-gray-300"
          >
            Cancel
          </button>
          <button
            @click="initializeLiquidity"
            :disabled="isSubmitting || !liquidityForm.stockAmount || !liquidityForm.baseAmount"
            class="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg font-semibold hover:bg-blue-700 disabled:opacity-50"
          >
            <span v-if="isSubmitting">Processing...</span>
            <span v-else>Add Liquidity</span>
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
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { ethers } from 'ethers'
import blockchain from '../utils/blockchain.js'
import { uploadToIPFS } from '../utils/ipfs.js'
import { uploadEncryptedToIPFS, downloadAndDecryptFromIPFS } from '../utils/encryptedIPFS.js'
import { getPublicKeyFromSigner } from '../utils/encryption.js'
import { getOrPromptKey, getPublicKey, getKeyAddress } from '../utils/keyManager.js'
import toast from '../utils/toast.js'
import { confirmWarning, confirm } from '../utils/confirm.js'
import { deployStockToken, deployStockAMM } from '../utils/contractDeployer.js'

export default {
  name: 'Register',
  setup() {
    const form = ref({
      companyName: '',
      symbol: '',
      description: '',
      tokenName: '',
      totalSupply: ''
    })

    const uploadProgress = ref([])
    const isSubmitting = ref(false)
    const uploadedFiles = ref({})
    const isLoading = ref(true)
    const existingCompany = ref(null)
    const isEditMode = ref(false)
    const editForm = ref({
      documentType: 'prospectus',
      ipfsCid: '',
      fileName: '',
      uploadStatus: null,
      encryptedKeys: null,
      metadata: null
    })

    // Document viewing state
    const viewingDoc = ref(null)
    const showPreviewModal = ref(false)
    const documentPreview = ref(null)

    // Deployment state
    const showTokenModal = ref(false)
    const showAMMModal = ref(false)
    const showLiquidityModal = ref(false)

    const tokenForm = ref({
      name: '',
      symbol: '',
      totalSupply: '1000000',
      decimals: 18
    })

    const ammForm = ref({
      feeRate: 30 // 0.3% in basis points
    })

    const liquidityForm = ref({
      stockAmount: '',
      baseAmount: ''
    })

    const tokenBalance = ref('0')
    const busdBalance = ref('0')
    const recentTrades = ref([])

    const hasToken = computed(() => {
      return existingCompany.value?.stockToken && existingCompany.value.stockToken !== '0x0000000000000000000000000000000000000000'
    })

    const hasAMM = computed(() => {
      return existingCompany.value?.ammPool && existingCompany.value.ammPool !== '0x0000000000000000000000000000000000000000'
    })

    const initialPrice = computed(() => {
      if (!liquidityForm.value.stockAmount || !liquidityForm.value.baseAmount) return '0'
      return (parseFloat(liquidityForm.value.baseAmount) / parseFloat(liquidityForm.value.stockAmount)).toFixed(2)
    })

    const canSubmit = computed(() => {
      return form.value.companyName &&
             form.value.symbol &&
             form.value.description &&
             form.value.tokenName &&
             form.value.totalSupply &&
             uploadedFiles.value.prospectus
    })

    const handleFileUpload = async (event, type) => {
      const file = event.target.files[0]
      if (!file) return

      // Add upload item to progress array
      const uploadIndex = uploadProgress.value.length
      uploadProgress.value.push({
        name: file.name,
        type: type,
        status: 'uploading',
        cid: null,
        error: null
      })

      try {
        if (type === 'logo') {
          const { uploadToIPFS } = await import('../utils/ipfs.js')
          const cid = await uploadToIPFS(file)

          uploadProgress.value[uploadIndex] = {
            ...uploadProgress.value[uploadIndex],
            status: 'completed',
            cid: cid
          }

          uploadedFiles.value[type] = {
            file: file,
            cid: cid,
            encryptedKeys: null, // No encryption for logo
            metadata: null
          }

          return
        }

        const globalPublicKey = getPublicKey()
        const globalAddress = getKeyAddress()

        if (!globalPublicKey || !globalAddress) {
          throw new Error('Encryption key not configured. Set VITE_ENCRYPTION_KEY in .env')
        }

        const recipients = [{ address: globalAddress, publicKey: globalPublicKey }]

        // Upload encrypted to IPFS
        console.log(`🔐 Encrypting and uploading ${type}...`)
        const { cid, encryptedKeys, metadata } = await uploadEncryptedToIPFS(file, recipients)

        // Update the specific item in the array to trigger reactivity
        uploadProgress.value[uploadIndex] = {
          ...uploadProgress.value[uploadIndex],
          status: 'completed',
          cid: cid
        }

        uploadedFiles.value[type] = {
          file: file,
          cid: cid,
          encryptedKeys: encryptedKeys,
          metadata: metadata
        }

        console.log(`✅ Encrypted and uploaded ${type}:`, cid)

      } catch (error) {
        // Update the specific item in the array to trigger reactivity
        uploadProgress.value[uploadIndex] = {
          ...uploadProgress.value[uploadIndex],
          status: 'error',
          error: error.message
        }
        console.error(`Error uploading ${type}:`, error)
      }
    }

    const checkExistingCompany = async () => {
      try {
        if (!blockchain.signer) {
          isLoading.value = false
          return
        }

        const address = await blockchain.signer.getAddress()
        const company = await blockchain.getCompanyByOwner(address)

        if (company) {
          existingCompany.value = company
        }
      } catch (error) {
        // Expected error when no company is registered - this is normal
        if (error.message?.includes('Company not found')) {
          console.log('✓ No existing company - ready to register')
        } else {
          console.error('Error checking company:', error)
        }
      } finally {
        isLoading.value = false
      }
    }

    const registerCompany = async () => {
      if (!canSubmit.value) return

      isSubmitting.value = true

      try {
        // Check if wallet is connected
        if (!blockchain.signer) {
          toast.warning('Please connect your wallet first!')
          isSubmitting.value = false
          return
        }

        // Create metadata object
        const metadata = {
          company: {
            name: form.value.companyName,
            symbol: form.value.symbol,
            description: form.value.description
          },
          token: {
            name: form.value.tokenName,
            symbol: form.value.symbol,
            totalSupply: form.value.totalSupply
          },
          documents: {
            prospectus: uploadedFiles.value.prospectus?.cid,
            financials: uploadedFiles.value.financials?.cid,
            logo: uploadedFiles.value.logo?.cid
          },
          timestamp: new Date().toISOString()
        }

        // Upload metadata to IPFS
        console.log('Uploading metadata to IPFS...')
        // For now, use a mock CID - in production, this would upload to IPFS
        const metadataCid = uploadedFiles.value.prospectus?.cid || `QmMeta${Math.random().toString(36).substring(2, 15)}`

        // Register company in the Registry contract
        console.log('Registering company in registry...')
        const companyId = await blockchain.registerCompany(
          form.value.companyName,
          form.value.symbol,
          uploadedFiles.value.prospectus?.cid || '',
          uploadedFiles.value.financials?.cid || '',
          uploadedFiles.value.logo?.cid || ''
        )

        console.log('Company registered with ID:', companyId)

        // Register encrypted documents on-chain with EncryptedDocRegistry
        console.log('Registering encrypted documents on-chain...')
        const docTypes = ['prospectus', 'financials', 'logo']
        for (const docType of docTypes) {
          const uploaded = uploadedFiles.value[docType]
          if (uploaded?.cid && uploaded?.encryptedKeys) {
            try {
              // Register document in EncryptedDocRegistry
              const docId = await blockchain.uploadEncryptedDocument(
                uploaded.cid,
                docType,
                uploaded.metadata?.originalName || uploaded.file.name,
                uploaded.metadata?.originalSize || uploaded.file.size,
                companyId
              )

              // Add encrypted key for the uploader
              if (uploaded.encryptedKeys.length > 0) {
                for (const keyData of uploaded.encryptedKeys) {
                  await blockchain.addDocumentRecipient(docId, keyData.recipient, keyData.encryptedKey)
                }
              }

              console.log(`✅ Registered encrypted ${docType} with doc ID: ${docId}`)
            } catch (err) {
              console.warn(`Could not register ${docType} in EncryptedDocRegistry:`, err)
            }
          }
        }

        toast.success(
          `Company ID: ${companyId}. Documents are encrypted and stored securely. An admin needs to deploy the StockToken and AMM contracts before trading can begin.`,
          'Company Registered!'
        )

        // Reload to show company details
        await checkExistingCompany()

      } catch (error) {
        console.error('Error registering company:', error)
        toast.txError(error, 'Registration Failed', 'Failed to register company')
      } finally {
        isSubmitting.value = false
      }
    }

    const handleEditFileUpload = async (event) => {
      const file = event.target.files[0]
      if (!file) return

      editForm.value.fileName = file.name
      editForm.value.uploadStatus = 'uploading'
      editForm.value.ipfsCid = ''
      editForm.value.encryptedKeys = null

      try {
        if (editForm.value.documentType === 'logo') {
          const { uploadToIPFS } = await import('../utils/ipfs.js')
          const cid = await uploadToIPFS(file)

          editForm.value.uploadStatus = 'completed'
          editForm.value.ipfsCid = cid

          uploadedFiles.value[editForm.value.documentType] = {
            file: file,
            cid: cid,
            encryptedKeys: null, // No encryption for logo
            metadata: null
          }

          return
        }
        // Use global encryption key from environment
        const globalPublicKey = getPublicKey()
        const globalAddress = getKeyAddress()

        if (!globalPublicKey || !globalAddress) {
          throw new Error('Encryption key not configured. Set VITE_ENCRYPTION_KEY in .env')
        }

        const recipients = [{ address: globalAddress, publicKey: globalPublicKey }]

        // Upload encrypted to IPFS
        console.log(`🔐 Encrypting and uploading ${editForm.value.documentType}...`)
        const { cid, encryptedKeys, metadata } = await uploadEncryptedToIPFS(file, recipients)

        editForm.value.uploadStatus = 'completed'
        editForm.value.ipfsCid = cid
        editForm.value.encryptedKeys = encryptedKeys
        editForm.value.metadata = metadata
      } catch (error) {
        editForm.value.uploadStatus = 'error'
        console.error(`Error uploading ${editForm.value.documentType}:`, error)
      }
    }

    const enableEditMode = () => {
      isEditMode.value = true
      editForm.value.documentType = 'prospectus'
      editForm.value.ipfsCid = ''
      editForm.value.fileName = ''
      editForm.value.uploadStatus = null
    }

    const cancelEdit = () => {
      isEditMode.value = false
      editForm.value.documentType = 'prospectus'
      editForm.value.ipfsCid = ''
      editForm.value.fileName = ''
      editForm.value.uploadStatus = null
    }

    const updateCompany = async () => {
      if (!editForm.value.ipfsCid) return
      isSubmitting.value = true

      try {
        if (!blockchain.signer) {
          toast.warning('Please connect your wallet first!')
          return
        }

        const registry = blockchain.getRegistry()
        let tx

        toast.txStep(`Update ${editForm.value.documentType}`, `Updating ${editForm.value.documentType} document on-chain`)

        // Call the appropriate update function based on document type
        if (editForm.value.documentType === 'prospectus') {
          tx = await registry.update_ipfs_prospectus(
            existingCompany.value.id,
            editForm.value.ipfsCid
          )
        } else if (editForm.value.documentType === 'financials') {
          tx = await registry.update_ipfs_financials(
            existingCompany.value.id,
            editForm.value.ipfsCid
          )
        } else if (editForm.value.documentType === 'logo') {
          tx = await registry.update_ipfs_logo(
            existingCompany.value.id,
            editForm.value.ipfsCid
          )
        }

        toast.txPending(`Updating ${editForm.value.documentType}`)
        await tx.wait()
        toast.txConfirmed('Document updated')

        // Also register the encrypted document in EncryptedDocRegistry
        if (editForm.value.encryptedKeys && editForm.value.encryptedKeys.length > 0) {
          try {
            const docId = await blockchain.uploadEncryptedDocument(
              editForm.value.ipfsCid,
              editForm.value.documentType,
              editForm.value.metadata?.originalName || editForm.value.fileName,
              editForm.value.metadata?.originalSize || 0,
              existingCompany.value.id
            )

            for (const keyData of editForm.value.encryptedKeys) {
              await blockchain.addDocumentRecipient(docId, keyData.recipient, keyData.encryptedKey)
            }

            console.log(`✅ Registered encrypted ${editForm.value.documentType} with doc ID: ${docId}`)
          } catch (err) {
            console.warn('Could not register in EncryptedDocRegistry:', err)
          }
        }

        toast.success('Your company document has been updated and encrypted.', 'Update Successful!')

        // Reload company data
        await checkExistingCompany()
        isEditMode.value = false

      } catch (error) {
        console.error('Error updating company:', error)
        toast.txError(error, 'Update Failed', 'Failed to update company')
      } finally {
        isSubmitting.value = false
      }
    }

    const removeCompany = async () => {
      const confirmed = await confirmWarning(
        `This will permanently delete ${existingCompany.value.name} from the registry. This action cannot be undone.`,
        'Remove Company?',
        'WARNING: This is for development/testing only. In production, companies should not be deletable for audit trail purposes.'
      )

      if (!confirmed) return

      isSubmitting.value = true

      try {
        if (!blockchain.signer) {
          toast.warning('Please connect your wallet first!')
          return
        }

        const registry = blockchain.getRegistry()

        toast.txStep('Remove Company', `Removing ${existingCompany.value.name} from registry`)
        const tx = await registry.remove_company(existingCompany.value.id)

        toast.txPending('Removing company')
        await tx.wait()

        toast.txConfirmed('Company removed', 'Company has been removed from the registry')

        // Reload page to show registration form
        existingCompany.value = null
        await checkExistingCompany()

      } catch (error) {
        console.error('Error removing company:', error)
        toast.txError(error, 'Removal Failed', 'Failed to remove company')
      } finally {
        isSubmitting.value = false
      }
    }

    const formatDate = (date) => {
      if (!date) return 'N/A'
      return new Date(date).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
      })
    }

    const formatAddress = (address) => {
      if (!address) return ''
      return `${address.slice(0, 6)}...${address.slice(-4)}`
    }

    const formatTradeTime = (timestamp) => {
      const now = new Date()
      const tradeTime = new Date(timestamp)
      const diffMs = now - tradeTime
      const diffMins = Math.floor(diffMs / 60000)
      const diffHours = Math.floor(diffMs / 3600000)
      const diffDays = Math.floor(diffMs / 86400000)

      if (diffMins < 1) return 'Just now'
      if (diffMins < 60) return `${diffMins}m ago`
      if (diffHours < 24) return `${diffHours}h ago`
      if (diffDays < 7) return `${diffDays}d ago`
      return tradeTime.toLocaleDateString()
    }

    const refreshBalance = async () => {
      if (!blockchain.signer) return

      try {
        const account = await blockchain.signer.getAddress()

        // Get stock token balance if deployed
        if (hasToken.value) {
          const balance = await blockchain.getTokenBalance(
            existingCompany.value.stockToken,
            account
          )
          tokenBalance.value = parseFloat(balance).toLocaleString()
        }

        // Get BUSD balance
        const busd = await blockchain.getBaseTokenBalance(account)
        busdBalance.value = parseFloat(busd).toLocaleString()
      } catch (error) {
        console.error('Error refreshing balance:', error)
      }
    }

    const loadRecentTrades = async () => {
      if (!existingCompany.value?.ammPool || !existingCompany.value?.isInitialized) {
        recentTrades.value = []
        return
      }

      try {
        console.log('📊 Loading recent trades for company AMM:', existingCompany.value.ammPool)

        // Fetch trades from blockchain (all trades for this AMM pool)
        const trades = await blockchain.getRecentTrades(existingCompany.value.ammPool, null, 10)

        // Map to the format expected by the template
        recentTrades.value = trades.map(trade => ({
          id: trade.id,
          type: trade.type,
          quantity: parseFloat(trade.type === 'buy' ? trade.amountOut : trade.amountIn),
          amount: parseFloat(trade.type === 'buy' ? trade.amountIn : trade.amountOut),
          timestamp: trade.timestamp
        }))

        console.log('📊 Loaded trades:', recentTrades.value)
      } catch (error) {
        console.error('Error loading recent trades:', error)
        recentTrades.value = []
      }
    }

    const mintBUSD = async () => {
      const confirmed = await confirm({
        title: 'Mint Test BUSD',
        message: 'Mint 10,000 BUSD tokens for testing?',
        details: 'This is a test token for development. In production, you would need real BUSD.',
        type: 'info',
        confirmText: 'Mint',
        cancelText: 'Cancel'
      })

      if (!confirmed) return
      isSubmitting.value = true

      try {
        const baseToken = blockchain.getBaseToken()
        const account = await blockchain.signer.getAddress()

        // Mint 10,000 BUSD (with 18 decimals)
        const amount = ethers.parseUnits('10000', 18)

        toast.info('Minting BUSD... Please confirm in MetaMask')
        const tx = await baseToken.mint(account, amount)
        await tx.wait()

        toast.success('10,000 BUSD minted successfully!', 'BUSD Minted')
        await refreshBalance()
      } catch (error) {
        console.error('Error minting BUSD:', error)
        toast.txError(error, 'Mint Failed', 'Failed to mint BUSD')
      } finally {
        isSubmitting.value = false
      }
    }

    const deployToken = async () => {
      const confirmed = await confirm({
        title: 'Deploy Stock Token',
        message: `Deploy ${tokenForm.value.name} (${tokenForm.value.symbol})?`,
        details: `Total Supply: ${tokenForm.value.totalSupply} tokens`,
        type: 'info',
        confirmText: 'Deploy',
        cancelText: 'Cancel'
      })

      if (!confirmed) return
      isSubmitting.value = true

      try {
        toast.txStep('Deploy Stock Token', `Deploying ${tokenForm.value.name} (${tokenForm.value.symbol}) with ${tokenForm.value.totalSupply} tokens`)
        const tokenAddress = await deployStockToken(blockchain.signer, {
          name: tokenForm.value.name,
          symbol: tokenForm.value.symbol,
          decimals: tokenForm.value.decimals,
          totalSupply: tokenForm.value.totalSupply,
          companyName: existingCompany.value.name,
          ipfsCid: existingCompany.value.ipfsProspectus || 'QmDefault'
        })

        toast.txConfirmed('Token deployed', `Address: ${tokenAddress.slice(0, 10)}...`)

        toast.txStep('Register Token', 'Linking token to your company in the registry')
        const registry = blockchain.getRegistry()
        const tx = await registry.set_stock_token(existingCompany.value.id, tokenAddress)

        toast.txPending('Registering token')
        await tx.wait()
        toast.txConfirmed('Token registered', 'Your stock token is now linked to your company')

        showTokenModal.value = false
        await checkExistingCompany()
        await refreshBalance()
      } catch (error) {
        console.error('Error deploying token:', error)
        toast.txError(error, 'Deployment Failed', 'Failed to deploy token')
      } finally {
        isSubmitting.value = false
      }
    }

    const redeployToken = async () => {
      const confirmed = await confirm({
        title: 'Redeploy Stock Token',
        message: `This will deploy a NEW token contract and replace the old one.`,
        details: `⚠️ WARNING: The old token at ${existingCompany.value.stockToken} will still exist but won't be linked to your company. Make sure you haven't distributed tokens yet!`,
        type: 'warning',
        confirmText: 'Redeploy',
        cancelText: 'Cancel'
      })

      if (!confirmed) return

      // Open token modal with pre-filled data
      showTokenModal.value = true
    }

    const deployAMM = async () => {
      const confirmed = await confirm({
        title: 'Deploy AMM Pool',
        message: 'Create your AMM pool for trading?',
        details: `Fee: ${ammForm.value.feeRate / 100}%`,
        type: 'info',
        confirmText: 'Deploy',
        cancelText: 'Cancel'
      })

      if (!confirmed) return
      isSubmitting.value = true

      try {
        toast.txStep('Deploy AMM Pool', `Creating trading pool with ${ammForm.value.feeRate / 100}% fee`)
        const ammAddress = await deployStockAMM(blockchain.signer, ammForm.value.feeRate)
        toast.txConfirmed('AMM deployed', `Address: ${ammAddress.slice(0, 10)}...`)

        toast.txStep('Register AMM', 'Linking AMM pool to your company')
        const registry = blockchain.getRegistry()
        const tx = await registry.set_amm_pool(existingCompany.value.id, ammAddress)

        toast.txPending('Registering AMM')
        await tx.wait()
        toast.txConfirmed('AMM registered', 'Your trading pool is ready')

        showAMMModal.value = false
        await checkExistingCompany()
      } catch (error) {
        console.error('Error deploying AMM:', error)
        toast.txError(error, 'Deployment Failed', 'Failed to deploy AMM')
      } finally {
        isSubmitting.value = false
      }
    }

    const redeployAMM = async () => {
      const confirmed = await confirm({
        title: 'Redeploy AMM Pool',
        message: `This will deploy a NEW AMM pool and replace the old one.`,
        details: `⚠️ WARNING: The old AMM at ${existingCompany.value.ammPool} will still exist. If it has liquidity, you'll need to remove it first. This is for fixing deployment issues.`,
        type: 'warning',
        confirmText: 'Redeploy',
        cancelText: 'Cancel'
      })

      if (!confirmed) return

      // Open AMM modal
      showAMMModal.value = true
    }

    const initializeLiquidity = async () => {
      const confirmed = await confirm({
        title: 'Add Initial Liquidity',
        message: `Add ${liquidityForm.value.stockAmount} ${existingCompany.value.symbol} and ${liquidityForm.value.baseAmount} BUSD?`,
        details: `Initial price: ${initialPrice.value} BUSD per ${existingCompany.value.symbol}`,
        type: 'warning',
        confirmText: 'Add Liquidity',
        cancelText: 'Cancel'
      })

      if (!confirmed) return
      isSubmitting.value = true

      try {
        const stockToken = blockchain.getStockToken(existingCompany.value.stockToken)
        const baseToken = blockchain.getBaseToken()
        const amm = blockchain.getAMM(existingCompany.value.ammPool)

        // Get decimals for proper conversion
        const stockDecimals = await stockToken.decimals()
        const baseDecimals = await baseToken.decimals()

        // Convert amounts to wei format
        const stockAmountWei = ethers.parseUnits(liquidityForm.value.stockAmount.toString(), stockDecimals)
        const baseAmountWei = ethers.parseUnits(liquidityForm.value.baseAmount.toString(), baseDecimals)

        toast.txStep('Approve Stock Tokens', `Allow AMM to use ${liquidityForm.value.stockAmount} ${existingCompany.value.symbol}`)
        let tx = await stockToken.approve(existingCompany.value.ammPool, stockAmountWei)
        toast.txPending('Approving stock tokens')
        await tx.wait()
        toast.txConfirmed('Stock tokens approved')

        toast.txStep('Approve BUSD', `Allow AMM to use ${liquidityForm.value.baseAmount} BUSD`)
        tx = await baseToken.approve(existingCompany.value.ammPool, baseAmountWei)
        toast.txPending('Approving BUSD')
        await tx.wait()
        toast.txConfirmed('BUSD approved')

        toast.txStep('Initialize Pool', `Add ${liquidityForm.value.stockAmount} ${existingCompany.value.symbol} + ${liquidityForm.value.baseAmount} BUSD`)
        tx = await amm.init_pool(
          existingCompany.value.stockToken,
          await baseToken.getAddress(),
          stockAmountWei,
          baseAmountWei
        )
        toast.txPending('Initializing pool')
        await tx.wait()

        toast.txConfirmed(
          'Pool initialized!',
          `Price: ${initialPrice.value} BUSD per ${existingCompany.value.symbol}`
        )

        showLiquidityModal.value = false
        await checkExistingCompany()
      } catch (error) {
        console.error('Error initializing liquidity:', error)
        toast.txError(error, 'Initialization Failed', 'Failed to initialize pool')
      } finally {
        isSubmitting.value = false
      }
    }

    // View encrypted document
    const viewEncryptedDocument = async (docType, ipfsCid) => {
      if (!ipfsCid) {
        toast.warning('No document uploaded')
        return
      }

      // Logo is NOT encrypted - open directly
      if (docType === 'logo') {
        window.open(`http://localhost:8081/ipfs/${ipfsCid}`, '_blank')
        return
      }

      viewingDoc.value = docType

      try {
        toast.info('Decrypting document...')

        // Use global key address for encrypted document access
        const globalAddress = getKeyAddress()

        // Find the document ID for this CID
        const companyId = parseInt(existingCompany.value.id)
        const docs = await blockchain.getCompanyEncryptedDocuments(companyId)
        const doc = docs.find(d => d.cid === ipfsCid || d.ipfsCid === ipfsCid)

        if (!doc) {
          // Document not in encrypted registry - try direct IPFS access (legacy unencrypted)
          window.open(`http://localhost:8081/ipfs/${ipfsCid}`, '_blank')
          viewingDoc.value = null
          return
        }

        const encryptedKey = await blockchain.getEncryptedKey(doc.id, globalAddress)

        if (!encryptedKey || !encryptedKey.ciphertext || encryptedKey.ciphertext === '0x' || encryptedKey.ciphertext === '') {
          toast.error('You do not have access to this document')
          viewingDoc.value = null
          return
        }

        // Get private key from key manager (prompts once per session)
        const privateKey = getOrPromptKey()

        if (!privateKey) {
          toast.warning('Decryption cancelled')
          viewingDoc.value = null
          return
        }

        // Download and decrypt
        const { url, blob, filename } = await downloadAndDecryptFromIPFS(
          ipfsCid,
          encryptedKey,
          privateKey,
          {
            originalName: doc.originalName,
            originalType: guessContentType(doc.originalName)
          }
        )

        documentPreview.value = {
          url,
          blob,
          filename,
          type: guessContentType(doc.originalName),
          docType
        }

        showPreviewModal.value = true
        toast.success('Document decrypted!')

      } catch (error) {
        console.error('Error viewing document:', error)
        toast.error('Failed to decrypt: ' + error.message)
      } finally {
        viewingDoc.value = null
      }
    }

    const guessContentType = (filename) => {
      const ext = filename?.split('.').pop()?.toLowerCase()
      const types = {
        'pdf': 'application/pdf',
        'png': 'image/png',
        'jpg': 'image/jpeg',
        'jpeg': 'image/jpeg',
        'gif': 'image/gif',
        'txt': 'text/plain'
      }
      return types[ext] || 'application/octet-stream'
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
      const a = document.createElement('a')
      a.href = documentPreview.value.url
      a.download = documentPreview.value.filename
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
    }

    onMounted(async () => {
      await checkExistingCompany()

      // Pre-fill token form if company exists
      if (existingCompany.value) {
        tokenForm.value.name = `${existingCompany.value.name} Token`
        tokenForm.value.symbol = existingCompany.value.symbol

        // Load token balance if token is deployed
        await refreshBalance()

        // Load recent trades from blockchain
        await loadRecentTrades()
      }
    })

    return {
      form,
      uploadProgress,
      isSubmitting,
      canSubmit,
      isLoading,
      existingCompany,
      isEditMode,
      editForm,
      handleFileUpload,
      handleEditFileUpload,
      registerCompany,
      enableEditMode,
      cancelEdit,
      updateCompany,
      removeCompany,
      formatDate,
      formatAddress,
      formatTradeTime,
      recentTrades,
      // Deployment
      showTokenModal,
      showAMMModal,
      showLiquidityModal,
      tokenForm,
      ammForm,
      liquidityForm,
      hasToken,
      hasAMM,
      initialPrice,
      tokenBalance,
      busdBalance,
      refreshBalance,
      loadRecentTrades,
      mintBUSD,
      deployToken,
      redeployToken,
      deployAMM,
      redeployAMM,
      initializeLiquidity,
      // Document viewing
      viewingDoc,
      viewEncryptedDocument,
      showPreviewModal,
      documentPreview,
      closePreview,
      downloadDecryptedFile
    }
  }
}
</script>
