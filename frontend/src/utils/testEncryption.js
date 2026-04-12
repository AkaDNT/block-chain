/**
 * Test utility to verify encryption is working correctly
 * Run this in browser console to test the encryption flow
 */

import {
  generateAESKey,
  exportAESKey,
  importAESKey,
  encryptAES,
  decryptAES,
  encryptECIES,
  decryptECIES
} from './encryption.js'
import { ethers } from 'ethers'

/**
 * Test AES-256-GCM encryption/decryption
 */
export async function testAESEncryption() {
  console.log('🧪 Testing AES-256-GCM encryption...')

  const testData = new TextEncoder().encode('Hello, this is a secret message!')

  // Generate key
  const key = await generateAESKey()
  console.log('✅ Generated AES key')

  // Encrypt
  const { ciphertext, iv } = await encryptAES(testData, key)
  console.log('✅ Encrypted data:', ciphertext.length, 'bytes')
  console.log('   IV:', Array.from(iv).map(b => b.toString(16).padStart(2, '0')).join(''))

  // Verify ciphertext is different from plaintext
  const isEncrypted = !arraysEqual(testData, ciphertext.slice(0, testData.length))
  console.log('✅ Data is encrypted (different from original):', isEncrypted)

  // Decrypt
  const decrypted = await decryptAES(ciphertext, key, iv)
  const decryptedText = new TextDecoder().decode(decrypted)
  console.log('✅ Decrypted:', decryptedText)

  // Verify
  const success = decryptedText === 'Hello, this is a secret message!'
  console.log(success ? '✅ AES TEST PASSED!' : '❌ AES TEST FAILED!')

  return success
}

/**
 * Test ECIES encryption with Ethereum keys
 */
export async function testECIESEncryption() {
  console.log('\n🧪 Testing ECIES encryption with Ethereum keys...')

  // Create a test wallet
  const wallet = ethers.Wallet.createRandom()
  console.log('✅ Created test wallet:', wallet.address)
  console.log('   Public key:', wallet.signingKey.publicKey)

  // Test data (simulating an AES key)
  const testKey = new Uint8Array(32)
  crypto.getRandomValues(testKey)
  console.log('✅ Generated test key (32 bytes)')

  // Encrypt with public key
  const encrypted = await encryptECIES(testKey, wallet.signingKey.publicKey)
  console.log('✅ ECIES encrypted:')
  console.log('   Ephemeral pubkey:', encrypted.ephemeralPublicKey.slice(0, 20) + '...')
  console.log('   IV:', encrypted.iv)
  console.log('   Ciphertext:', encrypted.ciphertext.slice(0, 20) + '...')

  // Decrypt with private key
  const decrypted = await decryptECIES(encrypted, wallet.privateKey)
  console.log('✅ ECIES decrypted:', decrypted.length, 'bytes')

  // Verify
  const success = arraysEqual(testKey, decrypted)
  console.log(success ? '✅ ECIES TEST PASSED!' : '❌ ECIES TEST FAILED!')

  return success
}

/**
 * Test full file encryption flow
 */
export async function testFileEncryption() {
  console.log('\n🧪 Testing full file encryption flow...')

  // Create a test file
  const testContent = 'This is a test PDF content. In reality, this would be binary data.'
  const testFile = new Blob([testContent], { type: 'application/pdf' })

  // Create test recipient
  const wallet = ethers.Wallet.createRandom()
  const recipients = [{ address: wallet.address, publicKey: wallet.signingKey.publicKey }]

  console.log('✅ Test file size:', testFile.size, 'bytes')
  console.log('✅ Recipient:', wallet.address)

  // Import the encryption function
  const { encryptFileForRecipients, decryptFileWithKey } = await import('./encryption.js')

  // Encrypt
  const { encryptedFile, encryptedKeys } = await encryptFileForRecipients(testFile, recipients)
  console.log('✅ Encrypted file size:', encryptedFile.size, 'bytes')
  console.log('✅ Encrypted keys for', encryptedKeys.length, 'recipient(s)')

  // Verify encrypted content is different
  const encryptedData = await encryptedFile.arrayBuffer()
  const originalData = await testFile.arrayBuffer()
  const isDifferent = !arraysEqual(
    new Uint8Array(originalData),
    new Uint8Array(encryptedData).slice(12, 12 + originalData.byteLength)
  )
  console.log('✅ Encrypted content differs from original:', isDifferent)

  // Decrypt
  const decrypted = await decryptFileWithKey(
    encryptedData,
    encryptedKeys[0].encryptedKey,
    wallet.privateKey
  )
  const decryptedText = new TextDecoder().decode(decrypted)
  console.log('✅ Decrypted content:', decryptedText.slice(0, 50) + '...')

  const success = decryptedText === testContent
  console.log(success ? '✅ FILE ENCRYPTION TEST PASSED!' : '❌ FILE ENCRYPTION TEST FAILED!')

  return success
}

/**
 * Run all tests
 */
export async function runAllTests() {
  console.log('=' .repeat(60))
  console.log('🔐 ENCRYPTION VERIFICATION TESTS')
  console.log('=' .repeat(60))

  const results = {
    aes: await testAESEncryption(),
    ecies: await testECIESEncryption(),
    file: await testFileEncryption()
  }

  console.log('\n' + '=' .repeat(60))
  console.log('📊 TEST RESULTS')
  console.log('=' .repeat(60))
  console.log('AES-256-GCM:', results.aes ? '✅ PASS' : '❌ FAIL')
  console.log('ECIES:', results.ecies ? '✅ PASS' : '❌ FAIL')
  console.log('File Encryption:', results.file ? '✅ PASS' : '❌ FAIL')
  console.log('=' .repeat(60))

  const allPassed = Object.values(results).every(r => r)
  console.log(allPassed ? '\n🎉 ALL TESTS PASSED!' : '\n⚠️ SOME TESTS FAILED')

  return results
}

// Helper function
function arraysEqual(a, b) {
  if (a.length !== b.length) return false
  for (let i = 0; i < a.length; i++) {
    if (a[i] !== b[i]) return false
  }
  return true
}

export default { runAllTests, testAESEncryption, testECIESEncryption, testFileEncryption }
