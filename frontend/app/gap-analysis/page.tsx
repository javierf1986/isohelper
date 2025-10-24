/**
 * Gap Analysis List Page
 * View all gap analyses for the workspace
 */

'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useTranslations } from 'next-intl';
import { ProtectedRoute } from '@/components/ProtectedRoute';

interface Analysis {
  id: string;
  analysis_number: string;
  document_name: string;
  status: string;
  progress_percent: number;
  total_gaps: number;
  critical_gaps: number;
  major_gaps: number;
  compliance_score: number | null;
  created_at: string;
  completed_at: string | null;
}

export default function GapAnalysisListPage() {
  const t = useTranslations();
  const router = useRouter();
  const [analyses, setAnalyses] = useState<Analysis[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchAnalyses();
  }, []);

  const fetchAnalyses = async () => {
    try {
      const token = localStorage.getItem('access_token');
      const workspaceId = localStorage.getItem('workspace_id');
      
      const response = await fetch(
        `http://localhost:8889/api/v1/gap-analysis/?workspace_id=${workspaceId}`,
        {
          headers: { 'Authorization': `Bearer ${token}` }
        }
      );

      if (response.ok) {
        const data = await response.json();
        setAnalyses(data);
      } else {
        setError(t('gapAnalysis.loadError'));
      }
    } catch (err) {
      setError(t('gapAnalysis.loadError'));
    } finally {
      setLoading(false);
    }
  };

  const getStatusBadge = (status: string, progress: number) => {
    const statusColors: any = {
      'pending': 'bg-gray-100 text-gray-800',
      'processing': 'bg-blue-100 text-blue-800',
      'completed': 'bg-green-100 text-green-800',
      'failed': 'bg-red-100 text-red-800'
    };

    return (
      <span className={`px-3 py-1 rounded-full text-xs font-medium ${statusColors[status] || 'bg-gray-100 text-gray-800'}`}>
        {status === 'processing' ? `${t('gapAnalysis.processing')} (${progress}%)` : status.toUpperCase()}
      </span>
    );
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  if (loading) {
    return (
      <ProtectedRoute>
        <div className="flex justify-center items-center min-h-screen">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
        </div>
      </ProtectedRoute>
    );
  }

  return (
    <ProtectedRoute>
      <div className="min-h-screen bg-gray-50 py-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          {/* Header */}
          <div className="mb-8 flex justify-between items-center">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">{t('gapAnalysis.title')}</h1>
              <p className="mt-2 text-gray-600">{t('gapAnalysis.subtitle')}</p>
            </div>
            <button
              onClick={() => router.push('/gap-analysis/upload')}
              className="px-6 py-3 bg-blue-600 text-white rounded-md hover:bg-blue-700 font-medium"
            >
              + {t('gapAnalysis.newAnalysis')}
            </button>
          </div>

          {/* Error Message */}
          {error && (
            <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-md">
              <p className="text-red-800">{error}</p>
            </div>
          )}

          {/* Analyses Grid */}
          {analyses.length === 0 ? (
            <div className="bg-white rounded-lg shadow-lg p-12 text-center">
              <div className="text-6xl mb-4">📊</div>
              <h2 className="text-2xl font-semibold text-gray-900 mb-2">{t('gapAnalysis.noAnalyses')}</h2>
              <p className="text-gray-600 mb-6">
                {t('gapAnalysis.noAnalysesDesc')}
              </p>
              <button
                onClick={() => router.push('/gap-analysis/upload')}
                className="px-6 py-3 bg-blue-600 text-white rounded-md hover:bg-blue-700 font-medium"
              >
                {t('gapAnalysis.createFirst')}
              </button>
            </div>
          ) : (
            <div className="grid grid-cols-1 gap-6">
              {analyses.map((analysis) => (
                <div
                  key={analysis.id}
                  className="bg-white rounded-lg shadow hover:shadow-lg transition-shadow p-6 cursor-pointer"
                  onClick={() => router.push(`/gap-analysis/${analysis.id}`)}
                >
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-2">
                        <h3 className="text-lg font-semibold text-gray-900">
                          {analysis.analysis_number}
                        </h3>
                        {getStatusBadge(analysis.status, analysis.progress_percent)}
                      </div>
                      <p className="text-gray-600">{analysis.document_name}</p>
                      <p className="text-sm text-gray-500 mt-1">
                        {t('gapAnalysis.created')}: {formatDate(analysis.created_at)}
                      </p>
                    </div>

                    {analysis.status === 'completed' && analysis.compliance_score !== null && (
                      <div className="text-right">
                        <div className="text-3xl font-bold" style={{
                          color: analysis.compliance_score >= 80 ? '#10B981' :
                                 analysis.compliance_score >= 60 ? '#F59E0B' : '#EF4444'
                        }}>
                          {analysis.compliance_score.toFixed(0)}%
                        </div>
                        <p className="text-sm text-gray-500">{t('gapAnalysis.compliance')}</p>
                      </div>
                    )}
                  </div>

                  {analysis.status === 'completed' && (
                    <div className="grid grid-cols-4 gap-4 pt-4 border-t">
                      <div>
                        <p className="text-2xl font-bold text-gray-900">{analysis.total_gaps}</p>
                        <p className="text-xs text-gray-500">{t('gapAnalysis.totalGaps')}</p>
                      </div>
                      <div>
                        <p className="text-2xl font-bold text-red-600">{analysis.critical_gaps}</p>
                        <p className="text-xs text-gray-500">{t('gapAnalysis.critical')}</p>
                      </div>
                      <div>
                        <p className="text-2xl font-bold text-orange-600">{analysis.major_gaps}</p>
                        <p className="text-xs text-gray-500">{t('gapAnalysis.major')}</p>
                      </div>
                      <div>
                        <p className="text-2xl font-bold text-blue-600">
                          {analysis.total_gaps - analysis.critical_gaps - analysis.major_gaps}
                        </p>
                        <p className="text-xs text-gray-500">{t('gapAnalysis.minor')}</p>
                      </div>
                    </div>
                  )}

                  {analysis.status === 'processing' && (
                    <div className="pt-4 border-t">
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div
                          className="bg-blue-600 h-2 rounded-full transition-all"
                          style={{ width: `${analysis.progress_percent}%` }}
                        ></div>
                      </div>
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </ProtectedRoute>
  );
}
