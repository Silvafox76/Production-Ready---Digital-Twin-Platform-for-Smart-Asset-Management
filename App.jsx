import React, { useState, useEffect } from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import './App.css'

// Components
import Sidebar from './components/Sidebar'
import Dashboard from './components/Dashboard'
import AssetManagement from './components/AssetManagement'
import AssetDetails from './components/AssetDetails'
import Analytics from './components/Analytics'
import Visualization3D from './components/Visualization3D'
import Settings from './components/Settings'

// API Service
import { apiService } from './lib/api'

function App() {
  const [assets, setAssets] = useState([])
  const [selectedAsset, setSelectedAsset] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false)

  // Load initial data
  useEffect(() => {
    loadAssets()
  }, [])

  const loadAssets = async () => {
    try {
      setLoading(true)
      const response = await apiService.getAssets()
      setAssets(response.assets || [])
      setError(null)
    } catch (err) {
      console.error('Failed to load assets:', err)
      setError('Failed to load assets. Please check your connection.')
    } finally {
      setLoading(false)
    }
  }

  const handleAssetSelect = (asset) => {
    setSelectedAsset(asset)
  }

  const handleAssetUpdate = (updatedAsset) => {
    setAssets(prev => prev.map(asset => 
      asset.id === updatedAsset.id ? updatedAsset : asset
    ))
    if (selectedAsset && selectedAsset.id === updatedAsset.id) {
      setSelectedAsset(updatedAsset)
    }
  }

  const handleAssetCreate = (newAsset) => {
    setAssets(prev => [...prev, newAsset])
  }

  const handleAssetDelete = (assetId) => {
    setAssets(prev => prev.filter(asset => asset.id !== assetId))
    if (selectedAsset && selectedAsset.id === assetId) {
      setSelectedAsset(null)
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
          <p className="text-muted-foreground">Loading Digital Twin Platform...</p>
        </div>
      </div>
    )
  }

  return (
    <Router>
      <div className="min-h-screen bg-background flex">
        <Sidebar 
          collapsed={sidebarCollapsed}
          onToggle={() => setSidebarCollapsed(!sidebarCollapsed)}
          assets={assets}
          selectedAsset={selectedAsset}
          onAssetSelect={handleAssetSelect}
        />
        
        <main className={`flex-1 transition-all duration-300 ${
          sidebarCollapsed ? 'ml-16' : 'ml-64'
        }`}>
          <div className="h-full">
            <Routes>
              <Route 
                path="/" 
                element={
                  <Dashboard 
                    assets={assets}
                    onAssetSelect={handleAssetSelect}
                    onRefresh={loadAssets}
                  />
                } 
              />
              <Route 
                path="/assets" 
                element={
                  <AssetManagement 
                    assets={assets}
                    onAssetSelect={handleAssetSelect}
                    onAssetUpdate={handleAssetUpdate}
                    onAssetCreate={handleAssetCreate}
                    onAssetDelete={handleAssetDelete}
                    onRefresh={loadAssets}
                  />
                } 
              />
              <Route 
                path="/assets/:id" 
                element={
                  <AssetDetails 
                    asset={selectedAsset}
                    onAssetUpdate={handleAssetUpdate}
                  />
                } 
              />
              <Route 
                path="/analytics" 
                element={
                  <Analytics 
                    assets={assets}
                    selectedAsset={selectedAsset}
                  />
                } 
              />
              <Route 
                path="/visualization" 
                element={
                  <Visualization3D 
                    assets={assets}
                    selectedAsset={selectedAsset}
                    onAssetSelect={handleAssetSelect}
                  />
                } 
              />
              <Route 
                path="/settings" 
                element={<Settings />} 
              />
              <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
          </div>
        </main>

        {error && (
          <div className="fixed bottom-4 right-4 bg-destructive text-destructive-foreground p-4 rounded-lg shadow-lg max-w-sm">
            <div className="flex items-center gap-2">
              <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
              </svg>
              <span className="text-sm">{error}</span>
              <button 
                onClick={() => setError(null)}
                className="ml-2 text-destructive-foreground/70 hover:text-destructive-foreground"
              >
                ×
              </button>
            </div>
          </div>
        )}
      </div>
    </Router>
  )
}

export default App

