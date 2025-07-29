'use client';

import { useEffect } from 'react';
import { 
  registerServiceWorker, 
  requestNotificationPermission, 
  setupInstallPrompt 
} from '@/lib/pwa';

interface PWAProviderProps {
  children: React.ReactNode;
}

export function PWAProvider({ children }: PWAProviderProps) {
  useEffect(() => {
    // Register service worker
    registerServiceWorker();
    
    // Setup install prompt
    setupInstallPrompt();
    
    // Request notification permission on first visit
    requestNotificationPermission();
  }, []);

  return <>{children}</>;
} 