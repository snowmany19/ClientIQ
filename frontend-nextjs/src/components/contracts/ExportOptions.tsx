'use client';

import { useState } from 'react';
import { 
  Download, 
  FileText, 
  FileSpreadsheet, 
  FileText as FilePdf, 
  FileJson,
  Settings,
  Check,
  X,
  Info,
  Filter,
  Calendar,
  Building
} from 'lucide-react';
import { ContractRecord } from '@/types';

interface ExportOptionsProps {
  contracts: ContractRecord[];
  onExport: (format: string, options: ExportOptions) => Promise<void>;
  onClose: () => void;
  className?: string;
}

interface ExportOptions {
  format: 'csv' | 'pdf' | 'json' | 'excel';
  includeAnalysis: boolean;
  includeRisks: boolean;
  includeSuggestions: boolean;
  includeMetadata: boolean;
  dateRange?: {
    start: string;
    end: string;
  };
  categories?: string[];
  statuses?: string[];
  customFields?: string[];
}

const EXPORT_FORMATS = [
  {
    id: 'csv',
    name: 'CSV',
    description: 'Spreadsheet format for data analysis',
    icon: FileSpreadsheet,
    color: 'text-green-600'
  },
  {
    id: 'pdf',
    name: 'PDF Report',
    description: 'Professional report with charts and analysis',
    icon: FilePdf,
    color: 'text-red-600'
  },
  {
    id: 'json',
    name: 'JSON',
    description: 'Raw data for developers and integrations',
    icon: FileJson,
    color: 'text-yellow-600'
  },
  {
    id: 'excel',
    name: 'Excel',
    description: 'Advanced spreadsheet with formatting',
    icon: FileSpreadsheet,
    color: 'text-green-700'
  }
];

