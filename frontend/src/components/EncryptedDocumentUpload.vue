<template>
  <div class="encrypted-upload">
    <div class="upload-header">
      <h3 class="text-lg font-semibold text-gray-900">Encrypted Document Upload</h3>
      <p class="text-sm text-gray-500">Files are encrypted client-side before uploading to IPFS</p>
    </div>

    <!-- File Selection -->
    <div class="mt-4">
      <label class="block text-sm font-medium text-gray-700">Select File</label>
      <div
        class="mt-1 flex justify-center px-6 pt-5 pb-6 border-2 border-gray-300 border-dashed rounded-lg hover:border-indigo-400 transition-colors"
        :class="{ 'border-indigo-500 bg-indigo-50': isDragging }"
        @dragover.prevent="isDragging = true"
        @dragleave.prevent="isDragging = false"
        @drop.prevent="handleDrop"
      >
        <div class="space-y-1 text-center">
          <svg class="mx-auto h-12 w-12 text-gray-400" stroke="currentColor" fill="none" viewBox="0 0 48 48">
            <path d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" />
          </svg>
          <div class="flex text-sm text-gray-600">
            <label class="relative cursor-pointer bg-white rounded-md font-medium text-indigo-600 hover:text-indigo-500">
              <span>Upload a file</span>
              <input type="file" class="sr-only" @change="handleFileSelect" ref="fileInput">
            </label>
            <p class="pl-1">or drag and drop</p>
          </div>
          <p class="text-xs text-gray-500">PDF, DOC, XLS, images up to 50MB</p>
        </div>
      </div>
    </div>

    <!-- Selected File Info -->
    <div v-if="selectedFile" class="mt-4 p-4 bg-gray-50 rounded-lg">
      <div class="flex items-center justify-between">
        <div class="flex items-center">
          <svg class="h-8 w-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          <div class="ml-3">
            <p class="text-sm font-medium text-gray-900">{{ selectedFile.name }}</p>
            <p class="text-xs text-gray-500">{{ formatFileSize(selectedFile.size) }}</p>
          </div>
        </div>
        <button @click="clearFile" class="text-gray-400 hover:text-gray-500">
          <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>
    </div>

    <!-- Document Type -->
    <div class="mt-4">
      <label class="block text-sm font-medium text-gray-700">Document Type</label>
      <select v-model="docType" class="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 rounded-md">
        <option value="kyc">KYC Document</option>
        <option value="prospectus">Prospectus</option>
        <option value="financial">Financial Statement</option>
        <option value="legal">Legal Document</option>
        <option value="other">Other</option>
      </select>
    </div>

    <!-- Recipients -->
    <div class="mt-4">
      <label class="block text-sm font-medium text-gray-700">Authorized Recipients</label>
      <p class="text-xs text-gray-500 mb-2">Add Ethereum addresses that can decrypt this document</p>

      <div v-for="(recipient, index) in recipients" :key="index" class="flex items-center gap-2 mb-2">
        <input
          v-model="recipient.address"
          type="text"
          placeholder="0x..."
          class="flex-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 text-sm"
        >
        <input
          v-model="recipient.publicKey"
          type="text"
          placeholder="Public key (0x04...)"
          class="flex-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 text-sm"
        >
        <button
          @click="removeRecipient(index)"
          class="p-2 text-red-500 hover:text-red-700"
          v-if="recipients.length > 1"
        >
          <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
          </svg>
        </button>
      </div>

      <button
        @click="addRecipient"
        class="mt-2 inline-flex items-center px-3 py-1.5 border border-gray-300 shadow-sm text-xs font-medium rounded text-gray-700 bg-white hover:bg-gray-50"
      >
        <svg class="h-4 w-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
        </svg>
        Add Recipient
      </button>
    </div>

    <!-- Upload Progress -->
    <div v-if="isUploading" class="mt-4">
      <div class="flex items-center justify-between mb-1">
        <span class="text-sm font-medium text-gray-700">{{ uploadStatus }}</span>
        <span class="text-sm text-gray-500">{{ uploadProgress }}%</span>
      </div>
      <div class="w-full bg-gray-200 rounded-full h-2">
        <div
          class="bg-indigo-600 h-2 rounded-full transition-all duration-300"
          :style="{ width: `${uploadProgress}%` }"
        ></div>
      </div>
    </div>

    <!-- Error Message -->
    <div v-if="error" class="mt-4 p-4 bg-red-50 rounded-lg">
      <div class="flex">
        <svg class="h-5 w-5 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <p class="ml-3 text-sm text-red-700">{{ error }}</p>
      </div>
    </div>

    <!-- Success Message -->
    <div v-if="uploadResult" class="mt-4 p-4 bg-green-50 rounded-lg">
      <div class="flex items-start">
        <svg class="h-5 w-5 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <div class="ml-3">
          <p class="text-sm font-medium text-green-800">Document uploaded successfully!</p>
          <p class="mt-1 text-xs text-green-700">Document ID: {{ uploadResult.docId }}</p>
          <p class="text-xs text-green-700">IPFS CID: {{ uploadResult.cid }}</p>
        </div>
      </div>
    </div>

    <!-- Upload Button -->
    <div class="mt-6">
      <button
        @click="uploadDocument"
        :disabled="!canUpload || isUploading"
        class="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed"
      >
        <svg v-if="isUploading" class="animate-spin -ml-1 mr-3 h-5 w-5 text-white" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
        {{ isUploading ? 'Encrypting & Uploading...' : 'Encrypt & Upload to IPFS' }}
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useEncryptedDocuments } from '../utils/useEncryptedDocuments.js'

