'use client';

import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/Button';

interface Violation {
  id: number;
  violation_number: number;
  description: string;
  status: string;
  created_at: string;
  due_date: string;
}

export default function ResidentPortalPage() {
  const [violations, setViolations] = useState<Violation[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadViolations();
  }, []);

  const loadViolations = async () => {
    try {
      setLoading(true);
      const response = await fetch('/api/resident-portal/my-violations', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
      });
      
      if (!response.ok) {
        throw new Error('Failed to load violations');
      }
      
      const data = await response.json();
      setViolations(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load violations');
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'open': return 'text-red-600 bg-red-100';
      case 'resolved': return 'text-green-600 bg-green-100';
      case 'disputed': return 'text-yellow-600 bg-yellow-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  if (loading) {
    return (
      <div className="container mx-auto p-6">
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="container mx-auto p-6">
        <div className="bg-red-50 border border-red-200 rounded-md p-4">
          <p className="text-red-800">{error}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto p-6">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Resident Portal</h1>
        <p className="text-gray-600">View and manage your violations</p>
      </div>

      <div className="bg-white shadow rounded-lg">
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-lg font-medium text-gray-900">My Violations</h2>
        </div>
        
        <div className="p-6">
          {violations.length === 0 ? (
            <div className="text-center py-8">
              <p className="text-gray-500">No violations found.</p>
            </div>
          ) : (
            <div className="space-y-4">
              {violations.map((violation) => (
                <div key={violation.id} className="border border-gray-200 rounded-lg p-4">
                  <div className="flex justify-between items-start">
                    <div className="flex-1">
                      <h3 className="font-medium text-gray-900">
                        Violation #{violation.violation_number}
                      </h3>
                      <p className="text-gray-600 mt-1">{violation.description}</p>
                      <div className="flex items-center space-x-4 mt-2 text-sm text-gray-500">
                        <span>Created: {new Date(violation.created_at).toLocaleDateString()}</span>
                        <span>Due: {new Date(violation.due_date).toLocaleDateString()}</span>
                      </div>
                    </div>
                    <div className="flex items-center space-x-2">
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(violation.status)}`}>
                        {violation.status}
                      </span>
                      <Button size="sm" variant="outline">
                        View Details
                      </Button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
} 