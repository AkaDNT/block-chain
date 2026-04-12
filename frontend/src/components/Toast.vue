<template>
  <Teleport to="body">
    <div class="fixed top-4 right-4 z-50 space-y-2">
      <TransitionGroup name="toast">
        <div
          v-for="toast in toasts"
          :key="toast.id"
          :class="[
            'flex items-start gap-3 p-4 rounded-lg shadow-lg max-w-md',
            'backdrop-blur-sm border',
            toast.type === 'success' && 'bg-green-50 border-green-200',
            toast.type === 'error' && 'bg-red-50 border-red-200',
            toast.type === 'info' && 'bg-blue-50 border-blue-200',
            toast.type === 'warning' && 'bg-yellow-50 border-yellow-200'
          ]"
        >
          <!-- Icon -->
          <div class="flex-shrink-0">
            <!-- Success Icon -->
            <svg
              v-if="toast.type === 'success'"
              class="w-6 h-6 text-green-600"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
              />
            </svg>

            <!-- Error Icon -->
            <svg
              v-else-if="toast.type === 'error'"
              class="w-6 h-6 text-red-600"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z"
              />
            </svg>

            <!-- Info Icon -->
            <svg
              v-else-if="toast.type === 'info'"
              class="w-6 h-6 text-blue-600"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
              />
            </svg>

            <!-- Warning Icon -->
            <svg
              v-else-if="toast.type === 'warning'"
              class="w-6 h-6 text-yellow-600"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
              />
            </svg>
          </div>

          <!-- Content -->
          <div class="flex-1 min-w-0">
            <p
              v-if="toast.title"
              :class="[
                'font-semibold text-sm',
                toast.type === 'success' && 'text-green-900',
                toast.type === 'error' && 'text-red-900',
                toast.type === 'info' && 'text-blue-900',
                toast.type === 'warning' && 'text-yellow-900'
              ]"
            >
              {{ toast.title }}
            </p>
            <p
              :class="[
                'text-sm',
                toast.title ? 'mt-1' : '',
                toast.type === 'success' && 'text-green-700',
                toast.type === 'error' && 'text-red-700',
                toast.type === 'info' && 'text-blue-700',
                toast.type === 'warning' && 'text-yellow-700'
              ]"
            >
              {{ toast.message }}
            </p>
          </div>

          <!-- Close Button -->
          <button
            @click="removeToast(toast.id)"
            :class="[
              'flex-shrink-0 rounded-lg p-1 hover:bg-black/5 transition-colors',
              toast.type === 'success' && 'text-green-600',
              toast.type === 'error' && 'text-red-600',
              toast.type === 'info' && 'text-blue-600',
              toast.type === 'warning' && 'text-yellow-600'
            ]"
          >
            <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
              <path
                fill-rule="evenodd"
                d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z"
                clip-rule="evenodd"
              />
            </svg>
          </button>
        </div>
      </TransitionGroup>
    </div>
  </Teleport>
</template>

<script>
import { toastState } from '../utils/toast.js'

export default {
  name: 'Toast',
  setup() {
    const removeToast = (id) => {
      const index = toastState.toasts.findIndex(t => t.id === id)
      if (index > -1) {
        toastState.toasts.splice(index, 1)
      }
    }

    return {
      toasts: toastState.toasts,
      removeToast
    }
  }
}
</script>

<style scoped>
.toast-enter-active,
.toast-leave-active {
  transition: all 0.3s ease;
}

.toast-enter-from {
  opacity: 0;
  transform: translateX(100%);
}

.toast-leave-to {
  opacity: 0;
  transform: translateX(100%);
}
</style>
