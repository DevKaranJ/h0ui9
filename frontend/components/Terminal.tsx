"use client";

import { useEffect, useState } from 'react';
import { Activity, Briefcase, Layers, Crosshair } from 'lucide-react';

// Cache the expensive Intl.NumberFormat instantiation outside the render loop
// This improves performance significantly as the terminal re-renders up to 10x/sec
const moneyFormatter = new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' });

export default function Terminal() {
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const [data, setData] = useState<any>(null);
  const [connected, setConnected] = useState(false);

  useEffect(() => {
    // Connect to backend websocket
    const ws = new WebSocket('ws://127.0.0.1:8000/ws');

    ws.onopen = () => {
      setConnected(true);
    };

    ws.onmessage = (event) => {
      const parsed = JSON.parse(event.data);
      setData(parsed);
    };

    ws.onclose = () => {
      setConnected(false);
    };

    return () => ws.close();
  }, []);

  if (!connected) {
    return (
      <div className="flex items-center justify-center h-screen w-full bg-black" role="status" aria-live="polite">
        <div className="text-gray-500 animate-pulse flex items-center gap-3 font-mono">
          <Activity size={20} aria-hidden="true" />
          Connecting to Order Flow Engine...
        </div>
      </div>
    );
  }

  const portfolio = data?.portfolio;
  const strategy = data?.strategy;
  const footprint = data?.footprint;

  // Formatting helpers
  const formatMoney = (val: number) => moneyFormatter.format(val);

  return (
    <div className="p-4 h-screen grid grid-cols-12 grid-rows-6 gap-4 font-mono text-sm">

      {/* Header Bar */}
      <div className="col-span-12 row-span-1 terminal-panel flex items-center justify-between !py-2 !px-6 border-b border-gray-800">
        <div className="flex items-center gap-4">
          <div className="h-3 w-3 rounded-full bg-green-500 shadow-[0_0_10px_rgba(34,197,94,0.6)]"></div>
          <span className="font-bold text-lg tracking-widest text-white">FINCEPT // TERMINAL</span>
          <span className="text-gray-600">v1.0.0-beta</span>
        </div>
        <div className="flex gap-6 text-gray-400">
          <div className="flex items-center gap-2">
            <span className="text-xs">MARKET:</span>
            <span className="text-white font-bold">BTC/USDT PERP</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="text-xs">STATUS:</span>
            <span className="text-green-400 font-bold">LIVE DATA</span>
          </div>
        </div>
      </div>

      {/* Main Data Feed (Footprint) */}
      <div className="col-span-8 row-span-4 terminal-panel flex flex-col">
        <div className="terminal-header flex justify-between items-center">
          <span className="flex items-center gap-2"><Layers size={16} aria-hidden="true" /> ORDER FLOW / FOOTPRINT (5M)</span>
          <span className="text-green-400 font-bold">{strategy?.current_price ? formatMoney(strategy.current_price) : '---'}</span>
        </div>

        <div className="flex-1 overflow-y-auto pr-2">
          {footprint?.levels ? (
            <table className="w-full text-right border-collapse">
              <thead>
                <tr className="text-gray-500 text-xs border-b border-gray-800">
                  <th className="pb-2 text-left font-normal w-1/4">PRICE</th>
                  <th className="pb-2 text-red-400 font-normal w-1/3">SELL VOL (BID)</th>
                  <th className="pb-2 text-green-400 font-normal w-1/3">BUY VOL (ASK)</th>
                  <th className="pb-2 text-gray-400 font-normal">DELTA</th>
                </tr>
              </thead>
              <tbody>
                {Object.keys(footprint.levels)
                  .map(Number)
                  .sort((a, b) => b - a)
                  .slice(0, 50) // Show top 50 levels closest to price
                  .map((price) => {
                    const level = footprint.levels[price];
                    const delta = level.buy - level.sell;
                    const maxVol = 10; // Simple normalization factor for visual bar

                    return (
                      <tr key={price} className="border-b border-gray-800/50 hover:bg-gray-800/20">
                        <td className="py-1.5 text-left text-gray-300 relative">
                           {price.toFixed(1)}
                           {Math.abs(price - strategy.current_price) < 0.6 && (
                             <div className="absolute left-[-8px] top-1/2 -translate-y-1/2 h-full w-[2px] bg-yellow-400"></div>
                           )}
                        </td>
                        <td className="py-1.5 text-red-400/80 relative pr-4">
                          <div className="absolute right-0 top-0 h-full bg-red-900/20" style={{ width: `${Math.min((level.sell/maxVol)*100, 100)}%` }}></div>
                          {level.sell > 0 ? level.sell.toFixed(3) : '-'}
                        </td>
                        <td className="py-1.5 text-green-400/80 relative pr-4">
                          <div className="absolute right-0 top-0 h-full bg-green-900/20" style={{ width: `${Math.min((level.buy/maxVol)*100, 100)}%` }}></div>
                          {level.buy > 0 ? level.buy.toFixed(3) : '-'}
                        </td>
                        <td className={`py-1.5 ${delta > 0 ? 'text-green-500' : delta < 0 ? 'text-red-500' : 'text-gray-600'}`}>
                          {delta > 0 ? '+' : ''}{delta.toFixed(3)}
                        </td>
                      </tr>
                    );
                })}
              </tbody>
            </table>
          ) : (
            <div className="h-full flex flex-col items-center justify-center text-gray-600 gap-2">
              <Activity size={24} className="opacity-50" aria-hidden="true" />
              <span>Awaiting Tick Data...</span>
            </div>
          )}
        </div>
      </div>

      {/* Portfolio & Risk Panel */}
      <div className="col-span-4 row-span-2 terminal-panel flex flex-col">
        <div className="terminal-header flex items-center gap-2"><Briefcase size={16} aria-hidden="true" /> PORTFOLIO & RISK (PAPER)</div>
        <div className="flex-1 flex flex-col gap-4">
          <div className="grid grid-cols-2 gap-4">
            <div className="bg-black border border-gray-800 p-3 rounded">
              <div className="text-gray-500 text-xs mb-1">EQUITY</div>
              <div className="text-xl text-white">{portfolio ? formatMoney(portfolio.equity) : '---'}</div>
            </div>
            <div className="bg-black border border-gray-800 p-3 rounded">
              <div className="text-gray-500 text-xs mb-1">AVAILABLE BALANCE</div>
              <div className="text-xl text-gray-300">{portfolio ? formatMoney(portfolio.balance) : '---'}</div>
            </div>
          </div>

          <div className="bg-black border border-gray-800 p-3 rounded flex-1">
            <div className="text-gray-500 text-xs mb-2 border-b border-gray-800 pb-2">ACTIVE POSITIONS ({portfolio?.open_positions?.length || 0})</div>
            {portfolio?.open_positions?.length > 0 ? (
              <div className="space-y-2">
                {/* eslint-disable-next-line @typescript-eslint/no-explicit-any */}
                {portfolio.open_positions.map((pos: any, idx: number) => (
                  <div key={idx} className="flex justify-between items-center text-xs">
                    <span className={`font-bold ${pos.action === 'LONG' ? 'text-green-400' : 'text-red-400'}`}>
                      {pos.action} {pos.size.toFixed(4)}
                    </span>
                    <span className="text-gray-400">@ {pos.entry_price.toFixed(1)}</span>
                    <span className={`font-bold ${pos.pnl >= 0 ? 'text-green-500' : 'text-red-500'}`}>
                      {pos.pnl >= 0 ? '+' : ''}{formatMoney(pos.pnl)}
                    </span>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-gray-600 text-xs h-full flex flex-col items-center justify-center gap-2">
                <Briefcase size={20} className="opacity-50" aria-hidden="true" />
                <span>No active positions</span>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Strategy Metrics Panel */}
      <div className="col-span-4 row-span-2 terminal-panel flex flex-col">
        <div className="terminal-header flex items-center gap-2"><Crosshair size={16} aria-hidden="true" /> STRATEGY ENGINE</div>

        <div className="grid grid-cols-2 gap-3 mb-4">
            <div className="bg-black border border-gray-800 p-3 rounded">
              <div className="text-gray-500 text-xs mb-1">CUMULATIVE DELTA (CVD)</div>
              <div className={`text-lg ${strategy?.cvd > 0 ? 'text-green-500' : 'text-red-500'}`}>
                {strategy?.cvd ? (strategy.cvd > 0 ? '+' : '') + strategy.cvd.toFixed(2) : '0.00'}
              </div>
            </div>
            <div className="bg-black border border-gray-800 p-3 rounded">
              <div className="text-gray-500 text-xs mb-1">TOTAL TRADES</div>
              <div className="text-lg text-white">{portfolio?.total_trades || 0}</div>
            </div>
        </div>

        <div className="bg-black border border-gray-800 p-3 rounded flex-1">
            <div className="text-gray-500 text-xs mb-2 border-b border-gray-800 pb-2">HTF STRUCTURAL ZONES</div>
            <div className="space-y-2 text-xs">
              <div className="flex justify-between text-gray-400">
                <span>Supply Zone (4H)</span>
                <span className="text-gray-500">Feature pending...</span>
              </div>
              <div className="flex justify-between text-gray-400">
                <span>Demand Zone (4H)</span>
                <span className="text-gray-500">Feature pending...</span>
              </div>
            </div>
        </div>
      </div>

      {/* System Logs */}
      <div className="col-span-12 row-span-1 terminal-panel">
        <div className="terminal-header flex justify-between">
          <span>SYSTEM LOGS</span>
          <span className="text-green-500 animate-pulse">● REC</span>
        </div>
        <div className="text-xs text-gray-500 font-mono space-y-1 h-full overflow-hidden">
          <div>[SYSTEM] Initialized Paper Trading Engine with $10,000.00 starting equity.</div>
          <div>[RISK] Constraints active: 10% Max Drawdown, 1% Risk Per Trade.</div>
          <div>[NETWORK] Connected to Binance wss://fstream.binance.com/ws/btcusdt@aggTrade</div>
          <div>[STRATEGY] Footprint Engine initialized. Timeframe: 5M. Tick size: 0.5. Waiting for Absorption-Initiation Pattern...</div>
          {strategy?.signal && (
            <div className="text-yellow-400">
              [SIGNAL] {strategy.signal.action} condition met at {strategy.signal.price}. Evaluating risk execution...
            </div>
          )}
        </div>
      </div>

    </div>
  );
}
