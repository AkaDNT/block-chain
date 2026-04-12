import { createApp } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'
import App from './App.vue'

// Import views
import Home from './views/Home.vue'
import Register from './views/Register.vue'
import Trade from './views/Trade.vue'
import Dashboard from './views/Dashboard.vue'
import Admin from './views/Admin.vue'
import CompanyDashboard from './views/CompanyDashboard.vue'

// Import blockchain service
import blockchain from './utils/blockchain.js'

// Import styles
import './assets/style.css'

// Define routes
const routes = [
  { path: '/', name: 'Home', component: Home },
  { path: '/register', name: 'Register', component: Register },
  { path: '/trade', name: 'Trade', component: Trade },
  { path: '/dashboard', name: 'Dashboard', component: Dashboard },
  { path: '/company', name: 'CompanyDashboard', component: CompanyDashboard },
  { path: '/admin', name: 'Admin', component: Admin }
]

// Create router
const router = createRouter({
  history: createWebHistory(),
  routes
})

// Create and mount app
const app = createApp(App)
app.use(router)

// Make blockchain service globally available
app.config.globalProperties.$blockchain = blockchain

// Initialize blockchain service before mounting
blockchain.initialize().then(() => {
  app.mount('#app')
})
