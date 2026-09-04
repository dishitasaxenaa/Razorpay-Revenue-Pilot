import React, { useState, useEffect } from "react";
import { Sliders, X, Shield, Check } from "lucide-react";

export default function PolicyModal({ isOpen, onClose, policy, onUpdatePolicy }) {
  if (!isOpen) return null;

  const [maxDiscount, setMaxDiscount] = useState(policy?.max_autonomous_discount_pct || 10.0);
  const [maxBudget, setMaxBudget] = useState(policy?.max_campaign_budget || 25000.0);
  const [requireApproval, setRequireApproval] = useState(policy?.require_human_approval_over_discount ?? true);
  const [isSaving, setIsSaving] = useState(false);

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
      onClose();
    } catch (err) {
      alert("Failed to update policy: " + err.message);
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-sm">
      <div className="bg-slate-900 border border-slate-700 rounded-2xl max-w-lg w-full p-6 shadow-2xl space-y-5">
        <div className="flex items-center justify-between pb-3 border-b border-slate-800">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-sky-500/10 border border-sky-500/30 flex items-center justify-center text-sky-400">
              <Sliders className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-lg font-bold text-white">Merchant Guardrail Settings</h3>
              <p className="text-xs text-slate-400">Autonomous Execution Boundaries &amp; Safety Limits</p>
            </div>
          </div>
          <button onClick={onClose} className="text-slate-400 hover:text-white p-1 rounded-lg hover:bg-slate-800 transition">
            <X className="w-5 h-5" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4 text-xs">
          {/* Max Autonomous Discount */}
          <div>
            <div className="flex justify-between mb-1">
              <label className="font-semibold text-slate-300">Max Autonomous Discount (%)</label>
              <span className="font-bold text-sky-400">{maxDiscount}%</span>
            </div>
            <p className="text-slate-400 text-[11px] mb-2">
              Any AI proposed discount higher than this will trigger a <strong>POLICY BLOCKED</strong> state and require human sign-off.
            </p>
            <input
              type="range"
              min="0"
              max="30"
              step="1"
              value={maxDiscount}
              onChange={(e) => setMaxDiscount(e.target.value)}
              className="w-full h-2 bg-slate-850 rounded-lg appearance-none cursor-pointer accent-sky-500"
            />
          </div>

          {/* Max Campaign Budget */}
          <div>
            <label className="block font-semibold text-slate-300 mb-1">Max Autonomous Campaign Budget (₹)</label>
            <input
              type="number"
              value={maxBudget}
              onChange={(e) => setMaxBudget(e.target.value)}
              className="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-white focus:outline-none focus:ring-2 focus:ring-sky-500"
            />
          </div>

          {/* Require Human Approval Toggle */}
          <div className="flex items-center justify-between p-3 bg-slate-800/40 rounded-xl border border-slate-750">
            <div>
              <div className="font-bold text-white">Mandatory Human Sign-Off on Violations</div>
              <div className="text-[11px] text-slate-400">Enforces HITL review before any payment links are created.</div>
            </div>
            <input
              type="checkbox"
              checked={requireApproval}
              onChange={(e) => setRequireApproval(e.target.checked)}
              className="w-4 h-4 rounded text-sky-500 focus:ring-sky-400"
            />
          </div>

          <div className="flex items-center justify-end gap-3 pt-3 border-t border-slate-800">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 text-xs font-medium text-slate-400 hover:text-white transition"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isSaving}
              className="bg-sky-500 hover:bg-sky-400 text-slate-950 font-bold px-5 py-2.5 rounded-lg transition disabled:opacity-50"
            >
              {isSaving ? "Saving..." : "Save Guardrails"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
