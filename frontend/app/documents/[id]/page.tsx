/**
 * Document Detail View Page
 * Display full document content with metadata and actions
 */

'use client';

import { useRouter, useParams } from 'next/navigation';
import { ProtectedRoute } from '@/components/ProtectedRoute';
import { documentService } from '@/lib/document-service';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useState } from 'react';
import { ExportModal } from '@/components/ExportModal';

function DocumentDetailContent() {
  const router = useRouter();
  const params = useParams();
  const queryClient = useQueryClient();
  const documentId = Number(params.id);
  
  const [showExportModal, setShowExportModal] = useState(false);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);

  // Fetch document
  const { data: document, isLoading, error } = useQuery({
    queryKey: ['document', documentId],
    queryFn: () => documentService.getDocument(documentId),
    enabled: !!documentId && !isNaN(documentId),
  });

  // Delete mutation
  const deleteMutation = useMutation({
    mutationFn: documentService.deleteDocument,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['documents'] });
      router.push('/documents');
    },
  });

  const handleDelete = async () => {
    await deleteMutation.mutateAsync(documentId);
  };

  const handleDownload = () => {
    if (document?.file_path) {
      documentService.downloadDocument(document.file_path);
    }
  };

  // Loading state
  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading document...</p>
        </div>
      </div>
    );
  }

  // Error state
  if (error || !document) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center max-w-md">
          <svg className="mx-auto h-12 w-12 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
          <h2 className="mt-4 text-xl font-bold text-gray-900">Document Not Found</h2>
          <p className="mt-2 text-gray-600">The document you're looking for doesn't exist or has been deleted.</p>
          <button
            onClick={() => router.push('/documents')}
            className="mt-6 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
          >
            Back to Library
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex-1">
              {/* Breadcrumb */}
              <nav className="flex items-center text-sm text-gray-500 mb-2">
                <button
                  onClick={() => router.push('/dashboard')}
                  className="hover:text-blue-600"
                >
                  Dashboard
                </button>
                <span className="mx-2">/</span>
                <button
                  onClick={() => router.push('/documents')}
                  className="hover:text-blue-600"
                >
                  Documents
                </button>
                <span className="mx-2">/</span>
                <span className="text-gray-900 font-medium">{document.title}</span>
              </nav>
              
              {/* Title */}
              <h1 className="text-2xl font-bold text-gray-900">{document.title}</h1>
              
              {/* Metadata badges */}
              <div className="flex items-center gap-3 mt-2">
                <span className="px-2 py-1 text-xs font-medium bg-blue-100 text-blue-800 rounded-full">
                  {document.iso_standard}
                </span>
                <span className="text-sm text-gray-500">
                  Created {new Date(document.created_at).toLocaleDateString()}
                </span>
                {document.file_size && (
                  <span className="text-sm text-gray-500">
                    {(document.file_size / 1024).toFixed(1)} KB
                  </span>
                )}
              </div>
            </div>

            {/* Actions */}
            <div className="flex gap-2 ml-4">
              <button
                onClick={handleDownload}
                className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50"
              >
                <svg className="inline-block w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                </svg>
                Download
              </button>
              <button
                onClick={() => setShowExportModal(true)}
                className="px-4 py-2 text-sm font-medium text-white bg-green-600 rounded-md hover:bg-green-700"
              >
                <svg className="inline-block w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7H5a2 2 0 00-2 2v9a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-3m-1 4l-3 3m0 0l-3-3m3 3V4" />
                </svg>
                Export
              </button>
              {showDeleteConfirm ? (
                <>
                  <button
                    onClick={handleDelete}
                    disabled={deleteMutation.isPending}
                    className="px-4 py-2 text-sm font-medium text-white bg-red-600 rounded-md hover:bg-red-700 disabled:opacity-50"
                  >
                    {deleteMutation.isPending ? 'Deleting...' : 'Confirm Delete'}
                  </button>
                  <button
                    onClick={() => setShowDeleteConfirm(false)}
                    disabled={deleteMutation.isPending}
                    className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50"
                  >
                    Cancel
                  </button>
                </>
              ) : (
                <button
                  onClick={() => setShowDeleteConfirm(true)}
                  className="px-4 py-2 text-sm font-medium text-red-600 bg-white border border-red-300 rounded-md hover:bg-red-50"
                >
                  <svg className="inline-block w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                  </svg>
                  Delete
                </button>
              )}
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Document Content - Main Column */}
          <div className="lg:col-span-2">
            <div className="bg-white rounded-lg shadow-sm p-6">
              <h2 className="text-lg font-bold text-gray-900 mb-4">Document Content</h2>
              
              {document.content ? (
                <div className="prose prose-sm max-w-none">
                  {/* Render markdown content */}
                  <div 
                    className="text-gray-700 leading-relaxed whitespace-pre-wrap"
                    dangerouslySetInnerHTML={{ __html: formatContent(document.content) }}
                  />
                </div>
              ) : (
                <div className="text-center py-12">
                  <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                  <p className="mt-2 text-sm text-gray-500">Content preview not available</p>
                  <p className="text-xs text-gray-400 mt-1">Download the document to view full content</p>
                </div>
              )}
            </div>
          </div>

          {/* Metadata Sidebar */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-lg shadow-sm p-6 sticky top-24">
              <h2 className="text-lg font-bold text-gray-900 mb-4">Document Details</h2>
              
              <dl className="space-y-4">
                {/* ISO Standard */}
                <div>
                  <dt className="text-xs font-medium text-gray-500 uppercase">ISO Standard</dt>
                  <dd className="mt-1 text-sm text-gray-900 font-medium">{document.iso_standard}</dd>
                </div>

                {/* Created Date */}
                <div>
                  <dt className="text-xs font-medium text-gray-500 uppercase">Created</dt>
                  <dd className="mt-1 text-sm text-gray-900">
                    {new Date(document.created_at).toLocaleDateString('en-US', {
                      year: 'numeric',
                      month: 'long',
                      day: 'numeric'
                    })}
                  </dd>
                </div>

                {/* File Size */}
                {document.file_size && (
                  <div>
                    <dt className="text-xs font-medium text-gray-500 uppercase">File Size</dt>
                    <dd className="mt-1 text-sm text-gray-900">
                      {formatFileSize(document.file_size)}
                    </dd>
                  </div>
                )}

                {/* File Path */}
                {document.file_path && (
                  <div>
                    <dt className="text-xs font-medium text-gray-500 uppercase">File Location</dt>
                    <dd className="mt-1 text-xs text-gray-600 break-all font-mono">
                      {document.file_path.split('/').pop()}
                    </dd>
                  </div>
                )}

                {/* Generation Time */}
                {document.generation_time && (
                  <div>
                    <dt className="text-xs font-medium text-gray-500 uppercase">Generation Time</dt>
                    <dd className="mt-1 text-sm text-gray-900">
                      {document.generation_time.toFixed(2)}s
                    </dd>
                  </div>
                )}
              </dl>

              {/* Quick Actions */}
              <div className="mt-6 pt-6 border-t border-gray-200">
                <h3 className="text-sm font-medium text-gray-900 mb-3">Quick Actions</h3>
                <div className="space-y-2">
                  <button
                    onClick={() => router.push('/documents')}
                    className="w-full px-3 py-2 text-sm text-gray-700 bg-gray-50 rounded-md hover:bg-gray-100 text-left"
                  >
                    ← Back to Library
                  </button>
                  <button
                    onClick={() => router.push('/generate')}
                    className="w-full px-3 py-2 text-sm text-gray-700 bg-gray-50 rounded-md hover:bg-gray-100 text-left"
                  >
                    + Generate New Document
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>

      {/* Export Modal */}
      {showExportModal && document && (
        <ExportModal
          isOpen={showExportModal}
          onClose={() => setShowExportModal(false)}
          documentPath={document.file_path}
          documentTitle={document.title}
        />
      )}
    </div>
  );
}

