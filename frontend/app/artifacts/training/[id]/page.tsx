'use client';

import { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';

interface TrainingDetail {
  id: string;
  record_number: string;
  employee_id: string;
  training_title: string;
  training_date: string;
  trainer_name?: string;
  training_hours?: number;
  training_type?: string;
  competency_area?: string;
  passed: boolean;
  score?: number;
  certificate_number?: string;
  expiry_date?: string;
  notes?: string;
  created_at: string;
  updated_at: string;
}

export default function TrainingDetailPage() {
  const params = useParams();
  const router = useRouter();
  const trainingId = params.id as string;

  const [training, setTraining] = useState<TrainingDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchTrainingDetail();
  }, [trainingId]);

  const fetchTrainingDetail = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`http://localhost:8889/api/v1/artifacts/training/${trainingId}`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        if (response.status === 404) {
          setError('Training Record not found');
        } else {
          setError('Failed to load training record');
        }
        setLoading(false);
        return;
      }

      const data = await response.json();
      setTraining(data);
    } catch (err) {
      setError('Failed to connect to server');
      console.error('Error fetching training:', err);
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateStr: string) => {
    return new Date(dateStr).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    });
  };

  const formatDateTime = (dateStr: string) => {
    return new Date(dateStr).toLocaleString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const isExpired = (expiryDate: string) => {
    return new Date(expiryDate) < new Date();
  };

  const isExpiringSoon = (expiryDate: string) => {
    const expiry = new Date(expiryDate);
    const today = new Date();
    const threeMonthsFromNow = new Date();
    threeMonthsFromNow.setMonth(today.getMonth() + 3);
    return expiry >= today && expiry <= threeMonthsFromNow;
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-lg">Loading Training Record...</div>
      </div>
    );
  }

  if (error || !training) {
    return (
      <div className="flex flex-col items-center justify-center min-h-screen">
        <div className="text-xl text-red-600 mb-4">{error || 'Training Record not found'}</div>
        <button
          onClick={() => router.push('/artifacts/training')}
          className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
        >
          Back to Training Records
        </button>
      </div>
    );
  }

  return (
    <div className="p-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="mb-6">
        <button
          onClick={() => router.push('/artifacts/training')}
          className="text-blue-600 hover:text-blue-800 mb-4 flex items-center"
        >
          ← Back to Training Records
        </button>
        
        <div className="flex justify-between items-start">
          <div>
            <h1 className="text-3xl font-bold mb-2">{training.record_number}: {training.training_title}</h1>
            <div className="flex gap-3 items-center">
              <span className={`px-3 py-1 rounded-full text-sm font-medium ${training.passed ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}>
                {training.passed ? 'PASSED' : 'FAILED'}
              </span>
              {training.certificate_number && (
                <span className="px-3 py-1 rounded-full text-sm font-medium bg-blue-100 text-blue-800">
                  Certified
                </span>
              )}
              {training.expiry_date && isExpired(training.expiry_date) && (
                <span className="px-3 py-1 rounded-full text-sm font-medium bg-red-100 text-red-800">
                  EXPIRED
                </span>
              )}
              {training.expiry_date && isExpiringSoon(training.expiry_date) && !isExpired(training.expiry_date) && (
                <span className="px-3 py-1 rounded-full text-sm font-medium bg-orange-100 text-orange-800">
                  EXPIRING SOON
                </span>
              )}
            </div>
          </div>
          <div className="flex gap-3">
            <button className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700">
              Edit
            </button>
            <button className="px-4 py-2 bg-gray-600 text-white rounded hover:bg-gray-700">
              Export Certificate
            </button>
          </div>
        </div>
      </div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column - Main Details */}
        <div className="lg:col-span-2 space-y-6">
          {/* Training Information */}
          <div className="bg-white shadow rounded-lg p-6">
            <h2 className="text-xl font-semibold mb-4">Training Information</h2>
            <div className="space-y-3">
              <div>
                <p className="text-sm text-gray-500">Employee ID</p>
                <p className="font-medium">{training.employee_id}</p>
              </div>
              <div>
                <p className="text-sm text-gray-500">Training Title</p>
                <p className="font-medium">{training.training_title}</p>
              </div>
              {training.training_type && (
                <div>
                  <p className="text-sm text-gray-500">Training Type</p>
                  <p className="font-medium capitalize">{training.training_type.replace('_', ' ')}</p>
                </div>
              )}
              {training.competency_area && (
                <div>
                  <p className="text-sm text-gray-500">Competency Area</p>
                  <p className="font-medium">{training.competency_area}</p>
                </div>
              )}
              {training.trainer_name && (
                <div>
                  <p className="text-sm text-gray-500">Trainer</p>
                  <p className="font-medium">{training.trainer_name}</p>
                </div>
              )}
            </div>
          </div>

          {/* Assessment Results */}
          <div className="bg-white shadow rounded-lg p-6">
            <h2 className="text-xl font-semibold mb-4">Assessment Results</h2>
            <div className="grid grid-cols-2 gap-4">
              <div className={`p-4 rounded-lg ${training.passed ? 'bg-green-50 border border-green-200' : 'bg-red-50 border border-red-200'}`}>
                <p className="text-sm text-gray-600 mb-1">Status</p>
                <p className={`text-2xl font-bold ${training.passed ? 'text-green-700' : 'text-red-700'}`}>
                  {training.passed ? 'PASSED' : 'FAILED'}
                </p>
              </div>
              {training.score !== undefined && (
                <div className="bg-blue-50 p-4 rounded-lg border border-blue-200">
                  <p className="text-sm text-gray-600 mb-1">Score</p>
                  <p className="text-2xl font-bold text-blue-700">{training.score}%</p>
                </div>
              )}
            </div>
          </div>

          {/* Certificate Information */}
          {training.certificate_number && (
            <div className="bg-white shadow rounded-lg p-6 border-l-4 border-blue-500">
              <h2 className="text-xl font-semibold mb-4">Certificate Information</h2>
              <div className="space-y-3">
                <div>
                  <p className="text-sm text-gray-500">Certificate Number</p>
                  <p className="font-medium text-lg">{training.certificate_number}</p>
                </div>
                {training.expiry_date && (
                  <div>
                    <p className="text-sm text-gray-500">Expiry Date</p>
                    <p className={`font-medium ${isExpired(training.expiry_date) ? 'text-red-600' : isExpiringSoon(training.expiry_date) ? 'text-orange-600' : 'text-green-600'}`}>
                      {formatDate(training.expiry_date)}
                      {isExpired(training.expiry_date) && ' (EXPIRED)'}
                      {isExpiringSoon(training.expiry_date) && !isExpired(training.expiry_date) && ' (EXPIRING SOON)'}
                    </p>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Notes */}
          {training.notes && (
            <div className="bg-white shadow rounded-lg p-6">
              <h2 className="text-xl font-semibold mb-3">Notes</h2>
              <p className="text-gray-700 whitespace-pre-wrap">{training.notes}</p>
            </div>
          )}
        </div>

        {/* Right Column - Info & Timeline */}
        <div className="space-y-6">
          {/* Key Information */}
          <div className="bg-white shadow rounded-lg p-6">
            <h2 className="text-xl font-semibold mb-4">Key Information</h2>
            <div className="space-y-3">
              <div>
                <p className="text-sm text-gray-500">Training Date</p>
                <p className="font-medium">{formatDate(training.training_date)}</p>
              </div>
              {training.training_hours !== undefined && (
                <div>
                  <p className="text-sm text-gray-500">Training Hours</p>
                  <p className="font-medium">{training.training_hours} hours</p>
                </div>
              )}
            </div>
          </div>

          {/* Timeline */}
          <div className="bg-white shadow rounded-lg p-6">
            <h2 className="text-xl font-semibold mb-4">Timeline</h2>
            <div className="space-y-4">
              <div>
                <p className="text-sm text-gray-500">Record Created</p>
                <p className="text-sm">{formatDateTime(training.created_at)}</p>
              </div>
              <div>
                <p className="text-sm text-gray-500">Last Updated</p>
                <p className="text-sm">{formatDateTime(training.updated_at)}</p>
              </div>
            </div>
          </div>

          {/* Actions */}
          <div className="bg-white shadow rounded-lg p-6">
            <h2 className="text-xl font-semibold mb-4">Actions</h2>
            <div className="space-y-3">
              <button className="w-full px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700">
                Update Record
              </button>
              {training.certificate_number && training.expiry_date && (
                <button className="w-full px-4 py-2 bg-orange-600 text-white rounded hover:bg-orange-700">
                  Renew Certificate
                </button>
              )}
              <button className="w-full px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700">
                Schedule Follow-up Training
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
