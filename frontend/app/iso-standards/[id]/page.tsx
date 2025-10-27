'use client';

import { useState, useEffect } from 'react';
import { useRouter, useParams } from 'next/navigation';
import { useTranslations } from 'next-intl';

interface Clause {
  id: string;
  clause_number: string;
  title: string;
  content: string;
  is_mandatory: boolean;
}

interface ISOStandardDetail {
  id: string;
  name: string;
  iso_number: string;
  year: number;
  description: string;
  category: string;
  is_active: boolean;
  imported_at: string;
  clauses: Clause[];
  qms_scope_statement?: string;
  qms_exclusions?: string;
  qms_applicability?: string;
  qms_boundaries?: string;
}

export default function ISOStandardDetailPage() {
  const t = useTranslations();
  const router = useRouter();
  const params = useParams();
  const standardId = params?.id as string;

  const [standard, setStandard] = useState<ISOStandardDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [expandedClauses, setExpandedClauses] = useState<Set<string>>(new Set());
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [deleting, setDeleting] = useState(false);
  const [showScopeEditor, setShowScopeEditor] = useState(false);
  const [scopeData, setScopeData] = useState({
    qms_scope_statement: '',
    qms_exclusions: '',
    qms_applicability: '',
    qms_boundaries: ''
  });

  useEffect(() => {
    if (standardId) {
      fetchStandardDetail();
    }
  }, [standardId]);

  const fetchStandardDetail = async () => {
    try {
      const response = await fetch(`http://localhost:8000/api/v1/iso-standards/${standardId}`);

      if (response.ok) {
        const data = await response.json();
        setStandard(data);
        // Initialize scope data
        setScopeData({
          qms_scope_statement: data.qms_scope_statement || '',
          qms_exclusions: data.qms_exclusions || '',
          qms_applicability: data.qms_applicability || '',
          qms_boundaries: data.qms_boundaries || ''
        });
      } else {
        setError('Failed to load ISO standard details');
      }
    } catch (err) {
      setError('Error loading ISO standard details');
      console.error('Error fetching standard detail:', err);
    } finally {
      setLoading(false);
    }
  };

  const toggleClause = (clauseId: string) => {
    const newExpanded = new Set(expandedClauses);
    if (newExpanded.has(clauseId)) {
      newExpanded.delete(clauseId);
    } else {
      newExpanded.add(clauseId);
    }
    setExpandedClauses(newExpanded);
  };

  const handleDelete = async () => {
    if (!standard) return;
    
    setDeleting(true);
    try {
      const response = await fetch(`http://localhost:8000/api/v1/iso-standards/${standardId}`, {
        method: 'DELETE',
      });

      if (response.ok) {
        // Redirect to standards list after successful deletion
        router.push('/iso-standards');
      } else {
        setError('Failed to delete ISO standard');
        setDeleting(false);
      }
    } catch (err) {
      setError('Error deleting ISO standard');
      console.error('Delete error:', err);
      setDeleting(false);
    }
    setShowDeleteConfirm(false);
  };

  const handleScopeUpdate = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const response = await fetch(`http://localhost:8000/api/v1/iso-standards/${standardId}/scope`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(scopeData)
      });

      if (response.ok) {
        setShowScopeEditor(false);
        fetchStandardDetail();
      } else {
        setError('Failed to update QMS scope');
      }
    } catch (err) {
      setError('Error updating QMS scope');
      console.error('Scope update error:', err);
    }
  };

  const getCategoryBadge = (category?: string) => {
    const safeCategory = (category || 'other').toLowerCase();
    
    const colors: any = {
      'quality': 'bg-blue-100 text-blue-800',
      'environmental': 'bg-green-100 text-green-800',
      'security': 'bg-red-100 text-red-800',
      'safety': 'bg-orange-100 text-orange-800',
      'food_safety': 'bg-purple-100 text-purple-800',
      'energy': 'bg-yellow-100 text-yellow-800',
      'other': 'bg-gray-100 text-gray-800'
    };

    return (
      <span className={`px-3 py-1 rounded-full text-xs font-medium ${colors[safeCategory] || colors['other']}`}>
        {safeCategory.toUpperCase()}
      </span>
    );
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (error || !standard) {
    return (
      <div className="min-h-screen bg-gray-50 py-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="bg-red-50 border border-red-200 rounded-md p-6">
            <p className="text-red-800">{error || 'Standard not found'}</p>
            <button
              onClick={() => router.push('/iso-standards')}
              className="mt-4 px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700"
            >
              ← Back to Standards
            </button>
          </div>
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
            onClick={() => router.push('/iso-standards')}
            className="flex items-center gap-2 text-gray-600 hover:text-gray-900 mb-4"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
            Back to Standards
          </button>

          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div className="flex items-start justify-between mb-4">
              <div className="flex-1">
                <div className="flex items-center gap-3 mb-2">
                  <h1 className="text-3xl font-bold text-gray-900">{standard.name}</h1>
                  {getCategoryBadge(standard.category)}
                </div>
                <p className="text-lg text-gray-600">ISO {standard.iso_number}:{standard.year}</p>
              </div>
              {standard.is_active && (
                <div className="flex items-center gap-2 px-3 py-2 bg-green-100 text-green-800 rounded-md font-medium">
                  <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                  </svg>
                  Active
                </div>
              )}
            </div>

            <p className="text-gray-700 mb-4">{standard.description}</p>

            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 pt-4 border-t">
              <div>
                <p className="text-sm text-gray-500">Total Clauses</p>
                <p className="text-2xl font-semibold text-gray-900">{standard.clauses.length}</p>
              </div>
              <div>
                <p className="text-sm text-gray-500">Mandatory</p>
                <p className="text-2xl font-semibold text-gray-900">
                  {standard.clauses.filter(c => c.is_mandatory).length}
                </p>
              </div>
              <div>
                <p className="text-sm text-gray-500">Optional</p>
                <p className="text-2xl font-semibold text-gray-900">
                  {standard.clauses.filter(c => !c.is_mandatory).length}
                </p>
              </div>
              <div>
                <p className="text-sm text-gray-500">Imported</p>
                <p className="text-sm font-medium text-gray-900">
                  {new Date(standard.imported_at).toLocaleDateString()}
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* QMS Scope Section (ISO 4.3) */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 mb-6">
          <div className="p-6 border-b border-gray-200">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-xl font-bold text-gray-900">QMS Scope</h2>
                <p className="text-sm text-gray-600 mt-1">ISO 4.3 - Scope of the Quality Management System</p>
              </div>
              <button
                onClick={() => setShowScopeEditor(true)}
                className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 text-sm font-medium"
              >
                {(standard.qms_scope_statement || standard.qms_exclusions || standard.qms_applicability || standard.qms_boundaries) 
                  ? 'Edit Scope' 
                  : 'Define Scope'}
              </button>
            </div>
          </div>

          <div className="p-6 space-y-4">
            {standard.qms_scope_statement ? (
              <>
                <div>
                  <h3 className="text-sm font-semibold text-gray-700 mb-1">Scope Statement</h3>
                  <p className="text-gray-900 whitespace-pre-wrap">{standard.qms_scope_statement}</p>
                </div>
                {standard.qms_exclusions && (
                  <div>
                    <h3 className="text-sm font-semibold text-gray-700 mb-1">Exclusions</h3>
                    <p className="text-gray-900 whitespace-pre-wrap">{standard.qms_exclusions}</p>
                  </div>
                )}
                {standard.qms_applicability && (
                  <div>
                    <h3 className="text-sm font-semibold text-gray-700 mb-1">Applicability</h3>
                    <p className="text-gray-900 whitespace-pre-wrap">{standard.qms_applicability}</p>
                  </div>
                )}
                {standard.qms_boundaries && (
                  <div>
                    <h3 className="text-sm font-semibold text-gray-700 mb-1">Boundaries</h3>
                    <p className="text-gray-900 whitespace-pre-wrap">{standard.qms_boundaries}</p>
                  </div>
                )}
              </>
            ) : (
              <p className="text-gray-500 text-center py-8">
                No QMS scope defined yet. Click "Define Scope" to add scope information.
              </p>
            )}
          </div>
        </div>

        {/* Clauses List */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200">
          <div className="p-6 border-b border-gray-200">
            <h2 className="text-xl font-bold text-gray-900">Clauses</h2>
            <p className="text-sm text-gray-600 mt-1">
              Click on any clause to view its full content
            </p>
          </div>

          <div className="divide-y divide-gray-200">
            {standard.clauses.map((clause) => {
              const isExpanded = expandedClauses.has(clause.id);
              return (
                <div key={clause.id} className="p-4 hover:bg-gray-50 transition-colors">
                  <button
                    onClick={() => toggleClause(clause.id)}
                    className="w-full flex items-start justify-between gap-4 text-left"
                  >
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-1">
                        <span className="px-2 py-1 bg-gray-100 text-gray-700 rounded font-mono text-sm font-medium">
                          {clause.clause_number}
                        </span>
                        <h3 className="font-semibold text-gray-900">{clause.title}</h3>
                        {clause.is_mandatory && (
                          <span className="px-2 py-0.5 bg-red-100 text-red-700 rounded text-xs font-medium">
                            MANDATORY
                          </span>
                        )}
                      </div>
                      {isExpanded && clause.content && (
                        <div className="mt-3 pl-4 border-l-2 border-blue-500">
                          <p className="text-sm text-gray-700 whitespace-pre-wrap">
                            {clause.content}
                          </p>
                        </div>
                      )}
                    </div>
                    <svg
                      className={`w-5 h-5 text-gray-400 flex-shrink-0 transition-transform ${
                        isExpanded ? 'transform rotate-180' : ''
                      }`}
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                    </svg>
                  </button>
                </div>
              );
            })}
          </div>
        </div>

        {/* Actions */}
        <div className="mt-6 flex gap-4">
          <button
            onClick={() => router.push('/generate')}
            className="px-6 py-3 bg-blue-600 text-white rounded-md hover:bg-blue-700 font-medium"
          >
            Generate Documents from this Standard
          </button>
          <button
            onClick={() => router.push('/gap-analysis')}
            className="px-6 py-3 bg-green-600 text-white rounded-md hover:bg-green-700 font-medium"
          >
            Run Gap Analysis
          </button>
          <button
            onClick={() => setShowDeleteConfirm(true)}
            disabled={deleting}
            className="ml-auto px-6 py-3 bg-red-600 text-white rounded-md hover:bg-red-700 font-medium disabled:bg-red-300 disabled:cursor-not-allowed"
          >
            {deleting ? 'Deleting...' : 'Delete Standard'}
          </button>
        </div>

        {/* Delete Confirmation Modal */}
        {showDeleteConfirm && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white rounded-lg p-6 max-w-md mx-4">
              <h3 className="text-xl font-bold text-gray-900 mb-4">Confirm Deletion</h3>
              <p className="text-gray-700 mb-6">
                Are you sure you want to delete <strong>{standard?.name}</strong>? 
                This will permanently remove the standard and all {standard?.clauses.length} clauses.
                This action cannot be undone.
              </p>
              <div className="flex gap-3 justify-end">
                <button
                  onClick={() => setShowDeleteConfirm(false)}
                  className="px-4 py-2 bg-gray-200 text-gray-800 rounded-md hover:bg-gray-300 font-medium"
                >
                  Cancel
                </button>
                <button
                  onClick={handleDelete}
                  disabled={deleting}
                  className="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 font-medium disabled:bg-red-300"
                >
                  {deleting ? 'Deleting...' : 'Delete Permanently'}
                </button>
              </div>
            </div>
          </div>
        )}

        {/* QMS Scope Editor Modal */}
        {showScopeEditor && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
            <div className="bg-white rounded-lg p-6 max-w-3xl w-full max-h-[90vh] overflow-y-auto">
              <h3 className="text-xl font-bold text-gray-900 mb-4">Edit QMS Scope</h3>
              <form onSubmit={handleScopeUpdate} className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Scope Statement *
                  </label>
                  <textarea
                    value={scopeData.qms_scope_statement}
                    onChange={(e) => setScopeData({...scopeData, qms_scope_statement: e.target.value})}
                    rows={4}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                    placeholder="Define the products, services, and processes covered by your QMS..."
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Exclusions
                  </label>
                  <textarea
                    value={scopeData.qms_exclusions}
                    onChange={(e) => setScopeData({...scopeData, qms_exclusions: e.target.value})}
                    rows={3}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                    placeholder="List any permitted exclusions (e.g., ISO 9001 clause 8.3 - Design and development)..."
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Applicability
                  </label>
                  <textarea
                    value={scopeData.qms_applicability}
                    onChange={(e) => setScopeData({...scopeData, qms_applicability: e.target.value})}
                    rows={3}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                    placeholder="Where and how the QMS applies (locations, departments, processes)..."
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Boundaries
                  </label>
                  <textarea
                    value={scopeData.qms_boundaries}
                    onChange={(e) => setScopeData({...scopeData, qms_boundaries: e.target.value})}
                    rows={3}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                    placeholder="Geographic, organizational, or operational boundaries..."
                  />
                </div>
                <div className="flex gap-3 justify-end pt-4 border-t">
                  <button
                    type="button"
                    onClick={() => setShowScopeEditor(false)}
                    className="px-4 py-2 bg-gray-200 text-gray-800 rounded-md hover:bg-gray-300 font-medium"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 font-medium"
                  >
                    Save Scope
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
