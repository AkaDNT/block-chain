<template>
  <div class="container mx-auto px-4 py-8">
    <h1 class="text-3xl font-bold mb-8">Company Dashboard</h1>

    <!-- Loading State -->
    <div v-if="isLoading" class="text-center py-12">
      <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
      <p class="mt-4 text-gray-600">Loading company information...</p>
    </div>

    <!-- No Company Found -->
    <div v-else-if="!company" class="card text-center py-12">
      <p class="text-gray-600 mb-4">You haven't registered a company yet.</p>
      <router-link to="/register" class="btn-primary inline-block">
        Register Your Company
      </router-link>
    </div>

    <!-- Company Dashboard -->
    <div v-else class="space-y-6">
      <!-- Company Info Card -->
      <div class="card">
        <div class="flex justify-between items-start mb-4">
          <div>
            <h2 class="text-2xl font-bold">{{ company.name }}</h2>
            <p class="text-gray-600">{{ company.symbol }}</p>
          </div>
          <span
            :class="[
              'px-3 py-1 rounded-full text-sm font-semibold',
              company.isVerified ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'
            ]"
          >
            {{ company.isVerified ? '✓ Verified' : '⏳ Pending Verification' }}
          </span>
        </div>
        <p class="text-gray-700">{{ company.description }}</p>
      </div>

      <!-- Deployment Status -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <!-- Token Status -->
        <div class="card">
          <h3 class="font-semibold mb-2">Stock Token</h3>
          <div v-if="company.stockToken && company.stockToken !== '0x0000000000000000000000000000000000000000'">
            <p class="text-green-600 font-semibold">✓ Deployed</p>
            <p class="text-xs text-gray-500 mt-1 break-all">{{ company.stockToken }}</p>
          </div>
          <p v-else class="text-gray-500">Not deployed</p>
        </div>

        <!-- AMM Status -->
        <div class="card">
          <h3 class="font-semibold mb-2">AMM Pool</h3>
          <div v-if="company.ammPool && company.ammPool !== '0x0000000000000000000000000000000000000000'">
            <p class="text-green-600 font-semibold">✓ Deployed</p>
            <p class="text-xs text-gray-500 mt-1 break-all">{{ company.ammPool }}</p>
          </div>
          <p v-else class="text-gray-500">Not deployed</p>
        </div>

        <!-- Pool Status -->
        <div class="card">
          <h3 class="font-semibold mb-2">Liquidity</h3>
          <p v-if="company.isInitialized" class="text-green-600 font-semibold">✓ Initialized</p>
          <p v-else class="text-gray-500">Not initialized</p>
        </div>
      </div>

      <!-- Action Buttons -->
      <div class="card">
        <h3 class="text-xl font-bold mb-4">Deployment Actions</h3>

        <!-- Step 1: Deploy Token -->
        <div class="mb-6">
          <div class="flex items-center justify-between mb-2">
            <h4 class="font-semibold">Step 1: Deploy Stock Token</h4>
            <span v-if="hasToken" class="text-green-600">✓ Complete</span>
          </div>
          <p class="text-sm text-gray-600 mb-3">
            Deploy your ERC-20 stock token. You control the total supply and token parameters.
          </p>
          <button
            v-if="!hasToken && company.isVerified"
            @click="showTokenModal = true"
            class="btn-primary"
          >
            Deploy Stock Token
          </button>
          <button v-else-if="!company.isVerified" disabled class="btn-primary opacity-50 cursor-not-allowed">
            Awaiting Verification
          </button>
        </div>

        <!-- Step 2: Deploy AMM -->
        <div class="mb-6">
          <div class="flex items-center justify-between mb-2">
            <h4 class="font-semibold">Step 2: Deploy AMM Pool</h4>
            <span v-if="hasAMM" class="text-green-600">✓ Complete</span>
          </div>
          <p class="text-sm text-gray-600 mb-3">
            Create your Automated Market Maker pool for trading.
          </p>
          <button
            v-if="hasToken && !hasAMM"
            @click="showAMMModal = true"
            class="btn-primary"
          >
            Deploy AMM Pool
          </button>
          <button v-else-if="!hasToken" disabled class="btn-primary opacity-50 cursor-not-allowed">
            Deploy Token First
          </button>
        </div>

        <!-- Step 3: Initialize Pool -->
        <div>
          <div class="flex items-center justify-between mb-2">
            <h4 class="font-semibold">Step 3: Initialize Liquidity</h4>
            <span v-if="company.isInitialized" class="text-green-600">✓ Complete</span>
          </div>
          <p class="text-sm text-gray-600 mb-3">
            Add initial liquidity to set the starting price for your stock.
          </p>
          <button
            v-if="hasToken && hasAMM && !company.isInitialized"
            @click="showLiquidityModal = true"
            class="btn-primary"
          >
            Add Initial Liquidity
          </button>
          <button v-else-if="!hasAMM" disabled class="btn-primary opacity-50 cursor-not-allowed">
            Deploy AMM First
          </button>
        </div>
      </div>
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
            :disabled="isProcessing"
            class="flex-1 px-4 py-2 bg-gray-200 text-gray-800 rounded-lg font-semibold hover:bg-gray-300"
          >
            Cancel
          </button>
          <button
            @click="deployToken"
            :disabled="isProcessing || !tokenForm.name || !tokenForm.symbol || !tokenForm.totalSupply"
            class="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg font-semibold hover:bg-blue-700 disabled:opacity-50"
          >
            <span v-if="isProcessing">Deploying...</span>
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
            :disabled="isProcessing"
            class="flex-1 px-4 py-2 bg-gray-200 text-gray-800 rounded-lg font-semibold hover:bg-gray-300"
          >
            Cancel
          </button>
          <button
            @click="deployAMM"
            :disabled="isProcessing"
            class="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg font-semibold hover:bg-blue-700 disabled:opacity-50"
          >
            <span v-if="isProcessing">Deploying...</span>
            <span v-else>Deploy AMM</span>
          </button>
        </div>
      </div>

      <!-- Encrypted Documents Section -->
      <div class="card">
        <div class="flex justify-between items-center mb-4">
          <div>
            <h3 class="text-xl font-bold">Encrypted Documents</h3>
            <p class="text-sm text-gray-500">Securely encrypted and stored on IPFS</p>
          </div>
          <button
            @click="showUploadModal = true"
            class="btn-primary flex items-center gap-2"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"></path>
            </svg>
            Upload Document
          </button>
        </div>

        <!-- Loading State -->
        <div v-if="loadingDocs" class="text-center py-4">
          <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
          <p class="mt-2 text-sm text-gray-500">Loading documents...</p>
        </div>

        <!-- Empty State -->
        <div v-else-if="encryptedDocuments.length === 0" class="text-center py-8 bg-gray-50 rounded-lg">
          <svg class="w-12 h-12 mx-auto text-gray-400 mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"></path>
          </svg>
          <p class="text-gray-500">No encrypted documents yet</p>
          <p class="text-sm text-gray-400">Upload your first encrypted document</p>
        </div>

        <!-- Documents List -->
        <div v-else class="space-y-3">
          <div
            v-for="doc in encryptedDocuments"
            :key="doc.id"
            class="flex items-center justify-between p-4 bg-amber-50 rounded-lg border border-amber-100"
          >
            <div class="flex items-center gap-3">
              <div class="w-10 h-10 bg-amber-100 rounded-lg flex items-center justify-center">
                <svg class="w-5 h-5 text-amber-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"></path>
                </svg>
              </div>
              <div>
                <p class="font-semibold text-gray-900">{{ doc.originalName }}</p>
                <p class="text-sm text-gray-500">
                  {{ doc.docType }} • {{ (doc.originalSize / 1024).toFixed(1) }} KB •
                  {{ doc.uploadedAt.toLocaleDateString() }}
                </p>
              </div>
            </div>
            <div class="flex gap-2">
              <button
                @click="viewDocument(doc)"
                :disabled="viewingDocId === doc.id"
                class="px-3 py-1.5 text-sm font-medium text-blue-600 bg-blue-50 rounded-lg hover:bg-blue-100 transition-colors disabled:opacity-50"
              >
                <span v-if="viewingDocId === doc.id">Decrypting...</span>
                <span v-else>View</span>
              </button>
              <button
                @click="revokeDocument(doc)"
                class="px-3 py-1.5 text-sm font-medium text-red-600 bg-red-50 rounded-lg hover:bg-red-100 transition-colors"
              >
                Revoke
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Upload Encrypted Document Modal -->
    <div v-if="showUploadModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg p-6 max-w-md w-full mx-4">
        <h3 class="text-xl font-bold mb-4">Upload Encrypted Document</h3>

        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium mb-1">Select File</label>
            <input
              type="file"
              @change="handleFileSelect"
              class="w-full px-3 py-2 border rounded-lg"
            />
            <p v-if="uploadForm.file" class="text-sm text-green-600 mt-1">
              Selected: {{ uploadForm.file.name }} ({{ (uploadForm.file.size / 1024).toFixed(1) }} KB)
            </p>
          </div>

          <div>
            <label class="block text-sm font-medium mb-1">Document Type</label>
            <select
              v-model="uploadForm.docType"
              class="w-full px-3 py-2 border rounded-lg"
            >
              <option value="prospectus">Prospectus</option>
              <option value="financial">Financial Statement</option>
              <option value="legal">Legal Document</option>
              <option value="kyc">KYC Document</option>
              <option value="other">Other</option>
            </select>
          </div>

          <div class="bg-blue-50 p-3 rounded-lg">
            <p class="text-sm text-blue-800">
              <strong>Note:</strong> Documents are encrypted client-side before upload.
              Only you and authorized recipients can decrypt them.
            </p>
          </div>

          <!-- Upload Progress -->
          <div v-if="isUploading" class="space-y-2">
            <div class="flex justify-between text-sm">
              <span>Uploading...</span>
              <span>{{ uploadProgress }}%</span>
            </div>
            <div class="w-full bg-gray-200 rounded-full h-2">
              <div
                class="bg-blue-600 h-2 rounded-full transition-all duration-300"
                :style="{ width: `${uploadProgress}%` }"
              ></div>
            </div>
          </div>
        </div>

        <div class="flex gap-3 mt-6">
          <button
            @click="showUploadModal = false"
            :disabled="isUploading"
            class="flex-1 px-4 py-2 bg-gray-200 text-gray-800 rounded-lg font-semibold hover:bg-gray-300"
          >
            Cancel
          </button>
          <button
            @click="uploadEncryptedDocument"
            :disabled="isUploading || !uploadForm.file"
            class="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg font-semibold hover:bg-blue-700 disabled:opacity-50"
          >
            <span v-if="isUploading">Uploading...</span>
            <span v-else>Encrypt & Upload</span>
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
            <label class="block text-sm font-medium mb-1">Stock Tokens ({{ company.symbol }})</label>
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
              <strong>Initial Price:</strong> {{ initialPrice }} BUSD per {{ company.symbol }}
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
            :disabled="isProcessing"
            class="flex-1 px-4 py-2 bg-gray-200 text-gray-800 rounded-lg font-semibold hover:bg-gray-300"
          >
            Cancel
          </button>
          <button
            @click="initializeLiquidity"
            :disabled="isProcessing || !liquidityForm.stockAmount || !liquidityForm.baseAmount"
            class="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg font-semibold hover:bg-blue-700 disabled:opacity-50"
          >
            <span v-if="isProcessing">Processing...</span>
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

        <!-- Preview Content -->
        <div class="flex-1 overflow-auto bg-gray-100 rounded-lg p-4 min-h-[400px]">
          <!-- PDF Preview -->
          <iframe
            v-if="documentPreview.type === 'application/pdf'"
            :src="documentPreview.url"
            class="w-full h-full min-h-[500px] rounded"
          ></iframe>

          <!-- Image Preview -->
          <img
            v-else-if="documentPreview.type.startsWith('image/')"
            :src="documentPreview.url"
            :alt="documentPreview.filename"
            class="max-w-full max-h-full mx-auto rounded"
          />

          <!-- Text Preview -->
          <pre
            v-else-if="documentPreview.type.startsWith('text/')"
            class="whitespace-pre-wrap text-sm bg-white p-4 rounded overflow-auto max-h-[500px]"
          >{{ documentPreview.textContent }}</pre>

          <!-- Other files - show download option -->
          <div v-else class="text-center py-12">
            <svg class="w-16 h-16 mx-auto text-gray-400 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
            </svg>
            <p class="text-gray-600 mb-2">Preview not available for this file type</p>
            <p class="text-sm text-gray-500">Click download to save the decrypted file</p>
          </div>
        </div>

        <!-- Actions -->
        <div class="flex gap-3 mt-4">
          <button
            @click="closePreview"
            class="flex-1 px-4 py-2 bg-gray-200 text-gray-800 rounded-lg font-semibold hover:bg-gray-300"
          >
            Close
          </button>
          <button
            @click="downloadDecryptedFile"
            class="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg font-semibold hover:bg-blue-700"
          >
            Download
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import blockchain from '../utils/blockchain.js'
import { deployStockToken, deployStockAMM } from '../utils/contractDeployer.js'
import toast from '../utils/toast.js'
import { confirm } from '../utils/confirm.js'
import { uploadEncryptedToIPFS, downloadAndDecryptFromIPFS } from '../utils/encryptedIPFS.js'
import { getPublicKeyFromSigner } from '../utils/encryption.js'
import { getOrPromptKey, getPublicKey, hasKey, getKeyAddress } from '../utils/keyManager.js'

