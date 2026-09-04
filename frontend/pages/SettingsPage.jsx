import React from "react";
import { Store, ShieldCheck, Cpu, Database, Check } from "lucide-react";

export default function SettingsPage() {
  return (
    <div className="space-y-6 max-w-3xl">
      <div>
        <h2 className="text-xl font-bold text-slate-900">Application Settings</h2>
        <p className="text-xs text-slate-500 mt-0.5">Configuration environment and system runtimes.</p>
      </div>

      <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-xs space-y-4 text-xs">
        {/* Merchant Store */}
        <div className="flex items-center justify-between p-3.5 bg-slate-50 rounded-xl border border-slate-100">
          <div className="flex items-center gap-3">
            <Store className="w-5 h-5 text-blue-600" />
            <div>
              <div className="font-bold text-slate-900">Merchant Store</div>
              <div className="text-[11px] text-slate-500">Connected e-commerce merchant entity</div>
            </div>
          </div>
          <span className="font-semibold text-slate-800 bg-white px-3 py-1 rounded-md border border-slate-200">
            Aura Living Store
          </span>
        </div>

        {/* Environment */}
        <div className="flex items-center justify-between p-3.5 bg-slate-50 rounded-xl border border-slate-100">
          <div className="flex items-center gap-3">
            <ShieldCheck className="w-5 h-5 text-emerald-600" />
            <div>
              <div className="font-bold text-slate-900">Payment Gateway Environment</div>
              <div className="text-[11px] text-slate-500">Razorpay API test sandbox mode</div>
            </div>
          </div>
          <span className="font-semibold text-emerald-800 bg-emerald-50 border border-emerald-200 px-3 py-1 rounded-md">
            Razorpay Test Mode
          </span>
        </div>

        {/* AI Reasoning */}
        <div className="flex items-center justify-between p-3.5 bg-slate-50 rounded-xl border border-slate-100">
          <div className="flex items-center gap-3">
            <Cpu className="w-5 h-5 text-indigo-600" />
            <div>
              <div className="font-bold text-slate-900">Reasoning Engine</div>
              <div className="text-[11px] text-slate-500">LLM strategy prioritization layer</div>
            </div>
          </div>
          <span className="font-semibold text-slate-800 bg-white px-3 py-1 rounded-md border border-slate-200">
            Claude API (Structured JSON)
          </span>
        </div>

        {/* Database */}
        <div className="flex items-center justify-between p-3.5 bg-slate-50 rounded-xl border border-slate-100">
          <div className="flex items-center gap-3">
            <Database className="w-5 h-5 text-amber-600" />
            <div>
              <div className="font-bold text-slate-900">Database Storage</div>
              <div className="text-[11px] text-slate-500">File-based deterministic relational store</div>
            </div>
          </div>
          <span className="font-semibold text-slate-800 bg-white px-3 py-1 rounded-md border border-slate-200">
            SQLite / Local Demo (revenue_system.db)
          </span>
        </div>
      </div>
    </div>
  );
}
