'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuthStore } from '@/lib/auth';
import Sidebar from '@/components/layout/Sidebar';
import ViolationForm from '@/components/forms/ViolationForm';

export default function NewViolationPage() {
  const { user, isAuthenticated, getCurrentUser } = useAuthStore();
  const router = useRouter();

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

  const handleCancel = () => {
    router.push('/dashboard/violations');
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <Sidebar />
      
      <div className="lg:pl-64">
        <ViolationForm onCancel={handleCancel} />
      </div>
    </div>
  );
} 