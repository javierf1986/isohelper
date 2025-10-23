'use client';

import { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';

interface AuditFormData {
  title: string;
  audit_type: string;
  scope_description: string;
  planned_date: string;
  iso_standard_id: string;
}

export default function AuditEditPage() {
  const params = useParams();
  const router = useRouter();
  const auditId = params.id as string;

  const [formData, setFormData] = useState<AuditFormData>({
    title: '',
    audit_type: 'internal',
    scope_description: '',
    planned_date: '',
    iso_standard_id: '',
  });

  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchAuditDetail();
  }, [auditId]);

  const fetchAuditDetail = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`http://localhost:8889/api/v1/artifacts/audit/${auditId}`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        throw new Error('Failed to load Audit');
      }

      const data = await response.json();
      
      setFormData({
        title: data.title || '',
        audit_type: data.audit_type || 'internal',
        scope_description: data.scope_description || '',
        planned_date: data.planned_date || '',
        iso_standard_id: data.iso_standard_id || '',
      });
    } catch (err) {
      setError('Failed to load Audit');
      console.error('Error fetching Audit:', err);
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
      const response = await fetch(`http://localhost:8889/api/v1/artifacts/audit/${auditId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify(formData),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to update Audit');
      }

      router.push(`/artifacts/audit/${auditId}`);
    } catch (err: any) {
      setError(err.message || 'Failed to update Audit');
      console.error('Error updating Audit:', err);
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
          onClick={() => router.push('/artifacts/audit')}
          className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
        >
          Back to Audits
        </button>
      </div>
    );
  }

  return (
    <div className="p-6 max-w-4xl mx-auto">
      <div className="mb-6">
        <button
          onClick={() => router.push(`/artifacts/audit/${auditId}`)}
          className="text-blue-600 hover:text-blue-800 mb-4"
        >
          ← Back to Audit Detail
        </button>
        <h1 className="text-3xl font-bold mb-2">Edit Internal Audit</h1>
        <p className="text-gray-600">Update the information for this Internal Audit</p>
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
            Audit Type *
          </label>
          <select
            value={formData.audit_type}
            onChange={(e) => setFormData({ ...formData, audit_type: e.target.value })}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            required
          >
            <option value="internal">INTERNAL</option>
            <option value="external">EXTERNAL</option>
            <option value="surveillance">SURVEILLANCE</option>
            <option value="certification">CERTIFICATION</option>
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Scope Description *
          </label>
          <textarea
            value={formData.scope_description}
            onChange={(e) => setFormData({ ...formData, scope_description: e.target.value })}
            rows={4}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            required
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Planned Date *
          </label>
          <input
            type="date"
            value={formData.planned_date}
            onChange={(e) => setFormData({ ...formData, planned_date: e.target.value })}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            required
          />
        </div>

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
            onClick={() => router.push(`/artifacts/audit/${auditId}`)}
            className="px-6 py-2 bg-gray-300 text-gray-700 rounded-lg hover:bg-gray-400"
          >
            Cancel
          </button>
        </div>
      </form>
    </div>
  );
}
