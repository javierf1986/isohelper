/**
 * Gap Analysis Upload Page
 * Upload documents for AI-powered compliance gap analysis
 */

'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { ProtectedRoute } from '@/components/ProtectedRoute';

interface ISOStandard {
  id: string;
  standard_number: string;
  title: string;
  version: string;
}

export default function GapAnalysisUploadPage() {
  const router = useRouter();
  const [workspaceId, setWorkspaceId] = useState<string>('');
  const [isoStandards, setIsoStandards] = useState<ISOStandard[]>([]);
  const [selectedStandard, setSelectedStandard] = useState<string>('');
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [analyzing, setAnalyzing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [dragActive, setDragActive] = useState(false);

  useEffect(() => {
    // Get workspace ID from localStorage
    const wsId = localStorage.getItem('workspace_id');
    if (wsId) {
      setWorkspaceId(wsId);
      fetchISOStandards(wsId);
    }
  }, []);

  const fetchISOStandards = async (wsId: string) => {
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(`http://localhost:8889/api/workspaces/${wsId}/iso-standards`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });

      if (response.ok) {
        const data = await response.json();
        setIsoStandards(data.standards || []);
        if (data.standards && data.standards.length > 0) {
          setSelectedStandard(data.standards[0].id);
        }
      }
    } catch (err) {
      console.error('Error fetching ISO standards:', err);
    }
  };

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileSelect(e.dataTransfer.files[0]);
    }
  };

  const handleFileSelect = (selectedFile: File) => {
    // Validate file type
    const validTypes = ['.pdf', '.docx', '.doc', '.txt'];
    const fileExt = '.' + selectedFile.name.split('.').pop()?.toLowerCase();
    
    if (!validTypes.includes(fileExt)) {
      setError(`Invalid file type. Supported: ${validTypes.join(', ')}`);
      return;
    }

    // Validate file size (50MB max)
    const maxSize = 50 * 1024 * 1024;
    if (selectedFile.size > maxSize) {
      setError('File too large. Maximum size: 50MB');
      return;
    }

    setFile(selectedFile);
    setError(null);
  };

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      handleFileSelect(e.target.files[0]);
    }
  };

  const handleUploadAndAnalyze = async () => {
    if (!file || !selectedStandard) {
      setError('Please select a file and ISO standard');
      return;
    }

    setUploading(true);
    setError(null);

    try {
      const token = localStorage.getItem('access_token');
      
      // Upload document
      const formData = new FormData();
      formData.append('file', file);
      formData.append('workspace_id', workspaceId);
      formData.append('iso_standard_id', selectedStandard);

      const uploadResponse = await fetch('http://localhost:8889/api/v1/gap-analysis/upload', {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` },
        body: formData
      });

      if (!uploadResponse.ok) {
        const errorData = await uploadResponse.json();
        throw new Error(errorData.detail || 'Upload failed');
      }

      const analysisData = await uploadResponse.json();
      const analysisId = analysisData.id;

      setUploading(false);
      setAnalyzing(true);

      // Start analysis
      const analyzeResponse = await fetch(
        `http://localhost:8889/api/v1/gap-analysis/${analysisId}/analyze?workspace_id=${workspaceId}`,
        {
          method: 'POST',
          headers: { 'Authorization': `Bearer ${token}` }
        }
      );

      if (!analyzeResponse.ok) {
        const errorData = await analyzeResponse.json();
        throw new Error(errorData.detail || 'Analysis failed');
      }

      // Redirect to results page
      router.push(`/gap-analysis/${analysisId}`);

    } catch (err: any) {
      setError(err.message || 'An error occurred');
      setUploading(false);
      setAnalyzing(false);
    }
  };

  const formatFileSize = (bytes: number) => {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
  };

  return (
    <ProtectedRoute>
      <div className="min-h-screen bg-gray-50 py-8">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          {/* Header */}
          <div className="mb-8">
            <button
              onClick={() => router.push('/dashboard')}
              className="text-blue-600 hover:text-blue-800 mb-4 flex items-center gap-2"
            >
              ← Back to Dashboard
            </button>
            <h1 className="text-3xl font-bold text-gray-900">Gap Analysis</h1>
            <p className="mt-2 text-gray-600">
              Upload your QMS documentation for AI-powered compliance analysis
            </p>
          </div>

          {/* Main Card */}
          <div className="bg-white rounded-lg shadow-lg p-8">
            {/* ISO Standard Selector */}
            <div className="mb-8">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                ISO Standard to Analyze Against
              </label>
              <select
                value={selectedStandard}
                onChange={(e) => setSelectedStandard(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500"
                disabled={uploading || analyzing}
              >
                {isoStandards.map((standard) => (
                  <option key={standard.id} value={standard.id}>
                    {standard.standard_number} - {standard.title} ({standard.version})
                  </option>
                ))}
              </select>
              {isoStandards.length === 0 && (
                <p className="mt-2 text-sm text-gray-500">
                  No ISO standards found in workspace. Add one first.
                </p>
              )}
            </div>

            {/* File Upload Area */}
            <div className="mb-8">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Upload Document
              </label>
              
              <div
                className={`relative border-2 border-dashed rounded-lg p-12 text-center transition-colors ${
                  dragActive
                    ? 'border-blue-500 bg-blue-50'
                    : 'border-gray-300 hover:border-gray-400'
                } ${uploading || analyzing ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}`}
                onDragEnter={handleDrag}
                onDragLeave={handleDrag}
                onDragOver={handleDrag}
                onDrop={handleDrop}
                onClick={() => !uploading && !analyzing && document.getElementById('fileInput')?.click()}
              >
                <input
                  id="fileInput"
                  type="file"
                  className="hidden"
                  accept=".pdf,.docx,.doc,.txt"
                  onChange={handleFileInput}
                  disabled={uploading || analyzing}
                />

                {!file ? (
                  <>
                    <div className="text-6xl mb-4">📄</div>
                    <p className="text-lg font-medium text-gray-700 mb-2">
                      Drop your document here or click to browse
                    </p>
                    <p className="text-sm text-gray-500">
                      Supported formats: PDF, DOCX, DOC, TXT (max 50MB)
                    </p>
                  </>
                ) : (
                  <>
                    <div className="text-6xl mb-4">✅</div>
                    <p className="text-lg font-medium text-gray-700 mb-2">
                      {file.name}
                    </p>
                    <p className="text-sm text-gray-500">
                      Size: {formatFileSize(file.size)}
                    </p>
                    {!uploading && !analyzing && (
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          setFile(null);
                        }}
                        className="mt-4 text-red-600 hover:text-red-800 text-sm"
                      >
                        Remove file
                      </button>
                    )}
                  </>
                )}
              </div>
            </div>

            {/* Error Message */}
            {error && (
              <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-md">
                <p className="text-red-800 text-sm">{error}</p>
              </div>
            )}

            {/* Info Box */}
            <div className="mb-8 p-4 bg-blue-50 border border-blue-200 rounded-md">
              <h3 className="text-sm font-semibold text-blue-900 mb-2">What happens next?</h3>
              <ul className="text-sm text-blue-800 space-y-1">
                <li>• Your document will be parsed and analyzed by AI</li>
                <li>• Each ISO requirement will be checked for compliance</li>
                <li>• Gaps will be identified with severity levels</li>
                <li>• An implementation roadmap will be generated</li>
                <li>• Analysis typically takes 2-5 minutes</li>
              </ul>
            </div>

            {/* Action Buttons */}
            <div className="flex gap-4">
              <button
                onClick={handleUploadAndAnalyze}
                disabled={!file || !selectedStandard || uploading || analyzing}
                className={`flex-1 py-3 px-6 rounded-md font-medium transition-colors ${
                  !file || !selectedStandard || uploading || analyzing
                    ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                    : 'bg-blue-600 text-white hover:bg-blue-700'
                }`}
              >
                {uploading
                  ? 'Uploading...'
                  : analyzing
                  ? 'Analyzing... This may take a few minutes'
                  : 'Upload & Start Analysis'}
              </button>

              <button
                onClick={() => router.push('/gap-analysis')}
                disabled={uploading || analyzing}
                className="px-6 py-3 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50 disabled:opacity-50"
              >
                View Previous Analyses
              </button>
            </div>

            {/* Progress Indicator */}
            {(uploading || analyzing) && (
              <div className="mt-6">
                <div className="flex items-center justify-center gap-3">
                  <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600"></div>
                  <span className="text-gray-600">
                    {uploading ? 'Uploading document...' : 'AI analysis in progress...'}
                  </span>
                </div>
                {analyzing && (
                  <p className="text-center text-sm text-gray-500 mt-2">
                    Please do not close this page. You'll be redirected when complete.
                  </p>
                )}
              </div>
            )}
          </div>

          {/* Help Section */}
          <div className="mt-8 bg-white rounded-lg shadow p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Tips for Best Results</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <h3 className="font-medium text-gray-700 mb-2">📝 Document Content</h3>
                <ul className="text-sm text-gray-600 space-y-1">
                  <li>• Include QMS procedures and policies</li>
                  <li>• Upload work instructions if available</li>
                  <li>• Include management review records</li>
                </ul>
              </div>
              <div>
                <h3 className="font-medium text-gray-700 mb-2">✅ Document Quality</h3>
                <ul className="text-sm text-gray-600 space-y-1">
                  <li>• Use text-based PDFs (not scanned images)</li>
                  <li>• Ensure document is complete and readable</li>
                  <li>• Minimum 100 words for meaningful analysis</li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </div>
    </ProtectedRoute>
  );
}
