'use client';

import { useState, useMemo } from 'react';
import { 
  AlertTriangle, 
  TrendingUp, 
  Shield, 
  Target,
  BarChart3,
  PieChart,
  Activity,
  Info
} from 'lucide-react';
import { ContractRisk } from '@/types';

interface RiskVisualizationProps {
  risks: ContractRisk[];
  className?: string;
}

export default function RiskVisualization({ risks, className = '' }: RiskVisualizationProps) {
  const [selectedRisk, setSelectedRisk] = useState<ContractRisk | null>(null);
  const [viewMode, setViewMode] = useState<'chart' | 'list' | 'matrix'>('chart');

  const riskStats = useMemo(() => {
    if (!risks.length) return null;

    const severityCounts = { 1: 0, 2: 0, 3: 0, 4: 0, 5: 0 };
    const categoryCounts: Record<string, number> = {};
    const totalConfidence = risks.reduce((sum, risk) => sum + risk.confidence, 0);
    const highRiskCount = risks.filter(r => r.severity >= 4).length;
    const criticalRiskCount = risks.filter(r => r.severity === 5).length;

    risks.forEach(risk => {
      severityCounts[risk.severity as keyof typeof severityCounts]++;
      categoryCounts[risk.category] = (categoryCounts[risk.category] || 0) + 1;
    });

    return {
      severityCounts,
      categoryCounts,
      averageConfidence: totalConfidence / risks.length,
      highRiskCount,
      criticalRiskCount,
      totalRisks: risks.length
    };
  }, [risks]);

  const getSeverityColor = (severity: number) => {
    switch (severity) {
      case 1: return 'bg-green-100 text-green-800 border-green-200';
      case 2: return 'bg-blue-100 text-blue-800 border-blue-200';
      case 3: return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 4: return 'bg-orange-100 text-orange-800 border-orange-200';
      case 5: return 'bg-red-100 text-red-800 border-red-200';
      default: return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const getSeverityLabel = (severity: number) => {
    switch (severity) {
      case 1: return 'Very Low';
      case 2: return 'Low';
      case 3: return 'Medium';
      case 4: return 'High';
      case 5: return 'Critical';
      default: return 'Unknown';
    }
  };

  if (!risks.length) {
    return (
      <div className={`bg-gray-50 rounded-lg p-6 text-center ${className}`}>
        <Shield className="h-12 w-12 text-gray-400 mx-auto mb-4" />
        <h3 className="text-lg font-medium text-gray-900 mb-2">No Risks Identified</h3>
        <p className="text-gray-600">Great news! No significant risks were found in this contract.</p>
      </div>
    );
  }

  return (
    <div className={`space-y-6 ${className}`}>
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-semibold text-gray-900">Risk Analysis</h3>
          <p className="text-sm text-gray-600">
            {risks.length} risk{risks.length !== 1 ? 's' : ''} identified with AI analysis
          </p>
        </div>
        <div className="flex space-x-2">
          <button
            onClick={() => setViewMode('chart')}
            className={`px-3 py-1 text-sm rounded-md transition-colors ${
              viewMode === 'chart' 
                ? 'bg-blue-100 text-blue-700' 
                : 'text-gray-600 hover:text-gray-800'
            }`}
          >
            <BarChart3 className="h-4 w-4" />
          </button>
          <button
            onClick={() => setViewMode('list')}
            className={`px-3 py-1 text-sm rounded-md transition-colors ${
              viewMode === 'list' 
                ? 'bg-blue-100 text-blue-700' 
                : 'text-gray-600 hover:text-gray-800'
            }`}
          >
            <Activity className="h-4 w-4" />
          </button>
          <button
            onClick={() => setViewMode('matrix')}
            className={`px-3 py-1 text-sm rounded-md transition-colors ${
              viewMode === 'matrix' 
                ? 'bg-blue-100 text-blue-700' 
                : 'text-gray-600 hover:text-gray-800'
            }`}
          >
            <PieChart className="h-4 w-4" />
          </button>
        </div>
      </div>

      {/* Risk Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white rounded-lg border p-4">
          <div className="flex items-center">
            <AlertTriangle className="h-8 w-8 text-red-500" />
            <div className="ml-3">
              <p className="text-sm font-medium text-gray-500">Total Risks</p>
              <p className="text-2xl font-bold text-gray-900">{riskStats?.totalRisks}</p>
            </div>
          </div>
        </div>
        
        <div className="bg-white rounded-lg border p-4">
          <div className="flex items-center">
            <TrendingUp className="h-8 w-8 text-orange-500" />
            <div className="ml-3">
              <p className="text-sm font-medium text-gray-500">High Risk</p>
              <p className="text-2xl font-bold text-orange-600">{riskStats?.highRiskCount}</p>
            </div>
          </div>
        </div>
        
        <div className="bg-white rounded-lg border p-4">
          <div className="flex items-center">
            <Target className="h-8 w-8 text-red-600" />
            <div className="ml-3">
              <p className="text-sm font-medium text-gray-500">Critical</p>
              <p className="text-2xl font-bold text-red-600">{riskStats?.criticalRiskCount}</p>
            </div>
          </div>
        </div>
        
        <div className="bg-white rounded-lg border p-4">
          <div className="flex items-center">
            <Shield className="h-8 w-8 text-blue-500" />
            <div className="ml-3">
              <p className="text-sm font-medium text-gray-500">Avg Confidence</p>
              <p className="text-2xl font-bold text-blue-600">
                {riskStats?.averageConfidence ? Math.round(riskStats.averageConfidence * 100) : 0}%
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* View Modes */}
      {viewMode === 'chart' && (
        <div className="bg-white rounded-lg border p-6">
          <h4 className="text-lg font-medium text-gray-900 mb-4">Risk Distribution by Severity</h4>
          <div className="space-y-4">
            {[5, 4, 3, 2, 1].map(severity => {
              const count = riskStats?.severityCounts[severity as keyof typeof riskStats.severityCounts] || 0;
              const percentage = riskStats ? (count / riskStats.totalRisks) * 100 : 0;
              
              return (
                <div key={severity} className="flex items-center space-x-4">
                  <div className="w-16 text-sm font-medium text-gray-600">
                    {getSeverityLabel(severity)}
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center space-x-2">
                      <div className="flex-1 bg-gray-200 rounded-full h-3">
                        <div 
                          className={`h-3 rounded-full transition-all duration-500 ${
                            severity === 5 ? 'bg-red-500' :
                            severity === 4 ? 'bg-orange-500' :
                            severity === 3 ? 'bg-yellow-500' :
                            severity === 2 ? 'bg-blue-500' :
                            'bg-green-500'
                          }`}
                          style={{ width: `${percentage}%` }}
                        ></div>
                      </div>
                      <span className="text-sm text-gray-600 w-12 text-right">
                        {count}
                      </span>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {viewMode === 'list' && (
        <div className="bg-white rounded-lg border">
          <div className="p-4 border-b">
            <h4 className="text-lg font-medium text-gray-900">Risk Details</h4>
          </div>
          <div className="divide-y divide-gray-200">
            {risks.map((risk, index) => (
              <div 
                key={index}
                className={`p-4 hover:bg-gray-50 cursor-pointer transition-colors ${
                  selectedRisk?.title === risk.title ? 'bg-blue-50' : ''
                }`}
                onClick={() => setSelectedRisk(selectedRisk?.title === risk.title ? null : risk)}
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center space-x-2 mb-2">
                      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getSeverityColor(risk.severity)}`}>
                        {getSeverityLabel(risk.severity)}
                      </span>
                      <span className="text-sm text-gray-500">
                        {Math.round(risk.confidence * 100)}% confidence
                      </span>
                    </div>
                    <h5 className="font-medium text-gray-900 mb-1">{risk.title}</h5>
                    <p className="text-sm text-gray-600 mb-2">{risk.description}</p>
                    <div className="text-xs text-gray-500">
                      Category: {risk.category} • Impact: {risk.business_impact}
                    </div>
                  </div>
                  <AlertTriangle className={`h-5 w-5 ${
                    risk.severity >= 4 ? 'text-red-500' :
                    risk.severity >= 3 ? 'text-orange-500' :
                    'text-yellow-500'
                  }`} />
                </div>
                
                {selectedRisk?.title === risk.title && (
                  <div className="mt-4 p-4 bg-gray-50 rounded-lg">
                    <div className="space-y-3">
                      <div>
                        <h6 className="text-sm font-medium text-gray-900 mb-1">Rationale</h6>
                        <p className="text-sm text-gray-600">{risk.rationale}</p>
                      </div>
                      {risk.clause_reference && (
                        <div>
                          <h6 className="text-sm font-medium text-gray-900 mb-1">Clause Reference</h6>
                          <p className="text-sm text-gray-600">{risk.clause_reference}</p>
                        </div>
                      )}
                      <div>
                        <h6 className="text-sm font-medium text-gray-900 mb-1">Mitigation Suggestions</h6>
                        <ul className="text-sm text-gray-600 space-y-1">
                          {risk.mitigation_suggestions.map((suggestion, idx) => (
                            <li key={idx} className="flex items-start space-x-2">
                              <span className="text-blue-500 mt-1">•</span>
                              <span>{suggestion}</span>
                            </li>
                          ))}
                        </ul>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {viewMode === 'matrix' && (
        <div className="bg-white rounded-lg border p-6">
          <h4 className="text-lg font-medium text-gray-900 mb-4">Risk Matrix</h4>
          <div className="grid grid-cols-5 gap-2">
            {[5, 4, 3, 2, 1].map(severity => (
              [5, 4, 3, 2, 1].map(confidence => {
                const matchingRisks = risks.filter(r => 
                  r.severity === severity && Math.round(r.confidence * 5) === confidence
                );
                
                return (
                  <div 
                    key={`${severity}-${confidence}`}
                    className={`aspect-square rounded-lg border-2 flex items-center justify-center text-xs font-medium ${
                      matchingRisks.length > 0
                        ? severity >= 4 
                          ? 'bg-red-100 border-red-300 text-red-800'
                          : severity >= 3
                          ? 'bg-orange-100 border-orange-300 text-orange-800'
                          : 'bg-yellow-100 border-yellow-300 text-yellow-800'
                        : 'bg-gray-50 border-gray-200 text-gray-400'
                    }`}
                  >
                    {matchingRisks.length > 0 ? matchingRisks.length : '-'}
                  </div>
                );
              })
            ))}
          </div>
          <div className="mt-4 text-center text-sm text-gray-600">
            <p>Risk Matrix: Severity (rows) vs Confidence (columns)</p>
          </div>
        </div>
      )}
    </div>
  );
}
