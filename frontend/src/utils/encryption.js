/**
 * Encryption Utilities for IPFS Documents
 *
 * Implements:
 * - AES-256-GCM for file encryption
 * - ECIES (secp256k1) for key encryption using Ethereum keypairs
 *
 * Flow:
 * 1. Generate random AES-256 key
 * 2. Encrypt file with AES-GCM
 * 3. Encrypt AES key with recipient's public key (ECIES)
 * 4. Store encrypted file on IPFS, encrypted keys on-chain
 */

import { ethers } from 'ethers'

// ============================================
// AES-256-GCM Encryption (File Encryption)
// ============================================

/**
 * Generate a random AES-256 key
 * @returns {Promise<CryptoKey>} AES-GCM key
 */
export async function generateAESKey() {
  return await crypto.subtle.generateKey(
    { name: 'AES-GCM', length: 256 },
    true, // extractable
    ['encrypt', 'decrypt']
  )
}

/**
 * Export AES key to raw bytes
 * @param {CryptoKey} key - AES key
 * @returns {Promise<Uint8Array>} Raw key bytes
 */
export async function exportAESKey(key) {
  const exported = await crypto.subtle.exportKey('raw', key)
  return new Uint8Array(exported)
}

/**
 * Import raw bytes as AES key
 * @param {Uint8Array} rawKey - Raw key bytes
 * @returns {Promise<CryptoKey>} AES-GCM key
 */
export async function importAESKey(rawKey) {
  return await crypto.subtle.importKey(
    'raw',
    rawKey,
    { name: 'AES-GCM', length: 256 },
    true,
    ['encrypt', 'decrypt']
  )
}

/**
 * Encrypt data with AES-256-GCM
 * @param {ArrayBuffer|Uint8Array} data - Data to encrypt
 * @param {CryptoKey} key - AES key
 * @returns {Promise<{ciphertext: Uint8Array, iv: Uint8Array}>}
 */
export async function encryptAES(data, key) {
  const iv = crypto.getRandomValues(new Uint8Array(12)) // 96-bit IV for GCM

  const ciphertext = await crypto.subtle.encrypt(
    { name: 'AES-GCM', iv },
    key,
    data
  )

  return {
    ciphertext: new Uint8Array(ciphertext),
    iv
  }
}

/**
 * Decrypt data with AES-256-GCM
 * @param {Uint8Array} ciphertext - Encrypted data
 * @param {CryptoKey} key - AES key
 * @param {Uint8Array} iv - Initialization vector
 * @returns {Promise<Uint8Array>} Decrypted data
 */
export async function decryptAES(ciphertext, key, iv) {
  const decrypted = await crypto.subtle.decrypt(
    { name: 'AES-GCM', iv },
    key,
    ciphertext
  )

  return new Uint8Array(decrypted)
}

// ============================================
// ECIES Encryption (Key Encryption)
// Using secp256k1 compatible with Ethereum keys
// ============================================

/**
 * Derive a shared secret using ECDH with secp256k1
 * This is a simplified ECIES implementation for browser
 * @param {string} recipientPublicKey - Recipient's public key (hex, uncompressed)
 * @param {Uint8Array} ephemeralPrivateKey - Ephemeral private key
 * @returns {Uint8Array} Shared secret
 */
function deriveSharedSecret(recipientPublicKey, ephemeralPrivateKey) {
  // Use ethers.js SigningKey for ECDH
  const signingKey = new ethers.SigningKey(ephemeralPrivateKey)
  const sharedPoint = signingKey.computeSharedSecret(recipientPublicKey)

  // Return first 32 bytes of shared point (x-coordinate)
  return ethers.getBytes(sharedPoint).slice(1, 33)
}

/**
 * Derive AES key from shared secret using HKDF-like derivation
 * @param {Uint8Array} sharedSecret - ECDH shared secret
 * @param {Uint8Array} ephemeralPublicKey - Ephemeral public key for salt
 * @returns {Promise<CryptoKey>} Derived AES key
 */
