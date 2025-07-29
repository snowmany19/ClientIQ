'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { useAuthStore } from '@/lib/auth';
import { apiClient } from '@/lib/api';
import MetricsCard from '@/components/dashboard/MetricsCard';
import ViolationsTable from '@/components/dashboard/ViolationsTable';
import { Violation, DashboardMetrics } from '@/types';
import { 
  FileText, 
  CheckCircle, 
  AlertCircle, 
  TrendingUp,
  Users,
  MapPin
} from 'lucide-react';

export default function Dashboard() {
  const { user } = useAuthStore();
  const [violations, setViolations] = useState<Violation[]>([]);
  const [metrics, setMetrics] = useState<DashboardMetrics | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Load dashboard data
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      
      // Load violations and metrics in parallel
      const [dashboardData, metricsData] = await Promise.all([
        apiClient.getDashboardData({ limit: 50 }),
        apiClient.getDashboardMetrics()
      ]);

      setViolations(dashboardData.violations);
      setMetrics(metricsData);
    } catch (error) {
      console.error('Failed to load dashboard data:', error);
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
                title="Total Violations"
                value={metrics.total_violations}
                icon={FileText}
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

          {/* Recent Violations */}
          <div className="mb-8">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-medium text-gray-900">
                Recent Violations
              </h2>
              <Link href="/dashboard/violations" className="text-sm text-blue-600 hover:text-blue-500">
                View all violations →
              </Link>
            </div>
            <ViolationsTable
              violations={violations.slice(0, 10)}
              onViolationUpdate={handleViolationUpdate}
              onViolationDelete={handleViolationDelete}
              userRole={user?.role}
            />
          </div>

          {/* Quick Stats */}
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
                    <MapPin className="h-6 w-6 text-gray-400" />
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
        </div>
      </div>
    </>
  );
} 