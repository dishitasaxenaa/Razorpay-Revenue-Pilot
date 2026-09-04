import React, { useState } from "react";
import {
  Users,
  DollarSign,
  Percent,
  AlertTriangle,
  CheckCircle,
  ChevronDown,
  ChevronUp,
  ArrowRight,
  ExternalLink,
  Shield,
  Zap,
} from "lucide-react";

export default function OpportunitiesPage({
  opportunities,
  actions,
  onSelectActionForApproval,
  onExecuteDirectly,
  onNavigateToTab,
}) {
  const [expandedReasoning, setExpandedReasoning] = useState({});

  const toggleReasoning = (id) => {
    setExpandedReasoning((prev) => ({ ...prev, [id]: !prev[id] }));
  };

  const actionPriority = {
  BLOCKED: 3,
  REQUIRES_APPROVAL: 3,
  APPROVED: 2,
  EXECUTED: 1,
};

const actionMap = {};

(actions || []).forEach((act) => {
  const current = actionMap[act.opportunity_id];

  const currentPriority = current
    ? actionPriority[current.status] ?? 0
    : -1;

  const newPriority = actionPriority[act.status] ?? 0;

  // Keep the higher-priority action.
  // For equal priority, keep the existing one because the API
  // returns actions newest-first.
  if (!current || newPriority > currentPriority) {
    actionMap[act.opportunity_id] = act;
  }
});

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-bold text-slate-900">AI Growth Opportunities</h2>
        <p className="text-xs text-slate-500 mt-0.5">
          Algorithmic revenue-growth opportunities calculated deterministically and evaluated against merchant guardrails.
        </p>
      </div>

      <div className="grid grid-cols-1 gap-5">
        {(opportunities || []).map((opp) => {
          const action = actionMap[opp.id];
          const isBlocked = action && (action.status === "BLOCKED" || action.policy_check_result === "VIOLATION_BLOCKED");
          const isExecuted = action && action.status === "EXECUTED";
          const isPaid = action && action.payment_status === "PAID";
          const isApproved = action && action.status === "APPROVED";
          const isReasoningOpen = !!expandedReasoning[opp.id];

          return (
            <div
              key={opp.id}
              className={`bg-white rounded-xl border p-6 shadow-xs transition space-y-4 ${
                isBlocked ? "border-amber-300 ring-1 ring-amber-300/40" : "border-slate-200"
              }`}
            >
              {/* Card Header */}
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3 border-b border-slate-100">
                <div className="flex items-center gap-2.5">
                  <span className="text-[11px] font-bold uppercase tracking-wider px-2.5 py-1 rounded-md bg-slate-100 text-slate-700">
                    {opp.type.replace("_", " ")}
                  </span>
                  <h3 className="text-base font-bold text-slate-900">{opp.title}</h3>
                </div>

                {/* Policy status badge */}
                <div>
                  {isBlocked ? (
                    <span className="inline-flex items-center gap-1.5 text-xs font-bold px-3 py-1 rounded-full bg-amber-50 text-amber-800 border border-amber-300">
                      <AlertTriangle className="w-3.5 h-3.5 text-amber-600" />
                      POLICY REVIEW REQUIRED
                    </span>
                  ) : isPaid ? (
                    <span className="inline-flex items-center gap-1.5 text-xs font-bold px-3 py-1 rounded-full bg-emerald-50 text-emerald-800 border border-emerald-200">
                      <CheckCircle className="w-3.5 h-3.5 text-emerald-600" />
                      PAYMENT REALIZED
                    </span>
                  ) : isExecuted ? (
                    <span className="inline-flex items-center gap-1.5 text-xs font-bold px-3 py-1 rounded-full bg-blue-50 text-blue-800 border border-blue-200">
                      <Zap className="w-3.5 h-3.5 text-blue-600" />
                      TEST LINK ACTIVE
                    </span>
                  ) : (
                    <span className="inline-flex items-center gap-1.5 text-xs font-bold px-3 py-1 rounded-full bg-emerald-50 text-emerald-700 border border-emerald-200">
                      <CheckCircle className="w-3.5 h-3.5 text-emerald-600" />
                      AUTO-APPROVED (≤10% Limit)
                    </span>
                  )}
                </div>
              </div>

              {/* Description */}
              <p className="text-xs text-slate-600 leading-relaxed">{opp.description}</p>

              {/* Metrics Grid */}
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 p-4 bg-slate-50 rounded-xl border border-slate-100 text-xs">
                <div>
                  <span className="text-slate-400 block text-[11px]">Target Cohort:</span>
                  <strong className="text-slate-900 font-bold flex items-center gap-1 mt-0.5">
                    <Users className="w-3.5 h-3.5 text-blue-600" />
                    <span>{opp.target_customer_count} Customers</span>
                  </strong>
                  <span className="text-[10px] text-slate-500 truncate block mt-0.5">{opp.target_cohort_name}</span>
                </div>

                <div>
                  <span className="text-slate-400 block text-[11px]">Proposed Offer:</span>
                  <strong className="text-slate-900 font-bold flex items-center gap-1 mt-0.5">
                    <Percent className="w-3.5 h-3.5 text-amber-600" />
                    <span>{opp.proposed_discount_pct}% Discount</span>
                  </strong>
                  <span className="text-[10px] text-slate-500 truncate block mt-0.5">
                    {opp.suggested_product_name || "Catalog Product"}
                  </span>
                </div>

                <div>
                  <span className="text-slate-400 block text-[11px]">Projected Revenue:</span>
                  <strong className="text-emerald-700 font-bold flex items-center gap-1 mt-0.5">
                    <DollarSign className="w-3.5 h-3.5 text-emerald-600" />
                    <span>₹{opp.projected_revenue?.toLocaleString("en-IN")}</span>
                  </strong>
                  <span className="text-[10px] text-slate-500 block mt-0.5">
                    Conversion: {(opp.estimated_conversion_rate * 100).toFixed(0)}%
                  </span>
                </div>

                <div>
                  <span className="text-slate-400 block text-[11px]">Projected ROI:</span>
                  <strong className="text-slate-900 font-bold block mt-0.5">{opp.projected_roi}%</strong>
                  <span className="text-[10px] text-slate-500 block mt-0.5">Net capital efficiency</span>
                </div>
              </div>

              {/* Policy Block Alert & Demonstrable Failure Box */}
              {isBlocked && (
                <div className="bg-amber-50/80 border border-amber-300 rounded-xl p-4 text-xs space-y-3">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2 text-amber-900 font-bold">
                      <AlertTriangle className="w-4 h-4 text-amber-600" />
                      <span>POLICY REVIEW REQUIRED</span>
                    </div>
                    <span className="text-[11px] font-semibold text-amber-800 bg-amber-100 px-2.5 py-0.5 rounded-md">
                      Autonomous Execution Held
                    </span>
                  </div>

                  <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 text-[11px] bg-white p-3 rounded-lg border border-amber-200">
                    <div>
                      <span className="text-slate-500 block">Requested:</span>
                      <strong className="text-rose-600 font-bold text-sm">15.0% discount</strong>
                    </div>
                    <div>
                      <span className="text-slate-500 block">Allowed Limit:</span>
                      <strong className="text-slate-900 font-bold text-sm">10.0% max</strong>
                    </div>
                    <div>
                      <span className="text-slate-500 block">Recommended Alternative:</span>
                      <strong className="text-emerald-700 font-bold text-sm">10.0% (₹4,499.10)</strong>
                    </div>
                  </div>

                  <p className="text-slate-700 text-[11px] leading-relaxed">
                    <strong>Reason:</strong> Exceeds merchant-defined autonomous discount limit. The AI agent proposed 15%
                    to maximize dormant VIP comeback probability, but merchant policy caps autonomous discounting at 10%.
                  </p>

                  <div className="flex items-center gap-3 pt-1">
                    <button
                      onClick={() => onSelectActionForApproval(action, opp)}
                      className="bg-blue-600 hover:bg-blue-700 text-white text-xs font-semibold px-4 py-2 rounded-lg shadow-sm transition flex items-center gap-1.5 cursor-pointer"
                    >
                      <span>Review &amp; Approve</span>
                      <ArrowRight className="w-3.5 h-3.5" />
                    </button>
                    <span className="text-[11px] text-slate-500">Adopting 10% preserves merchant unit economics</span>
                  </div>
                </div>
              )}

              {/* Actions for other states */}
              {!isBlocked && (
                <div className="flex items-center justify-between pt-2">
                  <div>
                    {isPaid ? (
                      <span className="text-xs font-semibold text-emerald-700 flex items-center gap-1">
                        <CheckCircle className="w-4 h-4" />
                        <span>Payment outcome recorded in goal</span>
                      </span>
                    ) : isExecuted ? (
                      <div className="flex items-center gap-3 text-xs">
                        <span className="text-slate-500">
                          Razorpay Link: <strong className="font-mono text-slate-900">{action.razorpay_link_id}</strong>
                        </span>
                        <a
                          href={action.razorpay_short_url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-blue-600 hover:text-blue-700 font-semibold flex items-center gap-1"
                        >
                          <span>Open Test Link</span>
                          <ExternalLink className="w-3 h-3" />
                        </a>
                      </div>
                    ) : isApproved ? (
                      <button
                        onClick={() => onExecuteDirectly(action.id)}
                        className="bg-blue-600 hover:bg-blue-700 text-white text-xs font-semibold px-4 py-2 rounded-lg shadow-sm transition flex items-center gap-1.5 cursor-pointer"
                      >
                        <span>Generate Razorpay Test Link</span>
                        <ArrowRight className="w-3.5 h-3.5" />
                      </button>
                    ) : null}
                  </div>

                  {/* Expand AI Reasoning Button (Collapsed by default!) */}
                  <button
                    onClick={() => toggleReasoning(opp.id)}
                    className="text-xs font-medium text-slate-500 hover:text-slate-800 flex items-center gap-1 cursor-pointer"
                  >
                    <span>{isReasoningOpen ? "Hide AI reasoning" : "View AI reasoning"}</span>
                    {isReasoningOpen ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
                  </button>
                </div>
              )}

              {/* Collapsed/Expanded AI Reasoning Box */}
              {isReasoningOpen && (
                <div className="p-4 bg-slate-50 rounded-xl border border-slate-200 text-xs text-slate-700 italic space-y-1 animate-fadeIn">
                  <span className="text-blue-600 font-semibold not-italic block">🤖 Strategic Decision Explainability:</span>
                  <p className="leading-relaxed">"{opp.reasoning}"</p>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
