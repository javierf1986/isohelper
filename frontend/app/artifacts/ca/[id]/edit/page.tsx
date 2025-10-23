'use client';

import { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';

interface CAFormData {
  title: string;
  description: string;
  action_plan: string;
  assigned_to: string;
  planned_start_date: string;
  planned_completion_date: string;
  nc_id: string;
  priority: string;
}

export default function CAEditPage() {
  const params = useParams();
  const router = useRouter();
  const caId = params.id as string;

  const [formData, setFormData] = useState<CAFormData>({
    title: '',
    description: '',
    action_plan: '',
    assigned_to: '',
    planned_start_date: '',
    planned_completion_date: '',
    nc_id: '',
    priority: 'medium',
  });

  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
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
        throw new Error('Failed to load Corrective Action');
      }

      const data = await response.json();
      
      setFormData({
        title: data.title || '',
        description: data.description || '',
        action_plan: data.action_plan || '',
        assigned_to: data.assigned_to || '',
        planned_start_date: data.planned_start_date || '',
        planned_completion_date: data.planned_completion_date || '',
        nc_id: data.nc_id || '',
        priority: data.priority || 'medium',
      });
    } catch (err) {
      setError('Failed to load Corrective Action');
      console.error('Error fetching CA:', err);
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
      const response = await fetch(`http://localhost:8889/api/v1/artifacts/ca/${caId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify(formData),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to update Corrective Action');
      }

      router.push(`/artifacts/ca/${caId}`);
    } catch (err: any) {
      setError(err.message || 'Failed to update Corrective Action');
      console.error('Error updating CA:', err);
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

  if (error && !formData.title) {
    return (
      <div className="flex flex-col items-center justify-center min-h-screen">
        <div className="text-xl text-red-600 mb-4">{error}</div>
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
    <div className="p-6 max-w-4xl mx-auto">
      <div className="mb-6">
        <button
          onClick={() => router.push(`/artifacts/ca/${caId}`)}
          className="text-blue-600 hover:text-blue-800 mb-4"
        >
          ← Back to CA Detail
        </button>
        <h1 className="text-3xl font-bold mb-2">Edit Corrective Action</h1>
        <p className="text-gray-600">Update the information for this Corrective Action</p>
      </div>

      {error && (
        <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
          {error}
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-6">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Title *
          </label>
          <input
            type="text"
            value={formData.title}
            onChange={(e) => setFormData({ ...formData, title: e.target.value })}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            required
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Description *
          </label>
          <textarea
            value={formData.description}
            onChange={(e) => setFormData({ ...formData, description: e.target.value })}
            rows={4}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            required
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Action Plan *
          </label>
          <textarea
            value={formData.action_plan}
            onChange={(e) => setFormData({ ...formData, action_plan: e.target.value })}
            rows={4}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            required
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Assigned To *
          </label>
          <input
            type="text"
            value={formData.assigned_to}
            onChange={(e) => setFormData({ ...formData, assigned_to: e.target.value })}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            required
          />
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Planned Start Date *
            </label>
            <input
              type="date"
              value={formData.planned_start_date}
              onChange={(e) => setFormData({ ...formData, planned_start_date: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Planned Completion Date *
            </label>
            <input
              type="date"
              value={formData.planned_completion_date}
              onChange={(e) => setFormData({ ...formData, planned_completion_date: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              required
            />
          </div>
        </div>

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
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Related NC ID
          </label>
          <input
            type="text"
            value={formData.nc_id}
            onChange={(e) => setFormData({ ...formData, nc_id: e.target.value })}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            placeholder="Optional: Link to a Non-Conformity"
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
            onClick={() => router.push(`/artifacts/ca/${caId}`)}
            className="px-6 py-2 bg-gray-300 text-gray-700 rounded-lg hover:bg-gray-400"
          >
            Cancel
          </button>
        </div>
      </form>
    </div>
  );
}
