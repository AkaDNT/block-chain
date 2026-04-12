<template>
  <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
    <div class="flex justify-between items-center mb-6">
      <div>
        <h3 class="text-lg font-bold text-gray-900">{{ tokenSymbol }} Price History</h3>
        <p class="text-sm text-gray-500 mt-1">Real-time price tracking</p>
      </div>
      <div class="flex space-x-2">
        <button
          v-for="period in periods"
          :key="period.value"
          @click="selectedPeriod = period.value"
          :class="selectedPeriod === period.value ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-600 hover:bg-gray-200'"
          class="px-3 py-1.5 rounded-lg text-xs font-medium transition-colors duration-150"
        >
          {{ period.label }}
        </button>
      </div>
    </div>

    <!-- Chart Canvas -->
    <div class="relative h-80">
      <canvas ref="chartCanvas"></canvas>
    </div>

    <!-- Stats Grid -->
    <div class="grid grid-cols-4 gap-4 mt-6 pt-6 border-t border-gray-200">
      <div class="text-center">
        <p class="text-xs text-gray-500 mb-1">Current Price</p>
        <p class="text-lg font-bold text-gray-900">${{ currentPrice.toFixed(4) }}</p>
        <p :class="priceChange >= 0 ? 'text-green-600' : 'text-red-600'" class="text-xs font-semibold mt-1">
          {{ priceChange >= 0 ? '▲' : '▼' }} {{ Math.abs(priceChange).toFixed(2) }}%
        </p>
      </div>
      <div class="text-center">
        <p class="text-xs text-gray-500 mb-1">24h High</p>
        <p class="text-lg font-bold text-green-600">${{ high24h.toFixed(4) }}</p>
      </div>
      <div class="text-center">
        <p class="text-xs text-gray-500 mb-1">24h Low</p>
        <p class="text-lg font-bold text-red-600">${{ low24h.toFixed(4) }}</p>
      </div>
      <div class="text-center">
        <p class="text-xs text-gray-500 mb-1">24h Volume</p>
        <p class="text-lg font-bold text-blue-600">${{ volume.toFixed(0) }}K</p>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, watch, onMounted, onUnmounted, onBeforeUnmount, markRaw, shallowRef } from 'vue'
import {
  Chart,
  LineController,
  LineElement,
  PointElement,
  LinearScale,
  CategoryScale,
  Filler,
  Tooltip,
  Legend
} from 'chart.js'
import blockchain from '../utils/blockchain.js'

// Register Chart.js components
Chart.register(
  LineController,
  LineElement,
  PointElement,
  LinearScale,
  CategoryScale,
  Filler,
  Tooltip,
  Legend
)

