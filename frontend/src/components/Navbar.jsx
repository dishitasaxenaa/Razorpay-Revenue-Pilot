import React from "react";
import { ShieldCheck, RefreshCw, Sliders, Zap } from "lucide-react";

export default function Navbar({ summary, onResetDemo, onOpenPolicy, isResetting }) {
  return (
    <header className="border-b border-slate-800 bg-slate-900/90 backdrop-blur sticky top-0 z-30">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        {/* Brand & Track */}
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-sky-600 to-indigo-600 flex items-center justify-center shadow-lg shadow-sky-500/20">
            <Zap className="w-5 h-5 text-white" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-extrabold text-lg tracking-tight text-white">Revenue Pilot</span>
              <span className="text-xs font-semibold px-2 py-0.5 rounded-full bg-sky-500/10 text-sky-400 border border-sky-500/30">
                Track 01: AI Growth & Agentic Commerce
              </span>
            </div>
            <p className="text-xs text-slate-400">Autonomous Merchant Growth Agent • Aura Living Store</p>
          </div>
        </div>

        {/* Store Metrics & Guardrail Badges */}
        <div className="flex items-center gap-3">
          {summary && (
            <div className="hidden md:flex items-center gap-2 bg-slate-800/80 px-3 py-1.5 rounded-lg border border-slate-700/60 text-xs">
              <span className="text-slate-400">Store Baseline:</span>
              <span className="text-emerald-400 font-semibold">₹{summary.total_revenue?.toLocaleString()} Rev</span>
              <span className="text-slate-600">•</span>
              <span className="text-sky-400 font-semibold">₹{summary.average_order_value?.toLocaleString()} AOV</span>
              <span className="text-slate-600">•</span>
              <span className="text-slate-300 font-semibold">{summary.total_customers} Customers</span>
            </div>
          )}

          {/* Razorpay Test Mode Pill */}
          <div className="flex items-center gap-1.5 bg-indigo-500/10 text-indigo-300 border border-indigo-500/30 px-3 py-1.5 rounded-lg text-xs font-medium">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
            <span>Razorpay TEST MODE</span>
          </div>

          {/* Guardrails Button */}
          <button
            onClick={onOpenPolicy}
            className="flex items-center gap-1.5 bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 px-3 py-1.5 rounded-lg text-xs font-medium transition"
          >
            <Sliders className="w-3.5 h-3.5 text-sky-400" />
            <span>Guardrails</span>
          </button>

          {/* Reset Demo Button */}
          <button
            onClick={onResetDemo}
            disabled={isResetting}
            title="Reset database to initial pristine state"
            className="flex items-center gap-1.5 bg-rose-500/10 hover:bg-rose-500/20 text-rose-300 border border-rose-500/30 px-3 py-1.5 rounded-lg text-xs font-medium transition"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${isResetting ? "animate-spin" : ""}`} />
            <span>Reset Demo</span>
          </button>
        </div>
      </div>
    </header>
  );
}
