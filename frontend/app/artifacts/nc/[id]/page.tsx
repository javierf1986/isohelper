"use client";

import { useEffect, useState } from "react";
import { useRouter, useParams } from "next/navigation";

interface NonConformity {
  id: string;
  nc_number: string;
  title: string;
  description: string;
  severity: string;
  status: string;
  detected_date: string;
  category: string | null;
  detected_location: string | null;
  iso_clause_number: string | null;
  reported_by: string;
  root_cause: string | null;
  contributing_factors: string | null;
  ai_root_cause_analysis: string | null;
  immediate_actions: string | null;
  target_closure_date: string | null;
  actual_closure_date: string | null;
  verified_by: string | null;
  verified_at: string | null;
  created_at: string;
  updated_at: string;
}

export default function NCDetailPage() {
  const router = useRouter();
  const params = useParams();
  const ncId = params?.id as string;

  const [nc, setNc] = useState<NonConformity | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (ncId) {
      fetchNCDetail();
    }
  }, [ncId]);

  const fetchNCDetail = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem("access_token");
      
      const response = await fetch(`http://localhost:8889/api/v1/artifacts/nc/${ncId}`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        throw new Error("Failed to fetch NC details");
      }

      const data = await response.json();
      setNc(data);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "An error occurred");
    } finally {
      setLoading(false);
    }
  };

  const getSeverityColor = (severity: string): string => {
    switch (severity.toUpperCase()) {
      case "CRITICAL":
        return "bg-red-100 text-red-800 border-red-300";
      case "MAJOR":
        return "bg-orange-100 text-orange-800 border-orange-300";
      case "MINOR":
        return "bg-yellow-100 text-yellow-800 border-yellow-300";
      default:
        return "bg-gray-100 text-gray-800 border-gray-300";
    }
  };

  const getStatusColor = (status: string): string => {
    switch (status.toUpperCase()) {
      case "OPEN":
        return "bg-blue-100 text-blue-800 border-blue-300";
      case "INVESTIGATING":
        return "bg-purple-100 text-purple-800 border-purple-300";
      case "RESOLVED":
        return "bg-green-100 text-green-800 border-green-300";
      case "VERIFIED":
        return "bg-teal-100 text-teal-800 border-teal-300";
      case "CLOSED":
        return "bg-gray-100 text-gray-800 border-gray-300";
      default:
        return "bg-gray-100 text-gray-800 border-gray-300";
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString("en-US", {
      year: "numeric",
      month: "long",
      day: "numeric",
    });
  };

  const formatDateTime = (dateString: string) => {
    return new Date(dateString).toLocaleString("en-US", {
      year: "numeric",
      month: "long",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center min-h-screen">
        <div className="text-lg">Loading non-conformity details...</div>
      </div>
    );
  }

  if (error || !nc) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
          {error || "Non-conformity not found"}
        </div>
        <button
          onClick={() => router.push("/artifacts/nc")}
          className="mt-4 text-blue-600 hover:text-blue-800"
        >
          ← Back to Non-Conformities
        </button>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      {/* Header */}
      <div className="mb-6">
        <button
          onClick={() => router.push("/artifacts/nc")}
          className="text-blue-600 hover:text-blue-800 mb-4"
        >
          ← Back to Non-Conformities
        </button>
        
        <div className="flex justify-between items-start">
          <div>
            <h1 className="text-3xl font-bold mb-2">{nc.nc_number}</h1>
            <p className="text-xl text-gray-700">{nc.title}</p>
          </div>
          <div className="flex gap-2">
            <button
              onClick={() => router.push(`/artifacts/nc/${nc.id}/edit`)}
              className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg transition"
            >
              Edit
            </button>
            <button
              className="bg-gray-200 hover:bg-gray-300 text-gray-700 px-4 py-2 rounded-lg transition"
            >
              Export PDF
            </button>
          </div>
        </div>
      </div>

      {/* Status and Severity Badges */}
      <div className="flex gap-4 mb-6">
        <div>
          <span className="text-sm text-gray-600">Severity</span>
          <div className={`mt-1 inline-flex px-4 py-2 text-sm font-semibold rounded-full border-2 ${getSeverityColor(nc.severity)}`}>
            {nc.severity}
          </div>
        </div>
        <div>
          <span className="text-sm text-gray-600">Status</span>
          <div className={`mt-1 inline-flex px-4 py-2 text-sm font-semibold rounded-full border-2 ${getStatusColor(nc.status)}`}>
            {nc.status.replace("_", " ")}
          </div>
        </div>
      </div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column - Main Details */}
        <div className="lg:col-span-2 space-y-6">
          {/* Description */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold mb-4">Description</h2>
            <p className="text-gray-700 whitespace-pre-wrap">{nc.description}</p>
          </div>

          {/* Root Cause Analysis */}
          {(nc.root_cause || nc.ai_root_cause_analysis) && (
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-xl font-semibold mb-4">Root Cause Analysis</h2>
              
              {nc.root_cause && (
                <div className="mb-4">
                  <h3 className="font-medium text-gray-700 mb-2">Root Cause</h3>
                  <p className="text-gray-700 whitespace-pre-wrap">{nc.root_cause}</p>
                </div>
              )}

              {nc.contributing_factors && (
                <div className="mb-4">
                  <h3 className="font-medium text-gray-700 mb-2">Contributing Factors</h3>
                  <p className="text-gray-700 whitespace-pre-wrap">{nc.contributing_factors}</p>
                </div>
              )}

              {nc.ai_root_cause_analysis && (
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                  <h3 className="font-medium text-blue-900 mb-2">🤖 AI Analysis</h3>
                  <p className="text-blue-800 text-sm whitespace-pre-wrap">{nc.ai_root_cause_analysis}</p>
                </div>
              )}
            </div>
          )}

          {/* Immediate Actions */}
          {nc.immediate_actions && (
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-xl font-semibold mb-4">Immediate Actions Taken</h2>
              <p className="text-gray-700 whitespace-pre-wrap">{nc.immediate_actions}</p>
            </div>
          )}
        </div>

        {/* Right Column - Metadata */}
        <div className="space-y-6">
          {/* Key Information */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold mb-4">Key Information</h2>
            <div className="space-y-3">
              <div>
                <div className="text-sm text-gray-600">Detected Date</div>
                <div className="font-medium">{formatDate(nc.detected_date)}</div>
              </div>

              <div>
                <div className="text-sm text-gray-600">Reported By</div>
                <div className="font-medium">{nc.reported_by}</div>
              </div>

              {nc.category && (
                <div>
                  <div className="text-sm text-gray-600">Category</div>
                  <div className="font-medium">{nc.category}</div>
                </div>
              )}

              {nc.detected_location && (
                <div>
                  <div className="text-sm text-gray-600">Location</div>
                  <div className="font-medium">{nc.detected_location}</div>
                </div>
              )}

              {nc.iso_clause_number && (
                <div>
                  <div className="text-sm text-gray-600">ISO Clause</div>
                  <div className="font-medium">{nc.iso_clause_number}</div>
                </div>
              )}
            </div>
          </div>

          {/* Timeline */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold mb-4">Timeline</h2>
            <div className="space-y-3">
              <div>
                <div className="text-sm text-gray-600">Created</div>
                <div className="font-medium text-sm">{formatDateTime(nc.created_at)}</div>
              </div>

              <div>
                <div className="text-sm text-gray-600">Last Updated</div>
                <div className="font-medium text-sm">{formatDateTime(nc.updated_at)}</div>
              </div>

              {nc.target_closure_date && (
                <div>
                  <div className="text-sm text-gray-600">Target Closure</div>
                  <div className="font-medium">{formatDate(nc.target_closure_date)}</div>
                </div>
              )}

              {nc.actual_closure_date && (
                <div>
                  <div className="text-sm text-gray-600">Actual Closure</div>
                  <div className="font-medium">{formatDate(nc.actual_closure_date)}</div>
                </div>
              )}

              {nc.verified_at && (
                <div>
                  <div className="text-sm text-gray-600">Verified</div>
                  <div className="font-medium text-sm">{formatDateTime(nc.verified_at)}</div>
                  {nc.verified_by && (
                    <div className="text-xs text-gray-500 mt-1">by {nc.verified_by}</div>
                  )}
                </div>
              )}
            </div>
          </div>

          {/* Actions */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold mb-4">Actions</h2>
            <div className="space-y-2">
              <button
                onClick={() => router.push(`/artifacts/ca/create?nc_id=${nc.id}`)}
                className="w-full bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg transition"
              >
                Create Corrective Action
              </button>
              <button
                className="w-full bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg transition"
              >
                Update Status
              </button>
              <button
                className="w-full bg-purple-600 hover:bg-purple-700 text-white px-4 py-2 rounded-lg transition"
              >
                Add Root Cause
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
