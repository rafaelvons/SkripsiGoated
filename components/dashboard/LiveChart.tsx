'use client';

import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine,
} from 'recharts';
import { Activity } from 'lucide-react';
import { ChartPoint, BabyStatus } from '@/lib/babyMonitor';

interface LiveChartProps {
  data: ChartPoint[];
}

const LABEL_COLORS: Record<BabyStatus, string> = {
  belly_pain: '#fb7185',
  burping:    '#38bdf8',
  discomfort: '#fb923c',
  hungry:     '#fbbf24',
  tired:      '#34d399',
};

function CustomTooltip({
  active,
  payload,
  label,
}: {
  active?: boolean;
  payload?: Array<{ name: string; value: number; payload: ChartPoint }>;
  label?: string;
}) {
  if (!active || !payload?.length) return null;
  const point = payload[0].payload;
  const color = LABEL_COLORS[point.label as BabyStatus] ?? '#6366f1';

  return (
    <div className="bg-white border border-slate-200 rounded-xl shadow-lg px-4 py-3 text-xs">
      <p className="text-slate-500 font-medium mb-2">{label}</p>
      <div className="flex items-center gap-2">
        <span className="w-2.5 h-2.5 rounded-full flex-shrink-0" style={{ backgroundColor: color }} />
        <span className="text-slate-600 capitalize">{point.label?.replace('_', ' ')}</span>
        <span className="font-bold text-slate-800 ml-auto">{payload[0].value}%</span>
      </div>
    </div>
  );
}

export default function LiveChart({ data }: LiveChartProps) {
  return (
    <div className="bg-white rounded-xl border border-gray-200 p-5 md:p-6">
      <div className="flex items-start md:items-center justify-between mb-5 md:mb-6 flex-col md:flex-row gap-4 md:gap-3">
        <div className="flex items-center gap-2 md:gap-3">
          <div className="bg-blue-50 border border-blue-100 rounded-lg p-2 md:p-2.5">
            <Activity className="w-4 h-4 md:w-5 md:h-5 text-blue-600" />
          </div>
          <div>
            <h2 className="text-[10px] md:text-[11px] font-semibold tracking-widest uppercase text-slate-500">
              Grafik Confidence SVM
            </h2>
            <p className="text-[11px] md:text-xs text-slate-400 mt-0.5">
              {data.length} deteksi terakhir
            </p>
          </div>
        </div>

        {/* Legend kelas */}
        <div className="flex flex-wrap items-center gap-3 text-[10px] text-slate-500">
          {(Object.entries(LABEL_COLORS) as [BabyStatus, string][]).map(([label, color]) => (
            <span key={label} className="flex items-center gap-1.5">
              <span className="w-2.5 h-2.5 rounded-full inline-block" style={{ backgroundColor: color }} />
              <span className="capitalize">{label.replace('_', ' ')}</span>
            </span>
          ))}
        </div>
      </div>

      <div className="h-64 sm:h-80">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={data} margin={{ top: 4, right: 8, left: -20, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" vertical={false} />
            <XAxis
              dataKey="time"
              tick={{ fontSize: 9, fill: '#94a3b8' }}
              tickLine={false}
              axisLine={false}
              interval="preserveStartEnd"
            />
            <YAxis
              domain={[0, 100]}
              tick={{ fontSize: 10, fill: '#94a3b8' }}
              tickLine={false}
              axisLine={false}
              tickFormatter={(v) => `${v}%`}
            />
            <Tooltip content={<CustomTooltip />} />
            <ReferenceLine y={80} stroke="#e2e8f0" strokeDasharray="4 4" label={{ value: '80%', position: 'insideRight', fontSize: 9, fill: '#cbd5e1' }} />
            <Line
              type="monotone"
              dataKey="confidence"
              name="Confidence"
              stroke="#6366f1"
              strokeWidth={2.5}
              dot={(props) => {
                const { cx, cy, payload } = props;
                const color = LABEL_COLORS[payload.label as BabyStatus] ?? '#6366f1';
                return <circle key={`dot-${cx}-${cy}`} cx={cx} cy={cy} r={4} fill={color} stroke="white" strokeWidth={1.5} />;
              }}
              activeDot={{ r: 5, strokeWidth: 0, fill: '#6366f1' }}
              isAnimationActive={false}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
