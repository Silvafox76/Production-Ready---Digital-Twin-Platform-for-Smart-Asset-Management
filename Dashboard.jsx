import React, { useState, useEffect } from 'react'
import { 
  Activity, 
  AlertTriangle, 
  CheckCircle, 
  TrendingUp, 
  Zap, 
  Thermometer,
  Droplets,
  Gauge,
  RefreshCw
} from 'lucide-react'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar, PieChart, Pie, Cell } from 'recharts'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card'
import { Button } from './ui/button'
import { Badge } from './ui/badge'
import { formatDate, formatNumber, getStatusColor, calculateHealthScore, generateMockTelemetry } from '../lib/utils'
import { wsService } from '../lib/api'

const Dashboard = ({ assets, onAssetSelect, onRefresh }) => {
  const [telemetryData, setTelemetryData] = useState({})
  const [systemStats, setSystemStats] = useState({
    totalAssets: 0,
    onlineAssets: 0,
    warningAssets: 0,
    errorAssets: 0,
    avgHealthScore: 0,
    totalPowerConsumption: 0
  })
  const [realtimeData, setRealtimeData] = useState([])
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    calculateSystemStats()
    loadTelemetryData()
    
    // Connect to WebSocket for real-time updates
    wsService.connect()
    wsService.on('telemetry', handleRealtimeUpdate)
    
    return () => {
      wsService.off('telemetry', handleRealtimeUpdate)
    }
  }, [assets])

  const calculateSystemStats = () => {
    const stats = {
      totalAssets: assets.length,
      onlineAssets: assets.filter(a => a.status === 'online').length,
      warningAssets: assets.filter(a => a.status === 'warning').length,
      errorAssets: assets.filter(a => a.status === 'error').length,
      avgHealthScore: 0,
      totalPowerConsumption: 0
    }

    // Calculate average health score (mock calculation)
    if (assets.length > 0) {
      const healthScores = assets.map(asset => {
        const mockData = generateMockTelemetry(asset.asset_type, 5)
        return calculateHealthScore(mockData)
      })
      stats.avgHealthScore = healthScores.reduce((sum, score) => sum + score, 0) / healthScores.length
    }

    // Mock total power consumption
    stats.totalPowerConsumption = assets.length * 12.5 + Math.random() * 50

    setSystemStats(stats)
  }

  const loadTelemetryData = async () => {
    setLoading(true)
    try {
      // Generate mock telemetry data for each asset
      const mockData = {}
      assets.forEach(asset => {
        mockData[asset.id] = generateMockTelemetry(asset.asset_type, 24)
      })
      setTelemetryData(mockData)
      
      // Generate mock real-time data for charts
      const realtimeChart = []
      for (let i = 23; i >= 0; i--) {
        const timestamp = new Date(Date.now() - i * 60 * 60 * 1000)
        realtimeChart.push({
          time: timestamp.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' }),
          temperature: 22 + Math.sin(i * 0.5) * 3 + (Math.random() - 0.5) * 2,
          power: 120 + Math.sin(i * 0.3) * 20 + (Math.random() - 0.5) * 10,
          efficiency: 85 + Math.sin(i * 0.4) * 10 + (Math.random() - 0.5) * 5
        })
      }
      setRealtimeData(realtimeChart)
    } catch (error) {
      console.error('Failed to load telemetry data:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleRealtimeUpdate = (data) => {
    // Update real-time charts with new data
    setRealtimeData(prev => {
      const newData = [...prev.slice(1), {
        time: new Date().toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' }),
        temperature: data.temperature || prev[prev.length - 1]?.temperature || 22,
        power: data.power_consumption * 10 || prev[prev.length - 1]?.power || 120,
        efficiency: 85 + (Math.random() - 0.5) * 10
      }]
      return newData
    })
  }

  const handleRefresh = async () => {
    await onRefresh()
    await loadTelemetryData()
  }

  const assetTypeDistribution = assets.reduce((acc, asset) => {
    acc[asset.asset_type] = (acc[asset.asset_type] || 0) + 1
    return acc
  }, {})

  const pieData = Object.entries(assetTypeDistribution).map(([type, count]) => ({
    name: type.toUpperCase(),
    value: count,
    color: getAssetTypeColor(type)
  }))

  function getAssetTypeColor(type) {
    const colors = {
      hvac: '#3b82f6',
      pump: '#10b981',
      motor: '#8b5cf6',
      sensor: '#f59e0b',
      valve: '#ec4899',
      compressor: '#6366f1',
      chiller: '#06b6d4',
      boiler: '#ef4444',
      fan: '#eab308',
      other: '#6b7280'
    }
    return colors[type] || colors.other
  }

  const StatCard = ({ title, value, subtitle, icon: Icon, trend, color = "blue" }) => (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-sm font-medium">{title}</CardTitle>
        <Icon className={`h-4 w-4 text-${color}-600`} />
      </CardHeader>
      <CardContent>
        <div className="text-2xl font-bold">{value}</div>
        {subtitle && (
          <p className="text-xs text-muted-foreground">{subtitle}</p>
        )}
        {trend && (
          <div className={`flex items-center text-xs ${trend > 0 ? 'text-green-600' : 'text-red-600'}`}>
            <TrendingUp className="h-3 w-3 mr-1" />
            {trend > 0 ? '+' : ''}{trend}% from last hour
          </div>
        )}
      </CardContent>
    </Card>
  )

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Dashboard</h1>
          <p className="text-muted-foreground">
            Real-time monitoring and analytics for your digital twin assets
          </p>
        </div>
        <Button onClick={handleRefresh} disabled={loading}>
          <RefreshCw className={`h-4 w-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
          Refresh
        </Button>
      </div>

      {/* Stats Grid */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <StatCard
          title="Total Assets"
          value={systemStats.totalAssets}
          subtitle="Monitored devices"
          icon={Activity}
          color="blue"
        />
        <StatCard
          title="Online Assets"
          value={systemStats.onlineAssets}
          subtitle={`${systemStats.warningAssets} warnings, ${systemStats.errorAssets} errors`}
          icon={CheckCircle}
          trend={2.5}
          color="green"
        />
        <StatCard
          title="Health Score"
          value={`${formatNumber(systemStats.avgHealthScore, 0)}%`}
          subtitle="Average system health"
          icon={Gauge}
          trend={-1.2}
          color="yellow"
        />
        <StatCard
          title="Power Usage"
          value={`${formatNumber(systemStats.totalPowerConsumption, 1)} kW`}
          subtitle="Total consumption"
          icon={Zap}
          trend={3.1}
          color="purple"
        />
      </div>

      {/* Charts Grid */}
      <div className="grid gap-6 md:grid-cols-2">
        {/* Real-time Temperature */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Thermometer className="h-5 w-5" />
              Temperature Trends
            </CardTitle>
            <CardDescription>
              Real-time temperature monitoring across all assets
            </CardDescription>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={realtimeData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="time" />
                <YAxis />
                <Tooltip />
                <Line 
                  type="monotone" 
                  dataKey="temperature" 
                  stroke="#3b82f6" 
                  strokeWidth={2}
                  dot={false}
                />
              </LineChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Power Consumption */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Zap className="h-5 w-5" />
              Power Consumption
            </CardTitle>
            <CardDescription>
              Energy usage patterns over time
            </CardDescription>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={realtimeData.slice(-12)}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="time" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="power" fill="#10b981" />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Asset Distribution */}
        <Card>
          <CardHeader>
            <CardTitle>Asset Distribution</CardTitle>
            <CardDescription>
              Breakdown of asset types in your system
            </CardDescription>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={pieData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {pieData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* System Efficiency */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <TrendingUp className="h-5 w-5" />
              System Efficiency
            </CardTitle>
            <CardDescription>
              Overall system performance metrics
            </CardDescription>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={realtimeData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="time" />
                <YAxis domain={[70, 100]} />
                <Tooltip />
                <Line 
                  type="monotone" 
                  dataKey="efficiency" 
                  stroke="#8b5cf6" 
                  strokeWidth={2}
                  dot={false}
                />
              </LineChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>

      {/* Recent Assets */}
      <Card>
        <CardHeader>
          <CardTitle>Recent Asset Activity</CardTitle>
          <CardDescription>
            Latest updates from your monitored assets
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {assets.slice(0, 5).map((asset) => {
              const mockData = generateMockTelemetry(asset.asset_type, 1)[0]
              const healthScore = calculateHealthScore([mockData])
              
              return (
                <div 
                  key={asset.id}
                  className="flex items-center justify-between p-4 border rounded-lg hover:bg-muted/50 cursor-pointer transition-colors"
                  onClick={() => onAssetSelect(asset)}
                >
                  <div className="flex items-center gap-4">
                    <div className={`w-3 h-3 rounded-full ${getAssetTypeColor(asset.asset_type)}`} />
                    <div>
                      <h4 className="font-medium">{asset.name}</h4>
                      <p className="text-sm text-muted-foreground">
                        {asset.location || 'No location'} • {asset.asset_type.toUpperCase()}
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center gap-4">
                    <div className="text-right">
                      <div className="text-sm font-medium">
                        {formatNumber(mockData.temperature)}°C
                      </div>
                      <div className="text-xs text-muted-foreground">
                        {formatNumber(mockData.power_consumption)} kW
                      </div>
                    </div>
                    <Badge className={getStatusColor(asset.status)}>
                      {asset.status}
                    </Badge>
                    <div className="text-right">
                      <div className="text-sm font-medium">
                        {formatNumber(healthScore)}%
                      </div>
                      <div className="text-xs text-muted-foreground">
                        Health
                      </div>
                    </div>
                  </div>
                </div>
              )
            })}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

export default Dashboard

