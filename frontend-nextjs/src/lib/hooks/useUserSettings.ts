import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '@/lib/api';

// Query keys for user settings
export const userSettingsKeys = {
  all: ['user-settings'] as const,
  settings: () => [...userSettingsKeys.all, 'settings'] as const,
  sessions: () => [...userSettingsKeys.all, 'sessions'] as const,
  twoFactor: () => [...userSettingsKeys.all, '2fa'] as const,
};

// Hook for fetching user settings
export function useUserSettings() {
  return useQuery({
    queryKey: userSettingsKeys.settings(),
    queryFn: async () => {
      return await apiClient.getUserSettings();
    },
    staleTime: 1000 * 60 * 10, // 10 minutes
  });
}

// Hook for updating notification preferences
export function useUpdateNotificationPreferences() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async (preferences: any) => {
      return await apiClient.updateNotificationPreferences(preferences);
    },
    onSuccess: () => {
      // Invalidate user settings to refetch
      queryClient.invalidateQueries({ queryKey: userSettingsKeys.settings() });
    },
  });
}

// Hook for updating appearance settings
export function useUpdateAppearanceSettings() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async (settings: any) => {
      return await apiClient.updateAppearanceSettings(settings);
    },
    onSuccess: () => {
      // Invalidate user settings to refetch
      queryClient.invalidateQueries({ queryKey: userSettingsKeys.settings() });
    },
  });
}

// Hook for fetching active sessions
export function useActiveSessions() {
  return useQuery({
    queryKey: userSettingsKeys.sessions(),
    queryFn: async () => {
      return await apiClient.getActiveSessions();
    },
    staleTime: 1000 * 60 * 2, // 2 minutes
  });
}

// Hook for revoking a session
export function useRevokeSession() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async (sessionId: string) => {
      return await apiClient.revokeSession(sessionId);
    },
    onSuccess: () => {
      // Invalidate active sessions to refetch
      queryClient.invalidateQueries({ queryKey: userSettingsKeys.sessions() });
    },
  });
}

// Hook for 2FA operations
export function useTwoFactor() {
  const queryClient = useQueryClient();
  
  const enable2FA = useMutation({
    mutationFn: async () => {
      return await apiClient.enable2FA();
    },
  });

  const verify2FA = useMutation({
    mutationFn: async (code: string) => {
      return await apiClient.verify2FA(code);
    },
    onSuccess: () => {
      // Invalidate user settings to refetch 2FA status
      queryClient.invalidateQueries({ queryKey: userSettingsKeys.settings() });
    },
  });

  const disable2FA = useMutation({
    mutationFn: async () => {
      return await apiClient.disable2FA();
    },
    onSuccess: () => {
      // Invalidate user settings to refetch 2FA status
      queryClient.invalidateQueries({ queryKey: userSettingsKeys.settings() });
    },
  });

  return {
    enable2FA,
    verify2FA,
    disable2FA,
  };
}
