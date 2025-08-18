import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { User } from '@/types';
import { apiClient } from './api';

interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
}

interface AuthActions {
  login: (username: string, password: string) => Promise<void>;
  logout: () => void;
  getCurrentUser: () => Promise<void>;
  clearError: () => void;
  initializeAuth: () => Promise<void>;
}

type AuthStore = AuthState & AuthActions;

export const useAuthStore = create<AuthStore>()(
  persist(
    (set, get) => ({
      // State
      user: null,
      token: null,
      isAuthenticated: false,
      isLoading: false,
      error: null,

      // Actions
      login: async (username: string, password: string) => {
        console.log('🔐 Login attempt for:', username);
        set({ isLoading: true, error: null });
        
        try {
          const response = await apiClient.login({ username, password });
          console.log('✅ Login successful:', response);
          set({
            user: response.user,
            token: response.access_token,
            isAuthenticated: true,
            isLoading: false,
            error: null,
          });
          // Also store token in localStorage for API client compatibility
          if (typeof window !== 'undefined') {
            localStorage.setItem('auth_token', response.access_token);
            console.log('💾 Token stored in localStorage');
          }
          return response; // Return the response for the LoginForm
        } catch (error) {
          console.error('❌ Login failed:', error);
          set({
            isLoading: false,
            error: error instanceof Error ? error.message : 'Login failed',
          });
          throw error;
        }
      },

      logout: () => {
        apiClient.logout();
        // Also clear localStorage
        if (typeof window !== 'undefined') {
          localStorage.removeItem('auth_token');
        }
        set({
          user: null,
          token: null,
          isAuthenticated: false,
          isLoading: false,
          error: null,
        });
      },

      getCurrentUser: async () => {
        set({ isLoading: true });
        
        try {
          const user = await apiClient.getCurrentUser();
          set({
            user,
            isAuthenticated: true,
            isLoading: false,
            error: null,
          });
        } catch (error) {
          set({
            user: null,
            token: null,
            isAuthenticated: false,
            isLoading: false,
            error: error instanceof Error ? error.message : 'Failed to get user',
          });
        }
      },

      clearError: () => {
        set({ error: null });
      },

      initializeAuth: async () => {
        console.log('🚀 Initializing auth...');
        set({ isLoading: true }); // Set loading state at the beginning
        
        try {
          // Check if we have a token in localStorage
          if (typeof window !== 'undefined') {
            const token = localStorage.getItem('auth_token');
            console.log('🔍 Found token in localStorage:', token ? 'Yes' : 'No');
            
            if (token) {
              // If we have a token, assume user is authenticated
              // We'll validate it when making actual API calls
              console.log('✅ Token found, assuming authenticated');
              set({
                token,
                isAuthenticated: true,
                isLoading: false,
                error: null,
                // Don't set user yet - it will be fetched when needed
              });
            } else {
              console.log('📝 No token found, user not authenticated');
              set({ 
                isLoading: false,
                isAuthenticated: false,
                user: null,
                token: null,
                error: null
              });
            }
          }
          console.log('🏁 Auth initialization complete');
        } catch (error) {
          console.error('❌ Auth initialization failed:', error);
          // If initialization fails, set loading to false and clear auth state
          localStorage.removeItem('auth_token');
          set({
            user: null,
            token: null,
            isAuthenticated: false,
            isLoading: false,
            error: null,
          });
        }
      },
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({
        user: state.user,
        token: state.token,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
); 