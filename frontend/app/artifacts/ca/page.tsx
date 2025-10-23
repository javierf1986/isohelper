'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';

interface CorrectiveAction {
  id: string;
  ca_number: string;
  title: string;
  description: string;
  status: 'planned' | 'in_progress' | 'completed' | 'verified' | 'effective' | 'not_effective';
  priority: string;
  assigned_to: string;
  planned_completion_date: string;
  nc_id: string | null;
  created_at: string;
}

export default function CorrectiveActionsPage() {
  const router = useRouter();
  const [cas, setCas] = useState<CorrectiveAction[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchCAs();
  }, []);

  const fetchCAs = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('access_token');

      const response = await fetch('http://localhost:8889/api/artifacts/ca?limit=100', {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (!response.ok) throw new Error('Failed to fetch CAs');

      const data = await response.json();
      setCas(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority.toLowerCase()) {
      case 'urgent': return 'bg-red-100 text-red-800 border-red-300';
      case 'high': return 'bg-orange-100 text-orange-800 border-orange-300';
      case 'medium': return 'bg-yellow-100 text-yellow-800 border-yellow-300';
      case 'low': return 'bg-green-100 text-green-800 border-green-300';
      default: return 'bg-gray-100 text-gray-800 border-gray-300';
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'planned': return 'bg-blue-100 text-blue-800';
      case 'in_progress': return 'bg-purple-100 text-purple-800';
      case 'completed': return 'bg-green-100 text-green-800';
      case 'verified': return 'bg-teal-100 text-teal-800';
      case 'effective': return 'bg-emerald-100 text-emerald-800';
      case 'not_effective': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const isOverdue = (date: string) => {
    return new Date(date) < new Date() && new Date(date).toDateString() !== new Date().toDateString();
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center min-h-screen">
        <div className="text-lg">Loading...</div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Corrective Actions</h1>
        <p className="text-gray-600">Manage actions to eliminate causes of non-conformities</p>
      </div>

      {/* Actions Bar */}
      <div className="mb-6 flex justify-between items-center">
        <div className="text-sm text-gray-600">
          Showing {cas.length} corrective actions
        </div>
        <button
          onClick={() => router.push('/artifacts/ca/create')}
          className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
        >
          + Create CA
        </button>
      </div>

      {/* Statistics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-5 gap-4 mb-6">
        <div className="bg-white rounded-lg shadow p-4">
          <div className="text-sm text-gray-600">Total CAs</div>
          <div className="text-2xl font-bold text-gray-900">{cas.length}</div>
        </div>
        <div className="bg-white rounded-lg shadow p-4">
          <div className="text-sm text-gray-600">Planned</div>
          <div className="text-2xl font-bold text-blue-600">
            {cas.filter(ca => ca.status === 'planned').length}
          </div>
        </div>
        <div className="bg-white rounded-lg shadow p-4">
          <div className="text-sm text-gray-600">In Progress</div>
          <div className="text-2xl font-bold text-purple-600">
            {cas.filter(ca => ca.status === 'in_progress').length}
          </div>
        </div>
        <div className="bg-white rounded-lg shadow p-4">
          <div className="text-sm text-gray-600">Completed</div>
          <div className="text-2xl font-bold text-green-600">
            {cas.filter(ca => ca.status === 'completed').length}
          </div>
        </div>
        <div className="bg-white rounded-lg shadow p-4">
          <div className="text-sm text-gray-600">Effective</div>
          <div className="text-2xl font-bold text-emerald-600">
            {cas.filter(ca => ca.status === 'effective').length}
          </div>
        </div>
      </div>

      {/* Error Message */}
      {error && (
        <div className="mb-4 bg-red-50 border border-red-300 text-red-800 px-4 py-3 rounded">
          {error}
        </div>
      )}

      {/* CAs Table */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                CA Number
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Title
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Priority
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Status
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Due Date
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                NC Linked
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Actions
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {cas.length === 0 ? (
              <tr>
                <td colSpan={7} className="px-6 py-8 text-center text-gray-500">
                  No corrective actions found. Click "Create CA" to add one.
                </td>
              </tr>
            ) : (
              cas.map((ca) => (
                <tr key={ca.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-blue-600">
                    {ca.ca_number}
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-900 max-w-xs truncate">
                    {ca.title}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`px-2 py-1 text-xs font-medium rounded border ${getPriorityColor(ca.priority)}`}>
                      {ca.priority.toUpperCase()}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`px-2 py-1 text-xs font-medium rounded ${getStatusColor(ca.status)}`}>
                      {ca.status.replace('_', ' ').toUpperCase()}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">
                    <span className={isOverdue(ca.planned_completion_date) ? 'text-red-600 font-medium' : 'text-gray-500'}>
                      {new Date(ca.planned_completion_date).toLocaleDateString()}
                      {isOverdue(ca.planned_completion_date) && (
                        <span className="ml-1 text-xs">(Overdue)</span>
                      )}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {ca.nc_id ? (
                      <span className="text-blue-600 cursor-pointer hover:underline">
                        Linked
                      </span>
                    ) : (
                      '-'
                    )}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                    <button
                      onClick={() => router.push(`/artifacts/ca/${ca.id}`)}
                      className="text-blue-600 hover:text-blue-900 mr-3"
                    >
                      View
                    </button>
                    <button
                      onClick={() => router.push(`/artifacts/ca/${ca.id}/edit`)}
                      className="text-gray-600 hover:text-gray-900"
                    >
                      Edit
                    </button>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
