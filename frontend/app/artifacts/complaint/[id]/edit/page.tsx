'use client';

import { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';

interface ComplaintFormData {
  complaint_title: string;
  complaint_description: string;
  customer_name: string;
  received_date: string;
  complaint_source: string;
  product_service: string;
  priority: string;
  assigned_to: string;
  resolution_target_date: string;
}

export default function ComplaintEditPage() {
  const params = useParams();
  const router = useRouter();
  const complaintId = params.id as string;

  const [formData, setFormData] = useState<ComplaintFormData>({
    complaint_title: '',
    complaint_description: '',
    customer_name: '',
    received_date: '',
    complaint_source: '',
    product_service: '',
    priority: 'medium',
    assigned_to: '',
    resolution_target_date: '',
  });

  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
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
        throw new Error('Failed to load Customer Complaint');
      }

      const data = await response.json();
      
      setFormData({
        complaint_title: data.complaint_title || '',
        complaint_description: data.complaint_description || '',
        customer_name: data.customer_name || '',
        received_date: data.received_date || '',
        complaint_source: data.complaint_source || '',
        product_service: data.product_service || '',
        priority: data.priority || 'medium',
        assigned_to: data.assigned_to || '',
        resolution_target_date: data.resolution_target_date || '',
      });
    } catch (err) {
      setError('Failed to load Customer Complaint');
      console.error('Error fetching Complaint:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    setError(null);

    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`http://localhost:8889/api/v1/artifacts/complaint/${complaintId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify(formData),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to update Customer Complaint');
      }

      router.push(`/artifacts/complaint/${complaintId}`);
    } catch (err: any) {
      setError(err.message || 'Failed to update Customer Complaint');
      console.error('Error updating Complaint:', err);
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-lg">Loading...</div>
      </div>
    );
  }

  if (error && !formData.complaint_title) {
    return (
      <div className="flex flex-col items-center justify-center min-h-screen">
        <div className="text-xl text-red-600 mb-4">{error}</div>
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
    <div className="p-6 max-w-4xl mx-auto">
      <div className="mb-6">
        <button
          onClick={() => router.push(`/artifacts/complaint/${complaintId}`)}
          className="text-blue-600 hover:text-blue-800 mb-4"
        >
          ← Back to Complaint Detail
        </button>
        <h1 className="text-3xl font-bold mb-2">Edit Customer Complaint</h1>
        <p className="text-gray-600">Update the information for this Customer Complaint</p>
      </div>

      {error && (
        <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
          {error}
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-6">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Complaint Title *
          </label>
          <input
            type="text"
            value={formData.complaint_title}
            onChange={(e) => setFormData({ ...formData, complaint_title: e.target.value })}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            required
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Complaint Description *
          </label>
          <textarea
            value={formData.complaint_description}
            onChange={(e) => setFormData({ ...formData, complaint_description: e.target.value })}
            rows={5}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            required
          />
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Customer Name *
            </label>
            <input
              type="text"
              value={formData.customer_name}
              onChange={(e) => setFormData({ ...formData, customer_name: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Received Date *
            </label>
            <input
              type="date"
              value={formData.received_date}
              onChange={(e) => setFormData({ ...formData, received_date: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              required
            />
          </div>
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Complaint Source
            </label>
            <input
              type="text"
              value={formData.complaint_source}
              onChange={(e) => setFormData({ ...formData, complaint_source: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              placeholder="e.g., Email, Phone, Website"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Product/Service
            </label>
            <input
              type="text"
              value={formData.product_service}
              onChange={(e) => setFormData({ ...formData, product_service: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            />
          </div>
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Priority *
            </label>
            <select
              value={formData.priority}
              onChange={(e) => setFormData({ ...formData, priority: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              required
            >
              <option value="low">LOW</option>
              <option value="medium">MEDIUM</option>
              <option value="high">HIGH</option>
              <option value="critical">CRITICAL</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Assigned To
            </label>
            <input
              type="text"
              value={formData.assigned_to}
              onChange={(e) => setFormData({ ...formData, assigned_to: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              placeholder="Person handling this complaint"
            />
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Resolution Target Date
          </label>
          <input
            type="date"
            value={formData.resolution_target_date}
            onChange={(e) => setFormData({ ...formData, resolution_target_date: e.target.value })}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
          />
        </div>

        <div className="flex gap-4 pt-4">
          <button
            type="submit"
            disabled={submitting}
            className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400"
          >
            {submitting ? 'Saving...' : 'Save Changes'}
          </button>
          <button
            type="button"
            onClick={() => router.push(`/artifacts/complaint/${complaintId}`)}
            className="px-6 py-2 bg-gray-300 text-gray-700 rounded-lg hover:bg-gray-400"
          >
            Cancel
          </button>
        </div>
      </form>
    </div>
  );
}
