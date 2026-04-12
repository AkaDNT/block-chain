<template>
  <div class="max-w-2xl mx-auto">
    <!-- Show KYC status if exists -->
    <div v-if="kycStatus">
      <!-- Pending Status -->
      <div v-if="kycStatus.status === 'PENDING'" class="bg-yellow-50 border border-yellow-200 rounded-lg p-6 mb-6">
        <div class="flex items-center justify-center gap-3 mb-4">
          <div class="w-4 h-4 bg-yellow-500 rounded-full animate-pulse"></div>
          <h2 class="text-2xl font-bold text-gray-900">KYC Verification Pending</h2>
        </div>
        <div class="text-center space-y-2">
          <p class="text-gray-700">Your KYC submission is being reviewed by our team.</p>
          <p class="text-sm text-gray-600">Submitted: {{ formatDate(kycStatus.createdAt) }}</p>
          <div class="mt-4 p-4 bg-white rounded-lg border border-yellow-200">
            <p class="text-sm font-semibold text-gray-700 mb-2">Submitted Information:</p>
            <div class="text-left text-sm space-y-1">
              <p><span class="font-medium">Name:</span> {{ kycStatus.fullName }}</p>
              <p><span class="font-medium">Email:</span> {{ kycStatus.email }}</p>
              <p><span class="font-medium">Country:</span> {{ kycStatus.country }}</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Verified Status -->
      <div v-else-if="kycStatus.status === 'VERIFIED'" class="bg-green-50 border border-green-200 rounded-lg p-6 mb-6">
        <div class="flex items-center justify-center gap-3 mb-4">
          <svg class="w-8 h-8 text-green-600" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"></path>
          </svg>
          <h2 class="text-2xl font-bold text-green-900">KYC Verified!</h2>
        </div>
        <div class="text-center space-y-2">
          <p class="text-gray-700">Your account is verified and ready to trade.</p>
          <p class="text-sm text-gray-600">Verified: {{ formatDate(kycStatus.verifiedAt) }}</p>
        </div>
      </div>

      <!-- Rejected Status -->
      <div v-else-if="kycStatus.status === 'REJECTED'" class="bg-red-50 border border-red-200 rounded-lg p-6 mb-6">
        <div class="flex items-center justify-center gap-3 mb-4">
          <svg class="w-8 h-8 text-red-600" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd"></path>
          </svg>
          <h2 class="text-2xl font-bold text-red-900">KYC Rejected</h2>
        </div>
        <div class="text-center space-y-3">
          <div class="p-4 bg-white rounded-lg border border-red-200">
            <p class="text-sm font-semibold text-gray-700 mb-2">Rejection Reason:</p>
            <p class="text-red-800">{{ kycStatus.rejectionReason }}</p>
          </div>
          <p class="text-sm text-gray-600">You can submit a new KYC request below with updated information.</p>
        </div>
      </div>
    </div>

    <!-- KYC Form (show if no KYC or rejected) -->
    <div v-if="!kycStatus || kycStatus.status === 'REJECTED'">
      <div v-if="!showForm" class="bg-blue-50 border border-blue-200 rounded-lg p-6 text-center">
        <svg class="w-16 h-16 mx-auto text-blue-600 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"></path>
        </svg>
        <h2 class="text-2xl font-bold text-gray-900 mb-2">Trader Verification Required</h2>
        <p class="text-gray-700 mb-4">
          Complete KYC verification to start trading stocks on our platform.
        </p>
        <button
          @click="showForm = true"
          class="bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 px-6 rounded-lg transition-all"
        >
          Start KYC Verification
        </button>
      </div>

      <div v-else class="bg-white rounded-lg shadow-lg border border-gray-200 p-6">
        <div class="flex items-center justify-between mb-6">
          <h2 class="text-2xl font-bold text-gray-900">KYC Verification</h2>
          <button @click="showForm = false" class="text-gray-500 hover:text-gray-700">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
            </svg>
          </button>
        </div>

        <form @submit.prevent="submitKYC" class="space-y-6">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              Full Legal Name <span class="text-red-500">*</span>
            </label>
            <input
              v-model="form.fullName"
              type="text"
              required
              class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="John Doe"
            />
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              Email Address <span class="text-red-500">*</span>
            </label>
            <input
              v-model="form.email"
              type="email"
              required
              class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="john@example.com"
            />
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              Country of Residence <span class="text-red-500">*</span>
            </label>
            <input
              v-model="form.country"
              type="text"
              required
              class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="United States"
            />
          </div>

          <div class="border-t border-gray-200 pt-6">
            <h3 class="text-lg font-semibold text-gray-900 mb-4">Encrypted Document Upload</h3>
            <p class="text-sm text-gray-600 mb-4">
              Upload clear photos of your identity documents. All documents are <strong>encrypted client-side</strong> before being stored on IPFS. Only authorized administrators can decrypt and view them.
            </p>

            <div class="space-y-4">
              <!-- ID Document Upload -->
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">
                  ID Document (Passport/Driver's License) <span class="text-red-500">*</span>
                </label>
                <input
                  @change="handleFileUpload($event, 'idDocument')"
                  type="file"
                  accept="image/*,.pdf"
                  class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm"
                  :disabled="isSubmitting"
                />
                <p class="text-xs text-gray-500 mt-1">Upload a clear photo or scan of your government-issued ID</p>

                <!-- Upload Status -->
                <div v-if="uploadStatus.idDocument" class="mt-2 p-2 rounded-lg flex items-center gap-2"
                  :class="{
                    'bg-blue-50 border border-blue-200': uploadStatus.idDocument === 'uploading',
                    'bg-green-50 border border-green-200': uploadStatus.idDocument === 'completed',
                    'bg-red-50 border border-red-200': uploadStatus.idDocument === 'error'
                  }">
                  <!-- Uploading -->
                  <svg v-if="uploadStatus.idDocument === 'uploading'" class="animate-spin h-4 w-4 text-blue-600" fill="none" viewBox="0 0 24 24">
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  <!-- Completed -->
                  <svg v-else-if="uploadStatus.idDocument === 'completed'" class="w-4 h-4 text-green-600" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"></path>
                  </svg>
                  <!-- Error -->
                  <svg v-else-if="uploadStatus.idDocument === 'error'" class="h-4 w-4 text-red-600" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd"></path>
                  </svg>
                  <div class="flex-1 min-w-0">
                    <p class="text-xs font-medium truncate"
                      :class="{
                        'text-blue-800': uploadStatus.idDocument === 'uploading',
                        'text-green-800': uploadStatus.idDocument === 'completed',
                        'text-red-800': uploadStatus.idDocument === 'error'
                      }">
                      {{ uploadedFiles.idDocument?.file?.name || 'ID Document' }}
                    </p>
                    <p v-if="uploadStatus.idDocument === 'uploading'" class="text-xs text-blue-600">🔐 Encrypting & uploading to IPFS...</p>
                    <p v-else-if="uploadStatus.idDocument === 'completed'" class="text-xs text-green-600 font-mono truncate">🔒 Encrypted - IPFS: {{ uploadedFiles.idDocument?.cid }}</p>
                    <p v-else-if="uploadStatus.idDocument === 'error'" class="text-xs text-red-600">{{ uploadErrors.idDocument }}</p>
                  </div>
                </div>
              </div>

              <!-- Selfie Upload -->
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">
                  Selfie with ID <span class="text-red-500">*</span>
                </label>
                <input
                  @change="handleFileUpload($event, 'selfie')"
                  type="file"
                  accept="image/*"
                  class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm"
                  :disabled="isSubmitting"
                />
                <p class="text-xs text-gray-500 mt-1">Upload a selfie holding your ID next to your face</p>

                <!-- Upload Status -->
                <div v-if="uploadStatus.selfie" class="mt-2 p-2 rounded-lg flex items-center gap-2"
                  :class="{
                    'bg-blue-50 border border-blue-200': uploadStatus.selfie === 'uploading',
                    'bg-green-50 border border-green-200': uploadStatus.selfie === 'completed',
                    'bg-red-50 border border-red-200': uploadStatus.selfie === 'error'
                  }">
                  <!-- Uploading -->
                  <svg v-if="uploadStatus.selfie === 'uploading'" class="animate-spin h-4 w-4 text-blue-600" fill="none" viewBox="0 0 24 24">
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  <!-- Completed -->
                  <svg v-else-if="uploadStatus.selfie === 'completed'" class="w-4 h-4 text-green-600" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"></path>
                  </svg>
                  <!-- Error -->
                  <svg v-else-if="uploadStatus.selfie === 'error'" class="h-4 w-4 text-red-600" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd"></path>
                  </svg>
                  <div class="flex-1 min-w-0">
                    <p class="text-xs font-medium truncate"
                      :class="{
                        'text-blue-800': uploadStatus.selfie === 'uploading',
                        'text-green-800': uploadStatus.selfie === 'completed',
                        'text-red-800': uploadStatus.selfie === 'error'
                      }">
                      {{ uploadedFiles.selfie?.file?.name || 'Selfie' }}
                    </p>
                    <p v-if="uploadStatus.selfie === 'uploading'" class="text-xs text-blue-600">🔐 Encrypting & uploading to IPFS...</p>
                    <p v-else-if="uploadStatus.selfie === 'completed'" class="text-xs text-green-600 font-mono truncate">🔒 Encrypted - IPFS: {{ uploadedFiles.selfie?.cid }}</p>
                    <p v-else-if="uploadStatus.selfie === 'error'" class="text-xs text-red-600">{{ uploadErrors.selfie }}</p>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div class="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
            <div class="flex gap-3">
              <svg class="w-5 h-5 text-yellow-600 flex-shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd"></path>
              </svg>
              <div class="text-sm text-yellow-800">
                <p class="font-semibold mb-1">Important:</p>
                <ul class="list-disc list-inside space-y-1">
                  <li>All information must be accurate and match your ID</li>
                  <li>Documents must be clear and legible</li>
                  <li>Verification typically takes 1-3 business days</li>
                </ul>
              </div>
            </div>
          </div>

          <div class="flex gap-4">
            <button
              type="button"
              @click="showForm = false"
              class="flex-1 px-6 py-3 border border-gray-300 rounded-lg text-gray-700 font-semibold hover:bg-gray-50 transition-all"
            >
              Cancel
            </button>
            <button
              type="submit"
              :disabled="!canSubmit"
              class="flex-1 bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 px-6 rounded-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <span v-if="isSubmitting" class="flex items-center justify-center">
                <svg class="animate-spin -ml-1 mr-2 h-5 w-5 text-white" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Submitting...
              </span>
              <span v-else>Submit KYC</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import blockchain from '../utils/blockchain.js'
