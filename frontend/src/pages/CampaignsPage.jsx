import React, { useState } from "react";
import { Megaphone, TrendingUp, HelpCircle, ChevronDown, ChevronUp, DollarSign, Award } from "lucide-react";

export default function CampaignsPage({ campaignData, onBudgetChange }) {
  const [budget, setBudget] = useState(20000);
  const [showExplanation, setShowExplanation] = useState(false);

  const crossSellAmount = Math.round(budget * 0.6);
  const winBackAmount = Math.round(budget * 0.4);
  const projectedRevenue = Math.round(budget * 4.47);
  const roas = 4.47;

  const handleBudgetInput = (val) => {
    const num = Number(val);
    setBudget(num);
    onBudgetChange?.(num);
  };

  const historicalCampaigns = campaignData?.historical_campaigns || [
    {
      id: "camp_1",
      name: "Q4 VIP Win-Back Initiative",
      type: "Win-Back",
      spend: 10000,
      revenue: 48200,
      conversion_rate: 34.2,
      roas: 4.82,
      is_best: true,
    },
    {
      id: "camp_2",
      name: "Diffuser Cross-Sell Wave 1",
      type: "Cross-Sell",
      spend: 15000,
      revenue: 63500,
      conversion_rate: 28.5,
      roas: 4.23,
      is_best: false,
    },
    {
      id: "camp_3",
      name: "Monsoon Herbal Tea Refill Push",
      type: "Replenishment",
      spend: 6000,
      revenue: 21800,
      conversion_rate: 41.0,
      roas: 3.63,
      is_best: false,
    },
    {
      id: "camp_4",
      name: "Diwali Luxury Hamper Pre-Book",
      type: "VIP Upsell",
      spend: 18000,
      revenue: 54000,
      conversion_rate: 19.8,
      roas: 3.0,
      is_best: false,
    },
  ];

  return (
    <div className="space-y-6">
      {/* Title & Concept */}
      <div>
        <h2 className="text-xl font-bold text-slate-900 flex items-center gap-2">
          <span>AI Campaign Strategy</span>
        </h2>
        <p className="text-xs text-slate-500 mt-0.5">
          "Use historical campaign performance to decide where your next ₹ should go."
        </p>
      </div>

      {/* Campaign Budget Input Card */}
      <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-xs space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <label className="text-xs font-bold uppercase tracking-wider text-slate-500 block mb-1">
              Campaign Budget
            </label>
            <div className="flex items-center gap-2">
              <span className="text-xl font-bold text-slate-400">₹</span>
              <input
                type="number"
                value={budget}
                onChange={(e) => handleBudgetInput(e.target.value)}
                className="text-2xl font-extrabold text-slate-900 border-b-2 border-blue-600 focus:outline-none w-44 bg-transparent"
              />
            </div>
            <p className="text-[11px] text-slate-400 mt-1">Adjust budget to see real-time AI allocation</p>
          </div>

          {/* Quick preset chips */}
          <div className="flex items-center gap-2">
            <span className="text-xs text-slate-400 font-medium">Presets:</span>
            {[10000, 20000, 35000, 50000].map((amt) => (
              <button
                key={amt}
                onClick={() => handleBudgetInput(amt)}
                className={`text-xs px-3 py-1.5 rounded-lg border transition font-medium cursor-pointer ${
                  budget === amt
                    ? "bg-blue-50 border-blue-400 text-blue-700 font-bold"
                    : "bg-slate-50 border-slate-200 text-slate-600 hover:bg-slate-100"
                }`}
              >
                ₹{amt.toLocaleString("en-IN")}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Recommended Allocation Card */}
      <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-xs space-y-5">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pb-3 border-b border-slate-100">
          <div>
            <h3 className="text-sm font-bold text-slate-900">Recommended Allocation</h3>
            <p className="text-xs text-slate-500">
              Optimal portfolio allocation balancing audience reach and capital efficiency
            </p>
          </div>

          <div className="flex items-center gap-6">
            <div className="text-right">
              <span className="text-slate-400 block text-[11px]">Projected Revenue</span>
              <span className="text-lg font-extrabold text-emerald-600">
                ₹{projectedRevenue.toLocaleString("en-IN")}
              </span>
            </div>
            <div className="text-right border-l border-slate-100 pl-4">
              <span className="text-slate-400 block text-[11px]">Projected ROAS</span>
              <span className="text-lg font-extrabold text-blue-600">{roas}×</span>
            </div>
          </div>
        </div>

        {/* Multi-segment allocation bar */}
        <div className="space-y-2">
          <div className="h-3 w-full bg-slate-100 rounded-full overflow-hidden flex">
            <div className="bg-blue-600 h-full transition-all duration-500" style={{ width: "60%" }}></div>
            <div className="bg-indigo-500 h-full transition-all duration-500" style={{ width: "40%" }}></div>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 pt-2">
            {/* Cross-Sell 60% */}
            <div className="p-4 rounded-xl border border-slate-100 bg-slate-50/70 flex items-center justify-between">
              <div className="flex items-center gap-3">
                <span className="w-3.5 h-3.5 rounded-full bg-blue-600 shrink-0"></span>
                <div>
                  <div className="text-xs font-bold text-slate-900">Diffuser Cross-Sell Campaign</div>
                  <div className="text-[11px] text-slate-500">Targeting 36 customers • 4.23× historical ROAS</div>
                </div>
              </div>
              <div className="text-right">
                <div className="text-sm font-extrabold text-slate-900">₹{crossSellAmount.toLocaleString("en-IN")}</div>
                <div className="text-xs font-bold text-blue-600">60% of budget</div>
              </div>
            </div>

            {/* Win-Back 40% */}
            <div className="p-4 rounded-xl border border-slate-100 bg-slate-50/70 flex items-center justify-between">
              <div className="flex items-center gap-3">
                <span className="w-3.5 h-3.5 rounded-full bg-indigo-500 shrink-0"></span>
                <div>
                  <div className="text-xs font-bold text-slate-900">VIP Churn Win-Back Campaign</div>
                  <div className="text-[11px] text-slate-500">Targeting 15 dormant VIPs • 4.82× historical ROAS</div>
                </div>
              </div>
              <div className="text-right">
                <div className="text-sm font-extrabold text-slate-900">₹{winBackAmount.toLocaleString("en-IN")}</div>
                <div className="text-xs font-bold text-indigo-600">40% of budget</div>
              </div>
            </div>
          </div>
        </div>

        {/* Expandable Explanation */}
        <div className="pt-2 border-t border-slate-100">
          <button
            onClick={() => setShowExplanation(!showExplanation)}
            className="text-xs font-semibold text-blue-600 hover:text-blue-700 flex items-center gap-1.5 cursor-pointer"
          >
            <HelpCircle className="w-3.5 h-3.5" />
            <span>Why this allocation?</span>
            {showExplanation ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
          </button>

          {showExplanation && (
            <div className="mt-3 p-4 bg-blue-50/60 border border-blue-100 rounded-xl text-xs text-slate-700 leading-relaxed animate-fadeIn">
              <p className="font-semibold text-blue-900 mb-1">
                Deterministic Optimization from Historical Performance:
              </p>
              <p>
                Our analysis of your past four campaigns reveals that <strong>Q4 VIP Win-Back</strong> produced the
                highest return on ad spend (<strong>4.82× ROAS</strong>), but operates on a constrained audience of 15
                dormant VIPs. In contrast, <strong>Diffuser Cross-Sell</strong> delivers steady <strong>4.23× ROAS</strong>{" "}
                across a wider 36-customer cohort.
              </p>
              <p className="mt-1.5">
                The agent allocates <strong>60% (₹{crossSellAmount.toLocaleString("en-IN")})</strong> to Cross-Sell to
                capture volume liquidity and <strong>40% (₹{winBackAmount.toLocaleString("en-IN")})</strong> to
                Win-Back to achieve peak margin efficiency without audience saturation.
              </p>
            </div>
          )}
        </div>
      </div>

      {/* Historical Campaign Performance Table */}
      <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-xs space-y-4">
        <div>
          <h3 className="text-sm font-bold text-slate-900">Historical Campaign Performance</h3>
          <p className="text-xs text-slate-500">
            Performance metrics informing the agent's current allocation strategy
          </p>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs text-slate-600">
            <thead className="bg-slate-50 text-slate-500 uppercase tracking-wider text-[10px] border-b border-slate-200">
              <tr>
                <th className="py-3 px-4">Campaign</th>
                <th className="py-3 px-4">Type</th>
                <th className="py-3 px-4">Spend</th>
                <th className="py-3 px-4">Revenue</th>
                <th className="py-3 px-4">Conversion Rate</th>
                <th className="py-3 px-4 text-right">ROAS</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {historicalCampaigns.map((camp) => (
                <tr
                  key={camp.id}
                  className={`transition ${camp.is_best ? "bg-emerald-50/50 hover:bg-emerald-50" : "hover:bg-slate-50"}`}
                >
                  <td className="py-3 px-4 font-semibold text-slate-900 flex items-center gap-2">
                    <span>{camp.name}</span>
                    {camp.is_best && (
                      <span className="inline-flex items-center gap-1 bg-emerald-100 text-emerald-800 text-[10px] font-bold px-2 py-0.5 rounded-full">
                        <Award className="w-3 h-3 text-emerald-700" />
                        Best ROAS
                      </span>
                    )}
                  </td>
                  <td className="py-3 px-4 font-medium text-slate-500">{camp.type}</td>
                  <td className="py-3 px-4 font-medium text-slate-700">₹{camp.spend.toLocaleString("en-IN")}</td>
                  <td className="py-3 px-4 font-bold text-slate-900">₹{camp.revenue.toLocaleString("en-IN")}</td>
                  <td className="py-3 px-4 font-medium text-slate-700">{camp.conversion_rate}%</td>
                  <td className="py-3 px-4 text-right font-extrabold text-blue-700 text-sm">{camp.roas}×</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