export default function ExportOptions({ 
  contracts, 
  onExport, 
  onClose, 
  className = '' 
}: ExportOptionsProps) {
  const [selectedFormat, setSelectedFormat] = useState<string>('csv');
  const [options, setOptions] = useState<ExportOptions>({
    format: 'csv',
    includeAnalysis: true,
    includeRisks: true,
    includeSuggestions: true,
    includeMetadata: true,
    dateRange: undefined,
    categories: [],
    statuses: [],
    customFields: []
  });
  const [isExporting, setIsExporting] = useState(false);
  const [showAdvanced, setShowAdvanced] = useState(false);

  const availableCategories = Array.from(new Set(contracts.map(c => c.category)));
  const availableStatuses = Array.from(new Set(contracts.map(c => c.status)));

  const handleFormatChange = (format: string) => {
    setSelectedFormat(format);
    setOptions(prev => ({ ...prev, format: format as ExportOptions['format'] }));
  };

  const handleOptionChange = (key: keyof ExportOptions, value: any) => {
    setOptions(prev => ({ ...prev, [key]: value }));
  };

  const handleExport = async () => {
    setIsExporting(true);
    try {
      await onExport(selectedFormat, options);
    } catch (error) {
      console.error('Export failed:', error);
    } finally {
      setIsExporting(false);
    }
  };

  const getFilteredContractCount = () => {
    let filtered = contracts;
    
    if (options.dateRange?.start) {
      filtered = filtered.filter(c => new Date(c.created_at) >= new Date(options.dateRange!.start));
    }
    
    if (options.dateRange?.end) {
      filtered = filtered.filter(c => new Date(c.created_at) <= new Date(options.dateRange!.end));
    }
    
    if (options.categories && options.categories.length > 0) {
      filtered = filtered.filter(c => options.categories!.includes(c.category));
    }
    
    if (options.statuses && options.statuses.length > 0) {
      filtered = filtered.filter(c => options.statuses!.includes(c.status));
    }
    
    return filtered.length;
  };

  const resetFilters = () => {
    setOptions(prev => ({
      ...prev,
      dateRange: undefined,
      categories: [],
      statuses: []
    }));
  };

  return (
    <div className={`bg-white rounded-lg border shadow-lg max-w-2xl mx-auto ${className}`}>
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b">
        <div className="flex items-center space-x-3">
          <Download className="h-6 w-6 text-blue-600" />
          <div>
            <h3 className="text-lg font-semibold text-gray-900">Export Contracts</h3>
            <p className="text-sm text-gray-600">
              Choose format and customize export options
            </p>
          </div>
        </div>
        <button
          onClick={onClose}
          className="text-gray-400 hover:text-gray-600"
        >
          <X className="h-6 w-6" />
        </button>
      </div>

      {/* Format Selection */}
      <div className="p-4 border-b">
        <h4 className="text-sm font-medium text-gray-700 mb-3">Export Format</h4>
        <div className="grid grid-cols-2 gap-3">
          {EXPORT_FORMATS.map(format => (
            <div
              key={format.id}
              className={`p-3 border rounded-lg cursor-pointer transition-colors ${
                selectedFormat === format.id
                  ? 'border-blue-500 bg-blue-50'
                  : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50'
              }`}
              onClick={() => handleFormatChange(format.id)}
            >
              <div className="flex items-center space-x-3">
                <format.icon className={`h-5 w-5 ${format.color}`} />
                <div>
                  <p className="text-sm font-medium text-gray-900">{format.name}</p>
                  <p className="text-xs text-gray-500">{format.description}</p>
                </div>
                {selectedFormat === format.id && (
                  <Check className="h-4 w-4 text-blue-500 ml-auto" />
                )}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Content Options */}
      <div className="p-4 border-b">
        <h4 className="text-sm font-medium text-gray-700 mb-3">Include in Export</h4>
        <div className="space-y-3">
          <label className="flex items-center space-x-3">
            <input
              type="checkbox"
              checked={options.includeMetadata}
              onChange={(e) => handleOptionChange('includeMetadata', e.target.checked)}
              className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
            />
            <span className="text-sm text-gray-700">Basic contract information</span>
          </label>
          
          <label className="flex items-center space-x-3">
            <input
              type="checkbox"
              checked={options.includeAnalysis}
              onChange={(e) => handleOptionChange('includeAnalysis', e.target.checked)}
              className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
            />
            <span className="text-sm text-gray-700">AI analysis summary</span>
          </label>
          
          <label className="flex items-center space-x-3">
            <input
              type="checkbox"
              checked={options.includeRisks}
              onChange={(e) => handleOptionChange('includeRisks', e.target.checked)}
              className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
            />
            <span className="text-sm text-gray-700">Risk assessment details</span>
          </label>
          
          <label className="flex items-center space-x-3">
            <input
              type="checkbox"
              checked={options.includeSuggestions}
              onChange={(e) => handleOptionChange('includeSuggestions', e.target.checked)}
              className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
            />
            <span className="text-sm text-gray-700">Rewrite suggestions</span>
          </label>
        </div>
      </div>

      {/* Advanced Options Toggle */}
      <div className="p-4 border-b">
        <button
          onClick={() => setShowAdvanced(!showAdvanced)}
          className="flex items-center space-x-2 text-sm text-gray-600 hover:text-gray-800"
        >
          <Settings className="h-4 w-4" />
          <span>Advanced Options</span>
        </button>
      </div>

      {/* Advanced Options */}
      {showAdvanced && (
        <div className="p-4 border-b bg-gray-50">
          <div className="space-y-4">
            {/* Date Range Filter */}
            <div>
              <h5 className="text-sm font-medium text-gray-700 mb-2">Date Range</h5>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs text-gray-600 mb-1">Start Date</label>
                  <input
                    type="date"
                    value={options.dateRange?.start || ''}
                    onChange={(e) => handleOptionChange('dateRange', { 
                      ...options.dateRange, 
                      start: e.target.value 
                    })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm"
                  />
                </div>
                <div>
                  <label className="block text-xs text-gray-600 mb-1">End Date</label>
                  <input
                    type="date"
                    value={options.dateRange?.end || ''}
                    onChange={(e) => handleOptionChange('dateRange', { 
                      ...options.dateRange, 
                      end: e.target.value 
                    })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm"
                  />
                </div>
              </div>
            </div>

            {/* Category Filter */}
            <div>
              <h5 className="text-sm font-medium text-gray-700 mb-2">Categories</h5>
              <div className="grid grid-cols-2 gap-2">
                {availableCategories.map(category => (
                  <label key={category} className="flex items-center space-x-2">
                    <input
                      type="checkbox"
                      checked={options.categories?.includes(category) || false}
                      onChange={(e) => {
                        const current = options.categories || [];
                        if (e.target.checked) {
                          handleOptionChange('categories', [...current, category]);
                        } else {
                          handleOptionChange('categories', current.filter(c => c !== category));
                        }
                      }}
                      className="h-3 w-3 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                    />
                    <span className="text-xs text-gray-700">{category}</span>
                  </label>
                ))}
              </div>
            </div>

            {/* Status Filter */}
            <div>
              <h5 className="text-sm font-medium text-gray-700 mb-2">Status</h5>
              <div className="grid grid-cols-2 gap-2">
                {availableStatuses.map(status => (
                  <label key={status} className="flex items-center space-x-2">
                    <input
                      type="checkbox"
                      checked={options.statuses?.includes(status) || false}
                      onChange={(e) => {
                        const current = options.statuses || [];
                        if (e.target.checked) {
                          handleOptionChange('statuses', [...current, status]);
                        } else {
                          handleOptionChange('statuses', current.filter(s => s !== status));
                        }
                      }}
                      className="h-3 w-3 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                    />
                    <span className="text-xs text-gray-700">{status}</span>
                  </label>
                ))}
              </div>
            </div>

            {/* Reset Filters */}
            <div className="pt-2">
              <button
                onClick={resetFilters}
                className="text-xs text-gray-500 hover:text-gray-700 underline"
              >
                Reset all filters
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Export Summary */}
      <div className="p-4 border-b bg-blue-50">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <Info className="h-4 w-4 text-blue-600" />
            <span className="text-sm text-blue-800">
              {getFilteredContractCount()} of {contracts.length} contracts will be exported
            </span>
          </div>
          <span className="text-xs text-blue-600">
            {selectedFormat.toUpperCase()} format
          </span>
        </div>
      </div>

      {/* Action Buttons */}
      <div className="p-4 flex items-center justify-end space-x-3">
        <button
          onClick={onClose}
          className="px-4 py-2 text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors"
        >
          Cancel
        </button>
        <button
          onClick={handleExport}
          disabled={isExporting || getFilteredContractCount() === 0}
          className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center space-x-2"
        >
          <Download className="h-4 w-4" />
          <span>{isExporting ? 'Exporting...' : 'Export'}</span>
        </button>
      </div>
    </div>
  );
}
