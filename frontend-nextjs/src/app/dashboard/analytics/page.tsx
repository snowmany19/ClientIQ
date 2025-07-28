'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuthStore } from '@/lib/auth';
import { apiClient } from '@/lib/api';
import Sidebar from '@/components/layout/Sidebar';
import MetricsCard from '@/components/dashboard/MetricsCard';
import ViolationsChart from '@/components/dashboard/ViolationsChart';
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
  const { user, isAuthenticated, getCurrentUser } = useAuthStore();
  const router = useRouter();
  const [metrics, setMetrics] = useState<DashboardMetrics | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!isAuthenticated) {
      router.push('/');
      return;
    }

    if (!user) {
      getCurrentUser();
    }

    loadAnalytics();
  }, [isAuthenticated, user, router, getCurrentUser]);

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

  if (!isAuthenticated || !user) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading analytics...</p>
        </div>
      </div>
    );
  }

  // Transform data for charts
  const monthlyTrendsData = metrics?.monthly_trends?.map(trend => ({
    date: new Date(trend.date).toLocaleDateString('en-US', { month: 'short', year: 'numeric' }),
    count: trend.count
  })) || [];

  const violationTypesData = metrics?.top_violation_types?.map(type => ({
    date: type.type,
    count: type.count
  })) || [];

  return (
    <div className="min-h-screen bg-gray-50">
      <Sidebar />
      
      <div className="lg:pl-64">
        {/* Header */}
        <div className="bg-white shadow">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
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
        <div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
          {/* Key Metrics */}
          {metrics && (
            <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4 mb-8">
              <MetricsCard
                title="Total Violations"
                value={metrics.total_violations}
                icon={BarChart3}
                color="blue"
              />
              <MetricsCard
                title="Open Violations"
                value={metrics.open_violations}
                icon={AlertCircle}
                color="yellow"
              />
              <MetricsCard
                title="Resolved"
                value={metrics.resolved_violations}
                icon={CheckCircle}
                color="green"
              />
              <MetricsCard
                title="Resolution Rate"
                value={`${metrics.resolution_rate}%`}
                icon={TrendingUp}
                color="purple"
              />
            </div>
          )}

          {/* Charts */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
            <ViolationsChart
              data={monthlyTrendsData}
              type="line"
              title="Monthly Violation Trends"
              height={300}
            />
            <ViolationsChart
              data={violationTypesData}
              type="bar"
              title="Violation Types"
              height={300}
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
                        Repeat Offenders
                      </dt>
                      <dd className="text-lg font-medium text-gray-900">
                        {metrics?.repeat_offenders || 0}
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
                        Average Resolution Time
                      </dt>
                      <dd className="text-lg font-medium text-gray-900">
                        {metrics?.average_resolution_time || 0} days
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
                        Disputed Violations
                      </dt>
                      <dd className="text-lg font-medium text-gray-900">
                        {metrics?.disputed_violations || 0}
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
                      <li>• Resolution rate: {metrics.resolution_rate}%</li>
                      <li>• Average resolution time: {metrics.average_resolution_time} days</li>
                      <li>• Repeat offenders: {metrics.repeat_offenders}</li>
                    </ul>
                  </div>
                  <div>
                    <h4 className="text-sm font-medium text-gray-900 mb-2">
                      Recommendations
                    </h4>
                    <ul className="text-sm text-gray-600 space-y-1">
                      <li>• Focus on reducing resolution time</li>
                      <li>• Address repeat offender patterns</li>
                      <li>• Improve communication with residents</li>
                    </ul>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
} 