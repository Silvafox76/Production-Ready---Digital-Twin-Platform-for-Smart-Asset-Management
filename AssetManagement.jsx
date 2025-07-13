import React, { useState } from 'react'
import { Plus, Search, Filter, MoreHorizontal, Edit, Trash2, Eye } from 'lucide-react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card'
import { Button } from './ui/button'
import { Badge } from './ui/badge'
import { formatDate, getStatusColor, getAssetTypeIcon } from '../lib/utils'

const AssetManagement = ({ 
  assets, 
  onAssetSelect, 
  onAssetUpdate, 
  onAssetCreate, 
  onAssetDelete, 
  onRefresh 
}) => {
  const [searchTerm, setSearchTerm] = useState('')
  const [filterStatus, setFilterStatus] = useState('all')
  const [filterType, setFilterType] = useState('all')
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [selectedAsset, setSelectedAsset] = useState(null)
  const [showEditModal, setShowEditModal] = useState(false)

  // Filter assets based on search and filters
  const filteredAssets = assets.filter(asset => {
    const matchesSearch = asset.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         asset.location?.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         asset.description?.toLowerCase().includes(searchTerm.toLowerCase())
    
    const matchesStatus = filterStatus === 'all' || asset.status === filterStatus
    const matchesType = filterType === 'all' || asset.asset_type === filterType
    
    return matchesSearch && matchesStatus && matchesType
  })

  const assetTypes = [...new Set(assets.map(asset => asset.asset_type))]
  const statusTypes = ['online', 'offline', 'warning', 'error', 'maintenance']

  const handleCreateAsset = async (assetData) => {
    try {
      // Mock asset creation - in real app, this would call the API
      const newAsset = {
        id: `asset_${Date.now()}`,
        ...assetData,
        status: 'offline',
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
        last_seen: null
      }
      onAssetCreate(newAsset)
      setShowCreateModal(false)
    } catch (error) {
      console.error('Failed to create asset:', error)
    }
  }

  const handleEditAsset = async (assetData) => {
    try {
      const updatedAsset = {
        ...selectedAsset,
        ...assetData,
        updated_at: new Date().toISOString()
      }
      onAssetUpdate(updatedAsset)
      setShowEditModal(false)
      setSelectedAsset(null)
    } catch (error) {
      console.error('Failed to update asset:', error)
    }
  }

  const handleDeleteAsset = async (assetId) => {
    if (window.confirm('Are you sure you want to delete this asset?')) {
      try {
        onAssetDelete(assetId)
      } catch (error) {
        console.error('Failed to delete asset:', error)
      }
    }
  }

  const AssetCard = ({ asset }) => (
    <Card className="hover:shadow-md transition-shadow">
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between">
          <div className="flex items-center gap-3">
            <div className="text-2xl">{getAssetTypeIcon(asset.asset_type)}</div>
            <div>
              <CardTitle className="text-lg">{asset.name}</CardTitle>
              <CardDescription>
                {asset.asset_type.toUpperCase()} • {asset.location || 'No location'}
              </CardDescription>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <Badge className={getStatusColor(asset.status)}>
              {asset.status}
            </Badge>
            <div className="relative">
              <Button variant="ghost" size="sm">
                <MoreHorizontal className="h-4 w-4" />
              </Button>
              <div className="absolute right-0 top-8 bg-white border rounded-md shadow-lg py-1 z-10 hidden group-hover:block">
                <button
                  onClick={() => onAssetSelect(asset)}
                  className="flex items-center gap-2 px-3 py-2 text-sm hover:bg-gray-50 w-full text-left"
                >
                  <Eye className="h-4 w-4" />
                  View Details
                </button>
                <button
                  onClick={() => {
                    setSelectedAsset(asset)
                    setShowEditModal(true)
                  }}
                  className="flex items-center gap-2 px-3 py-2 text-sm hover:bg-gray-50 w-full text-left"
                >
                  <Edit className="h-4 w-4" />
                  Edit
                </button>
                <button
                  onClick={() => handleDeleteAsset(asset.id)}
                  className="flex items-center gap-2 px-3 py-2 text-sm hover:bg-gray-50 w-full text-left text-red-600"
                >
                  <Trash2 className="h-4 w-4" />
                  Delete
                </button>
              </div>
            </div>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <div className="space-y-2">
          {asset.description && (
            <p className="text-sm text-muted-foreground">{asset.description}</p>
          )}
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div>
              <span className="font-medium">Manufacturer:</span>
              <br />
              <span className="text-muted-foreground">
                {asset.manufacturer || 'N/A'}
              </span>
            </div>
            <div>
              <span className="font-medium">Model:</span>
              <br />
              <span className="text-muted-foreground">
                {asset.model || 'N/A'}
              </span>
            </div>
            <div>
              <span className="font-medium">Installed:</span>
              <br />
              <span className="text-muted-foreground">
                {formatDate(asset.installation_date)}
              </span>
            </div>
            <div>
              <span className="font-medium">Last Seen:</span>
              <br />
              <span className="text-muted-foreground">
                {formatDate(asset.last_seen)}
              </span>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  )

  const AssetForm = ({ asset, onSubmit, onCancel }) => {
    const [formData, setFormData] = useState({
      name: asset?.name || '',
      description: asset?.description || '',
      asset_type: asset?.asset_type || 'hvac',
      location: asset?.location || '',
      building: asset?.building || '',
      floor: asset?.floor || '',
      room: asset?.room || '',
      manufacturer: asset?.manufacturer || '',
      model: asset?.model || '',
      serial_number: asset?.serial_number || '',
      installation_date: asset?.installation_date ? asset.installation_date.split('T')[0] : '',
      warranty_expiry: asset?.warranty_expiry ? asset.warranty_expiry.split('T')[0] : ''
    })

    const handleSubmit = (e) => {
      e.preventDefault()
      onSubmit(formData)
    }

    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div className="bg-white rounded-lg p-6 w-full max-w-2xl max-h-[90vh] overflow-y-auto">
          <h2 className="text-xl font-semibold mb-4">
            {asset ? 'Edit Asset' : 'Create New Asset'}
          </h2>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium mb-1">Name *</label>
                <input
                  type="text"
                  required
                  value={formData.name}
                  onChange={(e) => setFormData({...formData, name: e.target.value})}
                  className="w-full border rounded-md px-3 py-2"
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">Asset Type *</label>
                <select
                  required
                  value={formData.asset_type}
                  onChange={(e) => setFormData({...formData, asset_type: e.target.value})}
                  className="w-full border rounded-md px-3 py-2"
                >
                  <option value="hvac">HVAC</option>
                  <option value="pump">Pump</option>
                  <option value="motor">Motor</option>
                  <option value="sensor">Sensor</option>
                  <option value="valve">Valve</option>
                  <option value="compressor">Compressor</option>
                  <option value="chiller">Chiller</option>
                  <option value="boiler">Boiler</option>
                  <option value="fan">Fan</option>
                  <option value="other">Other</option>
                </select>
              </div>
            </div>
            
            <div>
              <label className="block text-sm font-medium mb-1">Description</label>
              <textarea
                value={formData.description}
                onChange={(e) => setFormData({...formData, description: e.target.value})}
                className="w-full border rounded-md px-3 py-2"
                rows={3}
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium mb-1">Location</label>
                <input
                  type="text"
                  value={formData.location}
                  onChange={(e) => setFormData({...formData, location: e.target.value})}
                  className="w-full border rounded-md px-3 py-2"
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">Building</label>
                <input
                  type="text"
                  value={formData.building}
                  onChange={(e) => setFormData({...formData, building: e.target.value})}
                  className="w-full border rounded-md px-3 py-2"
                />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium mb-1">Floor</label>
                <input
                  type="text"
                  value={formData.floor}
                  onChange={(e) => setFormData({...formData, floor: e.target.value})}
                  className="w-full border rounded-md px-3 py-2"
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">Room</label>
                <input
                  type="text"
                  value={formData.room}
                  onChange={(e) => setFormData({...formData, room: e.target.value})}
                  className="w-full border rounded-md px-3 py-2"
                />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium mb-1">Manufacturer</label>
                <input
                  type="text"
                  value={formData.manufacturer}
                  onChange={(e) => setFormData({...formData, manufacturer: e.target.value})}
                  className="w-full border rounded-md px-3 py-2"
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">Model</label>
                <input
                  type="text"
                  value={formData.model}
                  onChange={(e) => setFormData({...formData, model: e.target.value})}
                  className="w-full border rounded-md px-3 py-2"
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium mb-1">Serial Number</label>
              <input
                type="text"
                value={formData.serial_number}
                onChange={(e) => setFormData({...formData, serial_number: e.target.value})}
                className="w-full border rounded-md px-3 py-2"
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium mb-1">Installation Date</label>
                <input
                  type="date"
                  value={formData.installation_date}
                  onChange={(e) => setFormData({...formData, installation_date: e.target.value})}
                  className="w-full border rounded-md px-3 py-2"
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">Warranty Expiry</label>
                <input
                  type="date"
                  value={formData.warranty_expiry}
                  onChange={(e) => setFormData({...formData, warranty_expiry: e.target.value})}
                  className="w-full border rounded-md px-3 py-2"
                />
              </div>
            </div>

            <div className="flex justify-end gap-2 pt-4">
              <Button type="button" variant="outline" onClick={onCancel}>
                Cancel
              </Button>
              <Button type="submit">
                {asset ? 'Update Asset' : 'Create Asset'}
              </Button>
            </div>
          </form>
        </div>
      </div>
    )
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Asset Management</h1>
          <p className="text-muted-foreground">
            Manage and monitor all your digital twin assets
          </p>
        </div>
        <Button onClick={() => setShowCreateModal(true)}>
          <Plus className="h-4 w-4 mr-2" />
          Add Asset
        </Button>
      </div>

      {/* Filters */}
      <Card>
        <CardContent className="pt-6">
          <div className="flex flex-wrap gap-4">
            <div className="flex-1 min-w-64">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground h-4 w-4" />
                <input
                  type="text"
                  placeholder="Search assets..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="w-full pl-10 pr-4 py-2 border rounded-md"
                />
              </div>
            </div>
            <div>
              <select
                value={filterStatus}
                onChange={(e) => setFilterStatus(e.target.value)}
                className="border rounded-md px-3 py-2"
              >
                <option value="all">All Status</option>
                {statusTypes.map(status => (
                  <option key={status} value={status}>
                    {status.charAt(0).toUpperCase() + status.slice(1)}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <select
                value={filterType}
                onChange={(e) => setFilterType(e.target.value)}
                className="border rounded-md px-3 py-2"
              >
                <option value="all">All Types</option>
                {assetTypes.map(type => (
                  <option key={type} value={type}>
                    {type.toUpperCase()}
                  </option>
                ))}
              </select>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Assets Grid */}
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        {filteredAssets.map(asset => (
          <AssetCard key={asset.id} asset={asset} />
        ))}
      </div>

      {filteredAssets.length === 0 && (
        <Card>
          <CardContent className="pt-6">
            <div className="text-center py-12">
              <div className="text-muted-foreground mb-4">
                {searchTerm || filterStatus !== 'all' || filterType !== 'all' 
                  ? 'No assets match your current filters'
                  : 'No assets found'
                }
              </div>
              {!searchTerm && filterStatus === 'all' && filterType === 'all' && (
                <Button onClick={() => setShowCreateModal(true)}>
                  <Plus className="h-4 w-4 mr-2" />
                  Create Your First Asset
                </Button>
              )}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Create Asset Modal */}
      {showCreateModal && (
        <AssetForm
          onSubmit={handleCreateAsset}
          onCancel={() => setShowCreateModal(false)}
        />
      )}

      {/* Edit Asset Modal */}
      {showEditModal && selectedAsset && (
        <AssetForm
          asset={selectedAsset}
          onSubmit={handleEditAsset}
          onCancel={() => {
            setShowEditModal(false)
            setSelectedAsset(null)
          }}
        />
      )}
    </div>
  )
}

export default AssetManagement

