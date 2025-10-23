/**
 * Version Detail Page
 * Display specific version content and audit trail
 */

'use client';

import { useRouter, useParams } from 'next/navigation';
import { ProtectedRoute } from '@/components/ProtectedRoute';
import { useState, useEffect } from 'react';

interface Version {
  id: string;
  document_id: string;
  version_number: number;
  version_label: string;
  title: string;
  content: string;
  status: string;
  change_type: string;
  change_summary: string | null;
  content_hash: string;
  content_diff: any;
  created_by: string;
  approved_by: string | null;
  approved_at: string | null;
  created_at: string;
  updated_at: string;
  iso_standard_id: string | null;
}

interface AuditLog {
  id: string;
  version_id: string;
  action: string;
  action_description: string | null;
  actor_id: string;
  changes_made: any;
  metadata: any;
  created_at: string;
}

function VersionDetailContent() {
  const router = useRouter();
  const params = useParams();
  const documentId = params.id as string;
  const versionId = params.versionId as string;
  
  const [version, setVersion] = useState<Version | null>(null);
  const [auditLogs, setAuditLogs] = useState<AuditLog[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'content' | 'diff' | 'audit'>('content');

  useEffect(() => {
    const fetchData = async () => {
      try {
        const token = localStorage.getItem('token');
        
        // Fetch version details
        const versionResponse = await fetch(`http://localhost:8889/api/v1/versions/${versionId}`, {
          headers: { 'Authorization': `Bearer ${token}` },
        });
        if (!versionResponse.ok) throw new Error('Failed to fetch version');
        const versionData = await versionResponse.json();
        setVersion(versionData);

        // Fetch audit trail
        const auditResponse = await fetch(`http://localhost:8889/api/v1/versions/${versionId}/audit-trail`, {
          headers: { 'Authorization': `Bearer ${token}` },
        });
        if (!auditResponse.ok) throw new Error('Failed to fetch audit trail');
        const auditData = await auditResponse.json();
        setAuditLogs(auditData);
        
      } catch (err) {
        setError(err instanceof Error ? err.message : 'An error occurred');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [versionId]);

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

  const renderDiff = () => {
    if (!version?.content_diff) {
      return (
        <div className="text-center py-8 text-gray-500">
          <p>No diff available for this version</p>
          <p className="text-sm mt-2">(This is the first version of the document)</p>
        </div>
      );
    }

    const diff = version.content_diff;
    const changes = diff.changes || [];

    if (changes.length === 0) {
      return <div className="text-center py-8 text-gray-500">No changes detected</div>;
    }

    return (
      <div className="space-y-2">
        {changes.map((change: any, index: number) => {
          const bgColor = 
            change.type === 'added' ? 'bg-green-50 border-l-4 border-green-500' :
            change.type === 'removed' ? 'bg-red-50 border-l-4 border-red-500' :
            'bg-yellow-50 border-l-4 border-yellow-500';
          
          const icon =
            change.type === 'added' ? '+' :
            change.type === 'removed' ? '-' :
            '~';

          return (
            <div key={index} className={`p-3 ${bgColor} font-mono text-sm`}>
              <span className="font-bold mr-2">{icon}</span>
              <span className="text-gray-600">Line {change.line}:</span>
              <span className="ml-2">{change.content}</span>
            </div>
          );
        })}
      </div>
    );
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading version details...</p>
        </div>
      </div>
    );
  }

  if (error || !version) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center max-w-md">
          <svg className="mx-auto h-12 w-12 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
          <h2 className="mt-4 text-xl font-bold text-gray-900">Version Not Found</h2>
          <p className="mt-2 text-gray-600">{error}</p>
          <button
            onClick={() => router.push(`/documents/${documentId}/versions`)}
            className="mt-6 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
          >
            Back to Version History
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
            onClick={() => router.push(`/documents/${documentId}/versions`)}
            className="flex items-center text-blue-600 hover:text-blue-700 mb-4"
          >
            <svg className="w-5 h-5 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
            Back to Version History
          </button>
          
          <div className="flex justify-between items-start">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">{version.version_label}</h1>
              <p className="mt-2 text-gray-600">{version.title}</p>
            </div>
            
            <div className="flex gap-2">
              <span className={`px-3 py-1 inline-flex text-sm font-semibold rounded-full ${getStatusBadgeColor(version.status)}`}>
                {version.status.replace('_', ' ')}
              </span>
              <span className={`px-3 py-1 inline-flex text-sm font-semibold rounded-full ${getChangeTypeBadgeColor(version.change_type)}`}>
                {version.change_type}
              </span>
            </div>
          </div>
        </div>

        {/* Metadata Card */}
        <div className="bg-white rounded-lg shadow mb-6 p-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div>
              <p className="text-sm text-gray-500">Version Number</p>
              <p className="mt-1 text-lg font-semibold">{version.version_number}</p>
            </div>
            <div>
              <p className="text-sm text-gray-500">Content Hash</p>
              <p className="mt-1 text-sm font-mono">{version.content_hash.substring(0, 16)}...</p>
            </div>
            <div>
              <p className="text-sm text-gray-500">Created</p>
              <p className="mt-1 text-sm">{new Date(version.created_at).toLocaleString()}</p>
            </div>
            {version.change_summary && (
              <div className="md:col-span-3">
                <p className="text-sm text-gray-500">Change Summary</p>
                <p className="mt-1 text-sm">{version.change_summary}</p>
              </div>
            )}
            {version.approved_by && (
              <>
                <div>
                  <p className="text-sm text-gray-500">Approved By</p>
                  <p className="mt-1 text-sm">{version.approved_by}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-500">Approved At</p>
                  <p className="mt-1 text-sm">{version.approved_at ? new Date(version.approved_at).toLocaleString() : 'N/A'}</p>
                </div>
              </>
            )}
          </div>
        </div>

        {/* Tabs */}
        <div className="bg-white rounded-lg shadow">
          <div className="border-b border-gray-200">
            <nav className="flex -mb-px">
              <button
                onClick={() => setActiveTab('content')}
                className={`px-6 py-4 text-sm font-medium border-b-2 ${
                  activeTab === 'content'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                Content
              </button>
              <button
                onClick={() => setActiveTab('diff')}
                className={`px-6 py-4 text-sm font-medium border-b-2 ${
                  activeTab === 'diff'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                Changes
              </button>
              <button
                onClick={() => setActiveTab('audit')}
                className={`px-6 py-4 text-sm font-medium border-b-2 ${
                  activeTab === 'audit'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                Audit Trail ({auditLogs.length})
              </button>
            </nav>
          </div>

          <div className="p-6">
            {activeTab === 'content' && (
              <div className="prose max-w-none">
                <pre className="whitespace-pre-wrap bg-gray-50 p-4 rounded-md text-sm">
                  {version.content}
                </pre>
              </div>
            )}

            {activeTab === 'diff' && renderDiff()}

            {activeTab === 'audit' && (
              <div className="space-y-4">
                {auditLogs.length === 0 ? (
                  <div className="text-center py-8 text-gray-500">No audit logs available</div>
                ) : (
                  auditLogs.map((log) => (
                    <div key={log.id} className="border-l-4 border-blue-500 bg-gray-50 p-4">
                      <div className="flex justify-between items-start">
                        <div>
                          <p className="font-semibold text-gray-900">{log.action}</p>
                          {log.action_description && (
                            <p className="text-sm text-gray-600 mt-1">{log.action_description}</p>
                          )}
                          <p className="text-xs text-gray-500 mt-2">
                            Actor: {log.actor_id} • {new Date(log.created_at).toLocaleString()}
                          </p>
                        </div>
                      </div>
                      {log.changes_made && Object.keys(log.changes_made).length > 0 && (
                        <div className="mt-3 bg-white p-3 rounded text-xs">
                          <p className="font-semibold mb-2">Changes:</p>
                          <pre className="whitespace-pre-wrap">{JSON.stringify(log.changes_made, null, 2)}</pre>
                        </div>
                      )}
                    </div>
                  ))
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default function VersionDetailPage() {
  return (
    <ProtectedRoute>
      <VersionDetailContent />
    </ProtectedRoute>
  );
}
