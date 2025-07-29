'use client';

import { useEffect, useState } from 'react';
import { useAuthStore } from '@/lib/auth';
import { apiClient } from '@/lib/api';
import { Button } from '@/components/ui/Button';
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

export default function SettingsPage() {
  const { user } = useAuthStore();
  const [activeTab, setActiveTab] = useState('profile');
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);
  
  // Password change state
  const [passwordData, setPasswordData] = useState({
    currentPassword: '',
    newPassword: '',
    confirmPassword: '',
  });

  // Notification preferences
  const [notifications, setNotifications] = useState({
    email: true,
    push: true,
    violations: true,
    reports: true,
  });

  // Appearance settings
  const [theme, setTheme] = useState('light');
  const [pwaSettings, setPwaSettings] = useState({
    offline: true,
    appSwitcher: true,
  });

  // Security state
  const [activeSessions, setActiveSessions] = useState<any[]>([]);
  const [showSessions, setShowSessions] = useState(false);
  const [twoFactorEnabled, setTwoFactorEnabled] = useState(false);

  useEffect(() => {
    // Load initial data
    loadSettings();
  }, []);

  const loadSettings = async () => {
    try {
      setLoading(true);
      
      // Load user settings from backend
      const settings = await apiClient.getUserSettings();
      
      // Update state with actual settings
      setNotifications({
        email: settings.notifications.email,
        push: settings.notifications.push,
        violations: settings.notifications.violations,
        reports: settings.notifications.reports,
      });
      
      setTheme(settings.appearance.theme);
      setPwaSettings({
        offline: settings.appearance.pwa_offline,
        appSwitcher: settings.appearance.pwa_app_switcher,
      });
      
      setTwoFactorEnabled(settings.security.two_factor_enabled);
      
      // Load active sessions
      const sessions = await apiClient.getActiveSessions();
      setActiveSessions(sessions);
      
    } catch (error) {
      console.error('Failed to load settings:', error);
      showMessage('error', 'Failed to load settings');
    } finally {
      setLoading(false);
    }
  };

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
      setLoading(true);
      await apiClient.changePassword(passwordData.currentPassword, passwordData.newPassword);
      showMessage('success', 'Password updated successfully');
      setPasswordData({ currentPassword: '', newPassword: '', confirmPassword: '' });
    } catch (error) {
      showMessage('error', 'Failed to update password. Please check your current password.');
    } finally {
      setLoading(false);
    }
  };

  const handleNotificationSave = async () => {
    try {
      setLoading(true);
      await apiClient.updateNotificationPreferences(notifications);
      showMessage('success', 'Notification preferences saved');
    } catch (error) {
      showMessage('error', 'Failed to save notification preferences');
    } finally {
      setLoading(false);
    }
  };

  const handleAppearanceSave = async () => {
    try {
      setLoading(true);
      await apiClient.updateAppearanceSettings({
        theme,
        pwa_offline: pwaSettings.offline,
        pwa_app_switcher: pwaSettings.appSwitcher,
      });
      
      // Apply theme immediately
      applyTheme(theme);
      
      // Save to localStorage for persistence
      localStorage.setItem('theme', theme);
      localStorage.setItem('pwa_offline', pwaSettings.offline.toString());
      localStorage.setItem('pwa_app_switcher', pwaSettings.appSwitcher.toString());
      
      showMessage('success', 'Appearance settings saved');
    } catch (error) {
      showMessage('error', 'Failed to save appearance settings');
    } finally {
      setLoading(false);
    }
  };

  const applyTheme = (selectedTheme: string) => {
    const root = document.documentElement;
    
    // Remove existing theme classes
    root.classList.remove('light', 'dark');
    
    if (selectedTheme === 'dark') {
      root.classList.add('dark');
    } else if (selectedTheme === 'auto') {
      // Auto theme - use system preference
      if (window.matchMedia('(prefers-color-scheme: dark)').matches) {
        root.classList.add('dark');
      }
    }
    // For light theme, just remove dark class (default)
  };

  // Load saved theme on component mount
  useEffect(() => {
    const savedTheme = localStorage.getItem('theme') || 'light';
    const savedPwaOffline = localStorage.getItem('pwa_offline') === 'true';
    const savedPwaAppSwitcher = localStorage.getItem('pwa_app_switcher') === 'true';
    
    setTheme(savedTheme);
    setPwaSettings({
      offline: savedPwaOffline,
      appSwitcher: savedPwaAppSwitcher,
    });
    
    applyTheme(savedTheme);
  }, []);

  const handleExportData = async () => {
    try {
      setLoading(true);
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
    } finally {
      setLoading(false);
    }
  };

  const handleEnable2FA = async () => {
    try {
      setLoading(true);
      const result = await apiClient.enable2FA();
      setTwoFactorEnabled(true);
      showMessage('success', '2FA enabled successfully. Please scan the QR code with your authenticator app.');
      // In a real app, you'd show a modal with the QR code
      console.log('2FA QR Code:', result.qr_code);
    } catch (error) {
      showMessage('error', 'Failed to enable 2FA');
    } finally {
      setLoading(false);
    }
  };

  const handleDisable2FA = async () => {
    try {
      setLoading(true);
      await apiClient.disable2FA();
      setTwoFactorEnabled(false);
      showMessage('success', '2FA disabled successfully');
    } catch (error) {
      showMessage('error', 'Failed to disable 2FA');
    } finally {
      setLoading(false);
    }
  };

  const handleRevokeSession = async (sessionId: string) => {
    try {
      await apiClient.revokeSession(sessionId);
      setActiveSessions(prev => prev.filter(session => session.id !== sessionId));
      showMessage('success', 'Session revoked successfully');
    } catch (error) {
      showMessage('error', 'Failed to revoke session');
    }
  };

  const tabs = [
    { id: 'profile', name: 'Profile', icon: User },
    { id: 'notifications', name: 'Notifications', icon: Bell },
    { id: 'security', name: 'Security', icon: Shield },
    { id: 'appearance', name: 'Appearance', icon: Palette },
  ];

  const renderProfileTab = () => (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-medium text-gray-900 mb-4">Profile Information</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Username
            </label>
            <input
              type="text"
              value={user?.username || ''}
              disabled
              className="w-full px-3 py-2 border border-gray-300 rounded-md bg-gray-50 text-gray-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Email
            </label>
            <input
              type="email"
              value={user?.email || ''}
              disabled
              className="w-full px-3 py-2 border border-gray-300 rounded-md bg-gray-50 text-gray-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Role
            </label>
            <input
              type="text"
              value={user?.role || ''}
              disabled
              className="w-full px-3 py-2 border border-gray-300 rounded-md bg-gray-50 text-gray-500 capitalize"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Subscription Status
            </label>
            <input
              type="text"
              value={user?.subscription_status || 'Active'}
              disabled
              className="w-full px-3 py-2 border border-gray-300 rounded-md bg-gray-50 text-gray-500 capitalize"
            />
          </div>
        </div>
      </div>

      <div>
        <h3 className="text-lg font-medium text-gray-900 mb-4">Change Password</h3>
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Current Password
            </label>
            <div className="relative">
              <input
                type={showPassword ? 'text' : 'password'}
                value={passwordData.currentPassword}
                onChange={(e) => setPasswordData(prev => ({ ...prev, currentPassword: e.target.value }))}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500 pr-10"
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
            <label className="block text-sm font-medium text-gray-700 mb-2">
              New Password
            </label>
            <input
              type="password"
              value={passwordData.newPassword}
              onChange={(e) => setPasswordData(prev => ({ ...prev, newPassword: e.target.value }))}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
              placeholder="Enter new password"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Confirm New Password
            </label>
            <input
              type="password"
              value={passwordData.confirmPassword}
              onChange={(e) => setPasswordData(prev => ({ ...prev, confirmPassword: e.target.value }))}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
              placeholder="Confirm new password"
            />
          </div>
          <Button onClick={handlePasswordChange} disabled={loading}>
            <Save className="h-4 w-4 mr-2" />
            {loading ? 'Updating...' : 'Update Password'}
          </Button>
        </div>
      </div>
    </div>
  );

  const renderNotificationsTab = () => (
    <div className="space-y-6">
      <h3 className="text-lg font-medium text-gray-900 mb-4">Notification Preferences</h3>
      
      <div className="space-y-4">
        <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
          <div>
            <h4 className="text-sm font-medium text-gray-900">Email Notifications</h4>
            <p className="text-sm text-gray-500">Receive notifications via email</p>
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
            <h4 className="text-sm font-medium text-gray-900">Push Notifications</h4>
            <p className="text-sm text-gray-500">Receive push notifications in browser</p>
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
            <h4 className="text-sm font-medium text-gray-900">Violation Alerts</h4>
            <p className="text-sm text-gray-500">Get notified about new violations</p>
          </div>
          <label className="relative inline-flex items-center cursor-pointer">
            <input
              type="checkbox"
              checked={notifications.violations}
              onChange={(e) => setNotifications(prev => ({ ...prev, violations: e.target.checked }))}
              className="sr-only peer"
            />
            <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
          </label>
        </div>

        <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
          <div>
            <h4 className="text-sm font-medium text-gray-900">Report Notifications</h4>
            <p className="text-sm text-gray-500">Get notified about monthly reports</p>
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

      <Button onClick={handleNotificationSave} disabled={loading}>
        <Save className="h-4 w-4 mr-2" />
        {loading ? 'Saving...' : 'Save Preferences'}
      </Button>
    </div>
  );

  const renderSecurityTab = () => (
    <div className="space-y-6">
      <h3 className="text-lg font-medium text-gray-900 mb-4">Security Settings</h3>
      
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
            disabled={loading}
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
              {activeSessions.map((session) => (
                <div key={session.id} className="flex items-center justify-between p-3 bg-white rounded border">
                  <div>
                    <p className="text-sm font-medium">{session.device}</p>
                    <p className="text-xs text-gray-500">{session.location} • {session.last_activity}</p>
                  </div>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => handleRevokeSession(session.id)}
                    className="text-red-600 hover:text-red-700"
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
            disabled={loading}
          >
            <Download className="h-4 w-4 mr-2" />
            {loading ? 'Exporting...' : 'Export Data'}
          </Button>
        </div>
      </div>
    </div>
  );

  const renderAppearanceTab = () => (
    <div className="space-y-6">
      <h3 className="text-lg font-medium text-gray-900 mb-4">Appearance Settings</h3>
      
      <div className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Theme
          </label>
          <select
            value={theme}
            onChange={(e) => setTheme(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
          >
            <option value="light">Light</option>
            <option value="dark">Dark</option>
            <option value="auto">Auto (System)</option>
          </select>
        </div>

        <div className="p-4 bg-gray-50 rounded-lg">
          <h4 className="text-sm font-medium text-gray-900 mb-2">PWA Settings</h4>
          <p className="text-sm text-gray-500 mb-3">Manage Progressive Web App features</p>
          <div className="space-y-2">
            <label className="flex items-center">
              <input 
                type="checkbox" 
                checked={pwaSettings.offline}
                onChange={(e) => setPwaSettings(prev => ({ ...prev, offline: e.target.checked }))}
                className="rounded border-gray-300 text-blue-600 focus:ring-blue-500" 
              />
              <span className="ml-2 text-sm text-gray-700">Enable offline mode</span>
            </label>
            <label className="flex items-center">
              <input 
                type="checkbox" 
                checked={pwaSettings.appSwitcher}
                onChange={(e) => setPwaSettings(prev => ({ ...prev, appSwitcher: e.target.checked }))}
                className="rounded border-gray-300 text-blue-600 focus:ring-blue-500" 
              />
              <span className="ml-2 text-sm text-gray-700">Show app in app switcher</span>
            </label>
          </div>
        </div>
      </div>

      <Button onClick={handleAppearanceSave} disabled={loading}>
        <Save className="h-4 w-4 mr-2" />
        {loading ? 'Saving...' : 'Save Settings'}
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
    </>
  );
} 