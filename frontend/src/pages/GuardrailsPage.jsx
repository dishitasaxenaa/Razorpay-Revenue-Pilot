import React, { useState, useEffect } from "react";
import { ShieldCheck, Sliders, CheckCircle, AlertCircle } from "lucide-react";

export default function GuardrailsPage({ policy, onUpdatePolicy }) {
  const [maxDiscount, setMaxDiscount] = useState(policy?.max_autonomous_discount_pct || 10.0);
  const [maxBudget, setMaxBudget] = useState(policy?.max_campaign_budget || 20000.0);
  const [requireApproval, setRequireApproval] = useState(policy?.require_human_approval_over_discount ?? true);
  const [isSaving, setIsSaving] = useState(false);
  const [savedSuccess, setSavedSuccess] = useState(false);

  useEffect(() => {
    if (policy) {
      setMaxDiscount(policy.max_autonomous_discount_pct);
      setMaxBudget(policy.max_campaign_budget);
      setRequireApproval(policy.require_human_approval_over_discount);
    }
  }, [policy]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsSaving(true);
    try {
      await onUpdatePolicy({
        max_autonomous_discount_pct: Number(maxDiscount),
        max_campaign_budget: Number(maxBudget),
        require_human_approval_over_discount: requireApproval,
      });
      setSavedSuccess(true);
      setTimeout(() => setSavedSuccess(false), 3000);
    } catch (err) {
      alert("Failed to update guardrail policies: " + err.message);
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div className="space-y-6 max-w-4xl">
      <div>
        <h2 className="text-xl font-bold text-slate-900">Merchant Policy Guardrails</h2>
        <p className="text-xs text-slate-500 mt-0.5">
          "These policies bound what the AI Revenue Agent can execute autonomously."
        </p>
      </div>

      <form onSubmit={handleSubmit} className="bg-white border border-slate-200 rounded-xl p-6 shadow-xs space-y-6">
        {/* Guardrail Overview Notice */}
        <div className="bg-blue-50/60 border border-blue-100 rounded-xl p-4 flex items-start gap-3 text-xs">
          <ShieldCheck className="w-5 h-5 text-blue-600 shrink-0 mt-0.5" />
          <div className="space-y-1">
            <div className="font-bold text-blue-900">Safety &amp; Compliance Boundary</div>
            <p className="text-slate-600 text-[11px] leading-relaxed">
              Any growth action formulated by Claude reasoning that exceeds these limits will be automatically{" "}
              <strong>BLOCKED</strong> and redirected to Human-in-the-Loop review before generating a Razorpay test link.
            </p>
          </div>
        </div>

        {/* 1. Maximum Autonomous Discount */}
        <div className="p-4 bg-slate-50 rounded-xl border border-slate-200/80 space-y-2">
          <div className="flex items-center justify-between">
            <div>
              <label className="text-xs font-bold text-slate-900 block">Maximum Autonomous Discount</label>
              <span className="text-[11px] text-slate-500">
                Offers proposing discounts exceeding this cap trigger immediate policy review.
              </span>
            </div>
            <span className="text-lg font-extrabold text-blue-700 bg-white px-3 py-1 rounded-lg border border-slate-200 shadow-2xs">
              {maxDiscount}%
            </span>
          </div>

          <input
            type="range"
            min="5"
            max="10"
            step="1"
            value={maxDiscount}
            onChange={(e) => setMaxDiscount(e.target.value)}
            className="w-full h-2 bg-slate-200 rounded-lg appearance-none cursor-pointer accent-blue-600"
          />
          <div className="flex justify-between text-[10px] text-slate-400 font-medium">
            <span>5% (Conservative)</span>
            <span className="text-blue-700 font-bold">10% (Default Safe Bound)</span>
            <span>10% (Hard Ceiling)</span>
          </div>
        </div>

        {/* 2. Maximum Campaign Budget */}
        <div className="p-4 bg-slate-50 rounded-xl border border-slate-200/80 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <label className="text-xs font-bold text-slate-900 block">Maximum Autonomous Campaign Budget</label>
            <span className="text-[11px] text-slate-500">Total automated discount subsidy cap across active cohorts.</span>
          </div>

          <div className="flex items-center gap-2">
            <span className="text-xs text-slate-400 font-bold">₹</span>
            <input
              type="number"
              value={maxBudget}
              onChange={(e) => setMaxBudget(e.target.value)}
              className="bg-white border border-slate-200 rounded-lg px-3 py-1.5 text-xs font-bold text-slate-900 w-32 focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
        </div>

        {/* 3. Pre-configured Policy Toggles */}
        <div className="space-y-3 pt-2">
          {/* Maximum Autonomous Transaction */}
          <div className="p-3.5 bg-white rounded-xl border border-slate-200 flex items-center justify-between">
            <div>
              <div className="text-xs font-bold text-slate-900">Maximum Autonomous Transaction</div>
              <div className="text-[11px] text-slate-500">Individual checkout links capped at ₹5,000 autonomously.</div>
            </div>
            <span className="text-xs font-bold text-slate-700 bg-slate-100 px-2.5 py-1 rounded-md">₹5,000</span>
          </div>

          {/* Auto-create Payment Links */}
          <div className="p-3.5 bg-white rounded-xl border border-slate-200 flex items-center justify-between">
            <div>
              <div className="text-xs font-bold text-slate-900">Auto-create Payment Links</div>
              <div className="text-[11px] text-slate-500">Merchant explicitly generates a link only after approval.</div>
            </div>
            <span className="text-xs font-bold text-emerald-700 bg-emerald-50 border border-emerald-200 px-2.5 py-0.5 rounded-full">
              HUMAN-GATED
            </span>
          </div>

          {/* Auto-refunds */}
          <div className="p-3.5 bg-white rounded-xl border border-slate-200 flex items-center justify-between">
            <div>
              <div className="text-xs font-bold text-slate-900">Auto-refunds</div>
              <div className="text-[11px] text-slate-500">Agent autonomous refund permissions.</div>
            </div>
            <span className="text-xs font-bold text-slate-500 bg-slate-100 px-2.5 py-0.5 rounded-full">OFF</span>
          </div>

          {/* Mandatory Human Approval Above Limit */}
          <div className="p-3.5 bg-white rounded-xl border border-slate-200 flex items-center justify-between">
            <div>
              <div className="text-xs font-bold text-slate-900">Human Approval Required Above {maxDiscount}%</div>
              <div className="text-[11px] text-slate-500">
                Mandates merchant sign-off for any action proposal crossing limits.
              </div>
            </div>
            <input
              type="checkbox"
              checked={requireApproval}
              onChange={(e) => setRequireApproval(e.target.checked)}
              className="w-4 h-4 rounded text-blue-600 focus:ring-blue-500 cursor-pointer"
            />
          </div>
        </div>

        {/* Footer & Submit */}
        <div className="flex items-center justify-between pt-4 border-t border-slate-100">
          <div>
            {savedSuccess && (
              <span className="text-xs text-emerald-600 font-semibold flex items-center gap-1">
                <CheckCircle className="w-3.5 h-3.5" />
                <span>Guardrails updated and recorded in SQLite audit log!</span>
              </span>
            )}
          </div>

          <button
            type="submit"
            disabled={isSaving}
            className="bg-blue-600 hover:bg-blue-700 text-white text-xs font-semibold px-5 py-2.5 rounded-lg shadow-sm transition disabled:opacity-50 cursor-pointer"
          >
            {isSaving ? "Saving..." : "Save Guardrail Policies"}
          </button>
        </div>
      </form>
    </div>
  );
}
