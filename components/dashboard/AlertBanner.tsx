'use client';

import { TriangleAlert as AlertTriangle, CircleCheck as CheckCircle2, Info, Mic } from 'lucide-react';
import { BabyStatus } from '@/lib/babyMonitor';

interface AlertBannerProps {
  status: BabyStatus;
}

type AlertLevel = 'danger' | 'warning' | 'success' | 'info';

interface AlertConfig {
  level: AlertLevel;
  message: string;
  subtext: string;
  icon: React.ReactNode;
  classes: string;
  iconClasses: string;
}

function getAlertConfig(status: BabyStatus): AlertConfig {
  if (status === 'belly_pain') {
    return {
      level: 'danger',
      message: 'Perhatian: Bayi kemungkinan mengalami sakit perut!',
      subtext: 'Segera periksa kondisi bayi. Bisa jadi perlu ditenangkan atau diperiksa dokter.',
      icon: <AlertTriangle className="w-5 h-5 flex-shrink-0" />,
      classes: 'bg-red-50 border border-red-200 text-red-800',
      iconClasses: 'bg-red-100 text-red-600',
    };
  }

  if (status === 'hungry') {
    return {
      level: 'warning',
      message: 'Bayi Lapar — Perlu Menyusu',
      subtext: 'Classifier audio mendeteksi tangisan lapar. Segera berikan susu atau MPASI.',
      icon: <Info className="w-5 h-5 flex-shrink-0" />,
      classes: 'bg-yellow-50 border border-yellow-200 text-yellow-800',
      iconClasses: 'bg-yellow-100 text-yellow-600',
    };
  }

  if (status === 'discomfort') {
    return {
      level: 'warning',
      message: 'Bayi Tidak Nyaman',
      subtext: 'Periksa popok, suhu ruangan, atau posisi tidur bayi.',
      icon: <Info className="w-5 h-5 flex-shrink-0" />,
      classes: 'bg-orange-50 border border-orange-200 text-orange-800',
      iconClasses: 'bg-orange-100 text-orange-600',
    };
  }

  if (status === 'burping') {
    return {
      level: 'info',
      message: 'Bayi Ingin Bersendawa',
      subtext: 'Coba tegakkan bayi dan tepuk punggungnya perlahan setelah minum susu.',
      icon: <Mic className="w-5 h-5 flex-shrink-0" />,
      classes: 'bg-blue-50 border border-blue-200 text-blue-800',
      iconClasses: 'bg-blue-100 text-blue-600',
    };
  }

  // tired
  return {
    level: 'success',
    message: 'Bayi Kelelahan dan Mengantuk',
    subtext: 'Bayi ingin tidur. Pastikan lingkungan tenang dan nyaman.',
    icon: <CheckCircle2 className="w-5 h-5 flex-shrink-0" />,
    classes: 'bg-green-50 border border-green-200 text-green-800',
    iconClasses: 'bg-green-100 text-green-600',
  };
}

export default function AlertBanner({ status }: AlertBannerProps) {
  const config = getAlertConfig(status);

  return (
    <div
      className={`w-full rounded-xl p-4 sm:px-5 sm:py-4 flex flex-col sm:flex-row items-start gap-3 sm:gap-4 ${config.classes}`}
      role="alert"
    >
      <div className={`rounded-lg p-2 sm:p-2.5 mt-0.5 ${config.iconClasses}`}>
        {config.icon}
      </div>
      <div className="min-w-0 flex-1">
        <p className="font-semibold text-[13px] sm:text-[15px] leading-snug">
          {config.message}
        </p>
        <p className="text-[11px] sm:text-[13px] mt-1 font-normal opacity-80">{config.subtext}</p>
      </div>
    </div>
  );
}

