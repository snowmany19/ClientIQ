'use client';

import { Suspense, lazy } from 'react';
import { useAuthStore } from '@/lib/auth';
import { useRouter } from 'next/navigation';
import { useEffect } from 'react';

// Lazy load components for better performance
const Sidebar = lazy(() => import('@/components/layout/Sidebar'));

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const { user, isAuthenticated, isLoading, getCurrentUser } = useAuthStore();
  const router = useRouter();

  useEffect(() => {
    // Only redirect if we're not loading and definitely not authenticated
    if (!isLoading && !isAuthenticated) {
      router.push('/login');
    }
  }, [isLoading, isAuthenticated, router]);

  // Load user data when dashboard loads (if authenticated but no user data)
  useEffect(() => {
    if (isAuthenticated && !user && !isLoading) {
      console.log('🔄 Loading user data for dashboard...');
      getCurrentUser();
    }
  }, [isAuthenticated, user, isLoading, getCurrentUser]);

  // Show loading spinner while auth is initializing
  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  // Only show loading spinner if not authenticated after initialization
  if (!isAuthenticated) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  // If authenticated, render the dashboard even without user data
  // User data will be loaded by individual components as needed

  return (
    <div className="flex h-screen bg-gray-100 dark:bg-gray-900">
      <Suspense fallback={
        <div className="w-64 bg-white dark:bg-gray-800 shadow-lg flex items-center justify-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        </div>
      }>
        <Sidebar />
      </Suspense>
      
      <div className="flex-1 flex flex-col overflow-hidden">
        <Suspense fallback={
          <div className="flex-1 overflow-auto p-6">
            <div className="max-w-7xl mx-auto">
              <div className="flex items-center justify-center h-64">
                <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
              </div>
            </div>
          </div>
        }>
          {children}
        </Suspense>
      </div>
    </div>
  );
} 