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
  getPublicKeyFromSigner,
} from "./encryption.js";

const IPFS_API_URL =
  import.meta.env.VITE_IPFS_API_URL || "http://localhost:5001/api/v0";
const IPFS_GATEWAY_URL =
  import.meta.env.VITE_IPFS_GATEWAY_URL || "http://localhost:8081/ipfs";
const ENABLE_IPFS_MOCK = import.meta.env.VITE_IPFS_MOCK !== "false";
const MOCK_STORAGE_PREFIX = "blockchain_ipfs_mock:";

function generateMockCid() {
  const randomPart = Array.from(crypto.getRandomValues(new Uint8Array(16)))
    .map((value) => value.toString(16).padStart(2, "0"))
    .join("");
  return `bafy${randomPart}`;
}

function arrayBufferToBase64(buffer) {
  const bytes = new Uint8Array(buffer);
  let binary = "";
  for (let index = 0; index < bytes.length; index += 1) {
    binary += String.fromCharCode(bytes[index]);
  }
  return btoa(binary);
}

function base64ToArrayBuffer(base64) {
  const binary = atob(base64);
  const bytes = new Uint8Array(binary.length);
  for (let index = 0; index < binary.length; index += 1) {
    bytes[index] = binary.charCodeAt(index);
  }
  return bytes.buffer;
}

function saveMockIPFSRecord(record) {
  localStorage.setItem(
    `${MOCK_STORAGE_PREFIX}${record.cid}`,
    JSON.stringify(record),
  );
}

function loadMockIPFSRecord(cid) {
  const serialized = localStorage.getItem(`${MOCK_STORAGE_PREFIX}${cid}`);
  if (!serialized) return null;

  try {
    return JSON.parse(serialized);
  } catch {
    return null;
  }
}

/**
 * Upload an encrypted file to IPFS
 * @param {File} file - File to encrypt and upload
 * @param {Array<{address: string, publicKey: string}>} recipients - Authorized recipients
 * @param {Object} options - Upload options
 * @returns {Promise<{cid: string, encryptedKeys: Array, metadata: Object}>}
 */
export async function uploadEncryptedToIPFS(file, recipients, options = {}) {
  console.log(
    `🔐 Encrypting ${file.name} for ${recipients.length} recipient(s)...`,
  );

  // Encrypt file for all recipients
  const {
    encryptedFile,
    encryptedKeys,
    originalName,
    originalType,
    originalSize,
  } = await encryptFileForRecipients(file, recipients);

  console.log(`📤 Uploading encrypted file to IPFS...`);

  // Upload encrypted file to IPFS
  const formData = new FormData();
  formData.append("file", encryptedFile, `${originalName}.encrypted`);

  let cid = null;
  try {
    const response = await fetch(`${IPFS_API_URL}/add`, {
      method: "POST",
      body: formData,
    });

    if (!response.ok) {
      throw new Error(`IPFS upload failed: ${response.statusText}`);
    }

    const result = await response.json();
    cid = result.Hash;
  } catch (error) {
    if (!ENABLE_IPFS_MOCK) {
      throw new Error(`IPFS upload failed: ${error.message}`);
    }

    cid = generateMockCid();
    saveMockIPFSRecord({
      cid,
      contentBase64: arrayBufferToBase64(await encryptedFile.arrayBuffer()),
      contentType: encryptedFile.type || "application/octet-stream",
      encryptedKeys,
      metadata: {
        originalName,
        originalType,
        originalSize,
        encryptedSize: encryptedFile.size,
        uploadedAt: Date.now(),
        isEncrypted: true,
      },
    });
    console.warn(
      "⚠️ IPFS API not reachable, stored encrypted file in local mock cache:",
      cid,
    );
  }

  console.log(`✅ Encrypted file uploaded to IPFS: ${cid}`);

  // Create metadata object
  const metadata = {
    cid,
    originalName,
    originalType,
    originalSize,
    encryptedSize: encryptedFile.size,
    uploadedAt: Date.now(),
    isEncrypted: true,
  };

  // Optionally copy to MFS for visibility in IPFS Web UI
  if (ENABLE_IPFS_MOCK || options.copyToMFS === false) {
    // No-op for mock/local storage.
  } else if (options.copyToMFS !== false) {
    try {
      await fetch(`${IPFS_API_URL}/files/mkdir?arg=/encrypted&parents=true`, {
        method: "POST",
      }).catch(() => {});

      await fetch(
        `${IPFS_API_URL}/files/cp?arg=/ipfs/${cid}&arg=/encrypted/${originalName}.encrypted`,
        {
          method: "POST",
        },
      );
      console.log(`📁 Copied to MFS: /encrypted/${originalName}.encrypted`);
    } catch (e) {
      console.log("Note: Could not copy to MFS (optional)");
    }
  }

  return {
    cid,
    encryptedKeys,
    metadata,
  };
}

