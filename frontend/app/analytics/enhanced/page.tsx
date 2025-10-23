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
  const [costSummary, setCostSummary] = useState<any>(null);
  const [costTrends, setCostTrends] = useState<any>(null);
  const [budgetTracking, setBudgetTracking] = useState<any>(null);
  const [costByCategory, setCostByCategory] = useState<any>(null);
  const [predictions, setPredictions] = useState<any>(null);
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

      // Fetch cost analytics
      const costSummaryRes = await fetch(`${baseUrl}/cost-summary`, { headers });
      if (costSummaryRes.ok) setCostSummary(await costSummaryRes.json());

      const costTrendsRes = await fetch(`${baseUrl}/cost-trends?months=${timeRange}`, { headers });
      if (costTrendsRes.ok) setCostTrends(await costTrendsRes.json());

      const budgetTrackingRes = await fetch(`${baseUrl}/budget-tracking`, { headers });
      if (budgetTrackingRes.ok) setBudgetTracking(await budgetTrackingRes.json());

      const costByCategoryRes = await fetch(`${baseUrl}/cost-by-category`, { headers });
      if (costByCategoryRes.ok) setCostByCategory(await costByCategoryRes.json());

      // Fetch predictive analytics
      const predictionsRes = await fetch(`${baseUrl}/predictions`, { headers });
      if (predictionsRes.ok) setPredictions(await predictionsRes.json());

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
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
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

          {/* Cost Tracking Section */}
          {costSummary && budgetTracking && (
            <>
              <div className="mb-4 mt-12">
                <h2 className="text-2xl font-bold text-gray-900">Cost Tracking & Budget Management</h2>
                <p className="text-gray-600">Financial insights and budget performance</p>
              </div>

              {/* Cost Metrics */}
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
                <MetricCard
                  title="Total Estimated"
                  value={`$${(costSummary.totals?.estimated || 0).toLocaleString()}`}
                  subtitle="Planned budget"
                  icon="💰"
                  color="blue"
                />
                <MetricCard
                  title="Total Actual"
                  value={`$${(costSummary.totals?.actual || 0).toLocaleString()}`}
                  subtitle="Actual spend"
                  icon="💵"
                  color="green"
                />
                <MetricCard
                  title="Potential NC Cost"
                  value={`$${(costSummary.totals?.potential_nc || 0).toLocaleString()}`}
                  subtitle="Risk exposure"
                  icon="⚠️"
                  color="red"
                />
                <MetricCard
                  title="Budget Variance"
                  value={`${budgetTracking.overall?.total_variance >= 0 ? '+' : ''}$${(budgetTracking.overall?.total_variance || 0).toLocaleString()}`}
                  subtitle={budgetTracking.overall?.total_variance >= 0 ? 'Over budget' : 'Under budget'}
                  icon="📊"
                  color={budgetTracking.overall?.total_variance >= 0 ? 'red' : 'green'}
                />
              </div>

              {/* Cost Distribution */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
                {costSummary && (
                  <DonutChart
                    data={[
                      { name: 'Corrective Actions', value: costSummary.corrective_actions?.actual_cost || 0 },
                      { name: 'Audits', value: costSummary.audits?.actual_cost || 0 },
                      { name: 'Training', value: costSummary.training?.total_cost || 0 },
                      { name: 'Complaints', value: (costSummary.complaints?.resolution_cost || 0) + (costSummary.complaints?.compensation_amount || 0) },
                      { name: 'Management Reviews', value: costSummary.management_reviews?.meeting_cost || 0 }
                    ]}
                    nameKey="name"
                    valueKey="value"
                    title="Cost Distribution by Artifact Type"
                    height={300}
                  />
                )}

                {budgetTracking && (
                  <div className="bg-white p-6 rounded-lg shadow">
                    <h3 className="text-lg font-semibold mb-4">Budget Performance</h3>
                    <div className="space-y-4">
                      <div className="border-b pb-3">
                        <div className="flex justify-between items-center mb-2">
                          <span className="text-sm font-medium text-gray-700">Corrective Actions</span>
                          <span className={`text-sm font-semibold ${budgetTracking.corrective_actions?.variance >= 0 ? 'text-red-600' : 'text-green-600'}`}>
                            {budgetTracking.corrective_actions?.variance >= 0 ? '+' : ''}${(budgetTracking.corrective_actions?.variance || 0).toLocaleString()} 
                            ({budgetTracking.corrective_actions?.variance_percent}%)
                          </span>
                        </div>
                        <div className="w-full bg-gray-200 rounded-full h-2">
                          <div 
                            className={`h-2 rounded-full ${budgetTracking.corrective_actions?.variance >= 0 ? 'bg-red-500' : 'bg-green-500'}`}
                            style={{ width: `${Math.min(100, Math.abs(budgetTracking.corrective_actions?.variance_percent || 0))}%` }}
                          ></div>
                        </div>
                        <div className="flex justify-between text-xs text-gray-500 mt-1">
                          <span>Est: ${(budgetTracking.corrective_actions?.estimated || 0).toLocaleString()}</span>
                          <span>Act: ${(budgetTracking.corrective_actions?.actual || 0).toLocaleString()}</span>
                        </div>
                      </div>

                      <div className="border-b pb-3">
                        <div className="flex justify-between items-center mb-2">
                          <span className="text-sm font-medium text-gray-700">Audits</span>
                          <span className={`text-sm font-semibold ${budgetTracking.audits?.variance >= 0 ? 'text-red-600' : 'text-green-600'}`}>
                            {budgetTracking.audits?.variance >= 0 ? '+' : ''}${(budgetTracking.audits?.variance || 0).toLocaleString()} 
                            ({budgetTracking.audits?.variance_percent}%)
                          </span>
                        </div>
                        <div className="w-full bg-gray-200 rounded-full h-2">
                          <div 
                            className={`h-2 rounded-full ${budgetTracking.audits?.variance >= 0 ? 'bg-red-500' : 'bg-green-500'}`}
                            style={{ width: `${Math.min(100, Math.abs(budgetTracking.audits?.variance_percent || 0))}%` }}
                          ></div>
                        </div>
                        <div className="flex justify-between text-xs text-gray-500 mt-1">
                          <span>Est: ${(budgetTracking.audits?.estimated || 0).toLocaleString()}</span>
                          <span>Act: ${(budgetTracking.audits?.actual || 0).toLocaleString()}</span>
                        </div>
                      </div>

                      <div className="pt-2">
                        <div className="flex justify-between text-sm font-medium">
                          <span>Budget Compliance</span>
                          <span className="text-blue-600">
                            {budgetTracking.corrective_actions?.on_budget_count + budgetTracking.audits?.on_budget_count} / 
                            {budgetTracking.corrective_actions?.on_budget_count + budgetTracking.corrective_actions?.over_budget_count + 
                             budgetTracking.audits?.on_budget_count + budgetTracking.audits?.over_budget_count} items
                          </span>
                        </div>
                      </div>
                    </div>
                  </div>
                )}
              </div>

              {/* Cost Trends */}
              {costTrends && (
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
                  {costTrends.ca_costs && costTrends.ca_costs.length > 0 && (
                    <TrendLineChart
                      data={costTrends.ca_costs}
                      xKey="month"
                      yKeys={[
                        { key: 'estimated', name: 'Estimated', color: COLORS.tertiary },
                        { key: 'actual', name: 'Actual', color: COLORS.danger }
                      ]}
                      title="CA Cost Trends (Estimated vs Actual)"
                      height={300}
                    />
                  )}

                  {costTrends.training_costs && costTrends.training_costs.length > 0 && (
                    <TrendAreaChart
                      data={costTrends.training_costs}
                      xKey="month"
                      yKeys={[
                        { key: 'cost', name: 'Training Cost', color: COLORS.purple }
                      ]}
                      title="Training Cost Trends"
                      height={300}
                    />
                  )}
                </div>
              )}

              {/* Cost by Category */}
              {costByCategory && (
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
                  {costByCategory.nc_by_category && costByCategory.nc_by_category.length > 0 && (
                    <TrendBarChart
                      data={costByCategory.nc_by_category}
                      xKey="category"
                      yKeys={[
                        { key: 'cost', name: 'Potential Cost', color: COLORS.danger }
                      ]}
                      title="NC Potential Cost by Category"
                      height={300}
                    />
                  )}

                  {costByCategory.ca_by_type && costByCategory.ca_by_type.length > 0 && (
                    <TrendBarChart
                      data={costByCategory.ca_by_type}
                      xKey="type"
                      yKeys={[
                        { key: 'cost', name: 'Actual Cost', color: COLORS.tertiary }
                      ]}
                      title="CA Actual Cost by Type"
                      height={300}
                    />
                  )}
                </div>
              )}
            </>
          )}

          {/* Predictive Analytics Section */}
          {predictions && (
            <>
              <div className="mb-4 mt-12">
                <h2 className="text-2xl font-bold text-gray-900">Predictive Analytics & Risk Assessment</h2>
                <p className="text-gray-600">AI-powered forecasting and risk insights</p>
              </div>

              {/* Risk Score Card */}
              <div className="mb-8">
                <div className="bg-white p-8 rounded-lg shadow-lg border-l-4" style={{
                  borderLeftColor: predictions.risk_assessment?.level === 'high' ? '#EF4444' : 
                                    predictions.risk_assessment?.level === 'medium' ? '#F59E0B' : '#10B981'
                }}>
                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className="text-lg font-semibold text-gray-700 mb-2">System Risk Score</h3>
                      <div className="flex items-baseline gap-4">
                        <div className="text-5xl font-bold" style={{
                          color: predictions.risk_assessment?.level === 'high' ? '#EF4444' : 
                                 predictions.risk_assessment?.level === 'medium' ? '#F59E0B' : '#10B981'
                        }}>
                          {predictions.risk_assessment?.score || 0}
                        </div>
                        <div className="text-xl text-gray-500">/ 100</div>
                      </div>
                      <div className="mt-2">
                        <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${
                          predictions.risk_assessment?.level === 'high' ? 'bg-red-100 text-red-800' :
                          predictions.risk_assessment?.level === 'medium' ? 'bg-yellow-100 text-yellow-800' :
                          'bg-green-100 text-green-800'
                        }`}>
                          {predictions.risk_assessment?.level?.toUpperCase()} RISK
                        </span>
                      </div>
                    </div>
                    <div className="text-6xl">
                      {predictions.risk_assessment?.level === 'high' ? '🔴' : 
                       predictions.risk_assessment?.level === 'medium' ? '🟡' : '🟢'}
                    </div>
                  </div>
                  
                  <div className="mt-6 pt-6 border-t">
                    <h4 className="text-sm font-semibold text-gray-700 mb-3">Risk Factors:</h4>
                    {predictions.risk_assessment?.factors && predictions.risk_assessment.factors.length > 0 ? (
                      <ul className="space-y-2">
                        {predictions.risk_assessment.factors.map((factor: string, idx: number) => (
                          <li key={idx} className="flex items-start gap-2 text-sm text-gray-600">
                            <span className="text-red-500 mt-1">⚠️</span>
                            <span>{factor}</span>
                          </li>
                        ))}
                      </ul>
                    ) : (
                      <p className="text-sm text-green-600">✓ No significant risk factors identified</p>
                    )}
                  </div>

                  <div className="mt-6 pt-6 border-t">
                    <h4 className="text-sm font-semibold text-gray-700 mb-2">Recommendation:</h4>
                    <p className="text-sm text-gray-600">{predictions.risk_assessment?.recommendation}</p>
                  </div>
                </div>
              </div>

              {/* NC Forecast */}
              {predictions.nc_forecast && (
                <div className="mb-8">
                  <TrendLineChart
                    data={[
                      ...predictions.nc_forecast.historical.map((d: any) => ({ ...d, type: 'historical' })),
                      ...predictions.nc_forecast.predictions.map((d: any) => ({ 
                        month: d.month, 
                        count: d.predicted_count,
                        type: 'forecast'
                      }))
                    ]}
                    xKey="month"
                    yKeys={[
                      { key: 'count', name: 'NC Count (Historical & Forecast)', color: COLORS.primary }
                    ]}
                    title="NC Trend Forecast (Next 3 Months)"
                    height={300}
                  />
                  {predictions.nc_forecast.predictions.length > 0 && (
                    <div className="mt-2 text-sm text-gray-600 bg-blue-50 p-3 rounded">
                      <span className="font-medium">📊 Forecast:</span> Expected{' '}
                      {predictions.nc_forecast.predictions.map((p: any, idx: number) => (
                        <span key={idx}>
                          {p.predicted_count} NC{p.predicted_count !== 1 ? 's' : ''} in {p.month}
                          {idx < predictions.nc_forecast.predictions.length - 1 ? ', ' : ''}
                        </span>
                      ))}
                    </div>
                  )}
                </div>
              )}

              {/* CA Completion Predictions */}
              {predictions.ca_predictions && predictions.ca_predictions.length > 0 && (
                <div className="bg-white p-6 rounded-lg shadow mb-8">
                  <h3 className="text-lg font-semibold mb-4">Corrective Action Completion Predictions</h3>
                  <div className="overflow-x-auto">
                    <table className="min-w-full divide-y divide-gray-200">
                      <thead className="bg-gray-50">
                        <tr>
                          <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">CA Number</th>
                          <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Title</th>
                          <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Target Date</th>
                          <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Predicted</th>
                          <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Progress</th>
                          <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                        </tr>
                      </thead>
                      <tbody className="bg-white divide-y divide-gray-200">
                        {predictions.ca_predictions.map((ca: any) => (
                          <tr key={ca.ca_id}>
                            <td className="px-4 py-3 text-sm font-medium text-gray-900">{ca.ca_number}</td>
                            <td className="px-4 py-3 text-sm text-gray-600">{ca.title}</td>
                            <td className="px-4 py-3 text-sm text-gray-600">{ca.target_date}</td>
                            <td className="px-4 py-3 text-sm text-gray-600">{ca.predicted_completion_date}</td>
                            <td className="px-4 py-3 text-sm">
                              <div className="flex items-center gap-2">
                                <div className="flex-1 bg-gray-200 rounded-full h-2 w-20">
                                  <div 
                                    className="bg-blue-600 h-2 rounded-full"
                                    style={{ width: `${ca.progress_percent}%` }}
                                  ></div>
                                </div>
                                <span className="text-xs text-gray-600">{ca.progress_percent}%</span>
                              </div>
                            </td>
                            <td className="px-4 py-3 text-sm">
                              <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${
                                ca.on_track ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                              }`}>
                                {ca.on_track ? '✓ On Track' : '⚠ At Risk'}
                              </span>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}
            </>
          )}
        </div>
      </div>
    </ProtectedRoute>
  );
}
