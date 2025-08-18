import { useQuery } from '@tanstack/react-query';
import { apiClient } from '@/lib/api';

// Query keys for dashboard
export const dashboardKeys = {
  all: ['dashboard'] as const,
  metrics: () => [...dashboardKeys.all, 'metrics'] as const,
  analytics: () => [...dashboardKeys.all, 'analytics'] as const,
};

// Hook for fetching dashboard metrics
export function useDashboardMetrics() {
  return useQuery({
    queryKey: dashboardKeys.metrics(),
    queryFn: async () => {
      return await apiClient.getDashboardMetrics();
    },
    staleTime: 1000 * 60 * 5, // 5 minutes
  });
}

// Hook for fetching analytics data
export function useAnalytics() {
  return useQuery({
    queryKey: dashboardKeys.analytics(),
    queryFn: async () => {
      return await apiClient.getAnalytics();
    },
    staleTime: 1000 * 60 * 10, // 10 minutes
  });
}
