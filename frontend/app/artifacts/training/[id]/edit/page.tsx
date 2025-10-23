'use client';

import { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';

interface TrainingFormData {
  employee_id: string;
  training_title: string;
  training_date: string;
  trainer_name: string;
  training_hours: string;
  training_type: string;
  competency_area: string;
  passed: boolean;
  score: string;
  certificate_number: string;
  expiry_date: string;
  notes: string;
}

export default function TrainingEditPage() {
  const params = useParams();
  const router = useRouter();
  const trainingId = params.id as string;

  const [formData, setFormData] = useState<TrainingFormData>({
    employee_id: '',
    training_title: '',
    training_date: '',
    trainer_name: '',
    training_hours: '',
    training_type: '',
    competency_area: '',
    passed: false,
    score: '',
    certificate_number: '',
    expiry_date: '',
    notes: '',
  });

  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchTrainingDetail();
  }, [trainingId]);

  const fetchTrainingDetail = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`http://localhost:8889/api/v1/artifacts/training/${trainingId}`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        throw new Error('Failed to load Training Record');
      }

      const data = await response.json();
      
      setFormData({
        employee_id: data.employee_id || '',
        training_title: data.training_title || '',
        training_date: data.training_date || '',
        trainer_name: data.trainer_name || '',
        training_hours: data.training_hours?.toString() || '',
        training_type: data.training_type || '',
        competency_area: data.competency_area || '',
        passed: data.passed || false,
        score: data.score?.toString() || '',
        certificate_number: data.certificate_number || '',
        expiry_date: data.expiry_date || '',
        notes: data.notes || '',
      });
    } catch (err) {
      setError('Failed to load Training Record');
      console.error('Error fetching Training:', err);
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
      const payload = {
        ...formData,
        training_hours: formData.training_hours ? parseFloat(formData.training_hours) : null,
        score: formData.score ? parseFloat(formData.score) : null,
      };

      const response = await fetch(`http://localhost:8889/api/v1/artifacts/training/${trainingId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to update Training Record');
      }

      router.push(`/artifacts/training/${trainingId}`);
    } catch (err: any) {
      setError(err.message || 'Failed to update Training Record');
      console.error('Error updating Training:', err);
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

  if (error && !formData.training_title) {
    return (
      <div className="flex flex-col items-center justify-center min-h-screen">
        <div className="text-xl text-red-600 mb-4">{error}</div>
        <button
          onClick={() => router.push('/artifacts/training')}
          className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
        >
          Back to Training Records
        </button>
      </div>
    );
  }

  return (
    <div className="p-6 max-w-4xl mx-auto">
      <div className="mb-6">
        <button
          onClick={() => router.push(`/artifacts/training/${trainingId}`)}
          className="text-blue-600 hover:text-blue-800 mb-4"
        >
          ← Back to Training Detail
        </button>
        <h1 className="text-3xl font-bold mb-2">Edit Training Record</h1>
        <p className="text-gray-600">Update the information for this Training Record</p>
      </div>

      {error && (
        <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
          {error}
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-6">
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Employee ID *
            </label>
            <input
              type="text"
              value={formData.employee_id}
              onChange={(e) => setFormData({ ...formData, employee_id: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Training Date *
            </label>
            <input
              type="date"
              value={formData.training_date}
              onChange={(e) => setFormData({ ...formData, training_date: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              required
            />
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Training Title *
          </label>
          <input
            type="text"
            value={formData.training_title}
            onChange={(e) => setFormData({ ...formData, training_title: e.target.value })}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            required
          />
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Trainer Name
            </label>
            <input
              type="text"
              value={formData.trainer_name}
              onChange={(e) => setFormData({ ...formData, trainer_name: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Training Hours
            </label>
            <input
              type="number"
              step="0.5"
              value={formData.training_hours}
              onChange={(e) => setFormData({ ...formData, training_hours: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            />
          </div>
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Training Type
            </label>
            <input
              type="text"
              value={formData.training_type}
              onChange={(e) => setFormData({ ...formData, training_type: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              placeholder="e.g., Online, Classroom, On-the-job"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Competency Area
            </label>
            <input
              type="text"
              value={formData.competency_area}
              onChange={(e) => setFormData({ ...formData, competency_area: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              placeholder="e.g., Quality Management, Safety"
            />
          </div>
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Passed
            </label>
            <select
              value={formData.passed ? 'true' : 'false'}
              onChange={(e) => setFormData({ ...formData, passed: e.target.value === 'true' })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            >
              <option value="false">No</option>
              <option value="true">Yes</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Score
            </label>
            <input
              type="number"
              step="0.1"
              value={formData.score}
              onChange={(e) => setFormData({ ...formData, score: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              placeholder="e.g., 85.5"
            />
          </div>
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Certificate Number
            </label>
            <input
              type="text"
              value={formData.certificate_number}
              onChange={(e) => setFormData({ ...formData, certificate_number: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Expiry Date
            </label>
            <input
              type="date"
              value={formData.expiry_date}
              onChange={(e) => setFormData({ ...formData, expiry_date: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            />
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Notes
          </label>
          <textarea
            value={formData.notes}
            onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
            rows={4}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            placeholder="Additional notes about the training"
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
            onClick={() => router.push(`/artifacts/training/${trainingId}`)}
            className="px-6 py-2 bg-gray-300 text-gray-700 rounded-lg hover:bg-gray-400"
          >
            Cancel
          </button>
        </div>
      </form>
    </div>
  );
}
