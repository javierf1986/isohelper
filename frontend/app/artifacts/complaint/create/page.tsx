"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";

export default function CreateComplaintPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [formData, setFormData] = useState({
    complaint_title: "",
    complaint_description: "",
    customer_name: "",
    received_date: "",
    complaint_source: "",
    product_service: "",
    priority: "medium",
    assigned_to: "",
    resolution_target_date: "",
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const token = localStorage.getItem("access_token");
      
      // Prepare data
      const submitData: any = {
        complaint_title: formData.complaint_title,
        complaint_description: formData.complaint_description,
        customer_name: formData.customer_name,
        received_date: formData.received_date,
        priority: formData.priority,
      };
      
      if (formData.complaint_source) submitData.complaint_source = formData.complaint_source;
      if (formData.product_service) submitData.product_service = formData.product_service;
      if (formData.assigned_to) submitData.assigned_to = formData.assigned_to;
      if (formData.resolution_target_date) submitData.resolution_target_date = formData.resolution_target_date;

      const response = await fetch("http://localhost:8889/api/v1/artifacts/complaint", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(submitData),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Failed to create customer complaint");
      }

      const data = await response.json();
      router.push(`/artifacts/complaint/${data.id}`);
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
          <h1 className="text-3xl font-bold">Log Customer Complaint</h1>
          <p className="text-gray-600 mt-2">
            Record and track customer complaints to drive continuous improvement
          </p>
        </div>

        {error && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="bg-white rounded-lg shadow p-6 space-y-4">
            <h2 className="text-xl font-semibold mb-4">Complaint Details</h2>

            {/* Complaint Title */}
            <div>
              <label className="block text-sm font-medium mb-1">
                Complaint Title <span className="text-red-500">*</span>
              </label>
              <input
                type="text"
                required
                value={formData.complaint_title}
                onChange={(e) => setFormData({ ...formData, complaint_title: e.target.value })}
                className="w-full border rounded px-3 py-2"
                placeholder="e.g., Defective Product - Part Not Functioning"
              />
            </div>

            {/* Complaint Description */}
            <div>
              <label className="block text-sm font-medium mb-1">
                Complaint Description <span className="text-red-500">*</span>
              </label>
              <textarea
                required
                value={formData.complaint_description}
                onChange={(e) => setFormData({ ...formData, complaint_description: e.target.value })}
                className="w-full border rounded px-3 py-2"
                rows={5}
                placeholder="Provide detailed description of the complaint, including what happened, when, and any relevant context..."
              />
              <p className="text-sm text-gray-500 mt-1">
                Include all relevant details to help with investigation and resolution
              </p>
            </div>

            <div className="grid grid-cols-2 gap-4">
              {/* Customer Name */}
              <div>
                <label className="block text-sm font-medium mb-1">
                  Customer Name <span className="text-red-500">*</span>
                </label>
                <input
                  type="text"
                  required
                  value={formData.customer_name}
                  onChange={(e) => setFormData({ ...formData, customer_name: e.target.value })}
                  className="w-full border rounded px-3 py-2"
                  placeholder="e.g., ABC Corporation"
                />
              </div>

              {/* Received Date */}
              <div>
                <label className="block text-sm font-medium mb-1">
                  Received Date <span className="text-red-500">*</span>
                </label>
                <input
                  type="date"
                  required
                  value={formData.received_date}
                  onChange={(e) => setFormData({ ...formData, received_date: e.target.value })}
                  className="w-full border rounded px-3 py-2"
                />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              {/* Complaint Source */}
              <div>
                <label className="block text-sm font-medium mb-1">
                  Complaint Source
                </label>
                <select
                  value={formData.complaint_source}
                  onChange={(e) => setFormData({ ...formData, complaint_source: e.target.value })}
                  className="w-full border rounded px-3 py-2"
                >
                  <option value="">Select source...</option>
                  <option value="email">Email</option>
                  <option value="phone">Phone</option>
                  <option value="in-person">In Person</option>
                  <option value="website">Website</option>
                  <option value="social-media">Social Media</option>
                  <option value="letter">Letter</option>
                </select>
              </div>

              {/* Product/Service */}
              <div>
                <label className="block text-sm font-medium mb-1">
                  Product/Service
                </label>
                <input
                  type="text"
                  value={formData.product_service}
                  onChange={(e) => setFormData({ ...formData, product_service: e.target.value })}
                  className="w-full border rounded px-3 py-2"
                  placeholder="e.g., Product XYZ-123"
                />
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6 space-y-4">
            <h2 className="text-xl font-semibold mb-4">Management & Resolution</h2>

            <div className="grid grid-cols-2 gap-4">
              {/* Priority */}
              <div>
                <label className="block text-sm font-medium mb-1">
                  Priority <span className="text-red-500">*</span>
                </label>
                <select
                  required
                  value={formData.priority}
                  onChange={(e) => setFormData({ ...formData, priority: e.target.value })}
                  className="w-full border rounded px-3 py-2"
                >
                  <option value="low">Low</option>
                  <option value="medium">Medium</option>
                  <option value="high">High</option>
                  <option value="urgent">Urgent</option>
                </select>
              </div>

              {/* Assigned To */}
              <div>
                <label className="block text-sm font-medium mb-1">
                  Assigned To
                </label>
                <input
                  type="text"
                  value={formData.assigned_to}
                  onChange={(e) => setFormData({ ...formData, assigned_to: e.target.value })}
                  className="w-full border rounded px-3 py-2"
                  placeholder="User ID or name"
                />
              </div>
            </div>

            {/* Resolution Target Date */}
            <div>
              <label className="block text-sm font-medium mb-1">
                Resolution Target Date
              </label>
              <input
                type="date"
                value={formData.resolution_target_date}
                onChange={(e) => setFormData({ ...formData, resolution_target_date: e.target.value })}
                className="w-full border rounded px-3 py-2"
              />
              <p className="text-sm text-gray-500 mt-1">
                Set a target date for resolving this complaint
              </p>
            </div>
          </div>

          {/* Priority Guidelines */}
          <div className="bg-orange-50 border border-orange-200 rounded-lg p-4">
            <h3 className="font-semibold text-orange-900 mb-2">⚠️ Priority Guidelines</h3>
            <div className="space-y-2 text-sm text-orange-800">
              <div>
                <strong>Urgent:</strong> Critical safety issue or major customer impact - immediate action required
              </div>
              <div>
                <strong>High:</strong> Significant quality issue affecting multiple customers or high-value client
              </div>
              <div>
                <strong>Medium:</strong> Standard quality issue requiring investigation and resolution
              </div>
              <div>
                <strong>Low:</strong> Minor issue or suggestion with limited impact
              </div>
            </div>
          </div>

          {/* Complaint Management Guidelines */}
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <h3 className="font-semibold text-blue-900 mb-2">📞 Complaint Management Best Practices</h3>
            <div className="space-y-2 text-sm text-blue-800">
              <div>
                <strong>Acknowledge:</strong> Contact customer within 24 hours to acknowledge receipt
              </div>
              <div>
                <strong>Investigate:</strong> Conduct thorough root cause analysis
              </div>
              <div>
                <strong>Resolve:</strong> Implement corrective actions to prevent recurrence
              </div>
              <div>
                <strong>Follow-up:</strong> Verify customer satisfaction with resolution
              </div>
              <div>
                <strong>Learn:</strong> Use complaints as opportunities for continuous improvement
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
              {loading ? "Logging..." : "Log Complaint"}
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
