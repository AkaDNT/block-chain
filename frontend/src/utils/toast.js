import { reactive } from 'vue'

// Global toast state
export const toastState = reactive({
  toasts: []
})

let toastId = 0

/**
 * Show a toast notification
 * @param {Object} options - Toast options
 * @param {string} options.message - Toast message
 * @param {string} options.title - Optional toast title
 * @param {'success'|'error'|'info'|'warning'} options.type - Toast type
 * @param {number} options.duration - Duration in ms (default: 5000)
 */
function showToast({ message, title = '', type = 'info', duration = 5000 }) {
  const id = ++toastId

  const toast = {
    id,
    message,
    title,
    type
  }

  toastState.toasts.push(toast)

  // Auto remove after duration
  if (duration > 0) {
    setTimeout(() => {
      const index = toastState.toasts.findIndex(t => t.id === id)
      if (index > -1) {
        toastState.toasts.splice(index, 1)
      }
    }, duration)
  }

  return id
}

/**
 * Show success toast
 * @param {string} message - Success message
 * @param {string} title - Optional title
 */
export function success(message, title = 'Success') {
  return showToast({ message, title, type: 'success' })
}

/**
 * Show error toast
 * @param {string} message - Error message
 * @param {string} title - Optional title
 */
export function error(message, title = 'Error') {
  return showToast({ message, title, type: 'error' })
}

/**
 * Show info toast
 * @param {string} message - Info message
 * @param {string} title - Optional title
 */
export function info(message, title = '') {
  return showToast({ message, title, type: 'info' })
}

/**
 * Show warning toast
 * @param {string} message - Warning message
 * @param {string} title - Optional title
 */
export function warning(message, title = 'Warning') {
  return showToast({ message, title, type: 'warning' })
}

/**
 * Parse blockchain/transaction error to user-friendly message
 * @param {Error} err - Error object
 * @param {string} fallback - Fallback message if parsing fails
 * @returns {string} User-friendly error message
 */
export function parseError(err, fallback = 'Please try again.') {
  if (!err) return fallback

  // Check for reason first (ethers.js provides this)
  if (err.reason) {
    return err.reason
  }

  // Check for revert args (contract revert messages)
  if (err.revert?.args?.[0]) {
    return err.revert.args[0]
  }

  const message = err.message || ''

  // User rejected transaction
  if (message.includes('user rejected') || message.includes('User denied')) {
    return 'Transaction was cancelled'
  }

  // Insufficient token balance
  if (message.includes('Insufficient balance')) {
    return 'Insufficient balance to complete this transaction'
  }

  // Insufficient ETH for gas
  if (message.includes('insufficient funds')) {
    return 'Insufficient funds for gas fees'
  }

  // Slippage error
  if (message.includes('slippage') || message.includes('INSUFFICIENT_OUTPUT')) {
    return 'Price moved too much. Try increasing slippage tolerance'
  }

  // Already exists errors
  if (message.includes('already') && message.includes('request')) {
    return 'You already have a pending request'
  }

  // Not verified errors
  if (message.includes('not verified') || message.includes('NotVerified')) {
    return 'Account is not verified'
  }

  // Not authorized
  if (message.includes('Only admin') || message.includes('Only verifier') || message.includes('unauthorized')) {
    return 'You are not authorized to perform this action'
  }

  // Network errors
  if (message.includes('network') || message.includes('disconnected')) {
    return 'Network error. Please check your connection'
  }

  return fallback
}

/**
 * Show error toast with parsed blockchain error
 * @param {Error} err - Error object
 * @param {string} title - Toast title
 * @param {string} fallback - Fallback message
 */
export function txError(err, title = 'Transaction Failed', fallback = 'Please try again.') {
  const message = parseError(err, fallback)
  return showToast({ message, title, type: 'error' })
}

/**
 * Remove a specific toast
 * @param {number} id - Toast ID
 */
export function remove(id) {
  const index = toastState.toasts.findIndex(t => t.id === id)
  if (index > -1) {
    toastState.toasts.splice(index, 1)
  }
}

/**
 * Clear all toasts
 */
export function clear() {
  toastState.toasts = []
}

/**
 * Show a transaction step toast - for informing users what MetaMask action they're approving
 * @param {string} action - The action being performed (e.g., 'Approving tokens', 'Swapping')
 * @param {string} details - Additional details about the transaction
 */
export function txStep(action, details = '') {
  const message = details ? `${action}\n${details}` : action
  return showToast({
    message,
    title: 'Confirming in MetaMask',
    type: 'info',
    duration: 10000 // Longer duration for tx steps
  })
}

/**
 * Show transaction pending toast
 * @param {string} action - The action being processed
 */
export function txPending(action = 'Transaction submitted') {
  return showToast({
    message: `${action}. Waiting for blockchain confirmation...`,
    title: 'Processing',
    type: 'info',
    duration: 15000
  })
}

/**
 * Show transaction confirmed toast
 * @param {string} action - The action that was completed
 * @param {string} details - Additional details
 */
export function txConfirmed(action, details = '') {
  const message = details ? `${action}\n${details}` : action
  return showToast({
    message,
    title: 'Confirmed',
    type: 'success',
    duration: 5000
  })
}

export default {
  success,
  error,
  info,
  warning,
  remove,
  clear,
  parseError,
  txError,
  txStep,
  txPending,
  txConfirmed
}
