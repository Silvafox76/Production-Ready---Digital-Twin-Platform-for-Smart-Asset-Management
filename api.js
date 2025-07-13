import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

// Create axios instance with default config
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor
api.interceptors.request.use(
  (config) => {
    // Add auth token if available
    const token = localStorage.getItem('auth_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor
api.interceptors.response.use(
  (response) => {
    return response.data
  },
  (error) => {
    console.error('API Error:', error)
    
    if (error.response?.status === 401) {
      // Handle unauthorized access
      localStorage.removeItem('auth_token')
      // Redirect to login if needed
    }
    
    return Promise.reject(error)
  }
)

export const apiService = {
  // Health check
  async healthCheck() {
    return api.get('/health')
  },

  // Asset management
  async getAssets(skip = 0, limit = 100) {
    return api.get(`/api/v1/assets?skip=${skip}&limit=${limit}`)
  },

  async getAsset(assetId) {
    return api.get(`/api/v1/assets/${assetId}`)
  },

  async createAsset(assetData) {
    return api.post('/api/v1/assets', assetData)
  },

  async updateAsset(assetId, assetData) {
    return api.put(`/api/v1/assets/${assetId}`, assetData)
  },

  async deleteAsset(assetId) {
    return api.delete(`/api/v1/assets/${assetId}`)
  },

  // Telemetry data
  async getAssetTelemetry(assetId, params = {}) {
    const queryParams = new URLSearchParams(params).toString()
    return api.get(`/api/v1/assets/${assetId}/telemetry?${queryParams}`)
  },

  async createTelemetry(telemetryData) {
    return api.post('/api/v1/telemetry', telemetryData)
  },

  // ML predictions (if implemented)
  async getPredictions(assetId) {
    return api.get(`/api/v1/assets/${assetId}/predictions`)
  },

  async getHealthScore(assetId) {
    return api.get(`/api/v1/assets/${assetId}/health`)
  },

  // Analytics
  async getAssetAnalytics(assetId, timeRange = '24h') {
    return api.get(`/api/v1/assets/${assetId}/analytics?range=${timeRange}`)
  },

  async getDashboardStats() {
    return api.get('/api/v1/dashboard/stats')
  },

  // Alerts and notifications
  async getAlerts(params = {}) {
    const queryParams = new URLSearchParams(params).toString()
    return api.get(`/api/v1/alerts?${queryParams}`)
  },

  async acknowledgeAlert(alertId) {
    return api.post(`/api/v1/alerts/${alertId}/acknowledge`)
  },

  // System status
  async getSystemStatus() {
    return api.get('/api/v1/system/status')
  },
}

// WebSocket connection for real-time data
export class WebSocketService {
  constructor() {
    this.ws = null
    this.listeners = new Map()
    this.reconnectAttempts = 0
    this.maxReconnectAttempts = 5
    this.reconnectDelay = 1000
  }

  connect() {
    const wsUrl = API_BASE_URL.replace('http', 'ws') + '/ws/telemetry'
    
    try {
      this.ws = new WebSocket(wsUrl)
      
      this.ws.onopen = () => {
        console.log('WebSocket connected')
        this.reconnectAttempts = 0
        this.emit('connected')
      }
      
      this.ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data)
          this.emit('message', data)
          
          // Emit specific event types
          if (data.type) {
            this.emit(data.type, data.data)
          }
        } catch (error) {
          console.error('Failed to parse WebSocket message:', error)
        }
      }
      
      this.ws.onclose = () => {
        console.log('WebSocket disconnected')
        this.emit('disconnected')
        this.attemptReconnect()
      }
      
      this.ws.onerror = (error) => {
        console.error('WebSocket error:', error)
        this.emit('error', error)
      }
    } catch (error) {
      console.error('Failed to create WebSocket connection:', error)
    }
  }

  disconnect() {
    if (this.ws) {
      this.ws.close()
      this.ws = null
    }
  }

  attemptReconnect() {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++
      console.log(`Attempting to reconnect (${this.reconnectAttempts}/${this.maxReconnectAttempts})...`)
      
      setTimeout(() => {
        this.connect()
      }, this.reconnectDelay * this.reconnectAttempts)
    } else {
      console.error('Max reconnection attempts reached')
      this.emit('maxReconnectAttemptsReached')
    }
  }

  on(event, callback) {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, [])
    }
    this.listeners.get(event).push(callback)
  }

  off(event, callback) {
    if (this.listeners.has(event)) {
      const callbacks = this.listeners.get(event)
      const index = callbacks.indexOf(callback)
      if (index > -1) {
        callbacks.splice(index, 1)
      }
    }
  }

  emit(event, data) {
    if (this.listeners.has(event)) {
      this.listeners.get(event).forEach(callback => {
        try {
          callback(data)
        } catch (error) {
          console.error('Error in WebSocket event callback:', error)
        }
      })
    }
  }

  send(data) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(data))
    } else {
      console.warn('WebSocket is not connected')
    }
  }
}

// Create singleton instance
export const wsService = new WebSocketService()

export default api

