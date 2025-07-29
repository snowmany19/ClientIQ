'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuthStore } from '@/lib/auth';
import { apiClient } from '@/lib/api';
import ViolationsTable from '@/components/dashboard/ViolationsTable';
import { Button } from '@/components/ui/Button';
import { Violation } from '@/types';
import { Plus, Download } from 'lucide-react';

export default function ViolationsPage() {
  const { user } = useAuthStore();
  const router = useRouter();
  const [violations, setViolations] = useState<Violation[]>([]);
  const [loading, setLoading] = useState(true);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(0);
  const [totalViolations, setTotalViolations] = useState(0);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [sortField, setSortField] = useState<keyof Violation>('timestamp');
  const [sortDirection, setSortDirection] = useState<'asc' | 'desc'>('desc');

  useEffect(() => {
    loadViolations();
  }, [currentPage, searchTerm, statusFilter, sortField, sortDirection]);

  const loadViolations = async () => {
    try {
      setLoading(true);
      const params: any = {
        skip: (currentPage - 1) * 50,
        limit: 50
      };
      
      if (searchTerm) {
        // Note: Backend doesn't support search yet, so we'll filter client-side for now
      }
      
      if (statusFilter !== 'all') {
        params.status = statusFilter;
      }
      
      const response = await apiClient.getViolations(params);
      
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

  const handleSearchChange = (newSearchTerm: string) => {
    setSearchTerm(newSearchTerm);
    setCurrentPage(1); // Reset to first page when searching
  };

  const handleStatusFilterChange = (newStatusFilter: string) => {
    setStatusFilter(newStatusFilter);
    setCurrentPage(1); // Reset to first page when filtering
  };

  const handleSortChange = (field: keyof Violation, direction: 'asc' | 'desc') => {
    setSortField(field);
    setSortDirection(direction);
    setCurrentPage(1); // Reset to first page when sorting
  };

  const handlePageChange = (newPage: number) => {
    setCurrentPage(newPage);
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

  return (
    <>
      {/* Header */}
      <div className="bg-white shadow flex-shrink-0">
        <div className="w-full px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Violations</h1>
              <p className="mt-1 text-sm text-gray-500">
                Manage and track HOA violations
              </p>
            </div>
            <div className="flex items-center space-x-3">
              <Button
                variant="outline"
                onClick={handleExportCSV}
                className="flex items-center"
              >
                <Download className="h-4 w-4 mr-2" />
                Export CSV
              </Button>
              <Button
                onClick={() => router.push('/dashboard/violations/new')}
                className="flex items-center"
              >
                <Plus className="h-4 w-4 mr-2" />
                New Violation
              </Button>
            </div>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-auto p-6">
        <div className="max-w-7xl mx-auto">
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
              onSearchChange={handleSearchChange}
              onStatusFilterChange={handleStatusFilterChange}
              onSortChange={handleSortChange}
              searchTerm={searchTerm}
              statusFilter={statusFilter}
              sortField={sortField}
              sortDirection={sortDirection}
              totalViolations={totalViolations}
              currentPage={currentPage}
              totalPages={totalPages}
              onPageChange={handlePageChange}
              userRole={user?.role}
            />
          )}
        </div>
      </div>
    </>
  );
} 