/**
 * Reusable Chart Components for Analytics Dashboard
 * Built with recharts library
 */

'use client';

import React from 'react';
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  AreaChart,
  Area,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer
} from 'recharts';

// Color palette for charts
export const COLORS = {
  primary: '#3b82f6',      // blue-500
  secondary: '#10b981',    // green-500
  tertiary: '#f59e0b',     // amber-500
  danger: '#ef4444',       // red-500
  purple: '#8b5cf6',       // purple-500
  pink: '#ec4899',         // pink-500
  indigo: '#6366f1',       // indigo-500
  teal: '#14b8a6',         // teal-500
};

export const PIE_COLORS = [
  COLORS.primary,
  COLORS.secondary,
  COLORS.tertiary,
  COLORS.danger,
  COLORS.purple,
  COLORS.pink,
  COLORS.indigo,
  COLORS.teal,
];

interface TrendLineChartProps {
  data: any[];
  xKey: string;
  yKeys: { key: string; name: string; color: string }[];
  title: string;
  height?: number;
}

export function TrendLineChart({ data, xKey, yKeys, title, height = 300 }: TrendLineChartProps) {
  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">{title}</h3>
      <ResponsiveContainer width="100%" height={height}>
        <LineChart data={data} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
          <XAxis dataKey={xKey} stroke="#6b7280" style={{ fontSize: '12px' }} />
          <YAxis stroke="#6b7280" style={{ fontSize: '12px' }} />
          <Tooltip
            contentStyle={{
              backgroundColor: '#fff',
              border: '1px solid #e5e7eb',
              borderRadius: '6px',
            }}
          />
          <Legend wrapperStyle={{ fontSize: '12px' }} />
          {yKeys.map((yKey) => (
            <Line
              key={yKey.key}
              type="monotone"
              dataKey={yKey.key}
              name={yKey.name}
              stroke={yKey.color}
              strokeWidth={2}
              dot={{ r: 4 }}
              activeDot={{ r: 6 }}
            />
          ))}
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}

interface TrendBarChartProps {
  data: any[];
  xKey: string;
  yKeys: { key: string; name: string; color: string }[];
  title: string;
  height?: number;
  stacked?: boolean;
}

export function TrendBarChart({ data, xKey, yKeys, title, height = 300, stacked = false }: TrendBarChartProps) {
  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">{title}</h3>
      <ResponsiveContainer width="100%" height={height}>
        <BarChart data={data} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
          <XAxis dataKey={xKey} stroke="#6b7280" style={{ fontSize: '12px' }} />
          <YAxis stroke="#6b7280" style={{ fontSize: '12px' }} />
          <Tooltip
            contentStyle={{
              backgroundColor: '#fff',
              border: '1px solid #e5e7eb',
              borderRadius: '6px',
            }}
          />
          <Legend wrapperStyle={{ fontSize: '12px' }} />
          {yKeys.map((yKey) => (
            <Bar
              key={yKey.key}
              dataKey={yKey.key}
              name={yKey.name}
              fill={yKey.color}
              stackId={stacked ? 'stack' : undefined}
              radius={[4, 4, 0, 0]}
            />
          ))}
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}

interface TrendAreaChartProps {
  data: any[];
  xKey: string;
  yKeys: { key: string; name: string; color: string }[];
  title: string;
  height?: number;
}

export function TrendAreaChart({ data, xKey, yKeys, title, height = 300 }: TrendAreaChartProps) {
  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">{title}</h3>
      <ResponsiveContainer width="100%" height={height}>
        <AreaChart data={data} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
          <defs>
            {yKeys.map((yKey) => (
              <linearGradient key={`gradient-${yKey.key}`} id={`gradient-${yKey.key}`} x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor={yKey.color} stopOpacity={0.8} />
                <stop offset="95%" stopColor={yKey.color} stopOpacity={0.1} />
              </linearGradient>
            ))}
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
          <XAxis dataKey={xKey} stroke="#6b7280" style={{ fontSize: '12px' }} />
          <YAxis stroke="#6b7280" style={{ fontSize: '12px' }} />
          <Tooltip
            contentStyle={{
              backgroundColor: '#fff',
              border: '1px solid #e5e7eb',
              borderRadius: '6px',
            }}
          />
          <Legend wrapperStyle={{ fontSize: '12px' }} />
          {yKeys.map((yKey) => (
            <Area
              key={yKey.key}
              type="monotone"
              dataKey={yKey.key}
              name={yKey.name}
              stroke={yKey.color}
              fill={`url(#gradient-${yKey.key})`}
              strokeWidth={2}
            />
          ))}
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}

interface DonutChartProps {
  data: any[];
  nameKey: string;
  valueKey: string;
  title: string;
  height?: number;
}

export function DonutChart({ data, nameKey, valueKey, title, height = 300 }: DonutChartProps) {
  const total = data.reduce((sum, item) => sum + item[valueKey], 0);

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">{title}</h3>
      <ResponsiveContainer width="100%" height={height}>
        <PieChart>
          <Pie
            data={data}
            cx="50%"
            cy="50%"
            innerRadius={60}
            outerRadius={90}
            paddingAngle={2}
            dataKey={valueKey}
            nameKey={nameKey}
            label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
            labelLine={{ stroke: '#6b7280', strokeWidth: 1 }}
          >
            {data.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={PIE_COLORS[index % PIE_COLORS.length]} />
            ))}
          </Pie>
          <Tooltip
            contentStyle={{
              backgroundColor: '#fff',
              border: '1px solid #e5e7eb',
              borderRadius: '6px',
            }}
          />
        </PieChart>
      </ResponsiveContainer>
      <div className="mt-4 text-center">
        <p className="text-2xl font-bold text-gray-900">{total}</p>
        <p className="text-sm text-gray-500">Total</p>
      </div>
    </div>
  );
}

interface MetricCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  trend?: {
    value: number;
    isPositive: boolean;
  };
  icon?: React.ReactNode;
  color?: 'blue' | 'green' | 'red' | 'yellow' | 'purple';
}

export function MetricCard({ title, value, subtitle, trend, icon, color = 'blue' }: MetricCardProps) {
  const colorClasses = {
    blue: 'bg-blue-100 text-blue-600',
    green: 'bg-green-100 text-green-600',
    red: 'bg-red-100 text-red-600',
    yellow: 'bg-yellow-100 text-yellow-600',
    purple: 'bg-purple-100 text-purple-600',
  };

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="flex items-center justify-between">
        <div className="flex-1">
          <p className="text-sm font-medium text-gray-600">{title}</p>
          <p className="mt-2 text-3xl font-bold text-gray-900">{value}</p>
          {subtitle && (
            <p className="mt-1 text-sm text-gray-500">{subtitle}</p>
          )}
          {trend && (
            <div className="mt-2 flex items-center gap-1">
              <span className={`text-sm font-medium ${trend.isPositive ? 'text-green-600' : 'text-red-600'}`}>
                {trend.isPositive ? '↑' : '↓'} {Math.abs(trend.value)}%
              </span>
              <span className="text-xs text-gray-500">vs last period</span>
            </div>
          )}
        </div>
        {icon && (
          <div className={`flex-shrink-0 w-12 h-12 rounded-full ${colorClasses[color]} flex items-center justify-center`}>
            {icon}
          </div>
        )}
      </div>
    </div>
  );
}
