'use client';

import { useState, useEffect } from 'react';
import { useAuthStore } from '@/lib/auth';
import { apiClient } from '@/lib/api';
import { Button } from '@/components/ui/Button';
import { LoadingSkeleton } from '@/components/ui/LoadingSkeleton';
import { 
  Plus, 
  Edit, 
  Trash2, 
  Users, 
  Building,
  MapPin,
  Phone,
  Mail
} from 'lucide-react';

interface HOA {
  id: number;
  name: string;
  address: string;
  contact_email: string;
  contact_phone: string;
  total_homes: number;
  active_violations: number;
  created_at: string;
  status: 'active' | 'inactive';
}

export default function HOAManagementPage() {
  const { user } = useAuthStore();
  const [hoas, setHoas] = useState<HOA[]>([]);
  const [loading, setLoading] = useState(true);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [editingHOA, setEditingHOA] = useState<HOA | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (user?.role === 'super_admin') {
      loadHOAs();
    }
  }, [user]);

  const loadHOAs = async () => {
    try {
      setLoading(true);
      const hoasData = await apiClient.getHOAs();
      setHoas(hoasData);
    } catch (error) {
      console.error('Failed to load HOAs:', error);
      setError('Failed to load HOAs');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateHOA = async (data: any) => {
    try {
      await apiClient.createHOA(data);
      setShowCreateForm(false);
      loadHOAs();
    } catch (error) {
      console.error('Failed to create HOA:', error);
      setError('Failed to create HOA');
    }
  };

  const handleEditHOA = async (data: any) => {
    try {
      await apiClient.updateHOA(editingHOA!.id, data);
      setEditingHOA(null);
      loadHOAs();
    } catch (error) {
      console.error('Failed to update HOA:', error);
      setError('Failed to update HOA');
    }
  };

  const handleDeleteHOA = async (hoaId: number) => {
    if (confirm('Are you sure you want to delete this HOA? This action cannot be undone.')) {
      try {
        await apiClient.deleteHOA(hoaId);
        loadHOAs();
      } catch (error) {
        console.error('Failed to delete HOA:', error);
        setError('Failed to delete HOA');
      }
    }
  };

  // Check if user has super admin permissions
  if (user?.role !== 'super_admin') {
    return (
      <div className="flex-1 overflow-auto p-6">
        <div className="max-w-7xl mx-auto">
          <div className="flex items-center justify-center h-64">
            <div className="text-center">
              <h2 className="text-xl font-semibold text-gray-900 mb-2">Access Denied</h2>
              <p className="text-gray-700 font-medium">You don't have permission to access HOA management.</p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="flex-1 overflow-auto p-6">
        <div className="max-w-7xl mx-auto">
          <LoadingSkeleton lines={5} />
        </div>
      </div>
    );
  }

  return (
    <>
      {/* Header */}
      <div className="bg-white shadow flex-shrink-0">
        <div className="w-full px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <h1 className="text-xl font-semibold text-gray-900">
                HOA Management
              </h1>
            </div>
            <div className="flex items-center">
              <Button
                onClick={() => setShowCreateForm(true)}
                className="ml-4"
              >
                <Plus className="h-4 w-4 mr-2" />
                Add HOA
              </Button>
            </div>
          </div>
        </div>
      </div>

      {/* Main content */}
      <div className="flex-1 overflow-auto p-6">
        <div className="max-w-7xl mx-auto">
          {error && (
            <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-md">
              <p className="text-red-700 font-medium">{error}</p>
            </div>
          )}

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {hoas.map((hoa) => (
              <div key={hoa.id} className="bg-white rounded-lg shadow-md p-6">
                <div className="flex items-start justify-between mb-4">
                  <div className="flex items-center">
                    <Building className="h-8 w-8 text-blue-600 mr-3" />
                    <div>
                      <h3 className="text-lg font-semibold text-gray-900">{hoa.name}</h3>
                      <p className="text-sm text-gray-600">{hoa.address}</p>
                    </div>
                  </div>
                  <div className="flex space-x-2">
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => setEditingHOA(hoa)}
                    >
                      <Edit className="h-4 w-4" />
                    </Button>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => handleDeleteHOA(hoa.id)}
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                </div>

                <div className="space-y-3">
                  <div className="flex items-center text-sm text-gray-600">
                    <Users className="h-4 w-4 mr-2" />
                    {hoa.total_homes} homes
                  </div>
                  <div className="flex items-center text-sm text-gray-600">
                    <MapPin className="h-4 w-4 mr-2" />
                    {hoa.active_violations} active violations
                  </div>
                  <div className="flex items-center text-sm text-gray-600">
                    <Mail className="h-4 w-4 mr-2" />
                    {hoa.contact_email}
                  </div>
                  <div className="flex items-center text-sm text-gray-600">
                    <Phone className="h-4 w-4 mr-2" />
                    {hoa.contact_phone}
                  </div>
                </div>

                <div className="mt-4 pt-4 border-t border-gray-200">
                  <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                    hoa.status === 'active' 
                      ? 'bg-green-100 text-green-800' 
                      : 'bg-gray-100 text-gray-800'
                  }`}>
                    {hoa.status}
                  </span>
                </div>
              </div>
            ))}
          </div>

          {hoas.length === 0 && (
            <div className="text-center py-12">
              <Building className="h-12 w-12 text-gray-300 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">No HOAs found</h3>
              <p className="text-gray-600 mb-4">Get started by creating your first HOA.</p>
              <Button onClick={() => setShowCreateForm(true)}>
                <Plus className="h-4 w-4 mr-2" />
                Add HOA
              </Button>
            </div>
          )}
        </div>
      </div>
    </>
  );
} 