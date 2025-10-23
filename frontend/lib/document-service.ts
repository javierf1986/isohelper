/**
 * Document API Service
 * Handles document generation, listing, and management
 */

import apiClient from './api-client';

export interface ISOStandard {
  id: string;
  name: string;
  version: string;
  description: string;
}

export interface Clause {
  id: number;
  number: string;
  title: string;
  description: string;
  required: boolean;
}

export interface GenerateDocumentRequest {
  iso_standard: string;
  selected_clauses: string[];
  company_name: string;
  company_description?: string;
  scope?: string;
  use_ai_enhancement?: boolean;
}

export interface Document {
  id: number;
  title: string;
  content: string;
  file_path: string;
  iso_standard: string;
  created_at: string;
  updated_at: string;
  user_id: number;
  workspace_id: number;
}

export interface GenerateDocumentResponse {
  id: number;
  title: string;
  file_path: string;
  iso_standard: string;
  message: string;
}

export const documentService = {
  /**
   * Get list of available ISO standards
   */
  async getISOStandards(): Promise<ISOStandard[]> {
    const response = await apiClient.get<ISOStandard[]>('/templates/standards');
    return response.data;
  },

  /**
   * Get clauses for a specific ISO standard
   */
  async getClauses(isoStandard: string): Promise<Clause[]> {
    const response = await apiClient.get<Clause[]>(`/templates/${isoStandard}/clauses`);
    return response.data;
  },

  /**
   * Generate a new document
   */
  async generateDocument(data: GenerateDocumentRequest): Promise<GenerateDocumentResponse> {
    const response = await apiClient.post<GenerateDocumentResponse>('/documents/generate', data);
    return response.data;
  },

  /**
   * Get all documents for the current user
   */
  async getDocuments(): Promise<Document[]> {
    const response = await apiClient.get<Document[]>('/documents');
    return response.data;
  },

  /**
   * Get a specific document by ID
   */
  async getDocument(id: number): Promise<Document> {
    const response = await apiClient.get<Document>(`/documents/${id}`);
    return response.data;
  },

  /**
   * Delete a document
   */
  async deleteDocument(id: number): Promise<void> {
    await apiClient.delete(`/documents/${id}`);
  },

  /**
   * Download document content
   */
  async downloadDocument(filePath: string): Promise<string> {
    const response = await apiClient.get(`/documents/download`, {
      params: { file_path: filePath },
    });
    return response.data;
  },
};
