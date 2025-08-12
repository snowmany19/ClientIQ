'use client';

import { useState } from 'react';
import { 
  AlertTriangle, 
  CheckCircle, 
  FileText, 
  ChevronDown, 
  ChevronRight,
  Shield,
  Target,
  TrendingUp
} from 'lucide-react';
import { ContractAnalysis } from '@/types';

interface AIAnalysisResultsProps {
  analysis: ContractAnalysis;
  contractTitle: string;
}

export default function AIAnalysisResults({ analysis, contractTitle }: AIAnalysisResultsProps) {
  const [expandedSections, setExpandedSections] = useState<Record<string, boolean>>({
    summary: true,
    risks: true,
    suggestions: true,
    compliance: true
  });

  const toggleSection = (section: string) => {
    setExpandedSections(prev => ({
      ...prev,
      [section]: !prev[section]
    }));
  };

  const getRiskColor = (severity: number) => {
    if (severity >= 4) return 'text-red-600 bg-red-50 border-red-200';
    if (severity >= 3) return 'text-orange-600 bg-orange-50 border-orange-200';
    return 'text-yellow-600 bg-yellow-50 border-yellow-200';
  };

  const getRiskIcon = (severity: number) => {
    if (severity >= 4) return <AlertTriangle className="h-5 w-5 text-red-600" />;
    if (severity >= 3) return <AlertTriangle className="h-5 w-5 text-orange-600" />;
    return <AlertTriangle className="h-5 w-5 text-yellow-600" />;
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-50 to-indigo-50 p-6 rounded-lg border border-blue-200">
        <div className="flex items-center space-x-3">
          <div className="p-2 bg-blue-100 rounded-lg">
            <FileText className="h-6 w-6 text-blue-600" />
          </div>
          <div>
            <h2 className="text-xl font-semibold text-gray-900">AI Analysis Results</h2>
            <p className="text-gray-600">Contract: {contractTitle}</p>
          </div>
        </div>
      </div>

      {/* Executive Summary */}
      <div className="bg-white rounded-lg border border-gray-200">
        <button
          onClick={() => toggleSection('summary')}
          className="w-full px-6 py-4 flex items-center justify-between hover:bg-gray-50 transition-colors"
        >
          <div className="flex items-center space-x-3">
            <TrendingUp className="h-5 w-5 text-blue-600" />
            <h3 className="text-lg font-medium text-gray-900">Executive Summary</h3>
          </div>
          {expandedSections.summary ? (
            <ChevronDown className="h-5 w-5 text-gray-500" />
          ) : (
            <ChevronRight className="h-5 w-5 text-gray-500" />
          )}
        </button>
        
        {expandedSections.summary && (
          <div className="px-6 pb-4 border-t border-gray-200">
            <div className="pt-4 space-y-4">
              <div>
                <h4 className="font-medium text-gray-900 mb-2">Summary</h4>
                <p className="text-gray-700">{analysis.summary.executive_summary}</p>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <h4 className="font-medium text-gray-900 mb-2">Key Terms</h4>
                  <ul className="text-sm text-gray-700 space-y-1">
                    {Object.entries(analysis.summary.key_terms).map(([key, value]) => (
                      <li key={key} className="flex justify-between">
                        <span className="font-medium">{key}:</span>
                        <span>{String(value)}</span>
                      </li>
                    ))}
                  </ul>
                </div>
                
                <div>
                  <h4 className="font-medium text-gray-900 mb-2">Critical Dates</h4>
                  <ul className="text-sm text-gray-700 space-y-1">
                    {analysis.summary.critical_dates.map((date, index) => (
                      <li key={index} className="flex items-center space-x-2">
                        <CheckCircle className="h-4 w-4 text-green-500" />
                        <span>{date}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Risk Assessment */}
      <div className="bg-white rounded-lg border border-gray-200">
        <button
          onClick={() => toggleSection('risks')}
          className="w-full px-6 py-4 flex items-center justify-between hover:bg-gray-50 transition-colors"
        >
          <div className="flex items-center space-x-3">
            <AlertTriangle className="h-5 w-5 text-red-600" />
            <h3 className="text-lg font-medium text-gray-900">
              Risk Assessment ({analysis.risks.length} risks identified)
            </h3>
          </div>
          {expandedSections.risks ? (
            <ChevronDown className="h-5 w-5 text-gray-500" />
          ) : (
            <ChevronRight className="h-5 w-5 text-gray-500" />
          )}
        </button>
        
        {expandedSections.risks && (
          <div className="px-6 pb-4 border-t border-gray-200">
            <div className="pt-4 space-y-4">
              {analysis.risks.map((risk, index) => (
                <div key={index} className={`p-4 rounded-lg border ${getRiskColor(risk.severity)}`}>
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex items-center space-x-2">
                      {getRiskIcon(risk.severity)}
                      <span className="font-medium">Risk {index + 1}: {risk.title}</span>
                    </div>
                    <div className="flex items-center space-x-2 text-sm">
                      <span className="px-2 py-1 bg-white rounded-full border">
                        Severity: {risk.severity}/5
                      </span>
                      <span className="px-2 py-1 bg-white rounded-full border">
                        Confidence: {Math.round(risk.confidence * 100)}%
                      </span>
                    </div>
                  </div>
                  
                  <div className="space-y-3">
                    <div>
                      <h5 className="font-medium text-gray-900 mb-1">Description</h5>
                      <p className="text-sm">{risk.description}</p>
                    </div>
                    
                    <div>
                      <h5 className="font-medium text-gray-900 mb-1">Business Impact</h5>
                      <p className="text-sm">{risk.business_impact}</p>
                    </div>
                    
                    <div>
                      <h5 className="font-medium text-gray-900 mb-1">Mitigation Suggestions</h5>
                      <ul className="text-sm space-y-1">
                        {risk.mitigation_suggestions.map((suggestion, idx) => (
                          <li key={idx} className="flex items-start space-x-2">
                            <CheckCircle className="h-4 w-4 text-green-500 mt-0.5 flex-shrink-0" />
                            <span>{suggestion}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Improvement Suggestions */}
      <div className="bg-white rounded-lg border border-gray-200">
        <button
          onClick={() => toggleSection('suggestions')}
          className="w-full px-6 py-4 flex items-center justify-between hover:bg-gray-50 transition-colors"
        >
          <div className="flex items-center space-x-3">
            <Target className="h-5 w-5 text-green-600" />
            <h3 className="text-lg font-medium text-gray-900">
              Improvement Suggestions ({analysis.suggestions.length} suggestions)
            </h3>
          </div>
          {expandedSections.suggestions ? (
            <ChevronDown className="h-5 w-5 text-gray-500" />
          ) : (
            <ChevronRight className="h-5 w-5 text-gray-500" />
          )}
        </button>
        
        {expandedSections.suggestions && (
          <div className="px-6 pb-4 border-t border-gray-200">
            <div className="pt-4 space-y-4">
              {analysis.suggestions.map((suggestion, index) => (
                <div key={index} className="p-4 bg-green-50 rounded-lg border border-green-200">
                  <div className="flex items-center justify-between mb-3">
                    <span className="font-medium text-green-900">
                      Suggestion {index + 1}: {suggestion.category}
                    </span>
                    <span className="px-2 py-1 bg-green-100 text-green-800 rounded-full text-sm font-medium">
                      {suggestion.type}
                    </span>
                  </div>
                  
                  <div className="space-y-3">
                    <div>
                      <h5 className="font-medium text-green-900 mb-1">Suggested Text</h5>
                      <div className="p-3 bg-white rounded border text-sm">
                        {suggestion.suggested_text}
                      </div>
                    </div>
                    
                    <div>
                      <h5 className="font-medium text-green-900 mb-1">Rationale</h5>
                      <p className="text-sm text-green-800">{suggestion.rationale}</p>
                    </div>
                    
                    <div>
                      <h5 className="font-medium text-green-900 mb-1">Negotiation Tips</h5>
                      <ul className="text-sm text-green-800 space-y-1">
                        {suggestion.negotiation_tips.map((tip, idx) => (
                          <li key={idx} className="flex items-start space-x-2">
                            <Target className="h-4 w-4 text-green-600 mt-0.5 flex-shrink-0" />
                            <span>{tip}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Compliance Check */}
      <div className="bg-white rounded-lg border border-gray-200">
        <button
          onClick={() => toggleSection('compliance')}
          className="w-full px-6 py-4 flex items-center justify-between hover:bg-gray-50 transition-colors"
        >
          <div className="flex items-center space-x-3">
            <Shield className="h-5 w-5 text-purple-600" />
            <h3 className="text-lg font-medium text-gray-900">Compliance Check</h3>
          </div>
          {expandedSections.compliance ? (
            <ChevronDown className="h-5 w-5 text-gray-500" />
          ) : (
            <ChevronRight className="h-5 w-5 text-gray-500" />
          )}
        </button>
        
        {expandedSections.compliance && (
          <div className="px-6 pb-4 border-t border-gray-200">
            <div className="pt-4">
              <div className="p-4 bg-purple-50 rounded-lg border border-purple-200">
                <h4 className="font-medium text-purple-900 mb-2">Compliance Status</h4>
                <p className="text-sm text-purple-800">
                  {analysis.compliance?.status || 'Compliance analysis completed'}
                </p>
                
                {analysis.compliance?.issues && (
                  <div className="mt-3">
                    <h5 className="font-medium text-purple-900 mb-2">Issues Found</h5>
                    <ul className="text-sm text-purple-800 space-y-1">
                      {analysis.compliance.issues.map((issue, idx) => (
                        <li key={idx} className="flex items-start space-x-2">
                          <AlertTriangle className="h-4 w-4 text-purple-600 mt-0.5 flex-shrink-0" />
                          <span>{issue}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
