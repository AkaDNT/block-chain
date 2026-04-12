<template>
  <div class="max-w-6xl mx-auto">
    <h1 class="text-3xl font-bold mb-6">Trader KYC Verification</h1>

    <!-- Stats -->
    <div class="grid grid-cols-4 gap-4 mb-6">
      <div class="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
        <div class="text-2xl font-bold text-gray-900">{{ stats.total }}</div>
        <div class="text-sm text-gray-600">Total Requests</div>
      </div>
      <div class="bg-yellow-50 rounded-lg shadow-sm border border-yellow-200 p-4">
        <div class="text-2xl font-bold text-yellow-900">{{ stats.pending }}</div>
        <div class="text-sm text-yellow-700">Pending</div>
      </div>
      <div class="bg-green-50 rounded-lg shadow-sm border border-green-200 p-4">
        <div class="text-2xl font-bold text-green-900">{{ stats.verified }}</div>
        <div class="text-sm text-green-700">Verified</div>
      </div>
      <div class="bg-red-50 rounded-lg shadow-sm border border-red-200 p-4">
        <div class="text-2xl font-bold text-red-900">{{ stats.rejected }}</div>
        <div class="text-sm text-red-700">Rejected</div>
      </div>
    </div>

    <!-- Filter Tabs -->
    <div class="bg-white rounded-lg shadow-sm border border-gray-200 mb-4">
      <div class="flex border-b border-gray-200">
        <button
          v-for="filter in filters"
          :key="filter.value"
          @click="currentFilter = filter.value"
          :class="currentFilter === filter.value ? 'border-blue-600 text-blue-600' : 'border-transparent text-gray-600 hover:text-gray-900'"
          class="px-6 py-3 border-b-2 font-semibold text-sm transition"
        >
          {{ filter.label }}
        </button>
      </div>
    </div>

    <!-- Requests List -->
    <div class="space-y-4">
      <div
        v-for="request in filteredRequests"
        :key="request.id"
        class="bg-white rounded-lg shadow-sm border border-gray-200 p-5"
      >
        <div class="flex items-start justify-between">
          <div class="flex-1">
            <div class="flex items-center gap-3 mb-2">
              <span
                :class="{
                  'bg-yellow-100 text-yellow-800': request.status === 'PENDING',
                  'bg-green-100 text-green-800': request.status === 'VERIFIED' && request.verifiedOnChain,
                  'bg-orange-100 text-orange-800': request.status === 'VERIFIED' && !request.verifiedOnChain,
                  'bg-red-100 text-red-800': request.status === 'REJECTED',
                  'bg-gray-100 text-gray-800': request.status === 'REVOKED'
                }"
                class="px-3 py-1 rounded-full text-xs font-semibold"
              >
                {{ request.status }}
                <span v-if="request.status === 'VERIFIED' && !request.verifiedOnChain">(Not on-chain)</span>
              </span>
              <span class="text-sm text-gray-500">KYC #{{ request.id }}</span>
            </div>

            <div class="grid grid-cols-3 gap-4 mb-3">
              <div>
                <label class="text-xs font-medium text-gray-500">Full Name</label>
                <p class="text-sm font-semibold text-gray-900">{{ request.fullName }}</p>
              </div>
              <div>
                <label class="text-xs font-medium text-gray-500">Email</label>
                <p class="text-sm text-gray-900">{{ request.email }}</p>
              </div>
              <div>
                <label class="text-xs font-medium text-gray-500">Country</label>
                <p class="text-sm text-gray-900">{{ request.country }}</p>
              </div>
            </div>

            <div class="mb-3">
              <label class="text-xs font-medium text-gray-500">Trader Address</label>
              <p class="text-sm font-mono text-gray-900">{{ request.trader }}</p>
            </div>

            <!-- KYC Documents (Encrypted) -->
            <div class="mb-3">
              <label class="text-xs font-medium text-gray-500 mb-2 block">🔐 Encrypted KYC Documents</label>
              <div class="grid grid-cols-2 gap-2">
                <button
                  @click="viewEncryptedDocument('idDocument', request.ipfsIdDocument, request)"
                  :disabled="viewingDoc === `${request.id}-idDocument`"
                  class="flex items-center justify-center gap-1 px-3 py-2 bg-purple-50 text-purple-700 rounded-lg hover:bg-purple-100 transition text-xs font-medium disabled:opacity-50"
                >
                  <svg v-if="viewingDoc === `${request.id}-idDocument`" class="animate-spin h-4 w-4" fill="none" viewBox="0 0 24 24">
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  <svg v-else class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"></path>
                  </svg>
                  {{ viewingDoc === `${request.id}-idDocument` ? 'Decrypting...' : 'Decrypt ID Doc' }}
                </button>
                <button
                  @click="viewEncryptedDocument('selfie', request.ipfsSelfie, request)"
                  :disabled="viewingDoc === `${request.id}-selfie`"
                  class="flex items-center justify-center gap-1 px-3 py-2 bg-purple-50 text-purple-700 rounded-lg hover:bg-purple-100 transition text-xs font-medium disabled:opacity-50"
                >
                  <svg v-if="viewingDoc === `${request.id}-selfie`" class="animate-spin h-4 w-4" fill="none" viewBox="0 0 24 24">
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  <svg v-else class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"></path>
                  </svg>
                  {{ viewingDoc === `${request.id}-selfie` ? 'Decrypting...' : 'Decrypt Selfie' }}
                </button>
              </div>
              <p class="text-xs text-gray-500 mt-1">Documents are encrypted. Click to decrypt and view.</p>
            </div>

            <div class="grid grid-cols-2 gap-4 text-xs text-gray-600">
              <div>
                <span class="font-medium">Submitted:</span> {{ formatDate(request.createdAt) }}
              </div>
              <div v-if="request.processedAt">
                <span class="font-medium">Processed:</span> {{ formatDate(request.processedAt) }}
              </div>
            </div>

            <div v-if="request.rejectionReason" class="mt-3 p-3 bg-red-50 rounded-lg border border-red-200">
              <label class="text-xs font-medium text-red-700">Rejection Reason</label>
              <p class="text-sm text-red-900">{{ request.rejectionReason }}</p>
            </div>
          </div>

          <!-- Actions -->
          <div v-if="request.status === 'PENDING'" class="flex gap-2 ml-4">
            <button
              @click="verifyRequest(request)"
              class="px-4 py-2 bg-green-600 text-white text-sm font-semibold rounded-lg hover:bg-green-700 transition"
              :disabled="isProcessing"
            >
              Verify
            </button>
            <button
              @click="openRejectModal(request)"
              class="px-4 py-2 bg-red-600 text-white text-sm font-semibold rounded-lg hover:bg-red-700 transition"
              :disabled="isProcessing"
            >
              Reject
            </button>
          </div>

          <div v-else-if="request.status === 'VERIFIED'" class="ml-4 space-y-2">
            <button
              @click="revokeTrader(request)"
              class="px-4 py-2 bg-orange-600 text-white text-sm font-semibold rounded-lg hover:bg-orange-700 transition disabled:opacity-50 disabled:cursor-not-allowed"
              :disabled="isProcessing || !request.verifiedOnChain"
            >
              Revoke
            </button>
            <p v-if="!request.verifiedOnChain" class="text-xs text-orange-600 text-center">
              Not verified on-chain (cannot revoke)
            </p>
          </div>
        </div>
      </div>

      <div v-if="filteredRequests.length === 0" class="text-center py-12 bg-white rounded-lg shadow-sm border border-gray-200">
        <svg class="w-16 h-16 mx-auto text-gray-400 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
        </svg>
        <p class="text-gray-600">No {{ currentFilter.toLowerCase() }} requests found</p>
      </div>
    </div>

    <!-- Reject Modal -->
    <div v-if="showRejectModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50" @click.self="showRejectModal = false">
      <div class="bg-white rounded-xl shadow-2xl max-w-md w-full mx-4 p-6">
        <h2 class="text-2xl font-bold mb-4">Reject KYC Request</h2>
        <form @submit.prevent="submitRejection">
          <div class="mb-4">
            <label class="block text-sm font-medium text-gray-700 mb-2">
              Rejection Reason <span class="text-red-500">*</span>
            </label>
            <textarea
              v-model="rejectionReason"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent"
              rows="4"
              placeholder="Explain why this KYC is being rejected..."
              required
            ></textarea>
          </div>

          <div class="flex gap-3">
            <button
              type="button"
              @click="showRejectModal = false"
              class="flex-1 px-4 py-2 bg-gray-100 text-gray-700 rounded-lg font-semibold hover:bg-gray-200 transition"
            >
              Cancel
            </button>
            <button
              type="submit"
              :disabled="isProcessing || !rejectionReason"
              class="flex-1 px-4 py-2 bg-red-600 text-white rounded-lg font-semibold hover:bg-red-700 transition disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <span v-if="isProcessing">Rejecting...</span>
              <span v-else>Reject KYC</span>
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Document Preview Modal -->
    <div v-if="showPreviewModal && documentPreview" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg p-6 max-w-4xl w-full mx-4 max-h-[90vh] flex flex-col">
        <div class="flex justify-between items-center mb-4">
          <div>
            <h3 class="text-xl font-bold">{{ documentPreview.filename }}</h3>
            <p class="text-sm text-gray-500">KYC #{{ documentPreview.requestId }} - {{ documentPreview.docType === 'idDocument' ? 'ID Document' : 'Selfie with ID' }}</p>
          </div>
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
            <p class="text-gray-600 mb-2">Preview not available for this file type</p>
            <p class="text-sm text-gray-500">Click download to save the file</p>
          </div>
        </div>
        <div class="flex gap-3 mt-4">
          <button @click="closePreview" class="flex-1 px-4 py-2 bg-gray-200 text-gray-800 rounded-lg font-semibold hover:bg-gray-300">Close</button>
          <button @click="downloadDecryptedFile" class="flex-1 px-4 py-2 bg-purple-600 text-white rounded-lg font-semibold hover:bg-purple-700">Download</button>
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
import { downloadAndDecryptFromIPFS } from '../utils/encryptedIPFS.js'
import { getOrPromptKey, getKeyAddress } from '../utils/keyManager.js'

