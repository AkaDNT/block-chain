import { reactive } from 'vue'

// Global confirm state
export const confirmState = reactive({
  isOpen: false,
  title: '',
  message: '',
  details: '',
  type: 'info', // 'danger', 'warning', 'info', 'success'
  confirmText: 'Confirm',
  cancelText: 'Cancel',
  onConfirm: null,
  onCancel: null
})

/**
 * Show a confirmation dialog
 * @param {Object} options - Confirmation options
 * @param {string} options.title - Dialog title
 * @param {string} options.message - Main message
 * @param {string} options.details - Optional additional details
 * @param {'danger'|'warning'|'info'|'success'} options.type - Dialog type
 * @param {string} options.confirmText - Confirm button text
 * @param {string} options.cancelText - Cancel button text
 * @returns {Promise<boolean>} - Resolves to true if confirmed, false if cancelled
 */
export function confirm({
  title = 'Confirm Action',
  message = 'Are you sure you want to proceed?',
  details = '',
  type = 'info',
  confirmText = 'Confirm',
  cancelText = 'Cancel'
}) {
  return new Promise((resolve) => {
    confirmState.title = title
    confirmState.message = message
    confirmState.details = details
    confirmState.type = type
    confirmState.confirmText = confirmText
    confirmState.cancelText = cancelText

    confirmState.onConfirm = () => {
      resolve(true)
    }

    confirmState.onCancel = () => {
      resolve(false)
    }

    confirmState.isOpen = true
  })
}

/**
 * Show a danger confirmation dialog
 */
export function confirmDanger(message, title = 'Confirm Action', details = '') {
  return confirm({
    title,
    message,
    details,
    type: 'danger',
    confirmText: 'Delete',
    cancelText: 'Cancel'
  })
}

/**
 * Show a warning confirmation dialog
 */
export function confirmWarning(message, title = 'Warning', details = '') {
  return confirm({
    title,
    message,
    details,
    type: 'warning',
    confirmText: 'Continue',
    cancelText: 'Cancel'
  })
}

/**
 * Show an info confirmation dialog
 */
export function confirmInfo(message, title = 'Confirm', details = '') {
  return confirm({
    title,
    message,
    details,
    type: 'info',
    confirmText: 'OK',
    cancelText: 'Cancel'
  })
}

export default {
  confirm,
  confirmDanger,
  confirmWarning,
  confirmInfo
}
