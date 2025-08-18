'use client';

import { useState, useEffect } from 'react';
import { useAuthStore } from '@/lib/auth';
import { apiClient } from '@/lib/api';
import { Button } from '@/components/ui/Button';
import { TwoFactorModal } from '@/components/ui/TwoFactorModal';
import { useTheme } from '@/components/ui/ThemeProvider';
import { useUserSettings, useActiveSessions, useRevokeSession, useTwoFactor, useUpdateNotificationPreferences, useUpdateAppearanceSettings } from '@/lib/hooks';
import { 
  User, 
  Bell, 
  Shield, 
  Palette,
  Download,
  Trash2,
  Save,
  Eye,
  EyeOff,
  AlertCircle,
  CheckCircle
} from 'lucide-react';
import { showInstallPrompt, isPWAInstallable, isPWAInstalled } from '@/lib/pwa';

export default function SettingsPage() {
  const { user } = useAuthStore();
  const { theme, setTheme } = useTheme();
  const [activeTab, setActiveTab] = useState('profile');
  const [showPassword, setShowPassword] = useState(false);
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);
  
  // 2FA state
  const [show2FAModal, setShow2FAModal] = useState(false);
  const [twoFactorData, setTwoFactorData] = useState<{ qr_code: string; secret: string } | null>(null);
  
  // Password change state
  const [passwordData, setPasswordData] = useState({
    currentPassword: '',
    newPassword: '',
    confirmPassword: '',
  });

  // Security state
  const [showSessions, setShowSessions] = useState(false);

  // Use React Query hooks for better performance
  const { data: settings, isLoading: settingsLoading } = useUserSettings();
  const { data: activeSessions = [], isLoading: sessionsLoading } = useActiveSessions();
  const { data: twoFactorStatus } = useUserSettings();
  
  const updateNotificationPreferences = useUpdateNotificationPreferences();
  const updateAppearanceSettings = useUpdateAppearanceSettings();
  const revokeSessionMutation = useRevokeSession();
  const { enable2FA, verify2FA, disable2FA } = useTwoFactor();

  // Initialize state from settings
  const [notifications, setNotifications] = useState({
    email: true,
    push: true,
    contracts: true,
    reports: true,
  });

  const [pwaSettings, setPwaSettings] = useState({
    offline: true,
    appSwitcher: true,
  });

  const [twoFactorEnabled, setTwoFactorEnabled] = useState(false);

  // Update state when settings load
  useEffect(() => {
    if (settings) {
      setNotifications({
        email: settings.notifications?.email ?? true,
        push: settings.notifications?.push ?? true,
        contracts: settings.notifications?.contracts ?? true,
        reports: settings.notifications?.reports ?? true,
      });
      
      setPwaSettings({
        offline: settings.appearance?.pwa_offline ?? true,
        appSwitcher: settings.appearance?.pwa_app_switcher ?? true,
      });
      
      setTwoFactorEnabled(settings.security?.two_factor_enabled ?? false);
    }
  }, [settings]);

  const showMessage = (type: 'success' | 'error', text: string) => {
    setMessage({ type, text });
    setTimeout(() => setMessage(null), 5000);
  };

  const handlePasswordChange = async () => {
    if (passwordData.newPassword !== passwordData.confirmPassword) {
      showMessage('error', 'New passwords do not match');
      return;
    }

    if (passwordData.newPassword.length < 8) {
      showMessage('error', 'New password must be at least 8 characters long');
      return;
    }

    try {
      await apiClient.changePassword(passwordData.currentPassword, passwordData.newPassword);
      showMessage('success', 'Password updated successfully');
      setPasswordData({ currentPassword: '', newPassword: '', confirmPassword: '' });
    } catch (error) {
      showMessage('error', 'Failed to update password. Please check your current password.');
    }
  };

  const handleNotificationSave = async () => {
    try {
      await updateNotificationPreferences.mutateAsync(notifications);
      showMessage('success', 'Notification preferences saved');
    } catch (error) {
      showMessage('error', 'Failed to save notification preferences');
    }
  };

  const handleAppearanceSave = async () => {
    try {
      await updateAppearanceSettings.mutateAsync({
        theme,
        pwa_offline: pwaSettings.offline,
        pwa_app_switcher: pwaSettings.appSwitcher,
      });
      
      // Save to localStorage for persistence
      localStorage.setItem('pwa_offline', pwaSettings.offline.toString());
      localStorage.setItem('pwa_app_switcher', pwaSettings.appSwitcher.toString());
      
      showMessage('success', 'Appearance settings saved');
    } catch (error) {
      showMessage('error', 'Failed to save appearance settings');
    }
  };

  const handleExportData = async () => {
    try {
      const blob = await apiClient.exportUserData();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `user_data_${new Date().toISOString().split('T')[0]}.json`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
      showMessage('success', 'Data exported successfully');
    } catch (error) {
      showMessage('error', 'Failed to export data');
    }
  };

  const handleEnable2FA = async () => {
    try {
      const result = await enable2FA.mutateAsync();
      setTwoFactorData(result);
      setShow2FAModal(true);
    } catch (error) {
      showMessage('error', 'Failed to enable 2FA');
    }
  };

  const handleVerify2FA = async (code: string): Promise<boolean> => {
    try {
      const result = await verify2FA.mutateAsync(code);
      if (result.enabled) {
        setTwoFactorEnabled(true);
        setShow2FAModal(false);
        setTwoFactorData(null);
        showMessage('success', '2FA enabled successfully!');
        return true;
      }
      return false;
    } catch (error) {
      return false;
    }
  };

  const handleDisable2FA = async () => {
    try {
      await disable2FA.mutateAsync();
      setTwoFactorEnabled(false);
      showMessage('success', '2FA disabled successfully');
    } catch (error) {
      showMessage('error', 'Failed to disable 2FA');
    }
  };

  const handleRevokeSession = async (sessionId: string) => {
    try {
      await revokeSessionMutation.mutateAsync(sessionId);
      showMessage('success', 'Session revoked successfully');
    } catch (error) {
      showMessage('error', 'Failed to revoke session');
    }
  };

  if (settingsLoading) {
    return (
      <div className="flex-1 overflow-auto p-6">
        <div className="max-w-7xl mx-auto">
          <div className="flex items-center justify-center h-64">
            <div className="text-center">
              <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600 mx-auto"></div>
              <p className="mt-4 text-gray-600 dark:text-gray-400">Loading settings...</p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  const tabs = [
    { id: 'profile', name: 'Profile', icon: User },
    { id: 'notifications', name: 'Notifications', icon: Bell },
    { id: 'security', name: 'Security', icon: Shield },
    { id: 'appearance', name: 'Appearance', icon: Palette },
  ];

  const renderProfileTab = () => (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Profile Information</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label className="block text-sm font-semibold text-gray-900 mb-2">
              Username
            </label>
            <input
              type="text"
              value={user?.username || ''}
              disabled
              className="w-full px-3 py-2 border border-gray-300 rounded-md bg-gray-50 text-gray-700 font-medium"
            />
          </div>
          <div>
            <label className="block text-sm font-semibold text-gray-900 mb-2">
              Email
            </label>
            <input
              type="email"
              value={user?.email || ''}
              disabled
              className="w-full px-3 py-2 border border-gray-300 rounded-md bg-gray-50 text-gray-700 font-medium"
            />
          </div>
          <div>
            <label className="block text-sm font-semibold text-gray-900 mb-2">
              Role
            </label>
            <input
              type="text"
              value={user?.role || ''}
              disabled
              className="w-full px-3 py-2 border border-gray-300 rounded-md bg-gray-50 text-gray-700 font-medium capitalize"
            />
          </div>
          <div>
            <label className="block text-sm font-semibold text-gray-900 mb-2">
              Subscription Status
            </label>
            <input
              type="text"
              value={user?.subscription_status || 'Active'}
              disabled
              className="w-full px-3 py-2 border border-gray-300 rounded-md bg-gray-50 text-gray-700 font-medium capitalize"
            />
          </div>
        </div>
      </div>

      <div>
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Change Password</h3>
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-semibold text-gray-900 mb-2">
              Current Password
            </label>
            <div className="relative">
              <input
                type={showPassword ? 'text' : 'password'}
                value={passwordData.currentPassword}
                onChange={(e) => setPasswordData(prev => ({ ...prev, currentPassword: e.target.value }))}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500 pr-10 text-gray-900 bg-white"
                placeholder="Enter current password"
              />
              <button
                type="button"
                className="absolute inset-y-0 right-0 pr-3 flex items-center"
                onClick={() => setShowPassword(!showPassword)}
              >
                {showPassword ? (
                  <EyeOff className="h-5 w-5 text-gray-400" />
                ) : (
                  <Eye className="h-5 w-5 text-gray-400" />
                )}
              </button>
            </div>
          </div>
          <div>
            <label className="block text-sm font-semibold text-gray-900 mb-2">
              New Password
            </label>
            <input
              type="password"
              value={passwordData.newPassword}
              onChange={(e) => setPasswordData(prev => ({ ...prev, newPassword: e.target.value }))}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500 text-gray-900 bg-white"
              placeholder="Enter new password"
            />
          </div>
          <div>
            <label className="block text-sm font-semibold text-gray-900 mb-2">
              Confirm New Password
            </label>
            <input
              type="password"
              value={passwordData.confirmPassword}
              onChange={(e) => setPasswordData(prev => ({ ...prev, confirmPassword: e.target.value }))}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500 text-gray-900 bg-white"
              placeholder="Confirm new password"
            />
          </div>
          <Button onClick={handlePasswordChange}>
            <Save className="h-4 w-4 mr-2" />
            Update Password
          </Button>
        </div>
      </div>
    </div>
  );

  const renderNotificationsTab = () => (
    <div className="space-y-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">Notification Preferences</h3>
      
      <div className="space-y-4">
        <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
          <div>
            <h4 className="text-sm font-semibold text-gray-900">Email Notifications</h4>
            <p className="text-sm text-gray-700 font-medium">Receive notifications via email</p>
          </div>
          <label className="relative inline-flex items-center cursor-pointer">
            <input
              type="checkbox"
              checked={notifications.email}
              onChange={(e) => setNotifications(prev => ({ ...prev, email: e.target.checked }))}
              className="sr-only peer"
            />
            <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
          </label>
        </div>

        <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
          <div>
            <h4 className="text-sm font-semibold text-gray-900">Push Notifications</h4>
            <p className="text-sm text-gray-700 font-medium">Receive push notifications in browser</p>
          </div>
          <label className="relative inline-flex items-center cursor-pointer">
            <input
              type="checkbox"
              checked={notifications.push}
              onChange={(e) => setNotifications(prev => ({ ...prev, push: e.target.checked }))}
              className="sr-only peer"
            />
            <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
          </label>
        </div>

        <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
          <div>
            <h4 className="text-sm font-semibold text-gray-900">Contract Alerts</h4>
            <p className="text-sm text-gray-700 font-medium">Get notified about new contracts and analysis completion</p>
          </div>
          <label className="relative inline-flex items-center cursor-pointer">
            <input
              type="checkbox"
              checked={notifications.contracts}
              onChange={(e) => setNotifications(prev => ({ ...prev, contracts: e.target.checked }))}
              className="sr-only peer"
            />
            <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
          </label>
        </div>

        <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
          <div>
            <h4 className="text-sm font-semibold text-gray-900">Report Notifications</h4>
            <p className="text-sm text-gray-700 font-medium">Get notified about monthly reports</p>
          </div>
          <label className="relative inline-flex items-center cursor-pointer">
            <input
              type="checkbox"
              checked={notifications.reports}
              onChange={(e) => setNotifications(prev => ({ ...prev, reports: e.target.checked }))}
              className="sr-only peer"
            />
            <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
          </label>
        </div>
      </div>

      <Button onClick={handleNotificationSave} disabled={updateNotificationPreferences.isPending}>
        <Save className="h-4 w-4 mr-2" />
        {updateNotificationPreferences.isPending ? 'Saving...' : 'Save Preferences'}
      </Button>
    </div>
  );

  const renderSecurityTab = () => (
    <div className="space-y-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">Security Settings</h3>
      
      <div className="space-y-4">
        <div className="p-4 bg-gray-50 rounded-lg">
          <div className="flex items-center justify-between mb-3">
            <div>
              <h4 className="text-sm font-medium text-gray-900">Two-Factor Authentication</h4>
              <p className="text-sm text-gray-500">Add an extra layer of security to your account</p>
            </div>
            <div className="flex items-center">
              {twoFactorEnabled ? (
                <CheckCircle className="h-5 w-5 text-green-500 mr-2" />
              ) : (
                <AlertCircle className="h-5 w-5 text-yellow-500 mr-2" />
              )}
              <span className="text-sm text-gray-600">
                {twoFactorEnabled ? 'Enabled' : 'Disabled'}
              </span>
            </div>
          </div>
          <Button 
            variant="outline" 
            onClick={twoFactorEnabled ? handleDisable2FA : handleEnable2FA}
            disabled={enable2FA.isPending || disable2FA.isPending}
          >
            {twoFactorEnabled ? 'Disable 2FA' : 'Enable 2FA'}
          </Button>
        </div>

        <div className="p-4 bg-gray-50 rounded-lg">
          <h4 className="text-sm font-medium text-gray-900 mb-2">Active Sessions</h4>
          <p className="text-sm text-gray-500 mb-3">Manage your active login sessions</p>
          <Button 
            variant="outline" 
            onClick={() => setShowSessions(!showSessions)}
          >
            {showSessions ? 'Hide Sessions' : 'View Sessions'}
          </Button>
          
          {showSessions && (
            <div className="mt-4 space-y-2">
              {activeSessions.map((session: any) => (
                <div key={session.id} className="flex items-center justify-between p-3 bg-white dark:bg-gray-800 rounded border border-gray-200 dark:border-gray-700">
                  <div>
                    <p className="text-sm font-medium text-gray-900 dark:text-gray-100">{session.device}</p>
                    <p className="text-xs text-gray-500 dark:text-gray-400">{session.location} • {session.last_activity}</p>
                  </div>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => handleRevokeSession(session.id)}
                    className="text-red-600 hover:text-red-700 dark:text-red-500 dark:hover:text-red-400"
                  >
                    <Trash2 className="h-4 w-4" />
                  </Button>
                </div>
              ))}
            </div>
          )}
        </div>

        <div className="p-4 bg-gray-50 rounded-lg">
          <h4 className="text-sm font-medium text-gray-900 mb-2">Export Data</h4>
          <p className="text-sm text-gray-500 mb-3">Download a copy of your data</p>
          <Button 
            variant="outline" 
            onClick={handleExportData}
          >
            <Download className="h-4 w-4 mr-2" />
            Export Data
          </Button>
        </div>
      </div>
    </div>
  );

  const renderAppearanceTab = () => (
    <div className="space-y-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">Appearance Settings</h3>
      
      <div className="space-y-4">
        <div>
          <label className="block text-sm font-semibold text-gray-900 mb-2">
            Theme
          </label>
          <select
            value={theme}
            onChange={(e) => setTheme(e.target.value as 'light' | 'dark' | 'auto')}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500 text-gray-900 bg-white"
          >
            <option value="light">Light</option>
            <option value="dark">Dark</option>
            <option value="auto">Auto (System)</option>
          </select>
        </div>

        <div className="p-4 bg-gray-50 rounded-lg">
          <h4 className="text-sm font-semibold text-gray-900 mb-2">PWA Settings</h4>
          <p className="text-sm text-gray-700 font-medium mb-3">Manage Progressive Web App features</p>
          <div className="space-y-4">
            <div className="space-y-2">
              <label className="flex items-center">
                <input 
                  type="checkbox" 
                  checked={pwaSettings.offline}
                  onChange={(e) => setPwaSettings(prev => ({ ...prev, offline: e.target.checked }))}
                  className="rounded border-gray-300 text-blue-600 focus:ring-blue-500" 
                />
                <span className="ml-2 text-sm text-gray-900 font-medium">Enable offline mode</span>
              </label>
              <label className="flex items-center">
                <input 
                  type="checkbox" 
                  checked={pwaSettings.appSwitcher}
                  onChange={(e) => setPwaSettings(prev => ({ ...prev, appSwitcher: e.target.checked }))}
                  className="rounded border-gray-300 text-blue-600 focus:ring-blue-500" 
                />
                <span className="ml-2 text-sm text-gray-900 font-medium">Show app in app switcher</span>
              </label>
            </div>
            
            <div className="pt-3 border-t border-gray-200">
              <h5 className="text-sm font-semibold text-gray-900 mb-2">Install App</h5>
                              <p className="text-sm text-gray-700 font-medium mb-3">Install ContractGuard.ai as a mobile app for better experience</p>
              
              <div className="space-y-3">
                <Button 
                  onClick={showInstallPrompt}
                  variant="outline"
                  className="w-full"
                  disabled={!isPWAInstallable()}
                >
                  <Download className="h-4 w-4 mr-2" />
                  Install ContractGuard.ai App
                </Button>
                
                <div className="text-xs text-gray-500 space-y-1">
                  <p>This will add the app to your home screen for quick access</p>
                  {!isPWAInstallable() && (
                    <p className="text-yellow-600">
                      ⚠️ App installation requires HTTPS or localhost
                    </p>
                  )}
                  {isPWAInstalled() && (
                    <p className="text-green-600">
                      ✅ App is already installed
                    </p>
                  )}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <Button onClick={handleAppearanceSave} disabled={updateAppearanceSettings.isPending}>
        <Save className="h-4 w-4 mr-2" />
        {updateAppearanceSettings.isPending ? 'Saving...' : 'Save Settings'}
      </Button>
    </div>
  );

  const renderTabContent = () => {
    switch (activeTab) {
      case 'profile':
        return renderProfileTab();
      case 'notifications':
        return renderNotificationsTab();
      case 'security':
        return renderSecurityTab();
      case 'appearance':
        return renderAppearanceTab();
      default:
        return renderProfileTab();
    }
  };

  return (
    <>
      {/* Header */}
      <div className="bg-white shadow flex-shrink-0">
        <div className="w-full px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <h1 className="text-xl font-semibold text-gray-900">Settings</h1>
            </div>
          </div>
        </div>
      </div>
      
      {/* Main content */}
      <div className="flex-1 overflow-auto p-6">
        <div className="max-w-7xl mx-auto">
          {message && (
            <div className={`mb-4 p-4 rounded-md ${
              message.type === 'success'
                ? 'bg-green-50 border border-green-200 text-green-800'
                : 'bg-red-50 border border-red-200 text-red-800'
            }`}>
              <div className="flex">
                <div className="flex-shrink-0">
                  {message.type === 'success' ? (
                    <CheckCircle className="h-5 w-5 text-green-400" />
                  ) : (
                    <AlertCircle className="h-5 w-5 text-red-400" />
                  )}
                </div>
                <div className="ml-3">
                  <p className="text-sm font-medium">{message.text}</p>
                </div>
              </div>
            </div>
          )}
          <div className="bg-white shadow rounded-lg">
            {/* Tabs */}
            <div className="border-b border-gray-200">
              <nav className="-mb-px flex space-x-8 px-6">
                {tabs.map((tab) => {
                  const Icon = tab.icon;
                  return (
                    <button
                      key={tab.id}
                      onClick={() => setActiveTab(tab.id)}
                      className={`py-4 px-1 border-b-2 font-medium text-sm flex items-center ${
                        activeTab === tab.id
                          ? 'border-blue-500 text-blue-600'
                          : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                      }`}
                    >
                      <Icon className="h-4 w-4 mr-2" />
                      {tab.name}
                    </button>
                  );
                })}
              </nav>
            </div>
            {/* Tab content */}
            <div className="p-6">
              {renderTabContent()}
            </div>
          </div>
        </div>
      </div>

      {/* 2FA Modal */}
      {twoFactorData && (
        <TwoFactorModal
          isOpen={show2FAModal}
          onClose={() => {
            setShow2FAModal(false);
            setTwoFactorData(null);
          }}
          qrCode={twoFactorData.qr_code}
          secret={twoFactorData.secret}
          onVerify={handleVerify2FA}
        />
      )}
    </>
  );
} 