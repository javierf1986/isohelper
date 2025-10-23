'use client';

import { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';

interface ReviewDetail {
  id: string;
  review_number: string;
  review_date: string;
  attendees?: string;
  agenda?: string;
  minutes?: string;
  decisions?: string;
  action_items?: string;
  next_review_date?: string;
  created_at: string;
  updated_at: string;
}

export default function ReviewDetailPage() {
  const params = useParams();
  const router = useRouter();
  const reviewId = params.id as string;

  const [review, setReview] = useState<ReviewDetail | null>(null);
  const [loading, setLoading] = useState(true);
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
        if (response.status === 404) {
          setError('Management Review not found');
        } else {
          setError('Failed to load review');
        }
        setLoading(false);
        return;
      }

      const data = await response.json();
      setReview(data);
    } catch (err) {
      setError('Failed to connect to server');
      console.error('Error fetching review:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async () => {
    if (!window.confirm("Are you sure you want to delete this Management Review? This action cannot be undone.")) {
      return;
    }

    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`http://localhost:8889/api/v1/artifacts/management-review/${reviewId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        throw new Error('Failed to delete Management Review');
      }

      router.push('/artifacts/review');
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Failed to delete Management Review');
    }
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

  const extractQuarter = (reviewNumber: string) => {
    const match = reviewNumber.match(/Q(\d)/);
    return match ? `Q${match[1]}` : '';
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-lg">Loading Management Review...</div>
      </div>
    );
  }

  if (error || !review) {
    return (
      <div className="flex flex-col items-center justify-center min-h-screen">
        <div className="text-xl text-red-600 mb-4">{error || 'Management Review not found'}</div>
        <button
          onClick={() => router.push('/artifacts/review')}
          className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
        >
          Back to Management Reviews
        </button>
      </div>
    );
  }

  const quarter = extractQuarter(review.review_number);

  return (
    <div className="p-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="mb-6">
        <button
          onClick={() => router.push('/artifacts/review')}
          className="text-blue-600 hover:text-blue-800 mb-4 flex items-center"
        >
          ← Back to Management Reviews
        </button>
        
        <div className="flex justify-between items-start">
          <div>
            <h1 className="text-3xl font-bold mb-2">{review.review_number}</h1>
            <div className="flex gap-3 items-center">
              {quarter && (
                <span className="px-3 py-1 rounded-full text-sm font-medium bg-indigo-100 text-indigo-800">
                  {quarter}
                </span>
              )}
              <span className="text-gray-600">{formatDate(review.review_date)}</span>
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
          {/* Attendees */}
          {review.attendees && (
            <div className="bg-white shadow rounded-lg p-6">
              <h2 className="text-xl font-semibold mb-3">Attendees</h2>
              <p className="text-gray-700 whitespace-pre-wrap">{review.attendees}</p>
            </div>
          )}

          {/* Agenda */}
          {review.agenda && (
            <div className="bg-white shadow rounded-lg p-6">
              <h2 className="text-xl font-semibold mb-3">Agenda</h2>
              <p className="text-gray-700 whitespace-pre-wrap">{review.agenda}</p>
            </div>
          )}

          {/* Minutes */}
          {review.minutes && (
            <div className="bg-white shadow rounded-lg p-6">
              <h2 className="text-xl font-semibold mb-3">Meeting Minutes</h2>
              <p className="text-gray-700 whitespace-pre-wrap">{review.minutes}</p>
            </div>
          )}

          {/* Decisions */}
          {review.decisions && (
            <div className="bg-white shadow rounded-lg p-6">
              <h2 className="text-xl font-semibold mb-3">Key Decisions</h2>
              <p className="text-gray-700 whitespace-pre-wrap">{review.decisions}</p>
            </div>
          )}

          {/* Action Items */}
          {review.action_items && (
            <div className="bg-white shadow rounded-lg p-6 border-l-4 border-orange-500">
              <h2 className="text-xl font-semibold mb-3 flex items-center gap-2">
                <span className="text-orange-600">⚠</span> Action Items
              </h2>
              <p className="text-gray-700 whitespace-pre-wrap">{review.action_items}</p>
            </div>
          )}

          {/* ISO 9001 Requirements Info */}
          <div className="bg-indigo-50 border border-indigo-200 rounded-lg p-6">
            <h3 className="font-semibold text-indigo-900 mb-3">ISO 9001:2015 - Clause 9.3: Management Review</h3>
            <div className="space-y-2 text-sm text-indigo-800">
              <p><strong>Inputs:</strong> Status of previous actions, changes in external/internal issues, performance and conformity information, adequacy of resources, effectiveness of risk/opportunity actions</p>
              <p><strong>Outputs:</strong> Opportunities for improvement, need for QMS changes, resource needs</p>
              <p><strong>Frequency:</strong> Planned intervals (typically quarterly)</p>
            </div>
          </div>
        </div>

        {/* Right Column - Info & Timeline */}
        <div className="space-y-6">
          {/* Key Information */}
          <div className="bg-white shadow rounded-lg p-6">
            <h2 className="text-xl font-semibold mb-4">Key Information</h2>
            <div className="space-y-3">
              <div>
                <p className="text-sm text-gray-500">Review Date</p>
                <p className="font-medium">{formatDate(review.review_date)}</p>
              </div>
              {quarter && (
                <div>
                  <p className="text-sm text-gray-500">Quarter</p>
                  <p className="font-medium">{quarter}</p>
                </div>
              )}
              {review.next_review_date && (
                <div>
                  <p className="text-sm text-gray-500">Next Review Date</p>
                  <p className="font-medium">{formatDate(review.next_review_date)}</p>
                </div>
              )}
            </div>
          </div>

          {/* Timeline */}
          <div className="bg-white shadow rounded-lg p-6">
            <h2 className="text-xl font-semibold mb-4">Timeline</h2>
            <div className="space-y-4">
              <div>
                <p className="text-sm text-gray-500">Created</p>
                <p className="text-sm">{formatDateTime(review.created_at)}</p>
              </div>
              <div>
                <p className="text-sm text-gray-500">Last Updated</p>
                <p className="text-sm">{formatDateTime(review.updated_at)}</p>
              </div>
            </div>
          </div>

          {/* Actions */}
          <div className="bg-white shadow rounded-lg p-6">
            <h2 className="text-xl font-semibold mb-4">Actions</h2>
            <div className="space-y-3">
              <button className="w-full px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700">
                Add Minutes
              </button>
              <button className="w-full px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700">
                Record Decisions
              </button>
              <button className="w-full px-4 py-2 bg-orange-600 text-white rounded hover:bg-orange-700">
                Add Action Items
              </button>
              <button className="w-full px-4 py-2 bg-purple-600 text-white rounded hover:bg-purple-700">
                Schedule Next Review
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
