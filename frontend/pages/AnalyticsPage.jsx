import React from "react";
import { BarChart3, TrendingUp, ShoppingBag, Repeat, DollarSign } from "lucide-react";

export default function AnalyticsPage({ summary, goal, products }) {
  const baselineRev = summary?.total_revenue || 402490;
  const realizedRev = goal?.realized_amount || 0;
  const totalRev = baselineRev + realizedRev;
  const totalOrders = summary?.total_orders || 210;
  const aov = summary?.average_order_value || 1916.62;
  const repeatRate = summary?.repeat_purchase_rate || 76.7;

  const segmentCounts = summary?.segments_breakdown || {
    ACTIVE_VIP: 10,
    CHURNED_VIP: 15,
    DIFFUSER_OWNER: 20,
    REPLENISHMENT: 15,
  };

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-bold text-slate-900">Store Analytics &amp; Baseline</h2>
        <p className="text-xs text-slate-500 mt-0.5">
          Deterministic e-commerce metrics analyzed by the agent to forecast opportunities.
        </p>
      </div>

      {/* 4 Clean Metric Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-xs">
          <span className="text-xs font-medium text-slate-500 block mb-1">Total Store Revenue</span>
          <div className="text-2xl font-extrabold text-slate-900">
            ₹{totalRev.toLocaleString("en-IN", { minimumFractionDigits: 2 })}
          </div>
          <div className="text-[11px] text-emerald-600 font-semibold mt-1">
            +₹{realizedRev.toLocaleString("en-IN")} agent incremental
          </div>
        </div>

        <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-xs">
          <span className="text-xs font-medium text-slate-500 block mb-1">Total Orders</span>
          <div className="text-2xl font-extrabold text-slate-900">{totalOrders}</div>
          <div className="text-[11px] text-slate-500 mt-1">Paid transactions</div>
        </div>

        <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-xs">
          <span className="text-xs font-medium text-slate-500 block mb-1">Average Order Value (AOV)</span>
          <div className="text-2xl font-extrabold text-slate-900">
            ₹{aov.toLocaleString("en-IN", { minimumFractionDigits: 2 })}
          </div>
          <div className="text-[11px] text-blue-600 font-semibold mt-1">Across all product lines</div>
        </div>

        <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-xs">
          <span className="text-xs font-medium text-slate-500 block mb-1">Repeat Purchase Rate</span>
          <div className="text-2xl font-extrabold text-slate-900">{repeatRate}%</div>
          <div className="text-[11px] text-slate-500 mt-1">Customers with &gt;1 order</div>
        </div>
      </div>

      {/* Visual Breakdowns */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Customer Cohort Breakdown */}
        <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-xs space-y-4">
          <h3 className="text-sm font-bold text-slate-900">Customer Cohort Distribution</h3>

          <div className="space-y-3">
            {Object.entries(segmentCounts).map(([seg, count]) => {
              const pct = Math.round((count / (summary?.total_customers || 60)) * 100);
              return (
                <div key={seg} className="space-y-1">
                  <div className="flex justify-between text-xs font-medium">
                    <span className="text-slate-700">{seg.replace("_", " ")}</span>
                    <span className="text-slate-500">
                      {count} customers ({pct}%)
                    </span>
                  </div>
                  <div className="w-full h-2 bg-slate-100 rounded-full overflow-hidden">
                    <div className="bg-blue-600 h-full rounded-full" style={{ width: `${pct}%` }}></div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Product Catalog Margins */}
        <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-xs space-y-4">
          <h3 className="text-sm font-bold text-slate-900">Product Margins &amp; Inventory</h3>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs text-slate-600">
              <thead className="bg-slate-50 text-slate-500 uppercase tracking-wider text-[10px] border-b border-slate-200">
                <tr>
                  <th className="py-2 px-3">Product</th>
                  <th className="py-2 px-3">Price</th>
                  <th className="py-2 px-3">Gross Margin</th>
                  <th className="py-2 px-3">Stock</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {(products || []).slice(0, 5).map((p) => (
                  <tr key={p.id}>
                    <td className="py-2.5 px-3 font-semibold text-slate-900 truncate max-w-[180px]">{p.name}</td>
                    <td className="py-2.5 px-3 font-bold text-slate-900">₹{p.price?.toLocaleString("en-IN")}</td>
                    <td className="py-2.5 px-3 text-emerald-600 font-semibold">{p.margin_pct}%</td>
                    <td className="py-2.5 px-3 text-slate-500">{p.inventory_count} units</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}
