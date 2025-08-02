import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/Button';
import { Card } from '@/components/ui/card';
import { Upload, FileText, Trash2, Edit, Eye, CheckCircle, AlertCircle } from 'lucide-react';
import { apiClient } from '@/lib/api';

interface PolicyDocument {
  id: number;
  name: string;
  version: string;
  status: string;
  effective_date: string;
  created_at: string;
  sections_count: number;
}

export default function PolicyUploadForm() {
  const [policies, setPolicies] = useState<PolicyDocument[]>([]);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [policyName, setPolicyName] = useState('');
  const [isUploading, setIsUploading] = useState(false);
  const [uploadStatus, setUploadStatus] = useState<'idle' | 'success' | 'error'>('idle');
  const [uploadMessage, setUploadMessage] = useState('');

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    console.log('File select triggered', event.target.files);
    const file = event.target.files?.[0];
    if (file && file.type === 'application/pdf') {
      console.log('Valid PDF selected:', file.name);
      setSelectedFile(file);
      setPolicyName(file.name.replace('.pdf', ''));
    } else {
      console.log('Invalid file type:', file?.type);
      alert('Please select a valid PDF file');
    }
  };

  const handleUpload = async () => {
    if (!selectedFile || !policyName.trim()) {
      alert('Please select a file and enter a policy name');
      return;
    }

    setIsUploading(true);
    setUploadStatus('idle');

    try {
      const formData = new FormData();
      formData.append('file', selectedFile);
      formData.append('name', policyName);

      const response = await apiClient.uploadPolicy(formData);
      
      setUploadStatus('success');
      setUploadMessage('Policy uploaded and analyzed successfully!');
      
      // Reset form
      setSelectedFile(null);
      setPolicyName('');
      
      // Refresh policies list
      loadPolicies();
      
    } catch (error) {
      console.error('Error uploading policy:', error);
      setUploadStatus('error');
      setUploadMessage('Error uploading policy. Please try again.');
    } finally {
      setIsUploading(false);
    }
  };

  const loadPolicies = async () => {
    try {
      const policiesData = await apiClient.getPolicies();
      setPolicies(policiesData);
    } catch (error) {
      console.error('Error loading policies:', error);
    }
  };

  const handleActivatePolicy = async (policyId: number) => {
    try {
      await apiClient.activatePolicy(policyId.toString());
      loadPolicies(); // Refresh the list
    } catch (error) {
      console.error('Error activating policy:', error);
    }
  };

  const handleDeletePolicy = async (policyId: number) => {
    if (confirm('Are you sure you want to delete this policy?')) {
      try {
        await apiClient.deletePolicy(policyId.toString());
        loadPolicies(); // Refresh the list
      } catch (error) {
        console.error('Error deleting policy:', error);
      }
    }
  };

  // Load policies on component mount
  useEffect(() => {
    loadPolicies();
  }, []);

  return (
    <div className="space-y-6">
      {/* Upload Section */}
      <Card className="p-6">
        <h3 className="text-xl font-bold text-gray-900 mb-4">Upload HOA Policies</h3>
        <div className="border-2 border-dashed border-gray-400 rounded-lg p-6 text-center bg-gray-50">
          <Upload className="h-12 w-12 text-gray-600 mx-auto mb-4" />
          <p className="text-gray-900 mb-4 font-medium">
            Upload your HOA's policy document (PDF format) to enable AI-powered violation analysis
          </p>
          <input
            type="file"
            accept=".pdf"
            onChange={handleFileSelect}
            className="hidden"
            id="policy-upload"
          />
          <label 
            htmlFor="policy-upload" 
            className="cursor-pointer"
            onClick={() => {
              console.log('Label clicked');
              document.getElementById('policy-upload')?.click();
            }}
          >
            <Button 
              variant="outline" 
              className="mb-4"
              type="button"
            >
              Select PDF Policy Document
            </Button>
          </label>
          
          {selectedFile && (
            <div className="mt-4">
              <div className="flex items-center justify-center space-x-2 mb-4">
                <FileText className="h-5 w-5 text-blue-500" />
                <span className="text-sm text-gray-700">{selectedFile.name}</span>
              </div>
              
              <div className="mb-4">
                <label htmlFor="policy-name" className="block text-sm font-medium text-gray-700 mb-2">
                  Policy Name
                </label>
                <input
                  type="text"
                  id="policy-name"
                  value={policyName}
                  onChange={(e) => setPolicyName(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  placeholder="Enter policy name"
                />
              </div>
              
              <Button 
                onClick={handleUpload} 
                disabled={isUploading}
                className="w-full"
              >
                {isUploading ? 'Uploading and Analyzing...' : 'Upload & Analyze Policy'}
              </Button>
              
              {uploadStatus !== 'idle' && (
                <div className={`mt-4 p-3 rounded-md flex items-center space-x-2 ${
                  uploadStatus === 'success' 
                    ? 'bg-green-50 text-green-800' 
                    : 'bg-red-50 text-red-800'
                }`}>
                  {uploadStatus === 'success' ? (
                    <CheckCircle className="h-5 w-5" />
                  ) : (
                    <AlertCircle className="h-5 w-5" />
                  )}
                  <span className="text-sm">{uploadMessage}</span>
                </div>
              )}
            </div>
          )}
        </div>
      </Card>

      {/* Policy Management Section */}
      {policies.length > 0 && (
        <Card className="p-6">
          <h3 className="text-xl font-bold text-gray-900 mb-4">Policy Management</h3>
          <div className="space-y-4">
            {policies.map((policy) => (
              <div key={policy.id} className="border border-gray-200 rounded-lg p-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <FileText className="h-6 w-6 text-blue-500" />
                    <div>
                      <h4 className="font-medium text-gray-900">{policy.name}</h4>
                      <p className="text-sm text-gray-500">
                        Version {policy.version} • {policy.sections_count} sections
                      </p>
                      <p className="text-sm text-gray-500">
                        Created: {new Date(policy.created_at).toLocaleDateString()}
                      </p>
                    </div>
                  </div>
                  
                  <div className="flex items-center space-x-2">
                    <span className={`px-2 py-1 text-xs rounded-full ${
                      policy.status === 'active' 
                        ? 'bg-green-100 text-green-800' 
                        : policy.status === 'draft'
                        ? 'bg-yellow-100 text-yellow-800'
                        : 'bg-gray-100 text-gray-800'
                    }`}>
                      {policy.status}
                    </span>
                    
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handleActivatePolicy(policy.id)}
                      disabled={policy.status === 'active'}
                    >
                      <Eye className="h-4 w-4 mr-1" />
                      {policy.status === 'active' ? 'Active' : 'Activate'}
                    </Button>
                    
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handleDeletePolicy(policy.id)}
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </Card>
      )}

      {/* AI Training Status Section */}
      <Card className="p-6">
        <h3 className="text-xl font-bold text-gray-900 mb-4">AI Training Status</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="bg-blue-50 p-4 rounded-lg">
            <h4 className="font-bold text-blue-900 mb-2 text-lg">Active Policies</h4>
            <p className="text-2xl font-bold text-blue-600">
              {policies.filter(p => p.status === 'active').length}
            </p>
          </div>
          
          <div className="bg-green-50 p-4 rounded-lg">
            <h4 className="font-bold text-green-900 mb-2 text-lg">AI Status</h4>
            <p className="text-sm text-green-700">
              AI analysis enabled for custom policy enforcement
            </p>
          </div>
        </div>
        
        <div className="mt-4 p-4 bg-gray-50 rounded-lg">
                      <h4 className="font-bold text-gray-900 mb-2 text-lg">How it works</h4>
          <ul className="text-sm text-gray-800 space-y-1 font-medium">
            <li>• Upload your HOA's policy document as a PDF</li>
            <li>• AI extracts rules, violation types, and enforcement procedures</li>
            <li>• Violation analysis is customized to your specific policies</li>
            <li>• Letter generation uses your HOA's language and procedures</li>
          </ul>
        </div>
      </Card>
    </div>
  );
} 