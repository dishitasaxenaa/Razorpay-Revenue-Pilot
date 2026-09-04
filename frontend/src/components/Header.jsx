import React from "react";
import { RefreshCw, Shield, ExternalLink } from "lucide-react";

export default function Header({ activeTab, onResetDemo, isResetting }) {
  const pageTitles = {
    overview: "Overview",
    opportunities: "AI Opportunities",
    campaigns: "AI Campaign Strategy",
    razorpay: "Razorpay Payments",
    customers: "Customers & RFM Segments",
    analytics: "Store Analytics",
    audit: "Audit Trail & Explainability",
    guardrails: "Merchant Guardrails",
    settings: "Settings",
  };

  return (
    <header className="h-16 bg-white border-b border-slate-200 px-6 sm:px-8 flex items-center justify-between sticky top-0 z-10">
      {/* Breadcrumb / Title */}
      <div className="flex items-center gap-2">
        <span className="text-xs font-medium text-slate-400">Revenue Pilot</span>
        <span className="text-xs text-slate-300">/</span>
        <h1 className="text-sm font-bold text-slate-900">{pageTitles[activeTab] || "Dashboard"}</h1>
      </div>

      {/* Right Controls */}
      <div className="flex items-center gap-3">
        {/* Test Mode Badge */}
        <div className="flex items-center gap-1.5 bg-emerald-50 text-emerald-700 border border-emerald-200/80 px-3 py-1.5 rounded-lg text-xs font-semibold">
          <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
          <span>Razorpay TEST MODE</span>
        </div>

        {/* Reset Demo Button */}
        <button
          onClick={onResetDemo}
          disabled={isResetting}
          title="Reset database to clean initial demo state"
          className="flex items-center gap-1.5 bg-white hover:bg-slate-50 text-slate-700 border border-slate-200 px-3 py-1.5 rounded-lg text-xs font-medium transition shadow-sm hover:border-slate-300 cursor-pointer disabled:opacity-50"
        >
          <RefreshCw className={`w-3.5 h-3.5 text-slate-500 ${isResetting ? "animate-spin" : ""}`} />
          <span>Reset Demo</span>
        </button>
      </div>
    </header>
  );
}
