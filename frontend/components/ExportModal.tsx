/**
 * Export Modal Component
 * Reusable modal for exporting documents to PDF, DOCX, or HTML
 */

'use client';

import { useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import { exportService, type ExportFormat } from '@/lib/export-service';

interface ExportModalProps {
  isOpen: boolean;
  onClose: () => void;
  documentPath: string;
  documentTitle: string;
}

export function ExportModal({ isOpen, onClose, documentPath, documentTitle }: ExportModalProps) {
  const [format, setFormat] = useState<ExportFormat>('pdf');
  const [companyName, setCompanyName] = useState('');
  const [includeBranding, setIncludeBranding] = useState(true);

  // Export mutation
  const exportMutation = useMutation({
    mutationFn: exportService.exportDocument,
    onSuccess: async (response) => {
      // Download the exported file
      if (response.file_path) {
        const filename = response.file_path.split('/').pop() || `export.${format}`;
        try {
          const blob = await exportService.downloadExport(filename);
          exportService.triggerDownload(blob, filename);
        } catch (error) {
          console.error('Download failed:', error);
        }
      }
      
      // Reset and close
      setTimeout(() => {
        handleClose();
      }, 1500);
    },
  });

  const handleClose = () => {
    if (!exportMutation.isPending) {
      setFormat('pdf');
      setCompanyName('');
      setIncludeBranding(true);
      exportMutation.reset();
      onClose();
    }
  };

  const handleExport = () => {
    exportMutation.mutate({
      document_path: documentPath,
      format,
      company_name: companyName || undefined,
      include_branding: includeBranding,
    });
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto">
      {/* Backdrop */}
      <div 
        className="fixed inset-0 bg-black bg-opacity-50 transition-opacity"
        onClick={handleClose}
      />

      {/* Modal */}
      <div className="flex min-h-full items-center justify-center p-4">
        <div className="relative bg-white rounded-lg shadow-xl max-w-md w-full p-6">
          {/* Header */}
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-bold text-gray-900">Export Document</h3>
            <button
              onClick={handleClose}
              disabled={exportMutation.isPending}
              className="text-gray-400 hover:text-gray-600 disabled:opacity-50"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          {/* Document Info */}
          <div className="mb-4 p-3 bg-gray-50 rounded-lg">
            <p className="text-sm font-medium text-gray-700">Document</p>
            <p className="text-sm text-gray-900 mt-1">{documentTitle}</p>
          </div>

          {/* Form */}
          <div className="space-y-4">
            {/* Format Selection */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Export Format *
              </label>
              <div className="grid grid-cols-3 gap-2">
                {(['pdf', 'docx', 'html'] as ExportFormat[]).map((fmt) => (
                  <button
                    key={fmt}
                    onClick={() => setFormat(fmt)}
                    disabled={exportMutation.isPending}
                    className={`px-4 py-2 text-sm font-medium rounded-md border-2 transition-colors ${
                      format === fmt
                        ? 'border-blue-500 bg-blue-50 text-blue-700'
                        : 'border-gray-200 bg-white text-gray-700 hover:border-gray-300'
                    } disabled:opacity-50 disabled:cursor-not-allowed`}
                  >
                    {fmt.toUpperCase()}
                  </button>
                ))}
              </div>
              <p className="mt-2 text-xs text-gray-500">
                {format === 'pdf' && '📄 Portable Document Format - Best for sharing'}
                {format === 'docx' && '📝 Microsoft Word - Editable document'}
                {format === 'html' && '🌐 Web Page - View in browser'}
              </p>
            </div>

            {/* Company Name */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Company Name
              </label>
              <input
                type="text"
                value={companyName}
                onChange={(e) => setCompanyName(e.target.value)}
                disabled={exportMutation.isPending}
                placeholder="Optional: Add company name to header"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50 disabled:bg-gray-100"
              />
            </div>

            {/* Branding Toggle */}
            <div className="flex items-start gap-3">
              <input
                type="checkbox"
                id="branding"
                checked={includeBranding}
                onChange={(e) => setIncludeBranding(e.target.checked)}
                disabled={exportMutation.isPending}
                className="mt-1 h-4 w-4 text-blue-600 rounded focus:ring-blue-500 disabled:opacity-50"
              />
              <label htmlFor="branding" className="flex-1 cursor-pointer">
                <span className="text-sm font-medium text-gray-700">Include Branding</span>
                <p className="text-xs text-gray-500 mt-1">
                  Add professional headers, footers, and styling to the exported document
                </p>
              </label>
            </div>
          </div>

          {/* Status Messages */}
          {exportMutation.isPending && (
            <div className="mt-4 p-3 bg-blue-50 border border-blue-200 rounded-lg">
              <div className="flex items-center gap-3">
                <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-blue-600"></div>
                <div>
                  <p className="text-sm font-medium text-blue-900">Exporting...</p>
                  <p className="text-xs text-blue-700">Generating {format.toUpperCase()} file</p>
                </div>
              </div>
            </div>
          )}

          {exportMutation.isSuccess && (
            <div className="mt-4 p-3 bg-green-50 border border-green-200 rounded-lg">
              <div className="flex items-center gap-3">
                <svg className="w-5 h-5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
                <div>
                  <p className="text-sm font-medium text-green-900">Export Successful!</p>
                  <p className="text-xs text-green-700">Download should start automatically</p>
                </div>
              </div>
            </div>
          )}

          {exportMutation.isError && (
            <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded-lg">
              <div className="flex items-start gap-3">
                <svg className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
                <div className="flex-1">
                  <p className="text-sm font-medium text-red-900">Export Failed</p>
                  <p className="text-xs text-red-700 mt-1">
                    {(exportMutation.error as any)?.response?.data?.detail || exportMutation.error?.message || 'An error occurred'}
                  </p>
                </div>
              </div>
            </div>
          )}

          {/* Actions */}
          <div className="mt-6 flex gap-3">
            <button
              onClick={handleClose}
              disabled={exportMutation.isPending}
              className="flex-1 px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 rounded-md hover:bg-gray-200 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {exportMutation.isSuccess ? 'Close' : 'Cancel'}
            </button>
            <button
              onClick={handleExport}
              disabled={exportMutation.isPending || exportMutation.isSuccess}
              className="flex-1 px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {exportMutation.isPending ? 'Exporting...' : 'Export'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
