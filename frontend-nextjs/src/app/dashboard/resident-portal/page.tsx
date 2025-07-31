'use client';

import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/Button';
import { apiClient } from '@/lib/api';

interface Violation {
  id: number;
  violation_number: number;
  timestamp: string;
  description: string;
  summary?: string;
  tags?: string;
  repeat_offender_score?: number;
  hoa_name?: string;
  address: string;
  location?: string;
  offender?: string;
  status: string;
  letter_content?: string;
  letter_status?: string;
  letter_sent_at?: string;
}

interface Letter {
  letter_id: number;
  violation_id: number;
  violation_number: number;
  description: string;
  address: string;
  sent_at: string;
  status: string;
  opened_at?: string;
  letter_content: string;
}

export default function ResidentPortalPage() {
  const [violations, setViolations] = useState<Violation[]>([]);
  const [letters, setLetters] = useState<Letter[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'violations' | 'letters'>('violations');
  const [selectedViolation, setSelectedViolation] = useState<Violation | null>(null);
  const [showLetterModal, setShowLetterModal] = useState(false);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      
      // Load violations using API client
      const violationsData = await apiClient.getMyViolations();
      setViolations(violationsData);
      
      // Load letters using API client
      try {
        const lettersData = await apiClient.getMyLetters();
        setLetters(lettersData);
      } catch (letterError) {
        console.warn('Failed to load letters:', letterError);
        setLetters([]);
      }
      
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load data');
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'open': return 'text-red-600 bg-red-100';
      case 'resolved': return 'text-green-600 bg-green-100';
      case 'disputed': return 'text-yellow-600 bg-yellow-100';
      case 'sent': return 'text-blue-600 bg-blue-100';
      case 'opened': return 'text-green-600 bg-green-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const viewLetter = async (violation: Violation) => {
    try {
      const letterData = await apiClient.getViolationLetter(violation.id);
      setSelectedViolation({ ...violation, ...letterData });
      setShowLetterModal(true);
      
      // Mark as read
      await apiClient.markLetterAsRead(violation.id);
    } catch (err) {
      console.error('Error viewing letter:', err);
    }
  };

  if (loading) {
    return (
      <div className="container mx-auto p-6">
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="container mx-auto p-6">
        <div className="bg-red-50 border border-red-200 rounded-md p-4">
          <p className="text-red-800">{error}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto p-6">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Resident Portal</h1>
        <p className="text-gray-600">View and manage your violations and letters</p>
      </div>

      {/* Tab Navigation */}
      <div className="mb-6">
        <div className="border-b border-gray-200">
          <nav className="-mb-px flex space-x-8">
            <button
              onClick={() => setActiveTab('violations')}
              className={`py-2 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'violations'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              My Violations ({violations.length})
            </button>
            <button
              onClick={() => setActiveTab('letters')}
              className={`py-2 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'letters'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              Violation Letters ({letters.length})
            </button>
          </nav>
        </div>
      </div>

      {/* Violations Tab */}
      {activeTab === 'violations' && (
        <div className="bg-white shadow rounded-lg">
          <div className="px-6 py-4 border-b border-gray-200">
            <h2 className="text-lg font-medium text-gray-900">My Violations</h2>
          </div>
          
          <div className="p-6">
            {violations.length === 0 ? (
              <div className="text-center py-8">
                <p className="text-gray-500">No violations found.</p>
              </div>
            ) : (
              <div className="space-y-4">
                {violations.map((violation) => (
                  <div key={violation.id} className="border border-gray-200 rounded-lg p-4">
                    <div className="flex justify-between items-start">
                      <div className="flex-1">
                        <h3 className="font-medium text-gray-900">
                          Violation #{violation.violation_number}
                        </h3>
                        <p className="text-gray-600 mt-1">{violation.description}</p>
                        <div className="flex items-center space-x-4 mt-2 text-sm text-gray-500">
                          <span>Created: {new Date(violation.timestamp).toLocaleDateString()}</span>
                          {violation.address && (
                            <span>Address: {violation.address}</span>
                          )}
                          {violation.letter_status && (
                            <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(violation.letter_status)}`}>
                              Letter: {violation.letter_status}
                            </span>
                          )}
                        </div>
                      </div>
                      <div className="flex items-center space-x-2">
                        <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(violation.status)}`}>
                          {violation.status}
                        </span>
                        {violation.letter_content && (
                          <Button 
                            size="sm" 
                            variant="outline"
                            onClick={() => viewLetter(violation)}
                          >
                            View Letter
                          </Button>
                        )}
                        <Button 
                          size="sm" 
                          variant="outline"
                          onClick={() => {
                            setSelectedViolation(violation);
                            setShowLetterModal(true);
                          }}
                        >
                          View Details
                        </Button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}

      {/* Letters Tab */}
      {activeTab === 'letters' && (
        <div className="bg-white shadow rounded-lg">
          <div className="px-6 py-4 border-b border-gray-200">
            <h2 className="text-lg font-medium text-gray-900">Violation Letters</h2>
          </div>
          
          <div className="p-6">
            {letters.length === 0 ? (
              <div className="text-center py-8">
                <p className="text-gray-500">No letters found.</p>
              </div>
            ) : (
              <div className="space-y-4">
                {letters.map((letter) => (
                  <div key={letter.letter_id} className="border border-gray-200 rounded-lg p-4">
                    <div className="flex justify-between items-start">
                      <div className="flex-1">
                        <h3 className="font-medium text-gray-900">
                          Letter for Violation #{letter.violation_number}
                        </h3>
                        <p className="text-gray-600 mt-1">{letter.description}</p>
                        <p className="text-gray-500 text-sm mt-1">{letter.address}</p>
                        <div className="flex items-center space-x-4 mt-2 text-sm text-gray-500">
                          <span>Sent: {new Date(letter.sent_at).toLocaleDateString()}</span>
                          {letter.opened_at && (
                            <span>Read: {new Date(letter.opened_at).toLocaleDateString()}</span>
                          )}
                        </div>
                      </div>
                      <div className="flex items-center space-x-2">
                        <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(letter.status)}`}>
                          {letter.status}
                        </span>
                        <Button 
                          size="sm" 
                          variant="outline"
                          onClick={() => {
                            setSelectedViolation({
                              id: letter.violation_id,
                              violation_number: letter.violation_number,
                              timestamp: letter.sent_at,
                              description: letter.description,
                              address: letter.address,
                              status: '',
                              letter_content: letter.letter_content,
                              letter_status: letter.status,
                              letter_sent_at: letter.sent_at
                            });
                            setShowLetterModal(true);
                          }}
                        >
                          View Letter
                        </Button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}

      {/* Letter Modal */}
      {showLetterModal && selectedViolation && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-2xl w-full mx-4 max-h-[80vh] overflow-y-auto">
            <div className="flex justify-between items-start mb-4">
              <h2 className="text-xl font-bold text-gray-900">
                Violation #{selectedViolation.violation_number}
              </h2>
              <button
                onClick={() => setShowLetterModal(false)}
                className="text-gray-400 hover:text-gray-600"
              >
                ✕
              </button>
            </div>
            
            <div className="prose max-w-none">
              <div className="bg-gray-50 p-4 rounded-lg mb-4">
                <p className="text-sm text-gray-600">
                  <strong>Created:</strong> {new Date(selectedViolation.timestamp).toLocaleString()}
                </p>
                <p className="text-sm text-gray-600">
                  <strong>Status:</strong> {selectedViolation.status}
                </p>
                <p className="text-sm text-gray-600">
                  <strong>Address:</strong> {selectedViolation.address}
                </p>
                {selectedViolation.location && (
                  <p className="text-sm text-gray-600">
                    <strong>Location:</strong> {selectedViolation.location}
                  </p>
                )}
                {selectedViolation.tags && (
                  <p className="text-sm text-gray-600">
                    <strong>Tags:</strong> {selectedViolation.tags}
                  </p>
                )}
              </div>
              
              <div className="mb-4">
                <h3 className="font-medium text-gray-900 mb-2">Description</h3>
                <p className="text-gray-800">{selectedViolation.description}</p>
              </div>
              
              {selectedViolation.summary && (
                <div className="mb-4">
                  <h3 className="font-medium text-gray-900 mb-2">Summary</h3>
                  <p className="text-gray-800">{selectedViolation.summary}</p>
                </div>
              )}
              
              {selectedViolation.letter_content && (
                <div className="mt-6 pt-4 border-t border-gray-200">
                  <h3 className="font-medium text-gray-900 mb-2">Violation Letter</h3>
                  <div className="bg-gray-50 p-4 rounded-lg mb-4">
                    <p className="text-sm text-gray-600">
                      <strong>Sent:</strong> {selectedViolation.letter_sent_at ? 
                        new Date(selectedViolation.letter_sent_at).toLocaleString() : 'Not sent'}
                    </p>
                    <p className="text-sm text-gray-600">
                      <strong>Status:</strong> {selectedViolation.letter_status || 'Not sent'}
                    </p>
                  </div>
                  <div className="whitespace-pre-line text-gray-800">
                    {selectedViolation.letter_content}
                  </div>
                </div>
              )}
            </div>
            
            <div className="mt-6 flex justify-end space-x-3">
              <Button
                variant="outline"
                onClick={() => setShowLetterModal(false)}
              >
                Close
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
} 