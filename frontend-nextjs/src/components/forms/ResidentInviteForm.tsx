'use client';

import React, { useState } from 'react';
import { Button } from '@/components/ui/Button';
import { Card } from '@/components/ui/card';
import { Plus, Upload, Users, Mail, X } from 'lucide-react';

interface ResidentInvite {
  email: string;
  name: string;
  unit_number: string;
}

interface ResidentInviteFormProps {
  onInvite: (invites: ResidentInvite[]) => Promise<void>;
  onCancel: () => void;
}

export default function ResidentInviteForm({ onInvite, onCancel }: ResidentInviteFormProps) {
  const [invites, setInvites] = useState<ResidentInvite[]>([]);
  const [currentInvite, setCurrentInvite] = useState<ResidentInvite>({
    email: '',
    name: '',
    unit_number: ''
  });
  const [isLoading, setIsLoading] = useState(false);
  const [csvFile, setCsvFile] = useState<File | null>(null);

  const addInvite = () => {
    if (currentInvite.email && currentInvite.name && currentInvite.unit_number) {
      setInvites([...invites, currentInvite]);
      setCurrentInvite({ email: '', name: '', unit_number: '' });
    }
  };

  const removeInvite = (index: number) => {
    setInvites(invites.filter((_, i) => i !== index));
  };

  const handleCsvUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file && file.type === 'text/csv') {
      setCsvFile(file);
      parseCsvFile(file);
    }
  };

  const parseCsvFile = (file: File) => {
    const reader = new FileReader();
    reader.onload = (e) => {
      const text = e.target?.result as string;
      const lines = text.split('\n');
      const csvInvites: ResidentInvite[] = [];
      
      // Skip header row
      for (let i = 1; i < lines.length; i++) {
        const line = lines[i].trim();
        if (line) {
          const [email, name, unit_number] = line.split(',').map(field => field.trim());
          if (email && name && unit_number) {
            csvInvites.push({ email, name, unit_number });
          }
        }
      }
      
      setInvites(csvInvites);
    };
    reader.readAsText(file);
  };

  const handleSubmit = async () => {
    if (invites.length === 0) return;
    
    setIsLoading(true);
    try {
      await onInvite(invites);
    } catch (error) {
      console.error('Error inviting residents:', error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-gray-900">Invite Residents</h2>
        <Button variant="outline" onClick={onCancel}>
          Cancel
        </Button>
      </div>

      {/* CSV Upload Section */}
      <Card className="p-6">
        <div className="flex items-center space-x-2 mb-4">
          <Upload className="h-5 w-5 text-blue-500" />
          <h3 className="text-lg font-medium">Bulk Upload (CSV)</h3>
        </div>
        
        <div className="space-y-4">
          <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center">
            <input
              type="file"
              accept=".csv"
              onChange={handleCsvUpload}
              className="hidden"
              id="csv-upload"
            />
            <label htmlFor="csv-upload" className="cursor-pointer">
              <Upload className="mx-auto h-12 w-12 text-gray-400" />
              <p className="mt-2 text-sm text-gray-600">
                Click to upload CSV file or drag and drop
              </p>
              <p className="text-xs text-gray-500">
                Format: email, name, unit_number
              </p>
            </label>
          </div>
          
          {csvFile && (
            <div className="flex items-center space-x-2 text-sm text-green-600">
              <Upload className="h-4 w-4" />
              <span>{csvFile.name} uploaded successfully</span>
            </div>
          )}
        </div>
      </Card>

      {/* Individual Invite Section */}
      <Card className="p-6">
        <div className="flex items-center space-x-2 mb-4">
          <Users className="h-5 w-5 text-blue-500" />
          <h3 className="text-lg font-medium">Individual Invites</h3>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
          <input
            type="email"
            placeholder="Email address"
            value={currentInvite.email}
            onChange={(e) => setCurrentInvite({...currentInvite, email: e.target.value})}
            className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <input
            type="text"
            placeholder="Full name"
            value={currentInvite.name}
            onChange={(e) => setCurrentInvite({...currentInvite, name: e.target.value})}
            className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <input
            type="text"
            placeholder="Unit number"
            value={currentInvite.unit_number}
            onChange={(e) => setCurrentInvite({...currentInvite, unit_number: e.target.value})}
            className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>
        
        <Button onClick={addInvite} disabled={!currentInvite.email || !currentInvite.name || !currentInvite.unit_number}>
          <Plus className="h-4 w-4 mr-2" />
          Add to List
        </Button>
      </Card>

      {/* Invites List */}
      {invites.length > 0 && (
        <Card className="p-6">
          <div className="flex items-center space-x-2 mb-4">
            <Mail className="h-5 w-5 text-blue-500" />
            <h3 className="text-lg font-medium">Invites to Send ({invites.length})</h3>
          </div>
          
          <div className="space-y-2">
            {invites.map((invite, index) => (
              <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <div className="flex-1">
                  <p className="font-medium">{invite.name}</p>
                  <p className="text-sm text-gray-600">{invite.email}</p>
                  <p className="text-sm text-gray-500">Unit {invite.unit_number}</p>
                </div>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => removeInvite(index)}
                  className="text-red-500 hover:text-red-700"
                >
                  <X className="h-4 w-4" />
                </Button>
              </div>
            ))}
          </div>
          
          <div className="mt-6 flex justify-end space-x-3">
            <Button variant="outline" onClick={() => setInvites([])}>
              Clear All
            </Button>
            <Button onClick={handleSubmit} disabled={isLoading}>
              {isLoading ? 'Sending Invites...' : `Send ${invites.length} Invites`}
            </Button>
          </div>
        </Card>
      )}
    </div>
  );
} 