/**
 * Vue Composable for Encrypted Document Management
 *
 * Provides reactive state and methods for:
 * - Uploading encrypted documents to IPFS
 * - Storing encrypted keys on-chain
 * - Downloading and decrypting documents
 * - Managing document access control
 */

import { ref, computed } from 'vue'
import { ethers } from 'ethers'
import { uploadEncryptedToIPFS, downloadAndDecryptFromIPFS, triggerDownload } from './encryptedIPFS.js'
import { getPublicKeyFromSigner } from './encryption.js'

// Contract ABI (minimal interface for encrypted doc registry)
const ENCRYPTED_DOC_REGISTRY_ABI = [
  "function upload_document(string _cid, string _doc_type, string _original_name, uint256 _original_size, uint256 _company_id) external returns (uint256)",
  "function add_recipient(uint256 _doc_id, address _recipient, string _ephemeral_public_key, string _iv, string _ciphertext, string _mac) external",
  "function add_recipients_batch(uint256 _doc_id, address[] _recipients, string[] _ephemeral_public_keys, string[] _ivs, string[] _ciphertexts, string[] _macs) external",
  "function remove_recipient(uint256 _doc_id, address _recipient) external",
  "function revoke_document(uint256 _doc_id) external",
  "function get_document(uint256 _doc_id) external view returns (tuple(uint256 id, address uploader, string cid, string doc_type, string original_name, uint256 original_size, uint256 uploaded_at, bool is_revoked, uint256 company_id))",
  "function get_encrypted_key(uint256 _doc_id, address _recipient) external view returns (tuple(string ephemeral_public_key, string iv, string ciphertext, string mac))",
  "function can_access(uint256 _doc_id, address _recipient) external view returns (bool)",
  "function get_uploader_documents(address _uploader) external view returns (uint256[])",
  "function get_accessible_documents(address _recipient) external view returns (uint256[])",
  "function document_count() external view returns (uint256)",
  "event DocumentUploaded(uint256 indexed doc_id, address indexed uploader, string cid, string doc_type)",
  "event RecipientAdded(uint256 indexed doc_id, address indexed recipient)",
  "event RecipientRemoved(uint256 indexed doc_id, address indexed recipient)",
  "event DocumentRevoked(uint256 indexed doc_id, address indexed revoked_by)"
]

/**
 * Composable for encrypted document management
 * @param {string} contractAddress - EncryptedDocRegistry contract address
 * @param {ethers.Signer} signer - Ethers signer
 */
