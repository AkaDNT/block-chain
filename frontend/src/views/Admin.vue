<template>
  <div class="max-w-7xl mx-auto">
    <div class="mb-6">
      <h1 class="text-3xl font-bold text-gray-900">Admin Dashboard</h1>
      <p class="text-gray-600 mt-2">Manage companies, verify registrations, and deploy tokens</p>
    </div>

    <!-- Admin Check -->
    <div v-if="!isAdmin && !isLoading" class="card bg-red-50 border-red-200">
      <div class="flex items-center space-x-3">
        <svg class="w-6 h-6 text-red-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
        </svg>
        <div>
          <h3 class="font-semibold text-red-900">Access Denied</h3>
          <p class="text-sm text-red-700">You must be connected as an admin or verifier to access this page.</p>
        </div>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="isLoading" class="card text-center py-12">
      <svg class="animate-spin h-12 w-12 mx-auto text-blue-600 mb-4" fill="none" viewBox="0 0 24 24">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
      </svg>
      <p class="text-gray-600">Loading admin dashboard...</p>
    </div>

    <!-- Admin Dashboard -->
    <div v-if="isAdmin && !isLoading" class="space-y-6">
      <!-- Stats Cards -->
      <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div class="card bg-blue-50 border-blue-200">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm text-blue-600 font-semibold">Total Companies</p>
              <p class="text-2xl font-bold text-blue-900">{{ companies.length }}</p>
            </div>
            <svg class="w-10 h-10 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
            </svg>
          </div>
        </div>

        <div class="card bg-green-50 border-green-200">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm text-green-600 font-semibold">Verified</p>
              <p class="text-2xl font-bold text-green-900">{{ verifiedCount }}</p>
            </div>
            <svg class="w-10 h-10 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
        </div>

        <div class="card bg-yellow-50 border-yellow-200">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm text-yellow-600 font-semibold">Pending</p>
              <p class="text-2xl font-bold text-yellow-900">{{ pendingCount }}</p>
            </div>
            <svg class="w-10 h-10 text-yellow-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
        </div>

        <div class="card bg-purple-50 border-purple-200">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm text-purple-600 font-semibold">With Tokens</p>
              <p class="text-2xl font-bold text-purple-900">{{ withTokensCount }}</p>
            </div>
            <svg class="w-10 h-10 text-purple-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
        </div>
      </div>

      <!-- Trader KYC Verification Section -->
      <div class="card">
        <div class="flex items-center justify-between mb-6">
          <div>
            <h2 class="text-xl font-bold">Trader KYC Verification</h2>
            <p class="text-sm text-gray-600 mt-1">Review and verify individual trader accounts</p>
          </div>
          <button
            @click="loadTraderRequests"
            class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center space-x-2"
          >
            <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
            <span>Refresh</span>
          </button>
        </div>

        <!-- Filter Tabs -->
        <div class="flex space-x-2 mb-4 border-b border-gray-200">
          <button
            v-for="status in ['ALL', 'PENDING', 'VERIFIED', 'REJECTED']"
            :key="status"
            @click="requestFilter = status"
            :class="[
              'px-4 py-2 font-semibold text-sm transition-colors border-b-2',
              requestFilter === status
                ? 'border-blue-600 text-blue-600'
                : 'border-transparent text-gray-600 hover:text-gray-900'
            ]"
          >
            {{ status }}
            <span v-if="status !== 'ALL'" class="ml-1 px-2 py-0.5 bg-gray-100 rounded-full text-xs">
              {{ getRequestCountByStatus(status) }}
            </span>
          </button>
        </div>

        <!-- Requests List -->
        <div v-if="filteredRequests.length === 0" class="text-center py-12 text-gray-500">
          <svg class="w-16 h-16 mx-auto mb-4 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          <p class="font-semibold">No {{ requestFilter.toLowerCase() }} requests found</p>
        </div>

        <div v-else class="space-y-4">
          <div
            v-for="request in filteredRequests"
            :key="request.id"
            class="border rounded-lg p-4 hover:bg-gray-50 transition-colors"
          >
            <div class="flex items-start justify-between">
              <div class="flex-1">
                <div class="flex items-center space-x-3 mb-3">
                  <h3 class="text-lg font-bold">{{ request.fullName }}</h3>
                  <span
                    :class="[
                      'px-2 py-1 text-xs font-semibold rounded',
                      request.status === 'PENDING' ? 'bg-yellow-100 text-yellow-800' :
                      request.status === 'VERIFIED' ? 'bg-green-100 text-green-800' :
                      request.status === 'REJECTED' ? 'bg-red-100 text-red-800' :
                      'bg-gray-100 text-gray-800'
                    ]"
                  >
                    {{ request.status }}
                  </span>
                  <span class="text-xs text-gray-500">KYC #{{ request.id }}</span>
                  <span
                    v-if="request.status === 'VERIFIED' && !request.verifiedOnChain"
                    class="px-2 py-1 text-xs font-semibold rounded bg-yellow-100 text-yellow-800"
                  >
                    Not verified on-chain
                  </span>
                </div>

                <div class="grid grid-cols-2 gap-4 text-sm mb-3">
                  <div>
                    <p class="text-gray-500">Email</p>
                    <p class="font-medium">{{ request.email }}</p>
                  </div>
                  <div>
                    <p class="text-gray-500">Country</p>
                    <p class="font-medium">{{ request.country }}</p>
                  </div>
                  <div>
                    <p class="text-gray-500">Trader Address</p>
                    <p class="font-mono text-xs">{{ formatAddress(request.trader) }}</p>
                  </div>
                  <div>
                    <p class="text-gray-500">Submitted</p>
                    <p class="font-medium">{{ formatDate(request.createdAt) }}</p>
                  </div>
                  <div v-if="request.verifiedAt && request.verifiedAt.getTime() > 0">
                    <p class="text-gray-500">Processed</p>
                    <p class="font-medium">{{ formatDate(request.verifiedAt) }}</p>
                  </div>
                </div>

                <div v-if="request.status === 'REJECTED' && request.rejectionReason" class="mb-3 p-3 bg-red-50 rounded-lg">
                  <p class="text-sm font-semibold text-red-900 mb-1">Rejection Reason:</p>
                  <p class="text-sm text-red-800">{{ request.rejectionReason }}</p>
                </div>

                <!-- KYC Documents (Encrypted) -->
                <div class="flex items-center space-x-4 text-xs">
                  <button
                    @click="viewEncryptedKYCDocument(request.ipfsIdDocument, 'ID Document', request)"
                    :disabled="decryptingKYCDoc === `${request.id}-idDocument`"
                    class="text-purple-600 hover:text-purple-800 flex items-center space-x-1 disabled:opacity-50"
                  >
                    <svg v-if="decryptingKYCDoc === `${request.id}-idDocument`" class="animate-spin w-4 h-4" fill="none" viewBox="0 0 24 24">
                      <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                      <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    <svg v-else class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                    </svg>
                    <span>{{ decryptingKYCDoc === `${request.id}-idDocument` ? 'Decrypting...' : 'ID Document' }}</span>
                  </button>
                  <button
                    @click="viewEncryptedKYCDocument(request.ipfsSelfie, 'Selfie with ID', request)"
                    :disabled="decryptingKYCDoc === `${request.id}-selfie`"
                    class="text-purple-600 hover:text-purple-800 flex items-center space-x-1 disabled:opacity-50"
                  >
                    <svg v-if="decryptingKYCDoc === `${request.id}-selfie`" class="animate-spin w-4 h-4" fill="none" viewBox="0 0 24 24">
                      <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                      <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    <svg v-else class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                    </svg>
                    <span>{{ decryptingKYCDoc === `${request.id}-selfie` ? 'Decrypting...' : 'Selfie with ID' }}</span>
                  </button>
                  <span class="text-gray-400 ml-2">(Encrypted)</span>
                </div>
              </div>

              <!-- Actions -->
              <div v-if="request.status === 'PENDING'" class="flex flex-col space-y-2 ml-4">
                <button
                  @click="verifyRequest(request)"
                  class="px-4 py-2 bg-green-600 text-white text-sm rounded hover:bg-green-700 whitespace-nowrap"
                  :disabled="isProcessing"
                >
                  ✓ Verify
                </button>
                <button
                  @click="openRejectModal(request)"
                  class="px-4 py-2 bg-red-600 text-white text-sm rounded hover:bg-red-700 whitespace-nowrap"
                  :disabled="isProcessing"
                >
                  ✗ Reject
                </button>
              </div>
              <div v-else-if="request.status === 'VERIFIED'" class="ml-4 space-y-2">
                <button
                  @click="revokeTraderRequest(request)"
                  class="w-full px-4 py-2 bg-orange-600 text-white text-sm rounded hover:bg-orange-700 whitespace-nowrap"
                  :disabled="isProcessing || !request.verifiedOnChain"
                >
                  Revoke Access
                </button>
                <p class="text-xs text-gray-500 text-center">
                  <span v-if="request.verifiedOnChain">Removes trading privileges</span>
                  <span v-else>Not verified on-chain (cannot revoke)</span>
                </p>
              </div>
              <div v-else-if="request.status === 'REJECTED'" class="ml-4">
                <div class="px-4 py-2 bg-gray-100 text-gray-600 text-sm rounded text-center">
                  Rejected
                </div>
              </div>
              <div v-else class="ml-4">
                <div class="px-4 py-2 bg-gray-100 text-gray-600 text-sm rounded text-center">
                  {{ request.status }}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Companies List -->
      <div class="card">
        <div class="flex items-center justify-between mb-6">
          <h2 class="text-xl font-bold">Registered Companies</h2>
          <button
            @click="loadCompanies"
            class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center space-x-2"
          >
            <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
            <span>Refresh</span>
          </button>
        </div>

        <div v-if="companies.length === 0" class="text-center py-12 text-gray-500">
          <svg class="w-16 h-16 mx-auto mb-4 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4" />
          </svg>
          <p class="font-semibold">No companies registered yet</p>
        </div>

        <div v-else class="space-y-4">
          <div
            v-for="company in companies"
            :key="company.id"
            class="border rounded-lg p-4 hover:bg-gray-50 transition-colors"
          >
            <div class="flex items-start justify-between">
              <div class="flex-1">
                <div class="flex items-center space-x-3 mb-2">
                  <h3 class="text-lg font-bold">{{ company.name }}</h3>
                  <span class="px-2 py-1 bg-gray-100 text-gray-700 text-xs font-mono rounded">
                    {{ company.symbol }}
                  </span>
                  <span
                    :class="[
                      'px-2 py-1 text-xs font-semibold rounded',
                      company.isVerified ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'
                    ]"
                  >
                    {{ company.isVerified ? '✓ Verified' : '⏳ Pending' }}
                  </span>
                </div>

                <div class="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <p class="text-gray-500">Owner</p>
                    <p class="font-mono text-xs">{{ formatAddress(company.owner) }}</p>
                  </div>
                  <div>
                    <p class="text-gray-500">Company ID</p>
                    <p class="font-semibold">#{{ company.id }}</p>
                  </div>
                  <div>
                    <p class="text-gray-500">Stock Token</p>
                    <p class="font-mono text-xs" :class="company.hasToken ? 'text-green-600' : 'text-gray-400'">
                      {{ company.hasToken ? formatAddress(company.stockToken) : 'Not deployed' }}
                    </p>
                  </div>
                  <div>
                    <p class="text-gray-500">AMM Pool</p>
                    <p class="font-mono text-xs" :class="company.hasAmm ? 'text-green-600' : 'text-gray-400'">
                      {{ company.hasAmm ? formatAddress(company.ammPool) : 'Not deployed' }}
                    </p>
                  </div>
                </div>

                <!-- Documents -->
                <div class="mt-3">
                  <div class="flex items-center justify-between mb-2">
                    <span class="text-xs text-gray-500">Company Documents</span>
                    <button
                      v-if="!companyEncryptedDocs[company.id]"
                      @click="loadEncryptedDocsForCompany(company.id)"
                      class="text-xs text-blue-600 hover:text-blue-800"
                      :disabled="loadingDocsForCompany === company.id"
                    >
                      {{ loadingDocsForCompany === company.id ? 'Loading...' : 'Load Documents' }}
                    </button>
                  </div>

                  <div v-if="loadingDocsForCompany === company.id" class="flex items-center gap-2 text-xs text-gray-400">
                    <svg class="animate-spin w-4 h-4" fill="none" viewBox="0 0 24 24">
                      <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                      <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    Loading documents...
                  </div>

                  <div v-else-if="companyEncryptedDocs[company.id]?.length === 0" class="text-xs text-gray-400 italic">
                    No documents available
                  </div>

                  <div v-else-if="companyEncryptedDocs[company.id]" class="flex flex-wrap gap-2">
                    <button
                      v-for="doc in companyEncryptedDocs[company.id]"
                      :key="doc.id"
                      @click="downloadEncryptedDocument(doc)"
                      :disabled="downloadingDocId === doc.id"
                      :class="getDocTypeButtonClass(doc.docType)"
                      class="flex items-center space-x-1 text-xs disabled:opacity-50"
                    >
                      <svg v-if="downloadingDocId === doc.id" class="animate-spin w-4 h-4" fill="none" viewBox="0 0 24 24">
                        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                      </svg>
                      <svg v-else class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                      </svg>
                      <span>{{ downloadingDocId === doc.id ? 'Decrypting...' : formatDocType(doc.docType) }}</span>
                    </button>
                  </div>
                </div>
              </div>

              <!-- Actions -->
              <div class="flex flex-col space-y-2 ml-4">
                <button
                  v-if="!company.isVerified"
                  @click="verifyCompany(company)"
                  class="px-4 py-2 bg-green-600 text-white text-sm rounded hover:bg-green-700 whitespace-nowrap"
                >
                  ✓ Verify
                </button>
                <div v-else class="space-y-2">
                  <div class="text-sm text-gray-600 px-4 py-2 bg-gray-100 rounded">
                    <p class="font-semibold text-green-600 mb-1">✓ Verified</p>
                    <p class="text-xs">Company owner can deploy token & AMM</p>
                  </div>

                  <!-- Minter Management -->
                  <div class="flex gap-2">
                    <button
                      v-if="!company.isMinter"
                      @click="grantMinter(company)"
                      class="flex-1 px-3 py-2 bg-blue-600 text-white text-xs rounded hover:bg-blue-700"
                      :disabled="isProcessing"
                    >
                      Grant Minter
                    </button>
                    <button
                      v-else
                      @click="revokeMinter(company)"
                      class="flex-1 px-3 py-2 bg-red-600 text-white text-xs rounded hover:bg-red-700"
                      :disabled="isProcessing"
                    >
                      Revoke Minter
                    </button>
                  </div>
                  <p v-if="company.isMinter" class="text-xs text-blue-600 text-center">
                    ✓ Can mint BUSD
                  </p>
                </div>
                <span
                  v-if="company.isInitialized"
                  class="px-4 py-2 bg-gray-100 text-gray-600 text-sm rounded text-center"
                >
                  ✓ Ready
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Deploy Token Modal -->
    <div v-if="showDeployModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg p-6 max-w-md w-full mx-4">
        <h3 class="text-xl font-bold mb-4">Deploy Stock Token</h3>
        <p class="text-gray-600 mb-4">
          Deploy ERC20 token for <strong>{{ selectedCompany?.name }}</strong> ({{ selectedCompany?.symbol }})
        </p>

        <div class="space-y-4">
          <div>
            <label class="label">Total Supply</label>
            <input
              v-model="tokenSupply"
              type="number"
              class="input-field"
              placeholder="1000000"
            />
            <p class="text-xs text-gray-500 mt-1">Number of tokens to create</p>
          </div>
        </div>

        <div class="flex gap-4 mt-6">
          <button
            @click="showDeployModal = false"
            class="flex-1 px-4 py-2 bg-gray-200 text-gray-800 rounded-lg font-semibold hover:bg-gray-300"
          >
            Cancel
          </button>
          <button
            @click="confirmDeployToken"
            :disabled="isProcessing"
            class="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg font-semibold hover:bg-blue-700 disabled:opacity-50"
          >
            <span v-if="isProcessing">Deploying...</span>
            <span v-else>Deploy</span>
          </button>
        </div>
      </div>
    </div>

    <!-- Reject Request Modal -->
    <div v-if="showRejectModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg p-6 max-w-md w-full mx-4">
        <h3 class="text-xl font-bold mb-4">Reject Trader KYC</h3>
        <p class="text-gray-600 mb-4">
          Reject KYC from <strong>{{ selectedRequest?.fullName }}</strong>
        </p>

        <div class="space-y-4">
          <div>
            <label class="label">Rejection Reason <span class="text-red-500">*</span></label>
            <textarea
              v-model="rejectionReason"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent"
              rows="4"
              placeholder="Explain why this request is being rejected..."
              required
            ></textarea>
          </div>
        </div>

        <div class="flex gap-4 mt-6">
          <button
            @click="showRejectModal = false"
            class="flex-1 px-4 py-2 bg-gray-200 text-gray-800 rounded-lg font-semibold hover:bg-gray-300"
          >
            Cancel
          </button>
          <button
            @click="confirmRejectRequest"
            :disabled="isProcessing || !rejectionReason"
            class="flex-1 px-4 py-2 bg-red-600 text-white rounded-lg font-semibold hover:bg-red-700 disabled:opacity-50"
          >
            <span v-if="isProcessing">Rejecting...</span>
            <span v-else>Reject Request</span>
          </button>
        </div>
      </div>
    </div>

    <!-- Document Viewer Modal -->
    <div v-if="showDocumentModal" class="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50" @click="showDocumentModal = false">
      <div class="bg-white rounded-lg p-4 max-w-4xl w-full mx-4 max-h-[90vh] overflow-auto" @click.stop>
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-xl font-bold">{{ documentTitle }}</h3>
          <button
            @click="showDocumentModal = false"
            class="text-gray-500 hover:text-gray-700"
          >
            <svg class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
        <div class="flex justify-center">
          <img :src="documentUrl" :alt="documentTitle" class="max-w-full h-auto rounded-lg shadow-lg" />
        </div>
      </div>
    </div>

    <!-- Initialize Pool Modal -->
    <div v-if="showInitModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg p-6 max-w-md w-full mx-4">
        <h3 class="text-xl font-bold mb-4">Initialize AMM Pool</h3>
        <p class="text-gray-600 mb-4">
          Set initial liquidity for <strong>{{ selectedCompany?.name }}</strong>
        </p>

        <div class="space-y-4">
          <div>
            <label class="label">Initial Stock Amount</label>
            <input
              v-model="initialStock"
              type="number"
              class="input-field"
              placeholder="100000"
            />
          </div>

          <div>
            <label class="label">Initial Base Amount (BUSD)</label>
            <input
              v-model="initialBase"
              type="number"
              class="input-field"
              placeholder="1000000"
            />
          </div>

          <div v-if="initialStock && initialBase" class="bg-blue-50 p-3 rounded">
            <p class="text-sm text-blue-900">
              <strong>Initial Price:</strong> {{ (initialBase / initialStock).toFixed(2) }} BUSD per {{ selectedCompany?.symbol }}
            </p>
          </div>
        </div>

        <div class="flex gap-4 mt-6">
          <button
            @click="showInitModal = false"
            class="flex-1 px-4 py-2 bg-gray-200 text-gray-800 rounded-lg font-semibold hover:bg-gray-300"
          >
            Cancel
          </button>
          <button
            @click="confirmInitializePool"
            :disabled="isProcessing"
            class="flex-1 px-4 py-2 bg-indigo-600 text-white rounded-lg font-semibold hover:bg-indigo-700 disabled:opacity-50"
          >
            <span v-if="isProcessing">Initializing...</span>
            <span v-else>Initialize</span>
          </button>
        </div>
      </div>
    </div>

    <!-- Encrypted Document Preview Modal -->
    <div v-if="showPreviewModal && documentPreview" class="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50" @click="closePreview">
      <div class="bg-white rounded-lg max-w-4xl w-full mx-4 max-h-[90vh] overflow-hidden flex flex-col" @click.stop>
        <div class="flex items-center justify-between p-4 border-b">
          <div>
            <h3 class="text-lg font-bold">{{ documentPreview.doc?.originalName || 'Document Preview' }}</h3>
            <p class="text-sm text-gray-500">{{ formatDocType(documentPreview.doc?.docType) }}</p>
          </div>
          <div class="flex items-center gap-2">
            <button
              @click="downloadDecryptedFile"
              class="px-4 py-2 bg-blue-600 text-white text-sm rounded-lg hover:bg-blue-700 flex items-center gap-2"
            >
              <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
              </svg>
              Download
            </button>
            <button
              @click="closePreview"
              class="p-2 text-gray-500 hover:text-gray-700 rounded-lg hover:bg-gray-100"
            >
              <svg class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>
        <div class="flex-1 overflow-auto p-4 bg-gray-100">
          <!-- PDF Preview -->
          <iframe
            v-if="documentPreview.type === 'application/pdf'"
            :src="documentPreview.url"
            class="w-full h-full min-h-[70vh] rounded-lg"
          ></iframe>
          <!-- Image Preview -->
          <img
            v-else-if="documentPreview.type?.startsWith('image/')"
            :src="documentPreview.url"
            :alt="documentPreview.filename"
            class="max-w-full h-auto mx-auto rounded-lg shadow-lg"
          />
          <!-- Other files - download only -->
          <div v-else class="text-center py-12">
            <svg class="w-16 h-16 mx-auto text-gray-400 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            <p class="text-gray-600 mb-4">This file type cannot be previewed</p>
            <button
              @click="downloadDecryptedFile"
              class="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
            >
              Download File
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import blockchain from '../utils/blockchain.js'
import toast from '../utils/toast.js'
import { confirm } from '../utils/confirm.js'
import { downloadAndDecryptFromIPFS, triggerDownload } from '../utils/encryptedIPFS.js'
import { getKeyAddress, getOrPromptKey } from '../utils/keyManager.js'