export default {
  name: 'CompanyDashboard',
  setup() {
    const isLoading = ref(true)
    const isProcessing = ref(false)
    const company = ref(null)

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

    // Encrypted document upload state
    const showUploadModal = ref(false)
    const encryptedDocuments = ref([])
    const loadingDocs = ref(false)
    const uploadForm = ref({
      file: null,
      docType: 'prospectus',
      recipientAddresses: ''
    })
    const isUploading = ref(false)
    const uploadProgress = ref(0)
    const viewingDocId = ref(null)
    const documentPreview = ref(null)
    const showPreviewModal = ref(false)

    const hasToken = computed(() => {
      return company.value?.stockToken && company.value.stockToken !== '0x0000000000000000000000000000000000000000'
    })

    const hasAMM = computed(() => {
      return company.value?.ammPool && company.value.ammPool !== '0x0000000000000000000000000000000000000000'
    })

    const initialPrice = computed(() => {
      if (!liquidityForm.value.stockAmount || !liquidityForm.value.baseAmount) return '0'
      return (parseFloat(liquidityForm.value.baseAmount) / parseFloat(liquidityForm.value.stockAmount)).toFixed(2)
    })

    const loadCompany = async () => {
      try {
        const account = await blockchain.signer.getAddress()
        const companyData = await blockchain.getCompanyByOwner(account)

        if (companyData) {
          company.value = companyData

          // Pre-fill token form
          tokenForm.value.name = `${companyData.name} Token`
          tokenForm.value.symbol = companyData.symbol
        }
      } catch (error) {
        console.error('Error loading company:', error)
      } finally {
        isLoading.value = false
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

      isProcessing.value = true

      try {
        toast.info('Deploying stock token... Please confirm in MetaMask')

        // Deploy token
        const tokenAddress = await deployStockToken(blockchain.signer, {
          name: tokenForm.value.name,
          symbol: tokenForm.value.symbol,
          decimals: tokenForm.value.decimals,
          totalSupply: tokenForm.value.totalSupply,
          companyName: company.value.name,
          ipfsCid: company.value.ipfsProspectus || 'QmDefault'
        })

        toast.success(`Token deployed at ${tokenAddress}`, 'Token Deployed!')

        // Register token in registry
        toast.info('Registering token in registry...')
        const registry = blockchain.getRegistry()
        const tx = await registry.set_stock_token(company.value.id, tokenAddress)
        await tx.wait()

        toast.success('Token registered successfully!', 'Success')

        showTokenModal.value = false
        await loadCompany()
      } catch (error) {
        console.error('Error deploying token:', error)
        toast.txError(error, 'Deployment Failed', 'Failed to deploy token')
      } finally {
        isProcessing.value = false
      }
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

      isProcessing.value = true

      try {
        toast.info('Deploying AMM pool... Please confirm in MetaMask')

        // Deploy AMM
        const ammAddress = await deployStockAMM(blockchain.signer, ammForm.value.feeRate)

        toast.success(`AMM deployed at ${ammAddress}`, 'AMM Deployed!')

        // Register AMM in registry
        toast.info('Registering AMM in registry...')
        const registry = blockchain.getRegistry()
        const tx = await registry.set_amm_pool(company.value.id, ammAddress)
        await tx.wait()

        toast.success('AMM registered successfully!', 'Success')

        showAMMModal.value = false
        await loadCompany()
      } catch (error) {
        console.error('Error deploying AMM:', error)
        toast.txError(error, 'Deployment Failed', 'Failed to deploy AMM')
      } finally {
        isProcessing.value = false
      }
    }

    const initializeLiquidity = async () => {
      const confirmed = await confirm({
        title: 'Add Initial Liquidity',
        message: `Add ${liquidityForm.value.stockAmount} ${company.value.symbol} and ${liquidityForm.value.baseAmount} BUSD?`,
        details: `Initial price: ${initialPrice.value} BUSD per ${company.value.symbol}`,
        type: 'warning',
        confirmText: 'Add Liquidity',
        cancelText: 'Cancel'
      })

      if (!confirmed) return

      isProcessing.value = true

      try {
        const stockToken = blockchain.getStockToken(company.value.stockToken)
        const baseToken = blockchain.getBaseToken()
        const amm = blockchain.getAMM(company.value.ammPool)

        // Approve tokens
        toast.txStep('Approve Stock Tokens', `Allow AMM to use your ${company.value.symbol} tokens`)
        let tx = await stockToken.approve(company.value.ammPool, liquidityForm.value.stockAmount)
        toast.txPending('Approving stock tokens')
        await tx.wait()
        toast.txConfirmed('Stock tokens approved')

        toast.txStep('Approve BUSD', 'Allow AMM to use your BUSD tokens')
        tx = await baseToken.approve(company.value.ammPool, liquidityForm.value.baseAmount)
        toast.txPending('Approving BUSD')
        await tx.wait()
        toast.txConfirmed('BUSD approved')

        // Initialize pool
        toast.txStep('Initialize Pool', 'Adding initial liquidity to the trading pool')
        tx = await amm.init_pool(
          company.value.stockToken,
          await baseToken.getAddress(),
          liquidityForm.value.stockAmount,
          liquidityForm.value.baseAmount
        )
        toast.txPending('Initializing pool')
        await tx.wait()

        toast.txConfirmed(
          'Pool initialized!',
          `Price: ${initialPrice.value} BUSD per ${company.value.symbol}`
        )

        showLiquidityModal.value = false
        await loadCompany()
      } catch (error) {
        console.error('Error initializing liquidity:', error)
        toast.txError(error, 'Initialization Failed', 'Failed to initialize pool')
      } finally {
        isProcessing.value = false
      }
    }

    const loadEncryptedDocuments = async () => {
      if (!company.value?.id) return

      loadingDocs.value = true
      try {
        const docs = await blockchain.getCompanyEncryptedDocuments(parseInt(company.value.id))
        encryptedDocuments.value = docs
      } catch (error) {
        console.warn('Could not load encrypted documents:', error)
      } finally {
        loadingDocs.value = false
      }
    }

    const handleFileSelect = (event) => {
      uploadForm.value.file = event.target.files[0]
    }

    const uploadEncryptedDocument = async () => {
      if (!uploadForm.value.file || !company.value) return

      isUploading.value = true
      uploadProgress.value = 0

      try {
        // Use global encryption key from environment
        const globalPublicKey = getPublicKey()
        const globalAddress = getKeyAddress()

        if (!globalPublicKey || !globalAddress) {
          toast.error('Encryption key not configured. Set VITE_ENCRYPTION_KEY in .env')
          return
        }

        // Build recipients list using global key
        const recipients = [{ address: globalAddress, publicKey: globalPublicKey }]

        uploadProgress.value = 20
        toast.info('Encrypting and uploading to IPFS...')

        // Encrypt and upload to IPFS
        const { cid, encryptedKeys, metadata } = await uploadEncryptedToIPFS(
          uploadForm.value.file,
          recipients
        )

        uploadProgress.value = 60
        toast.info('Registering document on blockchain...')

        // Register document on-chain
        const docId = await blockchain.uploadEncryptedDocument(
          cid,
          uploadForm.value.docType,
          metadata.originalName,
          metadata.originalSize,
          parseInt(company.value.id)
        )

        uploadProgress.value = 80

        // Add encrypted keys for recipients
        if (encryptedKeys.length > 0) {
          for (const keyData of encryptedKeys) {
            await blockchain.addDocumentRecipient(docId, keyData.recipient, keyData.encryptedKey)
          }
        }

        uploadProgress.value = 100
        toast.success(`Document uploaded successfully! ID: ${docId}`)

        // Reset form and reload documents
        showUploadModal.value = false
        uploadForm.value = { file: null, docType: 'prospectus', recipientAddresses: '' }
        await loadEncryptedDocuments()

      } catch (error) {
        console.error('Error uploading encrypted document:', error)
        toast.txError(error, 'Upload Failed', 'Failed to upload encrypted document')
      } finally {
        isUploading.value = false
        uploadProgress.value = 0
      }
    }

    const viewDocument = async (doc) => {
      viewingDocId.value = doc.id

      try {
        toast.info('Decrypting document...')

        // Get the encrypted key using global key address
        const globalAddress = getKeyAddress()
        console.log('📄 Viewing document:', doc.id, 'for global key address:', globalAddress)

        const encryptedKey = await blockchain.getEncryptedKey(doc.id, globalAddress)
        console.log('🔑 Encrypted key:', encryptedKey)

        if (!encryptedKey || !encryptedKey.ciphertext || encryptedKey.ciphertext === '0x' || encryptedKey.ciphertext === '') {
          toast.error('You do not have access to this document')
          viewingDocId.value = null
          return
        }

        // Get private key from key manager (prompts once per session)
        const privateKey = getOrPromptKey()

        if (!privateKey) {
          toast.warning('Decryption cancelled')
          viewingDocId.value = null
          return
        }

        const cid = doc.ipfsCid || doc.cid
        console.log('🔓 Starting decryption for CID:', cid)

        // Download and decrypt
        const result = await downloadAndDecryptFromIPFS(
          cid,
          encryptedKey,
          privateKey,
          {
            originalName: doc.originalName,
            originalType: guessContentType(doc.originalName)
          }
        )

        console.log('✅ Decryption successful, showing preview modal')

        // Store preview data
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
        console.error('Error viewing document:', error)
        toast.error('Failed to decrypt document: ' + error.message)
      } finally {
        viewingDocId.value = null
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
        'txt': 'text/plain',
        'html': 'text/html',
        'json': 'application/json'
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

    const revokeDocument = async (doc) => {
      const confirmed = await confirm({
        title: 'Revoke Document',
        message: `Revoke access to "${doc.originalName}"?`,
        details: 'This will prevent anyone from accessing this document.',
        type: 'warning',
        confirmText: 'Revoke',
        cancelText: 'Cancel'
      })

      if (!confirmed) return

      try {
        await blockchain.revokeEncryptedDocument(doc.id)
        toast.success('Document revoked successfully')
        await loadEncryptedDocuments()
      } catch (error) {
        toast.txError(error, 'Revoke Failed', 'Failed to revoke document')
      }
    }

    onMounted(async () => {
      if (!blockchain.signer) {
        toast.warning('Please connect your wallet first')
        return
      }
      await loadCompany()
      await loadEncryptedDocuments()
    })

    return {
      isLoading,
      isProcessing,
      company,
      hasToken,
      hasAMM,
      showTokenModal,
      showAMMModal,
      showLiquidityModal,
      tokenForm,
      ammForm,
      liquidityForm,
      initialPrice,
      deployToken,
      deployAMM,
      initializeLiquidity,
      // Encrypted documents
      showUploadModal,
      encryptedDocuments,
      loadingDocs,
      uploadForm,
      isUploading,
      uploadProgress,
      handleFileSelect,
      uploadEncryptedDocument,
      revokeDocument,
      // Document viewing
      viewingDocId,
      viewDocument,
      showPreviewModal,
      documentPreview,
      closePreview,
      downloadDecryptedFile
    }
  }
}
</script>
