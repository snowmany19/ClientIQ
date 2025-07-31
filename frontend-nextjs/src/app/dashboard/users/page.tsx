'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuthStore } from '@/lib/auth';
import UserManagement from '@/components/admin/UserManagement';

export default function UsersPage() {
  const { user } = useAuthStore();
  const router = useRouter();

  console.log('UsersPage - Current user:', user);

  useEffect(() => {
    console.log('UsersPage useEffect - user:', user);
    
    // Redirect residents to resident portal
    if (user?.role === 'resident') {
      console.log('Redirecting resident to resident portal');
      router.push('/dashboard/resident-portal');
      return;
    }
    
    // Check if user has permission to access user management
    if (user && user.role === 'inspector') {
      console.log('Redirecting inspector to dashboard');
      router.push('/dashboard');
    }
  }, [user, router]);

  // Check permissions
  if (user?.role === 'resident' || user?.role === 'inspector') {
    console.log('Access denied for role:', user?.role);
    return (
      <div className="flex-1 overflow-auto p-6">
        <div className="max-w-7xl mx-auto">
          <div className="flex items-center justify-center h-64">
                      <div className="text-center">
            <h2 className="text-xl font-semibold text-gray-900 mb-2">Access Denied</h2>
            <p className="text-gray-600">
              {user?.role === 'resident' 
                ? 'Residents cannot access user management.' 
                : 'You don\'t have permission to access user management.'
              }
            </p>
          </div>
          </div>
        </div>
      </div>
    );
  }

  console.log('Rendering UserManagement component');
  return (
    <>
      {/* Header */}
      <div className="bg-white shadow flex-shrink-0">
        <div className="w-full px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <h1 className="text-xl font-semibold text-gray-900">
                User Management
              </h1>
            </div>
          </div>
        </div>
      </div>

      {/* Main content */}
      <div className="flex-1 overflow-auto p-6">
        <div className="max-w-7xl mx-auto">
          <UserManagement />
        </div>
      </div>
    </>
  );
} 