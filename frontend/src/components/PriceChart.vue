<template>
  <div class="pixel-border bg-gray-800 p-4 rounded-lg">
    <div class="flex justify-between items-center mb-4">
      <h3 class="text-cyan-400 text-[0.8rem] font-bold">{{ tokenSymbol }} PRICE CHART</h3>
      <div class="flex space-x-2">
        <button
          v-for="period in periods"
          :key="period"
          @click="selectedPeriod = period"
          :class="selectedPeriod === period ? 'bg-cyan-400 text-gray-900' : 'bg-gray-700 text-cyan-400'"
          class="pixel-btn px-2 py-1 text-[0.5rem]"
        >
          {{ period }}
        </button>
      </div>
    </div>

    <div class="relative h-64 bg-gray-900 border-2 border-cyan-400 p-2">
      <!-- Grid Lines -->
      <svg class="absolute inset-0 w-full h-full opacity-20">
        <defs>
          <pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse">
            <path d="M 40 0 L 0 0 0 40" fill="none" stroke="rgba(0,255,136,0.3)" stroke-width="1"/>
          </pattern>
        </defs>
        <rect width="100%" height="100%" fill="url(#grid)" />
      </svg>

      <!-- Price Line Chart -->
      <svg class="relative w-full h-full">
        <!-- Price Line -->
        <polyline
          :points="chartPoints"
          fill="none"
          stroke="url(#lineGradient)"
          stroke-width="3"
          class="drop-shadow-lg"
        />

        <!-- Area Fill -->
        <polygon
          :points="areaPoints"
          fill="url(#areaGradient)"
          opacity="0.3"
        />

        <!-- Price Points -->
        <circle
          v-for="(point, index) in priceData"
          :key="index"
          :cx="getX(index)"
          :cy="getY(point.price)"
          r="4"
          :fill="point.price > priceData[0].price ? '#00ff88' : '#ff0088'"
          class="animate-pulse"
        />

        <defs>
          <linearGradient id="lineGradient" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" style="stop-color:#00ff88;stop-opacity:1" />
            <stop offset="50%" style="stop-color:#00ccff;stop-opacity:1" />
            <stop offset="100%" style="stop-color:#ff00ff;stop-opacity:1" />
          </linearGradient>
          <linearGradient id="areaGradient" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" style="stop-color:#00ff88;stop-opacity:0.5" />
            <stop offset="100%" style="stop-color:#00ff88;stop-opacity:0" />
          </linearGradient>
        </defs>
      </svg>

      <!-- Current Price Indicator -->
      <div class="absolute top-2 left-2 bg-gray-900 border-2 border-green-400 px-3 py-1">
        <p class="text-green-400 text-[0.6rem]">CURRENT</p>
        <p class="text-green-400 text-[0.9rem] font-bold">${{ currentPrice.toFixed(2) }}</p>
        <p :class="priceChange >= 0 ? 'text-green-400' : 'text-red-400'" class="text-[0.5rem]">
          {{ priceChange >= 0 ? '▲' : '▼' }} {{ Math.abs(priceChange).toFixed(2) }}%
        </p>
      </div>
    </div>

    <!-- Stats Row -->
    <div class="grid grid-cols-4 gap-2 mt-4">
      <div class="bg-gray-900 border-2 border-cyan-400 p-2 text-center">
        <p class="text-cyan-400 text-[0.5rem]">24H HIGH</p>
        <p class="text-green-400 text-[0.7rem] font-bold">${{ high24h.toFixed(2) }}</p>
      </div>
      <div class="bg-gray-900 border-2 border-cyan-400 p-2 text-center">
        <p class="text-cyan-400 text-[0.5rem]">24H LOW</p>
        <p class="text-red-400 text-[0.7rem] font-bold">${{ low24h.toFixed(2) }}</p>
      </div>
      <div class="bg-gray-900 border-2 border-cyan-400 p-2 text-center">
        <p class="text-cyan-400 text-[0.5rem]">VOLUME</p>
        <p class="text-cyan-400 text-[0.7rem] font-bold">{{ volume }}K</p>
      </div>
      <div class="bg-gray-900 border-2 border-cyan-400 p-2 text-center">
        <p class="text-cyan-400 text-[0.5rem]">MARKET CAP</p>
        <p class="text-cyan-400 text-[0.7rem] font-bold">${{ marketCap }}M</p>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, onUnmounted } from 'vue'

