<template>
  <div>
    <!-- Pending Request Status -->
    <div v-if="minterRequest && minterRequest.status === 'PENDING'" class="bg-yellow-50 border border-yellow-200 rounded-lg p-6 text-center">
      <div class="flex items-center justify-center gap-2 mb-3">
        <div class="w-3 h-3 bg-yellow-500 rounded-full animate-pulse"></div>
        <span class="text-lg font-semibold text-gray-900">Request Pending</span>
      </div>
      <p class="text-gray-700 mb-2">Your minter request is awaiting admin approval.</p>
      <p class="text-sm text-gray-600">Submitted: {{ formatDate(minterRequest.createdAt) }}</p>
    </div>

    <!-- Rejected Request Status -->
    <div v-else-if="minterRequest && minterRequest.status === 'REJECTED'" class="bg-red-50 border border-red-200 rounded-lg p-6 mb-6">
      <div class="flex items-center justify-center gap-2 mb-3">
        <svg class="w-6 h-6 text-red-600" fill="currentColor" viewBox="0 0 20 20">
          <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd"></path>
        </svg>
        <span class="text-lg font-semibold text-red-900">Request Rejected</span>
      </div>
      <p class="text-red-800 mb-4">{{ minterRequest.rejectionReason }}</p>
      <p class="text-sm text-gray-600 mb-4">You can submit a new request below with updated information.</p>
    </div>

    <!-- Button to open KYC form (shown when form is closed) -->
    <div v-if="(!minterRequest || minterRequest.status !== 'PENDING') && !showForm" class="text-center">
      <button
        @click="showForm = true"
        class="px-6 py-3 bg-blue-600 text-white rounded-lg font-semibold hover:bg-blue-700 transition shadow-md hover:shadow-lg"
      >
        Submit KYC Request
      </button>
    </div>

    <!-- KYC Request Form (Shown when button is clicked) -->
    <div v-if="(!minterRequest || minterRequest.status !== 'PENDING') && showForm" class="bg-white rounded-xl shadow-lg border border-gray-200 p-6">
      <div class="mb-6">
        <h2 class="text-2xl font-bold">Request Minter Access</h2>
        <p class="text-sm text-gray-600 mt-1">Complete KYC verification to request minter privileges</p>
      </div>

      <form @submit.prevent="submitRequest" class="space-y-4">
        <!-- Personal Information -->
        <div class="border-b pb-4">
          <h3 class="text-lg font-semibold mb-3">Personal Information</h3>

          <div class="mb-3">
            <label class="block text-sm font-medium text-gray-700 mb-1">
              Full Legal Name <span class="text-red-500">*</span>
            </label>
            <input
              v-model="kycForm.fullName"
              type="text"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="John Doe"
              required
            />
          </div>

          <div class="mb-3">
            <label class="block text-sm font-medium text-gray-700 mb-1">
              Email Address <span class="text-red-500">*</span>
            </label>
            <input
              v-model="kycForm.email"
              type="email"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="john@example.com"
              required
            />
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">
              Reason for Request <span class="text-red-500">*</span>
            </label>
            <textarea
              v-model="kycForm.reason"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              rows="3"
              placeholder="Explain why you need minter privileges..."
              required
            ></textarea>
          </div>
        </div>

        <!-- KYC Documents -->
        <div class="border-b pb-4">
          <h3 class="text-lg font-semibold mb-3">Identity Verification</h3>

          <div class="mb-3">
            <label class="block text-sm font-medium text-gray-700 mb-1">
              ID Front Photo <span class="text-red-500">*</span>
            </label>
            <input
              @change="handleFileUpload($event, 'idFront')"
              type="file"
              accept="image/*"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm"
              required
            />
            <p class="text-xs text-gray-500 mt-1">Upload a clear photo of the front of your ID</p>
            <div v-if="uploadStatus.idFront" class="mt-2 text-xs" :class="uploadStatus.idFront === 'uploading' ? 'text-blue-600' : 'text-green-600'">
              {{ uploadStatus.idFront === 'uploading' ? '⏳ Uploading...' : '✓ Uploaded to IPFS' }}
            </div>
          </div>

          <div class="mb-3">
            <label class="block text-sm font-medium text-gray-700 mb-1">
              ID Back Photo <span class="text-red-500">*</span>
            </label>
            <input
              @change="handleFileUpload($event, 'idBack')"
              type="file"
              accept="image/*"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm"
              required
            />
            <p class="text-xs text-gray-500 mt-1">Upload a clear photo of the back of your ID</p>
            <div v-if="uploadStatus.idBack" class="mt-2 text-xs" :class="uploadStatus.idBack === 'uploading' ? 'text-blue-600' : 'text-green-600'">
              {{ uploadStatus.idBack === 'uploading' ? '⏳ Uploading...' : '✓ Uploaded to IPFS' }}
            </div>
          </div>

          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">
              Selfie with ID <span class="text-red-500">*</span>
            </label>
            <input
              @change="handleFileUpload($event, 'selfie')"
              type="file"
              accept="image/*"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm"
              required
            />
            <p class="text-xs text-gray-500 mt-1">Take a selfie holding your ID next to your face</p>
            <div v-if="uploadStatus.selfie" class="mt-2 text-xs" :class="uploadStatus.selfie === 'uploading' ? 'text-blue-600' : 'text-green-600'">
              {{ uploadStatus.selfie === 'uploading' ? '⏳ Uploading...' : '✓ Uploaded to IPFS' }}
            </div>
          </div>
        </div>

        <div class="flex gap-3 pt-4">
          <button
            type="button"
            @click="showForm = false"
            class="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg font-semibold hover:bg-gray-300 transition"
          >
            Cancel
          </button>
          <button
            type="submit"
            :disabled="isSubmitting || !canSubmit"
            class="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg font-semibold hover:bg-blue-700 transition disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <span v-if="isSubmitting">Submitting...</span>
            <span v-else>Submit KYC Request</span>
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, watch } from 'vue'
import blockchain from '../utils/blockchain.js'
import toast from '../utils/toast.js'
import { uploadToIPFS } from '../utils/ipfs.js'