export function useEncryptedDocuments(contractAddress, signer) {
  // Reactive state
  const isLoading = ref(false)
  const error = ref(null)
  const uploadProgress = ref(0)
  const myDocuments = ref([])
  const accessibleDocuments = ref([])
  const myPublicKey = ref(null)

  // Contract instance
  let contract = null

  /**
   * Initialize the composable
   */
  async function init() {
    if (!contractAddress || !signer) {
      throw new Error('Contract address and signer are required')
    }

    contract = new ethers.Contract(contractAddress, ENCRYPTED_DOC_REGISTRY_ABI, signer)

    // Derive user's public key for encryption
    try {
      myPublicKey.value = await getPublicKeyFromSigner(signer)
    } catch (e) {
      console.warn('Could not derive public key:', e.message)
    }
  }

  /**
   * Upload an encrypted document
   * @param {File} file - File to upload
   * @param {string} docType - Document type (e.g., 'kyc', 'prospectus')
   * @param {Array<{address: string, publicKey: string}>} recipients - Authorized recipients
   * @param {number} companyId - Associated company ID (0 if none)
   * @returns {Promise<{docId: number, cid: string, txHash: string}>}
   */
  async function uploadDocument(file, docType, recipients, companyId = 0) {
    isLoading.value = true
    error.value = null
    uploadProgress.value = 0

    try {
      // Step 1: Encrypt and upload to IPFS
      uploadProgress.value = 10
      console.log('🔐 Encrypting and uploading to IPFS...')

      const { cid, encryptedKeys, metadata } = await uploadEncryptedToIPFS(file, recipients)
      uploadProgress.value = 50

      // Step 2: Register document on-chain
      console.log('📝 Registering document on-chain...')
      const uploadTx = await contract.upload_document(
        cid,
        docType,
        metadata.originalName,
        metadata.originalSize,
        companyId
      )

      const uploadReceipt = await uploadTx.wait()
      uploadProgress.value = 70

      // Extract document ID from event
      const uploadEvent = uploadReceipt.logs.find(
        log => log.fragment?.name === 'DocumentUploaded'
      )
      const docId = uploadEvent ? Number(uploadEvent.args[0]) : null

      if (!docId) {
        throw new Error('Failed to get document ID from transaction')
      }

      // Step 3: Add recipients with encrypted keys
      console.log('🔑 Adding recipient keys on-chain...')

      if (encryptedKeys.length > 0) {
        // Prepare batch data
        const recipientAddresses = encryptedKeys.map(k => k.recipient)
        const ephemeralKeys = encryptedKeys.map(k => k.encryptedKey.ephemeralPublicKey)
        const ivs = encryptedKeys.map(k => k.encryptedKey.iv)
        const ciphertexts = encryptedKeys.map(k => k.encryptedKey.ciphertext)
        const macs = encryptedKeys.map(k => k.encryptedKey.mac)

        const addRecipientsTx = await contract.add_recipients_batch(
          docId,
          recipientAddresses,
          ephemeralKeys,
          ivs,
          ciphertexts,
          macs
        )
        await addRecipientsTx.wait()
      }

      uploadProgress.value = 100
      console.log(`✅ Document uploaded successfully! ID: ${docId}`)

      return {
        docId,
        cid,
        txHash: uploadReceipt.hash,
        metadata
      }

    } catch (e) {
      error.value = e.message
      console.error('Upload failed:', e)
      throw e
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Download and decrypt a document
   * @param {number} docId - Document ID
   * @returns {Promise<{data: Uint8Array, blob: Blob, url: string, filename: string}>}
   */
  async function downloadDocument(docId) {
    isLoading.value = true
    error.value = null

    try {
      const userAddress = await signer.getAddress()

      // Step 1: Get document metadata
      console.log('📄 Fetching document metadata...')
      const doc = await contract.get_document(docId)

      if (doc.is_revoked) {
        throw new Error('Document has been revoked')
      }

      // Step 2: Get encrypted key for this user
      console.log('🔑 Fetching encrypted key...')
      const encryptedKey = await contract.get_encrypted_key(docId, userAddress)

      if (!encryptedKey.ciphertext) {
        throw new Error('You do not have access to this document')
      }

      // Step 3: Get private key from signer (user must sign to prove ownership)
      // Note: In production, use a more secure method
      const privateKey = await getPrivateKeyFromSigner(signer)

      // Step 4: Download and decrypt from IPFS
      console.log('📥 Downloading and decrypting...')
      const result = await downloadAndDecryptFromIPFS(
        doc.cid,
        {
          ephemeralPublicKey: encryptedKey.ephemeral_public_key,
          iv: encryptedKey.iv,
          ciphertext: encryptedKey.ciphertext,
          mac: encryptedKey.mac
        },
        privateKey,
        {
          originalName: doc.original_name,
          originalType: guessContentType(doc.original_name)
        }
      )

      console.log('✅ Document decrypted successfully!')
      return result

    } catch (e) {
      error.value = e.message
      console.error('Download failed:', e)
      throw e
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Download document and trigger browser download
   * @param {number} docId - Document ID
   */
  async function downloadAndSave(docId) {
    const result = await downloadDocument(docId)
    triggerDownload(result.url, result.filename)

    // Clean up object URL after download
    setTimeout(() => URL.revokeObjectURL(result.url), 1000)
  }

  /**
   * Check if current user can access a document
   * @param {number} docId - Document ID
   * @returns {Promise<boolean>}
   */
  async function canAccess(docId) {
    const userAddress = await signer.getAddress()
    return await contract.can_access(docId, userAddress)
  }

  /**
   * Add a new recipient to an existing document
   * @param {number} docId - Document ID
   * @param {string} recipientAddress - Recipient's Ethereum address
   * @param {string} recipientPublicKey - Recipient's public key
   */
  async function addRecipient(docId, recipientAddress, recipientPublicKey) {
    isLoading.value = true
    error.value = null

    try {
      // Get the document's AES key (uploader must have it)
      // This requires the uploader to re-encrypt the key for the new recipient
      // For now, we'll need the uploader to provide the original AES key
      throw new Error('Adding recipients after upload requires the original AES key. Use uploadDocument with all recipients.')

    } catch (e) {
      error.value = e.message
      throw e
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Remove a recipient's access
   * @param {number} docId - Document ID
   * @param {string} recipientAddress - Recipient to remove
   */
  async function removeRecipient(docId, recipientAddress) {
    isLoading.value = true
    error.value = null

    try {
      const tx = await contract.remove_recipient(docId, recipientAddress)
      await tx.wait()
      console.log(`✅ Removed access for ${recipientAddress}`)
    } catch (e) {
      error.value = e.message
      throw e
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Revoke a document entirely
   * @param {number} docId - Document ID
   */
  async function revokeDocument(docId) {
    isLoading.value = true
    error.value = null

    try {
      const tx = await contract.revoke_document(docId)
      await tx.wait()
      console.log(`✅ Document ${docId} revoked`)
    } catch (e) {
      error.value = e.message
      throw e
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Fetch documents uploaded by current user
   */
  async function fetchMyDocuments() {
    const userAddress = await signer.getAddress()
    const docIds = await contract.get_uploader_documents(userAddress)

    const docs = await Promise.all(
      docIds.map(async (id) => {
        const doc = await contract.get_document(id)
        return {
          id: Number(id),
          ...doc
        }
      })
    )

    myDocuments.value = docs
    return docs
  }

  /**
   * Fetch documents accessible to current user
   */
  async function fetchAccessibleDocuments() {
    const userAddress = await signer.getAddress()
    const docIds = await contract.get_accessible_documents(userAddress)

    const docs = await Promise.all(
      docIds.map(async (id) => {
        const doc = await contract.get_document(id)
        return {
          id: Number(id),
          ...doc
        }
      })
    )

    accessibleDocuments.value = docs
    return docs
  }

  /**
   * Get document details
   * @param {number} docId - Document ID
   */
  async function getDocument(docId) {
    return await contract.get_document(docId)
  }

  return {
    // State
    isLoading,
    error,
    uploadProgress,
    myDocuments,
    accessibleDocuments,
    myPublicKey,

    // Methods
    init,
    uploadDocument,
    downloadDocument,
    downloadAndSave,
    canAccess,
    addRecipient,
    removeRecipient,
    revokeDocument,
    fetchMyDocuments,
    fetchAccessibleDocuments,
    getDocument
  }
}

// Helper functions

/**
 * Get private key from signer
 * Note: This only works with Wallet instances, not with browser wallets like MetaMask
 * For MetaMask, users need to export their private key manually
 */
async function getPrivateKeyFromSigner(signer) {
  // If signer is a Wallet instance, we can get the private key directly
  if (signer.privateKey) {
    return signer.privateKey
  }

  // For browser wallets, we need a different approach
  // The user must provide their private key or use a signing-based decryption
  throw new Error(
    'Cannot extract private key from browser wallet. ' +
    'Please use a Wallet instance or implement signature-based decryption.'
  )
}

/**
 * Guess content type from filename
 */
function guessContentType(filename) {
  const ext = filename.split('.').pop()?.toLowerCase()
  const types = {
    'pdf': 'application/pdf',
    'png': 'image/png',
    'jpg': 'image/jpeg',
    'jpeg': 'image/jpeg',
    'gif': 'image/gif',
    'doc': 'application/msword',
    'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'xls': 'application/vnd.ms-excel',
    'xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    'txt': 'text/plain',
    'json': 'application/json'
  }
  return types[ext] || 'application/octet-stream'
}

export default useEncryptedDocuments
