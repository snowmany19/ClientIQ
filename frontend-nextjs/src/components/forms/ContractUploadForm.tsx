'use client';

import { useState, useRef } from 'react';
import { useRouter } from 'next/navigation';
import { apiClient } from '@/lib/api';
import { ContractCreate } from '@/types';
import { Upload, FileText, X, AlertCircle } from 'lucide-react';
import { useCreateContract } from '@/lib/hooks/useContracts';

interface ContractUploadFormProps {
  onClose: () => void;
  onSuccess: () => void;
}

export default function ContractUploadForm({ onClose, onSuccess }: ContractUploadFormProps) {
  const router = useRouter();
  const fileInputRef = useRef<HTMLInputElement>(null);
  
  // Use the create contract hook for proper cache invalidation
  const createContractMutation = useCreateContract();
  
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
  const [fileUploadLoading, setFileUploadLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Combine loading states
  const isLoading = createContractMutation.isPending || fileUploadLoading;

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    console.log('File input change event triggered');
    console.log('Event target:', e.target);
    console.log('Event target files:', e.target.files);
    
    if (e.target.files) {
      const fileList = e.target.files;
      console.log('FileList length:', fileList.length);
      
      if (fileList.length > 0) {
        const newFiles = Array.from(fileList);
        console.log('Files selected:', newFiles.map(f => ({ name: f.name, size: f.size, type: f.type })));
        
        // Validate files
        const validFiles = newFiles.filter(file => {
          console.log('Validating file:', file.name, 'Size:', file.size, 'Type:', file.type);
          if (!file || file.size === 0) {
            console.error('Invalid file detected:', file);
            return false;
          }
          if (file.size > 10 * 1024 * 1024) { // 10MB limit
            console.error('File too large:', file.name, file.size);
            return false;
          }
          return true;
        });
        
        console.log('Valid files:', validFiles.length, 'Total files:', newFiles.length);
        
        if (validFiles.length !== newFiles.length) {
          setError(`Some files were invalid. Please ensure all files are valid and under 10MB.`);
          return;
        }
        
        setFiles(prev => {
          const updatedFiles = [...prev, ...validFiles];
          console.log('Files state updated. Total files:', updatedFiles.length);
          return updatedFiles;
        });
        setError(null); // Clear any previous errors
      } else {
        console.log('No files selected');
      }
    } else {
      console.log('No files property on target');
    }
  };

  const removeFile = (index: number) => {
    setFiles(prev => prev.filter((_, i) => i !== index));
  };

  const clearAllFiles = () => {
    setFiles([]);
    setError(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const triggerFileInput = () => {
    if (fileInputRef.current) {
      fileInputRef.current.click();
    }
  };

  // Helper function to convert date string to ISO format
  const formatDateForBackend = (dateString: string): string | undefined => {
    if (!dateString) return undefined;
    try {
      const date = new Date(dateString);
      if (isNaN(date.getTime())) return undefined;
      return date.toISOString();
    } catch {
      return undefined;
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    console.log('=== FORM SUBMISSION START ===');
    console.log('Form submitted with files:', files);
    console.log('Files details:', files.map(f => ({ name: f.name, size: f.size, type: f.type })));
    
    if (!formData.title || !formData.counterparty) {
      setError('Title and counterparty are required');
      return;
    }

    if (files.length === 0) {
      setError('Please upload at least one contract file');
      return;
    }

    // Validate that files are not empty (0 bytes)
    const emptyFiles = files.filter(f => !f || f.size === 0);
    if (emptyFiles.length > 0) {
      setError(`One or more selected files are empty (0 bytes): ${emptyFiles.map(f => f.name).join(', ')}. Please select valid files.`);
      return;
    }

    setFileUploadLoading(true); // Start file upload loading
    setError(null);

    try {
      // Format dates for backend
      const contractData: ContractCreate = {
        ...formData as ContractCreate,
        effective_date: formatDateForBackend(formData.effective_date || ''),
        term_end: formatDateForBackend(formData.term_end || ''),
        uploaded_files: [] // Will be populated after file upload
      };

      console.log('=== CONTRACT CREATION ===');
      console.log('Sending contract data to backend:', contractData);

      const contract = await createContractMutation.mutateAsync(contractData);

      console.log('Contract created successfully:', contract);
      console.log('Contract ID:', contract.id);

      // Upload files
      console.log('=== FILE UPLOAD START ===');
      console.log('Starting file upload for', files.length, 'files');
      
      for (let i = 0; i < files.length; i++) {
        const file = files[i];
        try {
          console.log(`--- Uploading file ${i + 1}/${files.length} ---`);
          console.log('File details:', { name: file.name, size: file.size, type: file.type });
          console.log('File object:', file);
          console.log('Contract ID for upload:', contract.id);
          
          const uploadResult = await apiClient.uploadContractFile(contract.id, file);
          console.log('File upload result:', uploadResult);
          console.log('File upload successful for:', file.name);
        } catch (uploadError: any) {
          console.error('=== FILE UPLOAD ERROR ===');
          console.error('File upload failed for', file.name, ':', uploadError);
          console.error('Error details:', {
            name: uploadError.name,
            message: uploadError.message,
            stack: uploadError.stack
          });
          throw new Error(`Failed to upload file ${file.name}: ${uploadError}`);
        }
      }

      console.log('=== ALL FILES UPLOADED SUCCESSFULLY ===');
      
      // Wait a moment for backend to process the upload
      console.log('Waiting for backend to process upload...');
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      // Refresh the contract data to get updated uploaded_files
      console.log('Refreshing contract data...');
      const refreshedContract = await apiClient.getContract(contract.id);
      console.log('Refreshed contract data:', refreshedContract);
      
      console.log('=== FORM SUBMISSION COMPLETE ===');
      onSuccess();
      onClose();
      router.push(`/dashboard/contracts/${contract.id}`);
    } catch (error: any) {
      console.error('=== FORM SUBMISSION ERROR ===');
      console.error('Failed to create contract:', error);
      console.error('Error details:', {
        name: error.name,
        message: error.message,
        stack: error.stack
      });
      setError('Failed to create contract. Please try again.');
    } finally {
      setFileUploadLoading(false); // End file upload loading
    }
  };

  return (
    <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
      <div className="relative top-20 mx-auto p-5 border w-full max-w-2xl shadow-lg rounded-md bg-white dark:bg-gray-900 border-gray-200 dark:border-gray-700">
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100">Upload Contract</h3>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 dark:text-gray-500 dark:hover:text-gray-300"
          >
            <X className="h-6 w-6" />
          </button>
        </div>

        {error && (
          <div className="mb-4 p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-md">
            <div className="flex items-center">
              <AlertCircle className="h-5 w-5 text-red-400 dark:text-red-500 mr-2" />
              <span className="text-sm text-red-700 dark:text-red-300">{error}</span>
            </div>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          {/* Basic Information */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-semibold text-gray-900 dark:text-gray-100 mb-1">
                Contract Title *
              </label>
              <input
                type="text"
                name="title"
                value={formData.title}
                onChange={handleInputChange}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:ring-blue-500 focus:border-blue-500 bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 placeholder-gray-500 dark:placeholder-gray-400"
                placeholder="e.g., Vendor Service Agreement"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-semibold text-gray-900 dark:text-gray-100 mb-1">
                Counterparty *
              </label>
              <input
                type="text"
                name="counterparty"
                value={formData.counterparty}
                onChange={handleInputChange}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:ring-blue-500 focus:border-blue-500 bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 placeholder-gray-500 dark:placeholder-gray-400"
                placeholder="e.g., ABC Corporation"
                required
              />
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-semibold text-gray-900 dark:text-gray-100 mb-1">
                Category
              </label>
              <select
                name="category"
                value={formData.category}
                onChange={handleInputChange}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:ring-blue-500 focus:border-blue-500 bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100"
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
              <label className="block text-sm font-semibold text-gray-900 dark:text-gray-100 mb-1">
                Governing Law
              </label>
              <input
                type="text"
                name="governing_law"
                value={formData.governing_law}
                onChange={handleInputChange}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:ring-blue-500 focus:border-blue-500 bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 placeholder-gray-500 dark:placeholder-gray-400"
                placeholder="e.g., California, USA"
              />
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-semibold text-gray-900 dark:text-gray-100 mb-1">
                Effective Date
              </label>
              <input
                type="date"
                name="effective_date"
                value={formData.effective_date}
                onChange={handleInputChange}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:ring-blue-500 focus:border-blue-500 bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100"
              />
            </div>

            <div>
              <label className="block text-sm font-semibold text-gray-900 dark:text-gray-100 mb-1">
                Term End
              </label>
              <input
                type="date"
                name="term_end"
                value={formData.term_end}
                onChange={handleInputChange}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:ring-blue-500 focus:border-blue-500 bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100"
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-semibold text-gray-900 dark:text-gray-100 mb-1">
              Renewal Terms
            </label>
            <textarea
              name="renewal_terms"
              value={formData.renewal_terms}
              onChange={handleInputChange}
              rows={3}
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:ring-blue-500 focus:border-blue-500 bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 placeholder-gray-500 dark:placeholder-gray-400"
              placeholder="Describe renewal terms, if any..."
            />
          </div>

          {/* File Upload */}
          <div>
            <label className="block text-sm font-semibold text-gray-900 dark:text-gray-100 mb-1">
              Contract Files *
            </label>
            <div className="border-2 border-dashed border-gray-300 dark:border-gray-600 rounded-lg p-6 text-center bg-gray-50 dark:bg-gray-800">
              <Upload className="mx-auto h-12 w-12 text-gray-400 dark:text-gray-500" />
              <div className="mt-2">
                <input
                  id="file-upload"
                  name="file-upload"
                  type="file"
                  multiple
                  accept=".pdf,.docx,.txt"
                  onChange={handleFileChange}
                  className="block w-full text-sm text-gray-500 dark:text-gray-400 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100 dark:file:bg-blue-900 dark:file:text-blue-200"
                />
              </div>
              <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                PDF, DOCX, or TXT files up to 10MB each
              </p>
            </div>
          </div>

          {/* File List */}
          {files.length > 0 && (
            <div>
              <div className="flex justify-between items-center mb-2">
                <h4 className="text-sm font-semibold text-gray-900 dark:text-gray-100">Uploaded Files:</h4>
                <button
                  type="button"
                  onClick={clearAllFiles}
                  className="text-sm text-red-600 hover:text-red-800 dark:text-red-400 dark:hover:text-red-300"
                >
                  Clear All
                </button>
              </div>
              <div className="space-y-2">
                {files.map((file, index) => (
                  <div key={index} className="flex items-center justify-between p-2 bg-gray-50 dark:bg-gray-800 rounded border border-gray-200 dark:border-gray-700">
                    <div className="flex items-center">
                      <FileText className="h-4 w-4 text-gray-400 dark:text-gray-500 mr-2" />
                      <span className="text-sm text-gray-700 dark:text-gray-300">{file.name}</span>
                      <span className="text-xs text-gray-500 dark:text-gray-400 ml-2">
                        ({(file.size / 1024 / 1024).toFixed(2)} MB)
                      </span>
                    </div>
                    <button
                      type="button"
                      onClick={() => removeFile(index)}
                      className="text-red-400 hover:text-red-600 dark:text-red-500 dark:hover:text-red-400"
                    >
                      <X className="h-4 w-4" />
                    </button>
                  </div>
                ))}
              </div>
              <div className="mt-2 text-xs text-gray-500">
                Debug: {files.length} file(s) selected
              </div>
            </div>
          )}

          {/* Submit Buttons */}
          <div className="flex justify-end space-x-3 pt-4">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-md hover:bg-gray-50 dark:hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isLoading}
              className="px-4 py-2 text-sm font-medium text-white bg-blue-600 border border-transparent rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
            >
              {isLoading ? 'Uploading...' : 'Upload Contract'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
