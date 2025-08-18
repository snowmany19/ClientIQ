'use client';

import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { useAuthStore } from '@/lib/auth';
import { useContracts, useDashboardMetrics } from '@/lib/hooks';
import MetricsCard from '@/components/dashboard/MetricsCard';

import { 
  FileText, 
  CheckCircle, 
  AlertCircle, 
  TrendingUp,
  Users,
  MapPin,
  AlertTriangle,
  Plus
} from 'lucide-react';

export default function Dashboard() {
  const { user } = useAuthStore();
  const router = useRouter();

  // Use React Query hooks for better performance
  const { data: contracts = [], isLoading: contractsLoading } = useContracts();
  const { data: metrics, isLoading: metricsLoading } = useDashboardMetrics();

  const isLoading = contractsLoading || metricsLoading;

  if (isLoading) {
    return (
      <div className="flex-1 overflow-auto p-6">
        <div className="max-w-7xl mx-auto">
          <div className="flex items-center justify-center h-64">
            <div className="text-center">
              <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600 mx-auto"></div>
              <p className="mt-4 text-gray-600 dark:text-gray-400">Loading dashboard...</p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <>
      {/* Header */}
      <div className="bg-white dark:bg-gray-800 shadow flex-shrink-0">
        <div className="w-full px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <h1 className="text-xl font-semibold text-gray-900 dark:text-gray-100">
                Dashboard
              </h1>
            </div>
            <div className="flex items-center space-x-4">
              <span className="text-sm text-gray-700 dark:text-gray-300">
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
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            <MetricsCard
              title="Total Contracts"
              value={contracts.length}
              icon={FileText}
              trend="+12%"
              trendDirection="up"
              color="blue"
            />
            <MetricsCard
              title="Completed Analysis"
              value={contracts.filter(c => c.status === 'completed').length}
              icon={CheckCircle}
              trend="+8%"
              trendDirection="up"
              color="green"
            />
            <MetricsCard
              title="Pending Review"
              value={contracts.filter(c => c.status === 'pending').length}
              icon={AlertCircle}
              trend="-3%"
              trendDirection="down"
              color="yellow"
            />
            <MetricsCard
              title="Risk Score"
              value={metrics?.average_risk_score?.toFixed(1) || '0.0'}
              icon={AlertTriangle}
              trend="+2%"
              trendDirection="up"
              color="red"
            />
          </div>

          {/* Quick Actions */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">
                Quick Actions
              </h3>
              <div className="space-y-3">
                <Link
                  href="/dashboard/contracts"
                  className="flex items-center p-3 rounded-lg border border-gray-200 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
                >
                  <Plus className="h-5 w-5 text-blue-600 mr-3" />
                  <span className="text-gray-700 dark:text-gray-300">Upload New Contract</span>
                </Link>
                <Link
                  href="/dashboard/analytics"
                  className="flex items-center p-3 rounded-lg border border-gray-200 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
                >
                  <TrendingUp className="h-5 w-5 text-green-600 mr-3" />
                  <span className="text-gray-700 dark:text-gray-300">View Analytics</span>
                </Link>
                <Link
                  href="/dashboard/settings"
                  className="flex items-center p-3 rounded-lg border border-gray-200 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
                >
                  <Users className="h-5 w-5 text-purple-600 mr-3" />
                  <span className="text-gray-700 dark:text-gray-300">Manage Settings</span>
                </Link>
              </div>
            </div>

            <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">
                Recent Activity
              </h3>
              <div className="space-y-3">
                {contracts.slice(0, 3).map((contract) => (
                  <div key={contract.id} className="flex items-center justify-between p-3 rounded-lg bg-gray-50 dark:bg-gray-700">
                    <div className="flex items-center">
                      <FileText className="h-4 w-4 text-gray-400 mr-3" />
                      <div>
                        <p className="text-sm font-medium text-gray-900 dark:text-gray-100">
                          {contract.title}
                        </p>
                        <p className="text-xs text-gray-500 dark:text-gray-400">
                          {contract.counterparty}
                        </p>
                      </div>
                    </div>
                    <span className={`px-2 py-1 text-xs rounded-full ${getStatusColor(contract.status)}`}>
                      {contract.status}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Contract Summary */}
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow">
            <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100">
                Contract Overview
              </h3>
            </div>
            <div className="p-6">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="text-center">
                  <div className="text-2xl font-bold text-blue-600 dark:text-blue-400">
                    {contracts.length}
                  </div>
                  <div className="text-sm text-gray-500 dark:text-gray-400">Total Contracts</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-green-600 dark:text-green-400">
                    {contracts.filter(c => c.status === 'completed').length}
                  </div>
                  <div className="text-sm text-gray-500 dark:text-gray-400">Analyzed</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-yellow-600 dark:text-yellow-400">
                    {contracts.filter(c => c.status === 'pending').length}
                  </div>
                  <div className="text-sm text-gray-500 dark:text-gray-400">Pending</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </>
  );
}

function getStatusColor(status: string) {
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
} 