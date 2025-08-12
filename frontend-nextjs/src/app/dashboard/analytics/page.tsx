'use client';

import { useEffect, useState } from 'react';
import { useAuthStore } from '@/lib/auth';
import { apiClient } from '@/lib/api';
import MetricsCard from '@/components/dashboard/MetricsCard';
import ContractTrendsChart from '@/components/dashboard/ContractTrendsChart';
import ContractCategoriesChart from '@/components/dashboard/ContractCategoriesChart';

import { DashboardMetrics } from '@/types';
import { 
  TrendingUp, 
  AlertCircle, 
  CheckCircle, 
  Users,
  Calendar,
  BarChart3
} from 'lucide-react';

export default function AnalyticsPage() {
  const { user } = useAuthStore();
  const [metrics, setMetrics] = useState<DashboardMetrics | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadAnalytics();
  }, []);

  const loadAnalytics = async () => {
    try {
      setLoading(true);
      const metricsData = await apiClient.getDashboardMetrics();
      setMetrics(metricsData);
    } catch (error) {
      console.error('Failed to load analytics:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex-1 overflow-auto p-6">
        <div className="max-w-7xl mx-auto">
          <div className="flex items-center justify-center h-64">
            <div className="text-center">
              <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600 mx-auto"></div>
              <p className="mt-4 text-gray-600">Loading analytics...</p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // Transform data for charts
  const monthlyTrendsData = metrics?.monthly_contract_trends
    ?.map(trend => ({
      date: new Date(trend.date).toLocaleDateString('en-US', { month: 'short', year: 'numeric' }),
      count: trend.count,
      originalDate: new Date(trend.date)
    }))
    ?.sort((a, b) => a.originalDate.getTime() - b.originalDate.getTime())
    ?.map(({ date, count }) => ({ date, count })) || [];

  return (
    <>
      {/* Header */}
      <div className="bg-white shadow flex-shrink-0">
        <div className="w-full px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <h1 className="text-xl font-semibold text-gray-900">
                Analytics
              </h1>
            </div>
            <div className="flex items-center space-x-4">
              <span className="text-sm text-gray-700">
                Last updated: {new Date().toLocaleDateString()}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Main content */}
      <div className="flex-1 overflow-auto p-6">
        <div className="max-w-7xl mx-auto">
          {/* Key Metrics */}
          {metrics && (
            <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4 mb-8">
              <MetricsCard
                title="Total Contracts"
                value={metrics.total_contracts || 0}
                icon={BarChart3}
                color="blue"
              />
              <MetricsCard
                title="Pending Analysis"
                value={metrics.pending_contracts || 0}
                icon={AlertCircle}
                color="yellow"
              />
              <MetricsCard
                title="Analyzed"
                value={metrics.analyzed_contracts || 0}
                icon={CheckCircle}
                color="green"
              />
              <MetricsCard
                title="High Risk Rate"
                value={`${metrics.total_contracts ? Math.round((metrics.high_risk_contracts || 0) / metrics.total_contracts * 100) : 0}%`}
                icon={TrendingUp}
                color="purple"
              />
            </div>
          )}

          {/* Charts */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
            <ContractTrendsChart
              data={monthlyTrendsData}
              title="Monthly Contract Trends"
            />
            <ContractCategoriesChart
              data={metrics?.top_contract_categories || []}
              title="Top Contract Categories"
            />
          </div>

          {/* Additional Metrics */}
          <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-3">
            <div className="bg-white overflow-hidden shadow rounded-lg">
              <div className="p-5">
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <Users className="h-6 w-6 text-gray-400" />
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
                    <Calendar className="h-6 w-6 text-gray-400" />
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
                    <AlertCircle className="h-6 w-6 text-gray-400" />
                  </div>
                  <div className="ml-5 w-0 flex-1">
                    <dl>
                      <dt className="text-sm font-medium text-gray-500 truncate">
                        Storage Used
                      </dt>
                      <dd className="text-lg font-medium text-gray-900">
                        {metrics?.total_contracts ? Math.round((metrics.total_contracts * 2.5)) : 0} MB
                      </dd>
                    </dl>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Insights */}
          {metrics && (
            <div className="mt-8 bg-white shadow rounded-lg">
              <div className="px-6 py-4 border-b border-gray-200">
                <h3 className="text-lg font-medium text-gray-900">
                  Key Insights
                </h3>
              </div>
              <div className="p-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <h4 className="text-sm font-medium text-gray-900 mb-2">
                      Performance Summary
                    </h4>
                    <ul className="text-sm text-gray-600 space-y-1">
                      <li>• Analysis completion rate: {metrics.analyzed_contracts && metrics.total_contracts ? Math.round((metrics.analyzed_contracts / metrics.total_contracts) * 100) : 0}%</li>
                      <li>• Average analysis time: {metrics.average_analysis_time || 0} minutes</li>
                      <li>• High risk contracts: {metrics.high_risk_contracts || 0}</li>
                    </ul>
                  </div>
                  <div>
                    <h4 className="text-sm font-medium text-gray-900 mb-2">
                      Recommendations
                    </h4>
                    <ul className="text-sm text-gray-600 space-y-1">
                      <li>• Focus on reducing analysis time</li>
                      <li>• Address high-risk contract patterns</li>
                      <li>• Improve contract review workflow</li>
                    </ul>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </>
  );
} 