async function deriveKeyFromSecret(sharedSecret, ephemeralPublicKey) {
  // Import shared secret as HKDF key material
  const keyMaterial = await crypto.subtle.importKey(
    'raw',
    sharedSecret,
    'HKDF',
    false,
    ['deriveKey']
  )

  // Derive AES key using HKDF
  return await crypto.subtle.deriveKey(
    {
      name: 'HKDF',
      hash: 'SHA-256',
      salt: ephemeralPublicKey.slice(0, 32),
      info: new TextEncoder().encode('ecies-aes-key')
    },
    keyMaterial,
    { name: 'AES-GCM', length: 256 },
    false,
    ['encrypt', 'decrypt']
  )
}

/**
 * Encrypt data using ECIES with recipient's Ethereum public key
 * @param {Uint8Array} data - Data to encrypt (typically an AES key)
 * @param {string} recipientPublicKey - Recipient's uncompressed public key (hex with 0x04 prefix)
 * @returns {Promise<{ephemeralPublicKey: string, iv: string, ciphertext: string, mac: string}>}
 */
export async function encryptECIES(data, recipientPublicKey) {
  // Generate ephemeral keypair
  const ephemeralWallet = ethers.Wallet.createRandom()
  const ephemeralPrivateKey = ethers.getBytes(ephemeralWallet.privateKey)
  const ephemeralPublicKey = ephemeralWallet.signingKey.publicKey

  // Derive shared secret
  const sharedSecret = deriveSharedSecret(recipientPublicKey, ephemeralPrivateKey)

  // Derive encryption key from shared secret
  const encryptionKey = await deriveKeyFromSecret(
    sharedSecret,
    ethers.getBytes(ephemeralPublicKey)
  )

  // Encrypt data with derived key
  const iv = crypto.getRandomValues(new Uint8Array(12))
  const ciphertext = await crypto.subtle.encrypt(
    { name: 'AES-GCM', iv },
    encryptionKey,
    data
  )

  // Compute MAC (authentication tag is included in GCM ciphertext)
  const mac = ethers.keccak256(
    ethers.concat([
      ethers.getBytes(ephemeralPublicKey),
      iv,
      new Uint8Array(ciphertext)
    ])
  )

  return {
    ephemeralPublicKey,
    iv: ethers.hexlify(iv),
    ciphertext: ethers.hexlify(new Uint8Array(ciphertext)),
    mac
  }
}

/**
 * Decrypt ECIES encrypted data using recipient's private key
 * @param {Object} encryptedData - {ephemeralPublicKey, iv, ciphertext, mac}
 * @param {string} recipientPrivateKey - Recipient's private key (hex)
 * @returns {Promise<Uint8Array>} Decrypted data
 */
export async function decryptECIES(encryptedData, recipientPrivateKey) {
  const { ephemeralPublicKey, iv, ciphertext, mac } = encryptedData

  // Verify MAC
  const expectedMac = ethers.keccak256(
    ethers.concat([
      ethers.getBytes(ephemeralPublicKey),
      ethers.getBytes(iv),
      ethers.getBytes(ciphertext)
    ])
  )

  if (mac !== expectedMac) {
    throw new Error('MAC verification failed - data may be corrupted')
  }

  // Derive shared secret using recipient's private key
  const recipientSigningKey = new ethers.SigningKey(recipientPrivateKey)
  const sharedPoint = recipientSigningKey.computeSharedSecret(ephemeralPublicKey)
  const sharedSecret = ethers.getBytes(sharedPoint).slice(1, 33)

  // Derive decryption key
  const decryptionKey = await deriveKeyFromSecret(
    sharedSecret,
    ethers.getBytes(ephemeralPublicKey)
  )

  // Decrypt
  const decrypted = await crypto.subtle.decrypt(
    { name: 'AES-GCM', iv: ethers.getBytes(iv) },
    decryptionKey,
    ethers.getBytes(ciphertext)
  )

  return new Uint8Array(decrypted)
}

// ============================================
// High-Level Encryption Functions
// ============================================

