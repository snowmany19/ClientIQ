'use client';

import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/Button';
import { apiClient } from '@/lib/api';
import { SubscriptionPlan, UserSubscription } from '@/types';
import { 
  CreditCard, 
  CheckCircle, 
  XCircle, 
  AlertCircle,
  Calendar,
  DollarSign,
  Users,
  Zap
} from 'lucide-react';

export default function BillingDashboard() {
  const [plans, setPlans] = useState<SubscriptionPlan[]>([]);
  const [subscription, setSubscription] = useState<UserSubscription | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [cancelling, setCancelling] = useState(false);

  useEffect(() => {
    loadBillingData();
  }, []);

  const loadBillingData = async () => {
    try {
      setLoading(true);
      const [plansData, subscriptionData] = await Promise.all([
        apiClient.getSubscriptionPlans(),
        apiClient.getUserSubscription()
      ]);
      
      setPlans(plansData.plans);
      setSubscription(subscriptionData);
    } catch (error) {
      console.error('Failed to load billing data:', error);
      setError('Failed to load billing information');
    } finally {
      setLoading(false);
    }
  };

  const handleUpgrade = async (planId: string) => {
    try {
      const successUrl = `${window.location.origin}/dashboard/billing?success=true`;
      const cancelUrl = `${window.location.origin}/dashboard/billing?canceled=true`;
      
      const response = await apiClient.createCheckoutSession(planId, successUrl, cancelUrl);
      window.location.href = response.checkout_url;
    } catch (error) {
      console.error('Failed to create checkout session:', error);
      setError('Failed to start checkout process');
    }
  };

  const handleCancelSubscription = async () => {
    if (!confirm('Are you sure you want to cancel your subscription? You will lose access to premium features at the end of your current billing period.')) {
      return;
    }

    try {
      setCancelling(true);
      await apiClient.cancelSubscription();
      await loadBillingData(); // Reload to get updated subscription status
    } catch (error) {
      console.error('Failed to cancel subscription:', error);
      setError('Failed to cancel subscription');
    } finally {
      setCancelling(false);
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'active':
        return <CheckCircle className="h-5 w-5 text-green-500" />;
      case 'canceled':
        return <XCircle className="h-5 w-5 text-red-500" />;
      case 'past_due':
        return <AlertCircle className="h-5 w-5 text-yellow-500" />;
      default:
        return <AlertCircle className="h-5 w-5 text-gray-500" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active':
        return 'bg-green-100 text-green-800';
      case 'canceled':
        return 'bg-red-100 text-red-800';
      case 'past_due':
        return 'bg-yellow-100 text-yellow-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading billing information...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Current Subscription */}
      {subscription && (
        <div className="bg-white shadow rounded-lg p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-medium text-gray-900">Current Subscription</h2>
            <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(subscription.status)}`}>
              {getStatusIcon(subscription.status)}
              <span className="ml-1 capitalize">{subscription.status}</span>
            </span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
            <div className="flex items-center">
              <CreditCard className="h-5 w-5 text-gray-400 mr-3" />
              <div>
                <p className="text-sm font-medium text-gray-900">{subscription.plan_id}</p>
                <p className="text-sm text-gray-500">Plan</p>
              </div>
            </div>
            <div className="flex items-center">
              <Calendar className="h-5 w-5 text-gray-400 mr-3" />
              <div>
                <p className="text-sm font-medium text-gray-900">
                  {new Date(subscription.current_period_end).toLocaleDateString()}
                </p>
                <p className="text-sm text-gray-500">Next billing date</p>
              </div>
            </div>
            <div className="flex items-center">
              <Users className="h-5 w-5 text-gray-400 mr-3" />
              <div>
                <p className="text-sm font-medium text-gray-900">
                  {subscription.limits.users === -1 ? 'Unlimited' : subscription.limits.users}
                </p>
                <p className="text-sm text-gray-500">Users allowed</p>
              </div>
            </div>
          </div>

          {subscription.cancel_at_period_end && (
            <div className="bg-yellow-50 border border-yellow-200 rounded-md p-4 mb-4">
              <div className="flex">
                <AlertCircle className="h-5 w-5 text-yellow-400" />
                <div className="ml-3">
                  <h3 className="text-sm font-medium text-yellow-800">
                    Subscription Canceling
                  </h3>
                  <div className="mt-2 text-sm text-yellow-700">
                    Your subscription will be canceled at the end of the current billing period on{' '}
                    {new Date(subscription.current_period_end).toLocaleDateString()}.
                  </div>
                </div>
              </div>
            </div>
          )}

          <div className="flex space-x-3">
            {!subscription.cancel_at_period_end && (
              <Button
                variant="outline"
                onClick={handleCancelSubscription}
                loading={cancelling}
              >
                Cancel Subscription
              </Button>
            )}
            <Button
              onClick={() => {
                // Redirect to Stripe billing portal
                // You'll need to implement this in your API
              }}
            >
              Manage Billing
            </Button>
          </div>
        </div>
      )}

      {/* Available Plans */}
      <div className="bg-white shadow rounded-lg p-6">
        <h2 className="text-lg font-medium text-gray-900 mb-4">Available Plans</h2>
        
                <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          {Array.isArray(plans) ? plans.map((plan) => (
            <div
              key={plan.id}
              className={`border rounded-lg p-6 ${
                subscription?.plan_id === plan.id
                  ? 'border-blue-500 bg-blue-50'
                  : 'border-gray-200'
              }`}
            >
              <div className="text-center">
                <h3 className="text-lg font-medium text-gray-900">{plan.name}</h3>
                <div className="mt-4">
                  <span className="text-3xl font-bold text-gray-900">
                    ${plan.price}
                  </span>
                  <span className="text-gray-500">/{plan.interval}</span>
                </div>

                {/* Plan Limits */}
                <div className="mt-4 space-y-2 text-sm text-gray-600">
                  <div>
                    <span className="font-medium">HOAs:</span> {plan.limits.hoas === -1 ? 'Unlimited' : plan.limits.hoas}
                  </div>
                  <div>
                    <span className="font-medium">Units:</span> {plan.limits.units === -1 ? 'Unlimited' : plan.limits.units}
                  </div>
                  <div>
                    <span className="font-medium">Users:</span> {plan.limits.users === -1 ? 'Unlimited' : plan.limits.users}
                  </div>
                  <div>
                    <span className="font-medium">Violations:</span> {plan.limits.violations_per_month === -1 ? 'Unlimited' : plan.limits.violations_per_month}/month
                  </div>
                </div>

                <ul className="mt-6 space-y-3">
                  {plan.features.slice(0, 4).map((feature, index) => (
                    <li key={index} className="flex items-center text-sm text-gray-600">
                      <CheckCircle className="h-4 w-4 text-green-500 mr-2" />
                      {feature}
                    </li>
                  ))}
                  {plan.features.length > 4 && (
                    <li className="text-sm text-gray-400">
                      +{plan.features.length - 4} more features
                    </li>
                  )}
                </ul>

                <div className="mt-6">
                  {subscription?.plan_id === plan.id ? (
                    <span className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-blue-700 bg-blue-100">
                      Current Plan
                    </span>
                  ) : (
                    <Button
                      onClick={() => handleUpgrade(plan.id)}
                      className="w-full"
                    >
                      {subscription ? 'Upgrade' : 'Get Started'}
                    </Button>
                  )}
                </div>
              </div>
            </div>
          )) : (
            <div className="col-span-4 text-center py-8">
              <p className="text-gray-500">Loading plans...</p>
            </div>
          )}
        </div>

        {/* White Label Contact */}
        <div className="mt-8 p-6 bg-gradient-to-r from-purple-50 to-blue-50 border border-purple-200 rounded-lg">
          <div className="text-center">
            <h3 className="text-xl font-semibold text-gray-900 mb-2">Need White-Label Solution?</h3>
            <p className="text-gray-600 mb-4">
              For property management companies and resellers who need custom branding and multi-HOA management.
            </p>
            <Button
              onClick={() => window.open('mailto:sales@civicloghoa.com?subject=White-Label Inquiry', '_blank')}
              variant="outline"
              className="border-purple-300 text-purple-700 hover:bg-purple-50"
            >
              Contact Sales Team
            </Button>
          </div>
        </div>
      </div>

      {/* Usage Statistics */}
      {subscription && (
        <div className="bg-white shadow rounded-lg p-6">
          <h2 className="text-lg font-medium text-gray-900 mb-4">Usage This Month</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
              <div className="flex items-center">
                <Zap className="h-5 w-5 text-blue-500 mr-3" />
                <div>
                  <p className="text-sm font-medium text-gray-900">Violations</p>
                  <p className="text-sm text-gray-500">
                    {subscription.limits.violations_per_month === -1 
                      ? 'Unlimited' 
                      : `${0} / ${subscription.limits.violations_per_month}`
                    }
                  </p>
                </div>
              </div>
              <div className="text-right">
                <div className="text-sm font-medium text-gray-900">
                  {subscription.limits.violations_per_month === -1 ? '∞' : '0%'}
                </div>
              </div>
            </div>

            <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
              <div className="flex items-center">
                <Users className="h-5 w-5 text-green-500 mr-3" />
                <div>
                  <p className="text-sm font-medium text-gray-900">Users</p>
                  <p className="text-sm text-gray-500">
                    {subscription.limits.users === -1 
                      ? 'Unlimited' 
                      : `${0} / ${subscription.limits.users}`
                    }
                  </p>
                </div>
              </div>
              <div className="text-right">
                <div className="text-sm font-medium text-gray-900">
                  {subscription.limits.users === -1 ? '∞' : '0%'}
                </div>
              </div>
            </div>

            <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
              <div className="flex items-center">
                <CreditCard className="h-5 w-5 text-purple-500 mr-3" />
                <div>
                  <p className="text-sm font-medium text-gray-900">HOAs</p>
                  <p className="text-sm text-gray-500">
                    {subscription.limits.hoas === -1 
                      ? 'Unlimited' 
                      : `${0} / ${subscription.limits.hoas}`
                    }
                  </p>
                </div>
              </div>
              <div className="text-right">
                <div className="text-sm font-medium text-gray-900">
                  {subscription.limits.hoas === -1 ? '∞' : '0%'}
                </div>
              </div>
            </div>

            <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
              <div className="flex items-center">
                <Calendar className="h-5 w-5 text-orange-500 mr-3" />
                <div>
                  <p className="text-sm font-medium text-gray-900">Units</p>
                  <p className="text-sm text-gray-500">
                    {subscription.limits.units === -1 
                      ? 'Unlimited' 
                      : `${0} / ${subscription.limits.units}`
                    }
                  </p>
                </div>
              </div>
              <div className="text-right">
                <div className="text-sm font-medium text-gray-900">
                  {subscription.limits.units === -1 ? '∞' : '0%'}
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Error Message */}
      {error && (
        <div className="rounded-md bg-red-50 p-4">
          <div className="flex">
            <AlertCircle className="h-5 w-5 text-red-400" />
            <div className="ml-3">
              <h3 className="text-sm font-medium text-red-800">Error</h3>
              <div className="mt-2 text-sm text-red-700">{error}</div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
} 