// Helper function to format content with basic HTML
function formatContent(content: string): string {
  // Escape HTML to prevent XSS
  const escapeHtml = (text: string) => {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  };

  // Simple markdown-like formatting
  let formatted = escapeHtml(content);
  
  // Headers (## Header)
  formatted = formatted.replace(/^## (.+)$/gm, '<h2 class="text-xl font-bold mt-6 mb-3 text-gray-900">$1</h2>');
  formatted = formatted.replace(/^### (.+)$/gm, '<h3 class="text-lg font-semibold mt-4 mb-2 text-gray-900">$1</h3>');
  
  // Bold (**text**)
  formatted = formatted.replace(/\*\*(.+?)\*\*/g, '<strong class="font-semibold">$1</strong>');
  
  // Lists (- item)
  formatted = formatted.replace(/^- (.+)$/gm, '<li class="ml-4">• $1</li>');
  
  // Paragraphs (double newline)
  formatted = formatted.replace(/\n\n/g, '</p><p class="mb-4">');
  formatted = '<p class="mb-4">' + formatted + '</p>';
  
  return formatted;
}

// Helper function to format file size
function formatFileSize(bytes: number): string {
  if (bytes < 1024) return bytes + ' B';
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
}

export default function DocumentDetailPage() {
  return (
    <ProtectedRoute>
      <DocumentDetailContent />
    </ProtectedRoute>
  );
}
