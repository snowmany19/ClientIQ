'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { useAuthStore } from '@/lib/auth';
import { ContractRecord, ContractCreate } from '@/types';
import ContractUploadForm from '@/components/forms/ContractUploadForm';
import { useContracts, useDeleteContract, useAnalyzeContract } from '@/lib/hooks/useContracts';
import { 
  Plus, 
  FileText, 
  Search, 
  Filter,
  Upload,
  Eye,
  Trash2,
  AlertTriangle,
  CheckCircle,
  Clock,
  Download,
  MessageSquare
} from 'lucide-react';
import { apiClient } from '@/lib/api';

export default function ContractsPage() {
  const { user } = useAuthStore();
  const router = useRouter();
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [selectedStatus, setSelectedStatus] = useState<string>('all');
  const [showUploadModal, setShowUploadModal] = useState(false);

  // Use React Query hooks for better performance
  const { data: contracts = [], isLoading, error } = useContracts();
  
  // Debug logging
  console.log('=== ContractsPage: Render ===');
  console.log('Contracts data:', contracts);
  console.log('Contracts length:', contracts?.length || 0);
  console.log('Is loading:', isLoading);
  console.log('Error:', error);
  
  if (contracts && Array.isArray(contracts)) {
    console.log('First few contracts:', contracts.slice(0, 3));
  }

  const deleteContractMutation = useDeleteContract();
  const analyzeContractMutation = useAnalyzeContract();

  const handleContractDelete = async (contractId: number) => {
    if (!confirm('Are you sure you want to delete this contract?')) return;
    
    try {
      await deleteContractMutation.mutateAsync(contractId);
    } catch (error) {
      console.error('Failed to delete contract:', error);
    }
  };

  const handleAnalyzeContract = async (contractId: number) => {
    try {
      await analyzeContractMutation.mutateAsync(contractId);
    } catch (error) {
      console.error('Failed to analyze contract:', error);
    }
  };

  const handleDownloadReport = async (contractId: number) => {
    try {
      const blob = await apiClient.downloadContractReport(contractId);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `contract_analysis_${contractId}_${new Date().toISOString().slice(0, 10)}.pdf`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (error) {
      console.error('Failed to download report:', error);
    }
  };

  const filteredContracts = contracts.filter((contract: any) => {
    const matchesSearch = contract.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         contract.counterparty.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesCategory = selectedCategory === 'all' || contract.category === selectedCategory;
    const matchesStatus = selectedStatus === 'all' || contract.status === selectedStatus;
    
    return matchesSearch && matchesCategory && matchesStatus;
  });

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'pending':
        return <Clock className="h-4 w-4 text-yellow-500" />;
      case 'analyzing':
        return <AlertTriangle className="h-4 w-4 text-blue-500" />;
      case 'completed':
        return <CheckCircle className="h-4 w-4 text-green-500" />;
      case 'error':
        return <AlertTriangle className="h-4 w-4 text-red-500" />;
      default:
        return <Clock className="h-4 w-4 text-gray-500" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'pending':
        return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/20 dark:text-yellow-300';
      case 'analyzing':
        return 'bg-blue-100 text-blue-800 dark:bg-blue-900/20 dark:text-blue-300';
      case 'completed':
        return 'bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-300';
      case 'error':
        return 'bg-red-100 text-red-800 dark:bg-red-900/20 dark:text-red-300';
      default:
        return 'bg-gray-100 text-gray-800 dark:bg-gray-900/20 dark:text-gray-300';
    }
  };

  const getCategoryColor = (category: string) => {
    switch (category) {
      case 'NDA':
        return 'bg-purple-100 text-purple-800';
      case 'MSA':
        return 'bg-blue-100 text-blue-800';
      case 'SOW':
        return 'bg-green-100 text-green-800';
      case 'Employment':
        return 'bg-orange-100 text-orange-800';
      case 'Vendor':
        return 'bg-indigo-100 text-indigo-800';
      case 'Lease':
        return 'bg-pink-100 text-pink-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  if (isLoading) {
    return (
      <div className="flex-1 overflow-auto p-6">
        <div className="max-w-7xl mx-auto">
          <div className="flex items-center justify-center h-64">
            <div className="text-center">
              <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600 mx-auto"></div>
              <p className="mt-4 text-gray-600 dark:text-gray-400">Loading contracts...</p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex-1 overflow-auto p-6">
        <div className="max-w-7xl mx-auto">
          <div className="text-center">
            <AlertTriangle className="h-16 w-16 text-red-500 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-2">
              Failed to load contracts
            </h3>
            <p className="text-gray-600 dark:text-gray-400 mb-4">
              There was an error loading your contracts. Please try again.
            </p>
            <button
              onClick={() => window.location.reload()}
              className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
            >
              Retry
            </button>
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
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <h1 className="text-xl font-semibold text-gray-900">
                Contracts
              </h1>
            </div>
            <div className="flex items-center space-x-4">
              <button
                onClick={() => setShowUploadModal(true)}
                className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
              >
                <Plus className="h-4 w-4 mr-2" />
                Upload Contract
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Main content */}
      <div className="flex-1 overflow-auto p-6">
        <div className="max-w-7xl mx-auto">
          {/* Filters */}
          <div className="mb-6 bg-white p-4 rounded-lg shadow">
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              {/* Search */}
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                <input
                  type="text"
                  placeholder="Search contracts..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10 pr-4 py-2 w-full border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                />
              </div>

              {/* Category Filter */}
              <select
                value={selectedCategory}
                onChange={(e) => setSelectedCategory(e.target.value)}
                className="px-4 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="all">All Categories</option>
                <option value="NDA">NDA</option>
                <option value="MSA">MSA</option>
                <option value="SOW">SOW</option>
                <option value="Employment">Employment</option>
                <option value="Vendor">Vendor</option>
                <option value="Lease">Lease</option>
                <option value="Other">Other</option>
              </select>

              {/* Status Filter */}
              <select
                value={selectedStatus}
                onChange={(e) => setSelectedStatus(e.target.value)}
                className="px-4 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="all">All Status</option>
                <option value="pending">Pending</option>
                <option value="analyzed">Analyzed</option>
                <option value="reviewed">Reviewed</option>
                <option value="approved">Approved</option>
                <option value="rejected">Rejected</option>
              </select>

              {/* Clear Filters */}
              <button
                onClick={() => {
                  setSearchTerm('');
                  setSelectedCategory('all');
                  setSelectedStatus('all');
                }}
                className="px-4 py-2 text-sm text-gray-600 hover:text-gray-800 border border-gray-300 rounded-md hover:bg-gray-50"
              >
                Clear Filters
              </button>
            </div>
          </div>

          {/* Contracts List */}
          <div className="bg-white shadow overflow-hidden sm:rounded-md">
            {filteredContracts.length === 0 ? (
              <div className="text-center py-12">
                <FileText className="mx-auto h-12 w-12 text-gray-400" />
                <h3 className="mt-2 text-sm font-medium text-gray-900">No contracts found</h3>
                <p className="mt-1 text-sm text-gray-500">
                  Get started by uploading your first contract.
                </p>
                <div className="mt-6">
                  <button
                    onClick={() => setShowUploadModal(true)}
                    className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                  >
                    <Upload className="h-4 w-4 mr-2" />
                    Upload Contract
                  </button>
                </div>
              </div>
            ) : (
              <ul className="divide-y divide-gray-200">
                {filteredContracts.map((r: any) => (
                  <div
                    key={r.id}
                    className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-4 hover:shadow-md transition-shadow"
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-4">
                        <div className="flex-shrink-0">
                          <FileText className="h-8 w-8 text-blue-600" />
                        </div>
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center space-x-2">
                            <h3 className="text-sm font-medium text-white truncate">
                              {r.title}
                            </h3>
                            <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getCategoryColor(r.category)}`}>
                              {r.category}
                            </span>
                            <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(r.status)}`}>
                              {getStatusIcon(r.status)}
                              <span className="ml-1">{r.status}</span>
                            </span>
                          </div>
                          <p className="text-sm text-gray-300">
                            Counterparty: {r.counterparty}
                          </p>
                          <p className="text-xs text-gray-400">
                            Created: {new Date(r.created_at).toLocaleDateString()}
                            {r.effective_date && ` • Effective: ${new Date(r.effective_date).toLocaleDateString()}`}
                          </p>
                        </div>
                      </div>
                      
                      <div className="flex items-center space-x-2">
                        {/* Risk indicator */}
                        {r.risk_items && r.risk_items.length > 0 && (
                          <div className="flex items-center space-x-1">
                            <AlertTriangle className="h-4 w-4 text-red-500" />
                            <span className="text-xs text-red-400 font-medium">
                              {r.risk_items.filter((risk: any) => risk.severity >= 4).length} high risks
                            </span>
                          </div>
                        )}

                        {/* Actions */}
                        <div className="flex items-center space-x-1">
                          <Link
                            href={`/dashboard/contracts/${r.id}`}
                            className="p-1 text-gray-400 hover:text-gray-600"
                            title="View Details"
                          >
                            <Eye className="h-4 w-4" />
                          </Link>
                          
                          {r.status === 'pending' && (
                            <button
                              onClick={() => handleAnalyzeContract(r.id)}
                              className="p-1 text-gray-400 hover:text-blue-600"
                              title="Analyze Contract"
                            >
                              <Search className="h-4 w-4" />
                            </button>
                          )}
                          
                          {r.analysis_json && (
                            <button
                              onClick={() => handleDownloadReport(r.id)}
                              className="p-1 text-gray-400 hover:text-green-600"
                              title="Download Report"
                            >
                              <Download className="h-4 w-4" />
                            </button>
                          )}
                          
                          <button
                            onClick={() => handleContractDelete(r.id)}
                            className="p-1 text-gray-400 hover:text-red-600"
                            title="Delete Contract"
                          >
                            <Trash2 className="h-4 w-4" />
                          </button>
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </ul>
            )}
          </div>
        </div>
      </div>

      {/* Upload Modal */}
      {showUploadModal && (
        <ContractUploadForm
          onClose={() => setShowUploadModal(false)}
          onSuccess={() => {
            setShowUploadModal(false);
            // Reload contracts after successful upload
            // This is handled by React Query's refetching
          }}
        />
      )}
    </>
  );
}
