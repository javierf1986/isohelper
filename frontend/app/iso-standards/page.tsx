'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useTranslations } from 'next-intl';
import { ProtectedRoute } from '@/components/ProtectedRoute';

interface ISOStandard {
  id: string;
  name: string;
  iso_number: string;
  year: number;
  description: string;
  category: string;
  clause_count: number;
  is_active: boolean;
  imported_at: string;
}

export default function ISOStandardsPage() {
  const t = useTranslations();
  const router = useRouter();
  const [standards, setStandards] = useState<ISOStandard[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchStandards();
  }, []);

  const fetchStandards = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/v1/iso-standards/');

      if (response.ok) {
        const data = await response.json();
        setStandards(data);
      } else {
        setError('Failed to load ISO standards');
      }
    } catch (err) {
      setError('Error loading ISO standards');
      console.error('Error fetching standards:', err);
    } finally {
      setLoading(false);
    }
  };

  const getCategoryBadge = (category?: string) => {
    // Handle undefined or null category
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

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8 flex justify-between items-center">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">ISO Standards Library</h1>
              <p className="mt-2 text-gray-600">Manage and view available ISO standards for your organization</p>
            </div>
            <button
              onClick={() => router.push('/iso-standards/upload')}
              className="px-6 py-3 bg-blue-600 text-white rounded-md hover:bg-blue-700 font-medium"
            >
              + Upload New ISO Standard
            </button>
          </div>

          {/* Error Message */}
          {error && (
            <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-md">
              <p className="text-red-800">{error}</p>
            </div>
          )}

          {/* Standards Grid */}
          {standards.length === 0 ? (
            <div className="bg-white rounded-lg shadow-lg p-12 text-center">
              <div className="text-6xl mb-4">📚</div>
              <h2 className="text-2xl font-semibold text-gray-900 mb-2">No ISO Standards Yet</h2>
              <p className="text-gray-600 mb-6">
                Upload ISO standard documents (PDF/DOCX) to start generating compliance documentation
              </p>
              <button
                onClick={() => router.push('/iso-standards/upload')}
                className="px-6 py-3 bg-blue-600 text-white rounded-md hover:bg-blue-700 font-medium"
              >
                Upload First ISO Standard
              </button>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {standards.map((standard) => (
                <div
                  key={standard.id}
                  className="bg-white rounded-lg shadow hover:shadow-lg transition-shadow p-6"
                >
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-2">
                        <h3 className="text-lg font-semibold text-gray-900">
                          {standard.name}
                        </h3>
                        {getCategoryBadge(standard.category)}
                      </div>
                      <p className="text-sm text-gray-500">ISO {standard.iso_number}:{standard.year}</p>
                    </div>
                    {standard.is_active && (
                      <div className="flex items-center gap-1 px-2 py-1 bg-green-100 text-green-800 rounded text-xs font-medium">
                        <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                        </svg>
                        Active
                      </div>
                    )}
                  </div>

                  <p className="text-sm text-gray-600 mb-4 line-clamp-2">
                    {standard.description || 'No description available'}
                  </p>

                  <div className="flex items-center justify-between pt-4 border-t">
                    <div className="flex items-center gap-2 text-sm text-gray-500">
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                      </svg>
                      <span>{standard.clause_count} clauses</span>
                    </div>
                    <button
                      onClick={() => router.push(`/iso-standards/${standard.id}`)}
                      className="text-blue-600 hover:text-blue-700 font-medium text-sm"
                    >
                      View Details →
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* Info Box */}
          <div className="mt-8 bg-blue-50 border border-blue-200 rounded-lg p-6">
            <div className="flex items-start gap-3">
              <svg className="w-6 h-6 text-blue-600 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <div>
                <h3 className="font-semibold text-blue-900 mb-1">About ISO Standards</h3>
                <p className="text-sm text-blue-800">
                  Upload ISO standard documents to enable document generation for that standard. 
                  The system will automatically parse the standard structure and make it available 
                  for creating compliance documentation. Supported formats: PDF, DOCX.
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
  );
}
