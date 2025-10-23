"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

interface TrainingRecord {
  id: string;
  employee_id: string;
  training_title: string;
  training_date: string;
  trainer_name: string | null;
  training_hours: number | null;
  training_type: string | null;
  competency_area: string | null;
  passed: boolean | null;
  score: number | null;
  certificate_number: string | null;
  expiry_date: string | null;
  notes: string | null;
  created_at: string;
}

export default function TrainingRecordsPage() {
  const router = useRouter();
  const [records, setRecords] = useState<TrainingRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [employeeFilter, setEmployeeFilter] = useState<string>("all");
  const [competencyFilter, setCompetencyFilter] = useState<string>("all");

  useEffect(() => {
    fetchRecords();
  }, [employeeFilter, competencyFilter]);

  const fetchRecords = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem("access_token");
      
      let url = "http://localhost:8889/api/v1/artifacts/training";
      const params = new URLSearchParams();
      
      if (employeeFilter !== "all") {
        params.append("employee_id", employeeFilter);
      }
      
      if (competencyFilter !== "all") {
        params.append("competency_area", competencyFilter);
      }
      
      if (params.toString()) {
        url += `?${params.toString()}`;
      }

      const response = await fetch(url, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        throw new Error("Failed to fetch training records");
      }

      const data = await response.json();
      setRecords(data);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "An error occurred");
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString();
  };

  const isExpiringSoon = (expiryDate: string | null): boolean => {
    if (!expiryDate) return false;
    const expiry = new Date(expiryDate);
    const now = new Date();
    const daysUntilExpiry = Math.floor((expiry.getTime() - now.getTime()) / (1000 * 60 * 60 * 24));
    return daysUntilExpiry > 0 && daysUntilExpiry <= 30;
  };

  const isExpired = (expiryDate: string | null): boolean => {
    if (!expiryDate) return false;
    return new Date(expiryDate) < new Date();
  };

  const getUniqueCompetencyAreas = () => {
    const areas = records
      .map(r => r.competency_area)
      .filter((area): area is string => area !== null);
    return Array.from(new Set(areas));
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center min-h-screen">
        <div className="text-lg">Loading training records...</div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold">Training Records</h1>
        <button
          onClick={() => router.push("/artifacts/training/create")}
          className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-lg transition"
        >
          Add Training Record
        </button>
      </div>

      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
          {error}
        </div>
      )}

      {/* Statistics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        <div className="bg-white p-4 rounded-lg shadow">
          <div className="text-gray-600 text-sm">Total Records</div>
          <div className="text-2xl font-bold">{records.length}</div>
        </div>
        <div className="bg-white p-4 rounded-lg shadow">
          <div className="text-gray-600 text-sm">Passed</div>
          <div className="text-2xl font-bold text-green-600">
            {records.filter(r => r.passed === true).length}
          </div>
        </div>
        <div className="bg-white p-4 rounded-lg shadow">
          <div className="text-gray-600 text-sm">With Certificates</div>
          <div className="text-2xl font-bold">
            {records.filter(r => r.certificate_number !== null).length}
          </div>
        </div>
        <div className="bg-white p-4 rounded-lg shadow">
          <div className="text-gray-600 text-sm">Expiring Soon</div>
          <div className="text-2xl font-bold text-orange-600">
            {records.filter(r => isExpiringSoon(r.expiry_date)).length}
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="bg-white p-4 rounded-lg shadow mb-6">
        <div className="flex gap-4">
          <div>
            <label className="block text-sm font-medium mb-1">Competency Area</label>
            <select
              value={competencyFilter}
              onChange={(e) => setCompetencyFilter(e.target.value)}
              className="border rounded px-3 py-2"
            >
              <option value="all">All Areas</option>
              {getUniqueCompetencyAreas().map(area => (
                <option key={area} value={area}>{area}</option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {/* Training Records List */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                Employee ID
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                Training Title
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                Training Date
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                Competency Area
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                Hours
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                Status
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                Certificate
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                Expiry
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                Actions
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {records.length === 0 ? (
              <tr>
                <td colSpan={9} className="px-6 py-4 text-center text-gray-500">
                  No training records found. Add your first training record!
                </td>
              </tr>
            ) : (
              records.map((record) => (
                <tr key={record.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap font-medium">
                    {record.employee_id}
                  </td>
                  <td className="px-6 py-4">
                    <div className="text-sm text-gray-900 max-w-xs">
                      {record.training_title}
                    </div>
                    {record.trainer_name && (
                      <div className="text-xs text-gray-500">
                        Trainer: {record.trainer_name}
                      </div>
                    )}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    {formatDate(record.training_date)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    {record.competency_area ? (
                      <span className="inline-flex px-2 py-1 text-xs font-semibold rounded-full bg-purple-100 text-purple-800">
                        {record.competency_area}
                      </span>
                    ) : (
                      <span className="text-gray-400 text-sm">-</span>
                    )}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    {record.training_hours ? `${record.training_hours}h` : "-"}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    {record.passed === true && (
                      <span className="inline-flex px-2 py-1 text-xs font-semibold rounded-full bg-green-100 text-green-800">
                        ✓ Passed
                      </span>
                    )}
                    {record.passed === false && (
                      <span className="inline-flex px-2 py-1 text-xs font-semibold rounded-full bg-red-100 text-red-800">
                        ✗ Failed
                      </span>
                    )}
                    {record.passed === null && (
                      <span className="text-gray-400 text-sm">N/A</span>
                    )}
                    {record.score !== null && (
                      <div className="text-xs text-gray-500 mt-1">
                        Score: {record.score}%
                      </div>
                    )}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    {record.certificate_number ? (
                      <span className="text-sm text-blue-600 font-mono">
                        {record.certificate_number}
                      </span>
                    ) : (
                      <span className="text-gray-400 text-sm">-</span>
                    )}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    {record.expiry_date ? (
                      <span className={`text-sm ${
                        isExpired(record.expiry_date)
                          ? "text-red-600 font-semibold"
                          : isExpiringSoon(record.expiry_date)
                          ? "text-orange-600 font-semibold"
                          : "text-gray-700"
                      }`}>
                        {formatDate(record.expiry_date)}
                        {isExpired(record.expiry_date) && " (Expired)"}
                        {isExpiringSoon(record.expiry_date) && " (Soon)"}
                      </span>
                    ) : (
                      <span className="text-gray-400 text-sm">No expiry</span>
                    )}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">
                    <button
                      onClick={() => router.push(`/artifacts/training/${record.id}`)}
                      className="text-blue-600 hover:text-blue-800 mr-3"
                    >
                      View
                    </button>
                    <button
                      onClick={() => router.push(`/artifacts/training/${record.id}/edit`)}
                      className="text-green-600 hover:text-green-800"
                    >
                      Edit
                    </button>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
