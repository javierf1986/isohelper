"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";

export default function CreateManagementReviewPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [formData, setFormData] = useState({
    review_date: "",
    attendees: "",
    agenda: "",
    minutes: "",
    decisions: "",
    action_items: "",
    next_review_date: "",
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const token = localStorage.getItem("access_token");
      
      // Prepare data, removing empty optional fields
      const submitData: any = {
        review_date: formData.review_date,
      };
      
      if (formData.attendees) submitData.attendees = formData.attendees;
      if (formData.agenda) submitData.agenda = formData.agenda;
      if (formData.minutes) submitData.minutes = formData.minutes;
      if (formData.decisions) submitData.decisions = formData.decisions;
      if (formData.action_items) submitData.action_items = formData.action_items;
      if (formData.next_review_date) submitData.next_review_date = formData.next_review_date;

      const response = await fetch("http://localhost:8889/api/v1/artifacts/management-review", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(submitData),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Failed to create management review");
      }

      const data = await response.json();
      router.push(`/artifacts/review/${data.id}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "An error occurred");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="max-w-4xl mx-auto">
        <div className="mb-6">
          <button
            onClick={() => router.back()}
            className="text-blue-600 hover:text-blue-800 mb-4"
          >
            ← Back
          </button>
          <h1 className="text-3xl font-bold">Schedule Management Review</h1>
          <p className="text-gray-600 mt-2">
            Document a management review meeting to evaluate QMS effectiveness
          </p>
        </div>

        {error && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="bg-white rounded-lg shadow p-6 space-y-4">
            <h2 className="text-xl font-semibold mb-4">Review Details</h2>

            {/* Review Date */}
            <div>
              <label className="block text-sm font-medium mb-1">
                Review Date <span className="text-red-500">*</span>
              </label>
              <input
                type="date"
                required
                value={formData.review_date}
                onChange={(e) => setFormData({ ...formData, review_date: e.target.value })}
                className="w-full border rounded px-3 py-2"
              />
            </div>

            {/* Attendees */}
            <div>
              <label className="block text-sm font-medium mb-1">
                Attendees
              </label>
              <textarea
                value={formData.attendees}
                onChange={(e) => setFormData({ ...formData, attendees: e.target.value })}
                className="w-full border rounded px-3 py-2"
                rows={3}
                placeholder="List attendees (e.g., CEO, Quality Manager, Operations Director...)"
              />
            </div>

            {/* Agenda */}
            <div>
              <label className="block text-sm font-medium mb-1">
                Agenda
              </label>
              <textarea
                value={formData.agenda}
                onChange={(e) => setFormData({ ...formData, agenda: e.target.value })}
                className="w-full border rounded px-3 py-2"
                rows={4}
                placeholder="Review agenda items (e.g., NC review, CA effectiveness, audit results, customer feedback...)"
              />
              <p className="text-sm text-gray-500 mt-1">
                List topics to be discussed during the review
              </p>
            </div>

            {/* Minutes */}
            <div>
              <label className="block text-sm font-medium mb-1">
                Meeting Minutes
              </label>
              <textarea
                value={formData.minutes}
                onChange={(e) => setFormData({ ...formData, minutes: e.target.value })}
                className="w-full border rounded px-3 py-2"
                rows={6}
                placeholder="Document meeting discussions, findings, and key points..."
              />
              <p className="text-sm text-gray-500 mt-1">
                Comprehensive notes from the management review meeting
              </p>
            </div>

            {/* Decisions */}
            <div>
              <label className="block text-sm font-medium mb-1">
                Decisions Made
              </label>
              <textarea
                value={formData.decisions}
                onChange={(e) => setFormData({ ...formData, decisions: e.target.value })}
                className="w-full border rounded px-3 py-2"
                rows={4}
                placeholder="Document key decisions (e.g., approve new procedures, allocate resources...)"
              />
              <p className="text-sm text-gray-500 mt-1">
                Record management decisions for QMS improvements
              </p>
            </div>

            {/* Action Items */}
            <div>
              <label className="block text-sm font-medium mb-1">
                Action Items
              </label>
              <textarea
                value={formData.action_items}
                onChange={(e) => setFormData({ ...formData, action_items: e.target.value })}
                className="w-full border rounded px-3 py-2"
                rows={5}
                placeholder="List action items with owners and due dates..."
              />
              <p className="text-sm text-gray-500 mt-1">
                Assign follow-up actions with responsibilities and deadlines
              </p>
            </div>

            {/* Next Review Date */}
            <div>
              <label className="block text-sm font-medium mb-1">
                Next Review Date
              </label>
              <input
                type="date"
                value={formData.next_review_date}
                onChange={(e) => setFormData({ ...formData, next_review_date: e.target.value })}
                className="w-full border rounded px-3 py-2"
              />
              <p className="text-sm text-gray-500 mt-1">
                Schedule the next management review (typically quarterly or semi-annually)
              </p>
            </div>
          </div>

          {/* Review Guidelines */}
          <div className="bg-indigo-50 border border-indigo-200 rounded-lg p-4">
            <h3 className="font-semibold text-indigo-900 mb-2">📊 Management Review Guidelines</h3>
            <div className="space-y-2 text-sm text-indigo-800">
              <div>
                <strong>ISO 9001 Requirements:</strong> Top management must review the QMS at planned intervals
              </div>
              <div>
                <strong>Review Inputs:</strong> Audit results, customer feedback, NC/CA status, process performance, resource needs
              </div>
              <div>
                <strong>Review Outputs:</strong> Decisions on QMS improvements, resource allocation, actions for improvement
              </div>
              <div>
                <strong>Frequency:</strong> Typically conducted quarterly or semi-annually, minimum annually
              </div>
            </div>
          </div>

          {/* Actions */}
          <div className="flex gap-4">
            <button
              type="submit"
              disabled={loading}
              className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-lg transition disabled:bg-gray-400"
            >
              {loading ? "Creating..." : "Create Management Review"}
            </button>
            <button
              type="button"
              onClick={() => router.back()}
              className="bg-gray-200 hover:bg-gray-300 text-gray-700 px-6 py-2 rounded-lg transition"
            >
              Cancel
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
