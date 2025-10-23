'use client';

import { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';

interface ReviewFormData {
  review_date: string;
  attendees: string;
  agenda: string;
  minutes: string;
  decisions: string;
  action_items: string;
  next_review_date: string;
}

export default function ReviewEditPage() {
  const params = useParams();
  const router = useRouter();
  const reviewId = params.id as string;

  const [formData, setFormData] = useState<ReviewFormData>({
    review_date: '',
    attendees: '',
    agenda: '',
    minutes: '',
    decisions: '',
    action_items: '',
    next_review_date: '',
  });

  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchReviewDetail();
  }, [reviewId]);

  const fetchReviewDetail = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`http://localhost:8889/api/v1/artifacts/management-review/${reviewId}`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        throw new Error('Failed to load Management Review');
      }

      const data = await response.json();
      
      setFormData({
        review_date: data.review_date || '',
        attendees: data.attendees || '',
        agenda: data.agenda || '',
        minutes: data.minutes || '',
        decisions: data.decisions || '',
        action_items: data.action_items || '',
        next_review_date: data.next_review_date || '',
      });
    } catch (err) {
      setError('Failed to load Management Review');
      console.error('Error fetching Review:', err);
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
      const response = await fetch(`http://localhost:8889/api/v1/artifacts/management-review/${reviewId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify(formData),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to update Management Review');
      }

      router.push(`/artifacts/management-review/${reviewId}`);
    } catch (err: any) {
      setError(err.message || 'Failed to update Management Review');
      console.error('Error updating Review:', err);
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

  if (error && !formData.review_date) {
    return (
      <div className="flex flex-col items-center justify-center min-h-screen">
        <div className="text-xl text-red-600 mb-4">{error}</div>
        <button
          onClick={() => router.push('/artifacts/management-review')}
          className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
        >
          Back to Management Reviews
        </button>
      </div>
    );
  }

  return (
    <div className="p-6 max-w-4xl mx-auto">
      <div className="mb-6">
        <button
          onClick={() => router.push(`/artifacts/management-review/${reviewId}`)}
          className="text-blue-600 hover:text-blue-800 mb-4"
        >
          ← Back to Review Detail
        </button>
        <h1 className="text-3xl font-bold mb-2">Edit Management Review</h1>
        <p className="text-gray-600">Update the information for this Management Review</p>
      </div>

      {error && (
        <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
          {error}
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-6">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Review Date *
          </label>
          <input
            type="date"
            value={formData.review_date}
            onChange={(e) => setFormData({ ...formData, review_date: e.target.value })}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            required
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Attendees
          </label>
          <textarea
            value={formData.attendees}
            onChange={(e) => setFormData({ ...formData, attendees: e.target.value })}
            rows={3}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            placeholder="List of attendees"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Agenda
          </label>
          <textarea
            value={formData.agenda}
            onChange={(e) => setFormData({ ...formData, agenda: e.target.value })}
            rows={4}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            placeholder="Review agenda items"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Minutes
          </label>
          <textarea
            value={formData.minutes}
            onChange={(e) => setFormData({ ...formData, minutes: e.target.value })}
            rows={6}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            placeholder="Meeting minutes and discussion summary"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Decisions
          </label>
          <textarea
            value={formData.decisions}
            onChange={(e) => setFormData({ ...formData, decisions: e.target.value })}
            rows={4}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            placeholder="Key decisions made during the review"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Action Items
          </label>
          <textarea
            value={formData.action_items}
            onChange={(e) => setFormData({ ...formData, action_items: e.target.value })}
            rows={4}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            placeholder="Action items and follow-ups"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Next Review Date
          </label>
          <input
            type="date"
            value={formData.next_review_date}
            onChange={(e) => setFormData({ ...formData, next_review_date: e.target.value })}
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
            onClick={() => router.push(`/artifacts/management-review/${reviewId}`)}
            className="px-6 py-2 bg-gray-300 text-gray-700 rounded-lg hover:bg-gray-400"
          >
            Cancel
          </button>
        </div>
      </form>
    </div>
  );
}
