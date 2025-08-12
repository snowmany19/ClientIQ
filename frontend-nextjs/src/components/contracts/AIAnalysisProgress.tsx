'use client';

import { useState, useEffect } from 'react';
import { 
  Brain, 
  FileText, 
  AlertTriangle, 
  CheckCircle, 
  Clock,
  TrendingUp,
  Shield,
  Target
} from 'lucide-react';

interface AIAnalysisProgressProps {
  isAnalyzing: boolean;
  progress: number;
  currentStep: string;
  estimatedTime?: number;
  onCancel?: () => void;
}

const ANALYSIS_STEPS = [
  { key: 'extracting', label: 'Extracting Text', icon: FileText, description: 'Reading and processing contract documents' },
  { key: 'analyzing', label: 'AI Analysis', icon: Brain, description: 'Analyzing contract terms and identifying risks' },
  { key: 'assessing', label: 'Risk Assessment', icon: AlertTriangle, description: 'Evaluating risk levels and business impact' },
  { key: 'suggesting', label: 'Generating Suggestions', icon: Target, description: 'Creating improvement recommendations' },
  { key: 'compliance', label: 'Compliance Check', icon: Shield, description: 'Checking regulatory compliance' },
  { key: 'summarizing', label: 'Final Summary', icon: TrendingUp, description: 'Compiling comprehensive analysis report' }
];

export default function AIAnalysisProgress({ 
  isAnalyzing, 
  progress, 
  currentStep, 
  estimatedTime = 120,
  onCancel 
}: AIAnalysisProgressProps) {
  const [timeElapsed, setTimeElapsed] = useState(0);
  const [currentStepIndex, setCurrentStepIndex] = useState(0);

  useEffect(() => {
    if (isAnalyzing) {
      const timer = setInterval(() => {
        setTimeElapsed(prev => prev + 1);
      }, 1000);
      return () => clearInterval(timer);
    } else {
      setTimeElapsed(0);
    }
  }, [isAnalyzing]);

  useEffect(() => {
    if (currentStep) {
      const stepIndex = ANALYSIS_STEPS.findIndex(step => step.key === currentStep);
      if (stepIndex !== -1) {
        setCurrentStepIndex(stepIndex);
      }
    }
  }, [currentStep]);

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const getProgressColor = (stepIndex: number) => {
    if (stepIndex < currentStepIndex) return 'bg-green-500';
    if (stepIndex === currentStepIndex) return 'bg-blue-500';
    return 'bg-gray-200';
  };

  const getStepIcon = (step: typeof ANALYSIS_STEPS[0], stepIndex: number) => {
    const Icon = step.icon;
    if (stepIndex < currentStepIndex) {
      return <CheckCircle className="h-5 w-5 text-green-500" />;
    }
    if (stepIndex === currentStepIndex) {
      return <Icon className="h-5 w-5 text-blue-500 animate-pulse" />;
    }
    return <Icon className="h-5 w-5 text-gray-400" />;
  };

  if (!isAnalyzing) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl p-6 max-w-2xl w-full mx-4">
        {/* Header */}
        <div className="text-center mb-6">
          <div className="flex items-center justify-center mb-4">
            <div className="relative">
              <Brain className="h-12 w-12 text-blue-600 animate-pulse" />
              <div className="absolute -top-1 -right-1 w-4 h-4 bg-green-500 rounded-full animate-ping"></div>
            </div>
          </div>
          <h3 className="text-xl font-semibold text-gray-900 mb-2">
            AI Contract Analysis in Progress
          </h3>
          <p className="text-gray-600">
            Our AI is carefully analyzing your contract for risks, opportunities, and insights
          </p>
        </div>

        {/* Progress Bar */}
        <div className="mb-6">
          <div className="flex justify-between text-sm text-gray-600 mb-2">
            <span>Overall Progress</span>
            <span>{Math.round(progress)}%</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-3">
            <div 
              className="bg-gradient-to-r from-blue-500 to-green-500 h-3 rounded-full transition-all duration-500 ease-out"
              style={{ width: `${progress}%` }}
            ></div>
          </div>
        </div>

        {/* Analysis Steps */}
        <div className="space-y-4 mb-6">
          {ANALYSIS_STEPS.map((step, index) => (
            <div key={step.key} className="flex items-center space-x-3">
              <div className="flex-shrink-0">
                {getStepIcon(step, index)}
              </div>
              <div className="flex-1">
                <div className="flex items-center justify-between">
                  <span className={`font-medium ${
                    index <= currentStepIndex ? 'text-gray-900' : 'text-gray-500'
                  }`}>
                    {step.label}
                  </span>
                  {index < currentStepIndex && (
                    <CheckCircle className="h-4 w-4 text-green-500" />
                  )}
                </div>
                <p className={`text-sm ${
                  index <= currentStepIndex ? 'text-gray-600' : 'text-gray-400'
                }`}>
                  {step.description}
                </p>
              </div>
            </div>
          ))}
        </div>

        {/* Time and Stats */}
        <div className="grid grid-cols-2 gap-4 mb-6">
          <div className="bg-gray-50 rounded-lg p-4 text-center">
            <Clock className="h-6 w-6 text-gray-500 mx-auto mb-2" />
            <div className="text-2xl font-semibold text-gray-900">
              {formatTime(timeElapsed)}
            </div>
            <div className="text-sm text-gray-600">Time Elapsed</div>
          </div>
          <div className="bg-gray-50 rounded-lg p-4 text-center">
            <Target className="h-6 w-6 text-gray-500 mx-auto mb-2" />
            <div className="text-2xl font-semibold text-gray-900">
              {formatTime(estimatedTime)}
            </div>
            <div className="text-sm text-gray-600">Estimated Total</div>
          </div>
        </div>

        {/* Fun Facts */}
        <div className="bg-blue-50 rounded-lg p-4 mb-6">
          <div className="flex items-center space-x-2 text-blue-800">
            <Brain className="h-4 w-4" />
            <span className="text-sm font-medium">AI Insight</span>
          </div>
          <p className="text-sm text-blue-700 mt-1">
            Our AI has analyzed thousands of contracts and can identify patterns that human reviewers might miss.
          </p>
        </div>

        {/* Cancel Button */}
        {onCancel && (
          <div className="text-center">
            <button
              onClick={onCancel}
              className="px-4 py-2 text-sm font-medium text-gray-600 hover:text-gray-800 border border-gray-300 rounded-md hover:bg-gray-50 transition-colors"
            >
              Cancel Analysis
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