import toast from '../utils/toast.js'
import { uploadEncryptedToIPFS } from '../utils/encryptedIPFS.js'
import { getPublicKey, getKeyAddress } from '../utils/keyManager.js'

export default {
  name: 'TraderKYC',
  emits: ['kyc-submitted', 'form-visibility-changed'],
  setup(props, { emit }) {
    const showForm = ref(false)
    const isSubmitting = ref(false)
    const kycStatus = ref(null)

    const form = ref({
      fullName: '',
      email: '',
      country: '',
      ipfsIdDocument: '',
      ipfsSelfie: ''
    })

    // File upload tracking
    const uploadStatus = ref({
      idDocument: null,
      selfie: null
    })
    const uploadErrors = ref({
      idDocument: null,
      selfie: null
    })
    const uploadedFiles = ref({
      idDocument: null,
      selfie: null
    })

    const canSubmit = computed(() => {
      return form.value.fullName &&
             form.value.email &&
             form.value.country &&
             uploadedFiles.value.idDocument &&
             uploadedFiles.value.selfie &&
             !isSubmitting.value
    })

    const checkKYCStatus = async () => {
      try {
        const address = await blockchain.signer.getAddress()
        const kyc = await blockchain.getTraderKYC(address)
        kycStatus.value = kyc
        console.log('KYC Status:', kyc)
      } catch (error) {
        console.log('No KYC found or error:', error)
        kycStatus.value = null
      }
    }

    const handleFileUpload = async (event, type) => {
      const file = event.target.files[0]
      if (!file) return

      // Set uploading status
      uploadStatus.value[type] = 'uploading'
      uploadErrors.value[type] = null

      try {
        // Use global encryption key from environment
        const globalPublicKey = getPublicKey()
        const globalAddress = getKeyAddress()

        if (!globalPublicKey || !globalAddress) {
          throw new Error('Encryption key not configured. Set VITE_ENCRYPTION_KEY in .env')
        }

        // Encrypt and upload to IPFS
        const recipients = [{ address: globalAddress, publicKey: globalPublicKey }]
        console.log(`🔐 Encrypting and uploading ${type}...`)

        const { cid, encryptedKeys, metadata } = await uploadEncryptedToIPFS(file, recipients)

        // Update status to completed
        uploadStatus.value[type] = 'completed'
        uploadedFiles.value[type] = {
          file: file,
          cid: cid,
          encryptedKeys: encryptedKeys,
          metadata: metadata
        }

        console.log(`✅ Encrypted and uploaded ${type}:`, cid)

      } catch (error) {
        // Update status to error
        uploadStatus.value[type] = 'error'
        uploadErrors.value[type] = error.message
        console.error(`Error uploading ${type}:`, error)
      }
    }

    const submitKYC = async () => {
      if (!blockchain.signer) {
        toast.warning('Please connect your wallet first!')
        return
      }

      if (!canSubmit.value) {
        toast.warning('Please fill all fields and upload required documents!')
        return
      }

      isSubmitting.value = true

      try {
        console.log('Submitting KYC...', form.value)

        // Submit KYC to TraderRegistry
        const kycId = await blockchain.submitTraderKYC({
          fullName: form.value.fullName,
          email: form.value.email,
          country: form.value.country,
          ipfsIdDocument: uploadedFiles.value.idDocument.cid,
          ipfsSelfie: uploadedFiles.value.selfie.cid
        })

        // Register encrypted documents in EncryptedDocRegistry
        console.log('Registering encrypted documents on-chain...')
        const docTypes = [
          { key: 'idDocument', type: 'kyc_id_document' },
          { key: 'selfie', type: 'kyc_selfie' }
        ]

        for (const { key, type } of docTypes) {
          const uploaded = uploadedFiles.value[key]
          if (uploaded?.cid && uploaded?.encryptedKeys) {
            try {
              // Register document in EncryptedDocRegistry (companyId = 0 for KYC docs)
              const docId = await blockchain.uploadEncryptedDocument(
                uploaded.cid,
                type,
                uploaded.metadata?.originalName || uploaded.file.name,
                uploaded.metadata?.originalSize || uploaded.file.size,
                0 // companyId = 0 for trader KYC documents
              )

              // Add encrypted key for the admin to decrypt
              if (uploaded.encryptedKeys.length > 0) {
                for (const keyData of uploaded.encryptedKeys) {
                  await blockchain.addDocumentRecipient(docId, keyData.recipient, keyData.encryptedKey)
                }
              }

              console.log(`✅ Registered encrypted ${type} with doc ID: ${docId}`)
            } catch (err) {
              console.warn(`Could not register ${type} in EncryptedDocRegistry:`, err)
            }
          }
        }

        toast.success('KYC submitted successfully! Documents are encrypted. Please wait for verification.', 'KYC Submitted')

        // Reset form
        form.value = {
          fullName: '',
          email: '',
          country: '',
          ipfsIdDocument: '',
          ipfsSelfie: ''
        }
        uploadedFiles.value = {
          idDocument: null,
          selfie: null
        }
        uploadStatus.value = {
          idDocument: null,
          selfie: null
        }
        uploadErrors.value = {
          idDocument: null,
          selfie: null
        }

        showForm.value = false
        emit('kyc-submitted')

        // Refresh status
        await checkKYCStatus()
      } catch (error) {
        console.error('Error submitting KYC:', error)
        toast.txError(error, 'KYC Submission Failed', 'Failed to submit KYC')
      } finally {
        isSubmitting.value = false
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

    onMounted(async () => {
      await checkKYCStatus()
    })

    return {
      showForm,
      isSubmitting,
      kycStatus,
      form,
      uploadStatus,
      uploadErrors,
      uploadedFiles,
      canSubmit,
      handleFileUpload,
      submitKYC,
      formatDate
    }
  }
}
</script>
