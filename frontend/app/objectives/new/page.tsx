'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { Target, ArrowLeft, Calendar, FileText, Link as LinkIcon } from 'lucide-react';
import Link from 'next/link';

interface ISOStandard {
  id: string;
  name: string;
  version: string;
}

export default function NewObjectivePage() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [isoStandards, setIsoStandards] = useState<ISOStandard[]>([]);
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    target_value: '',
    unit_of_measure: '',
    measurement_method: '',
    measurement_frequency: '',
    department: '',
    target_date: '',
    iso_standard_id: '',
    related_clause: '',
    linked_processes: '',
    linked_risks: ''
  });

  useEffect(() => {
    fetchISOStandards();
  }, []);

  const fetchISOStandards = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/v1/iso-standards');
      const data = await response.json();
      setIsoStandards(data);
    } catch (error) {
      console.error('Failed to fetch ISO standards:', error);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    try {
      const payload = {
        ...formData,
        linked_processes: formData.linked_processes ? JSON.stringify(formData.linked_processes.split(',').map(p => p.trim())) : null,
        linked_risks: formData.linked_risks ? JSON.stringify(formData.linked_risks.split(',').map(r => r.trim())) : null,
      };

      const response = await fetch('http://localhost:8000/api/v1/objectives', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        throw new Error('Failed to create objective');
      }

      const result = await response.json();
      router.push(`/objectives/${result.id}`);
    } catch (error) {
      console.error('Failed to create objective:', error);
      alert('Failed to create objective. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      {/* Header */}
      <div className="mb-8">
        <Link
          href="/objectives"
          className="inline-flex items-center gap-2 text-gray-600 hover:text-gray-900 mb-4"
        >
          <ArrowLeft className="h-4 w-4" />
          Back to Objectives
        </Link>
        <div className="flex items-center gap-3">
          <Target className="h-8 w-8 text-blue-600" />
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Create Quality Objective</h1>
            <p className="text-gray-600 mt-1">ISO 6.2 - Define measurable quality objectives</p>
          </div>
        </div>
      </div>

      {/* Form */}
      <form onSubmit={handleSubmit} className="max-w-3xl">
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 space-y-6">
          
          {/* Basic Information */}
          <div>
            <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
              <FileText className="h-5 w-5" />
              Basic Information
            </h2>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Title *
                </label>
                <input
                  type="text"
                  name="title"
                  required
                  value={formData.title}
                  onChange={handleChange}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="e.g., Reduce customer complaints by 30%"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Description
                </label>
                <textarea
                  name="description"
                  value={formData.description}
                  onChange={handleChange}
                  rows={3}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="Detailed description of the objective..."
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Department
                </label>
                <input
                  type="text"
                  name="department"
                  value={formData.department}
                  onChange={handleChange}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="e.g., Quality Assurance"
                />
              </div>
            </div>
          </div>

          {/* Measurement */}
          <div>
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Measurement</h2>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Target Value *
                </label>
                <input
                  type="text"
                  name="target_value"
                  required
                  value={formData.target_value}
                  onChange={handleChange}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="e.g., 100"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Unit of Measure
                </label>
                <input
                  type="text"
                  name="unit_of_measure"
                  value={formData.unit_of_measure}
                  onChange={handleChange}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="e.g., complaints, %, units"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Measurement Method
                </label>
                <input
                  type="text"
                  name="measurement_method"
                  value={formData.measurement_method}
                  onChange={handleChange}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="How will you measure this?"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Measurement Frequency
                </label>
                <select
                  name="measurement_frequency"
                  value={formData.measurement_frequency}
                  onChange={handleChange}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  <option value="">Select frequency</option>
                  <option value="Daily">Daily</option>
                  <option value="Weekly">Weekly</option>
                  <option value="Monthly">Monthly</option>
                  <option value="Quarterly">Quarterly</option>
                  <option value="Annually">Annually</option>
                </select>
              </div>
            </div>
          </div>

          {/* Timeline */}
          <div>
            <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
              <Calendar className="h-5 w-5" />
              Timeline
            </h2>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Target Date *
              </label>
              <input
                type="date"
                name="target_date"
                required
                value={formData.target_date}
                onChange={handleChange}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
          </div>

          {/* ISO Context */}
          <div>
            <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
              <LinkIcon className="h-5 w-5" />
              ISO Context
            </h2>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Related ISO Standard
                </label>
                <select
                  name="iso_standard_id"
                  value={formData.iso_standard_id}
                  onChange={handleChange}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  <option value="">Select ISO standard</option>
                  {isoStandards.map(standard => (
                    <option key={standard.id} value={standard.id}>
                      {standard.name} {standard.version}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Related Clause
                </label>
                <input
                  type="text"
                  name="related_clause"
                  value={formData.related_clause}
                  onChange={handleChange}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="e.g., 6.2, 8.1"
                />
              </div>
            </div>
          </div>

          {/* Linkages */}
          <div>
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Linkages</h2>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Linked Processes (comma-separated)
                </label>
                <input
                  type="text"
                  name="linked_processes"
                  value={formData.linked_processes}
                  onChange={handleChange}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="e.g., Manufacturing, Quality Control, Customer Service"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Linked Risks (comma-separated)
                </label>
                <input
                  type="text"
                  name="linked_risks"
                  value={formData.linked_risks}
                  onChange={handleChange}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="e.g., R-001, R-005"
                />
              </div>
            </div>
          </div>

          {/* Actions */}
          <div className="flex gap-4 pt-4 border-t border-gray-200">
            <button
              type="submit"
              disabled={loading}
              className="flex-1 bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition-colors disabled:bg-gray-400 disabled:cursor-not-allowed font-medium"
            >
              {loading ? 'Creating...' : 'Create Objective'}
            </button>
            <Link
              href="/objectives"
              className="px-6 py-3 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors font-medium text-gray-700"
            >
              Cancel
            </Link>
          </div>
        </div>
      </form>
    </div>
  );
}
