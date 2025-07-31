'use client';

import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/Button';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Plus, Mail, Download } from 'lucide-react';
import ResidentInviteForm from '@/components/forms/ResidentInviteForm';
import { apiClient } from '@/lib/api';

interface User {
  id: number;
  email: string;
  name: string;
  role: string;
  unit_number?: string;
  is_active: boolean;
  created_at: string;
}

export default function UserManagement() {
  const [users, setUsers] = useState<User[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [showInviteForm, setShowInviteForm] = useState(false);
  const [inviteResults, setInviteResults] = useState<any>(null);

  useEffect(() => {
    fetchUsers();
  }, []);

  const fetchUsers = async () => {
    try {
      console.log('Fetching users using API client...');
      const backendUsers = await apiClient.getUsers();
      console.log('Backend users received:', backendUsers);
      
      // Transform backend users to match frontend expectations
      const transformedUsers = backendUsers.map((user: any) => ({
        id: user.id,
        email: user.email,
        name: user.username || user.name || 'Unknown', // Use username as name
        role: user.role,
        unit_number: user.unit_number || null,
        is_active: user.subscription_status === 'active' || true, // Default to active
        created_at: user.created_at || new Date().toISOString(), // Default to current date
      }));
      
      console.log('Transformed users:', transformedUsers);
      setUsers(transformedUsers);
    } catch (error) {
      console.error('Error fetching users:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleInviteResidents = async (invites: any[]) => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch('/api/resident-portal/invite', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ invites })
      });

      const data = await response.json();
      
      if (response.ok) {
        setInviteResults(data);
        setShowInviteForm(false);
        // Refresh users list
        fetchUsers();
      } else {
        throw new Error(data.error || 'Failed to send invitations');
      }
    } catch (error) {
      console.error('Error inviting residents:', error);
      alert('Failed to send invitations. Please try again.');
    }
  };

  const getRoleBadgeColor = (role: string) => {
    switch (role) {
      case 'admin': return 'bg-red-100 text-red-800';
      case 'hoa_board': return 'bg-blue-100 text-blue-800';
      case 'inspector': return 'bg-green-100 text-green-800';
      case 'resident': return 'bg-gray-100 text-gray-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const downloadCsvTemplate = () => {
    const csvContent = 'email,name,unit_number\njohn@example.com,John Doe,101\njane@example.com,Jane Smith,102';
    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'resident_invites_template.csv';
    a.click();
    window.URL.revokeObjectURL(url);
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-gray-500">Loading users...</div>
      </div>
    );
  }

  if (showInviteForm) {
    return (
      <ResidentInviteForm
        onInvite={handleInviteResidents}
        onCancel={() => setShowInviteForm(false)}
      />
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">User Management</h1>
          <p className="text-gray-600">Manage HOA staff and resident accounts</p>
          <p className="text-sm text-blue-600">Debug: {users.length} users loaded</p>
        </div>
        <div className="flex space-x-3">
          <Button variant="outline" onClick={downloadCsvTemplate}>
            <Download className="h-4 w-4 mr-2" />
            CSV Template
          </Button>
          <Button onClick={() => setShowInviteForm(true)}>
            <Mail className="h-4 w-4 mr-2" />
            Invite Residents
          </Button>
          <Button>
            <Plus className="h-4 w-4 mr-2" />
            Add User
          </Button>
        </div>
      </div>

      {inviteResults && (
        <Card className="p-4 bg-green-50 border-green-200">
          <h3 className="font-medium text-green-900 mb-2">Invitation Results</h3>
          <p className="text-sm text-green-700 mb-2">{inviteResults.message}</p>
          {inviteResults.successful_invites.length > 0 && (
            <div className="mb-2">
              <p className="text-sm font-medium text-green-800">Successful ({inviteResults.successful_invites.length}):</p>
              <ul className="text-sm text-green-700">
                {inviteResults.successful_invites.map((invite: any, index: number) => (
                  <li key={index}>• {invite.name} ({invite.email}) - Unit {invite.unit_number}</li>
                ))}
              </ul>
            </div>
          )}
          {inviteResults.failed_invites.length > 0 && (
            <div>
              <p className="text-sm font-medium text-red-800">Failed ({inviteResults.failed_invites.length}):</p>
              <ul className="text-sm text-red-700">
                {inviteResults.failed_invites.map((invite: any, index: number) => (
                  <li key={index}>• {invite.email} - {invite.reason}</li>
                ))}
              </ul>
            </div>
          )}
          <Button
            variant="outline"
            size="sm"
            onClick={() => setInviteResults(null)}
            className="mt-2 text-green-700 hover:text-green-800"
          >
            Dismiss
          </Button>
        </Card>
      )}

      <Card className="p-6">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  User
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Role
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Unit
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Created
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {users.map((user) => (
                <tr key={user.id}>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div>
                      <div className="text-sm font-medium text-gray-900">{user.name}</div>
                      <div className="text-sm text-gray-500">{user.email}</div>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <Badge className={getRoleBadgeColor(user.role)}>
                      {user.role.replace('_', ' ')}
                    </Badge>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {user.unit_number || '-'}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <Badge className={user.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}>
                      {user.is_active ? 'Active' : 'Inactive'}
                    </Badge>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {new Date(user.created_at).toLocaleDateString()}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                    <Button variant="outline" size="sm">
                      Edit
                    </Button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>
    </div>
  );
} 