'use client';

import { BrainCircuit, Mic2, Clock, Stethoscope, Wind, Frown, UtensilsCrossed, Moon } from 'lucide-react';
import { BabyStatus, getStatusLabel, getStatusLabelEN } from '@/lib/babyMonitor';

interface MonitoringCardsProps {
  status: BabyStatus;
  confidence: number;
  timestamp: Date;
}

const STATUS_CONFIG: Record<
  BabyStatus,
  { bg: string; text: string; dot: string; iconBg: string; icon: React.ReactNode; desc: string }
> = {
  belly_pain: {
    bg: 'bg-red-50 border border-red-200',
    text: 'text-red-700',
    dot: 'bg-red-500',
    iconBg: 'bg-red-100 text-red-600',
    icon: <Stethoscope className="w-5 h-5" />,
    desc: 'Bayi mungkin mengalami sakit perut atau kram.',
  },
  burping: {
    bg: 'bg-blue-50 border border-blue-200',
    text: 'text-blue-700',
    dot: 'bg-blue-500',
    iconBg: 'bg-blue-100 text-blue-600',
    icon: <Wind className="w-5 h-5" />,
    desc: 'Bayi perlu disendawakan setelah minum susu.',
  },
  discomfort: {
    bg: 'bg-orange-50 border border-orange-200',
    text: 'text-orange-700',
    dot: 'bg-orange-500',
    iconBg: 'bg-orange-100 text-orange-600',
    icon: <Frown className="w-5 h-5" />,
    desc: 'Bayi merasa tidak nyaman, periksa popok atau suhu.',
  },
  hungry: {
    bg: 'bg-yellow-50 border border-yellow-200',
    text: 'text-yellow-700',
    dot: 'bg-yellow-500',
    iconBg: 'bg-yellow-100 text-yellow-600',
    icon: <UtensilsCrossed className="w-5 h-5" />,
    desc: 'Bayi lapar dan butuh makan atau minum susu.',
  },
  tired: {
    bg: 'bg-green-50 border border-green-200',
    text: 'text-green-700',
    dot: 'bg-green-500',
    iconBg: 'bg-green-100 text-green-600',
    icon: <Moon className="w-5 h-5" />,
    desc: 'Bayi kelelahan dan ingin tidur.',
  },
};

export default function MonitoringCards({
  status,
  confidence,
  timestamp,
}: MonitoringCardsProps) {
  const cfg = STATUS_CONFIG[status];

  const timeStr = timestamp.toLocaleTimeString('id-ID', {
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
    hour12: false,
  });

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 md:gap-6">
      {/* === CARD 1: Hasil Klasifikasi SVM === */}
      <div className="bg-white rounded-xl border border-gray-200 p-5 md:p-6 flex flex-col gap-4 md:gap-5">
        {/* Header card */}
        <div className="flex items-center gap-2 md:gap-3">
          <div className="bg-blue-50 border border-blue-100 rounded-lg p-2 md:p-2.5">
            <BrainCircuit className="w-4 h-4 md:w-5 md:h-5 text-blue-600" />
          </div>
          <span className="text-[10px] md:text-[11px] font-semibold tracking-widest uppercase text-slate-500">
            Audio SVM Classifier
          </span>
        </div>

        {/* Status utama */}
        <div className={`rounded-lg p-4 md:p-5 ${cfg.bg} ${cfg.text} flex items-center gap-3 md:gap-4`}>
          <div className={`rounded-lg p-2.5 flex-shrink-0 ${cfg.iconBg}`}>
            {cfg.icon}
          </div>
          <div>
            <p className="text-lg md:text-2xl font-bold tracking-tight leading-tight">
              {getStatusLabel(status)}
            </p>
            <p className="text-[11px] md:text-xs font-medium opacity-70 mt-0.5">
              {getStatusLabelEN(status)}
            </p>
          </div>
          <span className={`ml-auto w-3 h-3 rounded-full flex-shrink-0 ${cfg.dot} animate-pulse`} />
        </div>

        {/* Deskripsi */}
        <p className="text-[12px] md:text-[13px] text-slate-500 leading-relaxed">
          {cfg.desc}
        </p>

        {/* Confidence bar */}
        <div className="flex items-center justify-between pt-4 md:pt-5 border-t border-gray-100">
          <span className="text-[10px] md:text-[11px] text-slate-400 font-semibold tracking-wider uppercase">
            Model Confidence
          </span>
          <div className="flex items-center gap-2 md:gap-3">
            <div className="w-20 md:w-28 h-2 bg-gray-100 border border-gray-200 rounded-full overflow-hidden">
              <div
                className="h-full bg-blue-500 rounded-full transition-all duration-700"
                style={{ width: `${confidence}%` }}
              />
            </div>
            <span className="text-xs md:text-sm font-bold text-slate-700">
              {confidence}%
            </span>
          </div>
        </div>
      </div>

      {/* === CARD 2: Audio & Waktu Deteksi === */}
      <div className="bg-white rounded-xl border border-gray-200 p-5 md:p-6 flex flex-col gap-4 md:gap-5">
        {/* Header card */}
        <div className="flex items-center gap-2 md:gap-3">
          <div className="bg-purple-50 border border-purple-100 rounded-lg p-2 md:p-2.5">
            <Mic2 className="w-4 h-4 md:w-5 md:h-5 text-purple-600" />
          </div>
          <span className="text-[10px] md:text-[11px] font-semibold tracking-widest uppercase text-slate-500">
            Informasi Deteksi
          </span>
        </div>

        {/* Detail statistik */}
        <div className="flex flex-col gap-4 flex-1 justify-center">
          {/* Confidence besar */}
          <div className="flex flex-col gap-1.5">
            <span className="text-[11px] text-slate-400 font-semibold tracking-wider uppercase">
              Tingkat Keyakinan Model
            </span>
            <div className="flex items-end gap-2">
              <span className="text-4xl md:text-5xl font-bold text-slate-800 leading-none">
                {confidence}
              </span>
              <span className="text-lg font-semibold text-slate-400 mb-1">%</span>
            </div>
            <div className="w-full h-3 bg-gray-100 rounded-full overflow-hidden">
              <div
                className={`h-full rounded-full transition-all duration-700 ${
                  confidence >= 80
                    ? 'bg-green-500'
                    : confidence >= 60
                    ? 'bg-yellow-500'
                    : 'bg-red-500'
                }`}
                style={{ width: `${confidence}%` }}
              />
            </div>
          </div>

          {/* Waktu deteksi */}
          <div className="flex items-center gap-3 bg-gray-50 rounded-xl px-4 py-3 border border-gray-100">
            <div className="bg-white border border-gray-200 rounded-lg p-2">
              <Clock className="w-4 h-4 text-slate-400" />
            </div>
            <div>
              <p className="text-[10px] text-slate-400 font-semibold tracking-wider uppercase">
                Waktu Deteksi Terakhir
              </p>
              <p className="text-sm font-bold text-slate-700 font-mono mt-0.5">
                {timeStr}
              </p>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="pt-4 md:pt-5 border-t border-gray-100 flex items-center justify-between text-[9px] md:text-[11px] text-slate-400 tracking-widest uppercase font-semibold">
          <span>ESP32 + INMP441</span>
          <span className="text-blue-600 bg-blue-50 px-2 py-0.5 rounded border border-blue-100">Real-time</span>
        </div>
      </div>
    </div>
  );
}

