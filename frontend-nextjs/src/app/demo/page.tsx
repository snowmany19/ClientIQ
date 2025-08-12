'use client';

import { useState } from 'react';
import Link from 'next/link';
import { Button } from '@/components/ui/Button';
import { Card } from '@/components/ui/card';
import { apiClient } from '@/lib/api';
import { 
  Play, 
  ArrowRight, 
  Camera, 
  FileText, 
  Bell, 
  CheckCircle,
  Mail,
  Shield,
  BarChart3,
  Users,
  Settings,
  Star
} from 'lucide-react';

const testimonials = [
  {
    name: "Sarah Johnson",
    role: "General Counsel",
    company: "TechCorp Inc.",
            content: "ContractGuard.ai has transformed how we review contracts. The AI analysis saves us hours every week, and the risk assessment reports have improved our compliance significantly.",
    rating: 5
  },
  {
    name: "Michael Chen",
    role: "Legal Operations Manager",
    company: "Riverside Legal",
    content: "The contract upload feature is incredible. We can analyze contracts in any format and get instant insights. The AI analysis is spot-on every time.",
    rating: 5
  },
  {
    name: "Lisa Rodriguez",
    role: "Contract Manager",
    company: "Oakwood Enterprises",
    content: "The collaborative review feature has dramatically reduced our review time. Team members can comment, track changes, and communicate directly through the platform.",
    rating: 5
  },
  {
    name: "David Thompson",
    role: "Legal Director",
    company: "Pine Valley Corp",
    content: "The analytics dashboard gives us insights we never had before. We can track contract trends, identify risk patterns, and make data-driven decisions about negotiations.",
    rating: 5
  },
  {
    name: "Jennifer Williams",
    role: "Senior Counsel",
    company: "Maple Ridge Law",
    content: "Setting up was incredibly easy. The team walked us through everything, and we were up and running in less than a day. The support has been outstanding.",
    rating: 5
  },
  {
    name: "Robert Kim",
    role: "Legal Analyst",
    company: "Greenfield Legal",
    content: "The platform is intuitive and powerful. I can analyze contracts, generate reports, and track negotiations all from one place. It's made my job so much more efficient.",
    rating: 5
  }
];

const demoSteps = [
  {
    title: "Contract Upload",
    description: "Upload contracts in any format (PDF, Word, etc.)",
    demo: "/dashboard/contracts"
  },
  {
    title: "AI Analysis",
    description: "AI automatically analyzes contracts for risks and compliance issues",
    demo: "/dashboard/contracts"
  },
  {
    title: "Risk Assessment",
    description: "Generate comprehensive risk analysis and recommendations",
    demo: "/dashboard/contracts"
  },
  {
    title: "Collaborative Review",
    description: "Share contracts with team members for review and comments",
    demo: "/dashboard/contracts"
  },
  {
    title: "Report Generation",
    description: "Create professional PDF reports with findings and insights",
    demo: "/dashboard/contracts"
  }
];

