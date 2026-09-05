import React from "react";
import { Sparkles, ArrowRight, Target, Users, DollarSign, TrendingUp, CheckCircle, AlertTriangle } from "lucide-react";

export default function OverviewPage({
  goal,
  summary,
  opportunities,
  actions,
  onRunAnalysis,
  onTriggerRecovery,
  onNavigateToTab,
  isAnalyzing,
  isRecovering,
}) {
  const targetAmount = goal?.target_amount || 100000;
  const realizedAmount = goal?.realized_amount || 0;
  const projectedAmount = goal?.projected_amount || 77400;
  const remainingAmount = Math.max(0, targetAmount - realizedAmount);

  const baselineRevenue = summary?.total_revenue || 402490;
  const currentTotalRevenue = baselineRevenue + realizedAmount;

  const realizedPct = Math.min(100, Math.round((realizedAmount / targetAmount) * 100));
  const projectedPct = Math.min(100, Math.round((projectedAmount / targetAmount) * 100));

  // Map actions
  const actionMap = {};
  (actions || []).forEach((act) => {
    actionMap[act.opportunity_id] = act;
  });

  return (
    <div className="space-y-6">
      {/* Revenue Growth Goal Banner */}
      <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-xs flex flex-col md:flex-row md:items-center justify-between gap-6">
        <div className="space-y-1.5 max-w-2xl">
          <div className="flex items-center gap-2 text-blue-600 text-xs font-bold uppercase tracking-wider">
            <Target className="w-4 h-4" />
            <span>Active Revenue Growth Directive</span>
          </div>
          <h2 className="text-xl sm:text-2xl font-bold text-slate-900 tracking-tight">
            "{goal?.prompt || "Help me generate ₹1,00,000 additional revenue."}"
          </h2>
          <p className="text-xs text-slate-500">
            Targeting ₹{targetAmount.toLocaleString("en-IN")} in incremental sales via autonomous segmentation, bundle
            offers, and Razorpay test execution.
          </p>
        </div>

        <div className="flex flex-wrap gap-2">
          <button
            onClick={onRunAnalysis}
            disabled={isAnalyzing}
            className="w-full sm:w-auto flex items-center justify-center gap-2 bg-blue-600 hover:bg-blue-700 text-white text-xs font-semibold px-5 py-3 rounded-lg shadow-sm transition disabled:opacity-50 cursor-pointer"
          >
            <Sparkles className={`w-4 h-4 ${isAnalyzing ? "animate-spin" : ""}`} />
            <span>{isAnalyzing ? "Analyzing Store Data..." : "Run AI Growth Analysis"}</span>
          </button>
          <button
            onClick={onTriggerRecovery}
            disabled={isRecovering}
            className="w-full sm:w-auto flex items-center justify-center gap-2 bg-amber-500 hover:bg-amber-600 text-white text-xs font-semibold px-5 py-3 rounded-lg shadow-sm transition disabled:opacity-50 cursor-pointer"
          >
            <AlertTriangle className={`w-4 h-4 ${isRecovering ? "animate-pulse" : ""}`} />
            <span>{isRecovering ? "Activating Recovery..." : "Simulate Sales Drop"}</span>
          </button>
        </div>
      </div>

      {/* 4 Clean KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Realized Revenue */}
        <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-xs">
          <div className="flex items-center justify-between text-slate-500 text-xs font-medium mb-1">
            <span>Realized Revenue</span>
            <span className="w-7 h-7 rounded-lg bg-emerald-50 text-emerald-600 flex items-center justify-center">
              <CheckCircle className="w-4 h-4" />
            </span>
          </div>
          <div className="text-2xl font-extrabold text-slate-900">
            ₹{realizedAmount.toLocaleString("en-IN", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
          </div>
          <div className="text-[11px] text-emerald-600 font-semibold mt-1">
            {realizedPct}% of target milestone reached
          </div>
        </div>

        {/* Identified Opportunity */}
        <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-xs">
          <div className="flex items-center justify-between text-slate-500 text-xs font-medium mb-1">
            <span>Projected Opportunity Pipeline</span>
            <span className="w-7 h-7 rounded-lg bg-blue-50 text-blue-600 flex items-center justify-center">
              <TrendingUp className="w-4 h-4" />
            </span>
          </div>
          <div className="text-2xl font-extrabold text-slate-900">
            ₹{projectedAmount.toLocaleString("en-IN", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
          </div>
          <div className="text-[11px] text-slate-500 mt-1">{projectedPct}% coverage of growth goal</div>
        </div>

        {/* Remaining to Goal */}
        <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-xs">
          <div className="flex items-center justify-between text-slate-500 text-xs font-medium mb-1">
            <span>Remaining to Goal</span>
            <span className="w-7 h-7 rounded-lg bg-amber-50 text-amber-600 flex items-center justify-center">
              <Target className="w-4 h-4" />
            </span>
          </div>
          <div className="text-2xl font-extrabold text-slate-900">
            ₹{remainingAmount.toLocaleString("en-IN", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
          </div>
          <div className="text-[11px] text-slate-500 mt-1">Target: ₹{targetAmount.toLocaleString("en-IN")}</div>
        </div>

        {/* Customers */}
        <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-xs">
          <div className="flex items-center justify-between text-slate-500 text-xs font-medium mb-1">
            <span>Customers In Scope</span>
            <span className="w-7 h-7 rounded-lg bg-slate-50 text-slate-600 flex items-center justify-center">
              <Users className="w-4 h-4" />
            </span>
          </div>
          <div className="text-2xl font-extrabold text-slate-900">{summary?.total_customers || 60}</div>
          <div className="text-[11px] text-slate-500 mt-1">
            {summary?.repeat_purchase_rate || 76.7}% repeat rate
          </div>
        </div>
      </div>

      {/* Goal Progress Bar & Baseline Breakdown */}
      <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-xs space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
          <div>
            <h3 className="text-sm font-bold text-slate-900">Revenue Breakdown &amp; Goal Progress</h3>
            <p className="text-xs text-slate-500">
              Clear distinction between historical baseline revenue and agent-generated incremental revenue
            </p>
          </div>

          <div className="flex items-center gap-4 text-xs">
            <div>
              <span className="text-slate-400 block text-[11px]">Historical Baseline:</span>
              <span className="font-semibold text-slate-700">₹{baselineRevenue.toLocaleString("en-IN")}</span>
            </div>
            <div>
              <span className="text-slate-400 block text-[11px]">Agent-Generated:</span>
              <span className="font-bold text-emerald-600">
                +₹{realizedAmount.toLocaleString("en-IN", { minimumFractionDigits: 2 })}
              </span>
            </div>
            <div className="border-l border-slate-200 pl-3">
              <span className="text-slate-400 block text-[11px]">Current Total Store Rev:</span>
              <span className="font-extrabold text-slate-900">
                ₹{currentTotalRevenue.toLocaleString("en-IN", { minimumFractionDigits: 2 })}
              </span>
            </div>
          </div>
        </div>

        {/* Clean Progress bar */}
        <div className="space-y-1.5">
          <div className="w-full h-3 bg-slate-100 rounded-full overflow-hidden flex relative">
            <div
              className="h-full bg-blue-100 rounded-full transition-all duration-500"
              style={{ width: `${Math.min(100, projectedPct)}%` }}
            ></div>
            <div
              className="h-full bg-emerald-500 rounded-full absolute top-0 left-0 transition-all duration-500"
              style={{ width: `${Math.min(100, realizedPct)}%` }}
            ></div>
          </div>
          <div className="flex justify-between text-[11px] text-slate-400">
            <span>₹0</span>
            <span className="font-medium text-slate-600">
              Realized: <strong className="text-emerald-600 font-bold">{realizedPct}%</strong> • Projected Pipeline:{" "}
              <strong className="text-blue-600 font-bold">{projectedPct}%</strong>
            </span>
            <span>Goal: ₹{targetAmount.toLocaleString("en-IN")}</span>
          </div>
        </div>
      </div>

      {/* Top 3–4 Opportunities Summary Cards */}
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-sm font-bold text-slate-900">Identified Growth Opportunities</h3>
            <p className="text-xs text-slate-500">Top revenue opportunities identified by the agent</p>
          </div>
          <button
            onClick={() => onNavigateToTab("opportunities")}
            className="text-xs font-semibold text-blue-600 hover:text-blue-700 flex items-center gap-1 cursor-pointer"
          >
            <span>View all opportunities</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {(opportunities || []).slice(0, 4).map((opp) => {
            const action = actionMap[opp.id];
            const isBlocked = action && (action.status === "BLOCKED" || action.policy_check_result === "VIOLATION_BLOCKED");
            const isExecuted = action && action.status === "EXECUTED";
            const isPaid = action && action.payment_status === "PAID";

            return (
              <div
                key={opp.id}
                className="bg-white border border-slate-200 rounded-xl p-5 hover:border-slate-300 transition shadow-xs flex flex-col justify-between"
              >
                <div>
                  <div className="flex items-center justify-between gap-2 mb-2">
                    <span className="text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded bg-slate-100 text-slate-700">
                      {opp.type.replace("_", " ")}
                    </span>

                    {isBlocked ? (
                      <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-amber-50 text-amber-800 border border-amber-200 flex items-center gap-1">
                        <AlertTriangle className="w-3 h-3 text-amber-600" />
                        Policy review required
                      </span>
                    ) : isPaid ? (
                      <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-emerald-50 text-emerald-800 border border-emerald-200">
                        Payment Realized
                      </span>
                    ) : isExecuted ? (
                      <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-blue-50 text-blue-800 border border-blue-200">
                        Link Active
                      </span>
                    ) : (
                      <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-slate-100 text-slate-600">
                        Ready to Execute
                      </span>
                    )}
                  </div>

                  <h4 className="text-sm font-bold text-slate-900 mb-1">{opp.title}</h4>
                  <p className="text-xs text-slate-500 line-clamp-2 mb-3">{opp.description}</p>
                </div>

                <div className="pt-3 border-t border-slate-100 flex items-center justify-between text-xs">
                  <div className="text-slate-500">
                    Cohort: <strong className="text-slate-800 font-semibold">{opp.target_customer_count} customers</strong>
                  </div>
                  <div className="text-right">
                    <span className="text-slate-400 block text-[10px]">Projected:</span>
                    <strong className="text-slate-900 font-bold">₹{opp.projected_revenue?.toLocaleString("en-IN")}</strong>
                  </div>
                  <button
                    onClick={() => onNavigateToTab("opportunities")}
                    className="text-xs font-semibold text-blue-600 hover:text-blue-700 flex items-center gap-0.5 cursor-pointer ml-2"
                  >
                    <span>View details</span>
                    <ArrowRight className="w-3 h-3" />
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
