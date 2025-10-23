'use client';

import { useState, useEffect } from 'react';

interface NCStatistics {
  total: number;
  by_status: Record<string, number>;
  by_severity: Record<string, number>;
  by_category: Record<string, number>;
  open_rate: number;
  closure_rate: number;
}

interface CAEffectiveness {
  total_verified: number;
  effective: number;
  not_effective: number;
  effectiveness_rate: number;
}

interface AuditSummary {
  total_audits: number;
  completed: number;
  in_progress: number;
  planned: number;
  total_major_findings: number;
  total_minor_findings: number;
  completion_rate: number;
}

export default function AnalyticsPage() {
  const [ncStats, setNcStats] = useState<NCStatistics | null>(null);
  const [caEffectiveness, setCaEffectiveness] = useState<CAEffectiveness | null>(null);
  const [auditSummary, setAuditSummary] = useState<AuditSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchAnalytics();
  }, []);

  const fetchAnalytics = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('access_token');
      const headers = { 'Authorization': `Bearer ${token}` };

      // Fetch NC Statistics
      const ncResponse = await fetch('http://localhost:8889/api/artifacts/analytics/nc-statistics', {
        headers,
      });
      if (ncResponse.ok) {
        setNcStats(await ncResponse.json());
      }

      // Fetch CA Effectiveness
      const caResponse = await fetch('http://localhost:8889/api/artifacts/analytics/ca-effectiveness', {
        headers,
      });
      if (caResponse.ok) {
        setCaEffectiveness(await caResponse.json());
      }

      // Fetch Audit Summary
      const auditResponse = await fetch('http://localhost:8889/api/artifacts/analytics/audit-summary', {
        headers,
      });
      if (auditResponse.ok) {
        setAuditSummary(await auditResponse.json());
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load analytics');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center min-h-screen">
        <div className="text-lg">Loading analytics...</div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Analytics Dashboard</h1>
        <p className="text-gray-600">Compliance metrics and performance indicators</p>
      </div>

      {error && (
        <div className="mb-4 bg-red-50 border border-red-300 text-red-800 px-4 py-3 rounded">
          {error}
        </div>
      )}

      {/* Non-Conformities Section */}
      {ncStats && (
        <div className="mb-8">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Non-Conformities Overview</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
            <div className="bg-white rounded-lg shadow p-6">
              <div className="text-sm text-gray-600 mb-1">Total NCs</div>
              <div className="text-3xl font-bold text-gray-900">{ncStats.total}</div>
            </div>
            <div className="bg-white rounded-lg shadow p-6">
              <div className="text-sm text-gray-600 mb-1">Open Rate</div>
              <div className="text-3xl font-bold text-blue-600">
                {(ncStats.open_rate * 100).toFixed(1)}%
              </div>
            </div>
            <div className="bg-white rounded-lg shadow p-6">
              <div className="text-sm text-gray-600 mb-1">Closure Rate</div>
              <div className="text-3xl font-bold text-green-600">
                {(ncStats.closure_rate * 100).toFixed(1)}%
              </div>
            </div>
            <div className="bg-white rounded-lg shadow p-6">
              <div className="text-sm text-gray-600 mb-1">Critical NCs</div>
              <div className="text-3xl font-bold text-red-600">
                {ncStats.by_severity.critical || 0}
              </div>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* By Status */}
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Status Distribution</h3>
              <div className="space-y-3">
                {Object.entries(ncStats.by_status).map(([status, count]) => (
                  <div key={status} className="flex justify-between items-center">
                    <span className="text-sm text-gray-600 capitalize">{status.replace('_', ' ')}</span>
                    <div className="flex items-center gap-2">
                      <div className="w-32 bg-gray-200 rounded-full h-2">
                        <div
                          className="bg-blue-600 h-2 rounded-full"
                          style={{ width: `${(count / ncStats.total) * 100}%` }}
                        />
                      </div>
                      <span className="text-sm font-medium text-gray-900 w-12 text-right">{count}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* By Severity */}
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Severity Distribution</h3>
              <div className="space-y-3">
                {Object.entries(ncStats.by_severity).map(([severity, count]) => {
                  const color = severity === 'critical' ? 'bg-red-600' : severity === 'major' ? 'bg-orange-600' : 'bg-yellow-600';
                  return (
                    <div key={severity} className="flex justify-between items-center">
                      <span className="text-sm text-gray-600 capitalize">{severity}</span>
                      <div className="flex items-center gap-2">
                        <div className="w-32 bg-gray-200 rounded-full h-2">
                          <div
                            className={`${color} h-2 rounded-full`}
                            style={{ width: `${(count / ncStats.total) * 100}%` }}
                          />
                        </div>
                        <span className="text-sm font-medium text-gray-900 w-12 text-right">{count}</span>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Corrective Actions Section */}
      {caEffectiveness && (
        <div className="mb-8">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Corrective Actions Effectiveness</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="bg-white rounded-lg shadow p-6">
              <div className="text-sm text-gray-600 mb-1">Total Verified</div>
              <div className="text-3xl font-bold text-gray-900">{caEffectiveness.total_verified}</div>
            </div>
            <div className="bg-white rounded-lg shadow p-6">
              <div className="text-sm text-gray-600 mb-1">Effective</div>
              <div className="text-3xl font-bold text-green-600">{caEffectiveness.effective}</div>
            </div>
            <div className="bg-white rounded-lg shadow p-6">
              <div className="text-sm text-gray-600 mb-1">Not Effective</div>
              <div className="text-3xl font-bold text-red-600">{caEffectiveness.not_effective}</div>
            </div>
            <div className="bg-white rounded-lg shadow p-6">
              <div className="text-sm text-gray-600 mb-1">Effectiveness Rate</div>
              <div className="text-3xl font-bold text-emerald-600">
                {(caEffectiveness.effectiveness_rate * 100).toFixed(1)}%
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Audit Summary Section */}
      {auditSummary && (
        <div className="mb-8">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Internal Audits Summary</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
            <div className="bg-white rounded-lg shadow p-6">
              <div className="text-sm text-gray-600 mb-1">Total Audits</div>
              <div className="text-3xl font-bold text-gray-900">{auditSummary.total_audits}</div>
            </div>
            <div className="bg-white rounded-lg shadow p-6">
              <div className="text-sm text-gray-600 mb-1">Completion Rate</div>
              <div className="text-3xl font-bold text-blue-600">
                {(auditSummary.completion_rate * 100).toFixed(1)}%
              </div>
            </div>
            <div className="bg-white rounded-lg shadow p-6">
              <div className="text-sm text-gray-600 mb-1">Major Findings</div>
              <div className="text-3xl font-bold text-red-600">{auditSummary.total_major_findings}</div>
            </div>
            <div className="bg-white rounded-lg shadow p-6">
              <div className="text-sm text-gray-600 mb-1">Minor Findings</div>
              <div className="text-3xl font-bold text-orange-600">{auditSummary.total_minor_findings}</div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Audit Status Breakdown</h3>
            <div className="grid grid-cols-3 gap-4">
              <div className="text-center">
                <div className="text-2xl font-bold text-blue-600">{auditSummary.planned}</div>
                <div className="text-sm text-gray-600">Planned</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-purple-600">{auditSummary.in_progress}</div>
                <div className="text-sm text-gray-600">In Progress</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-green-600">{auditSummary.completed}</div>
                <div className="text-sm text-gray-600">Completed</div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Compliance Score Card */}
      <div className="bg-gradient-to-r from-blue-600 to-indigo-700 rounded-lg shadow-lg p-8 text-white">
        <h2 className="text-2xl font-bold mb-2">Overall Compliance Score</h2>
        <p className="text-blue-100 mb-4">Based on NC closure rate, CA effectiveness, and audit completion</p>
        <div className="flex items-baseline gap-2">
          <div className="text-6xl font-bold">
            {ncStats && caEffectiveness && auditSummary
              ? Math.round(
                  (ncStats.closure_rate * 0.4 +
                    caEffectiveness.effectiveness_rate * 0.3 +
                    auditSummary.completion_rate * 0.3) *
                    100
                )
              : '--'}
          </div>
          <div className="text-2xl text-blue-100">/ 100</div>
        </div>
      </div>
    </div>
  );
}
