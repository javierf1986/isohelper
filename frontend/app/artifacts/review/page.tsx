"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

interface ManagementReview {
  id: string;
  review_number: string;
  review_date: string;
  attendees: string | null;
  agenda: string | null;
  minutes: string | null;
  decisions: string | null;
  action_items: string | null;
  next_review_date: string | null;
  created_by: string;
  created_at: string;
}

export default function ManagementReviewsPage() {
  const router = useRouter();
  const [reviews, setReviews] = useState<ManagementReview[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [yearFilter, setYearFilter] = useState<string>("all");

  useEffect(() => {
    fetchReviews();
  }, [yearFilter]);

  const fetchReviews = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem("access_token");
      
      let url = "http://localhost:8889/api/v1/artifacts/management-review";
      const params = new URLSearchParams();
      
      if (yearFilter !== "all") {
        params.append("year", yearFilter);
      }
      
      if (params.toString()) {
        url += `?${params.toString()}`;
      }

      const response = await fetch(url, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        throw new Error("Failed to fetch management reviews");
      }

      const data = await response.json();
      setReviews(data);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "An error occurred");
    } finally {
      setLoading(false);
    }
  };

  const getYearOptions = () => {
    const currentYear = new Date().getFullYear();
    const years = [];
    for (let i = 0; i < 5; i++) {
      years.push(currentYear - i);
    }
    return years;
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString();
  };

  const getQuarterFromReviewNumber = (reviewNumber: string) => {
    const match = reviewNumber.match(/Q(\d)/);
    return match ? `Q${match[1]}` : "";
  };

  const parseActionItems = (actionItemsStr: string | null): string[] => {
    if (!actionItemsStr) return [];
    try {
      const parsed = JSON.parse(actionItemsStr);
      return Array.isArray(parsed) ? parsed : [];
    } catch {
      return [];
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center min-h-screen">
        <div className="text-lg">Loading management reviews...</div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold">Management Reviews</h1>
        <button
          onClick={() => router.push("/artifacts/review/create")}
          className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-lg transition"
        >
          Schedule Review
        </button>
      </div>

      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
          {error}
        </div>
      )}

      {/* Statistics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        <div className="bg-white p-4 rounded-lg shadow">
          <div className="text-gray-600 text-sm">Total Reviews</div>
          <div className="text-2xl font-bold">{reviews.length}</div>
        </div>
        <div className="bg-white p-4 rounded-lg shadow">
          <div className="text-gray-600 text-sm">This Year</div>
          <div className="text-2xl font-bold">
            {reviews.filter(r => new Date(r.review_date).getFullYear() === new Date().getFullYear()).length}
          </div>
        </div>
        <div className="bg-white p-4 rounded-lg shadow">
          <div className="text-gray-600 text-sm">With Action Items</div>
          <div className="text-2xl font-bold">
            {reviews.filter(r => parseActionItems(r.action_items).length > 0).length}
          </div>
        </div>
        <div className="bg-white p-4 rounded-lg shadow">
          <div className="text-gray-600 text-sm">Upcoming</div>
          <div className="text-2xl font-bold">
            {reviews.filter(r => r.next_review_date && new Date(r.next_review_date) > new Date()).length}
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="bg-white p-4 rounded-lg shadow mb-6">
        <div className="flex gap-4">
          <div>
            <label className="block text-sm font-medium mb-1">Year</label>
            <select
              value={yearFilter}
              onChange={(e) => setYearFilter(e.target.value)}
              className="border rounded px-3 py-2"
            >
              <option value="all">All Years</option>
              {getYearOptions().map(year => (
                <option key={year} value={year}>{year}</option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {/* Reviews List */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                Review Number
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                Quarter
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                Review Date
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                Attendees
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                Action Items
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                Next Review
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                Actions
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {reviews.length === 0 ? (
              <tr>
                <td colSpan={7} className="px-6 py-4 text-center text-gray-500">
                  No management reviews found. Schedule your first review!
                </td>
              </tr>
            ) : (
              reviews.map((review) => {
                const actionItems = parseActionItems(review.action_items);
                return (
                  <tr key={review.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap font-medium">
                      {review.review_number}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className="inline-flex px-2 py-1 text-xs font-semibold rounded-full bg-indigo-100 text-indigo-800">
                        {getQuarterFromReviewNumber(review.review_number)}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      {formatDate(review.review_date)}
                    </td>
                    <td className="px-6 py-4">
                      <div className="text-sm text-gray-900 max-w-xs truncate">
                        {review.attendees || "Not specified"}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      {actionItems.length > 0 ? (
                        <span className="inline-flex px-2 py-1 text-xs font-semibold rounded-full bg-orange-100 text-orange-800">
                          {actionItems.length} items
                        </span>
                      ) : (
                        <span className="text-gray-400 text-sm">None</span>
                      )}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      {review.next_review_date ? (
                        <span className={`text-sm ${
                          new Date(review.next_review_date) < new Date()
                            ? "text-red-600 font-semibold"
                            : "text-gray-700"
                        }`}>
                          {formatDate(review.next_review_date)}
                        </span>
                      ) : (
                        <span className="text-gray-400 text-sm">Not scheduled</span>
                      )}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm">
                      <button
                        onClick={() => router.push(`/artifacts/review/${review.id}`)}
                        className="text-blue-600 hover:text-blue-800 mr-3"
                      >
                        View
                      </button>
                      <button
                        onClick={() => router.push(`/artifacts/review/${review.id}/edit`)}
                        className="text-green-600 hover:text-green-800"
                      >
                        Edit
                      </button>
                    </td>
                  </tr>
                );
              })
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
