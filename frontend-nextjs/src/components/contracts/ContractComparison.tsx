'use client';

import { useState, useEffect } from 'react';
import { 
  FileText, 
  AlertTriangle, 
  CheckCircle, 
  Clock, 
  X,
  BarChart3,
  TrendingUp,
  Shield,
  Target
} from 'lucide-react';
import { ContractRecord, ContractAnalysis } from '@/types';
import { apiClient } from '@/lib/api';

interface ContractComparisonProps {
  onClose: () => void;
}

export default function ContractComparison({ onClose }: ContractComparisonProps) {
  const [contracts, setContracts] = useState<ContractRecord[]>([]);
  const [selectedContracts, setSelectedContracts] = useState<ContractRecord[]>([]);
  const [comparisonData, setComparisonData] = useState<{
    [contractId: number]: ContractAnalysis;
  }>({});
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState<'overview' | 'risks' | 'terms' | 'compliance'>('overview');

  useEffect(() => {
    loadContracts();
  }, []);

  const loadContracts = async () => {
    try {
      const response = await apiClient.getContracts();
      setContracts(response.data || []);
    } catch (error) {
      console.error('Failed to load contracts:', error);
    }
  };

  const toggleContractSelection = (contract: ContractRecord) => {
    setSelectedContracts(prev => {
      const isSelected = prev.some(c => c.id === contract.id);
      if (isSelected) {
        return prev.filter(c => c.id !== contract.id);
      } else {
        if (prev.length < 3) { // Limit to 3 contracts for comparison
          return [...prev, contract];
        }
        return prev;
      }
    });
  };

  const loadContractAnalysis = async (contractId: number) => {
    if (comparisonData[contractId]) return;
    
    try {
      setLoading(true);
      const contract = await apiClient.getContract(contractId);
      if (contract.analysis_json) {
        setComparisonData(prev => ({
          ...prev,
          [contractId]: contract.analysis_json
        }));
      }
    } catch (error) {
      console.error('Failed to load contract analysis:', error);
    } finally {
      setLoading(false);
    }
  };

  const getComparisonMetrics = () => {
    if (selectedContracts.length < 2) return [];

    const metrics = selectedContracts.map(contract => {
      const analysis = comparisonData[contract.id];
      return {
        contract,
        analysis,
        riskScore: analysis?.risks?.reduce((sum, risk) => sum + risk.severity, 0) / (analysis?.risks?.length || 1) || 0,
        riskCount: analysis?.risks?.length || 0,
        suggestionCount: analysis?.suggestions?.length || 0,
        hasComplianceIssues: (analysis?.compliance?.issues?.length || 0) > 0
      };
    });

    return metrics;
  };

  const getRiskComparison = () => {
    if (selectedContracts.length < 2) return null;

    const riskData = selectedContracts.map(contract => {
      const analysis = comparisonData[contract.id];
      const risks = analysis?.risks || [];
      
      return {
        contract,
        highRisk: risks.filter(r => r.severity >= 4).length,
        mediumRisk: risks.filter(r => r.severity === 3).length,
        lowRisk: risks.filter(r => r.severity <= 2).length,
        totalRisks: risks.length
      };
    });

    return riskData;
  };

  const comparisonMetrics = getComparisonMetrics();
  const riskComparison = getRiskComparison();

  return (
    <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
      <div className="relative top-4 mx-auto p-6 border w-full max-w-7xl shadow-lg rounded-md bg-white">
        {/* Header */}
        <div className="flex justify-between items-center mb-6">
          <div>
            <h2 className="text-2xl font-bold text-gray-900">Contract Comparison</h2>
            <p className="text-gray-600">Compare up to 3 contracts side by side</p>
          </div>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600"
          >
            <X className="h-6 w-6" />
          </button>
        </div>

        {/* Contract Selection */}
        <div className="mb-6">
          <h3 className="text-lg font-medium text-gray-900 mb-3">Select Contracts to Compare</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {contracts.map((contract) => {
              const isSelected = selectedContracts.some(c => c.id === contract.id);
              return (
                <div
                  key={contract.id}
                  onClick={() => toggleContractSelection(contract)}
                  className={`p-4 border-2 rounded-lg cursor-pointer transition-all ${
                    isSelected 
                      ? 'border-blue-500 bg-blue-50' 
                      : 'border-gray-200 hover:border-gray-300'
                  }`}
                >
                  <div className="flex items-center space-x-3">
                    <div className={`w-4 h-4 rounded-full border-2 ${
                      isSelected ? 'bg-blue-500 border-blue-500' : 'border-gray-300'
                    }`}>
                      {isSelected && <CheckCircle className="w-4 h-4 text-white" />}
                    </div>
                    <div className="flex-1">
                      <h4 className="font-medium text-gray-900">{contract.title}</h4>
                      <p className="text-sm text-gray-500">{contract.counterparty}</p>
                      <div className="flex items-center space-x-2 mt-2">
                        <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${
                          contract.status === 'pending' ? 'bg-yellow-100 text-yellow-800' :
                          contract.status === 'analyzed' ? 'bg-green-100 text-green-800' :
                          'bg-gray-100 text-gray-800'
                        }`}>
                          {contract.status}
                        </span>
                        <span className="text-xs text-gray-500">{contract.category}</span>
                      </div>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
          <p className="text-sm text-gray-500 mt-2">
            Selected: {selectedContracts.length}/3 contracts
          </p>
        </div>

        {selectedContracts.length >= 2 && (
          <>
            {/* Load Analysis Button */}
            <div className="mb-6">
              <button
                onClick={() => selectedContracts.forEach(c => loadContractAnalysis(c.id))}
                disabled={loading}
                className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
              >
                {loading ? 'Loading Analysis...' : 'Load Analysis for Comparison'}
              </button>
            </div>

            {/* Comparison Tabs */}
            <div className="mb-6">
              <div className="border-b border-gray-200">
                <nav className="-mb-px flex space-x-8">
                  {[
                    { key: 'overview', label: 'Overview', icon: BarChart3 },
                    { key: 'risks', label: 'Risk Analysis', icon: AlertTriangle },
                    { key: 'terms', label: 'Key Terms', icon: FileText },
                    { key: 'compliance', label: 'Compliance', icon: Shield }
                  ].map((tab) => {
                    const Icon = tab.icon;
                    return (
                      <button
                        key={tab.key}
                        onClick={() => setActiveTab(tab.key as any)}
                        className={`py-2 px-1 border-b-2 font-medium text-sm flex items-center space-x-2 ${
                          activeTab === tab.key
                            ? 'border-blue-500 text-blue-600'
                            : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                        }`}
                      >
                        <Icon className="h-4 w-4" />
                        <span>{tab.label}</span>
                      </button>
                    );
                  })}
                </nav>
              </div>
            </div>

            {/* Comparison Content */}
            <div className="min-h-96">
              {activeTab === 'overview' && comparisonMetrics && (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                  {comparisonMetrics.map((metric) => (
                    <div key={metric.contract.id} className="bg-gray-50 p-4 rounded-lg">
                      <h4 className="font-medium text-gray-900 mb-3">{metric.contract.title}</h4>
                      <div className="space-y-3">
                        <div className="flex justify-between">
                          <span className="text-sm text-gray-600">Risk Score:</span>
                          <span className={`font-medium ${
                            metric.riskScore >= 4 ? 'text-red-600' :
                            metric.riskScore >= 3 ? 'text-orange-600' : 'text-green-600'
                          }`}>
                            {metric.riskScore.toFixed(1)}/5
                          </span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-sm text-gray-600">Risks Found:</span>
                          <span className="font-medium">{metric.riskCount}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-sm text-gray-600">Suggestions:</span>
                          <span className="font-medium">{metric.suggestionCount}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-sm text-gray-600">Compliance:</span>
                          <span className={`font-medium ${
                            metric.hasComplianceIssues ? 'text-red-600' : 'text-green-600'
                          }`}>
                            {metric.hasComplianceIssues ? 'Issues Found' : 'Compliant'}
                          </span>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}

              {activeTab === 'risks' && riskComparison && (
                <div className="space-y-6">
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {riskComparison.map((riskData) => (
                      <div key={riskData.contract.id} className="bg-white border rounded-lg p-4">
                        <h4 className="font-medium text-gray-900 mb-3">{riskData.contract.title}</h4>
                        <div className="space-y-3">
                          <div className="flex items-center justify-between">
                            <span className="text-sm text-gray-600">High Risk:</span>
                            <span className="text-red-600 font-medium">{riskData.highRisk}</span>
                          </div>
                          <div className="flex items-center justify-between">
                            <span className="text-sm text-gray-600">Medium Risk:</span>
                            <span className="text-orange-600 font-medium">{riskData.mediumRisk}</span>
                          </div>
                          <div className="flex items-center justify-between">
                            <span className="text-sm text-gray-600">Low Risk:</span>
                            <span className="text-green-600 font-medium">{riskData.lowRisk}</span>
                          </div>
                          <div className="flex items-center justify-between">
                            <span className="text-sm text-gray-600">Total:</span>
                            <span className="font-medium">{riskData.totalRisks}</span>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {activeTab === 'terms' && (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                  {selectedContracts.map((contract) => {
                    const analysis = comparisonData[contract.id];
                    return (
                      <div key={contract.id} className="bg-white border rounded-lg p-4">
                        <h4 className="font-medium text-gray-900 mb-3">{contract.title}</h4>
                        {analysis?.summary?.key_terms ? (
                          <div className="space-y-2">
                            {Object.entries(analysis.summary.key_terms).map(([key, value]) => (
                              <div key={key} className="text-sm">
                                <span className="font-medium text-gray-700">{key}:</span>
                                <span className="text-gray-600 ml-2">{String(value)}</span>
                              </div>
                            ))}
                          </div>
                        ) : (
                          <p className="text-gray-500 text-sm">No analysis data available</p>
                        )}
                      </div>
                    );
                  })}
                </div>
              )}

              {activeTab === 'compliance' && (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                  {selectedContracts.map((contract) => {
                    const analysis = comparisonData[contract.id];
                    return (
                      <div key={contract.id} className="bg-white border rounded-lg p-4">
                        <h4 className="font-medium text-gray-900 mb-3">{contract.title}</h4>
                        {analysis?.compliance ? (
                          <div className="space-y-3">
                            <div className="flex items-center justify-between">
                              <span className="text-sm text-gray-600">Status:</span>
                              <span className={`font-medium ${
                                (analysis.compliance.issues?.length || 0) > 0 ? 'text-red-600' : 'text-green-600'
                              }`}>
                                {analysis.compliance.status}
                              </span>
                            </div>
                            {analysis.compliance.issues && analysis.compliance.issues.length > 0 && (
                              <div>
                                <span className="text-sm text-gray-600">Issues:</span>
                                <ul className="mt-1 space-y-1">
                                  {analysis.compliance.issues.map((issue, idx) => (
                                    <li key={idx} className="text-sm text-red-600 flex items-start space-x-2">
                                      <AlertTriangle className="h-3 w-3 mt-0.5 flex-shrink-0" />
                                      <span>{issue}</span>
                                    </li>
                                  ))}
                                </ul>
                              </div>
                            )}
                          </div>
                        ) : (
                          <p className="text-gray-500 text-sm">No compliance data available</p>
                        )}
                      </div>
                    );
                  })}
                </div>
              )}
            </div>
          </>
        )}

        {selectedContracts.length < 2 && (
          <div className="text-center py-12">
            <FileText className="mx-auto h-12 w-12 text-gray-400" />
            <h3 className="mt-2 text-sm font-medium text-gray-900">Select Contracts to Compare</h3>
            <p className="mt-1 text-sm text-gray-500">
              Choose at least 2 contracts to start comparing them.
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