export default {
  name: 'TokenPriceChart',
  props: {
    tokenSymbol: {
      type: String,
      default: 'TOKEN'
    },
    initialPrice: {
      type: Number,
      default: 10.0
    },
    ammPool: {
      type: String,
      default: null
    }
  },
  setup(props) {
    const chartCanvas = ref(null)
    let chartInstance = null
    let updateInterval = null

    const periods = [
      { value: '1H', label: '1H' },
      { value: '24H', label: '24H' },
      { value: '7D', label: '7D' },
      { value: '30D', label: '30D' }
    ]
    const selectedPeriod = ref('24H')

    // Use shallowRef to prevent deep reactivity issues with Chart.js
    const priceData = shallowRef([])
    const labels = shallowRef([])
    const volumeData = ref(0)
    const isLoading = ref(false)

    // Load actual price history from blockchain
    const loadPriceHistory = async () => {
      if (!props.ammPool) {
        generateFallbackData()
        return
      }

      isLoading.value = true
      try {
        const history = await blockchain.getPriceHistory(props.ammPool, 50)

        if (history.length > 0) {
          const data = history.map(h => h.price)
          const labs = history.map(h =>
            h.timestamp.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' })
          )

          priceData.value = data
          labels.value = labs

          // Calculate volume
          volumeData.value = history.reduce((sum, h) => sum + (h.volume || 0), 0)

          console.log('📊 Loaded price history:', data.length, 'points')
        } else {
          generateFallbackData()
        }
      } catch (error) {
        console.error('Error loading price history:', error)
        generateFallbackData()
      } finally {
        isLoading.value = false
      }
    }

    // Fallback: Generate data based on current price if no history
    const generateFallbackData = () => {
      const data = []
      const labs = []
      const points = 50
      const basePrice = props.initialPrice

      // Generate slight variations around current price
      for (let i = 0; i < points; i++) {
        const volatility = basePrice * 0.005 // 0.5% volatility for fallback
        const random = (Math.random() - 0.5) * volatility
        data.push(Math.max(basePrice * 0.99, Math.min(basePrice * 1.01, basePrice + random)))

        const time = new Date(Date.now() - (points - i) * 60000)
        labs.push(time.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' }))
      }

      // Ensure last point is current price
      data[data.length - 1] = basePrice

      priceData.value = data
      labels.value = labs
    }

    const currentPrice = computed(() => {
      return priceData.value[priceData.value.length - 1] || props.initialPrice
    })

    const priceChange = computed(() => {
      if (priceData.value.length < 2) return 0
      const first = priceData.value[0]
      const last = currentPrice.value
      if (first === 0) return 0
      return ((last - first) / first) * 100
    })

    const high24h = computed(() => {
      if (priceData.value.length === 0) return props.initialPrice
      return Math.max(...priceData.value)
    })

    const low24h = computed(() => {
      if (priceData.value.length === 0) return props.initialPrice
      return Math.min(...priceData.value)
    })

    const volume = computed(() => {
      return volumeData.value / 1000 // Convert to K
    })

    const createChart = () => {
      if (!chartCanvas.value) return

      const ctx = chartCanvas.value.getContext('2d')

      // Destroy existing chart
      if (chartInstance) {
        chartInstance.destroy()
        chartInstance = null
      }

      // Use markRaw to prevent Vue from making Chart.js instance reactive
      chartInstance = markRaw(new Chart(ctx, {
        type: 'line',
        data: {
          labels: labels.value,
          datasets: [{
            label: `${props.tokenSymbol} Price`,
            data: priceData.value,
            borderColor: priceChange.value >= 0 ? 'rgb(34, 197, 94)' : 'rgb(239, 68, 68)',
            backgroundColor: priceChange.value >= 0
              ? 'rgba(34, 197, 94, 0.1)'
              : 'rgba(239, 68, 68, 0.1)',
            borderWidth: 2,
            fill: true,
            tension: 0.4,
            pointRadius: 0,
            pointHoverRadius: 6,
            pointHoverBackgroundColor: priceChange.value >= 0 ? 'rgb(34, 197, 94)' : 'rgb(239, 68, 68)',
            pointHoverBorderColor: '#fff',
            pointHoverBorderWidth: 2
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          interaction: {
            intersect: false,
            mode: 'index'
          },
          plugins: {
            legend: {
              display: false
            },
            tooltip: {
              backgroundColor: 'rgba(0, 0, 0, 0.8)',
              padding: 12,
              titleColor: '#fff',
              bodyColor: '#fff',
              borderColor: priceChange.value >= 0 ? 'rgb(34, 197, 94)' : 'rgb(239, 68, 68)',
              borderWidth: 1,
              displayColors: false,
              callbacks: {
                label: function(context) {
                  return `$${context.parsed.y.toFixed(4)}`
                }
              }
            }
          },
          scales: {
            x: {
              display: true,
              grid: {
                display: false
              },
              ticks: {
                maxTicksLimit: 8,
                color: '#9ca3af',
                font: {
                  size: 11
                }
              }
            },
            y: {
              display: true,
              position: 'right',
              grid: {
                color: 'rgba(156, 163, 175, 0.1)',
                drawBorder: false
              },
              ticks: {
                color: '#9ca3af',
                font: {
                  size: 11
                },
                callback: function(value) {
                  return '$' + value.toFixed(2)
                }
              }
            }
          }
        }
      }))
    }

    const updateChart = () => {
      if (!chartInstance) return

      chartInstance.data.labels = labels.value
      chartInstance.data.datasets[0].data = priceData.value
      chartInstance.data.datasets[0].borderColor = priceChange.value >= 0 ? 'rgb(34, 197, 94)' : 'rgb(239, 68, 68)'
      chartInstance.data.datasets[0].backgroundColor = priceChange.value >= 0
        ? 'rgba(34, 197, 94, 0.1)'
        : 'rgba(239, 68, 68, 0.1)'
      chartInstance.data.datasets[0].pointHoverBackgroundColor = priceChange.value >= 0 ? 'rgb(34, 197, 94)' : 'rgb(239, 68, 68)'
      chartInstance.update('none')
    }

    const refreshPrice = async () => {
      // Fetch current price from AMM and add to chart
      if (!props.ammPool) return

      try {
        const currentAMMPrice = await blockchain.getAMMPrice(props.ammPool)
        const newPrice = parseFloat(currentAMMPrice)

        if (newPrice > 0 && newPrice !== priceData.value[priceData.value.length - 1]) {
          const newPriceData = [...priceData.value, newPrice]
          const time = new Date()
          const newLabels = [...labels.value, time.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' })]

          // Keep only last 50 points
          if (newPriceData.length > 50) {
            priceData.value = newPriceData.slice(-50)
            labels.value = newLabels.slice(-50)
          } else {
            priceData.value = newPriceData
            labels.value = newLabels
          }

          updateChart()
        }
      } catch (error) {
        console.warn('Error refreshing price:', error)
      }
    }

    const cleanup = () => {
      if (updateInterval) {
        clearInterval(updateInterval)
        updateInterval = null
      }
      if (chartInstance) {
        chartInstance.destroy()
        chartInstance = null
      }
    }

    watch(selectedPeriod, async () => {
      await loadPriceHistory()
      updateChart()
    })

    // Watch for token/pool changes and reload data
    watch(() => props.ammPool, async () => {
      cleanup()
      await loadPriceHistory()
      createChart()

      // Restart update interval - refresh every 10 seconds
      updateInterval = setInterval(() => {
        refreshPrice()
      }, 10000)
    })

    watch(() => props.initialPrice, async () => {
      cleanup()
      await loadPriceHistory()
      createChart()

      // Restart update interval
      updateInterval = setInterval(() => {
        refreshPrice()
      }, 10000)
    })

    onMounted(async () => {
      await loadPriceHistory()
      createChart()

      // Refresh price every 10 seconds from blockchain
      updateInterval = setInterval(() => {
        refreshPrice()
      }, 10000)
    })

    onBeforeUnmount(() => {
      cleanup()
    })

    onUnmounted(() => {
      cleanup()
    })

    return {
      chartCanvas,
      periods,
      selectedPeriod,
      currentPrice,
      priceChange,
      high24h,
      low24h,
      volume
    }
  }
}
</script>
