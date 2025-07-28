'use client';

import { useEffect, useState } from 'react';
import { useRouter, useParams } from 'next/navigation';
import { useAuthStore } from '@/lib/auth';
import { apiClient } from '@/lib/api';
import Sidebar from '@/components/layout/Sidebar';
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
  const { user, isAuthenticated } = useAuthStore();
  const router = useRouter();
  const params = useParams();
  const violationId = parseInt(params.id as string);
  
  const [violation, setViolation] = useState<Violation | null>(null);
  const [loading, setLoading] = useState(true);
  const [editing, setEditing] = useState(false);
  const [saving, setSaving] = useState(false);
  const [editedViolation, setEditedViolation] = useState<Partial<Violation>>({});

  useEffect(() => {
    if (!isAuthenticated) {
      router.push('/');
      return;
    }

    loadViolation();
  }, [isAuthenticated, router, violationId]);

  const loadViolation = async () => {
    try {
      setLoading(true);
      // For now, we'll get the violation from the list
      // In a real app, you'd have a specific endpoint for getting a single violation
      const violations = await apiClient.getViolations({ skip: 0, limit: 1000 });
      const foundViolation = violations.data.find(v => v.id === violationId);
      
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

  const handleStatusUpdate = async (newStatus: string) => {
    if (!violation) return;
    
    try {
      setSaving(true);
      const updatedViolation = await apiClient.updateViolationStatus(violation.id, newStatus);
      setViolation(updatedViolation);
      setEditedViolation(prev => ({ ...prev, status: newStatus as any }));
    } catch (error) {
      console.error('Failed to update status:', error);
      alert('Failed to update status');
    } finally {
      setSaving(false);
    }
  };

  const getStatusBadge = (status: string) => {
    const statusConfig = {
      open: { color: 'bg-yellow-100 text-yellow-800', icon: AlertCircle },
      under_review: { color: 'bg-blue-100 text-blue-800', icon: Clock },
      resolved: { color: 'bg-green-100 text-green-800', icon: CheckCircle },
      disputed: { color: 'bg-red-100 text-red-800', icon: XCircle },
    };
    
    const config = statusConfig[status as keyof typeof statusConfig] || statusConfig.open;
    const Icon = config.icon;
    
    return (
      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${config.color}`}>
        <Icon className="h-3 w-3 mr-1" />
        {status.replace('_', ' ')}
      </span>
    );
  };

  if (!isAuthenticated || !user) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50">
        <Sidebar />
        <div className="lg:pl-64">
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
      <div className="min-h-screen bg-gray-50">
        <Sidebar />
        <div className="lg:pl-64">
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
    <div className="min-h-screen bg-gray-50">
      <Sidebar />
      
      <div className="lg:pl-64">
        {/* Header */}
        <div className="bg-white shadow">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
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
                  <Button
                    onClick={() => setEditing(true)}
                  >
                    <Edit className="h-4 w-4 mr-2" />
                    Edit
                  </Button>
                )}
              </div>
            </div>
          </div>
        </div>

        {/* Main content */}
        <div className="max-w-4xl mx-auto py-6 sm:px-6 lg:px-8">
          <div className="bg-white shadow rounded-lg">
            {/* Status Section */}
            <div className="px-6 py-4 border-b border-gray-200">
              <div className="flex items-center justify-between">
                <h2 className="text-lg font-medium text-gray-900">Status</h2>
                {editing ? (
                  <select
                    value={editedViolation.status || violation.status}
                                         onChange={(e) => setEditedViolation(prev => ({ ...prev, status: e.target.value as any }))}
                    className="border border-gray-300 rounded-md px-3 py-2 text-sm"
                  >
                    <option value="open">Open</option>
                    <option value="under_review">Under Review</option>
                    <option value="resolved">Resolved</option>
                    <option value="disputed">Disputed</option>
                  </select>
                ) : (
                  <div className="flex items-center space-x-4">
                    {getStatusBadge(violation.status)}
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => setEditing(true)}
                    >
                      <Edit className="h-3 w-3 mr-1" />
                      Change Status
                    </Button>
                  </div>
                )}
              </div>
            </div>

            {/* Details Section */}
            <div className="px-6 py-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Basic Information */}
                <div>
                  <h3 className="text-lg font-medium text-gray-900 mb-4">Basic Information</h3>
                  <div className="space-y-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700">Description</label>
                      {editing ? (
                        <textarea
                          value={editedViolation.description || violation.description}
                          onChange={(e) => setEditedViolation(prev => ({ ...prev, description: e.target.value }))}
                          className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 text-sm"
                          rows={4}
                        />
                      ) : (
                        <p className="mt-1 text-sm text-gray-900">{violation.description}</p>
                      )}
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700">Address</label>
                      {editing ? (
                        <input
                          type="text"
                          value={editedViolation.address || violation.address}
                          onChange={(e) => setEditedViolation(prev => ({ ...prev, address: e.target.value }))}
                          className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 text-sm"
                        />
                      ) : (
                        <div className="mt-1 flex items-center text-sm text-gray-900">
                          <MapPin className="h-4 w-4 mr-2 text-gray-400" />
                          {violation.address}
                        </div>
                      )}
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700">Offender</label>
                      {editing ? (
                        <input
                          type="text"
                          value={editedViolation.offender || violation.offender}
                          onChange={(e) => setEditedViolation(prev => ({ ...prev, offender: e.target.value }))}
                          className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 text-sm"
                        />
                      ) : (
                        <div className="mt-1 flex items-center text-sm text-gray-900">
                          <User className="h-4 w-4 mr-2 text-gray-400" />
                          {violation.offender}
                        </div>
                      )}
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700">Date</label>
                      <div className="mt-1 flex items-center text-sm text-gray-900">
                        <Calendar className="h-4 w-4 mr-2 text-gray-400" />
                        {new Date(violation.timestamp).toLocaleDateString()} at {new Date(violation.timestamp).toLocaleTimeString()}
                      </div>
                    </div>
                  </div>
                </div>

                {/* Additional Information */}
                <div>
                  <h3 className="text-lg font-medium text-gray-900 mb-4">Additional Information</h3>
                  <div className="space-y-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700">Tags</label>
                      {editing ? (
                        <input
                          type="text"
                          value={editedViolation.tags || violation.tags || ''}
                          onChange={(e) => setEditedViolation(prev => ({ ...prev, tags: e.target.value }))}
                          className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 text-sm"
                          placeholder="Enter tags separated by commas"
                        />
                      ) : (
                        <p className="mt-1 text-sm text-gray-900">{violation.tags || 'No tags'}</p>
                      )}
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700">Repeat Offender Score</label>
                      <p className="mt-1 text-sm text-gray-900">{violation.repeat_offender_score || 0}</p>
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700">HOA</label>
                      <p className="mt-1 text-sm text-gray-900">{violation.hoa_name || 'N/A'}</p>
                    </div>

                    {violation.gps_coordinates && (
                      <div>
                        <label className="block text-sm font-medium text-gray-700">GPS Coordinates</label>
                        <p className="mt-1 text-sm text-gray-900">{violation.gps_coordinates}</p>
                      </div>
                    )}
                  </div>
                </div>
              </div>

              {/* Summary Section */}
              {violation.summary && (
                <div className="mt-6 pt-6 border-t border-gray-200">
                  <h3 className="text-lg font-medium text-gray-900 mb-4">AI Summary</h3>
                  <div className="bg-gray-50 rounded-lg p-4">
                    <div className="flex items-start">
                      <FileText className="h-5 w-5 text-blue-500 mr-3 mt-0.5" />
                      <p className="text-sm text-gray-700">{violation.summary}</p>
                    </div>
                  </div>
                </div>
              )}

              {/* Image Section */}
              {violation.image_url && (
                <div className="mt-6 pt-6 border-t border-gray-200">
                  <h3 className="text-lg font-medium text-gray-900 mb-4">Evidence Photo</h3>
                  <div className="max-w-md">
                    <img
                      src={violation.image_url}
                      alt="Violation evidence"
                      className="rounded-lg shadow-sm"
                    />
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
} 