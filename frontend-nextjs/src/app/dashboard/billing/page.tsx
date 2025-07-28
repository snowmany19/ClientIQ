'use client';

import { useEffect } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { useAuthStore } from '@/lib/auth';
import Sidebar from '@/components/layout/Sidebar';
import BillingDashboard from '@/components/billing/BillingDashboard';
import { CheckCircle, XCircle } from 'lucide-react';

export default function BillingPage() {
  const { user, isAuthenticated, getCurrentUser } = useAuthStore();
  const router = useRouter();
  const searchParams = useSearchParams();
  const success = searchParams.get('success');
  const canceled = searchParams.get('canceled');

  useEffect(() => {
    if (!isAuthenticated) {
      router.push('/');
      return;
    }

    if (!user) {
      getCurrentUser();
    }
  }, [isAuthenticated, user, router, getCurrentUser]);

  if (!isAuthenticated || !user) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
      </div>
    );
  }

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
                  Billing & Subscription
                </h1>
              </div>
              <div className="flex items-center space-x-4">
                <span className="text-sm text-gray-700">
                  Manage your subscription
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* Success/Cancel Messages */}
        {success && (
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-6">
            <div className="rounded-md bg-green-50 p-4">
              <div className="flex">
                <CheckCircle className="h-5 w-5 text-green-400" />
                <div className="ml-3">
                  <h3 className="text-sm font-medium text-green-800">
                    Payment Successful
                  </h3>
                  <div className="mt-2 text-sm text-green-700">
                    Your subscription has been updated successfully. You now have access to all premium features.
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {canceled && (
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-6">
            <div className="rounded-md bg-yellow-50 p-4">
              <div className="flex">
                <XCircle className="h-5 w-5 text-yellow-400" />
                <div className="ml-3">
                  <h3 className="text-sm font-medium text-yellow-800">
                    Payment Canceled
                  </h3>
                  <div className="mt-2 text-sm text-yellow-700">
                    Your payment was canceled. Your current subscription remains unchanged.
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Main content */}
        <div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
          <BillingDashboard />
        </div>
      </div>
    </div>
  );
} 