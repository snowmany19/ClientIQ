'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuthStore } from '@/lib/auth';
import PolicyUploadForm from '@/components/forms/PolicyUploadForm';

export default function PoliciesPage() {
  const { user } = useAuthStore();
  const router = useRouter();

  useEffect(() => {
    // Redirect residents to resident portal
    if (user?.role === 'resident') {
      router.push('/dashboard/resident-portal');
      return;
    }
    
    // Check if user has permission to access policy management
    if (user && user.role === 'inspector') {
      router.push('/dashboard');
      return;
    }
  }, [user, router]);

  // Check permissions
  if (user?.role === 'resident' || user?.role === 'inspector') {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="max-w-md w-full bg-white shadow-lg rounded-lg p-6">
          <div className="text-center">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">Access Denied</h2>
            <p className="text-gray-600 mb-6">
              Policy management is only available to HOA administrators and board members with Business-tier or higher subscriptions.
            </p>
            <button
              onClick={() => router.push('/dashboard')}
              className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 transition-colors"
            >
              Return to Dashboard
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-gray-900">Policy Management</h1>
            <p className="mt-2 text-gray-600">
              Upload and manage your HOA's policy documents to enable AI-powered violation analysis customized to your specific rules and regulations.
            </p>
          </div>
          <PolicyUploadForm />
        </div>
      </div>
    </div>
  );
} 