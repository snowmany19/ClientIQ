'use client';

import { useEffect, useState } from 'react';
import { useRouter, useParams } from 'next/navigation';
import { useAuthStore } from '@/lib/auth';
import { apiClient } from '@/lib/api';
import { Button } from '@/components/ui/Button';
import { Violation } from '@/types';
import { 
  ArrowLeft, 
  Edit, 
  Save, 
  X,
  MapPin,
  Calendar,
  User,
  FileText,
  AlertCircle,
  CheckCircle,
  XCircle,
  Clock
} from 'lucide-react';

export default function ViolationDetailPage() {
  const { user } = useAuthStore();
  const router = useRouter();
  const params = useParams();
  const violationId = parseInt(params.id as string);
  
  const [violation, setViolation] = useState<Violation | null>(null);
  const [loading, setLoading] = useState(true);
  const [editing, setEditing] = useState(false);
  const [saving, setSaving] = useState(false);
  const [editedViolation, setEditedViolation] = useState<Partial<Violation>>({});

  useEffect(() => {
    loadViolation();
  }, [violationId]);

  const loadViolation = async () => {
    try {
      setLoading(true);
      const foundViolation = await apiClient.getViolation(violationId);
      
      if (foundViolation) {
        setViolation(foundViolation);
        setEditedViolation(foundViolation);
      } else {
        alert('Violation not found');
        router.push('/dashboard/violations');
      }
    } catch (error) {
      console.error('Failed to load violation:', error);
      alert('Failed to load violation');
      router.push('/dashboard/violations');
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    if (!violation) return;
    
    try {
      setSaving(true);
      const updatedViolation = await apiClient.updateViolation(violation.id, editedViolation);
      setViolation(updatedViolation);
      setEditing(false);
    } catch (error) {
      console.error('Failed to update violation:', error);
      alert('Failed to update violation');
    } finally {
      setSaving(false);
    }
  };

  const getStatusBadge = (status: string) => {
    const statusConfig = {
      open: { color: 'bg-yellow-100 text-yellow-800 border border-yellow-300', icon: AlertCircle },
      under_review: { color: 'bg-blue-100 text-blue-800 border border-blue-300', icon: Clock },
      resolved: { color: 'bg-green-100 text-green-800 border border-green-300', icon: CheckCircle },
      disputed: { color: 'bg-red-100 text-red-800 border border-red-300', icon: XCircle },
    };
    
    const config = statusConfig[status as keyof typeof statusConfig] || statusConfig.open;
    const Icon = config.icon;
    
    return (
      <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${config.color}`}>
        <Icon className="h-4 w-4 mr-2 text-current" />
        {status.replace('_', ' ')}
      </span>
    );
  };

  const canEdit = user?.role === 'admin' || user?.role === 'hoa_board';

  if (loading) {
    return (
      <div className="flex-1 overflow-auto p-6">
        <div className="max-w-4xl mx-auto">
          <div className="flex items-center justify-center h-64">
            <div className="text-center">
              <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600 mx-auto"></div>
              <p className="mt-4 text-gray-600">Loading violation...</p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (!violation) {
    return (
      <div className="flex-1 overflow-auto p-6">
        <div className="max-w-4xl mx-auto">
          <div className="flex items-center justify-center h-64">
            <div className="text-center">
              <p className="text-gray-600">Violation not found</p>
              <Button onClick={() => router.push('/dashboard/violations')} className="mt-4">
                Back to Violations
              </Button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <>
      {/* Header */}
      <div className="bg-white shadow flex-shrink-0">
        <div className="w-full px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <Button
                variant="ghost"
                onClick={() => router.push('/dashboard/violations')}
                className="mr-4"
              >
                <ArrowLeft className="h-4 w-4 mr-2" />
                Back
              </Button>
              <div>
                <h1 className="text-xl font-semibold text-gray-900">
                  Violation #{violation.violation_number}
                </h1>
                <p className="text-sm text-gray-500">
                  {new Date(violation.timestamp).toLocaleDateString()}
                </p>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              {editing ? (
                <>
                  <Button
                    variant="outline"
                    onClick={() => {
                      setEditing(false);
                      setEditedViolation(violation);
                    }}
                    disabled={saving}
                  >
                    <X className="h-4 w-4 mr-2" />
                    Cancel
                  </Button>
                  <Button
                    onClick={handleSave}
                    disabled={saving}
                  >
                    <Save className="h-4 w-4 mr-2" />
                    {saving ? 'Saving...' : 'Save'}
                  </Button>
                </>
              ) : (
                canEdit ? (
                  <Button
                    onClick={() => setEditing(true)}
                  >
                    <Edit className="h-4 w-4 mr-2" />
                    Edit
                  </Button>
                ) : (
                  <div className="text-sm text-gray-500">
                    Only admins and HOA board members can edit violations
                  </div>
                )
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Main content */}
      <div className="flex-1 overflow-auto">
        <div className="max-w-4xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
          {/* Status Section */}
          <div className="bg-white rounded-lg shadow p-6 mb-6">
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-medium text-gray-900">Status</h2>
              {editing ? (
                <select
                  value={editedViolation.status || violation.status}
                  onChange={(e) => setEditedViolation(prev => ({ ...prev, status: e.target.value as any }))}
                  className="border-2 border-gray-300 rounded-md px-4 py-2 text-base focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white"
                >
                  <option value="open">Open</option>
                  <option value="under_review">Under Review</option>
                  <option value="resolved">Resolved</option>
                  <option value="disputed">Disputed</option>
                </select>
              ) : (
                <div className="flex items-center space-x-4">
                  {getStatusBadge(violation.status)}
                  {canEdit && (
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => setEditing(true)}
                    >
                      <Edit className="h-3 w-3 mr-1" />
                      Change Status
                    </Button>
                  )}
                </div>
              )}
            </div>
          </div>

          {/* Details Section */}
          <div className="bg-white rounded-lg shadow p-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
              {/* Basic Information */}
              <div>
                <h3 className="text-lg font-medium text-gray-900 mb-6">Basic Information</h3>
                <div className="space-y-6">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Description</label>
                    {editing ? (
                      <textarea
                        value={editedViolation.description || violation.description}
                        onChange={(e) => setEditedViolation(prev => ({ ...prev, description: e.target.value }))}
                        className="block w-full border-2 border-gray-300 rounded-lg px-4 py-3 text-base focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white shadow-sm"
                        rows={4}
                        placeholder="Enter violation description..."
                      />
                    ) : (
                      <p className="text-base text-gray-900 bg-gray-50 rounded-lg p-4">{violation.description}</p>
                    )}
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Address</label>
                    {editing ? (
                      <input
                        type="text"
                        value={editedViolation.address || violation.address}
                        onChange={(e) => setEditedViolation(prev => ({ ...prev, address: e.target.value }))}
                        className="block w-full border-2 border-gray-300 rounded-lg px-4 py-3 text-base focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white shadow-sm"
                        placeholder="Enter address..."
                      />
                    ) : (
                      <div className="flex items-center text-base text-gray-900 bg-gray-50 rounded-lg p-4">
                        <MapPin className="h-5 w-5 mr-3 text-gray-500" />
                        {violation.address}
                      </div>
                    )}
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Offender</label>
                    {editing ? (
                      <input
                        type="text"
                        value={editedViolation.offender || violation.offender}
                        onChange={(e) => setEditedViolation(prev => ({ ...prev, offender: e.target.value }))}
                        className="block w-full border-2 border-gray-300 rounded-lg px-4 py-3 text-base focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white shadow-sm"
                        placeholder="Enter offender name..."
                      />
                    ) : (
                      <div className="flex items-center text-base text-gray-900 bg-gray-50 rounded-lg p-4">
                        <User className="h-5 w-5 mr-3 text-gray-500" />
                        {violation.offender}
                      </div>
                    )}
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Date</label>
                    <div className="flex items-center text-base text-gray-900 bg-gray-50 rounded-lg p-4">
                      <Calendar className="h-5 w-5 mr-3 text-gray-500" />
                      {new Date(violation.timestamp).toLocaleDateString()} at {new Date(violation.timestamp).toLocaleTimeString()}
                    </div>
                  </div>
                </div>
              </div>

              {/* Additional Information */}
              <div>
                <h3 className="text-lg font-medium text-gray-900 mb-6">Additional Information</h3>
                <div className="space-y-6">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Tags</label>
                    {editing ? (
                      <input
                        type="text"
                        value={editedViolation.tags || violation.tags || ''}
                        onChange={(e) => setEditedViolation(prev => ({ ...prev, tags: e.target.value }))}
                        className="block w-full border-2 border-gray-300 rounded-lg px-4 py-3 text-base focus:ring-2 focus:ring-blue-500 focus:border-blue-500 bg-white shadow-sm"
                        placeholder="Enter tags separated by commas"
                      />
                    ) : (
                      <p className="text-base text-gray-900 bg-gray-50 rounded-lg p-4">{violation.tags || 'No tags'}</p>
                    )}
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Repeat Offender Score</label>
                    <p className="text-base text-gray-900 bg-gray-50 rounded-lg p-4">{violation.repeat_offender_score || 0}</p>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">HOA</label>
                    <p className="text-base text-gray-900 bg-gray-50 rounded-lg p-4">{violation.hoa_name || 'N/A'}</p>
                  </div>

                  {violation.gps_coordinates && (
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">GPS Coordinates</label>
                      <p className="text-base text-gray-900 bg-gray-50 rounded-lg p-4">{violation.gps_coordinates}</p>
                    </div>
                  )}
                </div>
              </div>
            </div>

            {/* Summary Section */}
            {violation.summary && (
              <div className="mt-8 pt-8 border-t border-gray-200">
                <h3 className="text-lg font-medium text-gray-900 mb-4">AI Summary</h3>
                <div className="bg-blue-50 rounded-lg p-6 border border-blue-200">
                  <div className="flex items-start">
                    <FileText className="h-6 w-6 text-blue-600 mr-4 mt-1" />
                    <p className="text-base text-gray-800 leading-relaxed">{violation.summary}</p>
                  </div>
                </div>
              </div>
            )}

            {/* Image Section */}
            {violation.image_url && (
              <div className="mt-8 pt-8 border-t border-gray-200">
                <h3 className="text-lg font-medium text-gray-900 mb-4">Evidence Photo</h3>
                <div className="max-w-2xl">
                  <img
                    src={violation.image_url}
                    alt="Violation evidence"
                    className="rounded-lg shadow-lg border border-gray-200"
                  />
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </>
  );
}