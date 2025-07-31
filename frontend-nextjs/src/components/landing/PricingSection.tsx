'use client';

import React from 'react';
import Link from 'next/link';
import { PRICING_TIERS } from '@/lib/pricing';

const getPlanFeatures = (planName: string) => {
  const baseFeatures = [
    'Mobile violation capture',
    'AI-powered analysis',
    'Professional PDF reports',
    'Automated notifications',
    'Resident portal',
    'Analytics dashboard',
    'User management',
    'Email support'
  ];

  switch (planName) {
    case 'Starter':
      return baseFeatures;
    case 'Business':
      return [...baseFeatures, 'Advanced reporting', 'Priority support'];
    case 'Pro':
      return [...baseFeatures, 'Advanced reporting', 'Priority support', 'Custom branding', 'API access'];
    case 'Enterprise':
      return [...baseFeatures, 'Advanced reporting', 'Priority support', 'Custom branding', 'API access', 'Dedicated account manager', 'Custom integrations'];
    case 'White Label':
      return [...baseFeatures, 'Advanced reporting', 'Priority support', 'Custom branding', 'API access', 'Dedicated account manager', 'Custom integrations', 'White-label solution', 'Multi-tenant support'];
    default:
      return baseFeatures;
  }
};

export default function PricingSection() {
  return (
    <div className="bg-gray-50 py-12" id="pricing">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center">
          <h2 className="text-3xl font-extrabold text-gray-900 sm:text-4xl">
            Simple, transparent pricing
          </h2>
          <p className="mt-4 text-lg text-gray-600">
            Choose the plan that fits your HOA's needs. All plans include our core features.
          </p>
        </div>

        <div className="mt-12 grid gap-8 lg:grid-cols-5 lg:gap-x-8">
          {PRICING_TIERS.map((tier, index) => {
            const features = getPlanFeatures(tier.name);
            const isPopular = tier.name === 'Business';
            const isWhiteLabel = tier.name === 'White Label';

            return (
              <div
                key={tier.name}
                className={`relative bg-white rounded-lg shadow-lg divide-y divide-gray-200 ${
                  isPopular ? 'ring-2 ring-blue-500' : ''
                }`}
              >
                {isPopular && (
                  <div className="absolute top-0 left-1/2 transform -translate-x-1/2 -translate-y-1/2">
                    <span className="inline-flex rounded-full bg-blue-600 px-4 py-1 text-sm font-semibold tracking-wide uppercase text-white">
                      Most Popular
                    </span>
                  </div>
                )}

                <div className="p-6">
                  <h3 className="text-lg font-medium text-gray-900">{tier.name}</h3>
                  <p className="mt-4 text-sm text-gray-500">{tier.description}</p>
                  <p className="mt-8">
                    <span className="text-4xl font-extrabold text-gray-900">
                      {typeof tier.price === 'number' ? `$${tier.price}` : tier.price}
                    </span>
                    {typeof tier.price === 'number' && (
                      <span className="text-base font-medium text-gray-500">/month</span>
                    )}
                  </p>
                  
                  {/* Limits Display */}
                  <div className="mt-6 space-y-2">
                    <div className="text-sm text-gray-600">
                      <span className="font-medium">HOAs:</span> {tier.hoaLimit}
                    </div>
                    <div className="text-sm text-gray-600">
                      <span className="font-medium">Units:</span> {tier.unitLimit}
                    </div>
                    <div className="text-sm text-gray-600">
                      <span className="font-medium">Users:</span> {tier.userLimit}
                    </div>
                  </div>

                  <Link
                    href={isWhiteLabel ? '/contact' : '/register'}
                    className={`mt-8 block w-full bg-blue-600 border border-transparent rounded-md py-2 text-sm font-semibold text-white text-center hover:bg-blue-700 ${
                      isPopular ? 'bg-blue-600 hover:bg-blue-700' : 'bg-gray-800 hover:bg-gray-900'
                    }`}
                  >
                    {isWhiteLabel ? 'Contact Sales' : 'Get Started'}
                  </Link>
                </div>
                <div className="pt-6 pb-8 px-6">
                  <h4 className="text-sm font-medium text-gray-900 tracking-wide uppercase">What's included</h4>
                  <ul className="mt-6 space-y-4">
                    {features.map((feature) => (
                      <li key={feature} className="flex space-x-3">
                        <svg
                          className="flex-shrink-0 h-5 w-5 text-green-500"
                          fill="currentColor"
                          viewBox="0 0 20 20"
                        >
                          <path
                            fillRule="evenodd"
                            d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                            clipRule="evenodd"
                          />
                        </svg>
                        <span className="text-sm text-gray-500">{feature}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
} 