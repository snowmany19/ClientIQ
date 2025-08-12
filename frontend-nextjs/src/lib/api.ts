// frontend-nextjs/src/lib/api.ts
// API client for ContractGuard.ai - AI Contract Review Platform

import { 
  User, 
  ContractRecord, 
  ContractCreate, 
  Workspace,
  LoginCredentials, 
  AuthResponse, 
  SubscriptionPlan, 
  UserSubscription, 
  DashboardMetrics, 
  PaginatedResponse, 
  ApiError 
} from '@/types';

const API_BASE_URL = (typeof window !== 'undefined' && (window as any).ENV?.NEXT_PUBLIC_API_URL) || 'http://localhost:8000';

class ApiClient {
  private baseURL: string;
  private token: string | null = null;

  constructor(baseURL: string = API_BASE_URL) {
    this.baseURL = baseURL;
    // Try to get token from localStorage on initialization
    if (typeof window !== 'undefined') {
      this.token = localStorage.getItem('access_token');
    }
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {},
    retries: number = 3
  ): Promise<T> {
    const url = `${this.baseURL}${endpoint}`;
    
    const config: RequestInit = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    };

    // Add authorization header if token exists
    if (this.token) {
      config.headers = {
        ...config.headers,
        Authorization: `Bearer ${this.token}`,
      };
    }

