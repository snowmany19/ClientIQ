'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/Button';
import { Card } from '@/components/ui/card';
import { Mail, X, Plus, Trash2 } from 'lucide-react';

interface UserInvite {
  email: string;
  name: string;
  role: string;
}

interface UserInviteFormProps {
  onInvite: (invites: UserInvite[]) => Promise<void>;
  onCancel: () => void;
}

export default function UserInviteForm({ onInvite, onCancel }: UserInviteFormProps) {
  const [invites, setInvites] = useState<UserInvite[]>([
    { email: '', name: '', role: 'viewer' }
  ]);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const addInvite = () => {
    setInvites([...invites, { email: '', name: '', role: 'viewer' }]);
  };

  const removeInvite = (index: number) => {
    if (invites.length > 1) {
      setInvites(invites.filter((_, i) => i !== index));
    }
  };

  const updateInvite = (index: number, field: keyof UserInvite, value: string) => {
    const newInvites = [...invites];
    newInvites[index] = { ...newInvites[index], [field]: value };
    setInvites(newInvites);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    const validInvites = invites.filter(invite => invite.email && invite.name);
    if (validInvites.length === 0) {
      alert('Please add at least one valid invitation.');
      return;
    }

    setIsSubmitting(true);
    try {
      await onInvite(validInvites);
    } catch (error) {
      console.error('Failed to send invitations:', error);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
      <div className="relative top-4 mx-auto p-6 border w-full max-w-2xl shadow-lg rounded-md bg-white">
        <div className="flex justify-between items-center mb-6">
          <div>
            <h2 className="text-2xl font-bold text-gray-900">Invite Users</h2>
            <p className="text-gray-600">Send invitations to new team members</p>
          </div>
          <button
            onClick={onCancel}
            className="text-gray-400 hover:text-gray-600"
          >
            <X className="h-6 w-6" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          {invites.map((invite, index) => (
            <Card key={index} className="p-4">
              <div className="flex items-center justify-between mb-3">
                <h3 className="text-lg font-medium text-gray-900">Invite #{index + 1}</h3>
                {invites.length > 1 && (
                  <button
                    type="button"
                    onClick={() => removeInvite(index)}
                    className="text-red-600 hover:text-red-700"
                  >
                    <Trash2 className="h-4 w-4" />
                  </button>
                )}
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Email Address *
                  </label>
                  <input
                    type="email"
                    required
                    value={invite.email}
                    onChange={(e) => updateInvite(index, 'email', e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="user@example.com"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Full Name *
                  </label>
                  <input
                    type="text"
                    required
                    value={invite.name}
                    onChange={(e) => updateInvite(index, 'name', e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="John Doe"
                  />
                </div>
              </div>
              
              <div className="mt-4">
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Role
                </label>
                <select
                  value={invite.role}
                  onChange={(e) => updateInvite(index, 'role', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  <option value="viewer">Viewer</option>
                  <option value="analyst">Analyst</option>
                  <option value="admin">Admin</option>
                </select>
              </div>
            </Card>
          ))}

          <div className="flex justify-center">
            <button
              type="button"
              onClick={addInvite}
              className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            >
              <Plus className="h-4 w-4 mr-2" />
              Add Another Invite
            </button>
          </div>

          <div className="flex justify-end space-x-3 pt-4 border-t">
            <Button
              type="button"
              variant="outline"
              onClick={onCancel}
              disabled={isSubmitting}
            >
              Cancel
            </Button>
            <Button
              type="submit"
              disabled={isSubmitting}
              className="bg-blue-600 hover:bg-blue-700"
            >
              <Mail className="h-4 w-4 mr-2" />
              {isSubmitting ? 'Sending...' : `Send ${invites.filter(i => i.email && i.name).length} Invitation(s)`}
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
}
