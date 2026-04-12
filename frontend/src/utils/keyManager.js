/**
 * Key Manager - Global encryption key from environment variable
 *
 * Set VITE_ENCRYPTION_KEY in your .env file
 * All encryption/decryption will use this key automatically
 */

import { ethers } from "ethers";

// Get key from environment variable
const DEFAULT_DEV_ENCRYPTION_KEY =
  "0x59c6995e998f97a5a004497e5d7d8f2b2c1d4c1b3f3c9b1a6b1d2c3d4e5f6789";
const ENV_KEY =
  import.meta.env.VITE_ENCRYPTION_KEY || DEFAULT_DEV_ENCRYPTION_KEY;

// Cached wallet instance
let cachedWallet = null;

/**
 * Initialize wallet from environment key
 */
function initWallet() {
  if (cachedWallet) return cachedWallet;

  if (!ENV_KEY) {
    console.error("❌ VITE_ENCRYPTION_KEY not set in .env file");
    return null;
  }

  try {
    const normalizedKey = ENV_KEY.startsWith("0x") ? ENV_KEY : "0x" + ENV_KEY;
    cachedWallet = new ethers.Wallet(normalizedKey);
    if (import.meta.env.VITE_ENCRYPTION_KEY) {
      console.log(
        "🔐 Global encryption key loaded for address:",
        cachedWallet.address,
      );
    } else {
      console.warn(
        "⚠️ VITE_ENCRYPTION_KEY missing, using built-in local dev encryption key",
      );
    }
    return cachedWallet;
  } catch (error) {
    console.error("❌ Invalid VITE_ENCRYPTION_KEY:", error.message);
    return null;
  }
}

/**
 * Get the global private key
 * @returns {string|null}
 */
export function getPrivateKey() {
  const wallet = initWallet();
  return wallet?.privateKey || null;
}

/**
 * Get the global public key
 * @returns {string|null}
 */
export function getPublicKey() {
  const wallet = initWallet();
  return wallet?.signingKey?.publicKey || null;
}

/**
 * Check if key is configured
 * @returns {boolean}
 */
export function hasKey() {
  return initWallet() !== null;
}

/**
 * Get the wallet address for the global key
 * @returns {string|null}
 */
export function getKeyAddress() {
  const wallet = initWallet();
  return wallet?.address || null;
}

/**
 * Get private key - returns global key (no prompt needed)
 * @returns {string|null}
 */
export function getOrPromptKey() {
  const key = getPrivateKey();
  if (!key) {
    console.error(
      "❌ No encryption key configured. Set VITE_ENCRYPTION_KEY in .env",
    );
    alert(
      "Encryption key not configured. Please set VITE_ENCRYPTION_KEY in your .env file.",
    );
  }
  return key;
}

/**
 * Get the wallet instance
 * @returns {ethers.Wallet|null}
 */
export function getWallet() {
  return initWallet();
}

export default {
  getPrivateKey,
  getPublicKey,
  hasKey,
  getKeyAddress,
  getOrPromptKey,
  getWallet,
};
