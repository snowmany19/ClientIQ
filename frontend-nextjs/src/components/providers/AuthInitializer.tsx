'use client';

import { useEffect, useState } from 'react';
import { useAuthStore } from '@/lib/auth';

export default function AuthInitializer() {
  const { initializeAuth, isAuthenticated, user } = useAuthStore();
  const [isInitialized, setIsInitialized] = useState(false);

  useEffect(() => {
    const initAuth = async () => {
      try {
        await initializeAuth();
      } catch (error) {
        console.error('Auth initialization failed:', error);
      } finally {
        setIsInitialized(true);
      }
    };

    // Wait a bit for Zustand to hydrate from localStorage
    const timer = setTimeout(initAuth, 100);
    return () => clearTimeout(timer);
  }, [initializeAuth]);

  // Don't render children until auth is initialized
  if (!isInitialized) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return null;
}
