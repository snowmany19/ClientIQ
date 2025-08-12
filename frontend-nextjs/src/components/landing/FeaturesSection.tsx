'use client';

import React from 'react';

const features = [
  {
    title: 'Contract Upload & Analysis',
    description: 'Upload contracts in any format and get instant AI-powered analysis and insights.',
    image: '📄',
  },
  {
    title: 'AI-Powered Risk Assessment',
    description: 'Automatic identification of legal risks, compliance issues, and contract anomalies.',
    image: '🤖',
  },
  {
    title: 'Professional Review Reports',
    description: 'Generate comprehensive PDF reports with risk analysis, recommendations, and legal insights.',
    image: '📊',
  },
  {
    title: 'Collaborative Review',
    description: 'Share contracts with team members and stakeholders for collaborative review.',
    image: '👥',
  },
];

export default function FeaturesSection() {
  return (
    <div className="py-12 bg-white" id="features">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="lg:text-center">
          <h2 className="text-base text-emerald-600 font-semibold tracking-wide uppercase">Features</h2>
          <p className="mt-2 text-3xl leading-8 font-extrabold tracking-tight text-gray-900 sm:text-4xl">
            Everything you need for professional contract review
          </p>
          <p className="mt-4 max-w-2xl text-xl text-gray-500 lg:mx-auto">
            Streamline your contract review process with our comprehensive platform designed specifically for legal professionals.
          </p>
        </div>

        <div className="mt-10">
          <dl className="space-y-10 md:space-y-0 md:grid md:grid-cols-2 md:gap-x-8 md:gap-y-10">
            {features.map((feature) => (
              <div key={feature.title} className="relative">
                <dt>
                  <div className="absolute flex items-center justify-center h-12 w-12 rounded-md bg-slate-700 text-white">
                    <span className="text-2xl">{feature.image}</span>
                  </div>
                  <p className="ml-16 text-lg leading-6 font-medium text-gray-900">{feature.title}</p>
                </dt>
                <dd className="mt-2 ml-16 text-base text-gray-500">{feature.description}</dd>
              </div>
            ))}
          </dl>
        </div>

        <div className="mt-16 bg-gray-50 rounded-lg p-8">
          <div className="text-center">
            <h3 className="text-2xl font-bold text-gray-900 mb-4">
              Ready to transform your contract review process?
            </h3>
            <p className="text-lg text-gray-600 mb-6">
              Join hundreds of legal professionals already using ContractGuard.ai to streamline their contract review.
            </p>
            <div className="flex justify-center space-x-4">
              <a
                href="/register"
                className="bg-slate-800 hover:bg-slate-900 text-white px-6 py-3 rounded-md text-sm font-medium"
              >
                Get Started
              </a>
              <a
                href="/demo"
                className="bg-emerald-600 hover:bg-emerald-700 text-white px-6 py-3 rounded-md text-sm font-medium"
              >
                Request Demo
              </a>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
} 