export default function DemoPage() {
  const [activeTab, setActiveTab] = useState('overview');
  const [demoForm, setDemoForm] = useState({
    name: '',
    email: '',
    company: '',
    phone: '',
    message: ''
  });
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitMessage, setSubmitMessage] = useState<{ type: 'success' | 'error', text: string } | null>(null);

  const handleDemoRequest = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    setSubmitMessage(null);
    
    try {
      const response = await apiClient.submitDemoRequest(demoForm);
      setSubmitMessage({ type: 'success', text: response.message });
      setDemoForm({ name: '', email: '', company: '', phone: '', message: '' });
    } catch (error: any) {
      setSubmitMessage({ 
        type: 'error', 
        text: error.message || 'Failed to submit demo request. Please try again.' 
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleLiveDemoRequest = () => {
    const subject = encodeURIComponent('Request for Live Demo - ContractGuard.ai');
    const body = encodeURIComponent(`Hello,

      I'm interested in scheduling a live demo of ContractGuard.ai for our contract management needs.

Please contact me to arrange a personalized demonstration of the platform.

Best regards,
[Your Name]`);
    
            window.open(`mailto:sales@contractguard.ai?subject=${subject}&body=${body}`, '_blank');
  };

  const renderStars = (rating: number) => {
    return Array.from({ length: 5 }, (_, i) => (
      <Star
        key={i}
        className={`h-4 w-4 ${
          i < rating ? 'text-yellow-400 fill-current' : 'text-gray-300'
        }`}
      />
    ));
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div className="flex items-center">
              <Link href="/" className="text-2xl font-bold text-blue-600">
                ContractGuard.ai
              </Link>
            </div>
            <div className="flex items-center space-x-4">
              <Link href="/login">
                <Button variant="outline">Sign In</Button>
              </Link>
              <Link href="/register">
                <Button>Get Started</Button>
              </Link>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {/* Hero Section */}
        <div className="text-center mb-12">
          <h1 className="text-4xl md:text-5xl font-bold text-gray-900 mb-6">
            See ContractGuard.ai in Action
          </h1>
          <p className="text-xl text-gray-700 mb-8 max-w-3xl mx-auto">
            Discover how our platform streamlines contract review from upload to final approval
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Button 
              size="lg" 
              className="flex items-center"
              onClick={() => {
                window.open('https://www.youtube.com/watch?v=dQw4w9WgXcQ', '_blank');
              }}
            >
              <Play className="h-5 w-5 mr-2" />
              Watch Demo Video
            </Button>
            <Button 
              variant="outline"
              size="lg"
              className="flex items-center"
              onClick={handleLiveDemoRequest}
            >
              <Mail className="h-5 w-5 mr-2" />
              Request Live Demo
            </Button>
          </div>
        </div>

        {/* Tab Navigation */}
        <div className="flex justify-center mb-8">
          <div className="flex space-x-1 bg-white rounded-lg p-1 shadow-sm">
            {[
              { id: 'overview', label: 'Overview' },
              { id: 'testimonials', label: 'Testimonials' },
              { id: 'workflow', label: 'Workflow' },
              { id: 'request', label: 'Request Demo' }
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                  activeTab === tab.id
                    ? 'bg-blue-600 text-white'
                    : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
                }`}
              >
                {tab.label}
              </button>
            ))}
          </div>
        </div>

        {/* Tab Content */}
        <div className="bg-white rounded-lg shadow-lg p-8">
          {activeTab === 'overview' && (
            <div className="space-y-12">
              <div className="text-center">
                <h2 className="text-3xl font-bold text-gray-900 mb-4">
                  Complete Contract Management
                </h2>
                <p className="text-xl text-gray-700 mb-8 max-w-3xl mx-auto">
                                       See how ContractGuard.ai streamlines the entire contract review process from upload to analysis, 
                       saving time and ensuring compliance.
                </p>
              </div>

              {/* Key Benefits */}
              <div className="grid md:grid-cols-3 gap-8">
                <Card className="p-6 text-center">
                  <Shield className="h-12 w-12 text-blue-600 mx-auto mb-4" />
                  <h3 className="text-lg font-semibold mb-2 text-gray-900">Compliance & Security</h3>
                  <p className="text-gray-700">
                    Ensure regulatory compliance with secure, auditable violation tracking
                  </p>
                </Card>
                <Card className="p-6 text-center">
                  <BarChart3 className="h-12 w-12 text-blue-600 mx-auto mb-4" />
                  <h3 className="text-lg font-semibold mb-2 text-gray-900">Analytics & Insights</h3>
                  <p className="text-gray-700">
                    Make data-driven decisions with comprehensive reporting and analytics
                  </p>
                </Card>
                <Card className="p-6 text-center">
                  <Settings className="h-12 w-12 text-blue-600 mx-auto mb-4" />
                  <h3 className="text-lg font-semibold mb-2 text-gray-900">Easy Management</h3>
                  <p className="text-gray-700">
                    Streamline operations with automated workflows and user-friendly interface
                  </p>
                </Card>
              </div>

              {/* Call to Action */}
              <div className="text-center">
                <h3 className="text-2xl font-bold mb-4 text-gray-900">
                  Ready to Transform Your Contract Review Process?
                </h3>
                <p className="text-gray-700 mb-6">
                  Schedule a personalized demo to see how ContractGuard.ai can work for your community
                </p>
                <Button 
                  size="lg"
                  className="flex items-center mx-auto"
                  onClick={handleLiveDemoRequest}
                >
                  <Mail className="h-4 w-4 mr-2" />
                  Request Live Demo
                  <ArrowRight className="h-4 w-4 ml-2" />
                </Button>
              </div>
            </div>
          )}

          {activeTab === 'testimonials' && (
            <div className="space-y-8">
              <div className="text-center mb-12">
                <h2 className="text-3xl font-bold text-gray-900 mb-4">What Our Customers Say</h2>
                <p className="text-xl text-gray-700">
                  Hear from legal professionals who have transformed their contract review process with ContractGuard.ai
                </p>
              </div>
              <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
                {testimonials.map((testimonial, index) => (
                  <Card key={index} className="p-6 hover:shadow-lg transition-shadow">
                    <div className="flex items-center mb-4">
                      <div className="flex">
                        {renderStars(testimonial.rating)}
                      </div>
                    </div>
                    <p className="text-gray-700 mb-4 italic">"{testimonial.content}"</p>
                    <div className="border-t pt-4">
                      <p className="font-semibold text-gray-900">{testimonial.name}</p>
                      <p className="text-sm text-gray-600">{testimonial.role}</p>
                      <p className="text-sm text-blue-600">{testimonial.company}</p>
                    </div>
                  </Card>
                ))}
              </div>
            </div>
          )}

          {activeTab === 'workflow' && (
            <div className="space-y-8">
              <div className="text-center mb-12">
                <h2 className="text-3xl font-bold text-gray-900 mb-4">Complete Workflow</h2>
                <p className="text-xl text-gray-700">
                  See how violations flow through the system from discovery to resolution
                </p>
              </div>
              <div className="space-y-12">
                {demoSteps.map((step, index) => (
                  <div key={index} className="flex items-center space-x-8">
                    <div className="flex-shrink-0">
                      <div className="w-16 h-16 bg-blue-600 text-white rounded-full flex items-center justify-center font-bold text-xl">
                        {index + 1}
                      </div>
                    </div>
                    <div className="flex-1">
                      <h3 className="text-xl font-semibold mb-2 text-gray-900">{step.title}</h3>
                      <p className="text-gray-700 mb-4">{step.description}</p>
                      <Button 
                        variant="outline" 
                        size="sm"
                        onClick={() => {
                          if (step.demo) {
                            window.open(step.demo, '_blank');
                          }
                        }}
                      >
                        View Demo
                      </Button>
                    </div>
                    <div className="flex-shrink-0">
                      <div className="w-48 h-32 bg-gray-200 rounded-lg flex items-center justify-center">
                        <Camera className="h-12 w-12 text-gray-400" />
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {activeTab === 'request' && (
            <div className="max-w-2xl mx-auto">
              <div className="text-center mb-8">
                <h2 className="text-3xl font-bold text-gray-900 mb-4">Request a Live Demo</h2>
                <p className="text-xl text-gray-700">
                  Get a personalized demonstration of ContractGuard.ai tailored to your contract management needs
                </p>
              </div>
              
              <form onSubmit={handleDemoRequest} className="space-y-6">
                <div className="grid md:grid-cols-2 gap-6">
                  <div>
                    <label htmlFor="name" className="block text-sm font-medium text-gray-700 mb-2">
                      Full Name *
                    </label>
                    <input
                      type="text"
                      id="name"
                      required
                      value={demoForm.name}
                      onChange={(e) => setDemoForm({ ...demoForm, name: e.target.value })}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                    />
                  </div>
                  <div>
                    <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-2">
                      Email Address *
                    </label>
                    <input
                      type="email"
                      id="email"
                      required
                      value={demoForm.email}
                      onChange={(e) => setDemoForm({ ...demoForm, email: e.target.value })}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                    />
                  </div>
                </div>
                
                <div className="grid md:grid-cols-2 gap-6">
                  <div>
                    <label htmlFor="company" className="block text-sm font-medium text-gray-700 mb-2">
                      Company Name
                    </label>
                    <input
                      type="text"
                      id="company"
                      value={demoForm.company}
                      onChange={(e) => setDemoForm({ ...demoForm, company: e.target.value })}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                    />
                  </div>
                  <div>
                    <label htmlFor="phone" className="block text-sm font-medium text-gray-700 mb-2">
                      Phone Number
                    </label>
                    <input
                      type="tel"
                      id="phone"
                      value={demoForm.phone}
                      onChange={(e) => setDemoForm({ ...demoForm, phone: e.target.value })}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                    />
                  </div>
                </div>
                
                <div>
                  <label htmlFor="message" className="block text-sm font-medium text-gray-700 mb-2">
                    Additional Information
                  </label>
                  <textarea
                    id="message"
                    rows={4}
                    value={demoForm.message}
                    onChange={(e) => setDemoForm({ ...demoForm, message: e.target.value })}
                                            placeholder="Tell us about your contract management needs, current challenges, or any questions you have..."
                    className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>

                {submitMessage && (
                  <div className={`p-4 rounded-md ${
                    submitMessage.type === 'success' 
                      ? 'bg-green-50 border border-green-200 text-green-800' 
                      : 'bg-red-50 border border-red-200 text-red-800'
                  }`}>
                    {submitMessage.text}
                  </div>
                )}

                <Button type="submit" className="w-full" disabled={isSubmitting}>
                  {isSubmitting ? 'Submitting...' : 'Request Live Demo'}
                </Button>
              </form>
            </div>
          )}
        </div>
      </div>
    </div>
  );
} 