/**
 * Document Generation Wizard
 * Multi-step form for creating ISO documents
 */

'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useTranslations } from 'next-intl';
import { ProtectedRoute } from '@/components/ProtectedRoute';
import { documentService, type ISOStandard, type Clause } from '@/lib/document-service';
import { useQuery, useMutation } from '@tanstack/react-query';

type Step = 'standard' | 'clauses' | 'company' | 'generating';

function GenerateContent() {
  const router = useRouter();
  const t = useTranslations();
  const [currentStep, setCurrentStep] = useState<Step>('standard');
  const [selectedStandard, setSelectedStandard] = useState<string>('');
  const [selectedClauses, setSelectedClauses] = useState<string[]>([]);
  const [companyName, setCompanyName] = useState('');
  const [companyDescription, setCompanyDescription] = useState('');
  const [scope, setScope] = useState('');
  const [useAI, setUseAI] = useState(true);

  // Fetch ISO standards
  const { data: standards, isLoading: loadingStandards } = useQuery({
    queryKey: ['iso-standards'],
    queryFn: documentService.getISOStandards,
  });

  // Fetch clauses for selected standard
  const { data: clauses, isLoading: loadingClauses } = useQuery({
    queryKey: ['clauses', selectedStandard],
    queryFn: () => documentService.getClauses(selectedStandard),
    enabled: !!selectedStandard,
  });

  // Generate document mutation
  const generateMutation = useMutation({
    mutationFn: documentService.generateDocument,
    onSuccess: (data) => {
      setTimeout(() => {
        router.push('/documents');
      }, 2000);
    },
  });

  const handleStandardSelect = (standardId: string) => {
    setSelectedStandard(standardId);
    setSelectedClauses([]);
    setCurrentStep('clauses');
  };

  const handleClauseToggle = (clauseNumber: string) => {
    setSelectedClauses(prev =>
      prev.includes(clauseNumber)
        ? prev.filter(c => c !== clauseNumber)
        : [...prev, clauseNumber]
    );
  };

  const handleSelectAll = () => {
    if (clauses) {
      setSelectedClauses(clauses.map(c => c.number));
    }
  };

  const handleDeselectAll = () => {
    setSelectedClauses([]);
  };

  const handleGenerate = async () => {
    if (!companyName || selectedClauses.length === 0) return;

    setCurrentStep('generating');
    
    try {
      await generateMutation.mutateAsync({
        iso_standard: selectedStandard,
        selected_clauses: selectedClauses,
        company_name: companyName,
        company_description: companyDescription || undefined,
        scope: scope || undefined,
        use_ai_enhancement: useAI,
      });
    } catch (error) {
      setCurrentStep('company');
    }
  };

  const renderStandardSelection = () => (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-gray-900 mb-2">{t('generate.selectStandard')}</h2>
        <p className="text-gray-600">Choose the ISO standard for your documentation</p>
      </div>

      {loadingStandards ? (
        <div className="flex items-center justify-center py-12">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {standards?.map((standard) => (
            <button
              key={standard.id}
              onClick={() => handleStandardSelect(standard.id)}
              className="p-6 border-2 border-gray-200 rounded-lg hover:border-blue-500 hover:bg-blue-50 transition-all text-left group"
            >
              <h3 className="text-lg font-bold text-gray-900 group-hover:text-blue-600 mb-2">
                {standard.name}
              </h3>
              <p className="text-sm text-gray-600 mb-2">{standard.version}</p>
              <p className="text-sm text-gray-700">{standard.description}</p>
            </button>
          ))}
        </div>
      )}
    </div>
  );

  const renderClauseSelection = () => (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900 mb-2">{t('generate.selectClauses')}</h2>
          <p className="text-gray-600">Choose which clauses to include in your document</p>
        </div>
        <button
          onClick={() => setCurrentStep('standard')}
          className="text-blue-600 hover:text-blue-700 font-medium"
        >
          ← Change Standard
        </button>
      </div>

      <div className="flex gap-2 mb-4">
        <button
          onClick={handleSelectAll}
          className="px-4 py-2 text-sm bg-blue-600 text-white rounded-md hover:bg-blue-700"
        >
          {t('generate.selectAll')}
        </button>
        <button
          onClick={handleDeselectAll}
          className="px-4 py-2 text-sm bg-gray-200 text-gray-700 rounded-md hover:bg-gray-300"
        >
          {t('generate.deselectAll')}
        </button>
        <div className="ml-auto text-sm text-gray-600 flex items-center">
          Selected: {selectedClauses.length} / {clauses?.length || 0}
        </div>
      </div>

      {loadingClauses ? (
        <div className="flex items-center justify-center py-12">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        </div>
      ) : (
        <div className="space-y-2 max-h-96 overflow-y-auto">
          {clauses?.map((clause) => (
            <label
              key={clause.id}
              className="flex items-start p-4 border border-gray-200 rounded-lg hover:bg-gray-50 cursor-pointer"
            >
              <input
                type="checkbox"
                checked={selectedClauses.includes(clause.number)}
                onChange={() => handleClauseToggle(clause.number)}
                className="mt-1 mr-3 h-4 w-4 text-blue-600 rounded"
              />
              <div className="flex-1">
                <div className="font-medium text-gray-900">
                  {clause.number} - {clause.title}
                  {clause.required && (
                    <span className="ml-2 text-xs text-red-600 font-normal">Required</span>
                  )}
                </div>
                <p className="text-sm text-gray-600 mt-1">{clause.description}</p>
              </div>
            </label>
          ))}
        </div>
      )}

      <div className="flex justify-end">
        <button
          onClick={() => setCurrentStep('company')}
          disabled={selectedClauses.length === 0}
          className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          Continue →
        </button>
      </div>
    </div>
  );

  const renderCompanyInfo = () => (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900 mb-2">{t('generate.companyInfo')}</h2>
          <p className="text-gray-600">Provide details about your organization</p>
        </div>
        <button
          onClick={() => setCurrentStep('clauses')}
          className="text-blue-600 hover:text-blue-700 font-medium"
        >
          ← {t('common.back')}
        </button>
      </div>

      <div className="space-y-4">
        <div>
          <label htmlFor="companyName" className="block text-sm font-medium text-gray-700 mb-2">
            {t('generate.companyName')} *
          </label>
          <input
            type="text"
            id="companyName"
            value={companyName}
            onChange={(e) => setCompanyName(e.target.value)}
            className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            placeholder="Acme Corporation"
            required
          />
        </div>

        <div>
          <label htmlFor="companyDescription" className="block text-sm font-medium text-gray-700 mb-2">
            Company Description
          </label>
          <textarea
            id="companyDescription"
            value={companyDescription}
            onChange={(e) => setCompanyDescription(e.target.value)}
            rows={3}
            className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            placeholder="Brief description of your organization..."
          />
        </div>

        <div>
          <label htmlFor="scope" className="block text-sm font-medium text-gray-700 mb-2">
            Scope
          </label>
          <textarea
            id="scope"
            value={scope}
            onChange={(e) => setScope(e.target.value)}
            rows={3}
            className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            placeholder="Scope of your quality management system..."
          />
        </div>

        <div className="flex items-center">
          <input
            type="checkbox"
            id="useAI"
            checked={useAI}
            onChange={(e) => setUseAI(e.target.checked)}
            className="h-4 w-4 text-blue-600 rounded"
          />
          <label htmlFor="useAI" className="ml-2 text-sm text-gray-700">
            {t('generate.enableAI')}
          </label>
        </div>
      </div>

      <div className="flex justify-end">
        <button
          onClick={handleGenerate}
          disabled={!companyName || generateMutation.isPending}
          className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {generateMutation.isPending ? t('generate.generating') : t('dashboard.generateDocument')}
        </button>
      </div>
    </div>
  );

  const renderGenerating = () => (
    <div className="space-y-6 text-center py-12">
      <div className="flex justify-center">
        <div className="animate-spin rounded-full h-16 w-16 border-b-4 border-blue-600"></div>
      </div>
      <div>
        <h2 className="text-2xl font-bold text-gray-900 mb-2">{t('generate.generating')}</h2>
        <p className="text-gray-600 mb-4">
          {useAI ? 'AI is enhancing your content...' : 'Creating your document...'}
        </p>
        <p className="text-sm text-gray-500">This may take a moment</p>
      </div>
      
      {generateMutation.isSuccess && (
        <div className="bg-green-50 border border-green-200 rounded-lg p-4 mt-6">
          <p className="text-green-800 font-medium">✓ {t('generate.documentSuccess')}</p>
          <p className="text-sm text-green-600 mt-1">{t('generate.redirecting')}</p>
        </div>
      )}

      {generateMutation.isError && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 mt-6">
          <p className="text-red-800 font-medium">✗ {t('generate.documentFailed')}</p>
          <p className="text-sm text-red-600 mt-1">
            {(generateMutation.error as any)?.response?.data?.detail || t('generate.tryAgain')}
          </p>
          <button
            onClick={() => setCurrentStep('company')}
            className="mt-3 text-sm text-red-600 hover:text-red-700 font-medium"
          >
            ← {t('generate.goBack')}
          </button>
        </div>
      )}
    </div>
  );

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <h1 className="text-2xl font-bold text-gray-900">{t('dashboard.generateDocument')}</h1>
            <button
              onClick={() => router.push('/dashboard')}
              className="text-gray-600 hover:text-gray-900"
            >
              {t('common.cancel')}
            </button>
          </div>
        </div>
      </header>

      {/* Progress Steps */}
      <div className="bg-white border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-center gap-4">
            {[
              { id: 'standard', label: t('generate.progressStandard') },
              { id: 'clauses', label: t('generate.progressClauses') },
              { id: 'company', label: t('generate.progressCompanyInfo') },
              { id: 'generating', label: t('generate.progressGenerate') },
            ].map((step, index) => (
              <div key={step.id} className="flex items-center">
                <div className={`flex items-center ${
                  currentStep === step.id ? 'text-blue-600' :
                  ['standard', 'clauses', 'company', 'generating'].indexOf(currentStep) >
                  ['standard', 'clauses', 'company', 'generating'].indexOf(step.id)
                    ? 'text-green-600' : 'text-gray-400'
                }`}>
                  <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium ${
                    currentStep === step.id ? 'bg-blue-100' :
                    ['standard', 'clauses', 'company', 'generating'].indexOf(currentStep) >
                    ['standard', 'clauses', 'company', 'generating'].indexOf(step.id)
                      ? 'bg-green-100' : 'bg-gray-100'
                  }`}>
                    {['standard', 'clauses', 'company', 'generating'].indexOf(currentStep) >
                    ['standard', 'clauses', 'company', 'generating'].indexOf(step.id) ? '✓' : index + 1}
                  </div>
                  <span className="ml-2 text-sm font-medium">{step.label}</span>
                </div>
                {index < 3 && (
                  <div className="w-12 h-0.5 bg-gray-300 mx-2"></div>
                )}
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Main Content */}
      <main className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="bg-white rounded-lg shadow-sm p-8">
          {currentStep === 'standard' && renderStandardSelection()}
          {currentStep === 'clauses' && renderClauseSelection()}
          {currentStep === 'company' && renderCompanyInfo()}
          {currentStep === 'generating' && renderGenerating()}
        </div>
      </main>
    </div>
  );
}

export default function GeneratePage() {
  return (
    <ProtectedRoute>
      <GenerateContent />
    </ProtectedRoute>
  );
}