export default {
  name: 'AdminMinterRequests',
  setup() {

    const requests = ref([])
    const currentFilter = ref('ALL')
    const isProcessing = ref(false)
    const showRejectModal = ref(false)
    const selectedRequest = ref(null)
    const rejectionReason = ref('')

    // Document viewing state
    const viewingDoc = ref(null)
    const showPreviewModal = ref(false)
    const documentPreview = ref(null)

    const filters = [
      { label: 'All Requests', value: 'ALL' },
      { label: 'Pending', value: 'PENDING' },
      { label: 'Verified', value: 'VERIFIED' },
      { label: 'Rejected', value: 'REJECTED' }
    ]

    const stats = computed(() => ({
      total: requests.value.length,
      pending: requests.value.filter(r => r.status === 'PENDING').length,
      verified: requests.value.filter(r => r.status === 'VERIFIED').length,
      rejected: requests.value.filter(r => r.status === 'REJECTED').length
    }))

    const filteredRequests = computed(() => {
      if (currentFilter.value === 'ALL') return requests.value
      return requests.value.filter(r => r.status === currentFilter.value)
    })

    const loadRequests = async () => {
      try {
        const allRequests = await blockchain.getAllTraderKYCs()
        requests.value = allRequests.sort((a, b) => b.createdAt - a.createdAt)
      } catch (error) {
        console.error('Error loading requests:', error)
        toast.txError(error, 'Load Failed', 'Failed to load KYC requests')
      }
    }

    const verifyRequest = async (request) => {
      const confirmed = await confirm({
        title: 'Verify Trader KYC',
        message: `Verify ${request.fullName} (${request.trader})?`,
        type: 'info',
        confirmText: 'Verify',
        cancelText: 'Cancel'
      })

      if (!confirmed) return

      isProcessing.value = true
      try {
        toast.info('Verifying KYC...')
        await blockchain.verifyTraderKYC(request.id)
        toast.success('Trader KYC verified successfully!', 'KYC Verified')
        await loadRequests()
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

    const submitRejection = async () => {
      isProcessing.value = true
      try {
        toast.info('Rejecting KYC...')
        await blockchain.rejectTraderKYC(selectedRequest.value.id, rejectionReason.value)
        toast.success('Trader KYC rejected', 'KYC Rejected')

        showRejectModal.value = false
        selectedRequest.value = null
        rejectionReason.value = ''
        await loadRequests()
      } catch (error) {
        console.error('Error rejecting KYC:', error)
        toast.txError(error, 'Rejection Failed', 'Failed to reject KYC')
      } finally {
        isProcessing.value = false
      }
    }

    const revokeTrader = async (request) => {
      const confirmed = await confirm({
        title: 'Revoke Trader Verification',
        message: `Revoke verification from ${request.fullName}?`,
        details: 'This will remove their ability to trade on the platform.',
        type: 'warning',
        confirmText: 'Revoke',
        cancelText: 'Cancel'
      })

      if (!confirmed) return

      isProcessing.value = true
      try {
        toast.info('Revoking trader verification...')
        await blockchain.revokeTrader(request.trader)
        toast.success('Trader verification revoked', 'Verification Revoked')
        await loadRequests()
      } catch (error) {
        console.error('Error revoking trader:', error)
        toast.txError(error, 'Revocation Failed', 'Failed to revoke verification')
      } finally {
        isProcessing.value = false
      }
    }

    const formatDate = (date) => {
      return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      })
    }

    // View encrypted KYC document
    const viewEncryptedDocument = async (docType, ipfsCid, request) => {
      if (!ipfsCid) {
        toast.warning('No document uploaded')
        return
      }

      viewingDoc.value = `${request.id}-${docType}`

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
          window.open(`http://localhost:8081/ipfs/${ipfsCid}`, '_blank')
          viewingDoc.value = null
          return
        }

        const encryptedKey = await blockchain.getEncryptedKey(doc.id, globalAddress)

        if (!encryptedKey || !encryptedKey.ciphertext || encryptedKey.ciphertext === '0x' || encryptedKey.ciphertext === '') {
          toast.error('You do not have access to decrypt this document')
          viewingDoc.value = null
          return
        }

        // Get private key from key manager
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
          docType,
          requestId: request.id
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

    onMounted(() => {
      loadRequests()
    })

    return {
      requests,
      currentFilter,
      filters,
      stats,
      filteredRequests,
      isProcessing,
      showRejectModal,
      rejectionReason,
      verifyRequest,
      openRejectModal,
      submitRejection,
      revokeTrader,
      formatDate,
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
