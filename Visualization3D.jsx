import React, { useRef, useState, useEffect, Suspense } from 'react'
import { Canvas, useFrame, useThree } from '@react-three/fiber'
import { OrbitControls, Text, Box, Sphere, Cylinder, Environment, Grid } from '@react-three/drei'
import * as THREE from 'three'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card'
import { Button } from './ui/button'
import { Badge } from './ui/badge'
import { 
  RotateCcw, 
  ZoomIn, 
  ZoomOut, 
  Home, 
  Settings,
  Eye,
  EyeOff,
  Layers
} from 'lucide-react'
import { getStatusColor, formatNumber } from '../lib/utils'

// Asset 3D Models
const AssetModel = ({ asset, position, onClick, isSelected }) => {
  const meshRef = useRef()
  const [hovered, setHovered] = useState(false)

  useFrame((state) => {
    if (meshRef.current) {
      // Gentle rotation animation
      meshRef.current.rotation.y += 0.005
      
      // Hover effect
      if (hovered) {
        meshRef.current.scale.setScalar(1.1)
      } else {
        meshRef.current.scale.setScalar(isSelected ? 1.05 : 1)
      }
    }
  })

  const getAssetGeometry = (type) => {
    switch (type) {
      case 'hvac':
        return <Box args={[2, 1.5, 1]} />
      case 'pump':
        return <Cylinder args={[0.5, 0.8, 1.5, 8]} />
      case 'motor':
        return <Cylinder args={[0.6, 0.6, 1, 16]} />
      case 'compressor':
        return <Box args={[1.5, 2, 1.2]} />
      case 'chiller':
        return <Box args={[3, 2, 1.5]} />
      case 'fan':
        return <Cylinder args={[1, 1, 0.3, 16]} />
      default:
        return <Box args={[1, 1, 1]} />
    }
  }

  const getAssetColor = (status) => {
    switch (status) {
      case 'online':
        return '#10b981' // green
      case 'warning':
        return '#f59e0b' // yellow
      case 'error':
        return '#ef4444' // red
      case 'maintenance':
        return '#3b82f6' // blue
      default:
        return '#6b7280' // gray
    }
  }

  return (
    <group
      ref={meshRef}
      position={position}
      onClick={onClick}
      onPointerOver={() => setHovered(true)}
      onPointerOut={() => setHovered(false)}
    >
      <mesh>
        {getAssetGeometry(asset.asset_type)}
        <meshStandardMaterial 
          color={getAssetColor(asset.status)}
          metalness={0.3}
          roughness={0.4}
          emissive={isSelected ? getAssetColor(asset.status) : '#000000'}
          emissiveIntensity={isSelected ? 0.2 : 0}
        />
      </mesh>
      
      {/* Asset label */}
      <Text
        position={[0, 2, 0]}
        fontSize={0.3}
        color="white"
        anchorX="center"
        anchorY="middle"
        outlineWidth={0.02}
        outlineColor="black"
      >
        {asset.name}
      </Text>
      
      {/* Status indicator */}
      <Sphere args={[0.1]} position={[1.2, 1.2, 0]}>
        <meshBasicMaterial color={getAssetColor(asset.status)} />
      </Sphere>
    </group>
  )
}

// Building/Floor Layout
const BuildingLayout = ({ assets, onAssetClick, selectedAsset }) => {
  // Group assets by building and floor
  const assetsByLocation = assets.reduce((acc, asset) => {
    const building = asset.building || 'Unknown Building'
    const floor = asset.floor || 'Ground Floor'
    const key = `${building}-${floor}`
    
    if (!acc[key]) {
      acc[key] = {
        building,
        floor,
        assets: []
      }
    }
    acc[key].assets.push(asset)
    return acc
  }, {})

  // Position assets in a grid layout
  const getAssetPosition = (assetIndex, totalAssets, floorIndex) => {
    const gridSize = Math.ceil(Math.sqrt(totalAssets))
    const x = (assetIndex % gridSize - gridSize / 2) * 4
    const z = (Math.floor(assetIndex / gridSize) - gridSize / 2) * 4
    const y = floorIndex * 5 // Stack floors vertically
    
    return [x, y, z]
  }

  return (
    <>
      {Object.values(assetsByLocation).map((location, floorIndex) => (
        <group key={`${location.building}-${location.floor}`}>
          {/* Floor plane */}
          <mesh position={[0, floorIndex * 5 - 0.5, 0]} receiveShadow>
            <planeGeometry args={[20, 20]} />
            <meshStandardMaterial 
              color="#f3f4f6" 
              transparent 
              opacity={0.3}
            />
          </mesh>
          
          {/* Floor label */}
          <Text
            position={[0, floorIndex * 5 + 3, -8]}
            fontSize={0.5}
            color="white"
            anchorX="center"
            anchorY="middle"
            outlineWidth={0.02}
            outlineColor="black"
          >
            {location.building} - {location.floor}
          </Text>
          
          {/* Assets on this floor */}
          {location.assets.map((asset, assetIndex) => (
            <AssetModel
              key={asset.id}
              asset={asset}
              position={getAssetPosition(assetIndex, location.assets.length, floorIndex)}
              onClick={() => onAssetClick(asset)}
              isSelected={selectedAsset?.id === asset.id}
            />
          ))}
        </group>
      ))}
    </>
  )
}

