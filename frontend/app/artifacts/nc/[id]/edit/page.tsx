'use client';

import { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';

interface NCFormData {
  title: string;
  description: string;
  severity: string;
  detected_date: string;
  category: string;
  detected_location: string;
  iso_standard_id: string;
  iso_clause_number: string;
  immediate_actions: string;
  target_closure_date: string;
}

export default function NCEditPage() {
  const params = useParams();
  const router = useRouter();
  const ncId = params.id as string;

  const [formData, setFormData] = useState<NCFormData>({
    title: '',
    description: '',
    severity: 'minor',
    detected_date: '',
    category: '',
    detected_location: '',
    iso_standard_id: '',
    iso_clause_number: '',
    immediate_actions: '',
    target_closure_date: '',
  });

  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchNCDetail();
  }, [ncId]);

  const fetchNCDetail = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`http://localhost:8889/api/v1/artifacts/nc/${ncId}`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        throw new Error('Failed to load NC');
      }

      const data = await response.json();
      
      // Populate form with existing data
      setFormData({
        title: data.title || '',
        description: data.description || '',
        severity: data.severity || 'minor',
        detected_date: data.detected_date || '',
        category: data.category || '',
        detected_location: data.detected_location || '',
        iso_standard_id: data.iso_standard_id || '',
        iso_clause_number: data.iso_clause_number || '',
        immediate_actions: data.immediate_actions || '',
        target_closure_date: data.target_closure_date || '',
      });
    } catch (err) {
      setError('Failed to load Non-Conformity');
      console.error('Error fetching NC:', err);
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
      const response = await fetch(`http://localhost:8889/api/v1/artifacts/nc/${ncId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({
          title: formData.title || null,
          description: formData.description || null,
          severity: formData.severity || null,
          detected_date: formData.detected_date || null,
          category: formData.category || null,
          detected_location: formData.detected_location || null,
          iso_standard_id: formData.iso_standard_id || null,
          iso_clause_number: formData.iso_clause_number || null,
          immediate_actions: formData.immediate_actions || null,
          target_closure_date: formData.target_closure_date || null,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to update NC');
      }

      // Redirect to detail page
      router.push(`/artifacts/nc/${ncId}`);
    } catch (err: any) {
      setError(err.message || 'Failed to update Non-Conformity');
      console.error('Error updating NC:', err);
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
          onClick={() => router.push('/artifacts/nc')}
          className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
        >
          Back to Non-Conformities
        </button>
      </div>
    );
  }

  return (
    <div className="p-6 max-w-4xl mx-auto">
      <div className="mb-6">
        <button
          onClick={() => router.push(`/artifacts/nc/${ncId}`)}
          className="text-blue-600 hover:text-blue-800 mb-4"
        >
          ← Back to NC Detail
        </button>
        <h1 className="text-3xl font-bold mb-2">Edit Non-Conformity</h1>
        <p className="text-gray-600">Update the information for this Non-Conformity</p>
      </div>

      {error && (
        <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
          {error}
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Title */}
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

        {/* Description */}
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

        {/* Severity */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Severity *
          </label>
          <select
            value={formData.severity}
            onChange={(e) => setFormData({ ...formData, severity: e.target.value })}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            required
          >
            <option value="minor">MINOR</option>
            <option value="major">MAJOR</option>
            <option value="critical">CRITICAL</option>
          </select>
        </div>

        {/* Detected Date */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Detected Date *
          </label>
          <input
            type="date"
            value={formData.detected_date}
            onChange={(e) => setFormData({ ...formData, detected_date: e.target.value })}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            required
          />
        </div>

        {/* Category */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Category
          </label>
          <input
            type="text"
            value={formData.category}
            onChange={(e) => setFormData({ ...formData, category: e.target.value })}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            placeholder="e.g., Process, Product, Documentation"
          />
        </div>

        {/* Detected Location */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Detected Location
          </label>
          <input
            type="text"
            value={formData.detected_location}
            onChange={(e) => setFormData({ ...formData, detected_location: e.target.value })}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            placeholder="e.g., Production Line 2, Quality Lab"
          />
        </div>

        {/* ISO Standard ID */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            ISO Standard ID
          </label>
          <input
            type="text"
            value={formData.iso_standard_id}
            onChange={(e) => setFormData({ ...formData, iso_standard_id: e.target.value })}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            placeholder="e.g., ISO9001"
          />
        </div>

        {/* ISO Clause Number */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            ISO Clause Number
          </label>
          <input
            type="text"
            value={formData.iso_clause_number}
            onChange={(e) => setFormData({ ...formData, iso_clause_number: e.target.value })}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            placeholder="e.g., 8.5.1, 4.4.2"
          />
        </div>

        {/* Immediate Actions */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Immediate Actions Taken
          </label>
          <textarea
            value={formData.immediate_actions}
            onChange={(e) => setFormData({ ...formData, immediate_actions: e.target.value })}
            rows={3}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            placeholder="Describe any immediate actions taken to address this NC"
          />
        </div>

        {/* Target Closure Date */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Target Closure Date
          </label>
          <input
            type="date"
            value={formData.target_closure_date}
            onChange={(e) => setFormData({ ...formData, target_closure_date: e.target.value })}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
          />
        </div>

        {/* Form Actions */}
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
            onClick={() => router.push(`/artifacts/nc/${ncId}`)}
            className="px-6 py-2 bg-gray-300 text-gray-700 rounded-lg hover:bg-gray-400"
          >
            Cancel
          </button>
        </div>
      </form>
    </div>
  );
}
