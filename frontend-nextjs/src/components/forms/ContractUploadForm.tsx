'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { apiClient } from '@/lib/api';
import { ContractCreate } from '@/types';
import { Upload, FileText, X, AlertCircle } from 'lucide-react';

interface ContractUploadFormProps {
  onClose: () => void;
  onSuccess: () => void;
}

export default function ContractUploadForm({ onClose, onSuccess }: ContractUploadFormProps) {
  const router = useRouter();
  const [formData, setFormData] = useState<Partial<ContractCreate>>({
    title: '',
    counterparty: '',
    category: 'Other' as any,
    effective_date: '',
    term_end: '',
    renewal_terms: '',
    governing_law: '',
    uploaded_files: [],
    status: 'pending'
  });
  const [files, setFiles] = useState<File[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      const newFiles = Array.from(e.target.files);
      setFiles(prev => [...prev, ...newFiles]);
    }
  };

  const removeFile = (index: number) => {
    setFiles(prev => prev.filter((_, i) => i !== index));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!formData.title || !formData.counterparty) {
      setError('Title and counterparty are required');
      return;
    }

    if (files.length === 0) {
      setError('Please upload at least one contract file');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      // Create contract record
      const contractData: ContractCreate = {
        ...formData as ContractCreate,
        uploaded_files: [] // Will be populated after file upload
      };

      const contract = await apiClient.createContract(contractData);

      // Upload files
      for (const file of files) {
        await apiClient.uploadContractFile(contract.id, file);
      }

      onSuccess();
      onClose();
      router.push(`/dashboard/contracts/${contract.id}`);
    } catch (error) {
      console.error('Failed to create contract:', error);
      setError('Failed to create contract. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
      <div className="relative top-20 mx-auto p-5 border w-full max-w-2xl shadow-lg rounded-md bg-white">
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-lg font-medium text-gray-900">Upload Contract</h3>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600"
          >
            <X className="h-6 w-6" />
          </button>
        </div>

        {error && (
          <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-md">
            <div className="flex items-center">
              <AlertCircle className="h-5 w-5 text-red-400 mr-2" />
              <span className="text-sm text-red-700">{error}</span>
            </div>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          {/* Basic Information */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Contract Title *
              </label>
              <input
                type="text"
                name="title"
                value={formData.title}
                onChange={handleInputChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                placeholder="e.g., Vendor Service Agreement"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Counterparty *
              </label>
              <input
                type="text"
                name="counterparty"
                value={formData.counterparty}
                onChange={handleInputChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                placeholder="e.g., ABC Corporation"
                required
              />
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Category
              </label>
              <select
                name="category"
                value={formData.category}
                onChange={handleInputChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="NDA">NDA</option>
                <option value="MSA">MSA</option>
                <option value="SOW">SOW</option>
                <option value="Employment">Employment</option>
                <option value="Vendor">Vendor</option>
                <option value="Lease">Lease</option>
                <option value="Other">Other</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Governing Law
              </label>
              <input
                type="text"
                name="governing_law"
                value={formData.governing_law}
                onChange={handleInputChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                placeholder="e.g., California, USA"
              />
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Effective Date
              </label>
              <input
                type="date"
                name="effective_date"
                value={formData.effective_date}
                onChange={handleInputChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Term End
              </label>
              <input
                type="date"
                name="term_end"
                value={formData.term_end}
                onChange={handleInputChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Renewal Terms
            </label>
            <textarea
              name="renewal_terms"
              value={formData.renewal_terms}
              onChange={handleInputChange}
              rows={3}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
              placeholder="Describe renewal terms, if any..."
            />
          </div>

          {/* File Upload */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Contract Files *
            </label>
            <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center">
              <Upload className="mx-auto h-12 w-12 text-gray-400" />
              <div className="mt-2">
                <label htmlFor="file-upload" className="cursor-pointer">
                  <span className="text-blue-600 hover:text-blue-500 font-medium">
                    Click to upload
                  </span>
                  <span className="text-gray-500"> or drag and drop</span>
                </label>
                <input
                  id="file-upload"
                  name="file-upload"
                  type="file"
                  multiple
                  accept=".pdf,.docx,.txt"
                  onChange={handleFileChange}
                  className="sr-only"
                />
              </div>
              <p className="text-xs text-gray-500 mt-1">
                PDF, DOCX, or TXT files up to 10MB each
              </p>
            </div>
          </div>

          {/* File List */}
          {files.length > 0 && (
            <div>
              <h4 className="text-sm font-medium text-gray-700 mb-2">Uploaded Files:</h4>
              <div className="space-y-2">
                {files.map((file, index) => (
                  <div key={index} className="flex items-center justify-between p-2 bg-gray-50 rounded">
                    <div className="flex items-center">
                      <FileText className="h-4 w-4 text-gray-400 mr-2" />
                      <span className="text-sm text-gray-700">{file.name}</span>
                      <span className="text-xs text-gray-500 ml-2">
                        ({(file.size / 1024 / 1024).toFixed(2)} MB)
                      </span>
                    </div>
                    <button
                      type="button"
                      onClick={() => removeFile(index)}
                      className="text-red-400 hover:text-red-600"
                    >
                      <X className="h-4 w-4" />
                    </button>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Submit Buttons */}
          <div className="flex justify-end space-x-3 pt-4">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={loading}
              className="px-4 py-2 text-sm font-medium text-white bg-blue-600 border border-transparent rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
            >
              {loading ? 'Uploading...' : 'Upload Contract'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