const props = defineProps({
  contractAddress: {
    type: String,
    required: true
  },
  signer: {
    type: Object,
    required: true
  },
  companyId: {
    type: Number,
    default: 0
  }
})

const emit = defineEmits(['uploaded', 'error'])

// State
const selectedFile = ref(null)
const docType = ref('kyc')
const recipients = ref([{ address: '', publicKey: '' }])
const isDragging = ref(false)
const isUploading = ref(false)
const uploadProgress = ref(0)
const uploadStatus = ref('')
const error = ref(null)
const uploadResult = ref(null)
const fileInput = ref(null)

// Composable
let encryptedDocs = null

onMounted(async () => {
  encryptedDocs = useEncryptedDocuments(props.contractAddress, props.signer)
  await encryptedDocs.init()

  // Add current user as default recipient
  const userAddress = await props.signer.getAddress()
  if (encryptedDocs.myPublicKey.value) {
    recipients.value[0] = {
      address: userAddress,
      publicKey: encryptedDocs.myPublicKey.value
    }
  }
})

// Computed
const canUpload = computed(() => {
  return selectedFile.value &&
         recipients.value.some(r => r.address && r.publicKey)
})

// Methods
function handleFileSelect(event) {
  const file = event.target.files[0]
  if (file) {
    selectedFile.value = file
    error.value = null
    uploadResult.value = null
  }
}

function handleDrop(event) {
  isDragging.value = false
  const file = event.dataTransfer.files[0]
  if (file) {
    selectedFile.value = file
    error.value = null
    uploadResult.value = null
  }
}

function clearFile() {
  selectedFile.value = null
  if (fileInput.value) {
    fileInput.value.value = ''
  }
}

function addRecipient() {
  recipients.value.push({ address: '', publicKey: '' })
}

function removeRecipient(index) {
  recipients.value.splice(index, 1)
}

function formatFileSize(bytes) {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

async function uploadDocument() {
  if (!canUpload.value || !encryptedDocs) return

  isUploading.value = true
  error.value = null
  uploadResult.value = null

  try {
    // Filter valid recipients
    const validRecipients = recipients.value.filter(r => r.address && r.publicKey)

    uploadStatus.value = 'Encrypting file...'
    uploadProgress.value = 10

    // Watch progress from composable
    const progressWatcher = setInterval(() => {
      uploadProgress.value = encryptedDocs.uploadProgress.value
      if (uploadProgress.value < 50) {
        uploadStatus.value = 'Encrypting and uploading to IPFS...'
      } else if (uploadProgress.value < 70) {
        uploadStatus.value = 'Registering on blockchain...'
      } else {
        uploadStatus.value = 'Adding recipient keys...'
      }
    }, 100)

    const result = await encryptedDocs.uploadDocument(
      selectedFile.value,
      docType.value,
      validRecipients,
      props.companyId
    )

    clearInterval(progressWatcher)
    uploadProgress.value = 100
    uploadStatus.value = 'Complete!'
    uploadResult.value = result

    emit('uploaded', result)

    // Reset form after success
    setTimeout(() => {
      clearFile()
      uploadProgress.value = 0
      isUploading.value = false
    }, 2000)

  } catch (e) {
    error.value = e.message
    emit('error', e)
    isUploading.value = false
  }
}
</script>

<style scoped>
.encrypted-upload {
  @apply p-6 bg-white rounded-xl shadow-sm border border-gray-200;
}
</style>
