'use client';

import { useEffect, useState } from 'react';
import { useRouter, useParams } from 'next/navigation';
import Link from 'next/link';
import { useAuthStore } from '@/lib/auth';
import { apiClient } from '@/lib/api';
import { ContractRecord, ContractRisk, ContractSuggestion } from '@/types';
import { 
  ArrowLeft, 
  FileText, 
  AlertTriangle, 
  CheckCircle, 
  Clock,
  Download,
  Search,
  MessageSquare,
  Shield,
  TrendingUp,
  Calendar,
  Building,
  User,
  FileCheck
} from 'lucide-react';

export default function ContractDetailPage() {
  const { user } = useAuthStore();
  const router = useRouter();
  const params = useParams();
  const contractId = parseInt(params.id as string);
  
  const [contract, setContract] = useState<ContractRecord | null>(null);
  const [loading, setLoading] = useState(true);
  const [analyzing, setAnalyzing] = useState(false);
  const [activeTab, setActiveTab] = useState('summary');
  const [showQAModal, setShowQAModal] = useState(false);
  const [question, setQuestion] = useState('');
  const [answer, setAnswer] = useState<any>(null);

  useEffect(() => {
    if (contractId) {
      loadContract();
    }
  }, [contractId]);

  const loadContract = async () => {
    try {
      setLoading(true);
      const response = await apiClient.getContract(contractId);
      setContract(response);
    } catch (error) {
      console.error('Failed to load contract:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleAnalyze = async () => {
    try {
      setAnalyzing(true);
      await apiClient.analyzeContract(contractId);
      await loadContract(); // Reload to get analysis results
    } catch (error) {
      console.error('Failed to analyze contract:', error);
    } finally {
      setAnalyzing(false);
    }
  };

  const handleAskQuestion = async () => {
    if (!question.trim()) return;
    
    try {
      const response = await apiClient.askContractQuestion(contractId, question);
      setAnswer(response.answer);
    } catch (error) {
      console.error('Failed to get answer:', error);
    }
  };

  const handleDownloadReport = async () => {
    try {
      const blob = await apiClient.downloadContractReport(contractId);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `contract_analysis_${contractId}_${new Date().toISOString().slice(0, 10)}.pdf`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (error) {
      console.error('Failed to download report:', error);
    }
  };

  const getSeverityColor = (severity: number) => {
    if (severity >= 4) return 'text-red-600 bg-red-100';
    if (severity >= 3) return 'text-orange-600 bg-orange-100';
    if (severity >= 2) return 'text-yellow-600 bg-yellow-100';
    return 'text-green-600 bg-green-100';
  };

  const getSeverityLabel = (severity: number) => {
    if (severity >= 4) return 'Critical';
    if (severity >= 3) return 'High';
    if (severity >= 2) return 'Medium';
    return 'Low';
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'pending':
        return <Clock className="h-5 w-5 text-yellow-500" />;
      case 'analyzed':
        return <CheckCircle className="h-5 w-5 text-green-500" />;
      case 'reviewed':
        return <FileCheck className="h-5 w-5 text-blue-500" />;
      case 'approved':
        return <CheckCircle className="h-5 w-5 text-green-600" />;
      case 'rejected':
        return <AlertTriangle className="h-5 w-5 text-red-500" />;
      default:
        return <Clock className="h-5 w-5 text-gray-400" />;
    }
  };

  if (loading) {
    return (
      <div className="flex-1 overflow-auto p-6">
        <div className="max-w-7xl mx-auto">
          <div className="flex items-center justify-center h-64">
            <div className="text-center">
              <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600 mx-auto"></div>
              <p className="mt-4 text-gray-600">Loading contract...</p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (!contract) {
    return (
      <div className="flex-1 overflow-auto p-6">
        <div className="max-w-7xl mx-auto">
          <div className="text-center py-12">
            <FileText className="mx-auto h-12 w-12 text-gray-400" />
            <h3 className="mt-2 text-sm font-medium text-gray-900">Contract not found</h3>
            <p className="mt-1 text-sm text-gray-500">
              The contract you're looking for doesn't exist or you don't have permission to view it.
            </p>
            <div className="mt-6">
              <Link
                href="/dashboard/contracts"
                className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700"
              >
                <ArrowLeft className="h-4 w-4 mr-2" />
                Back to Contracts
              </Link>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <>
      {/* Header */}
      <div className="bg-white shadow flex-shrink-0">
        <div className="w-full px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center space-x-4">
              <Link
                href="/dashboard/contracts"
                className="text-gray-400 hover:text-gray-600"
              >
                <ArrowLeft className="h-6 w-6" />
              </Link>
              <div>
                <h1 className="text-xl font-semibold text-gray-900">
                  {contract.title}
                </h1>
                <p className="text-sm text-gray-500">
                  {contract.counterparty} • {contract.category}
                </p>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2">
                {getStatusIcon(contract.status)}
                <span className="text-sm font-medium text-gray-900 capitalize">
                  {contract.status}
                </span>
              </div>
              {contract.status === 'pending' && (
                <button
                  onClick={handleAnalyze}
                  disabled={analyzing}
                  className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 disabled:opacity-50"
                >
                  {analyzing ? (
                    <>
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                      Analyzing...
                    </>
                  ) : (
                    <>
                      <Search className="h-4 w-4 mr-2" />
                      Analyze Contract
                    </>
                  )}
                </button>
              )}
              {contract.analysis_json && (
                <button
                  onClick={handleDownloadReport}
                  className="inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md shadow-sm text-gray-700 bg-white hover:bg-gray-50"
                >
                  <Download className="h-4 w-4 mr-2" />
                  Download Report
                </button>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Main content */}
      <div className="flex-1 overflow-auto p-6">
        <div className="max-w-7xl mx-auto">
          {/* Contract Info */}
          <div className="bg-white shadow rounded-lg mb-6">
            <div className="px-6 py-4 border-b border-gray-200">
              <h2 className="text-lg font-medium text-gray-900">Contract Information</h2>
            </div>
            <div className="px-6 py-4">
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                <div className="flex items-center space-x-3">
                  <Building className="h-5 w-5 text-gray-400" />
                  <div>
                    <p className="text-sm font-medium text-gray-900">Counterparty</p>
                    <p className="text-sm text-gray-500">{contract.counterparty}</p>
                  </div>
                </div>
                <div className="flex items-center space-x-3">
                  <FileText className="h-5 w-5 text-gray-400" />
                  <div>
                    <p className="text-sm font-medium text-gray-900">Category</p>
                    <p className="text-sm text-gray-500">{contract.category}</p>
                  </div>
                </div>
                <div className="flex items-center space-x-3">
                  <User className="h-5 w-5 text-gray-400" />
                  <div>
                    <p className="text-sm font-medium text-gray-900">Owner</p>
                    <p className="text-sm text-gray-500">{contract.owner_username}</p>
                  </div>
                </div>
                {contract.effective_date && (
                  <div className="flex items-center space-x-3">
                    <Calendar className="h-5 w-5 text-gray-400" />
                    <div>
                      <p className="text-sm font-medium text-gray-900">Effective Date</p>
                      <p className="text-sm text-gray-500">
                        {new Date(contract.effective_date).toLocaleDateString()}
                      </p>
                    </div>
                  </div>
                )}
                {contract.term_end && (
                  <div className="flex items-center space-x-3">
                    <Calendar className="h-5 w-5 text-gray-400" />
                    <div>
                      <p className="text-sm font-medium text-gray-900">Term End</p>
                      <p className="text-sm text-gray-500">
                        {new Date(contract.term_end).toLocaleDateString()}
                      </p>
                    </div>
                  </div>
                )}
                {contract.governing_law && (
                  <div className="flex items-center space-x-3">
                    <Shield className="h-5 w-5 text-gray-400" />
                    <div>
                      <p className="text-sm font-medium text-gray-900">Governing Law</p>
                      <p className="text-sm text-gray-500">{contract.governing_law}</p>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Tabs */}
          <div className="bg-white shadow rounded-lg">
            <div className="border-b border-gray-200">
              <nav className="-mb-px flex space-x-8 px-6">
                {[
                  { id: 'summary', name: 'Summary', icon: FileText },
                  { id: 'risks', name: 'Risks', icon: AlertTriangle },
                  { id: 'suggestions', name: 'Suggestions', icon: TrendingUp },
                  { id: 'qa', name: 'Q&A', icon: MessageSquare }
                ].map((tab) => (
                  <button
                    key={tab.id}
                    onClick={() => setActiveTab(tab.id)}
                    className={`py-4 px-1 border-b-2 font-medium text-sm flex items-center space-x-2 ${
                      activeTab === tab.id
                        ? 'border-blue-500 text-blue-600'
                        : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                    }`}
                  >
                    <tab.icon className="h-4 w-4" />
                    <span>{tab.name}</span>
                  </button>
                ))}
              </nav>
            </div>

            <div className="p-6">
              {/* Summary Tab */}
              {activeTab === 'summary' && (
                <div>
                  {contract.summary_text ? (
                    <div className="prose max-w-none">
                      <h3 className="text-lg font-medium text-gray-900 mb-4">Executive Summary</h3>
                      <p className="text-gray-700 whitespace-pre-wrap">{contract.summary_text}</p>
                      
                      {contract.analysis_json?.summary?.key_terms && (
                        <div className="mt-6">
                          <h4 className="text-md font-medium text-gray-900 mb-3">Key Terms</h4>
                          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            {Object.entries(contract.analysis_json.summary.key_terms).map(([key, value]) => (
                              <div key={key} className="bg-gray-50 p-3 rounded">
                                <dt className="text-sm font-medium text-gray-900 capitalize">
                                  {key.replace(/_/g, ' ')}
                                </dt>
                                <dd className="text-sm text-gray-600 mt-1">{value as string}</dd>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  ) : (
                    <div className="text-center py-8">
                      <FileText className="mx-auto h-12 w-12 text-gray-400" />
                      <h3 className="mt-2 text-sm font-medium text-gray-900">No analysis available</h3>
                      <p className="mt-1 text-sm text-gray-500">
                        Run analysis to see the contract summary and key terms.
                      </p>
                      {contract.status === 'pending' && (
                        <div className="mt-6">
                          <button
                            onClick={handleAnalyze}
                            disabled={analyzing}
                            className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700"
                          >
                            <Search className="h-4 w-4 mr-2" />
                            Analyze Contract
                          </button>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              )}

              {/* Risks Tab */}
              {activeTab === 'risks' && (
                <div>
                  {contract.risk_items && contract.risk_items.length > 0 ? (
                    <div className="space-y-4">
                      {contract.risk_items.map((risk, index) => (
                        <div key={index} className="border border-gray-200 rounded-lg p-4">
                          <div className="flex items-start justify-between">
                            <div className="flex-1">
                              <div className="flex items-center space-x-2 mb-2">
                                <h4 className="text-sm font-medium text-gray-900">{risk.title}</h4>
                                <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getSeverityColor(risk.severity)}`}>
                                  {getSeverityLabel(risk.severity)} (Level {risk.severity})
                                </span>
                                <span className="text-xs text-gray-500">
                                  Confidence: {Math.round(risk.confidence * 100)}%
                                </span>
                              </div>
                              <p className="text-sm text-gray-700 mb-2">{risk.description}</p>
                              <p className="text-sm text-gray-600 mb-2">
                                <strong>Rationale:</strong> {risk.rationale}
                              </p>
                              {risk.clause_reference && (
                                <p className="text-sm text-gray-600 mb-2">
                                  <strong>Reference:</strong> {risk.clause_reference}
                                </p>
                              )}
                              <p className="text-sm text-gray-600 mb-2">
                                <strong>Business Impact:</strong> {risk.business_impact}
                              </p>
                              {risk.mitigation_suggestions && risk.mitigation_suggestions.length > 0 && (
                                <div>
                                  <p className="text-sm font-medium text-gray-900 mb-1">Mitigation Suggestions:</p>
                                  <ul className="text-sm text-gray-600 list-disc list-inside space-y-1">
                                    {risk.mitigation_suggestions.map((suggestion, idx) => (
                                      <li key={idx}>{suggestion}</li>
                                    ))}
                                  </ul>
                                </div>
                              )}
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="text-center py-8">
                      <AlertTriangle className="mx-auto h-12 w-12 text-gray-400" />
                      <h3 className="mt-2 text-sm font-medium text-gray-900">No risks identified</h3>
                      <p className="mt-1 text-sm text-gray-500">
                        {contract.status === 'pending' 
                          ? 'Run analysis to identify potential risks in this contract.'
                          : 'No significant risks were found in this contract.'
                        }
                      </p>
                    </div>
                  )}
                </div>
              )}

              {/* Suggestions Tab */}
              {activeTab === 'suggestions' && (
                <div>
                  {contract.rewrite_suggestions && contract.rewrite_suggestions.length > 0 ? (
                    <div className="space-y-6">
                      {contract.rewrite_suggestions.map((suggestion, index) => (
                        <div key={index} className="border border-gray-200 rounded-lg p-4">
                          <div className="flex items-center space-x-2 mb-3">
                            <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                              suggestion.type === 'company_favorable' 
                                ? 'bg-green-100 text-green-800' 
                                : 'bg-blue-100 text-blue-800'
                            }`}>
                              {suggestion.type === 'company_favorable' ? 'Company Favorable' : 'Balanced'}
                            </span>
                            <span className="text-xs text-gray-500">{suggestion.category}</span>
                          </div>
                          
                          {suggestion.original_text && (
                            <div className="mb-3">
                              <p className="text-sm font-medium text-gray-900 mb-1">Original Text:</p>
                              <div className="bg-red-50 border border-red-200 rounded p-3">
                                <p className="text-sm text-gray-700">{suggestion.original_text}</p>
                              </div>
                            </div>
                          )}
                          
                          <div className="mb-3">
                            <p className="text-sm font-medium text-gray-900 mb-1">Suggested Text:</p>
                            <div className="bg-green-50 border border-green-200 rounded p-3">
                              <p className="text-sm text-gray-700">{suggestion.suggested_text}</p>
                            </div>
                          </div>
                          
                          <p className="text-sm text-gray-600 mb-3">
                            <strong>Rationale:</strong> {suggestion.rationale}
                          </p>
                          
                          {suggestion.negotiation_tips && suggestion.negotiation_tips.length > 0 && (
                            <div className="mb-3">
                              <p className="text-sm font-medium text-gray-900 mb-1">Negotiation Tips:</p>
                              <ul className="text-sm text-gray-600 list-disc list-inside space-y-1">
                                {suggestion.negotiation_tips.map((tip, idx) => (
                                  <li key={idx}>{tip}</li>
                                ))}
                              </ul>
                            </div>
                          )}
                          
                          {suggestion.fallback_position && (
                            <div>
                              <p className="text-sm font-medium text-gray-900 mb-1">Fallback Position:</p>
                              <p className="text-sm text-gray-600">{suggestion.fallback_position}</p>
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="text-center py-8">
                      <TrendingUp className="mx-auto h-12 w-12 text-gray-400" />
                      <h3 className="mt-2 text-sm font-medium text-gray-900">No suggestions available</h3>
                      <p className="mt-1 text-sm text-gray-500">
                        {contract.status === 'pending' 
                          ? 'Run analysis to get rewrite suggestions for this contract.'
                          : 'No rewrite suggestions were generated for this contract.'
                        }
                      </p>
                    </div>
                  )}
                </div>
              )}

              {/* Q&A Tab */}
              {activeTab === 'qa' && (
                <div>
                  <div className="mb-6">
                    <h3 className="text-lg font-medium text-gray-900 mb-4">Ask Questions About This Contract</h3>
                    <div className="flex space-x-4">
                      <input
                        type="text"
                        placeholder="Ask a question about this contract..."
                        value={question}
                        onChange={(e) => setQuestion(e.target.value)}
                        className="flex-1 px-4 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                        onKeyPress={(e) => e.key === 'Enter' && handleAskQuestion()}
                      />
                      <button
                        onClick={handleAskQuestion}
                        disabled={!question.trim()}
                        className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
                      >
                        Ask
                      </button>
                    </div>
                  </div>

                  {answer && (
                    <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                      <h4 className="text-sm font-medium text-gray-900 mb-2">Answer:</h4>
                      <p className="text-sm text-gray-700 mb-3">{answer.answer}</p>
                      {answer.confidence && (
                        <p className="text-xs text-gray-500 mb-2">
                          Confidence: {Math.round(answer.confidence * 100)}%
                        </p>
                      )}
                      {answer.source_reference && (
                        <p className="text-xs text-gray-500 mb-2">
                          Source: {answer.source_reference}
                        </p>
                      )}
                      {answer.context && (
                        <div className="mb-2">
                          <p className="text-xs font-medium text-gray-900">Context:</p>
                          <p className="text-xs text-gray-600">{answer.context}</p>
                        </div>
                      )}
                      {answer.implications && (
                        <div className="mb-2">
                          <p className="text-xs font-medium text-gray-900">Implications:</p>
                          <p className="text-xs text-gray-600">{answer.implications}</p>
                        </div>
                      )}
                      {answer.recommendations && answer.recommendations.length > 0 && (
                        <div>
                          <p className="text-xs font-medium text-gray-900">Recommendations:</p>
                          <ul className="text-xs text-gray-600 list-disc list-inside">
                            {answer.recommendations.map((rec: string, idx: number) => (
                              <li key={idx}>{rec}</li>
                            ))}
                          </ul>
                        </div>
                      )}
                    </div>
                  )}

                  <div className="mt-6">
                    <h4 className="text-sm font-medium text-gray-900 mb-2">Example Questions:</h4>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                      {[
                        "What are the payment terms?",
                        "What is the contract duration?",
                        "What are the termination conditions?",
                        "What are the liability limitations?",
                        "What happens if there's a breach?",
                        "What are the renewal terms?"
                      ].map((exampleQuestion, index) => (
                        <button
                          key={index}
                          onClick={() => setQuestion(exampleQuestion)}
                          className="text-left p-2 text-sm text-gray-600 hover:bg-gray-50 rounded border border-gray-200 hover:border-gray-300"
                        >
                          {exampleQuestion}
                        </button>
                      ))}
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </>
  );
}
