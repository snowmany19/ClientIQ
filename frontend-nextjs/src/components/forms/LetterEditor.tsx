'use client';

import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/Button';
import { apiClient } from '@/lib/api';
import { Violation } from '@/types';
import { 
  X, 
  Download, 
  FileText, 
  Loader2,
  Save,
  Edit3
} from 'lucide-react';

interface LetterEditorProps {
  violation: Violation;
  isOpen: boolean;
  onClose: () => void;
}

export default function LetterEditor({ violation, isOpen, onClose }: LetterEditorProps) {
  const [letterContent, setLetterContent] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isGenerating, setIsGenerating] = useState(false);
  const [isDownloading, setIsDownloading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Generate letter when modal opens
  useEffect(() => {
    if (isOpen && !letterContent) {
      generateLetter();
    }
  }, [isOpen, violation.id]);

  const generateLetter = async () => {
    setIsGenerating(true);
    setError(null);
    
    try {
      const response = await apiClient.generateViolationLetter(violation.id);
      setLetterContent(response.letter_content);
    } catch (err) {
      setError('Failed to generate letter. Please try again.');
      console.error('Error generating letter:', err);
    } finally {
      setIsGenerating(false);
    }
  };

  const downloadPDF = async () => {
    setIsDownloading(true);
    setError(null);
    
    try {
      const blob = await apiClient.generateLetterPDF(letterContent);
      
      // Create download link
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `violation_letter_${violation.violation_number}_${new Date().toISOString().split('T')[0]}.pdf`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
    } catch (err) {
      setError('Failed to download PDF. Please try again.');
      console.error('Error downloading PDF:', err);
    } finally {
      setIsDownloading(false);
    }
  };

  const handleSave = () => {
    // For now, just close the modal
    // In the future, you could save the letter to the database
    onClose();
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl w-full max-w-4xl h-[90vh] flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <div className="flex items-center space-x-3">
            <FileText className="h-6 w-6 text-blue-600" />
            <div>
              <h2 className="text-xl font-bold text-gray-900">
                Violation Letter - #{violation.violation_number}
              </h2>
              <p className="text-sm text-gray-700 font-medium">
                {violation.address} • {violation.offender}
              </p>
            </div>
          </div>
          <Button
            variant="outline"
            size="sm"
            onClick={onClose}
            className="text-gray-500 hover:text-gray-700 hover:bg-gray-100"
          >
            <X className="h-5 w-5" />
          </Button>
        </div>

        {/* Content */}
        <div className="flex-1 p-6 overflow-hidden">
          {error && (
            <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-md">
              <p className="text-red-800 text-sm font-medium">{error}</p>
            </div>
          )}

          {isGenerating ? (
            <div className="flex items-center justify-center h-full">
              <div className="text-center">
                <Loader2 className="h-8 w-8 animate-spin text-blue-600 mx-auto mb-4" />
                <p className="text-gray-900 font-medium">Generating violation letter...</p>
              </div>
            </div>
          ) : (
            <div className="h-full flex flex-col">
              {/* Editor */}
              <div className="flex-1">
                <label className="block text-sm font-semibold text-gray-900 mb-2">
                  Letter Content
                </label>
                <textarea
                  value={letterContent}
                  onChange={(e) => setLetterContent(e.target.value)}
                  className="w-full h-full p-4 border border-gray-300 rounded-md resize-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 font-mono text-sm text-gray-900 bg-white"
                  placeholder="Letter content will be generated automatically..."
                />
              </div>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="flex items-center justify-between p-6 border-t border-gray-200 bg-gray-50">
          <div className="flex items-center space-x-2">
            <Button
              variant="outline"
              size="sm"
              onClick={generateLetter}
              disabled={isGenerating}
              className="flex items-center space-x-2 border-gray-300 text-gray-700 hover:bg-gray-50 hover:text-gray-900"
            >
              {isGenerating ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <Edit3 className="h-4 w-4" />
              )}
              <span className="font-medium">Regenerate</span>
            </Button>
          </div>

          <div className="flex items-center space-x-3">
            <Button
              variant="outline"
              size="sm"
              onClick={onClose}
              className="border-gray-300 text-gray-700 hover:bg-gray-50 hover:text-gray-900"
            >
              <span className="font-medium">Cancel</span>
            </Button>
            
            <Button
              variant="outline"
              size="sm"
              onClick={downloadPDF}
              disabled={isDownloading || !letterContent}
              className="flex items-center space-x-2 border-gray-300 text-gray-700 hover:bg-gray-50 hover:text-gray-900"
            >
              {isDownloading ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <Download className="h-4 w-4" />
              )}
              <span className="font-medium">Download PDF</span>
            </Button>

            <Button
              size="sm"
              onClick={handleSave}
              disabled={!letterContent}
              className="flex items-center space-x-2 bg-blue-600 text-white hover:bg-blue-700 border border-blue-600"
            >
              <Save className="h-4 w-4" />
              <span className="font-medium">Save & Close</span>
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
} 