"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";

export default function CreateAuditPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [formData, setFormData] = useState({
    title: "",
    audit_type: "PROCESS",
    scope_description: "",
    planned_date: "",
    iso_standard_id: "",
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const token = localStorage.getItem("access_token");
      const response = await fetch("http://localhost:8889/api/v1/artifacts/audit", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(formData),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Failed to create audit");
      }

      const data = await response.json();
      router.push(`/artifacts/audit/${data.id}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "An error occurred");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="max-w-3xl mx-auto">
        <div className="mb-6">
          <button
            onClick={() => router.back()}
            className="text-blue-600 hover:text-blue-800 mb-4"
          >
            ← Back
          </button>
          <h1 className="text-3xl font-bold">Schedule Internal Audit</h1>
          <p className="text-gray-600 mt-2">
            Plan a new internal audit to verify compliance with ISO standards
          </p>
        </div>

        {error && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="bg-white rounded-lg shadow p-6 space-y-4">
            <h2 className="text-xl font-semibold mb-4">Audit Information</h2>

            {/* Title */}
            <div>
              <label className="block text-sm font-medium mb-1">
                Audit Title <span className="text-red-500">*</span>
              </label>
              <input
                type="text"
                required
                value={formData.title}
                onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                className="w-full border rounded px-3 py-2"
                placeholder="e.g., Q1 2025 Process Audit - Manufacturing"
              />
            </div>

            {/* Audit Type */}
            <div>
              <label className="block text-sm font-medium mb-1">
                Audit Type <span className="text-red-500">*</span>
              </label>
              <select
                required
                value={formData.audit_type}
                onChange={(e) => setFormData({ ...formData, audit_type: e.target.value })}
                className="w-full border rounded px-3 py-2"
              >
                <option value="PROCESS">Process Audit</option>
                <option value="PRODUCT">Product Audit</option>
                <option value="SYSTEM">System Audit</option>
                <option value="COMPLIANCE">Compliance Audit</option>
              </select>
              <p className="text-sm text-gray-500 mt-1">
                Select the type of audit being conducted
              </p>
            </div>

            {/* Planned Date */}
            <div>
              <label className="block text-sm font-medium mb-1">
                Planned Date <span className="text-red-500">*</span>
              </label>
              <input
                type="date"
                required
                value={formData.planned_date}
                onChange={(e) => setFormData({ ...formData, planned_date: e.target.value })}
                className="w-full border rounded px-3 py-2"
              />
            </div>

            {/* Scope Description */}
            <div>
              <label className="block text-sm font-medium mb-1">
                Scope Description <span className="text-red-500">*</span>
              </label>
              <textarea
                required
                value={formData.scope_description}
                onChange={(e) => setFormData({ ...formData, scope_description: e.target.value })}
                className="w-full border rounded px-3 py-2"
                rows={4}
                placeholder="Describe the audit scope, areas to be covered, and objectives..."
              />
              <p className="text-sm text-gray-500 mt-1">
                Provide a clear description of what will be audited
              </p>
            </div>

            {/* ISO Standard (Optional) */}
            <div>
              <label className="block text-sm font-medium mb-1">
                ISO Standard ID (Optional)
              </label>
              <input
                type="text"
                value={formData.iso_standard_id}
                onChange={(e) => setFormData({ ...formData, iso_standard_id: e.target.value })}
                className="w-full border rounded px-3 py-2"
                placeholder="e.g., ISO9001-2015"
              />
              <p className="text-sm text-gray-500 mt-1">
                Link this audit to a specific ISO standard
              </p>
            </div>
          </div>

          {/* Audit Type Guidelines */}
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <h3 className="font-semibold text-blue-900 mb-2">📋 Audit Type Guidelines</h3>
            <div className="space-y-2 text-sm text-blue-800">
              <div>
                <strong>Process Audit:</strong> Evaluates the effectiveness of processes and procedures
              </div>
              <div>
                <strong>Product Audit:</strong> Examines product quality and conformance to specifications
              </div>
              <div>
                <strong>System Audit:</strong> Reviews the entire management system for compliance
              </div>
              <div>
                <strong>Compliance Audit:</strong> Verifies adherence to ISO standards and regulations
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
              {loading ? "Scheduling..." : "Schedule Audit"}
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
