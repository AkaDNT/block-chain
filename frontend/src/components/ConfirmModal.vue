<template>
  <Teleport to="body">
    <Transition name="modal">
      <div
        v-if="isOpen"
        class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
        @click.self="cancel"
      >
        <div class="bg-white rounded-lg shadow-xl max-w-md w-full mx-4 overflow-hidden">
          <!-- Header -->
          <div :class="[
            'px-6 py-4 border-b',
            type === 'danger' && 'bg-red-50 border-red-200',
            type === 'warning' && 'bg-yellow-50 border-yellow-200',
            type === 'info' && 'bg-blue-50 border-blue-200',
            type === 'success' && 'bg-green-50 border-green-200'
          ]">
            <div class="flex items-center space-x-3">
              <!-- Danger Icon -->
              <div v-if="type === 'danger'" class="flex-shrink-0">
                <svg class="w-8 h-8 text-red-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                </svg>
              </div>

              <!-- Warning Icon -->
              <div v-else-if="type === 'warning'" class="flex-shrink-0">
                <svg class="w-8 h-8 text-yellow-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                </svg>
              </div>

              <!-- Info Icon -->
              <div v-else-if="type === 'info'" class="flex-shrink-0">
                <svg class="w-8 h-8 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>

              <!-- Success Icon -->
              <div v-else-if="type === 'success'" class="flex-shrink-0">
                <svg class="w-8 h-8 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>

              <h3 :class="[
                'text-lg font-bold',
                type === 'danger' && 'text-red-900',
                type === 'warning' && 'text-yellow-900',
                type === 'info' && 'text-blue-900',
                type === 'success' && 'text-green-900'
              ]">
                {{ title }}
              </h3>
            </div>
          </div>

          <!-- Body -->
          <div class="px-6 py-4">
            <p class="text-gray-700">{{ message }}</p>
            <p v-if="details" class="text-sm text-gray-500 mt-2">{{ details }}</p>
          </div>

          <!-- Footer -->
          <div class="px-6 py-4 bg-gray-50 flex gap-3 justify-end">
            <button
              @click="cancel"
              class="px-4 py-2 bg-white border border-gray-300 text-gray-700 rounded-lg font-semibold hover:bg-gray-50 transition-colors"
            >
              {{ cancelText }}
            </button>
            <button
              @click="confirm"
              :class="[
                'px-4 py-2 rounded-lg font-semibold transition-colors',
                type === 'danger' && 'bg-red-600 hover:bg-red-700 text-white',
                type === 'warning' && 'bg-yellow-600 hover:bg-yellow-700 text-white',
                type === 'info' && 'bg-blue-600 hover:bg-blue-700 text-white',
                type === 'success' && 'bg-green-600 hover:bg-green-700 text-white'
              ]"
            >
              {{ confirmText }}
            </button>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script>
import { toRefs } from 'vue'
import { confirmState } from '../utils/confirm.js'

export default {
  name: 'ConfirmModal',
  setup() {
    const cancel = () => {
      if (confirmState.onCancel) {
        confirmState.onCancel()
      }
      confirmState.isOpen = false
    }

    const confirm = () => {
      if (confirmState.onConfirm) {
        confirmState.onConfirm()
      }
      confirmState.isOpen = false
    }

    return {
      ...toRefs(confirmState),
      cancel,
      confirm
    }
  }
}
</script>

<style scoped>
.modal-enter-active,
.modal-leave-active {
  transition: opacity 0.2s ease;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}

.modal-enter-active .bg-white,
.modal-leave-active .bg-white {
  transition: transform 0.2s ease;
}

.modal-enter-from .bg-white {
  transform: scale(0.95);
}

.modal-leave-to .bg-white {
  transform: scale(0.95);
}
</style>
