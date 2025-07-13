import React, { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { 
  ArrowLeft, 
  Edit, 
  Trash2, 
  Download, 
  AlertTriangle,
  TrendingUp,
  TrendingDown,
  Activity,
  Thermometer,
  Droplets,
  Zap,
  Gauge
} from 'lucide-react'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, AreaChart, Area } from 'recharts'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card'
import { Button } from './ui/button'
import { Badge } from './ui/badge'
import { formatDate, formatNumber, getStatusColor, generateMockTelemetry, calculateHealthScore } from '../lib/utils'
import { apiService } from '../lib/api'

const AssetDetails = ({ asset, onAssetUpdate }) => {
  const { id } = useParams()
  const navigate = useNavigate()
  const [telemetryData, setTelemetryData] = useState([])
  const [loading, setLoading] = useState(false)
  const [timeRange, setTimeRange] = useState('24h')
  const [selectedMetric, setSelectedMetric] = useState('temperature')

  useEffect(() => {
    if (asset || id) {
      loadTelemetryData()
    }
  }, [asset, id, timeRange])

  const loadTelemetryData = async () => {
    setLoading(true)
    try {
      // In a real app, this would fetch from the API
      // For now, we'll generate mock data
      const mockData = generateMockTelemetry(
        asset?.asset_type || 'hvac', 
        timeRange === '24h' ? 24 : timeRange === '7d' ? 168 : 720
      )
      setTelemetryData(mockData)
    } catch (error) {
      console.error('Failed to load telemetry data:', error)
    } finally {
      setLoading(false)
    }
  }

  if (!asset && !id) {
    return (
      <div className="p-6">
        <div className="text-center py-12">
          <p className="text-muted-foreground">No asset selected</p>
          <Button onClick={() => navigate('/assets')} className="mt-4">
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back to Assets
          </Button>
        </div>
      </div>
    )
  }

  const currentAsset = asset || { id, name: 'Loading...', status: 'offline' }
  const healthScore = calculateHealthScore(telemetryData)
  const latestReading = telemetryData[0] || {}

  const getMetricData = (metric) => {
    return telemetryData.map(reading => ({
      timestamp: new Date(reading.timestamp).toLocaleTimeString('en-US', { 
        hour: '2-digit', 
        minute: '2-digit' 
      }),
      value: reading[metric] || 0,
      fullTimestamp: reading.timestamp
    })).reverse()
  }

  const getMetricInfo = (metric) => {
    const info = {
      temperature: { 
        label: 'Temperature', 
        unit: '°C', 
        icon: Thermometer, 
        color: '#ef4444',
        normal: [18, 25]
      },
      humidity: { 
        label: 'Humidity', 
        unit: '%', 
        icon: Droplets, 
        color: '#3b82f6',
        normal: [40, 60]
      },
      pressure: { 
        label: 'Pressure', 
        unit: 'kPa', 
        icon: Gauge, 
        color: '#8b5cf6',
        normal: [100, 105]
      },
      vibration: { 
        label: 'Vibration', 
        unit: 'mm/s', 
        icon: Activity, 
        color: '#f59e0b',
        normal: [0, 0.5]
      },
      power_consumption: { 
        label: 'Power', 
        unit: 'kW', 
        icon: Zap, 
        color: '#10b981',
        normal: [5, 15]
      }
    }
    return info[metric] || info.temperature
  }

  const metricInfo = getMetricInfo(selectedMetric)
  const metricData = getMetricData(selectedMetric)
  const currentValue = latestReading[selectedMetric] || 0
  const previousValue = telemetryData[1]?.[selectedMetric] || currentValue
  const trend = currentValue - previousValue

  const MetricCard = ({ metric, value, unit, icon: Icon, trend, status = 'normal' }) => (
    <Card className="cursor-pointer hover:shadow-md transition-shadow" onClick={() => setSelectedMetric(metric)}>
      <CardContent className="pt-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Icon className="h-5 w-5 text-muted-foreground" />
            <span className="text-sm font-medium">{getMetricInfo(metric).label}</span>
          </div>
          {trend !== 0 && (
            <div className={`flex items-center text-xs ${trend > 0 ? 'text-red-500' : 'text-green-500'}`}>
              {trend > 0 ? <TrendingUp className="h-3 w-3" /> : <TrendingDown className="h-3 w-3" />}
              {Math.abs(trend).toFixed(1)}
            </div>
          )}
        </div>
        <div className="mt-2">
          <div className="text-2xl font-bold">
            {formatNumber(value)} {unit}
          </div>
          <div className={`text-xs mt-1 ${
            status === 'warning' ? 'text-yellow-600' :
            status === 'error' ? 'text-red-600' :
            'text-muted-foreground'
          }`}>
            {status === 'normal' ? 'Normal range' : 
             status === 'warning' ? 'Outside normal range' :
             'Critical level'}
          </div>
        </div>
      </CardContent>
    </Card>
  )

  const getMetricStatus = (metric, value) => {
    const info = getMetricInfo(metric)
    if (!info.normal) return 'normal'
    
    const [min, max] = info.normal
    if (value < min * 0.8 || value > max * 1.2) return 'error'
    if (value < min || value > max) return 'warning'
    return 'normal'
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Button variant="outline" onClick={() => navigate('/assets')}>
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back
          </Button>
          <div>
            <h1 className="text-3xl font-bold tracking-tight">{currentAsset.name}</h1>
            <div className="flex items-center gap-2 mt-1">
              <Badge className={getStatusColor(currentAsset.status)}>
                {currentAsset.status}
              </Badge>
              <span className="text-muted-foreground">
                {currentAsset.asset_type?.toUpperCase()} • {currentAsset.location || 'No location'}
              </span>
            </div>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="outline">
            <Download className="h-4 w-4 mr-2" />
            Export Data
          </Button>
          <Button variant="outline">
            <Edit className="h-4 w-4 mr-2" />
            Edit Asset
          </Button>
        </div>
      </div>

      {/* Asset Info Cards */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium">Health Score</p>
                <p className="text-2xl font-bold">{formatNumber(healthScore, 0)}%</p>
              </div>
              <div className={`w-12 h-12 rounded-full flex items-center justify-center ${
                healthScore >= 80 ? 'bg-green-100 text-green-600' :
                healthScore >= 60 ? 'bg-yellow-100 text-yellow-600' :
                'bg-red-100 text-red-600'
              }`}>
                <Gauge className="h-6 w-6" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium">Uptime</p>
                <p className="text-2xl font-bold">99.2%</p>
              </div>
              <div className="w-12 h-12 rounded-full bg-green-100 text-green-600 flex items-center justify-center">
                <Activity className="h-6 w-6" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium">Last Maintenance</p>
                <p className="text-sm text-muted-foreground">15 days ago</p>
              </div>
              <div className="w-12 h-12 rounded-full bg-blue-100 text-blue-600 flex items-center justify-center">
                <AlertTriangle className="h-6 w-6" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium">Efficiency</p>
                <p className="text-2xl font-bold">87%</p>
              </div>
              <div className="w-12 h-12 rounded-full bg-purple-100 text-purple-600 flex items-center justify-center">
                <TrendingUp className="h-6 w-6" />
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Metrics Grid */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-5">
        <MetricCard
          metric="temperature"
          value={latestReading.temperature}
          unit="°C"
          icon={Thermometer}
          trend={latestReading.temperature - (telemetryData[1]?.temperature || latestReading.temperature)}
          status={getMetricStatus('temperature', latestReading.temperature)}
        />
        <MetricCard
          metric="humidity"
          value={latestReading.humidity}
          unit="%"
          icon={Droplets}
          trend={latestReading.humidity - (telemetryData[1]?.humidity || latestReading.humidity)}
          status={getMetricStatus('humidity', latestReading.humidity)}
        />
        <MetricCard
          metric="pressure"
          value={latestReading.pressure}
          unit="kPa"
          icon={Gauge}
          trend={latestReading.pressure - (telemetryData[1]?.pressure || latestReading.pressure)}
          status={getMetricStatus('pressure', latestReading.pressure)}
        />
        <MetricCard
          metric="vibration"
          value={latestReading.vibration}
          unit="mm/s"
          icon={Activity}
          trend={latestReading.vibration - (telemetryData[1]?.vibration || latestReading.vibration)}
          status={getMetricStatus('vibration', latestReading.vibration)}
        />
        <MetricCard
          metric="power_consumption"
          value={latestReading.power_consumption}
          unit="kW"
          icon={Zap}
          trend={latestReading.power_consumption - (telemetryData[1]?.power_consumption || latestReading.power_consumption)}
          status={getMetricStatus('power_consumption', latestReading.power_consumption)}
        />
      </div>

      {/* Charts */}
      <div className="grid gap-6 lg:grid-cols-3">
        {/* Main Chart */}
        <div className="lg:col-span-2">
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle className="flex items-center gap-2">
                    <metricInfo.icon className="h-5 w-5" />
                    {metricInfo.label} Trends
                  </CardTitle>
                  <CardDescription>
                    Real-time {metricInfo.label.toLowerCase()} monitoring over {timeRange}
                  </CardDescription>
                </div>
                <div className="flex items-center gap-2">
                  <select
                    value={timeRange}
                    onChange={(e) => setTimeRange(e.target.value)}
                    className="border rounded-md px-3 py-1 text-sm"
                  >
                    <option value="24h">Last 24 Hours</option>
                    <option value="7d">Last 7 Days</option>
                    <option value="30d">Last 30 Days</option>
                  </select>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={400}>
                <AreaChart data={metricData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis 
                    dataKey="timestamp" 
                    tick={{ fontSize: 12 }}
                    interval="preserveStartEnd"
                  />
                  <YAxis tick={{ fontSize: 12 }} />
                  <Tooltip 
                    labelFormatter={(value) => `Time: ${value}`}
                    formatter={(value) => [`${formatNumber(value)} ${metricInfo.unit}`, metricInfo.label]}
                  />
                  <Area
                    type="monotone"
                    dataKey="value"
                    stroke={metricInfo.color}
                    fill={metricInfo.color}
                    fillOpacity={0.1}
                    strokeWidth={2}
                  />
                </AreaChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </div>

        {/* Side Panel */}
        <div className="space-y-6">
          {/* Asset Information */}
          <Card>
            <CardHeader>
              <CardTitle>Asset Information</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                <div>
                  <span className="text-sm font-medium">Manufacturer:</span>
                  <p className="text-sm text-muted-foreground">
                    {currentAsset.manufacturer || 'N/A'}
                  </p>
                </div>
                <div>
                  <span className="text-sm font-medium">Model:</span>
                  <p className="text-sm text-muted-foreground">
                    {currentAsset.model || 'N/A'}
                  </p>
                </div>
                <div>
                  <span className="text-sm font-medium">Serial Number:</span>
                  <p className="text-sm text-muted-foreground">
                    {currentAsset.serial_number || 'N/A'}
                  </p>
                </div>
                <div>
                  <span className="text-sm font-medium">Installation Date:</span>
                  <p className="text-sm text-muted-foreground">
                    {formatDate(currentAsset.installation_date)}
                  </p>
                </div>
                <div>
                  <span className="text-sm font-medium">Last Seen:</span>
                  <p className="text-sm text-muted-foreground">
                    {formatDate(currentAsset.last_seen)}
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Recent Alerts */}
          <Card>
            <CardHeader>
              <CardTitle>Recent Alerts</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                <div className="flex items-start gap-3 p-3 border rounded-lg">
                  <AlertTriangle className="h-4 w-4 text-yellow-500 mt-0.5" />
                  <div>
                    <p className="text-sm font-medium">Temperature Warning</p>
                    <p className="text-xs text-muted-foreground">
                      Temperature exceeded normal range
                    </p>
                    <p className="text-xs text-muted-foreground">2 hours ago</p>
                  </div>
                </div>
                <div className="flex items-start gap-3 p-3 border rounded-lg">
                  <Activity className="h-4 w-4 text-blue-500 mt-0.5" />
                  <div>
                    <p className="text-sm font-medium">Maintenance Due</p>
                    <p className="text-xs text-muted-foreground">
                      Scheduled maintenance in 3 days
                    </p>
                    <p className="text-xs text-muted-foreground">1 day ago</p>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Quick Actions */}
          <Card>
            <CardHeader>
              <CardTitle>Quick Actions</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                <Button variant="outline" className="w-full justify-start">
                  <AlertTriangle className="h-4 w-4 mr-2" />
                  Schedule Maintenance
                </Button>
                <Button variant="outline" className="w-full justify-start">
                  <Download className="h-4 w-4 mr-2" />
                  Download Report
                </Button>
                <Button variant="outline" className="w-full justify-start">
                  <Edit className="h-4 w-4 mr-2" />
                  Update Configuration
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}

export default AssetDetails