export default {
  name: 'Admin',
  setup() {
    const isLoading = ref(true)
    const isAdmin = ref(false)
    const isProcessing = ref(false)
    const companies = ref([])
    const selectedCompany = ref(null)
    const showDeployModal = ref(false)
    const showInitModal = ref(false)
    const tokenSupply = ref('1000000')
    const initialStock = ref('100000')
    const initialBase = ref('1000000')

    // Minter request management
    const minterRequests = ref([])
    const requestFilter = ref('ALL')
    const selectedRequest = ref(null)
    const showRejectModal = ref(false)
    const rejectionReason = ref('')
    const showDocumentModal = ref(false)
    const documentUrl = ref('')
    const documentTitle = ref('')

    // Encrypted documents
    const companyEncryptedDocs = ref({}) // Map of companyId -> docs array
    const loadingDocsForCompany = ref(null)
    const downloadingDocId = ref(null)
    const showPreviewModal = ref(false)
    const documentPreview = ref(null)
    const decryptingKYCDoc = ref(null) // Track which KYC doc is being decrypted

    const verifiedCount = computed(() => companies.value.filter(c => c.isVerified).length)
    const pendingCount = computed(() => companies.value.filter(c => !c.isVerified).length)
    const withTokensCount = computed(() => companies.value.filter(c => c.hasToken).length)

    const filteredRequests = computed(() => {
      if (requestFilter.value === 'ALL') {
        return minterRequests.value
      }
      return minterRequests.value.filter(r => r.status === requestFilter.value)
    })

    const getRequestCountByStatus = (status) => {
      return minterRequests.value.filter(r => r.status === status).length
    }

    const formatAddress = (address) => {
      if (!address) return 'N/A'
      return `${address.slice(0, 6)}...${address.slice(-4)}`
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

    const checkAdminAccess = async () => {
      try {
        if (!blockchain.signer) {
          isAdmin.value = false
          return
        }

        const registry = blockchain.getRegistry()
        const address = await blockchain.signer.getAddress()

        // Check if user is admin or verifier
        const admin = await registry.admin()
        const isVerifier = await registry.verifiers(address)

        isAdmin.value = (address.toLowerCase() === admin.toLowerCase()) || isVerifier
      } catch (error) {
        console.error('Error checking admin access:', error)
        isAdmin.value = false
      }
    }

    const loadCompanies = async () => {
      try {
        const registry = blockchain.getRegistry()
        const count = await registry.company_count()
        const loadedCompanies = []

        for (let i = 1; i <= count; i++) {
          const company = await registry.get_company(i)

          const hasToken = company.stock_token !== '0x0000000000000000000000000000000000000000'
          const hasAmm = company.amm_pool !== '0x0000000000000000000000000000000000000000'

          let isInitialized = false
          if (hasAmm) {
            try {
              const amm = blockchain.getAMM(company.amm_pool)
              isInitialized = await amm.is_initialized()
            } catch (e) {
              isInitialized = false
            }
          }

          // Check if company owner is a minter
          let isMinter = false
          try {
            const baseToken = blockchain.getBaseToken()
            isMinter = await baseToken.minters(company.owner)
          } catch (e) {
            isMinter = false
          }

          loadedCompanies.push({
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
            hasToken,
            hasAmm,
            isInitialized,
            isMinter,
            createdAt: new Date(Number(company.created_at) * 1000)
          })
        }

        companies.value = loadedCompanies
      } catch (error) {
        console.error('Error loading companies:', error)
        toast.txError(error, 'Load Failed', 'Failed to load companies')
      }
    }

    const verifyCompany = async (company) => {
      const confirmed = await confirm({
        title: 'Verify Company',
        message: `Verify ${company.name}?`,
        details: 'This marks the company as legitimate and allows token deployment.',
        type: 'success',
        confirmText: 'Verify',
        cancelText: 'Cancel'
      })

      if (!confirmed) return

      try {
        const registry = blockchain.getRegistry()

        toast.txStep('Verify Company', `Setting ${company.name} as verified`)
        const tx = await registry.set_verified(company.id, true)

        toast.txPending('Verifying company')
        await tx.wait()

        toast.txConfirmed('Company verified', `${company.name} is now verified`)
        await loadCompanies()
      } catch (error) {
        console.error('Error verifying company:', error)
        toast.txError(error, 'Verification Failed', 'Failed to verify company')
      }
    }

    const grantMinter = async (company) => {
      const confirmed = await confirm({
        title: 'Grant Minter Permission',
        message: `Grant minter permission to ${company.name}?`,
        details: 'This will allow the company owner to mint BUSD tokens for testing and adding liquidity.',
        type: 'info',
        confirmText: 'Grant',
        cancelText: 'Cancel'
      })

      if (!confirmed) return

      isProcessing.value = true

      try {
        const baseToken = blockchain.getBaseToken()

        toast.txStep('Grant Minter', `Grant minter permission to ${company.name}`)
        const tx = await baseToken.add_minter(company.owner)

        toast.txPending('Granting permission')
        await tx.wait()

        toast.txConfirmed('Minter granted', `${company.name} can now mint BUSD`)
        await loadCompanies()
      } catch (error) {
        console.error('Error granting minter:', error)
        toast.txError(error, 'Grant Failed', 'Failed to grant minter')
      } finally {
        isProcessing.value = false
      }
    }

    const revokeMinter = async (company) => {
      const confirmed = await confirm({
        title: 'Revoke Minter Permission',
        message: `Revoke minter permission from ${company.name}?`,
        details: 'The company owner will no longer be able to mint BUSD tokens.',
        type: 'warning',
        confirmText: 'Revoke',
        cancelText: 'Cancel'
      })

      if (!confirmed) return

      isProcessing.value = true

      try {
        const baseToken = blockchain.getBaseToken()

        toast.txStep('Revoke Minter', `Remove minter permission from ${company.name}`)
        const tx = await baseToken.remove_minter(company.owner)

        toast.txPending('Revoking permission')
        await tx.wait()

        toast.txConfirmed('Minter revoked', `${company.name} can no longer mint BUSD`)
        await loadCompanies()
      } catch (error) {
        console.error('Error revoking minter:', error)
        toast.txError(error, 'Revoke Failed', 'Failed to revoke minter')
      } finally {
        isProcessing.value = false
      }
    }

    const deployToken = (company) => {
      selectedCompany.value = company
      tokenSupply.value = '1000000'
      showDeployModal.value = true
    }

    const confirmDeployToken = async () => {
      isProcessing.value = true

      try {
        toast.info('Deploying stock token...')

        // Call backend API to deploy token
        const response = await fetch('http://localhost:3001/api/deploy/token', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            companyId: selectedCompany.value.id,
            name: selectedCompany.value.name,
            symbol: selectedCompany.value.symbol,
            totalSupply: tokenSupply.value
          })
        })

        const data = await response.json()

        if (!response.ok) {
          throw new Error(data.error || 'Failed to deploy token')
        }

        toast.success(`Token deployed and registered successfully!`, 'Token Deployed!')

        showDeployModal.value = false
        await loadCompanies()
      } catch (error) {
        console.error('Error deploying token:', error)
        toast.txError(error, 'Deployment Failed', 'Failed to deploy token')
      } finally {
        isProcessing.value = false
      }
    }

    const deployAMM = async (company) => {
      const confirmed = await confirm({
        title: 'Deploy AMM Pool',
        message: `Deploy AMM pool for ${company.name}?`,
        details: 'This will create a new trading pool for the company stock.',
        type: 'info',
        confirmText: 'Deploy',
        cancelText: 'Cancel'
      })

      if (!confirmed) return

      try {
        toast.info('Deploying AMM pool...')

        // Call backend API to deploy AMM
        const response = await fetch('http://localhost:3001/api/deploy/amm', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            companyId: company.id
          })
        })

        const data = await response.json()

        if (!response.ok) {
          throw new Error(data.error || 'Failed to deploy AMM')
        }

        toast.success(`AMM deployed and registered successfully!`, 'AMM Deployed!')

        await loadCompanies()
      } catch (error) {
        console.error('Error deploying AMM:', error)
        toast.txError(error, 'Deployment Failed', 'Failed to deploy AMM')
      }
    }

    const initializePool = (company) => {
      selectedCompany.value = company
      initialStock.value = '100000'
      initialBase.value = '1000000'
      showInitModal.value = true
    }

    const confirmInitializePool = async () => {
      isProcessing.value = true

      try {
        toast.info('Initializing pool...')

        const baseToken = blockchain.getBaseToken()
        const baseTokenAddress = await baseToken.getAddress()

        // Call backend API to initialize pool
        const response = await fetch('http://localhost:3001/api/initialize/pool', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            ammAddress: selectedCompany.value.ammPool,
            stockTokenAddress: selectedCompany.value.stockToken,
            baseTokenAddress: baseTokenAddress,
            initialStock: initialStock.value,
            initialBase: initialBase.value
          })
        })

        const data = await response.json()

        if (!response.ok) {
          throw new Error(data.error || 'Failed to initialize pool')
        }

        toast.success(
          `Pool initialized! Price: ${parseFloat(data.price).toFixed(2)} BUSD per ${selectedCompany.value.symbol}`,
          'Pool Ready'
        )

        showInitModal.value = false
        await loadCompanies()
      } catch (error) {
        console.error('Error initializing pool:', error)
        toast.txError(error, 'Initialization Failed', 'Failed to initialize pool')
      } finally {
        isProcessing.value = false
      }
    }

    const loadTraderRequests = async () => {
      try {
        const requests = await blockchain.getAllTraderKYCs()
        minterRequests.value = requests.sort((a, b) => {
          // Sort by status (PENDING first) then by date
          if (a.status === 'PENDING' && b.status !== 'PENDING') return -1
          if (a.status !== 'PENDING' && b.status === 'PENDING') return 1
          return b.createdAt - a.createdAt
        })
      } catch (error) {
        console.error('Error loading trader requests:', error)
        toast.txError(error, 'Load Failed', 'Failed to load trader KYC requests')
      }
    }

    const verifyRequest = async (request) => {
      const confirmed = await confirm({
        title: 'Verify Trader KYC',
        message: `Verify trader ${request.fullName}?`,
        details: 'This will grant trading privileges on the platform.',
        type: 'success',
        confirmText: 'Verify',
        cancelText: 'Cancel'
      })

      if (!confirmed) return

      isProcessing.value = true

      try {
        toast.info('Verifying KYC... Please wait')
        await blockchain.verifyTraderKYC(request.id)

        toast.success(`${request.fullName} has been verified as a trader!`, 'KYC Verified')
        await loadTraderRequests()
      } catch (error) {
        console.error('Error verifying KYC:', error)
        toast.txError(error, 'Verification Failed', 'Failed to verify KYC')
      } finally {
        isProcessing.value = false
      }
    }

    const openRejectModal = (request) => {
      selectedRequest.value = request
      rejectionReason.value = ''
      showRejectModal.value = true
    }

    const confirmRejectRequest = async () => {
      if (!rejectionReason.value) return

      isProcessing.value = true

      try {
        toast.info('Rejecting KYC... Please wait')
        await blockchain.rejectTraderKYC(selectedRequest.value.id, rejectionReason.value)

        toast.success(`KYC from ${selectedRequest.value.fullName} has been rejected`, 'KYC Rejected')
        showRejectModal.value = false
        selectedRequest.value = null
        rejectionReason.value = ''
        await loadTraderRequests()
      } catch (error) {
        console.error('Error rejecting KYC:', error)
        toast.txError(error, 'Rejection Failed', 'Failed to reject KYC')
      } finally {
        isProcessing.value = false
      }
    }

    const revokeTraderRequest = async (request) => {
      const confirmed = await confirm({
        title: 'Revoke Trader Verification',
        message: `Revoke trading access from ${request.fullName}?`,
        details: 'This will remove their trading privileges on the platform.',
        type: 'warning',
        confirmText: 'Revoke',
        cancelText: 'Cancel'
      })

      if (!confirmed) return

      isProcessing.value = true

      try {
        toast.info('Revoking trader access... Please wait')
        await blockchain.revokeTrader(request.trader)

        toast.success(`Trading access revoked from ${request.fullName}`, 'Access Revoked')
        await loadTraderRequests()
      } catch (error) {
        console.error('Error revoking trader:', error)
        toast.txError(error, 'Revoke Failed', 'Failed to revoke trader')
      } finally {
        isProcessing.value = false
      }
    }

    const viewDocument = (ipfsCid, title) => {
      documentUrl.value = `http://localhost:8081/ipfs/${ipfsCid}`
      documentTitle.value = title
      showDocumentModal.value = true
    }

    // View encrypted KYC document
    const viewEncryptedKYCDocument = async (ipfsCid, title, request) => {
      if (!ipfsCid) {
        toast.warning('No document uploaded')
        return
      }

      const docKey = title === 'ID Document' ? `${request.id}-idDocument` : `${request.id}-selfie`
      decryptingKYCDoc.value = docKey

      try {
        toast.info('Decrypting document...')

        // Use global key address for encrypted document access
        const globalAddress = getKeyAddress()

        // Find the document ID for this CID in EncryptedDocRegistry
        const docCount = await blockchain.getEncryptedDocCount()
        let doc = null

        for (let i = 1; i <= docCount; i++) {
          try {
            const d = await blockchain.getEncryptedDocument(i)
            if (d && (d.cid === ipfsCid || d.ipfsCid === ipfsCid)) {
              doc = d
              break
            }
          } catch (e) {
            // Skip invalid doc IDs
          }
        }

        if (!doc) {
          // Document not in encrypted registry - might be old unencrypted doc
          toast.warning('Document not found in encrypted registry. Opening direct IPFS link (may be unencrypted legacy document).')
          documentUrl.value = `http://localhost:8081/ipfs/${ipfsCid}`
          documentTitle.value = title
          showDocumentModal.value = true
          decryptingKYCDoc.value = null
          return
        }

        const encryptedKey = await blockchain.getEncryptedKey(doc.id, globalAddress)

        if (!encryptedKey || !encryptedKey.ciphertext || encryptedKey.ciphertext === '0x' || encryptedKey.ciphertext === '') {
          toast.error('You do not have access to decrypt this document')
          decryptingKYCDoc.value = null
          return
        }

        // Get private key from key manager
        const privateKey = getOrPromptKey()

        if (!privateKey) {
          toast.warning('Decryption cancelled')
          decryptingKYCDoc.value = null
          return
        }

        // Download and decrypt
        const result = await downloadAndDecryptFromIPFS(
          ipfsCid,
          encryptedKey,
          privateKey,
          {
            originalName: doc.originalName,
            originalType: guessContentType(doc.originalName)
          }
        )

        documentPreview.value = {
          url: result.url,
          blob: result.blob,
          filename: result.filename,
          type: guessContentType(doc.originalName),
          doc: {
            ...doc,
            originalName: doc.originalName || title,
            docType: title
          }
        }
        showPreviewModal.value = true
        toast.success('Document decrypted!')

      } catch (error) {
        console.error('Error viewing KYC document:', error)
        toast.error('Failed to decrypt: ' + error.message)
      } finally {
        decryptingKYCDoc.value = null
      }
    }

    // Encrypted document functions
    const loadEncryptedDocsForCompany = async (companyId) => {
      if (companyEncryptedDocs.value[companyId]) return // Already loaded

      loadingDocsForCompany.value = companyId
      try {
        const docs = await blockchain.getCompanyEncryptedDocuments(parseInt(companyId))
        companyEncryptedDocs.value[companyId] = docs
        console.log(`📄 Loaded ${docs.length} encrypted docs for company ${companyId}`)
      } catch (error) {
        console.warn('Could not load encrypted documents:', error)
        companyEncryptedDocs.value[companyId] = []
      } finally {
        loadingDocsForCompany.value = null
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
        const globalAddress = getKeyAddress()

        const canAccess = await blockchain.canAccessDocument(doc.id, globalAddress)
        if (!canAccess) {
          toast.error('You do not have access to this document')
          return
        }

        const encryptedKey = await blockchain.getEncryptedKey(doc.id, globalAddress)

        if (!encryptedKey || !encryptedKey.ciphertext || encryptedKey.ciphertext === '0x' || encryptedKey.ciphertext === '') {
          toast.error('You do not have access to this document')
          return
        }

        const privateKey = getOrPromptKey()

        if (!privateKey) {
          toast.warning('Decryption cancelled')
          return
        }

        toast.info('Decrypting document...', 'Please wait')

        const result = await downloadAndDecryptFromIPFS(
          doc.ipfsCid || doc.cid,
          encryptedKey,
          privateKey,
          {
            originalName: doc.originalName,
            originalType: guessContentType(doc.originalName)
          }
        )

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
        'prospectus': 'text-blue-600 hover:text-blue-800',
        'financials': 'text-green-600 hover:text-green-800',
        'logo': 'text-purple-600 hover:text-purple-800',
        'encrypted': 'text-amber-600 hover:text-amber-800'
      }
      return classMap[docType] || 'text-gray-600 hover:text-gray-800'
    }

    onMounted(async () => {
      await checkAdminAccess()

      if (isAdmin.value) {
        await Promise.all([
          loadCompanies(),
          loadTraderRequests()
        ])
      }

      isLoading.value = false
    })

    return {
      isLoading,
      isAdmin,
      isProcessing,
      companies,
      selectedCompany,
      showDeployModal,
      showInitModal,
      tokenSupply,
      initialStock,
      initialBase,
      verifiedCount,
      pendingCount,
      withTokensCount,
      formatAddress,
      formatDate,
      loadCompanies,
      verifyCompany,
      grantMinter,
      revokeMinter,
      deployToken,
      confirmDeployToken,
      deployAMM,
      initializePool,
      confirmInitializePool,
      // Trader KYC management
      minterRequests,
      requestFilter,
      filteredRequests,
      selectedRequest,
      showRejectModal,
      rejectionReason,
      showDocumentModal,
      documentUrl,
      documentTitle,
      getRequestCountByStatus,
      loadTraderRequests,
      verifyRequest,
      openRejectModal,
      confirmRejectRequest,
      revokeTraderRequest,
      viewDocument,
      viewEncryptedKYCDocument,
      decryptingKYCDoc,
      // Encrypted documents
      companyEncryptedDocs,
      loadingDocsForCompany,
      downloadingDocId,
      showPreviewModal,
      documentPreview,
      loadEncryptedDocsForCompany,
      downloadEncryptedDocument,
      closePreview,
      downloadDecryptedFile,
      formatDocType,
      getDocTypeButtonClass
    }
  }
}
</script>
