# ContractGuard.ai Pricing Structure Update Summary

## Overview
Updated the ContractGuard.ai SaaS platform's billing logic to implement a new 5-tier pricing structure with updated pricing and limits.

## New Pricing Tiers

### 1. **Solo** - $39/month
- **Contracts:** 10/month
- **Users:** 1
- **Storage:** 5GB
- **Description:** For individual professionals and small businesses

### 2. **Team** - $99/month ⭐ **Most Popular**
- **Contracts:** 50/month
- **Users:** 5
- **Storage:** 20GB
- **Description:** Perfect for small teams and growing businesses

### 3. **Business** - $299/month
- **Contracts:** 250/month
- **Users:** 20
- **Storage:** 50GB
- **Description:** Great for established businesses and legal teams

### 4. **Enterprise** - $999/month
- **Contracts:** 1000/month
- **Users:** Unlimited
- **Storage:** 100GB
- **Description:** Supports large enterprises and legal firms

### 5. **White Label** - Contact Us
- **Contracts:** Unlimited
- **Users:** Unlimited
- **Storage:** Unlimited
- **Description:** Custom setup with white-label branding, API access, and more

## Files Updated

### Backend Changes

1. **`backend/utils/stripe_utils.py`**
   - Updated `SUBSCRIPTION_PLANS` configuration
   - Changed pricing from $199/$499/$999 to $99/$299/$499/$999
   - Added new "business" and "pro" tiers
   - Updated plan order in upgrade suggestions
   - Added new limits structure (hoas, units, users)

2. **`backend/utils/plan_enforcement.py`**
   - Updated plan features mapping
   - Added new tiers to feature requirements
   - Updated plan order for upgrade suggestions

3. **`backend/env_example.txt`**
   - Added new Stripe price ID environment variables
   - `STRIPE_STARTER_PRICE_ID`
   - `STRIPE_BUSINESS_PRICE_ID`
   - `STRIPE_PRO_PRICE_ID`
   - `STRIPE_ENTERPRISE_PRICE_ID`

### Frontend Changes

1. **`frontend-nextjs/src/types/index.ts`**
   - Updated `SubscriptionPlan` interface to include new limits structure
   - Added `PricingTier` interface for frontend pricing display
   - Updated `UserSubscription` interface

2. **`frontend-nextjs/src/lib/pricing.ts`** (New File)
   - Created shared pricing configuration
   - Defined `PRICING_TIERS` array
   - Added `getPlanFeatures()` and `getPlanLimits()` utility functions
   - Centralized pricing logic for consistency

3. **`frontend-nextjs/src/components/landing/PricingSection.tsx`**
   - Updated to use new shared pricing configuration
   - Changed from 3-column to 5-column layout
   - Added limits display (HOAs, Units, Users)
   - Updated pricing and descriptions
   - Added proper handling for White Label tier

4. **`frontend-nextjs/src/components/billing/BillingDashboard.tsx`**
   - Updated plan display to show new limits structure
   - Changed from 3-column to 4-column grid for plans
   - Added HOAs and Units to usage statistics
   - Updated feature display to show limited features with "+X more" indicator

5. **`frontend-nextjs/src/components/landing/CTASection.tsx`**
   - Updated starting price from $199 to $99

## Key Features

### Consistent Feature Access
All tiers now share the same core features:
- AI-powered contract analysis
- Risk assessment and scoring
- Professional reporting
- Automated contract review

### Scaling by Limits
Pricing scales by:
- **Number of Contracts per month** (10 → 50 → 250 → 1000 → Unlimited)
- **Number of Users** (1 → 5 → 20 → Unlimited → Unlimited)
- **Storage** (5GB → 20GB → 50GB → 100GB → Unlimited)

### White Label Tier
- Contact-only custom tier
- Unlimited everything
- White-label branding
- API access
- Dedicated support

## Environment Variables Required

Add these to your `.env` file:
```bash
STRIPE_SOLO_PRICE_ID=price_your_solo_price_id_here
STRIPE_TEAM_PRICE_ID=price_your_team_price_id_here
STRIPE_BUSINESS_PRICE_ID=price_your_business_price_id_here
STRIPE_ENTERPRISE_PRICE_ID=price_your_enterprise_price_id_here
```

## Migration Notes

1. **Existing Users:** Users on the old "Professional" plan will need to be migrated to the new "Business" plan
2. **Stripe Setup:** New price IDs need to be created in Stripe for each tier
3. **Database:** No database schema changes required
4. **Testing:** Test all pricing tiers and upgrade/downgrade flows

## Next Steps

1. Create new Stripe price IDs for each tier
2. Update environment variables with actual Stripe price IDs
3. Test the new pricing structure in development
4. Migrate existing users to new plan structure
5. Update documentation and marketing materials 