    try {
      const response = await fetch(url, config);
      
      if (response.status === 401) {
        // Token expired or invalid
        this.removeToken();
        window.location.href = '/login';
        throw new Error('Authentication required');
      }

      if (!response.ok) {
        const errorData: ApiError = await response.json();
        throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
      }

      // Handle empty responses
      const contentType = response.headers.get('content-type');
      if (contentType && contentType.includes('application/json')) {
        return await response.json();
      }
      
      return {} as T;
    } catch (error: any) {
      if (retries > 0 && error.name === 'TypeError') {
        // Network error, retry
        await new Promise(resolve => setTimeout(resolve, 1000));
        return this.request<T>(endpoint, options, retries - 1);
      }
      throw error;
    }
  }

  private getToken(): string | null {
    return this.token || localStorage.getItem('access_token');
  }

  private setToken(token: string): void {
    this.token = token;
    localStorage.setItem('access_token', token);
  }

  private removeToken(): void {
    this.token = null;
    localStorage.removeItem('access_token');
  }

  // ===========================
  // 🔐 Authentication Methods
  // ===========================

  async login(credentials: LoginCredentials): Promise<AuthResponse> {
    // Convert credentials to form data since backend expects OAuth2PasswordRequestForm
    const formData = new URLSearchParams();
    formData.append('username', credentials.username);
    formData.append('password', credentials.password);
    
    const response = await this.request<AuthResponse>('/api/login', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: formData.toString(),
    });
    
    if (response.access_token) {
      this.setToken(response.access_token);
    }
    
    return response;
  }

  async logout(): Promise<void> {
    // Backend doesn't have a logout endpoint, just clear local state
    this.removeToken();
  }

  async getCurrentUser(): Promise<User> {
    return this.request<User>('/api/me');
  }

  // ===========================
  // 📄 Contract Management
  // ===========================

  async getContracts(params?: {
    skip?: number;
    limit?: number;
    category?: string;
    status?: string;
    search?: string;
  }): Promise<PaginatedResponse<ContractRecord>> {
    const searchParams = new URLSearchParams();
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined) {
          searchParams.append(key, value.toString());
        }
      });
    }

    return this.request<PaginatedResponse<ContractRecord>>(`/contracts/?${searchParams}`);
  }

  async getContract(id: number): Promise<ContractRecord> {
    return this.request<ContractRecord>(`/contracts/${id}`);
  }

  async createContract(contract: ContractCreate): Promise<ContractRecord> {
    return this.request<ContractRecord>('/contracts/', {
      method: 'POST',
      body: JSON.stringify(contract),
    });
  }

  async updateContract(id: number, updates: Partial<ContractCreate>): Promise<ContractRecord> {
    return this.request<ContractRecord>(`/contracts/${id}`, {
      method: 'PUT',
      body: JSON.stringify(updates),
    });
  }

  async deleteContract(id: number): Promise<void> {
    return this.request<void>(`/contracts/${id}`, {
      method: 'DELETE',
    });
  }

  async analyzeContract(id: number): Promise<any> {
    return this.request<any>(`/contracts/${id}/analyze`, {
      method: 'POST',
    });
  }

  async askContractQuestion(id: number, question: string): Promise<any> {
    const formData = new FormData();
    formData.append('question', question);
    
    return this.request<any>(`/contracts/${id}/ask`, {
      method: 'POST',
      body: formData,
    });
  }

  async uploadContractFile(contractId: number, file: File): Promise<any> {
    const formData = new FormData();
    formData.append('file', file);
    
    return this.request<any>(`/contracts/${contractId}/upload`, {
      method: 'POST',
      body: formData,
    });
  }

  async downloadContractReport(id: number): Promise<Blob> {
    const response = await fetch(`${this.baseURL}/contracts/${id}/report`, {
      headers: {
        Authorization: `Bearer ${this.getToken()}`,
      },
    });
    
    if (!response.ok) {
      throw new Error('Failed to download report');
    }
    
    return response.blob();
  }

  // ===========================
  // 🏢 Workspace Management
  // ===========================

  async getWorkspaces(): Promise<Workspace[]> {
    return this.request<Workspace[]>('/workspaces/');
  }

  async getWorkspace(id: number): Promise<Workspace> {
    return this.request<Workspace>(`/workspaces/${id}`);
  }

  async createWorkspace(workspace: Partial<Workspace>): Promise<Workspace> {
    return this.request<Workspace>('/workspaces/', {
      method: 'POST',
      body: JSON.stringify(workspace),
    });
  }

  async updateWorkspace(id: number, updates: Partial<Workspace>): Promise<Workspace> {
    return this.request<Workspace>(`/workspaces/${id}`, {
      method: 'PUT',
      body: JSON.stringify(updates),
    });
  }

  async deleteWorkspace(id: number): Promise<void> {
    return this.request<void>(`/workspaces/${id}`, {
      method: 'DELETE',
    });
  }

  // ===========================
  // 👥 User Management
  // ===========================

  async getUsers(): Promise<User[]> {
    return this.request<User[]>('/api/users');
  }

  async createUser(userData: any): Promise<User> {
    return this.request<User>('/api/users/create', {
      method: 'POST',
      body: JSON.stringify(userData),
    });
  }

  async updateUser(userId: number, updates: any): Promise<User> {
    return this.request<User>(`/api/users/${userId}`, {
      method: 'PUT',
      body: JSON.stringify(updates),
    });
  }

  async deleteUser(userId: number): Promise<void> {
    return this.request<void>(`/api/users/${userId}`, {
      method: 'DELETE',
    });
  }

  // ===========================
  // 📊 Analytics & Dashboard
  // ===========================

  async getDashboardData(params?: {
    skip?: number;
    limit?: number;
    workspace_id?: number;
    start_date?: string;
    end_date?: string;
  }): Promise<{
    contracts: ContractRecord[];
    pagination: {
      total: number;
      pages: number;
      current_page: number;
      items_per_page: number;
    };
    workspaces: Workspace[];
  }> {
    const searchParams = new URLSearchParams();
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined) {
          searchParams.append(key, value.toString());
        }
      });
    }

    return this.request<{
      contracts: ContractRecord[];
      pagination: {
        total: number;
        pages: number;
        current_page: number;
        items_per_page: number;
      };
      workspaces: Workspace[];
    }>(`/dashboard/?${searchParams}`);
  }

  async getDashboardMetrics(params?: any): Promise<DashboardMetrics> {
    const searchParams = new URLSearchParams();
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined && value !== null) {
          searchParams.append(key, value.toString());
        }
      });
    }
    return this.request<DashboardMetrics>(`/api/dashboard-metrics?${searchParams}`);
  }

  // ===========================
  // 💳 Billing & Subscriptions
  // ===========================

  async getSubscriptionPlans(): Promise<SubscriptionPlan[]> {
    return this.request<SubscriptionPlan[]>('/api/plans');
  }

  async getUserSubscription(): Promise<UserSubscription> {
    return this.request<UserSubscription>('/api/my-subscription');
  }

  async createCheckoutSession(planId: string, successUrl: string, cancelUrl: string): Promise<any> {
    return this.request<any>('/api/create-checkout-session', {
      method: 'POST',
      body: JSON.stringify({ plan_id: planId, success_url: successUrl, cancel_url: cancelUrl }),
    });
  }

  async cancelSubscription(): Promise<any> {
    return this.request<any>('/api/cancel-subscription', {
      method: 'POST',
    });
  }

  // ===========================
  // ⚙️ User Settings & Preferences
  // ===========================

  async getUserSettings(): Promise<any> {
    return this.request<any>('/api/user-settings');
  }

  async changePassword(currentPassword: string, newPassword: string): Promise<any> {
    return this.request<any>('/api/users/change-password', {
      method: 'POST',
      body: JSON.stringify({ current_password: currentPassword, new_password: newPassword }),
    });
  }

  async updateNotificationPreferences(preferences: any): Promise<any> {
    return this.request<any>('/api/user-settings/notifications', {
      method: 'PUT',
      body: JSON.stringify(preferences),
    });
  }

  async updateAppearanceSettings(settings: any): Promise<any> {
    return this.request<any>('/api/user-settings/appearance', {
      method: 'PUT',
      body: JSON.stringify(settings),
    });
  }

  async exportUserData(): Promise<Blob> {
    const response = await fetch(`${this.baseURL}/api/user-settings/export-data`, {
      headers: {
        Authorization: `Bearer ${this.getToken()}`,
      },
    });
    if (!response.ok) throw new Error('Failed to export user data');
    return response.blob();
  }

  // ===========================
  // 🔐 Security & 2FA
  // ===========================

  async getActiveSessions(): Promise<any> {
    return this.request<any>('/api/user-settings/active-sessions');
  }

  async revokeSession(sessionId: string): Promise<any> {
    return this.request<any>(`/api/user-settings/revoke-session/${sessionId}`, {
      method: 'DELETE',
    });
  }

  async get2FAStatus(): Promise<any> {
    return this.request<any>('/api/user-settings/2fa-status');
  }

  async enable2FA(): Promise<any> {
    return this.request<any>('/api/user-settings/enable-2fa', {
      method: 'POST',
    });
  }

  async verify2FA(code: string): Promise<any> {
    return this.request<any>('/api/user-settings/verify-2fa', {
      method: 'POST',
      body: JSON.stringify({ code }),
    });
  }

  async disable2FA(): Promise<any> {
    return this.request<any>('/api/user-settings/disable-2fa', {
      method: 'DELETE',
    });
  }

  // ===========================
  // 📧 Demo & Contact
  // ===========================

  async submitDemoRequest(demoData: {
    name: string;
    email: string;
    company?: string;
    phone?: string;
    message?: string;
  }): Promise<{ message: string; status: string }> {
    return this.request<{ message: string; status: string }>('/demo/request', {
      method: 'POST',
      body: JSON.stringify(demoData),
    });
  }

  // ===========================
  // 📁 File Management
  // ===========================

  async uploadFile(file: File, workspaceId?: number): Promise<any> {
    const formData = new FormData();
    formData.append('file', file);
    if (workspaceId) {
      formData.append('workspace_id', workspaceId.toString());
    }
    
    return this.request<any>('/files/upload', {
      method: 'POST',
      body: formData,
    });
  }

  async downloadFile(fileId: string): Promise<Blob> {
    const response = await fetch(`${this.baseURL}/files/${fileId}`, {
      headers: {
        Authorization: `Bearer ${this.getToken()}`,
      },
    });
    
    if (!response.ok) {
      throw new Error('Failed to download file');
    }
    
    return response.blob();
  }

  async deleteFile(fileId: string): Promise<{ message: string }> {
    return this.request<{ message: string }>(`/files/${fileId}`, {
      method: 'DELETE',
    });
  }
}

// Export singleton instance
export const apiClient = new ApiClient(); 