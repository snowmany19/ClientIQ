'use client';

import { useState, useEffect } from 'react';
import { 
  FileText, 
  Play, 
  CheckCircle, 
  Clock, 
  AlertTriangle,
  X,
  BarChart3,
  Loader2,
  Download,
  Eye
} from 'lucide-react';
import { ContractRecord } from '@/types';
import { apiClient } from '@/lib/api';
import Link from 'next/link';

interface BatchAnalysisProps {
  onClose: () => void;
}

interface BatchJob {
  id: string;
  contractId: number;
  contractTitle: string;
  status: 'pending' | 'analyzing' | 'completed' | 'failed';
  progress: number;
  error?: string;
  startedAt?: Date;
  completedAt?: Date;
}

export default function BatchAnalysis({ onClose }: BatchAnalysisProps) {
  const [contracts, setContracts] = useState<ContractRecord[]>([]);
  const [selectedContracts, setSelectedContracts] = useState<ContractRecord[]>([]);
  const [batchJobs, setBatchJobs] = useState<BatchJob[]>([]);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [overallProgress, setOverallProgress] = useState(0);

  useEffect(() => {
    loadContracts();
  }, []);

  useEffect(() => {
    if (batchJobs.length > 0) {
      const completed = batchJobs.filter(job => job.status === 'completed').length;
      const total = batchJobs.length;
      setOverallProgress((completed / total) * 100);
    }
  }, [batchJobs]);

  const loadContracts = async () => {
    try {
      const response = await apiClient.getContracts();
      const pendingContracts = (response.data || []).filter(c => c.status === 'pending');
      setContracts(pendingContracts);
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
        return [...prev, contract];
      }
    });
  };

  const startBatchAnalysis = async () => {
    if (selectedContracts.length === 0) return;

    setIsAnalyzing(true);
    
    // Create batch jobs
    const jobs: BatchJob[] = selectedContracts.map(contract => ({
      id: `job-${contract.id}-${Date.now()}`,
      contractId: contract.id,
      contractTitle: contract.title,
      status: 'pending',
      progress: 0
    }));

    setBatchJobs(jobs);

    // Start analysis for each contract
    for (const job of jobs) {
      try {
        // Update job status to analyzing
        setBatchJobs(prev => prev.map(j => 
          j.id === job.id ? { ...j, status: 'analyzing', startedAt: new Date() } : j
        ));

        // Simulate progress updates
        const progressInterval = setInterval(() => {
          setBatchJobs(prev => prev.map(j => {
            if (j.id === job.id && j.status === 'analyzing') {
              const newProgress = Math.min(j.progress + Math.random() * 20, 90);
              return { ...j, progress: newProgress };
            }
            return j;
          }));
        }, 1000);

        // Start actual analysis
        await apiClient.analyzeContract(job.contractId);

        // Clear interval and mark as completed
        clearInterval(progressInterval);
        setBatchJobs(prev => prev.map(j => 
          j.id === job.id ? { 
            ...j, 
            status: 'completed', 
            progress: 100, 
            completedAt: new Date() 
          } : j
        ));

      } catch (error) {
        console.error(`Failed to analyze contract ${job.contractId}:`, error);
        setBatchJobs(prev => prev.map(j => 
          j.id === job.id ? { 
            ...j, 
            status: 'failed', 
            error: error instanceof Error ? error.message : 'Unknown error' 
          } : j
        ));
      }
    }

    setIsAnalyzing(false);
  };

  const retryJob = async (job: BatchJob) => {
    try {
      setBatchJobs(prev => prev.map(j => 
        j.id === job.id ? { ...j, status: 'analyzing', progress: 0, error: undefined } : j
      ));

      await apiClient.analyzeContract(job.contractId);

      setBatchJobs(prev => prev.map(j => 
        j.id === job.id ? { 
          ...j, 
          status: 'completed', 
          progress: 100, 
          completedAt: new Date() 
        } : j
      ));

    } catch (error) {
      console.error(`Failed to retry analysis for contract ${job.contractId}:`, error);
      setBatchJobs(prev => prev.map(j => 
        j.id === job.id ? { 
          ...j, 
          status: 'failed', 
          error: error instanceof Error ? error.message : 'Unknown error' 
        } : j
      ));
    }
  };

  const downloadBatchReport = async () => {
    try {
      const completedJobs = batchJobs.filter(job => job.status === 'completed');
      if (completedJobs.length === 0) return;

      // Create a summary report
      const reportData = {
        summary: {
          totalContracts: batchJobs.length,
          completed: completedJobs.length,
          failed: batchJobs.filter(job => job.status === 'failed').length,
          startedAt: batchJobs[0]?.startedAt,
          completedAt: new Date()
        },
        contracts: completedJobs.map(job => ({
          id: job.contractId,
          title: job.contractTitle,
          status: job.status,
          startedAt: job.startedAt,
          completedAt: job.completedAt
        }))
      };

      const blob = new Blob([JSON.stringify(reportData, null, 2)], {
        type: 'application/json'
      });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `batch_analysis_report_${new Date().toISOString().slice(0, 10)}.json`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (error) {
      console.error('Failed to download batch report:', error);
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'pending':
        return <Clock className="h-4 w-4 text-gray-500" />;
      case 'analyzing':
        return <Loader2 className="h-4 w-4 text-blue-600 animate-spin" />;
      case 'completed':
        return <CheckCircle className="h-4 w-4 text-green-600" />;
      case 'failed':
        return <AlertTriangle className="h-4 w-4 text-red-600" />;
      default:
        return <Clock className="h-4 w-4 text-gray-500" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'pending':
        return 'bg-gray-100 text-gray-800';
      case 'analyzing':
        return 'bg-blue-100 text-blue-800';
      case 'completed':
        return 'bg-green-100 text-green-800';
      case 'failed':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
      <div className="relative top-4 mx-auto p-6 border w-full max-w-6xl shadow-lg rounded-md bg-white">
        {/* Header */}
        <div className="flex justify-between items-center mb-6">
          <div>
            <h2 className="text-2xl font-bold text-gray-900">Batch Contract Analysis</h2>
            <p className="text-gray-600">Analyze multiple contracts simultaneously</p>
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
          <h3 className="text-lg font-medium text-gray-900 mb-3">
            Select Contracts for Batch Analysis ({selectedContracts.length} selected)
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 max-h-64 overflow-y-auto">
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
                        <span className="text-xs text-gray-500">{contract.category}</span>
                        <span className="text-xs text-gray-500">
                          {new Date(contract.created_at).toLocaleDateString()}
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Start Analysis Button */}
        {selectedContracts.length > 0 && batchJobs.length === 0 && (
          <div className="mb-6">
            <button
              onClick={startBatchAnalysis}
              disabled={isAnalyzing}
              className="px-6 py-3 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 flex items-center space-x-2"
            >
              <Play className="h-5 w-5" />
              <span>Start Batch Analysis ({selectedContracts.length} contracts)</span>
            </button>
          </div>
        )}

        {/* Overall Progress */}
        {batchJobs.length > 0 && (
          <div className="mb-6">
            <div className="bg-gray-50 p-4 rounded-lg">
              <div className="flex items-center justify-between mb-2">
                <h3 className="text-lg font-medium text-gray-900">Overall Progress</h3>
                <span className="text-sm font-medium text-gray-600">
                  {Math.round(overallProgress)}% Complete
                </span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-3">
                <div 
                  className="bg-blue-600 h-3 rounded-full transition-all duration-500"
                  style={{ width: `${overallProgress}%` }}
                ></div>
              </div>
              <div className="flex justify-between text-sm text-gray-600 mt-2">
                <span>
                  Completed: {batchJobs.filter(job => job.status === 'completed').length}
                </span>
                <span>
                  Failed: {batchJobs.filter(job => job.status === 'failed').length}
                </span>
                <span>
                  Total: {batchJobs.length}
                </span>
              </div>
            </div>
          </div>
        )}

        {/* Batch Jobs Status */}
        {batchJobs.length > 0 && (
          <div className="mb-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-medium text-gray-900">Analysis Status</h3>
              {batchJobs.some(job => job.status === 'completed') && (
                <button
                  onClick={downloadBatchReport}
                  className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 flex items-center space-x-2"
                >
                  <Download className="h-4 w-4" />
                  <span>Download Report</span>
                </button>
              )}
            </div>
            
            <div className="space-y-3 max-h-96 overflow-y-auto">
              {batchJobs.map((job) => (
                <div key={job.id} className="bg-white border rounded-lg p-4">
                  <div className="flex items-center justify-between mb-3">
                    <div className="flex items-center space-x-3">
                      {getStatusIcon(job.status)}
                      <div>
                        <h4 className="font-medium text-gray-900">{job.contractTitle}</h4>
                        <p className="text-sm text-gray-500">Contract ID: {job.contractId}</p>
                      </div>
                    </div>
                    <span className={`px-3 py-1 rounded-full text-xs font-medium ${getStatusColor(job.status)}`}>
                      {job.status.charAt(0).toUpperCase() + job.status.slice(1)}
                    </span>
                  </div>

                  {job.status === 'analyzing' && (
                    <div className="space-y-2">
                      <div className="flex justify-between text-sm text-gray-600">
                        <span>Progress</span>
                        <span>{Math.round(job.progress)}%</span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div 
                          className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                          style={{ width: `${job.progress}%` }}
                        ></div>
                      </div>
                    </div>
                  )}

                  {job.status === 'completed' && (
                    <div className="flex items-center justify-between text-sm text-gray-600">
                      <span>Completed at: {job.completedAt?.toLocaleTimeString()}</span>
                      <Link
                        href={`/dashboard/contracts/${job.contractId}`}
                        className="text-blue-600 hover:text-blue-700 flex items-center space-x-1"
                      >
                        <Eye className="h-4 w-4" />
                        <span>View Results</span>
                      </Link>
                    </div>
                  )}

                  {job.status === 'failed' && (
                    <div className="space-y-3">
                      <p className="text-sm text-red-600">{job.error}</p>
                      <button
                        onClick={() => retryJob(job)}
                        className="px-3 py-1 bg-red-100 text-red-700 rounded text-sm hover:bg-red-200"
                      >
                        Retry Analysis
                      </button>
                    </div>
                  )}

                  {job.startedAt && (
                    <p className="text-xs text-gray-500 mt-2">
                      Started: {job.startedAt.toLocaleTimeString()}
                    </p>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Empty State */}
        {selectedContracts.length === 0 && batchJobs.length === 0 && (
          <div className="text-center py-12">
            <FileText className="mx-auto h-12 w-12 text-gray-400" />
            <h3 className="mt-2 text-sm font-medium text-gray-900">No Contracts Selected</h3>
            <p className="mt-1 text-sm text-gray-500">
              Select contracts above to start batch analysis.
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
