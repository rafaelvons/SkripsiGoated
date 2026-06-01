'use client';

import { ClipboardList, CircleAlert as AlertCircle, CircleCheck as CheckCircle2, Info } from 'lucide-react';
import { EventLog as EventLogType } from '@/lib/babyMonitor';

interface EventLogProps {
  events: EventLogType[];
}

function EventIcon({ type }: { type: EventLogType['type'] }) {
  if (type === 'danger') {
    return (
      <div className="w-7 h-7 rounded-full bg-red-100 flex items-center justify-center flex-shrink-0">
        <AlertCircle className="w-3.5 h-3.5 text-red-500" />
      </div>
    );
  }
  if (type === 'warning') {
    return (
      <div className="w-7 h-7 rounded-full bg-amber-100 flex items-center justify-center flex-shrink-0">
        <Info className="w-3.5 h-3.5 text-amber-500" />
      </div>
    );
  }
  return (
    <div className="w-7 h-7 rounded-full bg-emerald-100 flex items-center justify-center flex-shrink-0">
      <CheckCircle2 className="w-3.5 h-3.5 text-emerald-500" />
    </div>
  );
}

export default function EventLog({ events }: EventLogProps) {
  return (
    <div className="bg-white rounded-xl border border-gray-200 p-5 md:p-6">
      <div className="flex items-center gap-2 md:gap-3 mb-5 md:mb-6">
        <div className="bg-blue-50 border border-blue-100 rounded-lg p-2 md:p-2.5">
          <ClipboardList className="w-4 h-4 md:w-5 md:h-5 text-blue-600" />
        </div>
        <div>
          <h2 className="text-[10px] md:text-[11px] font-semibold tracking-widest uppercase text-slate-500">
            Recent Event Log
          </h2>
          <p className="text-[11px] md:text-xs text-slate-400 mt-0.5">
            {events.length} event{events.length !== 1 ? 's' : ''} recorded
          </p>
        </div>
      </div>

      <div className="space-y-1 max-h-72 overflow-y-auto pr-1 scrollbar-thin">
        {events.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-10 text-slate-400">
            <ClipboardList className="w-8 h-8 mb-2 opacity-40" />
            <p className="text-sm">No events yet. Monitoring...</p>
          </div>
        ) : (
          events.map((event, index) => (
            <div
              key={event.id}
              className={`flex items-start gap-3 px-3 py-2.5 rounded-lg transition-colors ${
                index === 0
                  ? 'bg-blue-50'
                  : 'hover:bg-gray-50'
              }`}
            >
              <EventIcon type={event.type} />
              <div className="min-w-0 flex-1">
                <p className="text-sm text-slate-700 font-medium leading-snug">
                  {event.message}
                </p>
                <p className="text-xs text-slate-400 mt-0.5 font-mono">{event.time}</p>
              </div>
              {index === 0 && (
                <span className="text-[10px] font-semibold text-blue-600 bg-blue-100 rounded-full px-2 py-0.5 flex-shrink-0">
                  NEW
                </span>
              )}
            </div>
          ))
        )}
      </div>
    </div>
  );
}
