'use client';

import React from 'react';
import HeroSection from './HeroSection';
import ValueProposition from './ValueProposition';
import PricingSection from './PricingSection';
import FeaturesSection from './FeaturesSection';
import CTASection from './CTASection';
import Footer from './Footer';

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-white">
      {/* Navigation */}
      <nav className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <div className="flex items-center">
                  <img 
                    src="/ai_logo.png" 
                    alt="AI Logo" 
                    className="h-8 w-8 object-contain"
                  />
                  <span className="ml-2 text-xl font-bold text-gray-900">ContractGuard.ai</span>
                </div>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <a
                href="/login"
                className="text-gray-600 hover:text-gray-900 px-3 py-2 rounded-md text-sm font-medium"
              >
                Login
              </a>
              <a
                href="#pricing"
                className="bg-slate-800 hover:bg-slate-900 text-white px-4 py-2 rounded-md text-sm font-medium"
              >
                Get Started
              </a>
            </div>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main>
        <HeroSection />
        <ValueProposition />
        <FeaturesSection />
        <PricingSection />
        <CTASection />
      </main>

      <Footer />
    </div>
  );
} 