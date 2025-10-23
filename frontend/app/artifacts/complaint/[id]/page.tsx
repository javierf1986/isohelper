'use client';

import { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';

interface ComplaintDetail {
  id: string;
  complaint_number: string;
  complaint_title: string;
  complaint_description: string;
  customer_name: string;
  received_date: string;
  complaint_source: string;
  product_service?: string;
  status: string;
  priority: string;
  assigned_to?: string;
  root_cause?: string;
  resolution?: string;
  resolution_date?: string;
  resolution_target_date?: string;
  customer_feedback?: string;
  preventive_measures?: string;
  created_at: string;
  updated_at: string;
}

export default function ComplaintDetailPage() {
  const params = useParams();
  const router = useRouter();
  const complaintId = params.id as string;

  const [complaint, setComplaint] = useState<ComplaintDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchComplaintDetail();
  }, [complaintId]);

  const fetchComplaintDetail = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`http://localhost:8889/api/v1/artifacts/complaint/${complaintId}`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        if (response.status === 404) {
          setError('Customer Complaint not found');
        } else {
          setError('Failed to load complaint');
        }
        setLoading(false);
        return;
      }

      const data = await response.json();
      setComplaint(data);
    } catch (err) {
      setError('Failed to connect to server');
      console.error('Error fetching complaint:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async () => {
    if (!window.confirm("Are you sure you want to delete this Customer Complaint? This action cannot be undone.")) {
      return;
    }

    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`http://localhost:8889/api/v1/artifacts/complaint/${complaintId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        throw new Error('Failed to delete Customer Complaint');
      }

      router.push('/artifacts/complaint');
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Failed to delete Customer Complaint');
    }
  };

  const getPriorityColor = (priority: string) => {
    const colors: Record<string, string> = {
      urgent: 'bg-red-100 text-red-800',
      high: 'bg-orange-100 text-orange-800',
      medium: 'bg-yellow-100 text-yellow-800',
      low: 'bg-green-100 text-green-800',
    };
    return colors[priority.toLowerCase()] || 'bg-gray-100 text-gray-800';
  };

  const getStatusColor = (status: string) => {
    const colors: Record<string, string> = {
      open: 'bg-blue-100 text-blue-800',
      investigating: 'bg-purple-100 text-purple-800',
      resolved: 'bg-green-100 text-green-800',
      closed: 'bg-gray-100 text-gray-800',
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

  const isOverdue = (targetDate: string) => {
    return new Date(targetDate) < new Date();
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-lg">Loading Customer Complaint...</div>
      </div>
    );
  }

  if (error || !complaint) {
    return (
      <div className="flex flex-col items-center justify-center min-h-screen">
        <div className="text-xl text-red-600 mb-4">{error || 'Customer Complaint not found'}</div>
        <button
          onClick={() => router.push('/artifacts/complaint')}
          className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
        >
          Back to Customer Complaints
        </button>
      </div>
    );
  }

  return (
    <div className="p-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="mb-6">
        <button
          onClick={() => router.push('/artifacts/complaint')}
          className="text-blue-600 hover:text-blue-800 mb-4 flex items-center"
        >
          ← Back to Customer Complaints
        </button>
        
        <div className="flex justify-between items-start">
          <div>
            <h1 className="text-3xl font-bold mb-2">{complaint.complaint_number}: {complaint.complaint_title}</h1>
            <div className="flex gap-3 items-center">
              <span className={`px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(complaint.status)}`}>
                {complaint.status.toUpperCase()}
              </span>
              <span className={`px-3 py-1 rounded-full text-sm font-medium ${getPriorityColor(complaint.priority)}`}>
                Priority: {complaint.priority.toUpperCase()}
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
            <button 
              onClick={handleDelete}
              className="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700"
            >
              Delete
            </button>
          </div>
        </div>
      </div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column - Main Details */}
        <div className="lg:col-span-2 space-y-6">
          {/* Complaint Description */}
          <div className="bg-white shadow rounded-lg p-6">
            <h2 className="text-xl font-semibold mb-3">Complaint Description</h2>
            <p className="text-gray-700 whitespace-pre-wrap">{complaint.complaint_description}</p>
          </div>

          {/* Root Cause */}
          {complaint.root_cause && (
            <div className="bg-white shadow rounded-lg p-6">
              <h2 className="text-xl font-semibold mb-3">Root Cause Analysis</h2>
              <p className="text-gray-700 whitespace-pre-wrap">{complaint.root_cause}</p>
            </div>
          )}

          {/* Resolution */}
          {complaint.resolution && (
            <div className="bg-white shadow rounded-lg p-6 border-l-4 border-green-500">
              <h2 className="text-xl font-semibold mb-3">Resolution</h2>
              <p className="text-gray-700 whitespace-pre-wrap">{complaint.resolution}</p>
              {complaint.resolution_date && (
                <p className="text-sm text-gray-500 mt-3">
                  Resolved on: {formatDate(complaint.resolution_date)}
                </p>
              )}
            </div>
          )}

          {/* Customer Feedback */}
          {complaint.customer_feedback && (
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
              <h2 className="text-xl font-semibold mb-3 text-blue-900">Customer Feedback</h2>
              <p className="text-blue-800 whitespace-pre-wrap">{complaint.customer_feedback}</p>
            </div>
          )}

          {/* Preventive Measures */}
          {complaint.preventive_measures && (
            <div className="bg-white shadow rounded-lg p-6">
              <h2 className="text-xl font-semibold mb-3">Preventive Measures</h2>
              <p className="text-gray-700 whitespace-pre-wrap">{complaint.preventive_measures}</p>
            </div>
          )}
        </div>

        {/* Right Column - Info & Timeline */}
        <div className="space-y-6">
          {/* Customer Information */}
          <div className="bg-white shadow rounded-lg p-6">
            <h2 className="text-xl font-semibold mb-4">Customer Information</h2>
            <div className="space-y-3">
              <div>
                <p className="text-sm text-gray-500">Customer Name</p>
                <p className="font-medium">{complaint.customer_name}</p>
              </div>
              <div>
                <p className="text-sm text-gray-500">Received Date</p>
                <p className="font-medium">{formatDate(complaint.received_date)}</p>
              </div>
              <div>
                <p className="text-sm text-gray-500">Source</p>
                <p className="font-medium capitalize">{complaint.complaint_source.replace('_', ' ')}</p>
              </div>
              {complaint.product_service && (
                <div>
                  <p className="text-sm text-gray-500">Product/Service</p>
                  <p className="font-medium">{complaint.product_service}</p>
                </div>
              )}
            </div>
          </div>

          {/* Assignment & Priority */}
          <div className="bg-white shadow rounded-lg p-6">
            <h2 className="text-xl font-semibold mb-4">Assignment & Priority</h2>
            <div className="space-y-3">
              <div>
                <p className="text-sm text-gray-500">Priority</p>
                <p className="font-medium capitalize">{complaint.priority}</p>
              </div>
              {complaint.assigned_to && (
                <div>
                  <p className="text-sm text-gray-500">Assigned To</p>
                  <p className="font-medium">{complaint.assigned_to}</p>
                </div>
              )}
              {complaint.resolution_target_date && (
                <div>
                  <p className="text-sm text-gray-500">Target Resolution Date</p>
                  <p className={`font-medium ${isOverdue(complaint.resolution_target_date) && complaint.status !== 'resolved' && complaint.status !== 'closed' ? 'text-red-600' : 'text-green-600'}`}>
                    {formatDate(complaint.resolution_target_date)}
                    {isOverdue(complaint.resolution_target_date) && complaint.status !== 'resolved' && complaint.status !== 'closed' && ' ⚠ OVERDUE'}
                  </p>
                </div>
              )}
            </div>
          </div>

          {/* Timeline */}
          <div className="bg-white shadow rounded-lg p-6">
            <h2 className="text-xl font-semibold mb-4">Timeline</h2>
            <div className="space-y-4">
              <div>
                <p className="text-sm text-gray-500">Received</p>
                <p className="font-medium">{formatDate(complaint.received_date)}</p>
              </div>
              {complaint.resolution_date && (
                <div>
                  <p className="text-sm text-gray-500">Resolved</p>
                  <p className="font-medium">{formatDate(complaint.resolution_date)}</p>
                </div>
              )}
              <div className="pt-3 border-t">
                <p className="text-sm text-gray-500">Record Created</p>
                <p className="text-sm">{formatDateTime(complaint.created_at)}</p>
              </div>
              <div>
                <p className="text-sm text-gray-500">Last Updated</p>
                <p className="text-sm">{formatDateTime(complaint.updated_at)}</p>
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
                Add Resolution
              </button>
              <button className="w-full px-4 py-2 bg-purple-600 text-white rounded hover:bg-purple-700">
                Record Customer Feedback
              </button>
              <button className="w-full px-4 py-2 bg-orange-600 text-white rounded hover:bg-orange-700">
                Create NC
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
