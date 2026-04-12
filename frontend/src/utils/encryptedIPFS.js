/**
 * Encrypted IPFS Upload/Download Service
 *
 * Handles:
 * - Client-side encryption before IPFS upload
 * - Encrypted key management for ACL
 * - Decryption for authorized recipients
 */

import {
  encryptFileForRecipients,
  decryptFileWithKey,
  getPublicKeyFromSigner
} from './encryption.js'

const IPFS_API_URL = 'http://localhost:5001/api/v0'
const IPFS_GATEWAY_URL = 'http://localhost:8081/ipfs'

/**
 * Upload an encrypted file to IPFS
 * @param {File} file - File to encrypt and upload
 * @param {Array<{address: string, publicKey: string}>} recipients - Authorized recipients
 * @param {Object} options - Upload options
 * @returns {Promise<{cid: string, encryptedKeys: Array, metadata: Object}>}
 */
export async function uploadEncryptedToIPFS(file, recipients, options = {}) {
  console.log(`🔐 Encrypting ${file.name} for ${recipients.length} recipient(s)...`)

  // Encrypt file for all recipients
  const {
    encryptedFile,
    encryptedKeys,
    originalName,
    originalType,
    originalSize
  } = await encryptFileForRecipients(file, recipients)

  console.log(`📤 Uploading encrypted file to IPFS...`)

  // Upload encrypted file to IPFS
  const formData = new FormData()
  formData.append('file', encryptedFile, `${originalName}.encrypted`)

  const response = await fetch(`${IPFS_API_URL}/add`, {
    method: 'POST',
    body: formData
  })

  if (!response.ok) {
    throw new Error(`IPFS upload failed: ${response.statusText}`)
  }

  const result = await response.json()
  const cid = result.Hash

  console.log(`✅ Encrypted file uploaded to IPFS: ${cid}`)

  // Create metadata object
  const metadata = {
    cid,
    originalName,
    originalType,
    originalSize,
    encryptedSize: encryptedFile.size,
    uploadedAt: Date.now(),
    isEncrypted: true
  }

  // Optionally copy to MFS for visibility in IPFS Web UI
  if (options.copyToMFS !== false) {
    try {
      await fetch(`${IPFS_API_URL}/files/mkdir?arg=/encrypted&parents=true`, {
        method: 'POST'
      }).catch(() => {})

      await fetch(`${IPFS_API_URL}/files/cp?arg=/ipfs/${cid}&arg=/encrypted/${originalName}.encrypted`, {
        method: 'POST'
      })
      console.log(`📁 Copied to MFS: /encrypted/${originalName}.encrypted`)
    } catch (e) {
      console.log('Note: Could not copy to MFS (optional)')
    }
  }

  return {
    cid,
    encryptedKeys,
    metadata
  }
}

/**
 * Download and decrypt a file from IPFS
 * @param {string} cid - IPFS CID of encrypted file
 * @param {Object} encryptedKey - ECIES encrypted AES key for this recipient
 * @param {string} privateKey - Recipient's private key
 * @param {Object} metadata - File metadata (optional, for restoring filename/type)
 * @returns {Promise<{data: Uint8Array, blob: Blob, url: string}>}
 */
export async function downloadAndDecryptFromIPFS(cid, encryptedKey, privateKey, metadata = {}) {
  console.log(`📥 Fetching encrypted file from IPFS: ${cid}`)

  // Fetch encrypted file from IPFS gateway
  const response = await fetch(`${IPFS_GATEWAY_URL}/${cid}`)

  if (!response.ok) {
    throw new Error(`Failed to fetch from IPFS: ${response.statusText}`)
  }

  const encryptedData = await response.arrayBuffer()

  console.log(`🔓 Decrypting file...`)

  // Decrypt the file
  const decryptedData = await decryptFileWithKey(encryptedData, encryptedKey, privateKey)

  // Create blob with original type if available
  const mimeType = metadata.originalType || 'application/octet-stream'
  const blob = new Blob([decryptedData], { type: mimeType })

  // Create object URL for download/preview
  const url = URL.createObjectURL(blob)

  console.log(`✅ File decrypted successfully`)

  return {
    data: decryptedData,
    blob,
    url,
    filename: metadata.originalName || 'decrypted-file'
  }
}

/**
 * Create a download link for decrypted file
 * @param {string} url - Object URL from downloadAndDecryptFromIPFS
 * @param {string} filename - Filename for download
 */
export function triggerDownload(url, filename) {
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
}

/**
 * Encrypt and upload with signer-based public key derivation
 * This is a convenience function that derives public keys from signers
 * @param {File} file - File to encrypt and upload
 * @param {Array<{address: string, signer?: ethers.Signer, publicKey?: string}>} recipients
 * @returns {Promise<{cid: string, encryptedKeys: Array, metadata: Object}>}
 */
export async function uploadEncryptedWithSigners(file, recipients) {
  // Derive public keys for recipients that don't have them
  const recipientsWithKeys = await Promise.all(
    recipients.map(async (r) => {
      if (r.publicKey) {
        return { address: r.address, publicKey: r.publicKey }
      }
      if (r.signer) {
        const publicKey = await getPublicKeyFromSigner(r.signer)
        return { address: r.address, publicKey }
      }
      throw new Error(`Recipient ${r.address} needs either publicKey or signer`)
    })
  )

  return uploadEncryptedToIPFS(file, recipientsWithKeys)
}

/**
 * Verify if an encrypted file is accessible on IPFS
 * @param {string} cid - IPFS CID
 * @returns {Promise<boolean>}
 */
export async function verifyEncryptedCID(cid) {
  try {
    const response = await fetch(`${IPFS_GATEWAY_URL}/${cid}`, { method: 'HEAD' })
    return response.ok
  } catch (e) {
    return false
  }
}

/**
 * Get IPFS gateway URL for encrypted file
 * @param {string} cid - IPFS CID
 * @param {string} gateway - Gateway type
 * @returns {string}
 */
export function getEncryptedFileUrl(cid, gateway = 'local') {
  const gateways = {
    'local': `http://localhost:8081/ipfs/${cid}`,
    'ipfs.io': `https://ipfs.io/ipfs/${cid}`,
    'pinata': `https://gateway.pinata.cloud/ipfs/${cid}`,
    'cloudflare': `https://cloudflare-ipfs.com/ipfs/${cid}`
  }
  return gateways[gateway] || gateways['local']
}

export default {
  uploadEncryptedToIPFS,
  downloadAndDecryptFromIPFS,
  uploadEncryptedWithSigners,
  triggerDownload,
  verifyEncryptedCID,
  getEncryptedFileUrl
}
