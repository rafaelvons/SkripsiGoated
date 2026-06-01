// Mapping label SVM dari model (5 kelas)
export type BabyStatus = 'belly_pain' | 'burping' | 'discomfort' | 'hungry' | 'tired';

export interface BabySnapshot {
  status: BabyStatus;
  confidence: number;
  timestamp: Date;
  label: string; // raw label dari Firebase
}

export interface ChartPoint {
  time: string;
  confidence: number;
  label: string;
}

export interface EventLog {
  id: string;
  time: string;
  message: string;
  type: 'info' | 'warning' | 'danger';
}

const STATUS_LABELS: Record<BabyStatus, string> = {
  belly_pain: 'Sakit Perut',
  burping:    'Ingin Bersendawa',
  discomfort: 'Tidak Nyaman',
  hungry:     'Lapar',
  tired:      'Kelelahan',
};

const STATUS_LABELS_EN: Record<BabyStatus, string> = {
  belly_pain: 'Belly Pain',
  burping:    'Needs Burping',
  discomfort: 'Discomfort',
  hungry:     'Hungry',
  tired:      'Tired',
};

export function getStatusLabel(status: BabyStatus): string {
  return STATUS_LABELS[status] ?? status;
}

export function getStatusLabelEN(status: BabyStatus): string {
  return STATUS_LABELS_EN[status] ?? status;
}

export function formatTime(date: Date): string {
  return date.toLocaleTimeString('id-ID', {
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
    hour12: false,
  });
}

export function generateEventMessage(
  prev: BabySnapshot | null,
  current: BabySnapshot
): string | null {
  if (!prev) return null;
  if (prev.status === current.status) return null;

  const transitions: Record<BabyStatus, string> = {
    belly_pain: 'Terdeteksi: Bayi kemungkinan sakit perut',
    burping:    'Terdeteksi: Bayi ingin bersendawa',
    discomfort: 'Terdeteksi: Bayi merasa tidak nyaman',
    hungry:     'Terdeteksi: Bayi lapar — perlu menyusu',
    tired:      'Terdeteksi: Bayi kelelahan dan mengantuk',
  };

  return transitions[current.status] ?? `Status berubah: ${current.status}`;
}
