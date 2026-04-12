<template>
  <div class="encrypted-doc-list">
    <div class="flex items-center justify-between mb-4">
      <h3 class="text-lg font-semibold text-gray-900">{{ title }}</h3>
      <button
        @click="refresh"
        :disabled="isLoading"
        class="inline-flex items-center px-3 py-1.5 border border-gray-300 shadow-sm text-xs font-medium rounded text-gray-700 bg-white hover:bg-gray-50"
      >
        <svg
          class="h-4 w-4 mr-1"
          :class="{ 'animate-spin': isLoading }"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
        </svg>
        Refresh
      </button>
    </div>

    <!-- Loading State -->
    <div v-if="isLoading && documents.length === 0" class="text-center py-8">
      <svg class="animate-spin h-8 w-8 text-indigo-600 mx-auto" fill="none" viewBox="0 0 24 24">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
      </svg>
      <p class="mt-2 text-sm text-gray-500">Loading documents...</p>
    </div>

    <!-- Empty State -->
    <div v-else-if="documents.length === 0" class="text-center py-8">
      <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
      </svg>
      <p class="mt-2 text-sm text-gray-500">No documents found</p>
    </div>

    <!-- Document List -->
    <div v-else class="space-y-3">
      <div
        v-for="doc in documents"
        :key="doc.id"
        class="p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
        :class="{ 'opacity-50': doc.is_revoked }"
      >
        <div class="flex items-start justify-between">
          <div class="flex items-start">
            <div class="flex-shrink-0">
              <svg class="h-8 w-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
            </div>
            <div class="ml-3">
              <p class="text-sm font-medium text-gray-900">
                {{ doc.original_name }}
                <span v-if="doc.is_revoked" class="ml-2 inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-red-100 text-red-800">
                  Revoked
                </span>
              </p>
              <p class="text-xs text-gray-500">
                Type: {{ doc.doc_type }} | Size: {{ formatFileSize(Number(doc.original_size)) }}
              </p>
              <p class="text-xs text-gray-400">
                Uploaded: {{ formatDate(Number(doc.uploaded_at)) }}
              </p>
              <p class="text-xs text-gray-400 font-mono truncate max-w-xs">
                CID: {{ doc.cid }}
              </p>
            </div>
          </div>

          <div class="flex items-center space-x-2">
            <!-- Download Button -->
            <button
              v-if="!doc.is_revoked && mode === 'accessible'"
              @click="downloadDoc(doc)"
              :disabled="downloadingId === doc.id"
              class="inline-flex items-center px-3 py-1.5 border border-transparent text-xs font-medium rounded text-indigo-700 bg-indigo-100 hover:bg-indigo-200 disabled:opacity-50"
            >
              <svg v-if="downloadingId === doc.id" class="animate-spin h-4 w-4 mr-1" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              <svg v-else class="h-4 w-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
              </svg>
              {{ downloadingId === doc.id ? 'Decrypting...' : 'Download' }}
            </button>

            <!-- Revoke Button (for uploader) -->
            <button
              v-if="!doc.is_revoked && mode === 'uploaded'"
              @click="revokeDoc(doc)"
              class="inline-flex items-center px-3 py-1.5 border border-transparent text-xs font-medium rounded text-red-700 bg-red-100 hover:bg-red-200"
            >
              <svg class="h-4 w-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M18.364 18.364A9 9 0 005.636 5.636m12.728 12.728A9 9 0 015.636 5.636m12.728 12.728L5.636 5.636" />
              </svg>
              Revoke
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Error Message -->
    <div v-if="error" class="mt-4 p-4 bg-red-50 rounded-lg">
      <p class="text-sm text-red-700">{{ error }}</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
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
  mode: {
    type: String,
    default: 'accessible', // 'accessible' or 'uploaded'
    validator: (v) => ['accessible', 'uploaded'].includes(v)
  },
  title: {
    type: String,
    default: 'Documents'
  }
})

const emit = defineEmits(['download', 'revoke', 'error'])

// State
const documents = ref([])
const isLoading = ref(false)
const error = ref(null)
const downloadingId = ref(null)

// Composable
let encryptedDocs = null

onMounted(async () => {
  encryptedDocs = useEncryptedDocuments(props.contractAddress, props.signer)
  await encryptedDocs.init()
  await refresh()
})

watch(() => props.mode, () => {
  refresh()
})

async function refresh() {
  if (!encryptedDocs) return

  isLoading.value = true
  error.value = null

  try {
    if (props.mode === 'uploaded') {
      documents.value = await encryptedDocs.fetchMyDocuments()
    } else {
      documents.value = await encryptedDocs.fetchAccessibleDocuments()
    }
  } catch (e) {
    error.value = e.message
    emit('error', e)
  } finally {
    isLoading.value = false
  }
}

async function downloadDoc(doc) {
  downloadingId.value = doc.id
  error.value = null

  try {
    await encryptedDocs.downloadAndSave(doc.id)
    emit('download', doc)
  } catch (e) {
    error.value = e.message
    emit('error', e)
  } finally {
    downloadingId.value = null
  }
}

async function revokeDoc(doc) {
  if (!confirm(`Are you sure you want to revoke "${doc.original_name}"? This cannot be undone.`)) {
    return
  }

  error.value = null

  try {
    await encryptedDocs.revokeDocument(doc.id)
    emit('revoke', doc)
    await refresh()
  } catch (e) {
    error.value = e.message
    emit('error', e)
  }
}

function formatFileSize(bytes) {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

function formatDate(timestamp) {
  return new Date(timestamp * 1000).toLocaleString()
}

defineExpose({ refresh })
</script>

<style scoped>
.encrypted-doc-list {
  @apply p-6 bg-white rounded-xl shadow-sm border border-gray-200;
}
</style>