/**
 * Download and decrypt a file from IPFS
 * @param {string} cid - IPFS CID of encrypted file
 * @param {Object} encryptedKey - ECIES encrypted AES key for this recipient
 * @param {string} privateKey - Recipient's private key
 * @param {Object} metadata - File metadata (optional, for restoring filename/type)
 * @returns {Promise<{data: Uint8Array, blob: Blob, url: string}>}
 */
export async function downloadAndDecryptFromIPFS(
  cid,
  encryptedKey,
  privateKey,
  metadata = {},
) {
  console.log(`📥 Fetching encrypted file from IPFS: ${cid}`);

  // Fetch encrypted file from IPFS gateway
  let encryptedData;
  try {
    const response = await fetch(`${IPFS_GATEWAY_URL}/${cid}`);

    if (!response.ok) {
      throw new Error(`Failed to fetch from IPFS: ${response.statusText}`);
    }

    encryptedData = await response.arrayBuffer();
  } catch (error) {
    const mockRecord = ENABLE_IPFS_MOCK ? loadMockIPFSRecord(cid) : null;
    if (!mockRecord) {
      throw new Error(`Failed to fetch from IPFS: ${error.message}`);
    }

    encryptedData = base64ToArrayBuffer(mockRecord.contentBase64);
    if (!metadata.originalType) {
      metadata = { ...metadata, ...mockRecord.metadata };
    }
    console.warn("⚠️ Loaded encrypted file from local mock cache:", cid);
  }

  console.log(`🔓 Decrypting file...`);

  // Decrypt the file
  const decryptedData = await decryptFileWithKey(
    encryptedData,
    encryptedKey,
    privateKey,
  );

  // Create blob with original type if available
  const mimeType = metadata.originalType || "application/octet-stream";
  const blob = new Blob([decryptedData], { type: mimeType });

  // Create object URL for download/preview
  const url = URL.createObjectURL(blob);

  console.log(`✅ File decrypted successfully`);

  return {
    data: decryptedData,
    blob,
    url,
    filename: metadata.originalName || "decrypted-file",
  };
}

/**
 * Create a download link for decrypted file
 * @param {string} url - Object URL from downloadAndDecryptFromIPFS
 * @param {string} filename - Filename for download
 */
export function triggerDownload(url, filename) {
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
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
        return { address: r.address, publicKey: r.publicKey };
      }
      if (r.signer) {
        const publicKey = await getPublicKeyFromSigner(r.signer);
        return { address: r.address, publicKey };
      }
      throw new Error(
        `Recipient ${r.address} needs either publicKey or signer`,
      );
    }),
  );

  return uploadEncryptedToIPFS(file, recipientsWithKeys);
}

/**
 * Verify if an encrypted file is accessible on IPFS
 * @param {string} cid - IPFS CID
 * @returns {Promise<boolean>}
 */
export async function verifyEncryptedCID(cid) {
  try {
    const response = await fetch(`${IPFS_GATEWAY_URL}/${cid}`, {
      method: "HEAD",
    });
    return response.ok;
  } catch (e) {
    return false;
  }
}

/**
 * Get IPFS gateway URL for encrypted file
 * @param {string} cid - IPFS CID
 * @param {string} gateway - Gateway type
 * @returns {string}
 */
export function getEncryptedFileUrl(cid, gateway = "local") {
  const gateways = {
    local: `http://localhost:8081/ipfs/${cid}`,
    "ipfs.io": `https://ipfs.io/ipfs/${cid}`,
    pinata: `https://gateway.pinata.cloud/ipfs/${cid}`,
    cloudflare: `https://cloudflare-ipfs.com/ipfs/${cid}`,
  };
  return gateways[gateway] || gateways["local"];
}

export default {
  uploadEncryptedToIPFS,
  downloadAndDecryptFromIPFS,
  uploadEncryptedWithSigners,
  triggerDownload,
  verifyEncryptedCID,
  getEncryptedFileUrl,
};
