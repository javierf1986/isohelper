/**
 * Version Comparison Page
 * Side-by-side diff view for comparing two versions
 */

'use client';

import { useRouter, useParams, useSearchParams } from 'next/navigation';
import { ProtectedRoute } from '@/components/ProtectedRoute';
import { useState, useEffect } from 'react';

interface ComparisonData {
  version1: {
    id: string;
    version_number: number;
    version_label: string;
    created_at: string;
  };
  version2: {
    id: string;
    version_number: number;
    version_label: string;
    created_at: string;
  };
  diff: {
    changes: Array<{
      type: string;
      line: number;
      content: string;
      old_line?: number;
      new_line?: number;
    }>;
  };
}

function VersionCompareContent() {
  const router = useRouter();
  const params = useParams();
  const searchParams = useSearchParams();
  const documentId = params.id as string;
  const version1Id = searchParams.get('v1');
  const version2Id = searchParams.get('v2');
  
  const [comparison, setComparison] = useState<ComparisonData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!version1Id || !version2Id) {
      setError('Both version IDs are required');
      setLoading(false);
      return;
    }

    const fetchComparison = async () => {
      try {
        const token = localStorage.getItem('token');
        const response = await fetch(`http://localhost:8889/api/v1/versions/compare`, {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            version_id_1: version1Id,
            version_id_2: version2Id,
          }),
        });

        if (!response.ok) throw new Error('Failed to compare versions');
        
        const data = await response.json();
        setComparison(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'An error occurred');
      } finally {
        setLoading(false);
      }
    };

    fetchComparison();
  }, [version1Id, version2Id]);

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Comparing versions...</p>
        </div>
      </div>
    );
  }

  if (error || !comparison) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center max-w-md">
          <svg className="mx-auto h-12 w-12 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
          <h2 className="mt-4 text-xl font-bold text-gray-900">Comparison Failed</h2>
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

  const changes = comparison.diff?.changes || [];
  const addedCount = changes.filter(c => c.type === 'added').length;
  const removedCount = changes.filter(c => c.type === 'removed').length;
  const modifiedCount = changes.filter(c => c.type === 'modified').length;

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
          
          <h1 className="text-3xl font-bold text-gray-900">Version Comparison</h1>
          <p className="mt-2 text-gray-600">
            Comparing {comparison.version1.version_label} with {comparison.version2.version_label}
          </p>
        </div>

        {/* Version Info Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-gray-900">Version 1</h3>
              <span className="px-3 py-1 bg-blue-100 text-blue-800 text-sm font-semibold rounded-full">
                {comparison.version1.version_label}
              </span>
            </div>
            <div className="space-y-2 text-sm">
              <div>
                <span className="text-gray-500">Version Number:</span>
                <span className="ml-2 font-medium">{comparison.version1.version_number}</span>
              </div>
              <div>
                <span className="text-gray-500">Created:</span>
                <span className="ml-2 font-medium">{new Date(comparison.version1.created_at).toLocaleString()}</span>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-gray-900">Version 2</h3>
              <span className="px-3 py-1 bg-green-100 text-green-800 text-sm font-semibold rounded-full">
                {comparison.version2.version_label}
              </span>
            </div>
            <div className="space-y-2 text-sm">
              <div>
                <span className="text-gray-500">Version Number:</span>
                <span className="ml-2 font-medium">{comparison.version2.version_number}</span>
              </div>
              <div>
                <span className="text-gray-500">Created:</span>
                <span className="ml-2 font-medium">{new Date(comparison.version2.created_at).toLocaleString()}</span>
              </div>
            </div>
          </div>
        </div>

        {/* Change Statistics */}
        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Change Summary</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="flex items-center gap-3 p-3 bg-green-50 rounded-lg">
              <div className="flex-shrink-0 w-10 h-10 bg-green-100 rounded-full flex items-center justify-center">
                <svg className="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                </svg>
              </div>
              <div>
                <p className="text-2xl font-bold text-green-600">{addedCount}</p>
                <p className="text-sm text-green-700">Lines Added</p>
              </div>
            </div>

            <div className="flex items-center gap-3 p-3 bg-red-50 rounded-lg">
              <div className="flex-shrink-0 w-10 h-10 bg-red-100 rounded-full flex items-center justify-center">
                <svg className="w-6 h-6 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 12H4" />
                </svg>
              </div>
              <div>
                <p className="text-2xl font-bold text-red-600">{removedCount}</p>
                <p className="text-sm text-red-700">Lines Removed</p>
              </div>
            </div>

            <div className="flex items-center gap-3 p-3 bg-yellow-50 rounded-lg">
              <div className="flex-shrink-0 w-10 h-10 bg-yellow-100 rounded-full flex items-center justify-center">
                <svg className="w-6 h-6 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 8h10M7 12h4m1 8l-4-4H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-3l-4 4z" />
                </svg>
              </div>
              <div>
                <p className="text-2xl font-bold text-yellow-600">{modifiedCount}</p>
                <p className="text-sm text-yellow-700">Lines Modified</p>
              </div>
            </div>
          </div>
        </div>

        {/* Diff View */}
        <div className="bg-white rounded-lg shadow">
          <div className="px-6 py-4 border-b border-gray-200">
            <h3 className="text-lg font-semibold text-gray-900">Changes</h3>
          </div>
          <div className="p-6">
            {changes.length === 0 ? (
              <div className="text-center py-12">
                <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <h3 className="mt-4 text-lg font-medium text-gray-900">No Differences Found</h3>
                <p className="mt-2 text-gray-500">These versions have identical content.</p>
              </div>
            ) : (
              <div className="space-y-1 font-mono text-sm">
                {changes.map((change, index) => {
                  let bgColor, borderColor, icon, textColor;
                  
                  switch (change.type) {
                    case 'added':
                      bgColor = 'bg-green-50';
                      borderColor = 'border-l-4 border-green-500';
                      icon = '+';
                      textColor = 'text-green-700';
                      break;
                    case 'removed':
                      bgColor = 'bg-red-50';
                      borderColor = 'border-l-4 border-red-500';
                      icon = '-';
                      textColor = 'text-red-700';
                      break;
                    case 'modified':
                      bgColor = 'bg-yellow-50';
                      borderColor = 'border-l-4 border-yellow-500';
                      icon = '~';
                      textColor = 'text-yellow-700';
                      break;
                    default:
                      bgColor = 'bg-gray-50';
                      borderColor = 'border-l-4 border-gray-300';
                      icon = ' ';
                      textColor = 'text-gray-700';
                  }

                  return (
                    <div key={index} className={`p-3 ${bgColor} ${borderColor} flex items-start`}>
                      <span className={`font-bold mr-3 ${textColor} select-none`}>{icon}</span>
                      <div className="flex-1 flex items-start gap-4">
                        <span className="text-gray-400 text-xs mt-0.5 w-12 flex-shrink-0">
                          Line {change.line}
                        </span>
                        <span className={`flex-1 whitespace-pre-wrap break-all ${textColor}`}>
                          {change.content}
                        </span>
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        </div>

        {/* Actions */}
        <div className="mt-6 flex justify-end gap-3">
          <button
            onClick={() => router.push(`/documents/${documentId}/versions/${version1Id}`)}
            className="px-4 py-2 text-blue-600 bg-blue-50 rounded-md hover:bg-blue-100"
          >
            View {comparison.version1.version_label}
          </button>
          <button
            onClick={() => router.push(`/documents/${documentId}/versions/${version2Id}`)}
            className="px-4 py-2 text-green-600 bg-green-50 rounded-md hover:bg-green-100"
          >
            View {comparison.version2.version_label}
          </button>
        </div>
      </div>
    </div>
  );
}

export default function VersionComparePage() {
  return (
    <ProtectedRoute>
      <VersionCompareContent />
    </ProtectedRoute>
  );
}
