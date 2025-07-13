import { clsx } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs) {
  return twMerge(clsx(inputs))
}

export function formatDate(date) {
  if (!date) return 'N/A'
  return new Date(date).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

export function formatNumber(number, decimals = 2) {
  if (number === null || number === undefined) return 'N/A'
  return Number(number).toFixed(decimals)
}

export function formatPercentage(value, decimals = 1) {
  if (value === null || value === undefined) return 'N/A'
  return `${Number(value).toFixed(decimals)}%`
}

export function getStatusColor(status) {
  const colors = {
    online: 'text-green-600 bg-green-50 border-green-200',
    offline: 'text-gray-600 bg-gray-50 border-gray-200',
    warning: 'text-yellow-600 bg-yellow-50 border-yellow-200',
    error: 'text-red-600 bg-red-50 border-red-200',
    maintenance: 'text-blue-600 bg-blue-50 border-blue-200'
  }
  return colors[status] || colors.offline
}

export function getAssetTypeIcon(type) {
  const icons = {
    hvac: '🌡️',
    pump: '⚙️',
    motor: '🔧',
    sensor: '📡',
    valve: '🔄',
    compressor: '💨',
    chiller: '❄️',
    boiler: '🔥',
    fan: '🌀',
    other: '📦'
  }
  return icons[type] || icons.other
}

export function calculateHealthScore(telemetryData) {
  if (!telemetryData || telemetryData.length === 0) return 0
  
  // Simple health score calculation based on recent data
  const recent = telemetryData.slice(0, 10) // Last 10 readings
  let score = 100
  
  recent.forEach(reading => {
    // Temperature checks
    if (reading.temperature) {
      if (reading.temperature < 15 || reading.temperature > 30) {
        score -= 5
      }
    }
    
    // Vibration checks
    if (reading.vibration && reading.vibration > 1.0) {
      score -= 10
    }
    
    // Power consumption anomalies
    if (reading.power_consumption && reading.power_consumption > 25) {
      score -= 5
    }
    
    // Status checks
    if (reading.status === 'warning') {
      score -= 3
    } else if (reading.status === 'error') {
      score -= 15
    }
  })
  
  return Math.max(0, Math.min(100, score))
}

export function generateMockTelemetry(assetType, count = 24) {
  const data = []
  const now = new Date()
  
  for (let i = count - 1; i >= 0; i--) {
    const timestamp = new Date(now.getTime() - i * 60 * 60 * 1000) // Hourly data
    
    let baseTemp, basePower, baseVibration
    
    switch (assetType) {
      case 'hvac':
        baseTemp = 22
        basePower = 12
        baseVibration = 0.3
        break
      case 'chiller':
        baseTemp = 8
        basePower = 35
        baseVibration = 0.5
        break
      case 'pump':
        baseTemp = 40
        basePower = 6
        baseVibration = 0.4
        break
      default:
        baseTemp = 25
        basePower = 10
        baseVibration = 0.3
    }
    
    data.push({
      timestamp: timestamp.toISOString(),
      temperature: baseTemp + (Math.random() - 0.5) * 4,
      humidity: 45 + (Math.random() - 0.5) * 20,
      pressure: 102 + (Math.random() - 0.5) * 4,
      vibration: baseVibration + (Math.random() - 0.5) * 0.2,
      power_consumption: basePower + (Math.random() - 0.5) * 4,
      status: Math.random() > 0.9 ? 'warning' : 'online'
    })
  }
  
  return data
}

export function debounce(func, wait) {
  let timeout
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout)
      func(...args)
    }
    clearTimeout(timeout)
    timeout = setTimeout(later, wait)
  }
}

export function throttle(func, limit) {
  let inThrottle
  return function() {
    const args = arguments
    const context = this
    if (!inThrottle) {
      func.apply(context, args)
      inThrottle = true
      setTimeout(() => inThrottle = false, limit)
    }
  }
}

