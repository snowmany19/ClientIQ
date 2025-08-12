import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'
import { PWAProvider } from '@/components/providers/PWAProvider'
import { ThemeProvider } from '@/components/ui/ThemeProvider'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'ContractGuard.ai - AI Contract Review Platform',
  description: 'Professional AI-powered contract analysis and risk management platform',
  manifest: '/manifest.json',
  themeColor: '#1e293b',
  viewport: 'width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no',
  appleWebApp: {
    capable: true,
    statusBarStyle: 'default',
    title: 'ContractGuard.ai',
  },
  formatDetection: {
    telephone: false,
  },
  icons: {
    icon: [
      { url: '/icon-192x192.png', sizes: '192x192', type: 'image/png' },
      { url: '/icon-512x512.png', sizes: '512x512', type: 'image/png' },
    ],
    apple: [
      { url: '/icon-192x192.png', sizes: '192x192', type: 'image/png' },
    ],
  },
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <head>
        <meta name="application-name" content="ContractGuard.ai" />
        <meta name="apple-mobile-web-app-capable" content="yes" />
        <meta name="apple-mobile-web-app-status-bar-style" content="default" />
        <meta name="apple-mobile-web-app-title" content="ContractGuard.ai" />
        <meta name="description" content="Professional AI-powered contract analysis and risk management platform" />
        <meta name="format-detection" content="telephone=no" />
        <meta name="mobile-web-app-capable" content="yes" />
        <meta name="msapplication-config" content="/browserconfig.xml" />
        <meta name="msapplication-TileColor" content="#1e293b" />
        <meta name="msapplication-tap-highlight" content="no" />
        <meta name="theme-color" content="#1e293b" />

        <link rel="apple-touch-icon" href="/icon-192x192.png" />
        <link rel="icon" type="image/png" sizes="32x32" href="/icon-192x192.png" />
        <link rel="icon" type="image/png" sizes="16x16" href="/icon-192x192.png" />
        <link rel="manifest" href="/manifest.json" />
        <link rel="mask-icon" href="/icon-192x192.png" color="#1e293b" />
        <link rel="shortcut icon" href="/favicon.ico" />
      </head>
      <body className={inter.className}>
        <ThemeProvider>
          <PWAProvider>
            {children}
          </PWAProvider>
        </ThemeProvider>
      </body>
    </html>
  )
}
