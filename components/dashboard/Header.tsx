'use client';

import { Baby, Wifi, Mic } from 'lucide-react';

interface HeaderProps {
  isConnected: boolean;
}

export default function Header({ isConnected }: HeaderProps) {
  return (
    <header className="w-full bg-white border-b border-gray-200 sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-3 sm:px-6 lg:px-8 py-3 md:py-4 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 flex-wrap">
        <div className="flex items-center gap-3 md:gap-4 w-full sm:w-auto justify-between sm:justify-start">
          <div className="flex items-center gap-3">
            <div className="bg-blue-100 rounded-xl p-2.5 md:p-3">
              <Baby className="w-5 h-5 md:w-6 md:h-6 text-blue-600" />
            </div>
            <div>
              <h1 className="text-xl md:text-2xl font-bold text-slate-800 tracking-tight leading-none">
                Baby<span className="font-normal text-slate-500">Voice</span>
              </h1>
              <p className="text-[9px] md:text-[10px] uppercase text-slate-400 font-semibold tracking-widest mt-1">
                IoT Baby Cry Monitor
              </p>
            </div>
          </div>
        </div>

        <div className="flex items-center gap-2 md:gap-3 flex-wrap w-full sm:w-auto">
          {/* Connection status */}
          <div className="flex-1 sm:flex-none flex items-center justify-center gap-2 bg-white border border-gray-200 rounded-full px-3 md:px-4 py-1.5 md:py-2">
            <span className="relative flex h-2 w-2 md:h-2.5 md:w-2.5">
              {isConnected && (
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-50" />
              )}
              <span
                className={`relative inline-flex rounded-full h-2 w-2 md:h-2.5 md:w-2.5 ${
                  isConnected ? 'bg-green-500' : 'bg-red-500'
                }`}
              />
            </span>
            <span className="text-[11px] md:text-xs font-medium text-slate-600 whitespace-nowrap">
              {isConnected ? 'System Online' : 'Connecting...'}
            </span>
            <Wifi
              className={`w-3.5 h-3.5 md:w-4 md:h-4 ml-1 hidden min-[360px]:block ${
                isConnected ? 'text-green-500' : 'text-slate-400'
              }`}
            />
          </div>

          {/* Mic badge */}
          <div className="flex-1 sm:flex-none flex items-center justify-center gap-2 rounded-full px-3 md:px-4 py-1.5 md:py-2 text-[11px] md:text-xs font-medium border bg-blue-50 border-blue-200 text-blue-700 whitespace-nowrap">
            <Mic className="w-3.5 h-3.5 md:w-4 md:h-4" />
            Audio Monitoring
          </div>
        </div>
      </div>
    </header>
  );
}
