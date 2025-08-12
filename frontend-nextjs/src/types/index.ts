// User types
export interface User {
  id: number;
  username: string;
  email: string;
  role: 'admin' | 'analyst' | 'viewer' | 'super_admin' | 'resident' | 'inspector';
  subscription_status: 'active' | 'inactive' | 'cancelled';
  plan_id: string;
  workspace?: Workspace;
}

export interface Workspace {
  id: number;
  workspace_number: string;
  name: string;
  company_name: string;
  industry: string;
  contact_email: string;
  created_at: string;
  updated_at: string;
}

// Contract types
export interface ContractRecord {
  id: number;
  title: string;
  counterparty: string;
  category: 'NDA' | 'MSA' | 'SOW' | 'Employment' | 'Vendor' | 'Lease' | 'Other';
  effective_date?: string;
  term_end?: string;
  renewal_terms?: string;
  governing_law?: string;
  uploaded_files: string[];
  analysis_json?: any;
  summary_text?: string;
  risk_items: ContractRisk[];
  rewrite_suggestions: ContractSuggestion[];
  status: 'pending' | 'analyzed' | 'reviewed' | 'approved' | 'rejected';
  created_at: string;
  updated_at: string;
  owner_username?: string;
}

export interface ContractRisk {
  severity: number; // 1-5
  confidence: number; // 0.0-1.0
  category: string;
  title: string;
  description: string;
  rationale: string;
  clause_reference?: string;
  business_impact: string;
  mitigation_suggestions: string[];
}

export interface ContractSuggestion {
  risk_id: string;
  type: 'balanced' | 'company_favorable';
  category: string;
  original_text?: string;
  suggested_text: string;
  rationale: string;
  negotiation_tips: string[];
  fallback_position?: string;
}

export interface ContractCreate {
  title: string;
  counterparty: string;
  category: 'NDA' | 'MSA' | 'SOW' | 'Employment' | 'Vendor' | 'Lease' | 'Other';
  effective_date?: string;
  term_end?: string;
  renewal_terms?: string;
  governing_law?: string;
  uploaded_files: string[];
  status?: string;
}

export interface ContractAnalysis {
  summary: {
    executive_summary: string;
    key_terms: any;
    business_impact: string;
    critical_dates: string[];
    obligations: string[];
  };
  risks: ContractRisk[];
  suggestions: ContractSuggestion[];
  category_analysis: any;
  compliance: {
    status: string;
    issues?: string[];
  };
}

// Violation types (legacy - keeping for migration)


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
    contracts_per_month: number;
    users: number;
    storage_gb: number;
    workspaces?: number;
  };
}

export interface PricingTier {
  name: string;
  price: number | string;
  contractLimit: number | string;
  userLimit: number | string;
  workspaceLimit?: number | string;
  clientLimit?: number | string;
  description: string;
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
    contracts_per_month: number;
    users: number;
    storage_gb: number;
    workspaces?: number;
  };
}

// Analytics types
export interface DashboardMetrics {
  // Contract metrics
  total_contracts: number;
  analyzed_contracts: number;
  pending_contracts: number;
  high_risk_contracts: number;
  monthly_contract_trends: {
    date: string;
    count: number;
  }[];
  top_contract_categories: {
    category: string;
    count: number;
  }[];
  average_analysis_time: number;
  
  // Legacy violation metrics (for migration)
  total_violations?: number;
  open_violations?: number;
  resolved_violations?: number;
  disputed_violations?: number;
  repeat_offenders?: number;
  monthly_trends?: {
    date: string;
    count: number;
  }[];
  top_violation_types?: {
    type: string;
    count: number;
  }[];
  resolution_rate?: number;
  average_resolution_time?: number;
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