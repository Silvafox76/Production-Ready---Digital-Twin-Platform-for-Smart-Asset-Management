import React from 'react'
import { Link, useLocation } from 'react-router-dom'
import { 
  LayoutDashboard,
  Home, 
  Settings, 
  BarChart3, 
  Box, 
  Package,
  ChevronLeft,
  ChevronRight,
  Activity,
  AlertTriangle,
  Zap,
  CheckCircle,
  XCircle
} from 'lucide-react'
import { cn } from '../lib/utils'

const Sidebar = ({ collapsed, onToggle, assets, selectedAsset, onAssetSelect }) => {
  const location = useLocation()

  const navigation = [
    { name: 'Dashboard', href: '/', icon: LayoutDashboard },
    { name: 'Assets', href: '/assets', icon: Box },
    { name: 'Analytics', href: '/analytics', icon: BarChart3 },
    { name: '3D Visualization', href: '/visualization', icon: Package },
    { name: 'Settings', href: '/settings', icon: Settings },
  ]

  const getStatusIcon = (status) => {
    switch (status) {
      case 'online':
        return <CheckCircle className="w-3 h-3 text-green-500" />
      case 'warning':
        return <AlertTriangle className="w-3 h-3 text-yellow-500" />
      case 'error':
        return <XCircle className="w-3 h-3 text-red-500" />
      default:
        return <Activity className="w-3 h-3 text-gray-400" />
    }
  }

  const getAssetTypeColor = (type) => {
    const colors = {
      hvac: 'bg-blue-500',
      pump: 'bg-green-500',
      motor: 'bg-purple-500',
      sensor: 'bg-orange-500',
      valve: 'bg-pink-500',
      compressor: 'bg-indigo-500',
      chiller: 'bg-cyan-500',
      boiler: 'bg-red-500',
      fan: 'bg-yellow-500',
      other: 'bg-gray-500'
    }
    return colors[type] || colors.other
  }

  return (
    <div className={cn(
      "fixed left-0 top-0 h-full bg-sidebar border-r border-sidebar-border transition-all duration-300 z-50",
      collapsed ? "w-16" : "w-64"
    )}>
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-sidebar-border">
        {!collapsed && (
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 bg-primary rounded-lg flex items-center justify-center">
              <Package className="w-5 h-5 text-primary-foreground" />
            </div>
            <div>
              <h1 className="text-sm font-semibold text-sidebar-foreground">Digital Twin</h1>
              <p className="text-xs text-sidebar-foreground/60">Platform</p>
            </div>
          </div>
        )}
        <button
          onClick={onToggle}
          className="p-1.5 rounded-md hover:bg-sidebar-accent transition-colors"
        >
          {collapsed ? (
            <ChevronRight className="w-4 h-4 text-sidebar-foreground" />
          ) : (
            <ChevronLeft className="w-4 h-4 text-sidebar-foreground" />
          )}
        </button>
      </div>

      {/* Navigation */}
      <nav className="p-2">
        <div className="space-y-1">
          {navigation.map((item) => {
            const isActive = location.pathname === item.href
            return (
              <Link
                key={item.name}
                to={item.href}
                className={cn(
                  "flex items-center gap-3 px-3 py-2 rounded-md text-sm transition-colors",
                  isActive
                    ? "bg-sidebar-accent text-sidebar-accent-foreground"
                    : "text-sidebar-foreground hover:bg-sidebar-accent hover:text-sidebar-accent-foreground"
                )}
                title={collapsed ? item.name : undefined}
              >
                <item.icon className="w-4 h-4 flex-shrink-0" />
                {!collapsed && <span>{item.name}</span>}
              </Link>
            )
          })}
        </div>
      </nav>

      {/* Assets List */}
      {!collapsed && assets.length > 0 && (
        <div className="p-2 border-t border-sidebar-border mt-4">
          <h3 className="text-xs font-medium text-sidebar-foreground/60 uppercase tracking-wider mb-2 px-3">
            Assets ({assets.length})
          </h3>
          <div className="space-y-1 max-h-64 overflow-y-auto">
            {assets.slice(0, 10).map((asset) => (
              <button
                key={asset.id}
                onClick={() => onAssetSelect(asset)}
                className={cn(
                  "w-full flex items-center gap-2 px-3 py-2 rounded-md text-sm transition-colors text-left",
                  selectedAsset?.id === asset.id
                    ? "bg-sidebar-primary text-sidebar-primary-foreground"
                    : "text-sidebar-foreground hover:bg-sidebar-accent"
                )}
              >
                <div className={cn("w-2 h-2 rounded-full flex-shrink-0", getAssetTypeColor(asset.asset_type))} />
                <div className="flex-1 min-w-0">
                  <div className="truncate font-medium">{asset.name}</div>
                  <div className="text-xs text-sidebar-foreground/60 truncate">
                    {asset.location || 'No location'}
                  </div>
                </div>
                <div className="flex-shrink-0">
                  {getStatusIcon(asset.status)}
                </div>
              </button>
            ))}
            {assets.length > 10 && (
              <Link
                to="/assets"
                className="block px-3 py-2 text-xs text-sidebar-foreground/60 hover:text-sidebar-foreground transition-colors"
              >
                View all {assets.length} assets →
              </Link>
            )}
          </div>
        </div>
      )}

      {/* Collapsed Assets Indicator */}
      {collapsed && assets.length > 0 && (
        <div className="p-2 border-t border-sidebar-border mt-4">
          <div className="flex justify-center">
            <div className="w-8 h-8 bg-sidebar-accent rounded-md flex items-center justify-center">
              <span className="text-xs font-medium text-sidebar-accent-foreground">
                {assets.length}
              </span>
            </div>
          </div>
        </div>
      )}

      {/* Status Indicator */}
      <div className="absolute bottom-4 left-0 right-0 px-4">
        {!collapsed ? (
          <div className="flex items-center gap-2 text-xs text-sidebar-foreground/60">
            <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
            <span>System Online</span>
          </div>
        ) : (
          <div className="flex justify-center">
            <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
          </div>
        )}
      </div>
    </div>
  )
}

export default Sidebar

