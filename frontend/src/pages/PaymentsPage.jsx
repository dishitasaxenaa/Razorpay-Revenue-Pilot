import React from "react";
import { CreditCard, ExternalLink, CheckCircle, Clock, PlayCircle, ShieldCheck, AlertCircle } from "lucide-react";

export default function PaymentsPage({ actions, onSimulatePayment, isSimulating }) {
  const executedActions = (actions || []).filter((a) => a.status === "EXECUTED" || a.razorpay_link_id);

  return (
    <div className="space-y-6">
      {/* Title & Subtitle */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div>
          <h2 className="text-xl font-bold text-slate-900">Razorpay Payments</h2>
          <p className="text-xs text-slate-500 mt-0.5">Payment actions executed by your AI Revenue Agent.</p>
        </div>

        <div className="flex items-center gap-2">
          <span className="inline-flex items-center gap-1.5 bg-emerald-50 text-emerald-700 border border-emerald-200 px-3 py-1 rounded-full text-xs font-semibold">
            <ShieldCheck className="w-3.5 h-3.5 text-emerald-600" />
            <span>RAZORPAY TEST MODE</span>
          </span>
        </div>
      </div>

      {/* Prominent Demo Simulator Notice Banner */}
      <div className="bg-amber-50/60 border border-amber-200 rounded-xl p-4 flex items-start gap-3 text-xs">
        <AlertCircle className="w-4 h-4 text-amber-600 shrink-0 mt-0.5" />
        <div className="space-y-1">
          <div className="font-bold text-amber-900">DEMO / TESTING UTILITY NOTICE</div>
          <p className="text-slate-600 text-[11px] leading-relaxed">
            All links below are generated in <strong>Razorpay Test Mode</strong>. You can click{" "}
            <strong>"Open Test Checkout"</strong> to inspect the live Razorpay test checkout page, or use the{" "}
            <strong>[DEMO / TESTING UTILITY: Simulate Payment]</strong> button to emulate webhook delivery for
            hackathon judging evaluation. Simulated payments update goal progress and customer RFM profiles but are not
            actual Razorpay transactions.
          </p>
        </div>
      </div>

      {/* Payment Links Table */}
      <div className="bg-white border border-slate-200 rounded-xl shadow-xs overflow-hidden">
        {executedActions.length === 0 ? (
          <div className="p-12 text-center text-xs text-slate-500">
            No Razorpay test payment links generated yet. Approve opportunities on the AI Opportunities page to execute
            links.
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs text-slate-600">
              <thead className="bg-slate-50 text-slate-500 uppercase tracking-wider text-[10px] border-b border-slate-200">
                <tr>
                  <th className="py-3 px-4">Link ID</th>
                  <th className="py-3 px-4">Customer</th>
                  <th className="py-3 px-4">Amount</th>
                  <th className="py-3 px-4">Discount</th>
                  <th className="py-3 px-4">Status</th>
                  <th className="py-3 px-4">Created</th>
                  <th className="py-3 px-4 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {executedActions.map((act) => {
                  const isPaid = act.payment_status === "PAID";
                  const createdStr = act.created_at
                    ? new Date(act.created_at).toLocaleDateString("en-IN", {
                        month: "short",
                        day: "numeric",
                        hour: "2-digit",
                        minute: "2-digit",
                      })
                    : "Recent";

                  return (
                    <tr key={act.id} className="hover:bg-slate-50/80 transition">
                      <td className="py-3.5 px-4 font-mono text-blue-600 font-semibold">{act.razorpay_link_id}</td>
                      <td className="py-3.5 px-4 font-semibold text-slate-900">
                        {act.target_customer_name || "Target Customer"}
                      </td>
                      <td className="py-3.5 px-4 font-bold text-slate-900">
                        ₹{act.final_price?.toLocaleString("en-IN", { minimumFractionDigits: 2 })}
                      </td>
                      <td className="py-3.5 px-4 text-amber-700 font-medium">{act.proposed_discount_pct}% Off</td>
                      <td className="py-3.5 px-4">
                        {isPaid ? (
                          <span className="inline-flex items-center gap-1 bg-emerald-50 text-emerald-700 border border-emerald-200 px-2.5 py-0.5 rounded-full text-[10px] font-bold">
                            <CheckCircle className="w-3 h-3 text-emerald-600" />
                            PAID
                          </span>
                        ) : (
                          <span className="inline-flex items-center gap-1 bg-amber-50 text-amber-800 border border-amber-200 px-2.5 py-0.5 rounded-full text-[10px] font-bold">
                            <Clock className="w-3 h-3 text-amber-600" />
                            PENDING
                          </span>
                        )}
                      </td>
                      <td className="py-3.5 px-4 text-slate-500 text-[11px]">{createdStr}</td>
                      <td className="py-3.5 px-4 text-right space-x-2">
                        {act.razorpay_short_url && (
                          <a
                            href={act.razorpay_short_url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="inline-flex items-center gap-1 text-blue-600 hover:text-blue-800 font-semibold text-xs transition"
                          >
                            <span>Open Test Checkout</span>
                            <ExternalLink className="w-3 h-3" />
                          </a>
                        )}

                        {!isPaid && (
                          <button
                            onClick={() => onSimulatePayment(act.id)}
                            disabled={isSimulating}
                            title="[DEMO / TESTING UTILITY] Simulate customer payment callback"
                            className="inline-flex items-center gap-1 bg-emerald-600 hover:bg-emerald-700 text-white font-semibold px-3 py-1 rounded-md text-[11px] transition shadow-xs disabled:opacity-50 cursor-pointer ml-2"
                          >
                            <PlayCircle className="w-3 h-3" />
                            <span>Simulate Payment</span>
                          </button>
                        )}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
