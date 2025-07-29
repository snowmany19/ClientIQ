'use client';

import { useEffect, Suspense } from 'react';
import { useSearchParams } from 'next/navigation';
import { useAuthStore } from '@/lib/auth';
import BillingDashboard from '@/components/billing/BillingDashboard';
import { CheckCircle, XCircle } from 'lucide-react';

function BillingPageContent() {
  const { user } = useAuthStore();
  const searchParams = useSearchParams();
  const success = searchParams.get('success');
  const canceled = searchParams.get('canceled');

  return (
    <>
      {/* Header */}
      <div className="bg-white shadow flex-shrink-0">
        <div className="w-full px-4 sm:px-6 lg:px-8">
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
        <div className="w-full px-4 sm:px-6 lg:px-8 pt-6">
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
        <div className="w-full px-4 sm:px-6 lg:px-8 pt-6">
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
      <div className="flex-1 overflow-auto p-6">
        <div className="max-w-7xl mx-auto">
          <BillingDashboard />
        </div>
      </div>
    </>
  );
}

export default function BillingPage() {
  return (
    <Suspense fallback={
      <div className="flex-1 overflow-auto p-6">
        <div className="max-w-7xl mx-auto">
          <div className="flex items-center justify-center h-64">
            <div className="text-center">
              <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600 mx-auto"></div>
              <p className="mt-4 text-gray-600">Loading billing...</p>
            </div>
          </div>
        </div>
      </div>
    }>
      <BillingPageContent />
    </Suspense>
  );
} 