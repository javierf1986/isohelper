'use client';

import { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import Link from 'next/link';
import {
  Target,
  ArrowLeft,
  TrendingUp,
  Calendar,
  CheckCircle2,
  Clock,
  AlertCircle,
  FileText,
  Link as LinkIcon,
  Trash2,
  Edit,
  Plus
} from 'lucide-react';

interface Objective {
  id: string;
  objective_number: string;
  title: string;
  description: string;
  target_value: string;
  current_value: string;
  unit_of_measure: string;
  measurement_method: string;
  measurement_frequency: string;
  status: string;
  progress_percentage: number;
  responsible_person: string;
  department: string;
  target_date: string;
  start_date: string;
  achieved_date: string | null;
  iso_standard_id: string | null;
  related_clause: string;
  linked_processes: string | null;
  linked_risks: string | null;
  evidence: string | null;
  progress_notes: string | null;
  review_comments: string;
  created_at: string;
  is_active: boolean;
}

export default function ObjectiveDetailPage() {
  const params = useParams();
  const router = useRouter();
  const [objective, setObjective] = useState<Objective | null>(null);
  const [loading, setLoading] = useState(true);
  const [showProgressModal, setShowProgressModal] = useState(false);
  const [progressUpdate, setProgressUpdate] = useState({
    current_value: '',
    progress_percentage: 0,
    note: ''
  });

  useEffect(() => {
    if (params.id) {
      fetchObjective();
    }
  }, [params.id]);

  const fetchObjective = async () => {
    setLoading(true);
    try {
      const response = await fetch(`http://localhost:8000/api/v1/objectives/${params.id}`);
      const data = await response.json();
      setObjective(data);
      setProgressUpdate({
        current_value: data.current_value || '',
        progress_percentage: data.progress_percentage,
        note: ''
      });
    } catch (error) {
      console.error('Failed to fetch objective:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleProgressUpdate = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const response = await fetch(
        `http://localhost:8000/api/v1/objectives/${params.id}/progress?current_value=${progressUpdate.current_value}&progress_percentage=${progressUpdate.progress_percentage}&note=${encodeURIComponent(progressUpdate.note)}`,
        { method: 'PATCH' }
      );

      if (!response.ok) throw new Error('Failed to update progress');

      setShowProgressModal(false);
      fetchObjective();
    } catch (error) {
      console.error('Failed to update progress:', error);
      alert('Failed to update progress');
    }
  };

  const handleDelete = async () => {
    if (!confirm('Are you sure you want to delete this objective?')) return;

    try {
      const response = await fetch(`http://localhost:8000/api/v1/objectives/${params.id}`, {
        method: 'DELETE'
      });

      if (!response.ok) throw new Error('Failed to delete objective');

      router.push('/objectives');
    } catch (error) {
      console.error('Failed to delete objective:', error);
      alert('Failed to delete objective');
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'ACHIEVED':
        return <CheckCircle2 className="h-6 w-6 text-green-500" />;
      case 'IN_PROGRESS':
        return <TrendingUp className="h-6 w-6 text-blue-500" />;
      case 'DELAYED':
        return <AlertCircle className="h-6 w-6 text-red-500" />;
      default:
        return <Clock className="h-6 w-6 text-gray-500" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'ACHIEVED':
        return 'bg-green-100 text-green-800';
      case 'IN_PROGRESS':
        return 'bg-blue-100 text-blue-800';
      case 'DELAYED':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-yellow-100 text-yellow-800';
    }
  };

  const getProgressColor = (progress: number) => {
    if (progress >= 80) return 'bg-green-500';
    if (progress >= 50) return 'bg-blue-500';
    if (progress >= 25) return 'bg-yellow-500';
    return 'bg-red-500';
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-gray-500">Loading objective...</div>
      </div>
    );
  }

  if (!objective) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Objective not found</h2>
          <Link href="/objectives" className="text-blue-600 hover:text-blue-700">
            Back to Objectives
          </Link>
        </div>
      </div>
    );
  }

  const progressNotes = objective.progress_notes ? JSON.parse(objective.progress_notes) : [];
  const linkedProcesses = objective.linked_processes ? JSON.parse(objective.linked_processes) : [];
  const linkedRisks = objective.linked_risks ? JSON.parse(objective.linked_risks) : [];

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
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            {getStatusIcon(objective.status)}
            <div>
              <div className="flex items-center gap-3 mb-1">
                <h1 className="text-3xl font-bold text-gray-900">{objective.title}</h1>
                <span className={`px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(objective.status)}`}>
                  {objective.status.replace('_', ' ')}
                </span>
              </div>
              <p className="text-gray-600 font-mono">{objective.objective_number}</p>
            </div>
          </div>
          <div className="flex gap-3">
            <button
              onClick={() => setShowProgressModal(true)}
              className="flex items-center gap-2 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700"
            >
              <TrendingUp className="h-4 w-4" />
              Update Progress
            </button>
            <button
              onClick={handleDelete}
              className="flex items-center gap-2 bg-red-600 text-white px-4 py-2 rounded-lg hover:bg-red-700"
            >
              <Trash2 className="h-4 w-4" />
              Delete
            </button>
          </div>
        </div>
      </div>

      {/* Progress Card */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-semibold text-gray-900">Progress</h2>
          <span className="text-3xl font-bold text-gray-900">{objective.progress_percentage}%</span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-4 mb-4">
          <div
            className={`h-4 rounded-full transition-all ${getProgressColor(objective.progress_percentage)}`}
            style={{ width: `${objective.progress_percentage}%` }}
          />
        </div>
        <div className="grid grid-cols-3 gap-4 text-center">
          <div>
            <div className="text-sm text-gray-600 mb-1">Current</div>
            <div className="text-2xl font-bold text-blue-600">
              {objective.current_value || '-'} {objective.unit_of_measure}
            </div>
          </div>
          <div>
            <div className="text-sm text-gray-600 mb-1">Target</div>
            <div className="text-2xl font-bold text-green-600">
              {objective.target_value} {objective.unit_of_measure}
            </div>
          </div>
          <div>
            <div className="text-sm text-gray-600 mb-1">Remaining</div>
            <div className="text-2xl font-bold text-gray-900">
              {objective.target_value && objective.current_value
                ? Math.abs(parseFloat(objective.target_value) - parseFloat(objective.current_value))
                : '-'} {objective.unit_of_measure}
            </div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-3 gap-6">
        {/* Main Content */}
        <div className="col-span-2 space-y-6">
          {/* Details */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4 flex items-center gap-2">
              <FileText className="h-5 w-5" />
              Details
            </h2>
            <div className="space-y-4">
              {objective.description && (
                <div>
                  <div className="text-sm font-medium text-gray-700 mb-1">Description</div>
                  <p className="text-gray-900">{objective.description}</p>
                </div>
              )}
              <div className="grid grid-cols-2 gap-4">
                {objective.measurement_method && (
                  <div>
                    <div className="text-sm font-medium text-gray-700 mb-1">Measurement Method</div>
                    <p className="text-gray-900">{objective.measurement_method}</p>
                  </div>
                )}
                {objective.measurement_frequency && (
                  <div>
                    <div className="text-sm font-medium text-gray-700 mb-1">Frequency</div>
                    <p className="text-gray-900">{objective.measurement_frequency}</p>
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Progress Notes */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Progress History</h2>
            {progressNotes.length === 0 ? (
              <p className="text-gray-500 text-center py-8">No progress updates yet</p>
            ) : (
              <div className="space-y-4">
                {progressNotes.reverse().map((note: any, index: number) => (
                  <div key={index} className="border-l-4 border-blue-500 pl-4 py-2">
                    <div className="flex items-center justify-between mb-1">
                      <span className="font-medium text-gray-900">{note.progress}% Progress</span>
                      <span className="text-sm text-gray-500">{new Date(note.date).toLocaleDateString()}</span>
                    </div>
                    <p className="text-gray-700">{note.note}</p>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* Timeline */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
              <Calendar className="h-5 w-5" />
              Timeline
            </h3>
            <div className="space-y-3">
              <div>
                <div className="text-sm text-gray-600">Start Date</div>
                <div className="font-medium">{new Date(objective.start_date).toLocaleDateString()}</div>
              </div>
              <div>
                <div className="text-sm text-gray-600">Target Date</div>
                <div className="font-medium">{new Date(objective.target_date).toLocaleDateString()}</div>
              </div>
              {objective.achieved_date && (
                <div>
                  <div className="text-sm text-gray-600">Achieved Date</div>
                  <div className="font-medium text-green-600">{new Date(objective.achieved_date).toLocaleDateString()}</div>
                </div>
              )}
            </div>
          </div>

          {/* Responsibility */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Responsibility</h3>
            {objective.department && (
              <div className="mb-3">
                <div className="text-sm text-gray-600">Department</div>
                <div className="font-medium">{objective.department}</div>
              </div>
            )}
            <div>
              <div className="text-sm text-gray-600">Responsible Person</div>
              <div className="font-medium">{objective.responsible_person}</div>
            </div>
          </div>

          {/* ISO Context */}
          {(objective.related_clause || linkedProcesses.length > 0 || linkedRisks.length > 0) && (
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
                <LinkIcon className="h-5 w-5" />
                Linkages
              </h3>
              {objective.related_clause && (
                <div className="mb-3">
                  <div className="text-sm text-gray-600">ISO Clause</div>
                  <div className="font-medium">{objective.related_clause}</div>
                </div>
              )}
              {linkedProcesses.length > 0 && (
                <div className="mb-3">
                  <div className="text-sm text-gray-600 mb-1">Linked Processes</div>
                  <div className="flex flex-wrap gap-2">
                    {linkedProcesses.map((process: string, i: number) => (
                      <span key={i} className="px-2 py-1 bg-blue-100 text-blue-800 rounded text-sm">
                        {process}
                      </span>
                    ))}
                  </div>
                </div>
              )}
              {linkedRisks.length > 0 && (
                <div>
                  <div className="text-sm text-gray-600 mb-1">Linked Risks</div>
                  <div className="flex flex-wrap gap-2">
                    {linkedRisks.map((risk: string, i: number) => (
                      <span key={i} className="px-2 py-1 bg-red-100 text-red-800 rounded text-sm">
                        {risk}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </div>

      {/* Progress Update Modal */}
      {showProgressModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl p-6 w-full max-w-md">
            <h3 className="text-xl font-semibold text-gray-900 mb-4">Update Progress</h3>
            <form onSubmit={handleProgressUpdate}>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Current Value
                  </label>
                  <input
                    type="text"
                    value={progressUpdate.current_value}
                    onChange={(e) => setProgressUpdate({ ...progressUpdate, current_value: e.target.value })}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                    placeholder={`e.g., ${objective.target_value}`}
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Progress Percentage: {progressUpdate.progress_percentage}%
                  </label>
                  <input
                    type="range"
                    min="0"
                    max="100"
                    value={progressUpdate.progress_percentage}
                    onChange={(e) => setProgressUpdate({ ...progressUpdate, progress_percentage: parseFloat(e.target.value) })}
                    className="w-full"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Progress Note
                  </label>
                  <textarea
                    value={progressUpdate.note}
                    onChange={(e) => setProgressUpdate({ ...progressUpdate, note: e.target.value })}
                    rows={3}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                    placeholder="What changed? Any challenges?"
                  />
                </div>
              </div>
              <div className="flex gap-3 mt-6">
                <button
                  type="submit"
                  className="flex-1 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700"
                >
                  Update
                </button>
                <button
                  type="button"
                  onClick={() => setShowProgressModal(false)}
                  className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
                >
                  Cancel
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
