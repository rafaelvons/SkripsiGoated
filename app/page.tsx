'use client';

import { useState, useEffect, useRef } from 'react';
import Header from '@/components/dashboard/Header';
import AlertBanner from '@/components/dashboard/AlertBanner';
import MonitoringCards from '@/components/dashboard/MonitoringCards';
import LiveChart from '@/components/dashboard/LiveChart';
import EventLog from '@/components/dashboard/EventLog';
import {
  BabySnapshot,
  ChartPoint,
  EventLog as EventLogType,
  generateEventMessage,
  formatTime,
  BabyStatus,
} from '@/lib/babyMonitor';
import { ref, onValue } from 'firebase/database';
import { database } from '@/lib/firebase';

const MAX_CHART_POINTS = 20;
const MAX_LOG_ENTRIES = 50;

const VALID_STATUSES: BabyStatus[] = ['belly_pain', 'burping', 'discomfort', 'hungry', 'tired'];

function buildChartPoint(snapshot: BabySnapshot): ChartPoint {
  return {
    time: formatTime(snapshot.timestamp),
    confidence: snapshot.confidence,
    label: snapshot.label,
  };
}


const DEFAULT_SNAPSHOT: BabySnapshot = {
  status: 'tired',
  label: 'tired',
  confidence: 0,
  timestamp: new Date(0), // fixed timestamp to avoid hydration mismatch
};

export default function DashboardPage() {
  const [snapshot, setSnapshot] = useState<BabySnapshot>(DEFAULT_SNAPSHOT);
  const [rtdbReady, setRtdbReady] = useState(false);
  const [chartData, setChartData] = useState<ChartPoint[]>([]);
  const [logs, setLogs] = useState<EventLogType[]>([]);

  const prevSnapshot = useRef<BabySnapshot | null>(null);
  const logIdCounter = useRef(0);

  useEffect(() => {
    const dbRef = ref(database, 'deteksi_bayi/latest_result');

    const unsubscribe = onValue(dbRef, (rtdbSnapshot) => {
      setRtdbReady(true);
      console.log('[Firebase] onValue fired, exists:', rtdbSnapshot.exists());

      if (!rtdbSnapshot.exists()) return;

      const docData = rtdbSnapshot.val() as Record<string, unknown>;
      const rawLabel = String(docData.label || '').toLowerCase().trim();
      const status: BabyStatus = VALID_STATUSES.includes(rawLabel as BabyStatus)
        ? (rawLabel as BabyStatus)
        : 'tired';

      const tsRaw = docData.timestamp;
      const timestamp = typeof tsRaw === 'number' ? new Date(tsRaw) : new Date();

      const next: BabySnapshot = {
        status,
        label: rawLabel,
        confidence: docData.confidence ? Math.round(docData.confidence as number) : 95,
        timestamp,
      };

      if (!prevSnapshot.current) {
        setSnapshot(next);
        setChartData([buildChartPoint(next)]);
        prevSnapshot.current = next;
        // Log entri pertama saat data pertama kali masuk
        const initLog: EventLogType = {
          id: String(logIdCounter.current++),
          time: formatTime(next.timestamp),
          message: `Sistem terhubung — Deteksi awal: ${
            next.status === 'belly_pain' ? 'Sakit Perut' :
            next.status === 'burping'    ? 'Ingin Bersendawa' :
            next.status === 'discomfort' ? 'Tidak Nyaman' :
            next.status === 'hungry'     ? 'Lapar' : 'Kelelahan'
          } (${Math.round(next.confidence)}%)`,
          type:
            next.status === 'belly_pain' ? 'danger' :
            next.status === 'hungry' || next.status === 'discomfort' ? 'warning' : 'info',
        };
        setLogs([initLog]);
        return;
      }

      const eventMsg = generateEventMessage(prevSnapshot.current, next);
      if (eventMsg) {
        const newLog: EventLogType = {
          id: String(logIdCounter.current++),
          time: formatTime(next.timestamp),
          message: eventMsg,
          type:
            next.status === 'belly_pain'
              ? 'danger'
              : next.status === 'hungry' || next.status === 'discomfort'
              ? 'warning'
              : 'info',
        };
        setLogs((prev) => [newLog, ...prev].slice(0, MAX_LOG_ENTRIES));
      }

      prevSnapshot.current = next;
      setSnapshot(next);
      setChartData((prev) => [...prev, buildChartPoint(next)].slice(-MAX_CHART_POINTS));
    }, (error) => {
      console.error('[Firebase] RTDB error:', error.code, error.message);
    });

    return () => unsubscribe();
  }, []);

  return (
    <div className="min-h-screen bg-gray-50 text-slate-800 font-sans">
      <Header isConnected={rtdbReady} />

      <main className="max-w-7xl mx-auto px-3 sm:px-6 lg:px-8 py-5 md:py-8 space-y-4 md:space-y-5">
        <AlertBanner status={snapshot.status} />

        <MonitoringCards
          status={snapshot.status}
          confidence={snapshot.confidence}
          timestamp={snapshot.timestamp}
        />

        <LiveChart data={chartData} />

        <EventLog events={logs} />

        <footer className="text-center text-xs text-slate-400 pb-8 pt-4 tracking-wide">
          Smart Baby Monitor v1.0 &mdash; ESP32 &middot; INMP441 Mic &middot; SVM Audio Classifier
        </footer>
      </main>
    </div>
  );
}
