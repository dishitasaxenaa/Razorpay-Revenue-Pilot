import React from "react";
import { Users, DollarSign, Percent, AlertTriangle, CheckCircle, ArrowUpRight, Zap, Clock } from "lucide-react";

export default function OpportunityPipeline({ opportunities, actions, onSelectActionForApproval, onExecuteDirectly }) {
  if (!opportunities || opportunities.length === 0) {
    return (
      <div className="bg-slate-800/40 border border-dashed border-slate-750 rounded-2xl p-12 text-center">
        <Zap className="w-10 h-10 text-sky-400/60 mx-auto mb-3" />
        <h3 className="text-lg font-bold text-white mb-1">No Opportunities Generated Yet</h3>
        <p className="text-sm text-slate-400 max-w-md mx-auto mb-4">
          Click <strong className="text-sky-400">"Run AI Growth Analysis"</strong> above to analyze the 60 customers,
          historical purchase patterns, and identify revenue opportunities.
        </p>
      </div>
    );
  }

  // Map opportunity ID to action proposal
  const actionMap = {};
  (actions || []).forEach((act) => {
    actionMap[act.opportunity_id] = act;
  });

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            <span>AI Opportunity Pipeline</span>
            <span className="text-xs bg-slate-800 text-sky-400 border border-sky-500/30 px-2.5 py-0.5 rounded-full font-semibold">
              {opportunities.length} Quantified Levers
            </span>
          </h2>
          <p className="text-xs text-slate-400">
            Calculated via deterministic Python analytics & prioritized via Claude reasoning
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
        {opportunities.map((opp) => {
          const action = actionMap[opp.id];
          const isBlocked = action && (action.status === "BLOCKED" || action.policy_check_result === "VIOLATION_BLOCKED");
          const isExecuted = action && action.status === "EXECUTED";
          const isPaid = action && action.payment_status === "PAID";
          const isApproved = action && action.status === "APPROVED";

          return (
            <div
              key={opp.id}
              className={`rounded-xl border p-5 flex flex-col justify-between transition relative overflow-hidden ${
                isBlocked
                  ? "bg-amber-950/20 border-amber-500/40 hover:border-amber-500/60"
                  : isExecuted
                  ? "bg-indigo-950/20 border-indigo-500/40 hover:border-indigo-500/60"
                  : "bg-slate-850/80 border-slate-750 hover:border-slate-650"
              }`}
            >
              {/* Type pill & Policy compliance badge */}
              <div className="flex items-center justify-between gap-2 mb-3">
                <span className="text-xs font-bold uppercase tracking-wider px-2.5 py-1 rounded-md bg-slate-800 text-slate-300 border border-slate-700">
                  {opp.type.replace("_", " ")}
                </span>

                {isBlocked ? (
                  <span className="flex items-center gap-1.5 text-xs font-bold px-2.5 py-1 rounded-full bg-rose-500/10 text-rose-400 border border-rose-500/30 animate-pulse">
                    <AlertTriangle className="w-3.5 h-3.5" />
                    POLICY BLOCKED (15% &gt; 10% limit)
                  </span>
                ) : isPaid ? (
                  <span className="flex items-center gap-1.5 text-xs font-bold px-2.5 py-1 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">
                    <CheckCircle className="w-3.5 h-3.5" />
                    PAYMENT REALIZED
                  </span>
                ) : isExecuted ? (
                  <span className="flex items-center gap-1.5 text-xs font-bold px-2.5 py-1 rounded-full bg-sky-500/10 text-sky-400 border border-sky-500/30">
                    <Zap className="w-3.5 h-3.5" />
                    TEST LINK ACTIVE
                  </span>
                ) : (
                  <span className="flex items-center gap-1.5 text-xs font-bold px-2.5 py-1 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">
                    <CheckCircle className="w-3.5 h-3.5" />
                    AUTO-APPROVED (≤10% Limit)
                  </span>
                )}
              </div>

              {/* Title & Description */}
              <div className="mb-4">
                <h3 className="text-base font-bold text-white mb-1">{opp.title}</h3>
                <p className="text-xs text-slate-300 leading-relaxed mb-3">{opp.description}</p>

                {/* AI Reasoning / Explainability Quote */}
                <div className="bg-slate-900/70 rounded-lg p-3 border border-slate-800 text-xs text-slate-300 italic">
                  <span className="text-sky-400 font-semibold not-italic block mb-1">🤖 Agent Rationale:</span>
                  "{opp.reasoning}"
                </div>
              </div>

              {/* Deterministic Metrics Grid */}
              <div className="grid grid-cols-3 gap-2 py-3 border-y border-slate-750 mb-4 text-xs">
                <div>
                  <div className="text-slate-400 font-medium">Target Cohort</div>
                  <div className="text-white font-bold flex items-center gap-1 mt-0.5">
                    <Users className="w-3.5 h-3.5 text-sky-400" />
                    <span>{opp.target_customer_count} Customers</span>
                  </div>
                  <div className="text-[10px] text-slate-500 truncate">{opp.target_cohort_name}</div>
                </div>

                <div>
                  <div className="text-slate-400 font-medium">Proposed Offer</div>
                  <div className="text-amber-400 font-bold flex items-center gap-1 mt-0.5">
                    <Percent className="w-3.5 h-3.5" />
                    <span>{opp.proposed_discount_pct}% Off</span>
                  </div>
                  <div className="text-[10px] text-slate-500">
                    {opp.suggested_product_name ? opp.suggested_product_name.slice(0, 16) + "..." : "Product Offer"}
                  </div>
                </div>

                <div>
                  <div className="text-slate-400 font-medium">Projected Rev</div>
                  <div className="text-emerald-400 font-bold flex items-center gap-1 mt-0.5">
                    <DollarSign className="w-3.5 h-3.5" />
                    <span>₹{opp.projected_revenue.toLocaleString("en-IN")}</span>
                  </div>
                  <div className="text-[10px] text-slate-500 font-medium">
                    Est. Conv: {(opp.estimated_conversion_rate * 100).toFixed(0)}%
                  </div>
                </div>
              </div>

              {/* Demonstrable Failure Alert Box */}
              {isBlocked && (
                <div className="bg-rose-500/10 border border-rose-500/30 rounded-lg p-3 mb-4 text-xs space-y-1">
                  <div className="font-bold text-rose-300 flex items-center gap-1">
                    <AlertTriangle className="w-3.5 h-3.5 text-rose-400" />
                    <span>Demonstrable Failure: Autonomous Guardrail Triggered</span>
                  </div>
                  <p className="text-slate-300 text-[11px]">
                    The Agent sought maximum reactivation using <strong>15% discount</strong>. The Policy Engine blocked it
                    because default autonomous limit is <strong>10%</strong>.
                  </p>
                  <p className="text-emerald-400 font-medium text-[11px]">
                    💡 Compliant 10% alternative (₹4,499.10) formulated and ready for approval.
                  </p>
                </div>
              )}

              {/* Action Buttons */}
              <div>
                {isBlocked ? (
                  <button
                    onClick={() => onSelectActionForApproval(action, opp)}
                    className="w-full flex items-center justify-center gap-2 bg-amber-500 hover:bg-amber-400 text-slate-950 font-bold py-2.5 px-4 rounded-lg text-xs transition shadow-lg shadow-amber-500/20 cursor-pointer"
                  >
                    <span>Resolve Policy Block &amp; Review (HITL)</span>
                    <ArrowUpRight className="w-4 h-4" />
                  </button>
                ) : isPaid ? (
                  <div className="w-full text-center py-2 px-3 rounded-lg bg-emerald-500/10 text-emerald-400 text-xs font-semibold border border-emerald-500/20">
                    Payment Received • Realized in Goal
                  </div>
                ) : isExecuted ? (
                  <div className="flex items-center justify-between bg-slate-900/80 px-3 py-2 rounded-lg border border-slate-700 text-xs">
                    <span className="text-slate-400 truncate">Link: {action.razorpay_link_id}</span>
                    <a
                      href={action.razorpay_short_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-sky-400 hover:text-sky-300 font-semibold flex items-center gap-1"
                    >
                      <span>Open Link</span>
                      <ArrowUpRight className="w-3.5 h-3.5" />
                    </a>
                  </div>
                ) : isApproved ? (
                  <button
                    onClick={() => onExecuteDirectly(action.id)}
                    className="w-full flex items-center justify-center gap-2 bg-sky-500 hover:bg-sky-400 text-slate-950 font-bold py-2 px-4 rounded-lg text-xs transition"
                  >
                    <span>Generate Razorpay Test Link</span>
                    <Zap className="w-4 h-4" />
                  </button>
                ) : null}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