// Camera Controls
const CameraController = ({ target }) => {
  const { camera } = useThree()
  
  useEffect(() => {
    if (target) {
      // Animate camera to focus on selected asset
      camera.position.set(target[0] + 5, target[1] + 3, target[2] + 5)
      camera.lookAt(target[0], target[1], target[2])
    }
  }, [target, camera])
  
  return null
}

const Visualization3D = ({ assets, selectedAsset, onAssetSelect }) => {
  const [viewMode, setViewMode] = useState('building') // 'building', 'network', 'heatmap'
  const [showGrid, setShowGrid] = useState(true)
  const [showLabels, setShowLabels] = useState(true)
  const [cameraTarget, setCameraTarget] = useState(null)
  const controlsRef = useRef()

  const handleAssetClick = (asset) => {
    onAssetSelect(asset)
    // Set camera target to the selected asset
    const assetPosition = getAssetPosition(asset)
    setCameraTarget(assetPosition)
  }

  const getAssetPosition = (asset) => {
    // This would normally come from asset location data
    // For now, we'll use a simple grid layout
    const index = assets.findIndex(a => a.id === asset.id)
    const gridSize = Math.ceil(Math.sqrt(assets.length))
    const x = (index % gridSize - gridSize / 2) * 4
    const z = (Math.floor(index / gridSize) - gridSize / 2) * 4
    return [x, 0, z]
  }

  const resetCamera = () => {
    setCameraTarget(null)
    if (controlsRef.current) {
      controlsRef.current.reset()
    }
  }

  const getStatusStats = () => {
    const stats = assets.reduce((acc, asset) => {
      acc[asset.status] = (acc[asset.status] || 0) + 1
      return acc
    }, {})
    return stats
  }

  const statusStats = getStatusStats()

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">3D Visualization</h1>
          <p className="text-muted-foreground">
            Interactive 3D view of your digital twin assets
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Button
            variant={viewMode === 'building' ? 'default' : 'outline'}
            size="sm"
            onClick={() => setViewMode('building')}
          >
            Building View
          </Button>
          <Button
            variant={viewMode === 'network' ? 'default' : 'outline'}
            size="sm"
            onClick={() => setViewMode('network')}
          >
            Network View
          </Button>
          <Button
            variant={viewMode === 'heatmap' ? 'default' : 'outline'}
            size="sm"
            onClick={() => setViewMode('heatmap')}
          >
            Heat Map
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* 3D Viewport */}
        <div className="lg:col-span-3">
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle>3D Asset View</CardTitle>
                <div className="flex items-center gap-2">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setShowGrid(!showGrid)}
                  >
                    <Layers className="h-4 w-4" />
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setShowLabels(!showLabels)}
                  >
                    {showLabels ? <Eye className="h-4 w-4" /> : <EyeOff className="h-4 w-4" />}
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={resetCamera}
                  >
                    <Home className="h-4 w-4" />
                  </Button>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <div className="h-[600px] bg-gray-900 rounded-lg overflow-hidden">
                <Canvas
                  camera={{ position: [10, 10, 10], fov: 60 }}
                  shadows
                >
                  <Suspense fallback={null}>
                    {/* Lighting */}
                    <ambientLight intensity={0.4} />
                    <directionalLight
                      position={[10, 10, 5]}
                      intensity={1}
                      castShadow
                      shadow-mapSize-width={2048}
                      shadow-mapSize-height={2048}
                    />
                    <pointLight position={[-10, -10, -10]} intensity={0.3} />
                    
                    {/* Environment */}
                    <Environment preset="warehouse" />
                    
                    {/* Grid */}
                    {showGrid && (
                      <Grid
                        args={[20, 20]}
                        cellSize={1}
                        cellThickness={0.5}
                        cellColor="#6b7280"
                        sectionSize={5}
                        sectionThickness={1}
                        sectionColor="#374151"
                        fadeDistance={25}
                        fadeStrength={1}
                        followCamera={false}
                        infiniteGrid={true}
                      />
                    )}
                    
                    {/* Assets */}
                    <BuildingLayout
                      assets={assets}
                      onAssetClick={handleAssetClick}
                      selectedAsset={selectedAsset}
                    />
                    
                    {/* Camera Controls */}
                    <OrbitControls
                      ref={controlsRef}
                      enablePan={true}
                      enableZoom={true}
                      enableRotate={true}
                      minDistance={5}
                      maxDistance={50}
                    />
                    
                    <CameraController target={cameraTarget} />
                  </Suspense>
                </Canvas>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Side Panel */}
        <div className="space-y-6">
          {/* Status Overview */}
          <Card>
            <CardHeader>
              <CardTitle>System Status</CardTitle>
              <CardDescription>
                Real-time asset status overview
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {Object.entries(statusStats).map(([status, count]) => (
                  <div key={status} className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <div className={`w-3 h-3 rounded-full ${
                        status === 'online' ? 'bg-green-500' :
                        status === 'warning' ? 'bg-yellow-500' :
                        status === 'error' ? 'bg-red-500' :
                        'bg-gray-500'
                      }`} />
                      <span className="text-sm capitalize">{status}</span>
                    </div>
                    <Badge variant="secondary">{count}</Badge>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Selected Asset Details */}
          {selectedAsset && (
            <Card>
              <CardHeader>
                <CardTitle>Asset Details</CardTitle>
                <CardDescription>
                  {selectedAsset.name}
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  <div>
                    <span className="text-sm font-medium">Type:</span>
                    <p className="text-sm text-muted-foreground">
                      {selectedAsset.asset_type.toUpperCase()}
                    </p>
                  </div>
                  <div>
                    <span className="text-sm font-medium">Location:</span>
                    <p className="text-sm text-muted-foreground">
                      {selectedAsset.location || 'No location'}
                    </p>
                  </div>
                  <div>
                    <span className="text-sm font-medium">Status:</span>
                    <div className="mt-1">
                      <Badge className={getStatusColor(selectedAsset.status)}>
                        {selectedAsset.status}
                      </Badge>
                    </div>
                  </div>
                  <div>
                    <span className="text-sm font-medium">Manufacturer:</span>
                    <p className="text-sm text-muted-foreground">
                      {selectedAsset.manufacturer || 'N/A'}
                    </p>
                  </div>
                  <div>
                    <span className="text-sm font-medium">Model:</span>
                    <p className="text-sm text-muted-foreground">
                      {selectedAsset.model || 'N/A'}
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>
          )}

          {/* View Controls */}
          <Card>
            <CardHeader>
              <CardTitle>View Controls</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-sm">Show Grid</span>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setShowGrid(!showGrid)}
                  >
                    {showGrid ? 'Hide' : 'Show'}
                  </Button>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm">Show Labels</span>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setShowLabels(!showLabels)}
                  >
                    {showLabels ? 'Hide' : 'Show'}
                  </Button>
                </div>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={resetCamera}
                  className="w-full"
                >
                  <Home className="h-4 w-4 mr-2" />
                  Reset View
                </Button>
              </div>
            </CardContent>
          </Card>

          {/* Legend */}
          <Card>
            <CardHeader>
              <CardTitle>Legend</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 bg-green-500 rounded-full" />
                  <span className="text-sm">Online</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 bg-yellow-500 rounded-full" />
                  <span className="text-sm">Warning</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 bg-red-500 rounded-full" />
                  <span className="text-sm">Error</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 bg-blue-500 rounded-full" />
                  <span className="text-sm">Maintenance</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 bg-gray-500 rounded-full" />
                  <span className="text-sm">Offline</span>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}

export default Visualization3D

