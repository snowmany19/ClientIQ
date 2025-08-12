'use client';

import React from 'react';
import Link from 'next/link';

export default function CTASection() {
  return (
    <div className="bg-slate-800">
      <div className="max-w-7xl mx-auto py-12 px-4 sm:px-6 lg:py-16 lg:px-8 lg:flex lg:items-center lg:justify-between">
        <h2 className="text-3xl font-extrabold tracking-tight text-white sm:text-4xl">
          <span className="block">Ready to get started?</span>
          <span className="block text-emerald-200">Transform your contract review today.</span>
        </h2>
        <p className="mt-4 text-lg text-slate-200">
          Professional contract review starting at $199/month
        </p>
        <div className="mt-8 flex lg:mt-0 lg:flex-shrink-0">
          <div className="inline-flex rounded-md shadow">
            <Link
              href="/register"
              className="inline-flex items-center justify-center px-5 py-3 border border-transparent text-base font-medium rounded-md text-slate-800 bg-white hover:bg-gray-50"
            >
              Get Started
            </Link>
          </div>
          <div className="ml-3 inline-flex rounded-md shadow">
            <Link
              href="/login"
              className="inline-flex items-center justify-center px-5 py-3 border border-transparent text-base font-medium rounded-md text-white bg-emerald-600 hover:bg-emerald-700"
            >
              Sign in
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
} 