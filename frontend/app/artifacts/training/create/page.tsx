"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";

export default function CreateTrainingRecordPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [formData, setFormData] = useState({
    employee_id: "",
    training_title: "",
    training_date: "",
    trainer_name: "",
    training_hours: "",
    training_type: "",
    competency_area: "",
    passed: "",
    score: "",
    certificate_number: "",
    expiry_date: "",
    notes: "",
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const token = localStorage.getItem("access_token");
      
      // Prepare data with proper types
      const submitData: any = {
        employee_id: formData.employee_id,
        training_title: formData.training_title,
        training_date: formData.training_date,
      };
      
      if (formData.trainer_name) submitData.trainer_name = formData.trainer_name;
      if (formData.training_hours) submitData.training_hours = parseFloat(formData.training_hours);
      if (formData.training_type) submitData.training_type = formData.training_type;
      if (formData.competency_area) submitData.competency_area = formData.competency_area;
      if (formData.passed !== "") submitData.passed = formData.passed === "true";
      if (formData.score) submitData.score = parseFloat(formData.score);
      if (formData.certificate_number) submitData.certificate_number = formData.certificate_number;
      if (formData.expiry_date) submitData.expiry_date = formData.expiry_date;
      if (formData.notes) submitData.notes = formData.notes;

      const response = await fetch("http://localhost:8889/api/v1/artifacts/training", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(submitData),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Failed to create training record");
      }

      const data = await response.json();
      router.push(`/artifacts/training/${data.id}`);
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
          <h1 className="text-3xl font-bold">Add Training Record</h1>
          <p className="text-gray-600 mt-2">
            Document employee training and competency development
          </p>
        </div>

        {error && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="bg-white rounded-lg shadow p-6 space-y-4">
            <h2 className="text-xl font-semibold mb-4">Training Information</h2>

            {/* Employee ID */}
            <div>
              <label className="block text-sm font-medium mb-1">
                Employee ID <span className="text-red-500">*</span>
              </label>
              <input
                type="text"
                required
                value={formData.employee_id}
                onChange={(e) => setFormData({ ...formData, employee_id: e.target.value })}
                className="w-full border rounded px-3 py-2"
                placeholder="e.g., EMP001"
              />
            </div>

            {/* Training Title */}
            <div>
              <label className="block text-sm font-medium mb-1">
                Training Title <span className="text-red-500">*</span>
              </label>
              <input
                type="text"
                required
                value={formData.training_title}
                onChange={(e) => setFormData({ ...formData, training_title: e.target.value })}
                className="w-full border rounded px-3 py-2"
                placeholder="e.g., ISO 9001 Internal Auditor Training"
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              {/* Training Date */}
              <div>
                <label className="block text-sm font-medium mb-1">
                  Training Date <span className="text-red-500">*</span>
                </label>
                <input
                  type="date"
                  required
                  value={formData.training_date}
                  onChange={(e) => setFormData({ ...formData, training_date: e.target.value })}
                  className="w-full border rounded px-3 py-2"
                />
              </div>

              {/* Training Hours */}
              <div>
                <label className="block text-sm font-medium mb-1">
                  Training Hours
                </label>
                <input
                  type="number"
                  step="0.5"
                  value={formData.training_hours}
                  onChange={(e) => setFormData({ ...formData, training_hours: e.target.value })}
                  className="w-full border rounded px-3 py-2"
                  placeholder="e.g., 8"
                />
              </div>
            </div>

            {/* Trainer Name */}
            <div>
              <label className="block text-sm font-medium mb-1">
                Trainer Name
              </label>
              <input
                type="text"
                value={formData.trainer_name}
                onChange={(e) => setFormData({ ...formData, trainer_name: e.target.value })}
                className="w-full border rounded px-3 py-2"
                placeholder="e.g., John Smith"
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              {/* Training Type */}
              <div>
                <label className="block text-sm font-medium mb-1">
                  Training Type
                </label>
                <select
                  value={formData.training_type}
                  onChange={(e) => setFormData({ ...formData, training_type: e.target.value })}
                  className="w-full border rounded px-3 py-2"
                >
                  <option value="">Select type...</option>
                  <option value="classroom">Classroom</option>
                  <option value="online">Online</option>
                  <option value="on-the-job">On-the-Job</option>
                  <option value="workshop">Workshop</option>
                  <option value="certification">Certification</option>
                </select>
              </div>

              {/* Competency Area */}
              <div>
                <label className="block text-sm font-medium mb-1">
                  Competency Area
                </label>
                <input
                  type="text"
                  value={formData.competency_area}
                  onChange={(e) => setFormData({ ...formData, competency_area: e.target.value })}
                  className="w-full border rounded px-3 py-2"
                  placeholder="e.g., Quality Auditing"
                />
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6 space-y-4">
            <h2 className="text-xl font-semibold mb-4">Assessment & Certification</h2>

            <div className="grid grid-cols-2 gap-4">
              {/* Passed */}
              <div>
                <label className="block text-sm font-medium mb-1">
                  Training Result
                </label>
                <select
                  value={formData.passed}
                  onChange={(e) => setFormData({ ...formData, passed: e.target.value })}
                  className="w-full border rounded px-3 py-2"
                >
                  <option value="">Not assessed</option>
                  <option value="true">Passed</option>
                  <option value="false">Failed</option>
                </select>
              </div>

              {/* Score */}
              <div>
                <label className="block text-sm font-medium mb-1">
                  Score (%)
                </label>
                <input
                  type="number"
                  step="0.1"
                  min="0"
                  max="100"
                  value={formData.score}
                  onChange={(e) => setFormData({ ...formData, score: e.target.value })}
                  className="w-full border rounded px-3 py-2"
                  placeholder="e.g., 85.5"
                />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              {/* Certificate Number */}
              <div>
                <label className="block text-sm font-medium mb-1">
                  Certificate Number
                </label>
                <input
                  type="text"
                  value={formData.certificate_number}
                  onChange={(e) => setFormData({ ...formData, certificate_number: e.target.value })}
                  className="w-full border rounded px-3 py-2"
                  placeholder="e.g., CERT-2025-001"
                />
              </div>

              {/* Expiry Date */}
              <div>
                <label className="block text-sm font-medium mb-1">
                  Certificate Expiry Date
                </label>
                <input
                  type="date"
                  value={formData.expiry_date}
                  onChange={(e) => setFormData({ ...formData, expiry_date: e.target.value })}
                  className="w-full border rounded px-3 py-2"
                />
              </div>
            </div>

            {/* Notes */}
            <div>
              <label className="block text-sm font-medium mb-1">
                Notes
              </label>
              <textarea
                value={formData.notes}
                onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
                className="w-full border rounded px-3 py-2"
                rows={4}
                placeholder="Additional notes about the training, performance, or follow-up actions..."
              />
            </div>
          </div>

          {/* Training Guidelines */}
          <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
            <h3 className="font-semibold text-purple-900 mb-2">📚 Training Record Guidelines</h3>
            <div className="space-y-2 text-sm text-purple-800">
              <div>
                <strong>ISO 9001 Requirements:</strong> Maintain records of education, training, skills, and experience
              </div>
              <div>
                <strong>Competency:</strong> Ensure personnel are competent based on appropriate education and training
              </div>
              <div>
                <strong>Effectiveness:</strong> Take actions to acquire necessary competence and evaluate effectiveness
              </div>
              <div>
                <strong>Records:</strong> Retain documented information as evidence of competence
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
              {loading ? "Saving..." : "Save Training Record"}
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
