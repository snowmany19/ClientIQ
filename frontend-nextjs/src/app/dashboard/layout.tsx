'use client';

import { useEffect } from 'react';
import { useRouter, usePathname } from 'next/navigation';
import { useAuthStore } from '@/lib/auth';
import Sidebar from '@/components/layout/Sidebar';
import { ErrorBoundary } from '@/components/ui/ErrorBoundary';
import { InstallPrompt } from '@/components/ui/InstallPrompt';

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const { user, isAuthenticated, isLoading, initializeAuth } = useAuthStore();
  const router = useRouter();
  const pathname = usePathname();

  useEffect(() => {
    // Initialize auth state on component mount
    initializeAuth();
  }, []); // initializeAuth is stable from Zustand store

  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      router.push('/');
    }
  }, [isAuthenticated, isLoading, router]);

  useEffect(() => {
    // Redirect to login if not authenticated
    if (!isLoading && !isAuthenticated) {
      router.push('/');
      return;
    }

    // Redirect to appropriate page if on login page but authenticated
    if (isAuthenticated && pathname === '/') {
      router.push('/dashboard');
      return;
    }
  }, [isAuthenticated, isLoading, pathname, router]);

  if (isLoading) {
    return (
      <div className="h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return null;
  }

  return (
    <ErrorBoundary>
      <div className="h-screen flex bg-gray-50">
        <Sidebar />
        <div className="flex-1 flex flex-col overflow-hidden lg:ml-0">
          <main className="flex-1 overflow-y-auto">
            {children}
          </main>
        </div>
        <InstallPrompt />
      </div>
    </ErrorBoundary>
  );
} 