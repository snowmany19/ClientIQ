'use client';

import { useState } from 'react';
import { Violation } from '@/types';
import { apiClient } from '@/lib/api';
import { Button } from '@/components/ui/Button';
import { 
  Eye, 
  Edit, 
  Trash2, 
  CheckCircle, 
  XCircle, 
  AlertCircle,
  ChevronLeft,
  ChevronRight,
  Search,
  Filter,
  FileText,
  Mail
} from 'lucide-react';
import { TableSkeleton } from '@/components/ui/LoadingSkeleton';

interface ViolationsTableProps {
  violations: Violation[];
  loading?: boolean;
  onViolationUpdate?: (violation: Violation) => void;
  onViolationDelete?: (id: number) => void;
  onViolationView?: (violation: Violation) => void;
  onViolationEdit?: (violation: Violation) => void;
  onViolationLetter?: (violation: Violation) => void;
  onSearchChange?: (searchTerm: string) => void;
  onStatusFilterChange?: (status: string) => void;
  onSortChange?: (field: keyof Violation, direction: 'asc' | 'desc') => void;
  searchTerm?: string;
  statusFilter?: string;
  sortField?: keyof Violation;
  sortDirection?: 'asc' | 'desc';
  totalViolations?: number;
  currentPage?: number;
  totalPages?: number;
  onPageChange?: (page: number) => void;
  userRole?: string;
}