export default {
  name: 'PriceChart',
  props: {
    tokenSymbol: {
      type: String,
      default: 'BUSD'
    }
  },
  setup() {
    const periods = ['1H', '1D', '1W', '1M']
    const selectedPeriod = ref('1D')
    const priceData = ref([])
    const chartWidth = 600
    const chartHeight = 240

    // Generate mock price data
    const generatePriceData = () => {
      const basePrice = 1.0
      const data = []
      const points = 50

      for (let i = 0; i < points; i++) {
        const volatility = 0.02
        const trend = Math.sin(i / 10) * 0.01
        const random = (Math.random() - 0.5) * volatility
        const price = basePrice + trend + random + (i * 0.0001)

        data.push({
          time: new Date(Date.now() - (points - i) * 3600000).toISOString(),
          price: Math.max(0.95, Math.min(1.05, price))
        })
      }

      return data
    }

    priceData.value = generatePriceData()

    const currentPrice = computed(() => {
      return priceData.value[priceData.value.length - 1]?.price || 1.0
    })

    const priceChange = computed(() => {
      if (priceData.value.length < 2) return 0
      const first = priceData.value[0].price
      const last = currentPrice.value
      return ((last - first) / first) * 100
    })

    const high24h = computed(() => {
      return Math.max(...priceData.value.map(d => d.price))
    })

    const low24h = computed(() => {
      return Math.min(...priceData.value.map(d => d.price))
    })

    const volume = computed(() => {
      return (Math.random() * 500 + 100).toFixed(0)
    })

    const marketCap = computed(() => {
      return (Math.random() * 50 + 10).toFixed(1)
    })

    const getX = (index) => {
      const padding = 20
      const width = chartWidth - padding * 2
      return padding + (index / (priceData.value.length - 1)) * width
    }

    const getY = (price) => {
      const padding = 20
      const height = chartHeight - padding * 2
      const min = low24h.value
      const max = high24h.value
      const range = max - min || 0.01
      return chartHeight - padding - ((price - min) / range) * height
    }

    const chartPoints = computed(() => {
      return priceData.value.map((point, index) => {
        return `${getX(index)},${getY(point.price)}`
      }).join(' ')
    })

    const areaPoints = computed(() => {
      const points = priceData.value.map((point, index) => {
        return `${getX(index)},${getY(point.price)}`
      }).join(' ')

      const lastX = getX(priceData.value.length - 1)
      const firstX = getX(0)
      const bottom = chartHeight - 20

      return `${points} ${lastX},${bottom} ${firstX},${bottom}`
    })

    // Update prices periodically
    let interval
    onMounted(() => {
      interval = setInterval(() => {
        // Add new price point
        const lastPrice = priceData.value[priceData.value.length - 1].price
        const change = (Math.random() - 0.5) * 0.01
        const newPrice = Math.max(0.95, Math.min(1.05, lastPrice + change))

        priceData.value.push({
          time: new Date().toISOString(),
          price: newPrice
        })

        // Keep only last 50 points
        if (priceData.value.length > 50) {
          priceData.value.shift()
        }
      }, 3000) // Update every 3 seconds
    })

    onUnmounted(() => {
      if (interval) clearInterval(interval)
    })

    return {
      periods,
      selectedPeriod,
      priceData,
      currentPrice,
      priceChange,
      high24h,
      low24h,
      volume,
      marketCap,
      chartPoints,
      areaPoints,
      getX,
      getY
    }
  }
}
</script>

<style scoped>
.drop-shadow-lg {
  filter: drop-shadow(0 0 10px rgba(0, 255, 136, 0.5));
}
</style>
