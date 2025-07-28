'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuthStore } from '@/lib/auth';
import { apiClient } from '@/lib/api';
import Sidebar from '@/components/layout/Sidebar';
import ViolationsTable from '@/components/dashboard/ViolationsTable';
import { Button } from '@/components/ui/Button';
import { Violation } from '@/types';
import { Plus, Download } from 'lucide-react';

export default function ViolationsPage() {
  const { user, isAuthenticated, getCurrentUser } = useAuthStore();
  const router = useRouter();
  const [violations, setViolations] = useState<Violation[]>([]);
  const [loading, setLoading] = useState(true);
  const [currentPage, setCurrentPage] = useState(0);
  const [totalPages, setTotalPages] = useState(0);
  const [totalViolations, setTotalViolations] = useState(0);

  useEffect(() => {
    if (!isAuthenticated) {
      router.push('/');
      return;
    }

    if (!user) {
      getCurrentUser();
    }

    loadViolations();
  }, [isAuthenticated, user, router, getCurrentUser, currentPage]);

  const loadViolations = async () => {
    try {
      setLoading(true);
      const response = await apiClient.getViolations({
        skip: currentPage * 50,
        limit: 50
      });
      
      setViolations(response.data);
      setTotalPages(response.pagination.pages);
      setTotalViolations(response.pagination.total);
    } catch (error) {
      console.error('Failed to load violations:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleViolationUpdate = (updatedViolation: Violation) => {
    setViolations(prev => 
      prev.map(v => v.id === updatedViolation.id ? updatedViolation : v)
    );
  };

  const handleViolationDelete = (violationId: number) => {
    setViolations(prev => prev.filter(v => v.id !== violationId));
    setTotalViolations(prev => prev - 1);
  };

  const handleViolationView = (violation: Violation) => {
    // Navigate to the violation detail page
    router.push(`/dashboard/violations/${violation.id}`);
  };

  const handleViolationEdit = (violation: Violation) => {
    // Navigate to the violation detail page in edit mode
    router.push(`/dashboard/violations/${violation.id}`);
  };

  const handleExportCSV = async () => {
    try {
      const blob = await apiClient.exportViolationsCSV();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `violations_${new Date().toISOString().split('T')[0]}.csv`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (error) {
      console.error('Failed to export violations:', error);
    }
  };

  if (!isAuthenticated || !user) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
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
                <h1 className="text-xl font-semibold text-gray-900">
                  Violations
                </h1>
                <span className="ml-4 text-sm text-gray-500">
                  {totalViolations} total violations
                </span>
              </div>
              <div className="flex items-center space-x-4">
                <Button
                  variant="outline"
                  onClick={handleExportCSV}
                >
                  <Download className="h-4 w-4 mr-2" />
                  Export CSV
                </Button>
                <Button
                  onClick={() => router.push('/dashboard/violations/new')}
                >
                  <Plus className="h-4 w-4 mr-2" />
                  New Violation
                </Button>
              </div>
            </div>
          </div>
        </div>

        {/* Main content */}
        <div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
          {loading ? (
            <div className="flex items-center justify-center h-64">
              <div className="text-center">
                <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600 mx-auto"></div>
                <p className="mt-4 text-gray-600">Loading violations...</p>
              </div>
            </div>
          ) : (
            <ViolationsTable
              violations={violations}
              onViolationUpdate={handleViolationUpdate}
              onViolationDelete={handleViolationDelete}
              onViolationView={handleViolationView}
              onViolationEdit={handleViolationEdit}
            />
          )}

          {/* Pagination */}
          {totalPages > 1 && (
            <div className="mt-6 flex items-center justify-between">
              <div className="text-sm text-gray-700">
                Showing page {currentPage + 1} of {totalPages}
              </div>
              <div className="flex items-center space-x-2">
                <Button
                  variant="outline"
                  onClick={() => setCurrentPage(prev => Math.max(0, prev - 1))}
                  disabled={currentPage === 0}
                >
                  Previous
                </Button>
                <span className="text-sm text-gray-700">
                  Page {currentPage + 1} of {totalPages}
                </span>
                <Button
                  variant="outline"
                  onClick={() => setCurrentPage(prev => Math.min(totalPages - 1, prev + 1))}
                  disabled={currentPage === totalPages - 1}
                >
                  Next
                </Button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
} 