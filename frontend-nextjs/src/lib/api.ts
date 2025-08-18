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
      this.token = localStorage.getItem('auth_token');
    }
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {},
    retries: number = 3
  ): Promise<T> {
    const url = `${this.baseURL}${endpoint}`;
    
    console.log('=== API CLIENT: REQUEST METHOD ===');
    console.log('URL:', url);
    console.log('Method:', options.method || 'GET');
    console.log('Options:', options);
    
    const config: RequestInit = {
      ...options,
    };

    // Only set default Content-Type for JSON requests
    if (!options.body || typeof options.body === 'string') {
      config.headers = {
        'Content-Type': 'application/json',
        ...options.headers,
      };
      console.log('Set Content-Type: application/json');
    } else {
      // For FormData and other types, don't set Content-Type (let browser set it)
      config.headers = {
        ...options.headers,
      };
      console.log('No Content-Type set (browser will set it)');
    }

    // Add authorization header if token exists
    if (this.token) {
      config.headers = {
        ...config.headers,
        Authorization: `Bearer ${this.token}`,
      };
      console.log('Added Authorization header');
    }

    console.log('Final config:', config);
    console.log('Final headers:', config.headers);

    try {
      console.log('Making fetch request...');
      const response = await fetch(url, config);
      
      console.log('Response received:', {
        status: response.status,
        statusText: response.statusText,
        headers: Object.fromEntries(response.headers.entries())
      });
      
      if (response.status === 401) {
        // Token expired or invalid
        console.log('Unauthorized response, redirecting to login');
        this.removeToken();
        window.location.href = '/login';
        throw new Error('Authentication required');
      }

      if (!response.ok) {
        console.log('Response not OK, parsing error data');
        const errorData: ApiError = await response.json();
        console.log('Error data:', errorData);
        throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
      }

      // Handle empty responses
      const contentType = response.headers.get('content-type');
      console.log('Response content-type:', contentType);
      
      if (contentType && contentType.includes('application/json')) {
        const jsonResult = await response.json();
        console.log('JSON response:', jsonResult);
        return jsonResult;
      }
      
      console.log('Empty response, returning empty object');
      return {} as T;
    } catch (error: any) {
      console.error('=== API CLIENT: REQUEST ERROR ===');
      console.error('Request failed:', error);
      console.error('Error details:', {
        name: error.name,
        message: error.message,
        stack: error.stack
      });
      
      if (retries > 0 && error.name === 'TypeError') {
        // Network error, retry
        console.log(`Retrying request (${retries} retries left)...`);
        await new Promise(resolve => setTimeout(resolve, 1000));
        return this.request<T>(endpoint, options, retries - 1);
      }
      throw error;
    }
  }

  private getToken(): string | null {
    return this.token || localStorage.getItem('auth_token');
  }

  private setToken(token: string): void {
    this.token = token;
    localStorage.setItem('auth_token', token);
  }

  private removeToken(): void {
    this.token = null;
    localStorage.removeItem('auth_token');
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
    page?: number;
    per_page?: number;
    category?: string;
    status?: string;
    search?: string;
  }): Promise<any> { // Changed from PaginatedResponse<ContractRecord> to any to match backend response
    const searchParams = new URLSearchParams();
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined) {
          searchParams.append(key, value.toString());
        }
      });
    }

    return this.request<any>(`/api/list?${searchParams}`);
  }

  async getContract(id: number): Promise<ContractRecord> {
    return this.request<ContractRecord>(`/api/${id}`);
  }

  async createContract(contract: ContractCreate): Promise<ContractRecord> {
    return this.request<ContractRecord>('/api/', {
      method: 'POST',
      body: JSON.stringify(contract),
    });
  }

  async updateContract(id: number, updates: Partial<ContractCreate>): Promise<ContractRecord> {
    return this.request<ContractRecord>(`/api/${id}`, {
      method: 'PUT',
      body: JSON.stringify(updates),
    });
  }

  async deleteContract(id: number): Promise<void> {
    return this.request<void>(`/api/${id}`, {
      method: 'DELETE',
    });
  }

  async analyzeContract(id: number): Promise<any> {
    return this.request<any>(`/api/analyze/${id}`, {
      method: 'POST',
    });
  }

  async askContractQuestion(id: number, question: string): Promise<any> {
    const formData = new FormData();
    formData.append('question', question);
    
    return this.request<any>(`/api/ask/${id}`, {
      method: 'POST',
      body: formData,
    });
  }

  async uploadContractFile(contractId: number, file: File): Promise<any> {
    console.log('=== API CLIENT: UPLOAD CONTRACT FILE ===');
    console.log('Contract ID:', contractId);
    console.log('File details:', { name: file.name, size: file.size, type: file.type });
    console.log('File object:', file);
    
    const formData = new FormData();
    formData.append('file', file);
    
    console.log('FormData created:', formData);
    console.log('FormData entries:');
    for (const [key, value] of formData.entries()) {
      console.log(`  ${key}:`, value);
    }
    
    console.log('Making request to:', `/api/upload/${contractId}`);
    console.log('Request method: POST');
    console.log('Request body type:', typeof formData);
    
    try {
      const result = await this.request<any>(`/api/upload/${contractId}`, {
        method: 'POST',
        body: formData,
      });
      
      console.log('Upload request successful:', result);
      return result;
    } catch (error) {
      console.error('=== API CLIENT: UPLOAD ERROR ===');
      console.error('Upload request failed:', error);
      throw error;
    }
  }

  async downloadContractReport(id: number): Promise<Blob> {
    console.log('=== API CLIENT: DOWNLOAD REPORT ===');
    console.log('Contract ID:', id);
    
    try {
      const response = await fetch(`${this.baseURL}/api/report/${id}`, {
        headers: {
          Authorization: `Bearer ${this.getToken()}`,
        },
      });
      
      console.log('Download response:', {
        status: response.status,
        statusText: response.statusText,
        headers: Object.fromEntries(response.headers.entries())
      });
      
      if (!response.ok) {
        console.error('Download failed with status:', response.status);
        throw new Error(`Failed to download report: ${response.status} ${response.statusText}`);
      }
      
      const blob = await response.blob();
      console.log('Download successful, blob size:', blob.size);
      return blob;
    } catch (error) {
      console.error('=== API CLIENT: DOWNLOAD ERROR ===');
      console.error('Download failed:', error);
      throw error;
    }
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