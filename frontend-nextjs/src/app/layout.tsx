import type { Metadata } from 'next';
import './globals.css';
import { ThemeProvider } from '@/components/ui/ThemeProvider';
import { PWAProvider } from '@/components/providers/PWAProvider';
import QueryProvider from '@/components/providers/QueryProvider';
import AuthInitializer from '@/components/providers/AuthInitializer';

export const metadata: Metadata = {
  title: 'ContractGuard.ai - AI Contract Review Platform',
  description: 'AI-powered contract review and analysis platform for legal teams and businesses',
  manifest: '/manifest.json',
  icons: {
    icon: '/icon-192x192.png',
    apple: '/icon-192x192.png',
  },
  viewport: 'width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no',
  themeColor: '#3b82f6',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className="antialiased">
        <QueryProvider>
          <ThemeProvider>
            <PWAProvider>
              <AuthInitializer />
              {children}
            </PWAProvider>
          </ThemeProvider>
        </QueryProvider>
      </body>
    </html>
  );
}
