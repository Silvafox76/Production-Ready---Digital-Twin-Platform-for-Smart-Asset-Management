import React, { useState, useEffect } from 'react'
import { 
  TrendingUp, 
  TrendingDown, 
  BarChart3, 
  PieChart, 
  Activity,
  AlertTriangle,
  Zap,
  Clock,
  Target,
  Download
} from 'lucide-react'
import { 
  LineChart, 
  Line, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer, 
  BarChart, 
  Bar, 
  PieChart as RechartsPieChart, 
  Pie, 
  Cell,
  ScatterChart,
  Scatter,
  ComposedChart,
  Area,
  AreaChart
} from 'recharts'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card'
import { Button } from './ui/button'
import { Badge } from './ui/badge'
import { formatNumber, generateMockTelemetry } from '../lib/utils'

const Analytics = ({ assets, selectedAsset }) => {
  const [timeRange, setTimeRange] = useState('7d')
  const [analyticsData, setAnalyticsData] = useState({})
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    generateAnalyticsData()
  }, [assets, timeRange])

  const generateAnalyticsData = () => {
    setLoading(true)
    
    // Generate comprehensive analytics data
    const data = {
      performanceMetrics: generatePerformanceMetrics(),
      energyAnalysis: generateEnergyAnalysis(),
      predictiveInsights: generatePredictiveInsights(),
      assetComparison: generateAssetComparison(),
      maintenanceAnalytics: generateMaintenanceAnalytics(),
      efficiencyTrends: generateEfficiencyTrends()
    }
    
    setAnalyticsData(data)
    setLoading(false)
  }

  const generatePerformanceMetrics = () => {
    const days = timeRange === '24h' ? 1 : timeRange === '7d' ? 7 : 30
    const metrics = []
    
    for (let i = days - 1; i >= 0; i--) {
      const date = new Date()
      date.setDate(date.getDate() - i)
      
      metrics.push({
        date: date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
        efficiency: 85 + Math.sin(i * 0.5) * 10 + (Math.random() - 0.5) * 5,
        uptime: 95 + Math.random() * 5,
        performance: 80 + Math.sin(i * 0.3) * 15 + (Math.random() - 0.5) * 8,
        alerts: Math.floor(Math.random() * 5)
      })
    }
    
    return metrics
  }

  const generateEnergyAnalysis = () => {
    const hourlyData = []
    for (let hour = 0; hour < 24; hour++) {
      hourlyData.push({
        hour: `${hour}:00`,
        consumption: 100 + Math.sin(hour * 0.5) * 30 + (Math.random() - 0.5) * 20,
        cost: (100 + Math.sin(hour * 0.5) * 30) * 0.12,
        efficiency: 85 + Math.sin(hour * 0.3) * 10
      })
    }
    
    return {
      hourlyConsumption: hourlyData,
      totalConsumption: hourlyData.reduce((sum, item) => sum + item.consumption, 0),
      totalCost: hourlyData.reduce((sum, item) => sum + item.cost, 0),
      avgEfficiency: hourlyData.reduce((sum, item) => sum + item.efficiency, 0) / 24,
      peakHour: hourlyData.reduce((max, item) => item.consumption > max.consumption ? item : max, hourlyData[0])
    }
  }

  const generatePredictiveInsights = () => {
    return assets.map(asset => {
      const failureRisk = Math.random() * 100
      const maintenanceDue = Math.floor(Math.random() * 30) + 1
      const healthScore = 100 - failureRisk * 0.8
      
      return {
        id: asset.id,
        name: asset.name,
        type: asset.asset_type,
        failureRisk,
        maintenanceDue,
        healthScore,
        recommendation: failureRisk > 70 ? 'Immediate attention required' :
                       failureRisk > 40 ? 'Schedule maintenance soon' :
                       'Operating normally'
      }
    })
  }

  const generateAssetComparison = () => {
    return assets.map(asset => {
      const mockData = generateMockTelemetry(asset.asset_type, 24)
      const avgTemp = mockData.reduce((sum, reading) => sum + reading.temperature, 0) / mockData.length
      const avgPower = mockData.reduce((sum, reading) => sum + reading.power_consumption, 0) / mockData.length
      const efficiency = 85 + (Math.random() - 0.5) * 20
      
      return {
        name: asset.name,
        type: asset.asset_type,
        temperature: avgTemp,
        power: avgPower,
        efficiency,
        status: asset.status,
        uptime: 95 + Math.random() * 5
      }
    })
  }

  const generateMaintenanceAnalytics = () => {
    const maintenanceTypes = ['Preventive', 'Corrective', 'Emergency', 'Scheduled']
    const data = maintenanceTypes.map(type => ({
      type,
      count: Math.floor(Math.random() * 20) + 5,
      cost: Math.floor(Math.random() * 5000) + 1000,
      avgDuration: Math.floor(Math.random() * 8) + 2
    }))
    
    return {
      byType: data,
      totalMaintenance: data.reduce((sum, item) => sum + item.count, 0),
      totalCost: data.reduce((sum, item) => sum + item.cost, 0),
      avgDuration: data.reduce((sum, item) => sum + item.avgDuration, 0) / data.length
    }
  }

  const generateEfficiencyTrends = () => {
    const trends = []
    for (let i = 11; i >= 0; i--) {
      const date = new Date()
      date.setMonth(date.getMonth() - i)
      
      trends.push({
        month: date.toLocaleDateString('en-US', { month: 'short' }),
        efficiency: 85 + Math.sin(i * 0.5) * 10,
        energySavings: Math.floor(Math.random() * 1000) + 500,
        co2Reduction: Math.floor(Math.random() * 50) + 20
      })
    }
    
    return trends
  }

  const StatCard = ({ title, value, subtitle, icon: Icon, trend, color = "blue" }) => (
    <Card>
      <CardContent className="pt-6">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm font-medium text-muted-foreground">{title}</p>
            <p className="text-2xl font-bold">{value}</p>
            {subtitle && (
              <p className="text-xs text-muted-foreground mt-1">{subtitle}</p>
            )}
          </div>
          <div className={`w-12 h-12 rounded-full bg-${color}-100 text-${color}-600 flex items-center justify-center`}>
            <Icon className="h-6 w-6" />
          </div>
        </div>
        {trend !== undefined && (
          <div className={`flex items-center text-xs mt-2 ${trend >= 0 ? 'text-green-600' : 'text-red-600'}`}>
            {trend >= 0 ? <TrendingUp className="h-3 w-3 mr-1" /> : <TrendingDown className="h-3 w-3 mr-1" />}
            {Math.abs(trend).toFixed(1)}% from last period
          </div>
        )}
      </CardContent>
    </Card>
  )

  const COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#06b6d4']

  if (loading) {
    return (
      <div className="p-6">
        <div className="text-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
          <p className="text-muted-foreground">Loading analytics...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Analytics</h1>
          <p className="text-muted-foreground">
            Comprehensive insights and performance analytics for your digital twin assets
          </p>
        </div>
        <div className="flex items-center gap-2">
          <select
            value={timeRange}
            onChange={(e) => setTimeRange(e.target.value)}
            className="border rounded-md px-3 py-2"
          >
            <option value="24h">Last 24 Hours</option>
            <option value="7d">Last 7 Days</option>
            <option value="30d">Last 30 Days</option>
          </select>
          <Button>
            <Download className="h-4 w-4 mr-2" />
            Export Report
          </Button>
        </div>
      </div>

      {/* Key Metrics */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <StatCard
          title="System Efficiency"
          value={`${formatNumber(analyticsData.energyAnalysis?.avgEfficiency || 87, 1)}%`}
          subtitle="Average across all assets"
          icon={Target}
          trend={2.3}
          color="green"
        />
        <StatCard
          title="Energy Consumption"
          value={`${formatNumber(analyticsData.energyAnalysis?.totalConsumption || 2400, 0)} kWh`}
          subtitle={`$${formatNumber(analyticsData.energyAnalysis?.totalCost || 288, 0)} cost`}
          icon={Zap}
          trend={-1.2}
          color="blue"
        />
        <StatCard
          title="Active Alerts"
          value="12"
          subtitle="3 critical, 9 warnings"
          icon={AlertTriangle}
          trend={-15.5}
          color="yellow"
        />
        <StatCard
          title="Avg Uptime"
          value="99.2%"
          subtitle="Across all monitored assets"
          icon={Clock}
          trend={0.8}
          color="purple"
        />
      </div>

      {/* Charts Grid */}
      <div className="grid gap-6 lg:grid-cols-2">
        {/* Performance Trends */}
        <Card>
          <CardHeader>
            <CardTitle>Performance Trends</CardTitle>
            <CardDescription>
              System efficiency and uptime over time
            </CardDescription>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <ComposedChart data={analyticsData.performanceMetrics || []}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis />
                <Tooltip />
                <Area
                  type="monotone"
                  dataKey="efficiency"
                  fill="#3b82f6"
                  fillOpacity={0.1}
                  stroke="#3b82f6"
                  strokeWidth={2}
                />
                <Line
                  type="monotone"
                  dataKey="uptime"
                  stroke="#10b981"
                  strokeWidth={2}
                  dot={false}
                />
              </ComposedChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Energy Consumption */}
        <Card>
          <CardHeader>
            <CardTitle>Energy Consumption Pattern</CardTitle>
            <CardDescription>
              Hourly energy usage and efficiency
            </CardDescription>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={analyticsData.energyAnalysis?.hourlyConsumption || []}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="hour" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="consumption" fill="#3b82f6" />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Asset Comparison */}
        <Card>
          <CardHeader>
            <CardTitle>Asset Performance Comparison</CardTitle>
            <CardDescription>
              Efficiency vs power consumption by asset
            </CardDescription>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <ScatterChart data={analyticsData.assetComparison || []}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="power" name="Power (kW)" />
                <YAxis dataKey="efficiency" name="Efficiency %" />
                <Tooltip 
                  formatter={(value, name) => [
                    `${formatNumber(value)} ${name === 'power' ? 'kW' : '%'}`,
                    name === 'power' ? 'Power Consumption' : 'Efficiency'
                  ]}
                  labelFormatter={(label, payload) => payload?.[0]?.payload?.name || ''}
                />
                <Scatter dataKey="efficiency" fill="#3b82f6" />
              </ScatterChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Maintenance Analytics */}
        <Card>
          <CardHeader>
            <CardTitle>Maintenance Breakdown</CardTitle>
            <CardDescription>
              Distribution of maintenance activities
            </CardDescription>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <RechartsPieChart>
                <Pie
                  data={analyticsData.maintenanceAnalytics?.byType || []}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ type, percent }) => `${type} ${(percent * 100).toFixed(0)}%`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="count"
                >
                  {(analyticsData.maintenanceAnalytics?.byType || []).map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </RechartsPieChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>

      {/* Predictive Insights */}
      <Card>
        <CardHeader>
          <CardTitle>Predictive Insights</CardTitle>
          <CardDescription>
            AI-powered predictions and maintenance recommendations
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {(analyticsData.predictiveInsights || []).slice(0, 5).map((insight) => (
              <div key={insight.id} className="flex items-center justify-between p-4 border rounded-lg">
                <div className="flex items-center gap-4">
                  <div className={`w-3 h-3 rounded-full ${
                    insight.failureRisk > 70 ? 'bg-red-500' :
                    insight.failureRisk > 40 ? 'bg-yellow-500' :
                    'bg-green-500'
                  }`} />
                  <div>
                    <h4 className="font-medium">{insight.name}</h4>
                    <p className="text-sm text-muted-foreground">
                      {insight.type.toUpperCase()} • Health Score: {formatNumber(insight.healthScore, 0)}%
                    </p>
                  </div>
                </div>
                <div className="text-right">
                  <div className="text-sm font-medium">
                    {insight.failureRisk > 70 ? 'High Risk' :
                     insight.failureRisk > 40 ? 'Medium Risk' :
                     'Low Risk'}
                  </div>
                  <div className="text-xs text-muted-foreground">
                    Maintenance due in {insight.maintenanceDue} days
                  </div>
                </div>
                <Badge variant={
                  insight.failureRisk > 70 ? 'destructive' :
                  insight.failureRisk > 40 ? 'secondary' :
                  'default'
                }>
                  {insight.recommendation}
                </Badge>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Efficiency Trends */}
      <Card>
        <CardHeader>
          <CardTitle>Long-term Efficiency Trends</CardTitle>
          <CardDescription>
            Monthly efficiency improvements and environmental impact
          </CardDescription>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={300}>
            <ComposedChart data={analyticsData.efficiencyTrends || []}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="month" />
              <YAxis yAxisId="left" />
              <YAxis yAxisId="right" orientation="right" />
              <Tooltip />
              <Area
                yAxisId="left"
                type="monotone"
                dataKey="efficiency"
                fill="#3b82f6"
                fillOpacity={0.1}
                stroke="#3b82f6"
                strokeWidth={2}
              />
              <Bar yAxisId="right" dataKey="energySavings" fill="#10b981" />
            </ComposedChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>
    </div>
  )
}

export default Analytics

