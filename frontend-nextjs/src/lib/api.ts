import { 
  User, 
  Violation, 
  ViolationCreate, 
  LoginCredentials, 
  AuthResponse, 
  SubscriptionPlan, 
  UserSubscription,
  DashboardMetrics,
  PaginatedResponse,
  ApiError 
} from '@/types';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';

class ApiClient {
  private baseURL: string;

  constructor(baseURL: string = API_BASE_URL) {
    this.baseURL = baseURL;
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseURL}${endpoint}`;
    
    const config: RequestInit = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    };

    // Add auth token if available
    const token = this.getToken();
    if (token) {
      config.headers = {
        ...config.headers,
        Authorization: `Bearer ${token}`,
      };
    }

    try {
      const response = await fetch(url, config);
      
      if (!response.ok) {
        const errorData: ApiError = await response.json();
        throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('API request failed:', error);
      throw error;
    }
  }

  private getToken(): string | null {
    if (typeof window !== 'undefined') {
      return localStorage.getItem('auth_token');
    }
    return null;
  }

  private setToken(token: string): void {
    if (typeof window !== 'undefined') {
      localStorage.setItem('auth_token', token);
    }
  }

  private removeToken(): void {
    if (typeof window !== 'undefined') {
      localStorage.removeItem('auth_token');
    }
  }

  // Authentication
  async login(credentials: LoginCredentials): Promise<AuthResponse> {
    const formData = new FormData();
    formData.append('username', credentials.username);
    formData.append('password', credentials.password);

    const response = await fetch(`${this.baseURL}/login`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      const errorData: ApiError = await response.json();
      throw new Error(errorData.detail || 'Login failed');
    }

    const data: AuthResponse = await response.json();
    this.setToken(data.access_token);
    return data;
  }

  async logout(): Promise<void> {
    this.removeToken();
  }

  async getCurrentUser(): Promise<User> {
    return this.request<User>('/me');
  }

  // Violations
  async getViolations(params?: {
    skip?: number;
    limit?: number;
    hoa_id?: number;
    tag?: string;
    status?: string;
  }): Promise<PaginatedResponse<Violation>> {
    const searchParams = new URLSearchParams();
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined) {
          searchParams.append(key, value.toString());
        }
      });
    }

    return this.request<PaginatedResponse<Violation>>(`/violations/?${searchParams}`);
  }

  async getViolation(id: number): Promise<Violation> {
    return this.request<Violation>(`/violations/${id}`);
  }

  async updateViolation(violationId: number, updates: Partial<Violation>): Promise<Violation> {
    return this.request<Violation>(`/violations/${violationId}`, {
      method: 'PUT',
      body: JSON.stringify(updates),
    });
  }

  async createViolation(violation: ViolationCreate): Promise<Violation> {
    const formData = new FormData();
    
    // Add text fields
    formData.append('description', violation.description);
    formData.append('hoa', violation.hoa);
    formData.append('address', violation.address);
    formData.append('location', violation.location);
    formData.append('offender', violation.offender);
    
    // Add optional fields
    if (violation.gps_coordinates) {
      formData.append('gps_coordinates', violation.gps_coordinates);
    }
    if (violation.violation_type) {
      formData.append('violation_type', violation.violation_type);
    }
    if (violation.file) {
      formData.append('file', violation.file);
    }
    if (violation.mobile_capture !== undefined) {
      formData.append('mobile_capture', violation.mobile_capture.toString());
    }
    if (violation.auto_gps !== undefined) {
      formData.append('auto_gps', violation.auto_gps.toString());
    }

    const response = await fetch(`${this.baseURL}/violations/`, {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${this.getToken()}`,
      },
      body: formData,
    });

    if (!response.ok) {
      const errorData: ApiError = await response.json();
      throw new Error(errorData.detail || 'Failed to create violation');
    }

    return response.json();
  }

  async updateViolationStatus(
    id: number,
    status: string,
    resolution_notes?: string,
    resolved_by?: string
  ): Promise<Violation> {
    const searchParams = new URLSearchParams();
    searchParams.append('new_status', status);
    if (resolution_notes) {
      searchParams.append('resolution_notes', resolution_notes);
    }
    if (resolved_by) {
      searchParams.append('resolved_by', resolved_by);
    }

    return this.request<Violation>(`/violations/${id}/status?${searchParams}`, {
      method: 'PUT',
    });
  }

  async deleteViolation(id: number): Promise<void> {
    return this.request<void>(`/violations/${id}`, {
      method: 'DELETE',
    });
  }

  // Dashboard Data
  async getDashboardData(params?: {
    skip?: number;
    limit?: number;
    hoa_id?: number;
    tag?: string;
    status?: string;
  }): Promise<{
    violations: Violation[];
    pagination: {
      total: number;
      pages: number;
      current_page: number;
      items_per_page: number;
    };
    accessible_hoas: any[];
  }> {
    const searchParams = new URLSearchParams();
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined) {
          searchParams.append(key, value.toString());
        }
      });
    }

    return this.request(`/violations/dashboard-data?${searchParams}`);
  }

  // Analytics
  async getDashboardMetrics(params?: {
    hoa_id?: number;
    start_date?: string;
    end_date?: string;
  }): Promise<DashboardMetrics> {
    const searchParams = new URLSearchParams();
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined) {
          searchParams.append(key, value.toString());
        }
      });
    }

    return this.request<DashboardMetrics>(`/analytics/dashboard-metrics?${searchParams}`);
  }

  // Billing
  async getSubscriptionPlans(): Promise<{ plans: SubscriptionPlan[] }> {
    try {
      const response = await this.request<{ plans: any; message: string }>('/billing/plans');
      
      // Transform the backend response to match frontend expectations
      const plansArray = Object.entries(response.plans || {}).map(([id, plan]: [string, any]) => ({
        id,
        name: plan.name,
        price: plan.price,
        currency: plan.currency,
        interval: plan.interval,
        features: plan.features || [],
        limits: {
          violations_per_month: plan.limits?.incidents_per_month || 0,
          users: plan.limits?.users || 0
        }
      }));
      
      return { plans: plansArray };
    } catch (error) {
      console.error('Error in getSubscriptionPlans:', error);
      // Return empty array as fallback
      return { plans: [] };
    }
  }

  async getUserSubscription(): Promise<UserSubscription> {
    const response = await this.request<{
      subscription: { status: string; plan_id: string };
      plan: any;
      features: string[];
      limits: any;
    }>('/billing/my-subscription');
    
    // Transform the backend response to match frontend expectations
    return {
      subscription_id: 'current',
      plan_id: response.subscription.plan_id,
      status: response.subscription.status,
      current_period_start: new Date().toISOString(),
      current_period_end: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString(),
      cancel_at_period_end: false,
      features: response.features,
      limits: {
        violations_per_month: response.limits.incidents_per_month,
        users: response.limits.users
      }
    };
  }

  async createCheckoutSession(planId: string, successUrl: string, cancelUrl: string): Promise<{ checkout_url: string }> {
    return this.request<{ checkout_url: string }>('/billing/create-checkout-session', {
      method: 'POST',
      body: JSON.stringify({
        plan_id: planId,
        success_url: successUrl,
        cancel_url: cancelUrl,
      }),
    });
  }

  async cancelSubscription(): Promise<{ message: string; cancel_at_period_end: boolean }> {
    return this.request<{ message: string; cancel_at_period_end: boolean }>('/billing/cancel-subscription', {
      method: 'POST',
    });
  }

  // User Management
  async getUsers(): Promise<User[]> {
    return this.request<User[]>('/admin/users');
  }

  async createUser(userData: {
    username: string;
    email: string;
    password: string;
    role: string;
    hoa_id?: number;
  }): Promise<User> {
    return this.request<User>('/admin/users', {
      method: 'POST',
      body: JSON.stringify(userData),
    });
  }

  async updateUser(userId: number, userData: {
    username?: string;
    email?: string;
    role?: string;
    hoa_id?: number;
  }): Promise<User> {
    return this.request<User>(`/admin/users/${userId}`, {
      method: 'PUT',
      body: JSON.stringify(userData),
    });
  }

  async deleteUser(userId: number): Promise<{ message: string }> {
    return this.request<{ message: string }>(`/admin/users/${userId}`, {
      method: 'DELETE',
    });
  }

  // Export
  async exportViolationsCSV(params?: {
    hoa_id?: number;
    tag?: string;
    status?: string;
  }): Promise<Blob> {
    const searchParams = new URLSearchParams();
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined) {
          searchParams.append(key, value.toString());
        }
      });
    }

    const response = await fetch(`${this.baseURL}/violations/export-csv?${searchParams}`, {
      headers: {
        Authorization: `Bearer ${this.getToken()}`,
      },
    });

    if (!response.ok) {
      throw new Error('Failed to export violations');
    }

    return response.blob();
  }

  // Settings
  async changePassword(currentPassword: string, newPassword: string): Promise<{ message: string }> {
    return this.request<{ message: string }>('/auth/change-password', {
      method: 'POST',
      body: JSON.stringify({
        current_password: currentPassword,
        new_password: newPassword,
      }),
    });
  }

  async updateNotificationPreferences(preferences: {
    email: boolean;
    push: boolean;
    violations: boolean;
    reports: boolean;
  }): Promise<{ message: string }> {
    return this.request<{ message: string }>('/user-settings/notifications', {
      method: 'PUT',
      body: JSON.stringify(preferences),
    });
  }

  async updateAppearanceSettings(settings: {
    theme: string;
    pwa_offline: boolean;
    pwa_app_switcher: boolean;
  }): Promise<{ message: string }> {
    return this.request<{ message: string }>('/user-settings/appearance', {
      method: 'PUT',
      body: JSON.stringify(settings),
    });
  }

  async exportUserData(): Promise<Blob> {
    const response = await fetch(`${this.baseURL}/user-settings/export-data`, {
      headers: {
        Authorization: `Bearer ${this.getToken()}`,
      },
    });

    if (!response.ok) {
      throw new Error('Failed to export user data');
    }

    return response.blob();
  }

  async getActiveSessions(): Promise<any[]> {
    return this.request<any[]>('/user-settings/active-sessions');
  }

  async revokeSession(sessionId: string): Promise<{ message: string }> {
    return this.request<{ message: string }>(`/user-settings/revoke-session/${sessionId}`, {
      method: 'DELETE',
    });
  }

  async getUserSettings(): Promise<{
    notifications: {
      email: boolean;
      push: boolean;
      violations: boolean;
      reports: boolean;
    };
    appearance: {
      theme: string;
      pwa_offline: boolean;
      pwa_app_switcher: boolean;
    };
    security: {
      two_factor_enabled: boolean;
    };
  }> {
    return this.request<{
      notifications: {
        email: boolean;
        push: boolean;
        violations: boolean;
        reports: boolean;
      };
      appearance: {
        theme: string;
        pwa_offline: boolean;
        pwa_app_switcher: boolean;
      };
      security: {
        two_factor_enabled: boolean;
      };
    }>('/user-settings/user-settings');
  }

  async get2FAStatus(): Promise<{ enabled: boolean }> {
    return this.request<{ enabled: boolean }>('/user-settings/2fa-status');
  }

  async enable2FA(): Promise<{ qr_code: string; secret: string }> {
    return this.request<{ qr_code: string; secret: string }>('/user-settings/enable-2fa', {
      method: 'POST',
    });
  }

  async disable2FA(): Promise<{ message: string }> {
    return this.request<{ message: string }>('/user-settings/disable-2fa', {
      method: 'DELETE',
    });
  }
}

export const apiClient = new ApiClient(); 