export default {
  name: 'MinterRequestNotice',
  emits: ['form-visibility-changed', 'request-submitted'],
  setup(props, { emit }) {
    const minterRequest = ref(null)
    const isSubmitting = ref(false)
    const showForm = ref(false)

    // Watch showForm and emit changes
    watch(showForm, (newValue) => {
      emit('form-visibility-changed', newValue)
    })

    const kycForm = ref({
      fullName: '',
      email: '',
      reason: '',
      ipfsIdFront: '',
      ipfsIdBack: '',
      ipfsSelfie: ''
    })

    const uploadStatus = ref({
      idFront: null,
      idBack: null,
      selfie: null
    })

    const canSubmit = computed(() => {
      return kycForm.value.fullName &&
             kycForm.value.email &&
             kycForm.value.reason &&
             kycForm.value.ipfsIdFront &&
             kycForm.value.ipfsIdBack &&
             kycForm.value.ipfsSelfie
    })

    const checkMinterStatus = async () => {
      if (!blockchain.signer) {
        return
      }

      try {
        // Ensure contract addresses are loaded
        await blockchain.loadContractAddresses()

        const address = await blockchain.signer.getAddress()
        const request = await blockchain.getMinterRequest(address)
        minterRequest.value = request
      } catch (error) {
        // Only log if it's not a "no request found" error
        if (!error.message?.includes('No request found')) {
          console.error('Error checking minter status:', error)
        }
      }
    }

    const handleFileUpload = async (event, type) => {
      const file = event.target.files[0]
      if (!file) return

      uploadStatus.value[type] = 'uploading'

      try {
        // Upload to IPFS using centralized utility
        const cid = await uploadToIPFS(file)

        if (type === 'idFront') {
          kycForm.value.ipfsIdFront = cid
        } else if (type === 'idBack') {
          kycForm.value.ipfsIdBack = cid
        } else if (type === 'selfie') {
          kycForm.value.ipfsSelfie = cid
        }

        uploadStatus.value[type] = 'completed'
        const fileLabel = type === 'idFront' ? 'ID Front' : type === 'idBack' ? 'ID Back' : 'Selfie'
        toast.success(`${fileLabel} uploaded successfully to IPFS`)
      } catch (error) {
        console.error('Error uploading to IPFS:', error)
        uploadStatus.value[type] = 'error'
        toast.txError(error, 'Upload Failed', 'Failed to upload file')
      }
    }

    const submitRequest = async () => {
      isSubmitting.value = true
      try {
        toast.info('Submitting KYC request...')
        await blockchain.requestMinter(kycForm.value)
        toast.success('Minter request submitted successfully!', 'Request Submitted')

        // Reset form
        kycForm.value = {
          fullName: '',
          email: '',
          reason: '',
          ipfsIdFront: '',
          ipfsIdBack: '',
          ipfsSelfie: ''
        }
        uploadStatus.value = {
          idFront: null,
          idBack: null,
          selfie: null
        }

        // Hide form and refresh status
        showForm.value = false
        await checkMinterStatus()

        // Emit event to parent to refresh status
        emit('request-submitted')
      } catch (error) {
        console.error('Error submitting request:', error)
        toast.txError(error, 'Submission Failed', 'Failed to submit request')
      } finally {
        isSubmitting.value = false
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

    onMounted(() => {
      checkMinterStatus()
    })

    return {
      minterRequest,
      kycForm,
      uploadStatus,
      canSubmit,
      isSubmitting,
      showForm,
      handleFileUpload,
      submitRequest,
      formatDate
    }
  }
}
</script>
