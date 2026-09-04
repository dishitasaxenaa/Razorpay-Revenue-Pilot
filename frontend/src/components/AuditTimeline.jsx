import React, { useState } from "react";
import { History, ShieldAlert, CheckCircle, Clock, Zap, AlertTriangle, Filter } from "lucide-react";

export default function AuditTimeline({ logs }) {
  const [filter, setFilter] = useState("ALL");

  const filteredLogs = (logs || []).filter((l) => {
    if (filter === "ALL") return true;
    if (filter === "POLICY") return l.event_type.includes("POLICY");
    if (filter === "RAZORPAY") return l.event_type.includes("RAZORPAY") || l.event_type.includes("PAYMENT");
    return true;
  });

  const getEventBadge = (eventType) => {
    if (eventType === "POLICY_BLOCKED") {
      return (
        <span className="inline-flex items-center gap-1 bg-rose-500/15 text-rose-400 border border-rose-500/30 px-2 py-0.5 rounded text-[10px] font-bold">
          <AlertTriangle className="w-3 h-3" />
          POLICY BLOCKED
        </span>
      );
    }
    if (eventType.includes("MERCHANT_APPROVAL")) {
      return (
        <span className="inline-flex items-center gap-1 bg-amber-500/15 text-amber-400 border border-amber-500/30 px-2 py-0.5 rounded text-[10px] font-bold">
          <CheckCircle className="w-3 h-3" />
          MERCHANT SIGN-OFF
        </span>
      );
    }
    if (eventType.includes("RAZORPAY")) {
      return (
        <span className="inline-flex items-center gap-1 bg-sky-500/15 text-sky-400 border border-sky-500/30 px-2 py-0.5 rounded text-[10px] font-bold">
          <Zap className="w-3 h-3" />
          RAZORPAY ACTION
        </span>
      );
    }
    if (eventType.includes("PAYMENT")) {
      return (
        <span className="inline-flex items-center gap-1 bg-emerald-500/15 text-emerald-400 border border-emerald-500/30 px-2 py-0.5 rounded text-[10px] font-bold">
          <CheckCircle className="w-3 h-3" />
          PAYMENT RECORDED
        </span>
      );
    }
    return (
      <span className="inline-flex items-center gap-1 bg-slate-800 text-slate-300 border border-slate-700 px-2 py-0.5 rounded text-[10px] font-bold">
        {eventType}
      </span>
    );
  };

  return (
    <div className="bg-slate-850 rounded-2xl border border-slate-750 p-6 space-y-4">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3 border-b border-slate-750">
        <div>
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            <History className="w-5 h-5 text-sky-400" />
            <span>First-Class Audit Trail &amp; Explainability Log</span>
          </h2>
          <p className="text-xs text-slate-400">
            Transparent, tamper-proof record of every agent recommendation, policy check, human approval, and payment event
          </p>
        </div>

        {/* Filter buttons */}
        <div className="flex items-center gap-1.5 bg-slate-900 p-1 rounded-lg border border-slate-800 text-xs">
          <button
            onClick={() => setFilter("ALL")}
            className={`px-2.5 py-1 rounded-md transition font-medium ${
              filter === "ALL" ? "bg-sky-500 text-slate-950 font-bold" : "text-slate-400 hover:text-white"
            }`}
          >
            All ({logs?.length || 0})
          </button>
          <button
            onClick={() => setFilter("POLICY")}
            className={`px-2.5 py-1 rounded-md transition font-medium ${
              filter === "POLICY" ? "bg-amber-500 text-slate-950 font-bold" : "text-slate-400 hover:text-white"
            }`}
          >
            Policy &amp; Guardrails
          </button>
          <button
            onClick={() => setFilter("RAZORPAY")}
            className={`px-2.5 py-1 rounded-md transition font-medium ${
              filter === "RAZORPAY" ? "bg-emerald-500 text-slate-950 font-bold" : "text-slate-400 hover:text-white"
            }`}
          >
            Razorpay &amp; Payments
          </button>
        </div>
      </div>

      {filteredLogs.length === 0 ? (
        <div className="text-center py-8 text-xs text-slate-400">No audit log entries matching filter.</div>
      ) : (
        <div className="relative pl-6 space-y-4 before:absolute before:left-2 before:top-2 before:bottom-2 before:w-0.5 before:bg-slate-800">
          {filteredLogs.map((item) => {
            const timeStr = new Date(item.timestamp).toLocaleTimeString("en-IN", {
              hour: "2-digit",
              minute: "2-digit",
              second: "2-digit",
            });

            return (
              <div key={item.id} className="relative group">
                {/* Node dot on timeline */}
                <div className="absolute -left-6 top-1.5 w-2.5 h-2.5 rounded-full bg-sky-400 ring-4 ring-slate-900 group-hover:scale-125 transition"></div>

                <div className="bg-slate-900/90 rounded-xl p-4 border border-slate-800 hover:border-slate-700 transition space-y-2.5">
                  {/* Top bar */}
                  <div className="flex flex-wrap items-center justify-between gap-2 text-xs">
                    <div className="flex items-center gap-2">
                      {getEventBadge(item.event_type)}
                      <span className="font-mono text-[11px] text-slate-400">{timeStr}</span>
                    </div>

                    <div className="flex items-center gap-2 text-[11px]">
                      {item.human_approval && (
                        <span className="bg-slate-800 text-slate-300 px-2 py-0.5 rounded border border-slate-700">
                          Sign-off: <strong>{item.human_approval}</strong>
                        </span>
                      )}
                      {item.proposed_amount && (
                        <span className="text-emerald-400 font-bold">
                          ₹{item.proposed_amount.toLocaleString("en-IN")}
                        </span>
                      )}
                    </div>
                  </div>

                  {/* Recommendation */}
                  <div className="text-xs">
                    <span className="text-slate-400 font-medium">Agent Recommendation: </span>
                    <span className="text-white font-semibold">{item.agent_recommendation}</span>
                  </div>

                  {/* Reason & Explainability */}
                  <div className="text-xs bg-slate-950/70 p-2.5 rounded-lg border border-slate-850 text-slate-300 leading-relaxed">
                    <span className="text-sky-400 font-medium block mb-0.5">Decision Rationale:</span>
                    {item.reason}
                  </div>

                  {/* Policy & Outcome Footer */}
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 pt-1 text-[11px] border-t border-slate-850">
                    <div>
                      <span className="text-slate-500">Applicable Policy: </span>
                      <span className="text-slate-300 font-mono">{item.applicable_policy}</span>
                    </div>
                    <div>
                      <span className="text-slate-500">Policy Result: </span>
                      <span
                        className={`font-semibold ${
                          item.policy_result.includes("BLOCKED")
                            ? "text-rose-400"
                            : item.policy_result.includes("APPROVED") || item.policy_result.includes("PASSED")
                            ? "text-emerald-400"
                            : "text-sky-300"
                        }`}
                      >
                        {item.policy_result}
                      </span>
                    </div>
                    {item.razorpay_action && (
                      <div className="sm:col-span-2">
                        <span className="text-slate-500">Razorpay Action: </span>
                        <span className="text-sky-400 font-mono">{item.razorpay_action}</span>
                      </div>
                    )}
                    <div className="sm:col-span-2">
                      <span className="text-slate-500">Outcome: </span>
                      <span className="text-slate-200">{item.final_outcome}</span>
                    </div>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
