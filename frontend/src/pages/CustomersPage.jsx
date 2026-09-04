import React, { useState } from "react";
import { Users, UserCheck, UserX, Clock, Filter, ArrowRight } from "lucide-react";

export default function CustomersPage({ customers }) {
  const [selectedSegment, setSelectedSegment] = useState("ALL");

  const total = customers?.length || 0;
  const vipCount = (customers || []).filter((c) => c.segment?.includes("VIP")).length;
  const churnedCount = (customers || []).filter((c) => c.segment === "CHURNED_VIP").length;
  const diffuserOwners = (customers || []).filter((c) => c.segment === "DIFFUSER_OWNER").length;
  const replenishment = (customers || []).filter((c) => c.segment === "REPLENISHMENT").length;

  const filtered = (customers || []).filter((c) => {
    if (selectedSegment === "ALL") return true;
    if (selectedSegment === "VIP") return c.segment?.includes("VIP");
    if (selectedSegment === "CHURNED") return c.segment === "CHURNED_VIP";
    if (selectedSegment === "DIFFUSER") return c.segment === "DIFFUSER_OWNER";
    if (selectedSegment === "REPLENISH") return c.segment === "REPLENISHMENT";
    return true;
  });

  const getRecommendedAction = (seg) => {
    if (seg === "CHURNED_VIP") return "Send VIP Win-Back Offer (10% Cap)";
    if (seg === "DIFFUSER_OWNER") return "Recommend Essential Oils Bundle";
    if (seg === "ACTIVE_VIP" || seg === "REACTIVATED_VIP") return "Early Access Luxury Hamper";
    if (seg === "REPLENISHMENT") return "Send Restock Refill Incentive";
    return "Nurture Repeat Purchase";
  };

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-bold text-slate-900">Customers &amp; RFM Segmentation</h2>
        <p className="text-xs text-slate-500 mt-0.5">
          Audience segmentation informing the agent's targeted growth campaigns.
        </p>
      </div>

      {/* Summary Metric Cards */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        <div className="bg-white border border-slate-200 rounded-xl p-4 shadow-xs">
          <span className="text-slate-500 text-xs font-medium block mb-1">Total Customers</span>
          <div className="text-2xl font-extrabold text-slate-900">{total}</div>
          <span className="text-[11px] text-slate-400 mt-0.5 block">Store database</span>
        </div>

        <div className="bg-white border border-slate-200 rounded-xl p-4 shadow-xs">
          <span className="text-slate-500 text-xs font-medium block mb-1">VIP Customers</span>
          <div className="text-2xl font-extrabold text-blue-700">{vipCount}</div>
          <span className="text-[11px] text-blue-600 font-medium mt-0.5 block">LTV &gt; ₹10,000</span>
        </div>

        <div className="bg-white border border-slate-200 rounded-xl p-4 shadow-xs">
          <span className="text-slate-500 text-xs font-medium block mb-1">Dormant / At Risk</span>
          <div className="text-2xl font-extrabold text-amber-700">{churnedCount}</div>
          <span className="text-[11px] text-amber-600 font-medium mt-0.5 block">&gt;60 days inactive</span>
        </div>

        <div className="bg-white border border-slate-200 rounded-xl p-4 shadow-xs">
          <span className="text-slate-500 text-xs font-medium block mb-1">Diffuser Owners</span>
          <div className="text-2xl font-extrabold text-indigo-700">{diffuserOwners}</div>
          <span className="text-[11px] text-indigo-600 font-medium mt-0.5 block">Cross-sell candidates</span>
        </div>
      </div>

      {/* Table Container */}
      <div className="bg-white border border-slate-200 rounded-xl shadow-xs overflow-hidden space-y-3 p-5">
        {/* Filter Tabs */}
        <div className="flex flex-wrap items-center justify-between gap-3 pb-3 border-b border-slate-100">
          <div className="flex items-center gap-1.5">
            {[
              { id: "ALL", label: `All (${total})` },
              { id: "VIP", label: `VIPs (${vipCount})` },
              { id: "CHURNED", label: `Dormant VIPs (${churnedCount})` },
              { id: "DIFFUSER", label: `Diffuser Owners (${diffuserOwners})` },
              { id: "REPLENISH", label: `Refill Regulars (${replenishment})` },
            ].map((f) => (
              <button
                key={f.id}
                onClick={() => setSelectedSegment(f.id)}
                className={`text-xs px-3 py-1.5 rounded-lg font-medium transition cursor-pointer ${
                  selectedSegment === f.id
                    ? "bg-blue-50 text-blue-700 font-bold border border-blue-200"
                    : "text-slate-600 hover:bg-slate-100 border border-transparent"
                }`}
              >
                {f.label}
              </button>
            ))}
          </div>

          <span className="text-[11px] text-slate-400">Showing {filtered.length} customers</span>
        </div>

        {/* Customer Table */}
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs text-slate-600">
            <thead className="bg-slate-50 text-slate-500 uppercase tracking-wider text-[10px] border-b border-slate-200">
              <tr>
                <th className="py-2.5 px-4">Customer</th>
                <th className="py-2.5 px-4">Segment</th>
                <th className="py-2.5 px-4">Orders</th>
                <th className="py-2.5 px-4">Lifetime Spend</th>
                <th className="py-2.5 px-4">Last Purchase</th>
                <th className="py-2.5 px-4">AI Recommended Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {filtered.map((c) => {
                const dateStr = c.last_order_date
                  ? new Date(c.last_order_date).toLocaleDateString("en-IN", {
                      month: "short",
                      day: "numeric",
                    })
                  : "N/A";

                return (
                  <tr key={c.id} className="hover:bg-slate-50/80 transition">
                    <td className="py-3 px-4">
                      <div className="font-semibold text-slate-900">{c.name}</div>
                      <div className="text-[11px] text-slate-400 font-mono">{c.email}</div>
                    </td>
                    <td className="py-3 px-4">
                      <span
                        className={`inline-block px-2 py-0.5 rounded text-[10px] font-bold ${
                          c.segment === "CHURNED_VIP"
                            ? "bg-amber-100 text-amber-800"
                            : c.segment?.includes("VIP")
                            ? "bg-blue-100 text-blue-800"
                            : "bg-slate-100 text-slate-700"
                        }`}
                      >
                        {c.segment}
                      </span>
                    </td>
                    <td className="py-3 px-4 font-semibold text-slate-900">{c.orders_count}</td>
                    <td className="py-3 px-4 font-bold text-slate-900">₹{c.total_spent?.toLocaleString("en-IN")}</td>
                    <td className="py-3 px-4 text-slate-500">{dateStr}</td>
                    <td className="py-3 px-4">
                      <span className="text-[11px] font-medium text-blue-700 bg-blue-50 px-2.5 py-1 rounded-md inline-block">
                        {getRecommendedAction(c.segment)}
                      </span>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
