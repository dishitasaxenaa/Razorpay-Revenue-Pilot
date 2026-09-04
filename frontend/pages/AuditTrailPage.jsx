import React, { useState } from "react";
import { History, ShieldAlert, CheckCircle, AlertTriangle, Zap, DollarSign, Clock } from "lucide-react";

export default function AuditTrailPage({ logs }) {
  const [filter, setFilter] = useState("ALL");

  const filtered = (logs || []).filter((l) => {
    if (filter === "ALL") return true;
    if (filter === "FAILURE") return l.event_type.includes("BLOCKED") || l.policy_result.includes("BLOCKED");
    if (filter === "POLICY") return l.event_type.includes("POLICY");
    if (filter === "APPROVAL") return l.human_approval?.includes("APPROVED");
    if (filter === "RAZORPAY") return l.event_type.includes("RAZORPAY");
    if (filter === "PAYMENT") return l.event_type.includes("PAYMENT");
    return true;
  });

  const getStepBadge = (event_type, policy_result) => {
    if (event_type === "POLICY_BLOCKED" || policy_result === "VIOLATION_BLOCKED") {
      return (
        <span className="inline-flex items-center gap-1 bg-rose-50 text-rose-700 border border-rose-200 px-2.5 py-0.5 rounded-full text-[10px] font-bold">
          <AlertTriangle className="w-3 h-3 text-rose-600" />
          BLOCKED (POLICY VIOLATION)
        </span>
      );
    }
    if (event_type.includes("MERCHANT_APPROVAL")) {
      return (
        <span className="inline-flex items-center gap-1 bg-blue-50 text-blue-800 border border-blue-200 px-2.5 py-0.5 rounded-full text-[10px] font-bold">
          <CheckCircle className="w-3 h-3 text-blue-600" />
          HUMAN APPROVAL GRANTED
        </span>
      );
    }
    if (event_type.includes("RAZORPAY")) {
      return (
        <span className="inline-flex items-center gap-1 bg-indigo-50 text-indigo-700 border border-indigo-200 px-2.5 py-0.5 rounded-full text-[10px] font-bold">
          <Zap className="w-3 h-3 text-indigo-600" />
          RAZORPAY TEST LINK
        </span>
      );
    }
    if (event_type.includes("PAYMENT")) {
      return (
        <span className="inline-flex items-center gap-1 bg-emerald-50 text-emerald-800 border border-emerald-200 px-2.5 py-0.5 rounded-full text-[10px] font-bold">
          <CheckCircle className="w-3 h-3 text-emerald-600" />
          PAYMENT RECORDED
        </span>
      );
    }
    return (
      <span className="inline-flex items-center gap-1 bg-slate-100 text-slate-700 px-2.5 py-0.5 rounded-full text-[10px] font-bold">
        {event_type}
      </span>
    );
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div>
          <h2 className="text-xl font-bold text-slate-900">Audit Trail &amp; Decision Explainability</h2>
          <p className="text-xs text-slate-500 mt-0.5">
            Immutable SQLite event log demonstrating complete agent transparency, policy checks, and execution receipts.
          </p>
        </div>

        {/* Filter pills */}
        <div className="flex flex-wrap items-center gap-1.5 bg-white p-1 rounded-xl border border-slate-200 shadow-2xs">
          {[
            { id: "ALL", label: `All (${logs?.length || 0})` },
            { id: "FAILURE", label: "Failure / Blocked" },
            { id: "POLICY", label: "Policy Checks" },
            { id: "APPROVAL", label: "Approvals" },
            { id: "RAZORPAY", label: "Razorpay" },
            { id: "PAYMENT", label: "Payments" },
          ].map((f) => (
            <button
              key={f.id}
              onClick={() => setFilter(f.id)}
              className={`text-xs px-3 py-1.5 rounded-lg font-medium transition cursor-pointer ${
                filter === f.id
                  ? "bg-blue-600 text-white font-semibold shadow-2xs"
                  : "text-slate-600 hover:text-slate-900 hover:bg-slate-50"
              }`}
            >
              {f.label}
            </button>
          ))}
        </div>
      </div>

      {/* Vertical Timeline */}
      <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-xs">
        {filtered.length === 0 ? (
          <div className="text-center py-8 text-xs text-slate-500">No audit log entries matching selected filter.</div>
        ) : (
          <div className="relative pl-6 space-y-6 before:absolute before:left-2.5 before:top-2 before:bottom-2 before:w-0.5 before:bg-slate-200">
            {filtered.map((log) => {
              const timeStr = new Date(log.timestamp).toLocaleTimeString("en-IN", {
                hour: "2-digit",
                minute: "2-digit",
                second: "2-digit",
              });

              const isBlocked = log.event_type.includes("BLOCKED") || log.policy_result.includes("BLOCKED");

              return (
                <div key={log.id} className="relative group">
                  {/* Timeline Dot */}
                  <div
                    className={`absolute -left-6 top-1 w-3 h-3 rounded-full ring-4 ring-white transition ${
                      isBlocked ? "bg-rose-500" : "bg-blue-600"
                    }`}
                  ></div>

                  <div className="bg-slate-50/70 rounded-xl border border-slate-200/80 p-4 hover:border-slate-300 transition space-y-2">
                    {/* Header */}
                    <div className="flex flex-wrap items-center justify-between gap-2">
                      <div className="flex items-center gap-2">
                        {getStepBadge(log.event_type, log.policy_result)}
                        <span className="font-mono text-[11px] text-slate-400">{timeStr}</span>
                      </div>

                      <div className="flex items-center gap-2 text-xs">
                        {log.proposed_amount && (
                          <span className="font-bold text-slate-900">
                            ₹{log.proposed_amount.toLocaleString("en-IN", { minimumFractionDigits: 2 })}
                          </span>
                        )}
                        {log.human_approval && (
                          <span className="text-[10px] font-medium bg-white px-2 py-0.5 rounded border border-slate-200 text-slate-600">
                            HITL: {log.human_approval}
                          </span>
                        )}
                      </div>
                    </div>

                    {/* Recommendation */}
                    <div className="text-xs">
                      <span className="text-slate-500 font-medium">Recommendation: </span>
                      <strong className="text-slate-900">{log.agent_recommendation}</strong>
                    </div>

                    {/* Decision Rationale */}
                    <div className="bg-white p-3 rounded-lg border border-slate-200 text-xs text-slate-700 leading-relaxed">
                      <span className="text-blue-700 font-semibold block text-[11px] mb-0.5">Decision Rationale:</span>
                      {log.reason}
                    </div>

                    {/* Policy & Outcome Footer */}
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-[11px] pt-1 text-slate-600 border-t border-slate-200/60">
                      <div>
                        <span className="text-slate-400">Policy: </span>
                        <span className="font-mono text-slate-700">{log.applicable_policy}</span>
                      </div>
                      <div>
                        <span className="text-slate-400">Policy Result: </span>
                        <span
                          className={`font-semibold ${
                            isBlocked
                              ? "text-rose-600 font-bold"
                              : log.policy_result.includes("APPROVED") || log.policy_result.includes("PASSED")
                              ? "text-emerald-700"
                              : "text-blue-700"
                          }`}
                        >
                          {log.policy_result}
                        </span>
                      </div>
                      {log.razorpay_action && (
                        <div className="sm:col-span-2">
                          <span className="text-slate-400">Razorpay Action: </span>
                          <span className="font-mono text-slate-800">{log.razorpay_action}</span>
                        </div>
                      )}
                      <div className="sm:col-span-2">
                        <span className="text-slate-400">Outcome: </span>
                        <span className="text-slate-800 font-medium">{log.final_outcome}</span>
                      </div>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}
