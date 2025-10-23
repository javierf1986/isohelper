'use client';

import { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';

interface CADetail {
  id: string;
  ca_number: string;
  title: string;
  description: string;
  action_plan: string;
  status: string;
  priority: string;
  assigned_to: string;
  nc_id?: string;
  nc_number?: string;
  planned_start_date: string;
  planned_completion_date: string;
  actual_start_date?: string;
  actual_completion_date?: string;
  progress_updates?: string;
  resources_required?: string;
  is_effective?: boolean;
  effectiveness_results?: string;
  effectiveness_check_date?: string;
  created_at: string;
  updated_at: string;
}

export default function CADetailPage() {
  const params = useParams();
  const router = useRouter();
  const caId = params.id as string;

  const [ca, setCA] = useState<CADetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchCADetail();
  }, [caId]);

  const fetchCADetail = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`http://localhost:8889/api/v1/artifacts/ca/${caId}`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        if (response.status === 404) {
          setError('Corrective Action not found');
        } else {
          setError('Failed to load Corrective Action');
        }
        setLoading(false);
        return;
      }

      const data = await response.json();
      setCA(data);
    } catch (err) {
      setError('Failed to connect to server');
      console.error('Error fetching CA:', err);
    } finally {
      setLoading(false);
    }
  };

  const getPriorityColor = (priority: string) => {
    const colors: Record<string, string> = {
      critical: 'bg-red-100 text-red-800',
      high: 'bg-orange-100 text-orange-800',
      medium: 'bg-yellow-100 text-yellow-800',
      low: 'bg-green-100 text-green-800',
    };
    return colors[priority.toLowerCase()] || 'bg-gray-100 text-gray-800';
  };

  const getStatusColor = (status: string) => {
    const colors: Record<string, string> = {
      planned: 'bg-blue-100 text-blue-800',
      in_progress: 'bg-purple-100 text-purple-800',
      completed: 'bg-green-100 text-green-800',
      effective: 'bg-teal-100 text-teal-800',
      not_effective: 'bg-red-100 text-red-800',
    };
    return colors[status.toLowerCase()] || 'bg-gray-100 text-gray-800';
  };

  const formatDate = (dateStr: string) => {
    return new Date(dateStr).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    });
  };

  const formatDateTime = (dateStr: string) => {
    return new Date(dateStr).toLocaleString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-lg">Loading Corrective Action...</div>
      </div>
    );
  }

  if (error || !ca) {
    return (
      <div className="flex flex-col items-center justify-center min-h-screen">
        <div className="text-xl text-red-600 mb-4">{error || 'Corrective Action not found'}</div>
        <button
          onClick={() => router.push('/artifacts/ca')}
          className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
        >
          Back to Corrective Actions
        </button>
      </div>
    );
  }

  return (
    <div className="p-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="mb-6">
        <button
          onClick={() => router.push('/artifacts/ca')}
          className="text-blue-600 hover:text-blue-800 mb-4 flex items-center"
        >
          ← Back to Corrective Actions
        </button>
        
        <div className="flex justify-between items-start">
          <div>
            <h1 className="text-3xl font-bold mb-2">{ca.ca_number}: {ca.title}</h1>
            <div className="flex gap-3 items-center">
              <span className={`px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(ca.status)}`}>
                {ca.status.replace('_', ' ').toUpperCase()}
              </span>
              <span className={`px-3 py-1 rounded-full text-sm font-medium ${getPriorityColor(ca.priority)}`}>
                Priority: {ca.priority.toUpperCase()}
              </span>
            </div>
          </div>
          <div className="flex gap-3">
            <button className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700">
              Edit
            </button>
            <button className="px-4 py-2 bg-gray-600 text-white rounded hover:bg-gray-700">
              Export PDF
            </button>
          </div>
        </div>
      </div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column - Main Details */}
        <div className="lg:col-span-2 space-y-6">
          {/* Description */}
          <div className="bg-white shadow rounded-lg p-6">
            <h2 className="text-xl font-semibold mb-3">Description</h2>
            <p className="text-gray-700 whitespace-pre-wrap">{ca.description}</p>
          </div>

          {/* Action Plan */}
          <div className="bg-white shadow rounded-lg p-6">
            <h2 className="text-xl font-semibold mb-3">Action Plan</h2>
            <p className="text-gray-700 whitespace-pre-wrap">{ca.action_plan}</p>
          </div>

          {/* Progress Updates */}
          {ca.progress_updates && (
            <div className="bg-white shadow rounded-lg p-6">
              <h2 className="text-xl font-semibold mb-3">Progress Updates</h2>
              <p className="text-gray-700 whitespace-pre-wrap">{ca.progress_updates}</p>
            </div>
          )}

          {/* Resources Required */}
          {ca.resources_required && (
            <div className="bg-white shadow rounded-lg p-6">
              <h2 className="text-xl font-semibold mb-3">Resources Required</h2>
              <p className="text-gray-700 whitespace-pre-wrap">{ca.resources_required}</p>
            </div>
          )}

          {/* Effectiveness Check */}
          {ca.is_effective !== undefined && ca.effectiveness_results && (
            <div className="bg-white shadow rounded-lg p-6">
              <h2 className="text-xl font-semibold mb-3">Effectiveness Check</h2>
              <div className="space-y-3">
                <div>
                  <span className="font-medium text-gray-700">Result: </span>
                  <span className={`px-2 py-1 rounded text-sm font-medium ${ca.is_effective ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}>
                    {ca.is_effective ? 'EFFECTIVE' : 'NOT EFFECTIVE'}
                  </span>
                </div>
                {ca.effectiveness_check_date && (
                  <div>
                    <span className="font-medium text-gray-700">Checked: </span>
                    <span className="text-gray-600">{formatDate(ca.effectiveness_check_date)}</span>
                  </div>
                )}
                <div>
                  <p className="font-medium text-gray-700 mb-1">Details:</p>
                  <p className="text-gray-700 whitespace-pre-wrap">{ca.effectiveness_results}</p>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Right Column - Info & Timeline */}
        <div className="space-y-6">
          {/* Key Information */}
          <div className="bg-white shadow rounded-lg p-6">
            <h2 className="text-xl font-semibold mb-4">Key Information</h2>
            <div className="space-y-3">
              <div>
                <p className="text-sm text-gray-500">Assigned To</p>
                <p className="font-medium">{ca.assigned_to}</p>
              </div>
              <div>
                <p className="text-sm text-gray-500">Priority</p>
                <p className="font-medium capitalize">{ca.priority}</p>
              </div>
              {ca.nc_number && (
                <div>
                  <p className="text-sm text-gray-500">Related NC</p>
                  <button
                    onClick={() => router.push(`/artifacts/nc/${ca.nc_id}`)}
                    className="font-medium text-blue-600 hover:text-blue-800"
                  >
                    {ca.nc_number}
                  </button>
                </div>
              )}
            </div>
          </div>

          {/* Timeline */}
          <div className="bg-white shadow rounded-lg p-6">
            <h2 className="text-xl font-semibold mb-4">Timeline</h2>
            <div className="space-y-4">
              <div>
                <p className="text-sm text-gray-500">Planned Start</p>
                <p className="font-medium">{formatDate(ca.planned_start_date)}</p>
              </div>
              {ca.actual_start_date && (
                <div>
                  <p className="text-sm text-gray-500">Actual Start</p>
                  <p className="font-medium">{formatDate(ca.actual_start_date)}</p>
                </div>
              )}
              <div>
                <p className="text-sm text-gray-500">Planned Completion</p>
                <p className="font-medium">{formatDate(ca.planned_completion_date)}</p>
              </div>
              {ca.actual_completion_date && (
                <div>
                  <p className="text-sm text-gray-500">Actual Completion</p>
                  <p className="font-medium">{formatDate(ca.actual_completion_date)}</p>
                </div>
              )}
              <div className="pt-3 border-t">
                <p className="text-sm text-gray-500">Created</p>
                <p className="text-sm">{formatDateTime(ca.created_at)}</p>
              </div>
              <div>
                <p className="text-sm text-gray-500">Last Updated</p>
                <p className="text-sm">{formatDateTime(ca.updated_at)}</p>
              </div>
            </div>
          </div>

          {/* Actions */}
          <div className="bg-white shadow rounded-lg p-6">
            <h2 className="text-xl font-semibold mb-4">Actions</h2>
            <div className="space-y-3">
              <button className="w-full px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700">
                Update Status
              </button>
              <button className="w-full px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700">
                Add Progress Update
              </button>
              <button className="w-full px-4 py-2 bg-purple-600 text-white rounded hover:bg-purple-700">
                Check Effectiveness
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
