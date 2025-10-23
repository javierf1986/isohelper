/**
 * Export API Service
 * Handles document export to PDF, DOCX, and HTML
 */

import apiClient from './api-client';

export type ExportFormat = 'pdf' | 'docx' | 'html';

export interface ExportRequest {
  document_path: string;
  format: ExportFormat;
  company_name?: string;
  include_branding?: boolean;
  output_filename?: string;
}

export interface ExportResponse {
  success: boolean;
  format: ExportFormat;
  file_path: string;
  file_size_bytes: number;
  message: string;
}

export interface ExportedFile {
  filename: string;
  format: ExportFormat;
  size_bytes: number;
  created_at: string;
  download_url: string;
}

export interface ExportListResponse {
  files: ExportedFile[];
  total_count: number;
}

export const exportService = {
  /**
   * Export a document to specified format
   */
  async exportDocument(data: ExportRequest): Promise<ExportResponse> {
    const response = await apiClient.post<ExportResponse>('/export', data);
    return response.data;
  },

  /**
   * List all exported files
   */
  async listExports(format?: ExportFormat): Promise<ExportListResponse> {
    const response = await apiClient.get<ExportListResponse>('/export/list', {
      params: format ? { format } : undefined,
    });
    return response.data;
  },

  /**
   * Download an exported file
   */
  async downloadExport(filename: string): Promise<Blob> {
    const response = await apiClient.get(`/export/download/${filename}`, {
      responseType: 'blob',
    });
    return response.data;
  },

  /**
   * Delete an exported file
   */
  async deleteExport(filename: string): Promise<void> {
    await apiClient.delete(`/export/${filename}`);
  },

  /**
   * Trigger download of exported file
   */
  triggerDownload(blob: Blob, filename: string): void {
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(url);
  },
};
