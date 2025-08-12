import { PricingTier } from '@/types';

export const PRICING_TIERS: PricingTier[] = [
  {
    name: "Starter",
    price: 199,
    contractLimit: 25,
    workspaceLimit: 1,
    clientLimit: 5,
    userLimit: 2,
    description: "For small law firms and solo practitioners"
  },
  {
    name: "Business",
    price: 499,
    contractLimit: 100,
    workspaceLimit: 1,
    clientLimit: 15,
    userLimit: 5,
    description: "Perfect for growing law firms and legal departments"
  },
  {
    name: "Pro",
    price: 999,
    contractLimit: 250,
    workspaceLimit: 2,
    clientLimit: 50,
    userLimit: 10,
    description: "Great for established law firms and corporate legal teams"
  },
  {
    name: "Enterprise",
    price: 1999,
    contractLimit: 500,
    workspaceLimit: 5,
    clientLimit: 100,
    userLimit: 20,
    description: "Supports large law firms and enterprise legal departments"
  },
  {
    name: "White Label",
    price: "Contact Us",
    contractLimit: "Unlimited",
    workspaceLimit: "Unlimited",
    clientLimit: "Unlimited",
    userLimit: "Unlimited",
    description: "Custom setup with white-label branding, API access, and more"
  }
];

export const getPlanFeatures = (planName: string): string[] => {
  const baseFeatures = [
    "Contract upload & analysis",
    "AI-powered risk assessment", 
    "Professional review reports",
    "Collaborative review"
  ];

  switch (planName.toLowerCase()) {
    case "starter":
      return [
        ...baseFeatures,
        "Basic contract analysis",
        "Standard risk assessment",
        "Email support",
        "Standard reports"
      ];
    case "business":
      return [
        ...baseFeatures,
        "Advanced analytics & reporting",
        "AI-powered risk assessment",
        "Priority support",
        "Custom integrations"
      ];
    case "pro":
      return [
        ...baseFeatures,
        "Advanced analytics & reporting",
        "AI-powered risk assessment",
        "Priority support",
        "Custom integrations",
        "Multi-client management"
      ];
    case "enterprise":
      return [
        ...baseFeatures,
        "Advanced analytics & reporting",
        "AI-powered risk assessment",
        "Priority support",
        "Custom integrations",
        "Multi-client management",
        "Dedicated account manager",
        "Advanced compliance tools"
      ];
    case "white label":
      return [
        ...baseFeatures,
        "Advanced analytics & reporting",
        "AI-powered risk assessment",
        "Priority support",
        "Custom integrations",
        "Multi-client management",
        "Dedicated account manager",
        "Advanced compliance tools",
        "White-label branding",
        "API access",
        "Custom integrations",
        "Dedicated support"
      ];
    default:
      return baseFeatures;
  }
};

export const getPlanLimits = (planName: string) => {
  switch (planName.toLowerCase()) {
    case "starter":
      return {
        workspaces: 1,
        contracts_per_month: 25,
        users: 2,
        storage_gb: 10
      };
    case "business":
      return {
        workspaces: 1,
        contracts_per_month: 100,
        users: 5,
        storage_gb: 25
      };
    case "pro":
      return {
        workspaces: 2,
        contracts_per_month: 250,
        users: 10,
        storage_gb: 50
      };
    case "enterprise":
      return {
        workspaces: 5,
        contracts_per_month: 500,
        users: 20,
        storage_gb: 100
      };
    case "white label":
      return {
        workspaces: -1, // unlimited
        contracts_per_month: -1, // unlimited
        users: -1, // unlimited
        storage_gb: -1 // unlimited
      };
    default:
      return {
        workspaces: 1,
        contracts_per_month: 25,
        users: 2,
        storage_gb: 10
      };
  }
}; 