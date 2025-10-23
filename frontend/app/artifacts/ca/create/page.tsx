'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';

export default function CreateCAPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [formData, setFormData] = useState({
    title: '',
    description: '',
    action_plan: '',
    assigned_to: '',
    planned_start_date: new Date().toISOString().split('T')[0],
    planned_completion_date: '',
    priority: 'medium',
    nc_id: '',
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const token = localStorage.getItem('access_token');
      
      // Prepare payload
      const payload = {
        ...formData,
        nc_id: formData.nc_id || null,
      };

      const response = await fetch('http://localhost:8889/api/v1/artifacts/ca', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.detail || 'Failed to create CA');
      }

      const result = await response.json();
      router.push(`/artifacts/ca/${result.id}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  return (
    <div className="container mx-auto px-4 py-8 max-w-3xl">
      {/* Header */}
      <div className="mb-8">
        <button
          onClick={() => router.back()}
          className="text-blue-600 hover:text-blue-800 mb-4 inline-flex items-center"
        >
          ← Back
        </button>
        <h1 className="text-3xl font-bold text-gray-900">Create Corrective Action</h1>
        <p className="text-gray-600 mt-2">Define actions to eliminate the cause of non-conformities</p>
      </div>

      {/* Error Message */}
      {error && (
        <div className="mb-6 bg-red-50 border border-red-300 text-red-800 px-4 py-3 rounded">
          {error}
        </div>
      )}

      {/* Form */}
      <form onSubmit={handleSubmit} className="bg-white rounded-lg shadow p-6 space-y-6">
        {/* Title */}
        <div>
          <label htmlFor="title" className="block text-sm font-medium text-gray-700 mb-2">
            Title <span className="text-red-500">*</span>
          </label>
          <input
            type="text"
            id="title"
            name="title"
            required
            value={formData.title}
            onChange={handleChange}
            className="w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
            placeholder="Brief title for the corrective action"
          />
        </div>

        {/* Description */}
        <div>
          <label htmlFor="description" className="block text-sm font-medium text-gray-700 mb-2">
            Description <span className="text-red-500">*</span>
          </label>
          <textarea
            id="description"
            name="description"
            required
            rows={3}
            value={formData.description}
            onChange={handleChange}
            className="w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
            placeholder="Describe what needs to be corrected..."
          />
        </div>

        {/* Action Plan */}
        <div>
          <label htmlFor="action_plan" className="block text-sm font-medium text-gray-700 mb-2">
            Action Plan <span className="text-red-500">*</span>
          </label>
          <textarea
            id="action_plan"
            name="action_plan"
            required
            rows={4}
            value={formData.action_plan}
            onChange={handleChange}
            className="w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
            placeholder="Detail the steps to implement this corrective action..."
          />
          <p className="mt-1 text-sm text-gray-500">
            Include specific steps, resources needed, and success criteria
          </p>
        </div>

        {/* Priority and Assigned To */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label htmlFor="priority" className="block text-sm font-medium text-gray-700 mb-2">
              Priority <span className="text-red-500">*</span>
            </label>
            <select
              id="priority"
              name="priority"
              required
              value={formData.priority}
              onChange={handleChange}
              className="w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
            >
              <option value="low">Low</option>
              <option value="medium">Medium</option>
              <option value="high">High</option>
              <option value="urgent">Urgent</option>
            </select>
          </div>

          <div>
            <label htmlFor="assigned_to" className="block text-sm font-medium text-gray-700 mb-2">
              Assigned To (User ID) <span className="text-red-500">*</span>
            </label>
            <input
              type="text"
              id="assigned_to"
              name="assigned_to"
              required
              value={formData.assigned_to}
              onChange={handleChange}
              className="w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
              placeholder="Enter user ID"
            />
            <p className="mt-1 text-sm text-gray-500">Who will implement this action</p>
          </div>
        </div>

        {/* Date Range */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label htmlFor="planned_start_date" className="block text-sm font-medium text-gray-700 mb-2">
              Planned Start Date <span className="text-red-500">*</span>
            </label>
            <input
              type="date"
              id="planned_start_date"
              name="planned_start_date"
              required
              value={formData.planned_start_date}
              onChange={handleChange}
              className="w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
            />
          </div>

          <div>
            <label htmlFor="planned_completion_date" className="block text-sm font-medium text-gray-700 mb-2">
              Planned Completion Date <span className="text-red-500">*</span>
            </label>
            <input
              type="date"
              id="planned_completion_date"
              name="planned_completion_date"
              required
              value={formData.planned_completion_date}
              onChange={handleChange}
              className="w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
            />
          </div>
        </div>

        {/* Link to NC (Optional) */}
        <div>
          <label htmlFor="nc_id" className="block text-sm font-medium text-gray-700 mb-2">
            Link to Non-Conformity (Optional)
          </label>
          <input
            type="text"
            id="nc_id"
            name="nc_id"
            value={formData.nc_id}
            onChange={handleChange}
            className="w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
            placeholder="Enter NC ID if this CA addresses a specific NC"
          />
        </div>

        {/* Priority Info */}
        <div className="bg-orange-50 border border-orange-200 rounded-md p-4">
          <h3 className="text-sm font-medium text-orange-900 mb-2">Priority Guidelines</h3>
          <ul className="text-sm text-orange-800 space-y-1">
            <li><strong>Low:</strong> Can be addressed in routine schedule</li>
            <li><strong>Medium:</strong> Should be completed within planned timeline</li>
            <li><strong>High:</strong> Requires priority attention and resources</li>
            <li><strong>Urgent:</strong> Immediate action required, top priority</li>
          </ul>
        </div>

        {/* Actions */}
        <div className="flex gap-3 pt-4">
          <button
            type="submit"
            disabled={loading}
            className="flex-1 bg-blue-600 text-white px-6 py-3 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed font-medium"
          >
            {loading ? 'Creating...' : 'Create Corrective Action'}
          </button>
          <button
            type="button"
            onClick={() => router.back()}
            className="px-6 py-3 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
          >
            Cancel
          </button>
        </div>
      </form>
    </div>
  );
}