/**
 * Encrypt a file for multiple recipients
 * @param {File|Blob|ArrayBuffer} file - File to encrypt
 * @param {Array<{address: string, publicKey: string}>} recipients - List of recipients with their public keys
 * @returns {Promise<{encryptedFile: Blob, encryptedKeys: Array<{recipient: string, encryptedKey: Object}>}>}
 */
export async function encryptFileForRecipients(file, recipients) {
  // Read file as ArrayBuffer
  let fileData
  if (file instanceof File || file instanceof Blob) {
    fileData = await file.arrayBuffer()
  } else {
    fileData = file
  }

  // Generate random AES key
  const aesKey = await generateAESKey()
  const rawAESKey = await exportAESKey(aesKey)

  // Encrypt file with AES-GCM
  const { ciphertext, iv } = await encryptAES(fileData, aesKey)

  // Create encrypted file blob (IV + ciphertext)
  const encryptedFileData = new Uint8Array(iv.length + ciphertext.length)
  encryptedFileData.set(iv, 0)
  encryptedFileData.set(ciphertext, iv.length)

  const encryptedFile = new Blob([encryptedFileData], { type: 'application/octet-stream' })

  // Encrypt AES key for each recipient using ECIES
  const encryptedKeys = []
  for (const recipient of recipients) {
    const encryptedKey = await encryptECIES(rawAESKey, recipient.publicKey)
    encryptedKeys.push({
      recipient: recipient.address,
      encryptedKey
    })
  }

  return {
    encryptedFile,
    encryptedKeys,
    originalName: file.name || 'encrypted-file',
    originalType: file.type || 'application/octet-stream',
    originalSize: fileData.byteLength
  }
}

/**
 * Decrypt a file using recipient's private key
 * @param {ArrayBuffer|Uint8Array} encryptedFileData - Encrypted file data (IV + ciphertext)
 * @param {Object} encryptedKey - ECIES encrypted AES key
 * @param {string} recipientPrivateKey - Recipient's private key
 * @returns {Promise<Uint8Array>} Decrypted file data
 */
export async function decryptFileWithKey(encryptedFileData, encryptedKey, recipientPrivateKey) {
  // Convert to Uint8Array if needed
  const data = encryptedFileData instanceof ArrayBuffer
    ? new Uint8Array(encryptedFileData)
    : encryptedFileData

  // Extract IV (first 12 bytes) and ciphertext
  const iv = data.slice(0, 12)
  const ciphertext = data.slice(12)

  // Decrypt AES key using ECIES
  const rawAESKey = await decryptECIES(encryptedKey, recipientPrivateKey)

  // Import AES key
  const aesKey = await importAESKey(rawAESKey)

  // Decrypt file
  return await decryptAES(ciphertext, aesKey, iv)
}

/**
 * Get public key from Ethereum address using wallet signature
 * This requires the user to sign a message to recover their public key
 * @param {ethers.Signer} signer - Ethers signer
 * @returns {Promise<string>} Uncompressed public key (hex)
 */
export async function getPublicKeyFromSigner(signer) {
  const message = 'Sign this message to derive your public key for encryption'
  const signature = await signer.signMessage(message)

  // Recover public key from signature
  const messageHash = ethers.hashMessage(message)
  const publicKey = ethers.SigningKey.recoverPublicKey(messageHash, signature)

  return publicKey
}

/**
 * Utility: Convert hex string to Uint8Array
 */
export function hexToBytes(hex) {
  return ethers.getBytes(hex)
}

/**
 * Utility: Convert Uint8Array to hex string
 */
export function bytesToHex(bytes) {
  return ethers.hexlify(bytes)
}

export default {
  // AES functions
  generateAESKey,
  exportAESKey,
  importAESKey,
  encryptAES,
  decryptAES,

  // ECIES functions
  encryptECIES,
  decryptECIES,

  // High-level functions
  encryptFileForRecipients,
  decryptFileWithKey,
  getPublicKeyFromSigner,

  // Utilities
  hexToBytes,
  bytesToHex
}
