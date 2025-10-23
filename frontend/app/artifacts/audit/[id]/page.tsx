'use client';

import { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';

interface AuditDetail {
  id: string;
  audit_number: string;
  title: string;
  audit_type: string;
  status: string;
  scope_description: string;
  planned_date: string;
  actual_date?: string;
  lead_auditor: string;
  team_members?: string;
  major_findings: number;
  minor_findings: number;
  observations: number;
  findings_summary?: string;
  recommendations?: string;
  follow_up_required: boolean;
  iso_standard_id?: string;
  created_at: string;
  updated_at: string;
}

export default function AuditDetailPage() {
  const params = useParams();
  const router = useRouter();
  const auditId = params.id as string;

  const [audit, setAudit] = useState<AuditDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchAuditDetail();
  }, [auditId]);

  const fetchAuditDetail = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`http://localhost:8889/api/v1/artifacts/audit/${auditId}`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        if (response.status === 404) {
          setError('Audit not found');
        } else {
          setError('Failed to load audit');
        }
        setLoading(false);
        return;
      }

      const data = await response.json();
      setAudit(data);
    } catch (err) {
      setError('Failed to connect to server');
      console.error('Error fetching audit:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async () => {
    if (!window.confirm("Are you sure you want to delete this Internal Audit? This action cannot be undone.")) {
      return;
    }

    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`http://localhost:8889/api/v1/artifacts/audit/${auditId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        throw new Error('Failed to delete audit');
      }

      router.push('/artifacts/audit');
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Failed to delete Internal Audit');
    }
  };

  const getStatusColor = (status: string) => {
    const colors: Record<string, string> = {
      planned: 'bg-blue-100 text-blue-800',
      in_progress: 'bg-purple-100 text-purple-800',
      completed: 'bg-green-100 text-green-800',
    };
    return colors[status.toLowerCase()] || 'bg-gray-100 text-gray-800';
  };

  const getTypeColor = (type: string) => {
    const colors: Record<string, string> = {
      process: 'bg-blue-100 text-blue-800',
      product: 'bg-green-100 text-green-800',
      system: 'bg-purple-100 text-purple-800',
      compliance: 'bg-orange-100 text-orange-800',
    };
    return colors[type.toLowerCase()] || 'bg-gray-100 text-gray-800';
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

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-lg">Loading audit...</div>
      </div>
    );
  }

  if (error || !audit) {
    return (
      <div className="flex flex-col items-center justify-center min-h-screen">
        <div className="text-xl text-red-600 mb-4">{error || 'Audit not found'}</div>
        <button
          onClick={() => router.push('/artifacts/audit')}
          className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
        >
          Back to Audits
        </button>
      </div>
    );
  }

  const totalFindings = audit.major_findings + audit.minor_findings;

  return (
    <div className="p-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="mb-6">
        <button
          onClick={() => router.push('/artifacts/audit')}
          className="text-blue-600 hover:text-blue-800 mb-4 flex items-center"
        >
          ← Back to Audits
        </button>
        
        <div className="flex justify-between items-start">
          <div>
            <h1 className="text-3xl font-bold mb-2">{audit.audit_number}: {audit.title}</h1>
            <div className="flex gap-3 items-center">
              <span className={`px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(audit.status)}`}>
                {audit.status.replace('_', ' ').toUpperCase()}
              </span>
              <span className={`px-3 py-1 rounded-full text-sm font-medium ${getTypeColor(audit.audit_type)}`}>
                Type: {audit.audit_type.toUpperCase()}
              </span>
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
          {/* Scope */}
          <div className="bg-white shadow rounded-lg p-6">
            <h2 className="text-xl font-semibold mb-3">Audit Scope</h2>
            <p className="text-gray-700 whitespace-pre-wrap">{audit.scope_description}</p>
          </div>

          {/* Findings Summary */}
          <div className="bg-white shadow rounded-lg p-6">
            <h2 className="text-xl font-semibold mb-4">Findings Summary</h2>
            <div className="grid grid-cols-3 gap-4 mb-4">
              <div className="bg-red-50 p-4 rounded-lg border border-red-200">
                <p className="text-sm text-red-600 mb-1">Major Findings</p>
                <p className="text-3xl font-bold text-red-700">{audit.major_findings}</p>
              </div>
              <div className="bg-yellow-50 p-4 rounded-lg border border-yellow-200">
                <p className="text-sm text-yellow-600 mb-1">Minor Findings</p>
                <p className="text-3xl font-bold text-yellow-700">{audit.minor_findings}</p>
              </div>
              <div className="bg-blue-50 p-4 rounded-lg border border-blue-200">
                <p className="text-sm text-blue-600 mb-1">Observations</p>
                <p className="text-3xl font-bold text-blue-700">{audit.observations}</p>
              </div>
            </div>
            {audit.findings_summary && (
              <div>
                <h3 className="font-medium text-gray-700 mb-2">Details:</h3>
                <p className="text-gray-700 whitespace-pre-wrap">{audit.findings_summary}</p>
              </div>
            )}
          </div>

          {/* Recommendations */}
          {audit.recommendations && (
            <div className="bg-white shadow rounded-lg p-6">
              <h2 className="text-xl font-semibold mb-3">Recommendations</h2>
              <p className="text-gray-700 whitespace-pre-wrap">{audit.recommendations}</p>
            </div>
          )}

          {/* Follow-up Status */}
          <div className="bg-white shadow rounded-lg p-6">
            <h2 className="text-xl font-semibold mb-3">Follow-up Required</h2>
            <div className="flex items-center gap-2">
              <span className={`px-3 py-1 rounded-full text-sm font-medium ${audit.follow_up_required ? 'bg-orange-100 text-orange-800' : 'bg-green-100 text-green-800'}`}>
                {audit.follow_up_required ? 'YES - Follow-up audit required' : 'NO - No follow-up required'}
              </span>
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
                <p className="text-sm text-gray-500">Lead Auditor</p>
                <p className="font-medium">{audit.lead_auditor}</p>
              </div>
              {audit.team_members && (
                <div>
                  <p className="text-sm text-gray-500">Team Members</p>
                  <p className="font-medium">{audit.team_members}</p>
                </div>
              )}
              <div>
                <p className="text-sm text-gray-500">Audit Type</p>
                <p className="font-medium capitalize">{audit.audit_type.replace('_', ' ')}</p>
              </div>
              {audit.iso_standard_id && (
                <div>
                  <p className="text-sm text-gray-500">ISO Standard</p>
                  <p className="font-medium">{audit.iso_standard_id}</p>
                </div>
              )}
              <div>
                <p className="text-sm text-gray-500">Total Findings</p>
                <p className="font-medium text-2xl">{totalFindings}</p>
              </div>
            </div>
          </div>

          {/* Timeline */}
          <div className="bg-white shadow rounded-lg p-6">
            <h2 className="text-xl font-semibold mb-4">Timeline</h2>
            <div className="space-y-4">
              <div>
                <p className="text-sm text-gray-500">Planned Date</p>
                <p className="font-medium">{formatDate(audit.planned_date)}</p>
              </div>
              {audit.actual_date && (
                <div>
                  <p className="text-sm text-gray-500">Actual Date</p>
                  <p className="font-medium">{formatDate(audit.actual_date)}</p>
                </div>
              )}
              <div className="pt-3 border-t">
                <p className="text-sm text-gray-500">Created</p>
                <p className="text-sm">{formatDateTime(audit.created_at)}</p>
              </div>
              <div>
                <p className="text-sm text-gray-500">Last Updated</p>
                <p className="text-sm">{formatDateTime(audit.updated_at)}</p>
              </div>
            </div>
          </div>

          {/* Actions */}
          <div className="bg-white shadow rounded-lg p-6">
            <h2 className="text-xl font-semibold mb-4">Actions</h2>
            <div className="space-y-3">
              <button className="w-full px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700">
                Update Status
              </button>
              <button className="w-full px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700">
                Record Findings
              </button>
              <button className="w-full px-4 py-2 bg-purple-600 text-white rounded hover:bg-purple-700">
                Create NC from Finding
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
