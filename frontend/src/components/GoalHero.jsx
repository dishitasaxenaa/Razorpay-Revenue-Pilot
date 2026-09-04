import React, { useState } from "react";
import { Target, Sparkles, TrendingUp, CheckCircle, ArrowRight } from "lucide-react";

export default function GoalHero({ goal, onRunAnalysis, onSetGoal, isAnalyzing }) {
  const [isEditing, setIsEditing] = useState(false);
  const [customPrompt, setCustomPrompt] = useState(goal?.prompt || "Help me generate ₹1,00,000 additional revenue.");
  const [customTarget, setCustomTarget] = useState(goal?.target_amount || 100000);

  const targetAmount = goal?.target_amount || 100000;
  const realizedAmount = goal?.realized_amount || 0;
  const projectedAmount = goal?.projected_amount || 0;

  const realizedPct = Math.min(100, Math.round((realizedAmount / targetAmount) * 100));
  const projectedPct = Math.min(100, Math.round((projectedAmount / targetAmount) * 100));

  const handlePreset = (amount, text) => {
    setCustomTarget(amount);
    setCustomPrompt(text);
    onSetGoal(text, amount);
    setIsEditing(false);
  };

  const handleCustomSubmit = (e) => {
    e.preventDefault();
    onSetGoal(customPrompt, Number(customTarget));
    setIsEditing(false);
  };

  return (
    <div className="bg-gradient-to-b from-slate-800/80 to-slate-900/90 rounded-2xl border border-slate-700/80 p-6 sm:p-8 shadow-xl shadow-slate-950/40 relative overflow-hidden">
      {/* Background glow accents */}
      <div className="absolute top-0 right-0 w-96 h-96 bg-sky-500/10 rounded-full blur-3xl pointer-events-none -mr-20 -mt-20"></div>
      <div className="absolute bottom-0 left-0 w-80 h-80 bg-indigo-500/10 rounded-full blur-3xl pointer-events-none -ml-20 -mb-20"></div>

      <div className="relative z-10">
        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-6 pb-6 border-b border-slate-750">
          <div className="space-y-2">
            <div className="flex items-center gap-2 text-sky-400 text-xs font-bold uppercase tracking-wider">
              <Target className="w-4 h-4" />
              <span>Merchant Growth Directive</span>
            </div>

            {!isEditing ? (
              <div className="flex items-center gap-3">
                <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
                  "{goal?.prompt || "Help me generate ₹1,00,000 additional revenue."}"
                </h1>
                <button
                  onClick={() => setIsEditing(true)}
                  className="text-xs bg-slate-700/60 hover:bg-slate-700 text-slate-300 px-2.5 py-1 rounded-md border border-slate-600 transition"
                >
                  Edit Goal
                </button>
              </div>
            ) : (
              <form onSubmit={handleCustomSubmit} className="flex flex-wrap items-center gap-2 pt-1">
                <input
                  type="text"
                  value={customPrompt}
                  onChange={(e) => setCustomPrompt(e.target.value)}
                  className="bg-slate-900 border border-sky-500/50 rounded-lg px-3 py-1.5 text-sm text-white focus:outline-none focus:ring-2 focus:ring-sky-500 min-w-[320px]"
                />
                <input
                  type="number"
                  value={customTarget}
                  onChange={(e) => setCustomTarget(e.target.value)}
                  placeholder="Target (₹)"
                  className="bg-slate-900 border border-sky-500/50 rounded-lg px-3 py-1.5 text-sm text-white focus:outline-none focus:ring-2 focus:ring-sky-500 w-32"
                />
                <button
                  type="submit"
                  className="bg-sky-500 hover:bg-sky-400 text-slate-950 font-bold text-xs px-3 py-2 rounded-lg transition"
                >
                  Save Directive
                </button>
                <button
                  type="button"
                  onClick={() => setIsEditing(false)}
                  className="text-slate-400 hover:text-white text-xs px-2"
                >
                  Cancel
                </button>
              </form>
            )}

            {/* Quick preset chips */}
            <div className="flex items-center gap-2 pt-1 text-xs text-slate-400">
              <span>Goal Presets:</span>
              <button
                onClick={() => handlePreset(50000, "Help me generate ₹50,000 additional revenue.")}
                className="hover:text-sky-300 bg-slate-800/80 px-2 py-0.5 rounded border border-slate-700 transition"
              >
                ₹50k
              </button>
              <button
                onClick={() => handlePreset(100000, "Help me generate ₹1,00,000 additional revenue.")}
                className="hover:text-sky-300 bg-slate-800/80 px-2 py-0.5 rounded border border-slate-700 transition font-semibold text-sky-400"
              >
                ₹1,00,000 (Buildathon Default)
              </button>
              <button
                onClick={() => handlePreset(250000, "Help me generate ₹2,50,000 additional revenue.")}
                className="hover:text-sky-300 bg-slate-800/80 px-2 py-0.5 rounded border border-slate-700 transition"
              >
                ₹2.5L
              </button>
            </div>
          </div>

          {/* Run Analysis Trigger Button */}
          <div className="flex items-center">
            <button
              onClick={onRunAnalysis}
              disabled={isAnalyzing}
              className="w-full sm:w-auto flex items-center justify-center gap-2.5 bg-gradient-to-r from-sky-500 to-indigo-600 hover:from-sky-400 hover:to-indigo-500 text-white font-bold px-6 py-3.5 rounded-xl shadow-lg shadow-sky-500/25 transition-all transform active:scale-95 disabled:opacity-50 cursor-pointer"
            >
              <Sparkles className={`w-5 h-5 ${isAnalyzing ? "animate-spin" : ""}`} />
              <span>{isAnalyzing ? "Analyzing Store Data..." : "Run AI Growth Analysis"}</span>
            </button>
          </div>
        </div>

        {/* Dynamic Metric Progress Counters */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 pt-6">
          {/* 1. Realized Revenue */}
          <div className="bg-slate-900/60 rounded-xl p-4 border border-slate-800 flex items-center justify-between">
            <div>
              <div className="text-xs text-slate-400 font-medium">Realized Revenue</div>
              <div className="text-2xl font-extrabold text-emerald-400">
                ₹{realizedAmount.toLocaleString("en-IN", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
              </div>
              <div className="text-xs text-emerald-500/80 font-medium mt-0.5">
                {realizedPct}% of target reached
              </div>
            </div>
            <div className="w-10 h-10 rounded-full bg-emerald-500/10 flex items-center justify-center text-emerald-400">
              <CheckCircle className="w-5 h-5" />
            </div>
          </div>

          {/* 2. Projected Pipeline */}
          <div className="bg-slate-900/60 rounded-xl p-4 border border-slate-800 flex items-center justify-between">
            <div>
              <div className="text-xs text-slate-400 font-medium">Projected Revenue Pipeline</div>
              <div className="text-2xl font-extrabold text-sky-400">
                ₹{projectedAmount.toLocaleString("en-IN", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
              </div>
              <div className="text-xs text-sky-400/80 font-medium mt-0.5">
                {projectedPct}% coverage identified
              </div>
            </div>
            <div className="w-10 h-10 rounded-full bg-sky-500/10 flex items-center justify-center text-sky-400">
              <TrendingUp className="w-5 h-5" />
            </div>
          </div>

          {/* 3. Goal Target */}
          <div className="bg-slate-900/60 rounded-xl p-4 border border-slate-800 flex items-center justify-between">
            <div>
              <div className="text-xs text-slate-400 font-medium">Target Revenue Goal</div>
              <div className="text-2xl font-extrabold text-white">
                ₹{targetAmount.toLocaleString("en-IN", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
              </div>
              <div className="text-xs text-indigo-400/80 font-medium mt-0.5">
                100% Milestone Goal
              </div>
            </div>
            <div className="w-10 h-10 rounded-full bg-indigo-500/10 flex items-center justify-center text-indigo-400">
              <Target className="w-5 h-5" />
            </div>
          </div>
        </div>

        {/* Multi-tier Progress Bar */}
        <div className="mt-6 space-y-1.5">
          <div className="flex justify-between text-xs text-slate-400 font-medium">
            <span>Progress toward ₹{targetAmount.toLocaleString("en-IN")} target</span>
            <span>
              Realized: <strong className="text-emerald-400">{realizedPct}%</strong> • Projected Pipeline:{" "}
              <strong className="text-sky-400">{projectedPct}%</strong>
            </span>
          </div>

          <div className="w-full h-3.5 bg-slate-950 rounded-full overflow-hidden p-0.5 border border-slate-800 flex relative">
            {/* Projected bar (backdrop) */}
            <div
              className="h-full bg-sky-500/40 rounded-full transition-all duration-700 ease-out"
              style={{ width: `${Math.min(100, projectedPct)}%` }}
            ></div>
            {/* Realized bar (foreground overlay) */}
            <div
              className="h-full bg-emerald-500 rounded-full absolute top-0.5 left-0.5 transition-all duration-700 ease-out shadow-sm shadow-emerald-500/50"
              style={{ width: `${Math.min(100, realizedPct)}%` }}
            ></div>
          </div>
        </div>
      </div>
    </div>
  );
}
