/**
 * Enhanced Analytics Dashboard
 * Phase 4.5: Advanced Analytics with Trend Charts and Visualizations
 */

'use client';

import { useState, useEffect } from 'react';
import { ProtectedRoute } from '@/components/ProtectedRoute';
import {
  TrendLineChart,
  TrendBarChart,
  TrendAreaChart,
  DonutChart,
  MetricCard,
  COLORS
} from '@/components/ChartComponents';

export default function EnhancedAnalyticsPage() {
  const [performanceMetrics, setPerformanceMetrics] = useState<any>(null);
  const [ncTrends, setNcTrends] = useState<any[]>([]);
  const [caTrends, setCaTrends] = useState<any[]>([]);
  const [auditTrends, setAuditTrends] = useState<any[]>([]);
  const [severityData, setSeverityData] = useState<any>(null);
  const [categoryData, setCategoryData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [timeRange, setTimeRange] = useState<number>(12); // months

  useEffect(() => {
    fetchAllAnalytics();
  }, [timeRange]);

  const fetchAllAnalytics = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('access_token');
      const headers = { 'Authorization': `Bearer ${token}` };
      const baseUrl = 'http://localhost:8889/api/artifacts/analytics';

      // Fetch performance metrics
      const metricsRes = await fetch(`${baseUrl}/performance-metrics`, { headers });
      if (metricsRes.ok) setPerformanceMetrics(await metricsRes.json());

      // Fetch NC trends
      const ncTrendsRes = await fetch(`${baseUrl}/trends/nc-by-month?months=${timeRange}`, { headers });
      if (ncTrendsRes.ok) {
        const data = await ncTrendsRes.json();
        setNcTrends(data.trends);
      }

      // Fetch CA trends
      const caTrendsRes = await fetch(`${baseUrl}/trends/ca-by-month?months=${timeRange}`, { headers });
      if (caTrendsRes.ok) {
        const data = await caTrendsRes.json();
        setCaTrends(data.trends);
      }

      // Fetch audit trends
      const auditTrendsRes = await fetch(`${baseUrl}/trends/audits-by-quarter?years=2`, { headers });
      if (auditTrendsRes.ok) {
        const data = await auditTrendsRes.json();
        setAuditTrends(data.trends);
      }

      // Fetch severity distribution
      const severityRes = await fetch(`${baseUrl}/severity-distribution`, { headers });
      if (severityRes.ok) setSeverityData(await severityRes.json());

      // Fetch category breakdown
      const categoryRes = await fetch(`${baseUrl}/category-breakdown`, { headers });
      if (categoryRes.ok) setCategoryData(await categoryRes.json());

    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load analytics');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <ProtectedRoute>
        <div className="flex justify-center items-center min-h-screen bg-gray-50">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
            <p className="mt-4 text-gray-600">Loading analytics...</p>
          </div>
        </div>
      </ProtectedRoute>
    );
  }

  if (error) {
    return (
      <ProtectedRoute>
        <div className="flex justify-center items-center min-h-screen bg-gray-50">
          <div className="text-center">
            <div className="text-red-600 text-xl mb-4">⚠️ Error</div>
            <p className="text-gray-600">{error}</p>
            <button
              onClick={() => window.location.reload()}
              className="mt-4 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
            >
              Retry
            </button>
          </div>
        </div>
      </ProtectedRoute>
    );
  }

  return (
    <ProtectedRoute>
      <div className="min-h-screen bg-gray-50 py-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          {/* Header */}
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-gray-900">Analytics Dashboard</h1>
            <p className="mt-2 text-gray-600">Comprehensive insights into your ISO management system</p>
            
            {/* Time Range Selector */}
            <div className="mt-4 flex items-center gap-2">
              <label className="text-sm font-medium text-gray-700">Time Range:</label>
              <select
                value={timeRange}
                onChange={(e) => setTimeRange(Number(e.target.value))}
                className="px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500 text-sm"
              >
                <option value={3}>Last 3 Months</option>
                <option value={6}>Last 6 Months</option>
                <option value={12}>Last 12 Months</option>
                <option value={24}>Last 24 Months</option>
              </select>
            </div>
          </div>

          {/* Performance Metrics Grid */}
          {performanceMetrics && (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
              <MetricCard
                title="Non-Conformities"
                value={performanceMetrics.nc.total}
                subtitle={`${performanceMetrics.nc.open} Open`}
                trend={{
                  value: performanceMetrics.nc.closure_rate,
                  isPositive: performanceMetrics.nc.closure_rate > 50
                }}
                icon={
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                  </svg>
                }
                color="red"
              />
              
              <MetricCard
                title="Corrective Actions"
                value={performanceMetrics.ca.total}
                subtitle={`${performanceMetrics.ca.effective} Effective`}
                trend={{
                  value: performanceMetrics.ca.effectiveness_rate,
                  isPositive: performanceMetrics.ca.effectiveness_rate > 70
                }}
                icon={
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                }
                color="green"
              />
              
              <MetricCard
                title="Internal Audits"
                value={performanceMetrics.audits.total}
                subtitle={`${performanceMetrics.audits.completed} Completed`}
                trend={{
                  value: performanceMetrics.audits.completion_rate,
                  isPositive: performanceMetrics.audits.completion_rate > 80
                }}
                icon={
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                  </svg>
                }
                color="blue"
              />
              
              <MetricCard
                title="Training Records"
                value={performanceMetrics.training.total}
                subtitle={`${performanceMetrics.training.completed} Completed`}
                trend={{
                  value: performanceMetrics.training.completion_rate,
                  isPositive: performanceMetrics.training.completion_rate > 90
                }}
                icon={
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
                  </svg>
                }
                color="purple"
              />
            </div>
          )}

          {/* NC Trends */}
          {ncTrends.length > 0 && (
            <div className="mb-8">
              <TrendAreaChart
                data={ncTrends}
                xKey="month"
                yKeys={[
                  { key: 'count', name: 'Total NCs', color: COLORS.primary },
                  { key: 'open', name: 'Open', color: COLORS.danger },
                  { key: 'closed', name: 'Closed', color: COLORS.secondary }
                ]}
                title="Non-Conformity Trends"
                height={350}
              />
            </div>
          )}

          {/* CA Trends */}
          {caTrends.length > 0 && (
            <div className="mb-8">
              <TrendLineChart
                data={caTrends}
                xKey="month"
                yKeys={[
                  { key: 'count', name: 'Total CAs', color: COLORS.primary },
                  { key: 'completed', name: 'Completed', color: COLORS.secondary },
                  { key: 'effective', name: 'Effective', color: COLORS.tertiary }
                ]}
                title="Corrective Action Trends"
                height={350}
              />
            </div>
          )}

          {/* Audit Trends */}
          {auditTrends.length > 0 && (
            <div className="mb-8">
              <TrendBarChart
                data={auditTrends}
                xKey="quarter"
                yKeys={[
                  { key: 'major_findings', name: 'Major Findings', color: COLORS.danger },
                  { key: 'minor_findings', name: 'Minor Findings', color: COLORS.tertiary }
                ]}
                title="Audit Findings by Quarter"
                height={350}
                stacked={true}
              />
            </div>
          )}

          {/* Severity & Category Distribution */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
            {severityData && severityData.nc_by_severity.length > 0 && (
              <DonutChart
                data={severityData.nc_by_severity}
                nameKey="severity"
                valueKey="count"
                title="NC Distribution by Severity"
                height={300}
              />
            )}
            
            {severityData && severityData.complaints_by_priority.length > 0 && (
              <DonutChart
                data={severityData.complaints_by_priority}
                nameKey="priority"
                valueKey="count"
                title="Complaints by Priority"
                height={300}
              />
            )}
          </div>

          {/* Category Breakdown */}
          {categoryData && (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
              {categoryData.nc_by_category.length > 0 && (
                <TrendBarChart
                  data={categoryData.nc_by_category}
                  xKey="category"
                  yKeys={[
                    { key: 'count', name: 'Count', color: COLORS.primary }
                  ]}
                  title="Top NC Categories"
                  height={300}
                />
              )}
              
              {categoryData.ca_by_type.length > 0 && (
                <TrendBarChart
                  data={categoryData.ca_by_type}
                  xKey="type"
                  yKeys={[
                    { key: 'count', name: 'Count', color: COLORS.secondary }
                  ]}
                  title="Top CA Types"
                  height={300}
                />
              )}
            </div>
          )}
        </div>
      </div>
    </ProtectedRoute>
  );
}
