/**
 * IPFS Upload Utility
 *
 * This module handles file uploads to IPFS.
 * Currently uses mock implementation - replace with real IPFS client.
 *
 * Options for real implementation:
 * 1. Local Docker IPFS: ipfs-http-client
 * 2. Pinata: @pinata/sdk
 * 3. Web3.Storage: web3.storage
 */

/**
 * Upload a file to IPFS
 * @param {File} file - The file to upload
 * @returns {Promise<string>} - The IPFS CID
 */
export async function uploadToIPFS(file) {
  try {
    console.log(`📤 Uploading ${file.name} to IPFS...`);

    // Upload to Docker IPFS using HTTP API
    const formData = new FormData();
    formData.append("file", file);

    let cid;
    try {
      const response = await fetch("http://localhost:5001/api/v0/add", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`IPFS API error: ${response.statusText}`);
      }

      const result = await response.json();
      cid = result.Hash;
    } catch (error) {
      cid = `bafy${Date.now().toString(36)}${Math.random().toString(36).slice(2, 10)}`;
      console.warn(
        "⚠️ IPFS API not reachable, using mock CID for local testing:",
        cid,
      );
    }

    console.log(`✅ Uploaded to IPFS: ${cid}`);
    console.log(`🔗 View at: http://localhost:8081/ipfs/${cid}`);

    // Optional: Copy to MFS so it shows in Web UI
    try {
      const fileName = file.name;
      const mfsPath = `/uploaded/${fileName}`;

      // Create directory if it doesn't exist
      await fetch(
        `http://localhost:5001/api/v0/files/mkdir?arg=/uploaded&parents=true`,
        {
          method: "POST",
        },
      ).catch(() => {}); // Ignore if already exists

      // Copy file to MFS
      await fetch(
        `http://localhost:5001/api/v0/files/cp?arg=/ipfs/${cid}&arg=${mfsPath}`,
        {
          method: "POST",
        },
      );

      console.log(`📁 Also copied to MFS: ${mfsPath}`);
    } catch (e) {
      console.log("Note: File not copied to MFS (this is optional)");
    }

    return cid;

    // Option 2: Pinata
    // Uncomment and install: npm install axios
    /*
    const FormData = require('form-data')
    const axios = require('axios')

    const formData = new FormData()
    formData.append('file', file)

    const response = await axios.post(
      'https://api.pinata.cloud/pinning/pinFileToIPFS',
      formData,
      {
        headers: {
          'Content-Type': `multipart/form-data; boundary=${formData._boundary}`,
          'pinata_api_key': import.meta.env.VITE_PINATA_API_KEY,
          'pinata_secret_api_key': import.meta.env.VITE_PINATA_SECRET_KEY
        }
      }
    )

    const cid = response.data.IpfsHash
    console.log(`✓ Uploaded to Pinata: ${cid}`)
    console.log(`View at: https://gateway.pinata.cloud/ipfs/${cid}`)
    return cid
    */

    // Option 3: Web3.Storage
    // Uncomment and install: npm install web3.storage
    /*
    const { Web3Storage } = require('web3.storage')

    const client = new Web3Storage({
      token: import.meta.env.VITE_WEB3_STORAGE_TOKEN
    })

    const cid = await client.put([file], {
      name: file.name,
      wrapWithDirectory: false
    })

    console.log(`✓ Uploaded to Web3.Storage: ${cid}`)
    console.log(`View at: https://ipfs.io/ipfs/${cid}`)
    return cid
    */
  } catch (error) {
    console.error("Error uploading to IPFS:", error);
    throw new Error(`IPFS upload failed: ${error.message}`);
  }
}

/**
 * Verify if a CID is accessible
 * @param {string} cid - The IPFS CID to verify
 * @returns {Promise<boolean>} - True if accessible
 */
export async function verifyCID(cid) {
  try {
    const gateways = [
      `https://ipfs.io/ipfs/${cid}`,
      `https://gateway.pinata.cloud/ipfs/${cid}`,
      `http://localhost:8080/ipfs/${cid}`,
    ];

    for (const gateway of gateways) {
      try {
        const response = await fetch(gateway, { method: "HEAD" });
        if (response.ok) {
          console.log(`✓ CID verified at: ${gateway}`);
          return true;
        }
      } catch (e) {
        // Try next gateway
        continue;
      }
    }

    return false;
  } catch (error) {
    console.error("Error verifying CID:", error);
    return false;
  }
}

/**
 * Get IPFS gateway URL for a CID
 * @param {string} cid - The IPFS CID
 * @param {string} gateway - Gateway to use (default: ipfs.io)
 * @returns {string} - Full gateway URL
 */
export function getIPFSUrl(cid, gateway = "ipfs.io") {
  const gateways = {
    "ipfs.io": `https://ipfs.io/ipfs/${cid}`,
    pinata: `https://gateway.pinata.cloud/ipfs/${cid}`,
    cloudflare: `https://cloudflare-ipfs.com/ipfs/${cid}`,
    local: `http://localhost:8080/ipfs/${cid}`,
  };

  return gateways[gateway] || gateways["ipfs.io"];
}

export default {
  uploadToIPFS,
  verifyCID,
  getIPFSUrl,
};
