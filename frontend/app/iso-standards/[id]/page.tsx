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
        </div>
      </div>
    </div>
  );
}
