'use client';

import React from 'react';
import Link from 'next/link';

const plans = [
  {
    name: 'Starter',
    price: '$199',
    period: '/month',
    description: 'Perfect for small HOAs getting started',
    features: [
      'Up to 100 homes',
      'Basic violation tracking',
      'Standard letter generation',
      'Email support',
      'Standard reports',
      '3 users included',
      '50 violations per month',
      '5GB storage',
    ],
    cta: 'Start Free Trial',
    popular: false,
  },
  {
    name: 'Professional',
    price: '$499',
    period: '/month',
    description: 'Ideal for growing HOAs with advanced needs',
    features: [
      'Up to 500 homes',
      'Advanced analytics & reporting',
      'AI-powered letter generation',
      'Priority support',
      'Custom integrations',
      '10 users included',
      '200 violations per month',
      '20GB storage',
    ],
    cta: 'Start Free Trial',
    popular: true,
  },
  {
    name: 'Enterprise',
    price: '$999',
    period: '/month',
    description: 'For large HOAs and property management companies',
    features: [
      'Unlimited homes',
      'Full feature suite',
      'Dedicated account manager',
      'Custom integrations',
      'Advanced compliance tools',
      '50 users included',
      '1000 violations per month',
      '100GB storage',
    ],
    cta: 'Contact Sales',
    popular: false,
  },
];

export default function PricingSection() {
  return (
    <div className="bg-white py-12" id="pricing">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="sm:text-center">
          <h2 className="text-base text-blue-600 font-semibold tracking-wide uppercase">Pricing</h2>
          <p className="mt-2 text-3xl leading-8 font-extrabold tracking-tight text-gray-900 sm:text-4xl">
            Simple, transparent pricing
          </p>
          <p className="mt-4 max-w-2xl text-xl text-gray-500 lg:mx-auto">
            Choose the plan that fits your HOA's needs. All plans include a 14-day free trial.
          </p>
        </div>

        <div className="mt-12 space-y-4 sm:mt-16 sm:space-y-0 sm:grid sm:grid-cols-2 sm:gap-6 lg:max-w-4xl lg:mx-auto xl:max-w-none xl:mx-0 xl:grid-cols-3">
          {plans.map((plan, index) => (
            <div
              key={index}
              className={`border border-gray-200 rounded-lg shadow-sm divide-y divide-gray-200 bg-white ${
                plan.popular ? 'ring-2 ring-blue-500' : ''
              }`}
            >
              <div className="p-6">
                {plan.popular && (
                  <div className="mb-4">
                    <span className="inline-flex px-4 py-1 text-sm font-semibold text-blue-600 bg-blue-100 rounded-full">
                      Most Popular
                    </span>
                  </div>
                )}
                <h3 className="text-lg leading-6 font-medium text-gray-900">{plan.name}</h3>
                <p className="mt-4 text-sm text-gray-500">{plan.description}</p>
                <p className="mt-8">
                  <span className="text-4xl font-extrabold text-gray-900">{plan.price}</span>
                  <span className="text-base font-medium text-gray-500">{plan.period}</span>
                </p>
                <Link
                  href={plan.name === 'Enterprise' ? '/contact' : '/register'}
                  className={`mt-8 block w-full bg-blue-600 border border-transparent rounded-md py-2 text-sm font-semibold text-white text-center hover:bg-blue-700 ${
                    plan.popular ? 'bg-blue-600 hover:bg-blue-700' : 'bg-gray-800 hover:bg-gray-900'
                  }`}
                >
                  {plan.cta}
                </Link>
              </div>
              <div className="pt-6 pb-8 px-6">
                <h4 className="text-xs font-semibold text-gray-900 tracking-wide uppercase">What's included</h4>
                <ul className="mt-6 space-y-4">
                  {plan.features.map((feature, featureIndex) => (
                    <li key={featureIndex} className="flex space-x-3">
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
          ))}
        </div>

        <div className="mt-12 text-center">
          <p className="text-sm text-gray-500">
            All plans include a 14-day free trial. No credit card required to start.
          </p>
          <p className="mt-2 text-sm text-gray-500">
            Need a custom plan? <Link href="/contact" className="text-blue-600 hover:text-blue-500">Contact us</Link>
          </p>
        </div>
      </div>
    </div>
  );
} 