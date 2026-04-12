#!/usr/bin/env node
/**
 * Test IPFS file upload and retrieval
 *
 * Installation:
 * npm install ipfs-http-client
 *
 * Usage:
 * node scripts/test_ipfs.js <file-path>
 */

const { create } = require('ipfs-http-client')
const fs = require('fs')

async function testIPFS(filePath) {
  try {
    // Connect to local IPFS node (make sure ipfs daemon is running)
    // Or use a public gateway
    const ipfs = create({
      host: 'localhost',
      port: 5001,
      protocol: 'http'
    })

    console.log('📤 Uploading file to IPFS...')

    // Read file
    const file = fs.readFileSync(filePath)

    // Add to IPFS
    const result = await ipfs.add(file)
    const cid = result.path

    console.log('✅ File uploaded successfully!')
    console.log('📋 CID:', cid)
    console.log('🔗 View at:')
    console.log(`   - https://ipfs.io/ipfs/${cid}`)
    console.log(`   - https://gateway.pinata.cloud/ipfs/${cid}`)
    console.log(`   - https://cloudflare-ipfs.com/ipfs/${cid}`)

    // Try to retrieve
    console.log('\n📥 Retrieving file from IPFS...')
    const chunks = []
    for await (const chunk of ipfs.cat(cid)) {
      chunks.push(chunk)
    }
    const retrieved = Buffer.concat(chunks)

    console.log('✅ File retrieved successfully!')
    console.log(`📊 Original size: ${file.length} bytes`)
    console.log(`📊 Retrieved size: ${retrieved.length} bytes`)
    console.log(`✓ Match: ${file.equals(retrieved)}`)

  } catch (error) {
    console.error('❌ Error:', error.message)
    console.log('\n💡 Tips:')
    console.log('   1. Make sure IPFS daemon is running: ipfs daemon')
    console.log('   2. Or use a service like Pinata or Web3.Storage')
    console.log('   3. Install ipfs-http-client: npm install ipfs-http-client')
  }
}

// Get file path from command line
const filePath = process.argv[2]

if (!filePath) {
  console.log('Usage: node test_ipfs.js <file-path>')
  console.log('Example: node test_ipfs.js ./document.pdf')
  process.exit(1)
}

if (!fs.existsSync(filePath)) {
  console.error(`File not found: ${filePath}`)
  process.exit(1)
}

testIPFS(filePath)
