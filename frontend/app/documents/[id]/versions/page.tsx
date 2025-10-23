/**
 * Document Version History Page
 * Display all versions of a document with comparison, approval, and rollback capabilities
 */

'use client';

import { useRouter, useParams } from 'next/navigation';
import { ProtectedRoute } from '@/components/ProtectedRoute';
import { useState } from 'react';

interface Version {
  id: string;
  document_id: string;
  version_number: number;
  version_label: string;
  title: string;
  status: string;
  change_type: string;
  change_summary: string | null;
  content_hash: string;
  created_by: string;
  approved_by: string | null;
  approved_at: string | null;
  created_at: string;
  updated_at: string;
  iso_standard_id: string | null;
}

interface CompareModalProps {
  versions: Version[];
  onClose: () => void;
  onCompare: (v1: string, v2: string) => void;
}

function CompareModal({ versions, onClose, onCompare }: CompareModalProps) {
  const [version1, setVersion1] = useState('');
  const [version2, setVersion2] = useState('');

  const handleCompare = () => {
    if (version1 && version2 && version1 !== version2) {
      onCompare(version1, version2);
      onClose();
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
        <h3 className="text-lg font-semibold mb-4">Compare Versions</h3>
        
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              First Version
            </label>
            <select
              value={version1}
              onChange={(e) => setVersion1(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="">Select version...</option>
              {versions.map((v) => (
                <option key={v.id} value={v.id}>
                  {v.version_label} - {v.title} ({new Date(v.created_at).toLocaleDateString()})
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Second Version
            </label>
            <select
              value={version2}
              onChange={(e) => setVersion2(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="">Select version...</option>
              {versions.map((v) => (
                <option key={v.id} value={v.id}>
                  {v.version_label} - {v.title} ({new Date(v.created_at).toLocaleDateString()})
                </option>
              ))}
            </select>
          </div>
        </div>

        <div className="mt-6 flex justify-end gap-3">
          <button
            onClick={onClose}
            className="px-4 py-2 text-gray-700 bg-gray-100 rounded-md hover:bg-gray-200"
          >
            Cancel
          </button>
          <button
            onClick={handleCompare}
            disabled={!version1 || !version2 || version1 === version2}
            className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Compare
          </button>
        </div>
      </div>
    </div>
  );
}

function VersionHistoryContent() {
  const router = useRouter();
  const params = useParams();
  const documentId = params.id as string;
  
  const [versions, setVersions] = useState<Version[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showCompareModal, setShowCompareModal] = useState(false);
  const [actionLoading, setActionLoading] = useState<string | null>(null);

  // Fetch versions
  useState(() => {
    const fetchVersions = async () => {
      try {
        const token = localStorage.getItem('token');
        const response = await fetch(`http://localhost:8889/api/v1/versions/document/${documentId}`, {
          headers: {
            'Authorization': `Bearer ${token}`,
          },
        });

        if (!response.ok) throw new Error('Failed to fetch versions');
        
        const data = await response.json();
        setVersions(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'An error occurred');
      } finally {
        setLoading(false);
      }
    };

    fetchVersions();
  });

  const getStatusBadgeColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'approved':
        return 'bg-green-100 text-green-800';
      case 'pending_approval':
        return 'bg-yellow-100 text-yellow-800';
      case 'rejected':
        return 'bg-red-100 text-red-800';
      case 'draft':
        return 'bg-gray-100 text-gray-800';
      case 'archived':
        return 'bg-purple-100 text-purple-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getChangeTypeBadgeColor = (changeType: string) => {
    switch (changeType.toLowerCase()) {
      case 'critical':
        return 'bg-red-100 text-red-800';
      case 'major':
        return 'bg-orange-100 text-orange-800';
      case 'minor':
        return 'bg-blue-100 text-blue-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const handleApprove = async (versionId: string) => {
    if (!confirm('Are you sure you want to approve this version?')) return;

    setActionLoading(versionId);
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`http://localhost:8889/api/v1/versions/${versionId}/approve`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ comment: null }),
      });

      if (!response.ok) throw new Error('Failed to approve version');

      // Refresh versions
      const refreshResponse = await fetch(`http://localhost:8889/api/v1/versions/document/${documentId}`, {
        headers: { 'Authorization': `Bearer ${token}` },
      });
      const data = await refreshResponse.json();
      setVersions(data);
      
      alert('Version approved successfully');
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Failed to approve version');
    } finally {
      setActionLoading(null);
    }
  };

  const handleReject = async (versionId: string) => {
    const reason = prompt('Please provide a reason for rejection:');
    if (!reason) return;

    setActionLoading(versionId);
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`http://localhost:8889/api/v1/versions/${versionId}/reject`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ reason }),
      });

      if (!response.ok) throw new Error('Failed to reject version');

      // Refresh versions
      const refreshResponse = await fetch(`http://localhost:8889/api/v1/versions/document/${documentId}`, {
        headers: { 'Authorization': `Bearer ${token}` },
      });
      const data = await refreshResponse.json();
      setVersions(data);
      
      alert('Version rejected successfully');
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Failed to reject version');
    } finally {
      setActionLoading(null);
    }
  };

  const handleRollback = async (versionId: string, versionLabel: string) => {
    const reason = prompt(`Rollback to ${versionLabel}?\n\nThis will create a new version with this content. Please provide a reason:`);
    if (!reason) return;

    setActionLoading(versionId);
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`http://localhost:8889/api/v1/versions/${versionId}/rollback`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ reason }),
      });

      if (!response.ok) throw new Error('Failed to rollback version');

      // Refresh versions
      const refreshResponse = await fetch(`http://localhost:8889/api/v1/versions/document/${documentId}`, {
        headers: { 'Authorization': `Bearer ${token}` },
      });
      const data = await refreshResponse.json();
      setVersions(data);
      
      alert('Rollback successful - new version created');
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Failed to rollback version');
    } finally {
      setActionLoading(null);
    }
  };

  const handleCompare = (version1Id: string, version2Id: string) => {
    router.push(`/documents/${documentId}/versions/compare?v1=${version1Id}&v2=${version2Id}`);
  };

  const handleViewDetails = (versionId: string) => {
    router.push(`/documents/${documentId}/versions/${versionId}`);
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading version history...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center max-w-md">
          <svg className="mx-auto h-12 w-12 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
          <h2 className="mt-4 text-xl font-bold text-gray-900">Error Loading Versions</h2>
          <p className="mt-2 text-gray-600">{error}</p>
          <button
            onClick={() => router.push(`/documents/${documentId}`)}
            className="mt-6 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
          >
            Back to Document
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-6">
          <button
            onClick={() => router.push(`/documents/${documentId}`)}
            className="flex items-center text-blue-600 hover:text-blue-700 mb-4"
          >
            <svg className="w-5 h-5 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
            Back to Document
          </button>
          
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Version History</h1>
              <p className="mt-2 text-gray-600">
                {versions.length} {versions.length === 1 ? 'version' : 'versions'} • Document ID: {documentId}
              </p>
            </div>
            
            <button
              onClick={() => setShowCompareModal(true)}
              disabled={versions.length < 2}
              className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4" />
              </svg>
              Compare Versions
            </button>
          </div>
        </div>

        {/* Version Table */}
        {versions.length === 0 ? (
          <div className="bg-white rounded-lg shadow p-12 text-center">
            <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            <h3 className="mt-4 text-lg font-medium text-gray-900">No Versions Yet</h3>
            <p className="mt-2 text-gray-500">Create your first version to start tracking changes.</p>
          </div>
        ) : (
          <div className="bg-white rounded-lg shadow overflow-hidden">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Version
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Title
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Status
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Change Type
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Created
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {versions.map((version) => (
                  <tr key={version.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        <div className="flex-shrink-0 h-10 w-10 bg-blue-100 rounded-full flex items-center justify-center">
                          <span className="text-blue-600 font-medium">{version.version_number}</span>
                        </div>
                        <div className="ml-4">
                          <div className="text-sm font-medium text-gray-900">{version.version_label}</div>
                          <div className="text-xs text-gray-500">{version.content_hash.substring(0, 8)}...</div>
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <div className="text-sm text-gray-900">{version.title}</div>
                      {version.change_summary && (
                        <div className="text-xs text-gray-500 mt-1">{version.change_summary}</div>
                      )}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ${getStatusBadgeColor(version.status)}`}>
                        {version.status.replace('_', ' ')}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ${getChangeTypeBadgeColor(version.change_type)}`}>
                        {version.change_type}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      <div>{new Date(version.created_at).toLocaleDateString()}</div>
                      <div className="text-xs">{new Date(version.created_at).toLocaleTimeString()}</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                      <div className="flex gap-2">
                        <button
                          onClick={() => handleViewDetails(version.id)}
                          className="text-blue-600 hover:text-blue-900"
                          title="View Details"
                        >
                          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                          </svg>
                        </button>
                        
                        {version.status === 'DRAFT' || version.status === 'PENDING_APPROVAL' ? (
                          <>
                            <button
                              onClick={() => handleApprove(version.id)}
                              disabled={actionLoading === version.id}
                              className="text-green-600 hover:text-green-900 disabled:opacity-50"
                              title="Approve"
                            >
                              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                              </svg>
                            </button>
                            <button
                              onClick={() => handleReject(version.id)}
                              disabled={actionLoading === version.id}
                              className="text-red-600 hover:text-red-900 disabled:opacity-50"
                              title="Reject"
                            >
                              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                              </svg>
                            </button>
                          </>
                        ) : null}
                        
                        {version.status === 'APPROVED' && version.version_number !== 1 ? (
                          <button
                            onClick={() => handleRollback(version.id, version.version_label)}
                            disabled={actionLoading === version.id}
                            className="text-orange-600 hover:text-orange-900 disabled:opacity-50"
                            title="Rollback"
                          >
                            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 10h10a8 8 0 018 8v2M3 10l6 6m-6-6l6-6" />
                            </svg>
                          </button>
                        ) : null}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Compare Modal */}
      {showCompareModal && (
        <CompareModal
          versions={versions}
          onClose={() => setShowCompareModal(false)}
          onCompare={handleCompare}
        />
      )}
    </div>
  );
}

export default function VersionHistoryPage() {
  return (
    <ProtectedRoute>
      <VersionHistoryContent />
    </ProtectedRoute>
  );
}
