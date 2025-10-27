'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { 
  Target, 
  Plus, 
  Filter, 
  TrendingUp, 
  Calendar, 
  CheckCircle2, 
  Clock,
  AlertCircle,
  XCircle 
} from 'lucide-react';

interface Objective {
  id: string;
  objective_number: string;
  title: string;
  description: string;
  target_value: string;
  current_value: string;
  status: string;
  progress_percentage: number;
  responsible_person: string;
  department: string;
  target_date: string;
  achieved_date: string | null;
  related_clause: string;
  created_at: string;
  is_active: boolean;
}

interface Analytics {
  total_objectives: number;
  by_status: Record<string, number>;
  achievement_rate: number;
  average_progress: number;
  overdue_count: number;
  by_department: Record<string, number>;
}

export default function ObjectivesPage() {
  const [objectives, setObjectives] = useState<Objective[]>([]);
  const [analytics, setAnalytics] = useState<Analytics | null>(null);
  const [loading, setLoading] = useState(true);
  const [filterStatus, setFilterStatus] = useState<string>('');
  const [filterDepartment, setFilterDepartment] = useState<string>('');

  useEffect(() => {
    fetchObjectives();
    fetchAnalytics();
  }, [filterStatus, filterDepartment]);

  const fetchObjectives = async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      if (filterStatus) params.append('status', filterStatus);
      if (filterDepartment) params.append('department', filterDepartment);
      
      const response = await fetch(`http://localhost:8000/api/v1/objectives?${params.toString()}`);
      const data = await response.json();
      setObjectives(data);
    } catch (error) {
      console.error('Failed to fetch objectives:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchAnalytics = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/v1/objectives/analytics/summary');
      const data = await response.json();
      setAnalytics(data);
    } catch (error) {
      console.error('Failed to fetch analytics:', error);
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'ACHIEVED':
        return <CheckCircle2 className="h-5 w-5 text-green-500" />;
      case 'IN_PROGRESS':
        return <TrendingUp className="h-5 w-5 text-blue-500" />;
      case 'DELAYED':
        return <AlertCircle className="h-5 w-5 text-red-500" />;
      case 'CANCELLED':
        return <XCircle className="h-5 w-5 text-gray-400" />;
      default:
        return <Clock className="h-5 w-5 text-gray-500" />;
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
      case 'CANCELLED':
        return 'bg-gray-100 text-gray-600';
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

  const isOverdue = (targetDate: string, status: string) => {
    if (status === 'ACHIEVED' || status === 'CANCELLED') return false;
    return new Date(targetDate) < new Date();
  };

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Target className="h-8 w-8 text-blue-600" />
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Quality Objectives</h1>
              <p className="text-gray-600 mt-1">ISO 6.2 - Quality objectives and planning</p>
            </div>
          </div>
          <Link
            href="/objectives/new"
            className="flex items-center gap-2 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
          >
            <Plus className="h-5 w-5" />
            New Objective
          </Link>
        </div>
      </div>

      {/* Analytics Cards */}
      {analytics && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4 mb-8">
          <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
            <div className="text-sm text-gray-600 mb-1">Total Objectives</div>
            <div className="text-3xl font-bold text-gray-900">{analytics.total_objectives}</div>
          </div>
          <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
            <div className="text-sm text-gray-600 mb-1">Achievement Rate</div>
            <div className="text-3xl font-bold text-green-600">{analytics.achievement_rate}%</div>
          </div>
          <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
            <div className="text-sm text-gray-600 mb-1">Average Progress</div>
            <div className="text-3xl font-bold text-blue-600">{analytics.average_progress}%</div>
          </div>
          <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
            <div className="text-sm text-gray-600 mb-1">In Progress</div>
            <div className="text-3xl font-bold text-blue-600">{analytics.by_status.IN_PROGRESS || 0}</div>
          </div>
          <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
            <div className="text-sm text-gray-600 mb-1">Overdue</div>
            <div className="text-3xl font-bold text-red-600">{analytics.overdue_count}</div>
          </div>
        </div>
      )}

      {/* Filters */}
      <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-200 mb-6">
        <div className="flex items-center gap-4">
          <Filter className="h-5 w-5 text-gray-500" />
          <select
            value={filterStatus}
            onChange={(e) => setFilterStatus(e.target.value)}
            className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="">All Statuses</option>
            <option value="PLANNED">Planned</option>
            <option value="IN_PROGRESS">In Progress</option>
            <option value="ACHIEVED">Achieved</option>
            <option value="DELAYED">Delayed</option>
            <option value="CANCELLED">Cancelled</option>
          </select>
          <select
            value={filterDepartment}
            onChange={(e) => setFilterDepartment(e.target.value)}
            className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="">All Departments</option>
            {analytics?.by_department && Object.keys(analytics.by_department).map(dept => (
              <option key={dept} value={dept}>{dept}</option>
            ))}
          </select>
          {(filterStatus || filterDepartment) && (
            <button
              onClick={() => {
                setFilterStatus('');
                setFilterDepartment('');
              }}
              className="text-blue-600 hover:text-blue-700 text-sm font-medium"
            >
              Clear Filters
            </button>
          )}
        </div>
      </div>

      {/* Objectives List */}
      {loading ? (
        <div className="flex items-center justify-center h-64">
          <div className="text-gray-500">Loading objectives...</div>
        </div>
      ) : objectives.length === 0 ? (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-12 text-center">
          <Target className="h-16 w-16 text-gray-400 mx-auto mb-4" />
          <h3 className="text-xl font-semibold text-gray-900 mb-2">No objectives found</h3>
          <p className="text-gray-600 mb-6">Create your first quality objective to get started</p>
          <Link
            href="/objectives/new"
            className="inline-flex items-center gap-2 bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700"
          >
            <Plus className="h-5 w-5" />
            Create Objective
          </Link>
        </div>
      ) : (
        <div className="space-y-4">
          {objectives.map((objective) => (
            <Link
              key={objective.id}
              href={`/objectives/${objective.id}`}
              className="block bg-white rounded-lg shadow-sm border border-gray-200 p-6 hover:shadow-md transition-shadow"
            >
              <div className="flex items-start justify-between mb-4">
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-2">
                    {getStatusIcon(objective.status)}
                    <h3 className="text-lg font-semibold text-gray-900">{objective.title}</h3>
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(objective.status)}`}>
                      {objective.status.replace('_', ' ')}
                    </span>
                    {isOverdue(objective.target_date, objective.status) && (
                      <span className="px-2 py-1 rounded-full text-xs font-medium bg-red-100 text-red-800">
                        OVERDUE
                      </span>
                    )}
                  </div>
                  <p className="text-gray-600 text-sm mb-3">{objective.description}</p>
                  <div className="flex items-center gap-6 text-sm text-gray-500">
                    <span className="font-mono">{objective.objective_number}</span>
                    {objective.department && (
                      <span>📂 {objective.department}</span>
                    )}
                    {objective.related_clause && (
                      <span>📋 Clause {objective.related_clause}</span>
                    )}
                    <span className="flex items-center gap-1">
                      <Calendar className="h-4 w-4" />
                      Target: {new Date(objective.target_date).toLocaleDateString()}
                    </span>
                  </div>
                </div>
              </div>

              {/* Progress Bar */}
              <div className="space-y-2">
                <div className="flex items-center justify-between text-sm">
                  <div className="flex items-center gap-2">
                    <span className="text-gray-600">Progress:</span>
                    <span className="font-medium">{objective.current_value || '-'} / {objective.target_value}</span>
                  </div>
                  <span className="font-bold text-gray-900">{objective.progress_percentage}%</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-3">
                  <div
                    className={`h-3 rounded-full transition-all ${getProgressColor(objective.progress_percentage)}`}
                    style={{ width: `${objective.progress_percentage}%` }}
                  />
                </div>
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
