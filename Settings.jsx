import React, { useState } from 'react'
import { 
  Settings as SettingsIcon, 
  User, 
  Bell, 
  Shield, 
  Database, 
  Wifi,
  Save,
  RefreshCw,
  AlertTriangle,
  CheckCircle
} from 'lucide-react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card'
import { Button } from './ui/button'
import { Badge } from './ui/badge'

const Settings = () => {
  const [activeTab, setActiveTab] = useState('general')
  const [settings, setSettings] = useState({
    general: {
      systemName: 'Digital Twin Platform',
      timezone: 'UTC-5',
      language: 'en',
      theme: 'light',
      autoRefresh: true,
      refreshInterval: 30
    },
    notifications: {
      emailAlerts: true,
      smsAlerts: false,
      pushNotifications: true,
      alertThresholds: {
        temperature: { min: 15, max: 30 },
        humidity: { min: 30, max: 70 },
        pressure: { min: 95, max: 110 },
        vibration: { max: 1.0 },
        power: { max: 25 }
      }
    },
    security: {
      twoFactorAuth: false,
      sessionTimeout: 60,
      passwordExpiry: 90,
      auditLogging: true
    },
    database: {
      retentionPeriod: 365,
      backupFrequency: 'daily',
      compressionEnabled: true,
      archiveOldData: true
    },
    connectivity: {
      mqttBroker: 'localhost:1883',
      apiTimeout: 30,
      retryAttempts: 3,
      heartbeatInterval: 60
    }
  })
  const [saving, setSaving] = useState(false)
  const [saved, setSaved] = useState(false)

  const tabs = [
    { id: 'general', label: 'General', icon: SettingsIcon },
    { id: 'notifications', label: 'Notifications', icon: Bell },
    { id: 'security', label: 'Security', icon: Shield },
    { id: 'database', label: 'Database', icon: Database },
    { id: 'connectivity', label: 'Connectivity', icon: Wifi }
  ]

  const handleSave = async () => {
    setSaving(true)
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 1000))
    setSaving(false)
    setSaved(true)
    setTimeout(() => setSaved(false), 3000)
  }

  const updateSetting = (category, key, value) => {
    setSettings(prev => ({
      ...prev,
      [category]: {
        ...prev[category],
        [key]: value
      }
    }))
  }

  const updateNestedSetting = (category, parentKey, key, value) => {
    setSettings(prev => ({
      ...prev,
      [category]: {
        ...prev[category],
        [parentKey]: {
          ...prev[category][parentKey],
          [key]: value
        }
      }
    }))
  }

  const GeneralSettings = () => (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>System Configuration</CardTitle>
          <CardDescription>
            Basic system settings and preferences
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-2">System Name</label>
            <input
              type="text"
              value={settings.general.systemName}
              onChange={(e) => updateSetting('general', 'systemName', e.target.value)}
              className="w-full border rounded-md px-3 py-2"
            />
          </div>
          
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium mb-2">Timezone</label>
              <select
                value={settings.general.timezone}
                onChange={(e) => updateSetting('general', 'timezone', e.target.value)}
                className="w-full border rounded-md px-3 py-2"
              >
                <option value="UTC-8">Pacific Time (UTC-8)</option>
                <option value="UTC-5">Eastern Time (UTC-5)</option>
                <option value="UTC+0">UTC</option>
                <option value="UTC+1">Central European Time (UTC+1)</option>
              </select>
            </div>
            
            <div>
              <label className="block text-sm font-medium mb-2">Language</label>
              <select
                value={settings.general.language}
                onChange={(e) => updateSetting('general', 'language', e.target.value)}
                className="w-full border rounded-md px-3 py-2"
              >
                <option value="en">English</option>
                <option value="es">Spanish</option>
                <option value="fr">French</option>
                <option value="de">German</option>
              </select>
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">Theme</label>
            <select
              value={settings.general.theme}
              onChange={(e) => updateSetting('general', 'theme', e.target.value)}
              className="w-full border rounded-md px-3 py-2"
            >
              <option value="light">Light</option>
              <option value="dark">Dark</option>
              <option value="auto">Auto</option>
            </select>
          </div>

          <div className="flex items-center justify-between">
            <div>
              <label className="text-sm font-medium">Auto Refresh</label>
              <p className="text-xs text-muted-foreground">
                Automatically refresh dashboard data
              </p>
            </div>
            <input
              type="checkbox"
              checked={settings.general.autoRefresh}
              onChange={(e) => updateSetting('general', 'autoRefresh', e.target.checked)}
              className="rounded"
            />
          </div>

          {settings.general.autoRefresh && (
            <div>
              <label className="block text-sm font-medium mb-2">
                Refresh Interval (seconds)
              </label>
              <input
                type="number"
                min="10"
                max="300"
                value={settings.general.refreshInterval}
                onChange={(e) => updateSetting('general', 'refreshInterval', parseInt(e.target.value))}
                className="w-full border rounded-md px-3 py-2"
              />
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )

  const NotificationSettings = () => (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>Alert Preferences</CardTitle>
          <CardDescription>
            Configure how you receive notifications and alerts
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <label className="text-sm font-medium">Email Alerts</label>
              <p className="text-xs text-muted-foreground">
                Receive alerts via email
              </p>
            </div>
            <input
              type="checkbox"
              checked={settings.notifications.emailAlerts}
              onChange={(e) => updateSetting('notifications', 'emailAlerts', e.target.checked)}
              className="rounded"
            />
          </div>

          <div className="flex items-center justify-between">
            <div>
              <label className="text-sm font-medium">SMS Alerts</label>
              <p className="text-xs text-muted-foreground">
                Receive critical alerts via SMS
              </p>
            </div>
            <input
              type="checkbox"
              checked={settings.notifications.smsAlerts}
              onChange={(e) => updateSetting('notifications', 'smsAlerts', e.target.checked)}
              className="rounded"
            />
          </div>

          <div className="flex items-center justify-between">
            <div>
              <label className="text-sm font-medium">Push Notifications</label>
              <p className="text-xs text-muted-foreground">
                Browser push notifications
              </p>
            </div>
            <input
              type="checkbox"
              checked={settings.notifications.pushNotifications}
              onChange={(e) => updateSetting('notifications', 'pushNotifications', e.target.checked)}
              className="rounded"
            />
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Alert Thresholds</CardTitle>
          <CardDescription>
            Set thresholds for automatic alerts
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-2">Temperature (°C)</label>
            <div className="grid grid-cols-2 gap-2">
              <input
                type="number"
                placeholder="Min"
                value={settings.notifications.alertThresholds.temperature.min}
                onChange={(e) => updateNestedSetting('notifications', 'alertThresholds', 'temperature', {
                  ...settings.notifications.alertThresholds.temperature,
                  min: parseFloat(e.target.value)
                })}
                className="border rounded-md px-3 py-2"
              />
              <input
                type="number"
                placeholder="Max"
                value={settings.notifications.alertThresholds.temperature.max}
                onChange={(e) => updateNestedSetting('notifications', 'alertThresholds', 'temperature', {
                  ...settings.notifications.alertThresholds.temperature,
                  max: parseFloat(e.target.value)
                })}
                className="border rounded-md px-3 py-2"
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">Humidity (%)</label>
            <div className="grid grid-cols-2 gap-2">
              <input
                type="number"
                placeholder="Min"
                value={settings.notifications.alertThresholds.humidity.min}
                onChange={(e) => updateNestedSetting('notifications', 'alertThresholds', 'humidity', {
                  ...settings.notifications.alertThresholds.humidity,
                  min: parseFloat(e.target.value)
                })}
                className="border rounded-md px-3 py-2"
              />
              <input
                type="number"
                placeholder="Max"
                value={settings.notifications.alertThresholds.humidity.max}
                onChange={(e) => updateNestedSetting('notifications', 'alertThresholds', 'humidity', {
                  ...settings.notifications.alertThresholds.humidity,
                  max: parseFloat(e.target.value)
                })}
                className="border rounded-md px-3 py-2"
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">Vibration (mm/s)</label>
            <input
              type="number"
              placeholder="Max"
              value={settings.notifications.alertThresholds.vibration.max}
              onChange={(e) => updateNestedSetting('notifications', 'alertThresholds', 'vibration', {
                max: parseFloat(e.target.value)
              })}
              className="w-full border rounded-md px-3 py-2"
            />
          </div>
        </CardContent>
      </Card>
    </div>
  )

  const SecuritySettings = () => (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>Authentication & Access</CardTitle>
          <CardDescription>
            Security settings and access controls
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <label className="text-sm font-medium">Two-Factor Authentication</label>
              <p className="text-xs text-muted-foreground">
                Add an extra layer of security
              </p>
            </div>
            <input
              type="checkbox"
              checked={settings.security.twoFactorAuth}
              onChange={(e) => updateSetting('security', 'twoFactorAuth', e.target.checked)}
              className="rounded"
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">
              Session Timeout (minutes)
            </label>
            <input
              type="number"
              min="15"
              max="480"
              value={settings.security.sessionTimeout}
              onChange={(e) => updateSetting('security', 'sessionTimeout', parseInt(e.target.value))}
              className="w-full border rounded-md px-3 py-2"
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">
              Password Expiry (days)
            </label>
            <input
              type="number"
              min="30"
              max="365"
              value={settings.security.passwordExpiry}
              onChange={(e) => updateSetting('security', 'passwordExpiry', parseInt(e.target.value))}
              className="w-full border rounded-md px-3 py-2"
            />
          </div>

          <div className="flex items-center justify-between">
            <div>
              <label className="text-sm font-medium">Audit Logging</label>
              <p className="text-xs text-muted-foreground">
                Log all user actions for security
              </p>
            </div>
            <input
              type="checkbox"
              checked={settings.security.auditLogging}
              onChange={(e) => updateSetting('security', 'auditLogging', e.target.checked)}
              className="rounded"
            />
          </div>
        </CardContent>
      </Card>
    </div>
  )

  const DatabaseSettings = () => (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>Data Management</CardTitle>
          <CardDescription>
            Configure data retention and backup settings
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-2">
              Data Retention Period (days)
            </label>
            <input
              type="number"
              min="30"
              max="3650"
              value={settings.database.retentionPeriod}
              onChange={(e) => updateSetting('database', 'retentionPeriod', parseInt(e.target.value))}
              className="w-full border rounded-md px-3 py-2"
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">Backup Frequency</label>
            <select
              value={settings.database.backupFrequency}
              onChange={(e) => updateSetting('database', 'backupFrequency', e.target.value)}
              className="w-full border rounded-md px-3 py-2"
            >
              <option value="hourly">Hourly</option>
              <option value="daily">Daily</option>
              <option value="weekly">Weekly</option>
              <option value="monthly">Monthly</option>
            </select>
          </div>

          <div className="flex items-center justify-between">
            <div>
              <label className="text-sm font-medium">Data Compression</label>
              <p className="text-xs text-muted-foreground">
                Compress data to save storage space
              </p>
            </div>
            <input
              type="checkbox"
              checked={settings.database.compressionEnabled}
              onChange={(e) => updateSetting('database', 'compressionEnabled', e.target.checked)}
              className="rounded"
            />
          </div>

          <div className="flex items-center justify-between">
            <div>
              <label className="text-sm font-medium">Archive Old Data</label>
              <p className="text-xs text-muted-foreground">
                Move old data to archive storage
              </p>
            </div>
            <input
              type="checkbox"
              checked={settings.database.archiveOldData}
              onChange={(e) => updateSetting('database', 'archiveOldData', e.target.checked)}
              className="rounded"
            />
          </div>
        </CardContent>
      </Card>
    </div>
  )

  const ConnectivitySettings = () => (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>Connection Settings</CardTitle>
          <CardDescription>
            Configure external connections and timeouts
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-2">MQTT Broker</label>
            <input
              type="text"
              value={settings.connectivity.mqttBroker}
              onChange={(e) => updateSetting('connectivity', 'mqttBroker', e.target.value)}
              className="w-full border rounded-md px-3 py-2"
              placeholder="hostname:port"
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">
              API Timeout (seconds)
            </label>
            <input
              type="number"
              min="5"
              max="120"
              value={settings.connectivity.apiTimeout}
              onChange={(e) => updateSetting('connectivity', 'apiTimeout', parseInt(e.target.value))}
              className="w-full border rounded-md px-3 py-2"
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">
              Retry Attempts
            </label>
            <input
              type="number"
              min="1"
              max="10"
              value={settings.connectivity.retryAttempts}
              onChange={(e) => updateSetting('connectivity', 'retryAttempts', parseInt(e.target.value))}
              className="w-full border rounded-md px-3 py-2"
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">
              Heartbeat Interval (seconds)
            </label>
            <input
              type="number"
              min="30"
              max="300"
              value={settings.connectivity.heartbeatInterval}
              onChange={(e) => updateSetting('connectivity', 'heartbeatInterval', parseInt(e.target.value))}
              className="w-full border rounded-md px-3 py-2"
            />
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Connection Status</CardTitle>
          <CardDescription>
            Current status of external connections
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-sm">MQTT Broker</span>
              <Badge className="bg-green-100 text-green-800">
                <CheckCircle className="h-3 w-3 mr-1" />
                Connected
              </Badge>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm">Database</span>
              <Badge className="bg-green-100 text-green-800">
                <CheckCircle className="h-3 w-3 mr-1" />
                Connected
              </Badge>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm">Redis Cache</span>
              <Badge className="bg-yellow-100 text-yellow-800">
                <AlertTriangle className="h-3 w-3 mr-1" />
                Degraded
              </Badge>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )

  const renderTabContent = () => {
    switch (activeTab) {
      case 'general':
        return <GeneralSettings />
      case 'notifications':
        return <NotificationSettings />
      case 'security':
        return <SecuritySettings />
      case 'database':
        return <DatabaseSettings />
      case 'connectivity':
        return <ConnectivitySettings />
      default:
        return <GeneralSettings />
    }
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Settings</h1>
          <p className="text-muted-foreground">
            Configure your Digital Twin Platform preferences and system settings
          </p>
        </div>
        <div className="flex items-center gap-2">
          {saved && (
            <Badge className="bg-green-100 text-green-800">
              <CheckCircle className="h-3 w-3 mr-1" />
              Settings Saved
            </Badge>
          )}
          <Button onClick={handleSave} disabled={saving}>
            {saving ? (
              <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
            ) : (
              <Save className="h-4 w-4 mr-2" />
            )}
            {saving ? 'Saving...' : 'Save Changes'}
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Sidebar */}
        <div className="lg:col-span-1">
          <Card>
            <CardContent className="pt-6">
              <nav className="space-y-1">
                {tabs.map((tab) => (
                  <button
                    key={tab.id}
                    onClick={() => setActiveTab(tab.id)}
                    className={`w-full flex items-center gap-3 px-3 py-2 rounded-md text-sm transition-colors ${
                      activeTab === tab.id
                        ? 'bg-primary text-primary-foreground'
                        : 'text-muted-foreground hover:bg-muted hover:text-foreground'
                    }`}
                  >
                    <tab.icon className="h-4 w-4" />
                    {tab.label}
                  </button>
                ))}
              </nav>
            </CardContent>
          </Card>
        </div>

        {/* Content */}
        <div className="lg:col-span-3">
          {renderTabContent()}
        </div>
      </div>
    </div>
  )
}

export default Settings

