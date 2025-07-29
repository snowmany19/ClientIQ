// PWA utilities for service worker registration and PWA features

export function registerServiceWorker() {
  if (typeof window !== 'undefined' && 'serviceWorker' in navigator) {
    window.addEventListener('load', () => {
      navigator.serviceWorker
        .register('/sw.js')
        .then((registration) => {
          console.log('SW registered: ', registration);
        })
        .catch((registrationError) => {
          console.log('SW registration failed: ', registrationError);
        });
    });
  }
}

export function requestNotificationPermission() {
  if (typeof window !== 'undefined' && 'Notification' in window) {
    if (Notification.permission === 'default') {
      Notification.requestPermission().then((permission) => {
        if (permission === 'granted') {
          console.log('Notification permission granted');
        }
      });
    }
  }
}

export function showNotification(title: string, options?: NotificationOptions) {
  if (typeof window !== 'undefined' && 'Notification' in window && Notification.permission === 'granted') {
    new Notification(title, options);
  }
}

export function isPWAInstalled(): boolean {
  if (typeof window === 'undefined') return false;
  
  // Check if running in standalone mode (installed PWA)
  return window.matchMedia('(display-mode: standalone)').matches ||
         (window.navigator as any).standalone === true;
}

export function showInstallPrompt() {
  if (typeof window === 'undefined') return;
  
  // Check if there's a deferred prompt
  const deferredPrompt = (window as any).deferredPrompt;
  if (deferredPrompt) {
    deferredPrompt.prompt();
    deferredPrompt.userChoice.then((choiceResult: any) => {
      if (choiceResult.outcome === 'accepted') {
        console.log('User accepted the install prompt');
      }
      (window as any).deferredPrompt = null;
    });
  } else {
    // Fallback: try to trigger the browser's install prompt
    console.log('No deferred prompt available, trying alternative method');
    
    // Check if the app is installable
    if (isPWAInstallable()) {
      // Show a custom install guide
      alert('To install CivicLogHOA:\n\n1. Look for the install icon in your browser address bar\n2. Or use the browser menu (⋮) and select "Install app"\n3. Or add to home screen from your browser menu');
    } else {
      alert('CivicLogHOA is not currently installable. Please try again later or use the browser menu to install.');
    }
  }
}

export function isPWAInstallable(): boolean {
  if (typeof window === 'undefined') return false;
  
  // Check if the app meets install criteria
  const hasManifest = !!document.querySelector('link[rel="manifest"]');
  const hasServiceWorker = 'serviceWorker' in navigator;
  const isHTTPS = window.location.protocol === 'https:' || window.location.hostname === 'localhost';
  
  return hasManifest && hasServiceWorker && isHTTPS;
}

// Listen for beforeinstallprompt event
export function setupInstallPrompt() {
  if (typeof window === 'undefined') return;
  
  window.addEventListener('beforeinstallprompt', (e) => {
    e.preventDefault();
    (window as any).deferredPrompt = e;
  });
} 