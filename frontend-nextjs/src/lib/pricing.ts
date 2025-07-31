import { PricingTier } from '@/types';

export const PRICING_TIERS: PricingTier[] = [
  {
    name: "Starter",
    price: 99,
    hoaLimit: 1,
    unitLimit: 25,
    userLimit: 2,
    description: "For small HOAs with limited units"
  },
  {
    name: "Business",
    price: 299,
    hoaLimit: 1,
    unitLimit: 100,
    userLimit: 5,
    description: "Perfect for midsize HOAs looking to scale"
  },
  {
    name: "Pro",
    price: 499,
    hoaLimit: 2,
    unitLimit: 250,
    userLimit: 10,
    description: "Great for self-managed large HOAs or small firms"
  },
  {
    name: "Enterprise",
    price: 999,
    hoaLimit: 5,
    unitLimit: 500,
    userLimit: 20,
    description: "Supports multi-HOA management and larger teams"
  },
  {
    name: "White Label",
    price: "Contact Us",
    hoaLimit: "Unlimited",
    unitLimit: "Unlimited",
    userLimit: "Unlimited",
    description: "Custom setup with white-label branding, API access, and more"
  }
];

export const getPlanFeatures = (planName: string): string[] => {
  const baseFeatures = [
    "Mobile violation capture",
    "AI-powered analysis", 
    "Professional reporting",
    "Automated communication"
  ];

  switch (planName.toLowerCase()) {
    case "starter":
      return [
        ...baseFeatures,
        "Basic violation tracking",
        "Standard letter generation",
        "Email support",
        "Standard reports"
      ];
    case "business":
      return [
        ...baseFeatures,
        "Advanced analytics & reporting",
        "AI-powered letter generation",
        "Priority support",
        "Custom integrations"
      ];
    case "pro":
      return [
        ...baseFeatures,
        "Advanced analytics & reporting",
        "AI-powered letter generation",
        "Priority support",
        "Custom integrations",
        "Multi-HOA management"
      ];
    case "enterprise":
      return [
        ...baseFeatures,
        "Advanced analytics & reporting",
        "AI-powered letter generation",
        "Priority support",
        "Custom integrations",
        "Multi-HOA management",
        "Dedicated account manager",
        "Advanced compliance tools"
      ];
    case "white label":
      return [
        ...baseFeatures,
        "Advanced analytics & reporting",
        "AI-powered letter generation",
        "Priority support",
        "Custom integrations",
        "Multi-HOA management",
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
        hoas: 1,
        units: 25,
        users: 2,
        violations_per_month: 50,
        storage_gb: 5
      };
    case "business":
      return {
        hoas: 1,
        units: 100,
        users: 5,
        violations_per_month: 200,
        storage_gb: 20
      };
    case "pro":
      return {
        hoas: 2,
        units: 250,
        users: 10,
        violations_per_month: 500,
        storage_gb: 50
      };
    case "enterprise":
      return {
        hoas: 5,
        units: 500,
        users: 20,
        violations_per_month: 1000,
        storage_gb: 100
      };
    case "white label":
      return {
        hoas: -1, // unlimited
        units: -1, // unlimited
        users: -1, // unlimited
        violations_per_month: -1, // unlimited
        storage_gb: -1 // unlimited
      };
    default:
      return {
        hoas: 1,
        units: 25,
        users: 2,
        violations_per_month: 50,
        storage_gb: 5
      };
  }
}; 