export default function ViolationsTable({ 
  violations, 
  loading = false,
  onViolationUpdate, 
  onViolationDelete,
  onViolationView,
  onViolationEdit,
  onViolationLetter,
  onSearchChange,
  onStatusFilterChange,
  onSortChange,
  searchTerm = '',
  statusFilter = 'all',
  sortField = 'timestamp',
  sortDirection = 'desc',
  totalViolations = 0,
  currentPage = 1,
  totalPages = 1,
  onPageChange,
  userRole
}: ViolationsTableProps) {
  const [localSearchTerm, setLocalSearchTerm] = useState(searchTerm);
  const [localStatusFilter, setLocalStatusFilter] = useState(statusFilter);

  // Add bulk selection state
  const [selectedViolations, setSelectedViolations] = useState<number[]>([]);
  const [selectAll, setSelectAll] = useState(false);

  // Add advanced filter state
  const [advancedFilters, setAdvancedFilters] = useState({
    dateRange: '',
    violationType: '',
    repeatOffender: false,
    hasPhotos: false,
    gpsCoordinates: false
  });

  const canEdit = userRole === 'admin' || userRole === 'hoa_board';
  const canDelete = userRole === 'admin' || userRole === 'hoa_board';
  const canGenerateLetter = userRole === 'admin' || userRole === 'hoa_board' || userRole === 'inspector';

  const handleSearchChange = (value: string) => {
    setLocalSearchTerm(value);
    onSearchChange?.(value);
  };

  const handleStatusFilterChange = (value: string) => {
    setLocalStatusFilter(value);
    onStatusFilterChange?.(value);
  };

  const handleSort = (field: keyof Violation) => {
    const newDirection = sortField === field && sortDirection === 'asc' ? 'desc' : 'asc';
    onSortChange?.(field, newDirection);
  };

  const handleStatusUpdate = async (violationId: number, newStatus: string) => {
    try {
      const updatedViolation = await apiClient.updateViolationStatus(violationId, newStatus);
      onViolationUpdate?.(updatedViolation);
    } catch (error) {
      console.error('Failed to update violation status:', error);
    }
  };

  const handleDelete = async (violationId: number) => {
    if (confirm('Are you sure you want to delete this violation?')) {
      try {
        await apiClient.deleteViolation(violationId);
        onViolationDelete?.(violationId);
      } catch (error) {
        console.error('Failed to delete violation:', error);
      }
    }
  };

  // Add bulk operations
  const handleBulkStatusUpdate = async (newStatus: string) => {
    try {
      await Promise.all(
        selectedViolations.map(id => 
          apiClient.updateViolationStatus(id, newStatus)
        )
      );
      onViolationUpdate && onViolationUpdate({} as Violation); // Refresh
      setSelectedViolations([]);
    } catch (error) {
      console.error('Bulk update failed:', error);
    }
  };

  const handleBulkDelete = async () => {
    if (confirm(`Are you sure you want to delete ${selectedViolations.length} violations?`)) {
      try {
        await Promise.all(
          selectedViolations.map(id => 
            apiClient.deleteViolation(id)
          )
        );
        onViolationDelete && selectedViolations.forEach(id => onViolationDelete(id));
        setSelectedViolations([]);
      } catch (error) {
        console.error('Bulk delete failed:', error);
      }
    }
  };

  // Add advanced search function
  const applyAdvancedFilters = (violations: Violation[]) => {
    return violations.filter(violation => {
      // Date range filter
      if (advancedFilters.dateRange) {
        const violationDate = new Date(violation.timestamp);
        const now = new Date();
        const daysAgo = parseInt(advancedFilters.dateRange);
        const cutoffDate = new Date(now.getTime() - (daysAgo * 24 * 60 * 60 * 1000));
        if (violationDate < cutoffDate) return false;
      }

      // Violation type filter
      if (advancedFilters.violationType && violation.tags) {
        if (!violation.tags.toLowerCase().includes(advancedFilters.violationType.toLowerCase())) {
          return false;
        }
      }

      // Repeat offender filter
      if (advancedFilters.repeatOffender && violation.repeat_offender_score < 3) {
        return false;
      }

      // Has photos filter
      if (advancedFilters.hasPhotos && !violation.image_url) {
        return false;
      }

      // Has GPS filter
      if (advancedFilters.gpsCoordinates && !violation.gps_coordinates) {
        return false;
      }

      return true;
    });
  };

  const getStatusBadge = (status: string) => {
    const statusConfig = {
      open: { color: 'bg-yellow-100 text-yellow-800 border border-yellow-300', icon: AlertCircle },
      under_review: { color: 'bg-blue-100 text-blue-800 border border-blue-300', icon: AlertCircle },
      resolved: { color: 'bg-green-100 text-green-800 border border-green-300', icon: CheckCircle },
      disputed: { color: 'bg-red-100 text-red-800 border border-red-300', icon: XCircle },
    };

    const config = statusConfig[status as keyof typeof statusConfig] || statusConfig.open;
    const Icon = config.icon;

    return (
      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${config.color}`}>
        <Icon className="w-3 h-3 mr-1 text-current" />
        {status.replace('_', ' ')}
      </span>
    );
  };

  return (
    <div className="bg-white shadow rounded-lg min-h-[600px] flex flex-col">
      {/* Header with search and filters */}
      <div className="px-6 py-4 border-b border-gray-200">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div className="flex-1">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
              <input
                type="text"
                placeholder="Search violations..."
                className="pl-10 pr-4 py-2 w-full border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                value={localSearchTerm}
                onChange={(e) => handleSearchChange(e.target.value)}
              />
            </div>
          </div>
          <div className="flex items-center gap-2">
            <select
              value={localStatusFilter}
              onChange={(e) => handleStatusFilterChange(e.target.value)}
              className="border border-gray-300 rounded-md px-3 py-2 focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="all">All Status</option>
              <option value="open">Open</option>
              <option value="under_review">Under Review</option>
              <option value="resolved">Resolved</option>
              <option value="disputed">Disputed</option>
            </select>
          </div>
        </div>
      </div>

      {/* Add advanced filters UI */}
      <div className="mb-4 p-4 bg-gray-50 rounded-lg">
        <div className="flex items-center justify-between mb-3">
          <h3 className="text-sm font-medium text-gray-900">Advanced Filters</h3>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setAdvancedFilters({
              dateRange: '',
              violationType: '',
              repeatOffender: false,
              hasPhotos: false,
              gpsCoordinates: false
            })}
          >
            Clear All
          </Button>
        </div>
        
        <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
          <div>
            <label className="block text-xs font-medium text-gray-700 mb-1">
              Date Range
            </label>
            <select
              value={advancedFilters.dateRange}
              onChange={(e) => setAdvancedFilters(prev => ({ ...prev, dateRange: e.target.value }))}
              className="w-full text-sm border-gray-300 rounded-md"
            >
              <option value="">All Time</option>
              <option value="7">Last 7 Days</option>
              <option value="30">Last 30 Days</option>
              <option value="90">Last 90 Days</option>
            </select>
          </div>
          
          <div>
            <label className="block text-xs font-medium text-gray-700 mb-1">
              Violation Type
            </label>
            <input
              type="text"
              placeholder="e.g., parking, noise"
              value={advancedFilters.violationType}
              onChange={(e) => setAdvancedFilters(prev => ({ ...prev, violationType: e.target.value }))}
              className="w-full text-sm border-gray-300 rounded-md"
            />
          </div>
          
          <div className="flex items-center">
            <input
              type="checkbox"
              id="repeatOffender"
              checked={advancedFilters.repeatOffender}
              onChange={(e) => setAdvancedFilters(prev => ({ ...prev, repeatOffender: e.target.checked }))}
              className="h-4 w-4 text-blue-600 border-gray-300 rounded"
            />
            <label htmlFor="repeatOffender" className="ml-2 text-xs text-gray-700">
              Repeat Offenders Only
            </label>
          </div>
          
          <div className="flex items-center">
            <input
              type="checkbox"
              id="hasPhotos"
              checked={advancedFilters.hasPhotos}
              onChange={(e) => setAdvancedFilters(prev => ({ ...prev, hasPhotos: e.target.checked }))}
              className="h-4 w-4 text-blue-600 border-gray-300 rounded"
            />
            <label htmlFor="hasPhotos" className="ml-2 text-xs text-gray-700">
              With Photos
            </label>
          </div>
          
          <div className="flex items-center">
            <input
              type="checkbox"
              id="gpsCoordinates"
              checked={advancedFilters.gpsCoordinates}
              onChange={(e) => setAdvancedFilters(prev => ({ ...prev, gpsCoordinates: e.target.checked }))}
              className="h-4 w-4 text-blue-600 border-gray-300 rounded"
            />
            <label htmlFor="gpsCoordinates" className="ml-2 text-xs text-gray-700">
              With GPS
            </label>
          </div>
        </div>
      </div>

      {/* Add bulk operations UI */}
      {selectedViolations.length > 0 && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-4">
          <div className="flex items-center justify-between">
            <p className="text-sm font-medium text-blue-900">
              {selectedViolations.length} violation(s) selected
            </p>
            <div className="flex space-x-2">
              <Button
                variant="outline"
                size="sm"
                onClick={() => handleBulkStatusUpdate('resolved')}
              >
                Mark Resolved
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={() => handleBulkStatusUpdate('escalated')}
              >
                Escalate
              </Button>
              <Button
                variant="destructive"
                size="sm"
                onClick={handleBulkDelete}
              >
                Delete Selected
              </Button>
            </div>
          </div>
        </div>
      )}

      {/* Table */}
      <div className="flex-1 overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th 
                className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                onClick={() => handleSort('violation_number')}
              >
                <div className="flex items-center">
                  #
                  {sortField === 'violation_number' && (
                    <span className="ml-1">{sortDirection === 'asc' ? '↑' : '↓'}</span>
                  )}
                </div>
              </th>
              <th 
                className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                onClick={() => handleSort('timestamp')}
              >
                <div className="flex items-center">
                  Date
                  {sortField === 'timestamp' && (
                    <span className="ml-1">{sortDirection === 'asc' ? '↑' : '↓'}</span>
                  )}
                </div>
              </th>
              <th 
                className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                onClick={() => handleSort('description')}
              >
                <div className="flex items-center">
                  Description
                  {sortField === 'description' && (
                    <span className="ml-1">{sortDirection === 'asc' ? '↑' : '↓'}</span>
                  )}
                </div>
              </th>
              <th 
                className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                onClick={() => handleSort('address')}
              >
                <div className="flex items-center">
                  Address
                  {sortField === 'address' && (
                    <span className="ml-1">{sortDirection === 'asc' ? '↑' : '↓'}</span>
                  )}
                </div>
              </th>
              <th 
                className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                onClick={() => handleSort('offender')}
              >
                <div className="flex items-center">
                  Offender
                  {sortField === 'offender' && (
                    <span className="ml-1">{sortDirection === 'asc' ? '↑' : '↓'}</span>
                  )}
                </div>
              </th>
              <th 
                className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                onClick={() => handleSort('status')}
              >
                <div className="flex items-center">
                  Status
                  {sortField === 'status' && (
                    <span className="ml-1">{sortDirection === 'asc' ? '↑' : '↓'}</span>
                  )}
                </div>
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Actions
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {loading ? (
              <tr>
                <td colSpan={7} className="px-6 py-4">
                  <TableSkeleton />
                </td>
              </tr>
            ) : violations.length === 0 ? (
              <tr>
                <td colSpan={7} className="px-6 py-12 text-center text-gray-500">
                  <div className="flex flex-col items-center">
                    <FileText className="h-12 w-12 text-gray-300 mb-4" />
                    <p className="text-lg font-medium">No violations found</p>
                    <p className="text-sm">Try adjusting your search or filters</p>
                  </div>
                </td>
              </tr>
            ) : (
              violations.map((violation) => (
                <tr key={violation.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                    {violation.violation_number}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {new Date(violation.timestamp).toLocaleDateString()}
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-900 max-w-xs truncate">
                    {violation.description}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {violation.address}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {violation.offender}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    {getStatusBadge(violation.status)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                    <div className="flex items-center space-x-2">
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => onViolationView?.(violation)}
                        title="View details"
                        className="text-gray-600 hover:text-blue-600 hover:bg-blue-50"
                      >
                        <Eye className="h-4 w-4" />
                      </Button>
                      {canEdit && (
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => onViolationEdit?.(violation)}
                          title="Edit violation"
                          className="text-gray-600 hover:text-green-600 hover:bg-green-50"
                        >
                          <Edit className="h-4 w-4" />
                        </Button>
                      )}
                      {canGenerateLetter && (
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => onViolationLetter?.(violation)}
                          title="Generate letter"
                          className="text-gray-600 hover:text-purple-600 hover:bg-purple-50"
                        >
                          <Mail className="h-4 w-4" />
                        </Button>
                      )}
                      {canDelete && (
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handleDelete(violation.id)}
                          title="Delete violation"
                          className="text-gray-600 hover:text-red-600 hover:bg-red-50"
                        >
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      )}
                    </div>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="px-6 py-4 border-t border-gray-200">
          <div className="flex items-center justify-between">
            <div className="text-sm text-gray-700">
              Showing {((currentPage - 1) * 50) + 1} to {Math.min(currentPage * 50, totalViolations)} of {totalViolations} results
            </div>
            <div className="flex items-center space-x-2">
              <Button
                variant="outline"
                size="sm"
                onClick={() => onPageChange?.(currentPage - 1)}
                disabled={currentPage === 1}
              >
                <ChevronLeft className="h-4 w-4" />
                Previous
              </Button>
              <span className="text-sm text-gray-700">
                Page {currentPage} of {totalPages}
              </span>
              <Button
                variant="outline"
                size="sm"
                onClick={() => onPageChange?.(currentPage + 1)}
                disabled={currentPage === totalPages}
              >
                Next
                <ChevronRight className="h-4 w-4" />
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
} 