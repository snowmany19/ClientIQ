'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { useAuthStore } from '@/lib/auth';
import { apiClient } from '@/lib/api';
import MetricsCard from '@/components/dashboard/MetricsCard';

import { ContractRecord, DashboardMetrics } from '@/types';
import { 
  FileText, 
  CheckCircle, 
  AlertCircle, 
  TrendingUp,
  Users,
  MapPin,
  AlertTriangle
} from 'lucide-react';

export default function Dashboard() {
  const { user } = useAuthStore();
  const router = useRouter();
  const [contracts, setContracts] = useState<ContractRecord[]>([]);
  const [metrics, setMetrics] = useState<DashboardMetrics | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Load dashboard data
    loadDashboardData();
  }, [user]); // Remove router from dependencies as it's stable

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      
      // Load contracts and metrics in parallel
      const [contractsData, metricsData] = await Promise.all([
        apiClient.getContracts(),
        apiClient.getDashboardMetrics()
      ]);

      setContracts(contractsData.data || []);
      setMetrics(metricsData);
    } catch (error) {
      console.error('Failed to load dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleContractUpdate = (updatedContract: ContractRecord) => {
    setContracts(prev => 
      prev.map(c => c.id === updatedContract.id ? updatedContract : c)
    );
  };

  const handleContractDelete = (contractId: number) => {
    setContracts(prev => prev.filter(c => c.id !== contractId));
  };

  if (loading) {
    return (
      <div className="flex-1 overflow-auto p-6">
        <div className="max-w-7xl mx-auto">
          <div className="flex items-center justify-center h-64">
            <div className="text-center">
              <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600 mx-auto"></div>
              <p className="mt-4 text-gray-600">Loading dashboard...</p>
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
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <h1 className="text-xl font-semibold text-gray-900">
                Dashboard
              </h1>
            </div>
            <div className="flex items-center space-x-4">
              <span className="text-sm text-gray-700">
                Welcome back, {user?.username}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Main content */}
      <div className="flex-1 overflow-auto p-6">
        <div className="max-w-7xl mx-auto">
          {/* Metrics Cards */}
          {metrics && (
            <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4 mb-8">
              <MetricsCard
                title="Total Contracts"
                value={metrics.total_contracts || 0}
                icon={FileText}
                color="blue"
              />
              <MetricsCard
                title="Analyzed Contracts"
                value={metrics.analyzed_contracts || 0}
                icon={CheckCircle}
                color="green"
              />
              <MetricsCard
                title="Pending Analysis"
                value={metrics.pending_contracts || 0}
                icon={AlertCircle}
                color="yellow"
              />
              <MetricsCard
                title="High Risk Contracts"
                value={metrics.high_risk_contracts || 0}
                icon={AlertTriangle}
                color="red"
              />
            </div>
          )}

          {/* Recent Contracts */}
          <div className="mb-8">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-medium text-gray-900">
                Recent Contracts
              </h2>
              <Link href="/dashboard/contracts" className="text-sm text-blue-600 hover:text-blue-500">
                View all contracts →
              </Link>
            </div>
            <div className="bg-white shadow overflow-hidden sm:rounded-md">
              {contracts.length === 0 ? (
                <div className="text-center py-8">
                  <FileText className="mx-auto h-12 w-12 text-gray-400" />
                  <h3 className="mt-2 text-sm font-medium text-gray-900">No contracts yet</h3>
                  <p className="mt-1 text-sm text-gray-500">
                    Get started by uploading your first contract.
                  </p>
                  <div className="mt-6">
                    <Link
                      href="/dashboard/contracts"
                      className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700"
                    >
                      Upload Contract
                    </Link>
                  </div>
                </div>
              ) : (
                <ul className="divide-y divide-gray-200">
                  {contracts.slice(0, 5).map((contract) => (
                    <li key={contract.id} className="px-6 py-4 hover:bg-gray-50">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-3">
                          <FileText className="h-5 w-5 text-blue-600" />
                          <div>
                            <p className="text-sm font-medium text-gray-900">{contract.title}</p>
                            <p className="text-sm text-gray-500">{contract.counterparty}</p>
                          </div>
                        </div>
                        <div className="flex items-center space-x-2">
                          <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                            contract.status === 'pending' ? 'bg-yellow-100 text-yellow-800' :
                            contract.status === 'analyzed' ? 'bg-green-100 text-green-800' :
                            'bg-gray-100 text-gray-800'
                          }`}>
                            {contract.status}
                          </span>
                          <Link
                            href={`/dashboard/contracts/${contract.id}`}
                            className="text-blue-600 hover:text-blue-500 text-sm"
                          >
                            View →
                          </Link>
                        </div>
                      </div>
                    </li>
                  ))}
                </ul>
              )}
            </div>
          </div>

          {/* Quick Stats */}
          <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-3">
            <div className="bg-white overflow-hidden shadow rounded-lg">
              <div className="p-5">
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <TrendingUp className="h-6 w-6 text-gray-400" />
                  </div>
                  <div className="ml-5 w-0 flex-1">
                    <dl>
                      <dt className="text-sm font-medium text-gray-500 truncate">
                        Average Analysis Time
                      </dt>
                      <dd className="text-lg font-medium text-gray-900">
                        {metrics?.average_analysis_time || 0} min
                      </dd>
                    </dl>
                  </div>
                </div>
              </div>
            </div>

            <div className="bg-white overflow-hidden shadow rounded-lg">
              <div className="p-5">
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <FileText className="h-6 w-6 text-gray-400" />
                  </div>
                  <div className="ml-5 w-0 flex-1">
                    <dl>
                      <dt className="text-sm font-medium text-gray-500 truncate">
                        Top Category
                      </dt>
                      <dd className="text-lg font-medium text-gray-900">
                        {metrics?.top_contract_categories?.[0]?.category || 'N/A'}
                      </dd>
                    </dl>
                  </div>
                </div>
              </div>
            </div>

            <div className="bg-white overflow-hidden shadow rounded-lg">
              <div className="p-5">
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <AlertTriangle className="h-6 w-6 text-gray-400" />
                  </div>
                  <div className="ml-5 w-0 flex-1">
                    <dl>
                      <dt className="text-sm font-medium text-gray-500 truncate">
                        High Risk Rate
                      </dt>
                      <dd className="text-lg font-medium text-gray-900">
                        {metrics?.total_contracts ? Math.round((metrics.high_risk_contracts || 0) / metrics.total_contracts * 100) : 0}%
                      </dd>
                    </dl>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </>
  );
} 