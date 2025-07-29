'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuthStore } from '@/lib/auth';
import Sidebar from '@/components/layout/Sidebar';

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const { user, isAuthenticated, getCurrentUser } = useAuthStore();
  const router = useRouter();

  useEffect(() => {
    if (!isAuthenticated) {
      router.push('/');
      return;
    }

    // Get current user data if not already loaded
    if (!user) {
      getCurrentUser();
    }
  }, [isAuthenticated, user, router, getCurrentUser]);

  // Don't render anything if not authenticated
  if (!isAuthenticated || !user) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading authentication...</p>
          <p className="text-sm text-gray-500">If this persists, please log in again</p>
        </div>
      </div>
    );
  }

  return (
    <div className="h-screen flex bg-gray-50">
      <Sidebar />
      <div className="flex-1 flex flex-col overflow-hidden">
        {children}
      </div>
    </div>
  );
} 