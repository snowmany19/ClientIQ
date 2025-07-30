// User types
export interface User {
  id: number;
  username: string;
  email: string;
  role: 'admin' | 'hoa_board' | 'inspector' | 'super_admin' | 'resident';
  subscription_status: 'active' | 'inactive' | 'cancelled';
  plan_id: string;
  hoa?: HOA;
}

export interface HOA {
  id: number;
  hoa_number: string;
  name: string;
  location: string;
  contact_email: string;
}

// Violation types
export interface Violation {
  id: number;
  violation_number: number;
  timestamp: string;
  description: string;
  summary: string;
  tags: string;
  repeat_offender_score: number;
  hoa_name: string;
  address: string;
  location: string;
  offender: string;
  gps_coordinates?: string;
  status: 'open' | 'resolved' | 'disputed' | 'escalated';
  pdf_path?: string;
  image_url?: string;
  user_id: number;
  inspected_by: string;
  resolved_at?: string;
  resolved_by?: string;
  resolution_notes?: string;
  reviewed_at?: string;
  reviewed_by?: string;
}

export interface ViolationCreate {
  description: string;
  hoa: string;
  address: string;
  location: string;
  offender: string;
  gps_coordinates?: string;
  violation_type?: string;
  file?: File;
  mobile_capture?: boolean;
  auto_gps?: boolean;
}

// Authentication types
export interface LoginCredentials {
  username: string;
  password: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User;
}

// Billing types
export interface SubscriptionPlan {
  id: string;
  name: string;
  price: number;
  currency: string;
  interval: string;
  features: string[];
  limits: {
    violations_per_month: number;
    users: number;
  };
}

export interface UserSubscription {
  subscription_id: string;
  plan_id: string;
  status: string;
  current_period_start: string;
  current_period_end: string;
  cancel_at_period_end: boolean;
  features: string[];
  limits: {
    violations_per_month: number;
    users: number;
  };
}

// Analytics types
export interface DashboardMetrics {
  total_violations: number;
  open_violations: number;
  resolved_violations: number;
  disputed_violations: number;
  repeat_offenders: number;
  monthly_trends: {
    date: string;
    count: number;
  }[];
  top_violation_types: {
    type: string;
    count: number;
  }[];
  resolution_rate: number;
  average_resolution_time: number;
}

// API Response types
export interface PaginatedResponse<T> {
  data: T[];
  pagination: {
    total: number;
    pages: number;
    current_page: number;
    items_per_page: number;
  };
}

export interface ApiError {
  detail: string;
  type: string;
  errors?: Array<{
    field: string;
    message: string;
  }>;
} 