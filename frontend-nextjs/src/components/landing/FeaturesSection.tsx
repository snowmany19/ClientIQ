'use client';

import React from 'react';

const features = [
  {
    title: 'Mobile Violation Capture',
    description: 'Capture violations on-site with photos, GPS coordinates, and detailed notes using our mobile-optimized interface.',
    image: '📱',
  },
  {
    title: 'AI-Powered Analysis',
    description: 'Our advanced AI automatically categorizes violations, generates summaries, and identifies repeat offenders.',
    image: '🤖',
  },
  {
    title: 'Professional Reporting',
    description: 'Generate comprehensive PDF reports with photos, maps, and detailed violation information for legal compliance.',
    image: '📄',
  },
  {
    title: 'Automated Communication',
    description: 'Send professional violation notifications automatically with customizable templates and delivery tracking.',
    image: '📧',
  },
];

export default function FeaturesSection() {
  return (
    <div className="py-12 bg-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="lg:text-center">
          <h2 className="text-base text-blue-600 font-semibold tracking-wide uppercase">How it works</h2>
          <p className="mt-2 text-3xl leading-8 font-extrabold tracking-tight text-gray-900 sm:text-4xl">
            Streamline your violation management process
          </p>
          <p className="mt-4 max-w-2xl text-xl text-gray-500 lg:mx-auto">
            From initial violation capture to final resolution, CivicLogHOA provides a complete workflow 
            that saves time and ensures compliance.
          </p>
        </div>

        <div className="mt-10">
          <div className="space-y-10 md:space-y-0 md:grid md:grid-cols-2 md:gap-x-8 md:gap-y-10">
            {features.map((feature, index) => (
              <div key={index} className="relative">
                <div className="absolute flex items-center justify-center h-12 w-12 rounded-md bg-blue-500 text-white text-2xl">
                  {feature.image}
                </div>
                <div className="ml-16">
                  <h3 className="text-lg leading-6 font-medium text-gray-900">{feature.title}</h3>
                  <p className="mt-2 text-base text-gray-500">{feature.description}</p>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="mt-16 bg-gray-50 rounded-lg p-8">
          <div className="text-center">
            <h3 className="text-2xl font-bold text-gray-900 mb-4">
              Ready to transform your HOA management?
            </h3>
            <p className="text-lg text-gray-600 mb-6">
              Join hundreds of HOAs already using CivicLogHOA to streamline their violation management.
            </p>
            <div className="flex justify-center space-x-4">
              <a
                href="/register"
                className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-md text-sm font-medium"
              >
                Start Free Trial
              </a>
              <a
                href="/demo"
                className="bg-gray-800 hover:bg-gray-900 text-white px-6 py-3 rounded-md text-sm font-medium"
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