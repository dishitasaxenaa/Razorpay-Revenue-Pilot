import React, { useState } from "react";
import { ShieldAlert, Check, X, ArrowRight, AlertTriangle } from "lucide-react";

export default function ApprovalModal({ action, opportunity, isOpen, onClose, onApprove }) {
  if (!isOpen || !action) return null;

  const [selectedDiscount, setSelectedDiscount] = useState(10.0); // Defaults to compliant 10% alternative
  const [notes, setNotes] = useState("Approved compliant 10% alternative to adhere to merchant guardrail policy.");
  const [isSubmitting, setIsSubmitting] = useState(false);

  const originalPrice = action.original_price || 4999.0;
  const compliantPrice = (originalPrice * 0.9).toFixed(2);
  const overridePrice = (originalPrice * 0.85).toFixed(2);

  const handleSelectAlternative = () => {
    setSelectedDiscount(10.0);
    setNotes("Adopted policy-compliant 10% alternative discount. Safeguards margin while driving reactivation.");
  };

  const handleKeepViolationOverride = () => {
    setSelectedDiscount(15.0);
    setNotes("Merchant manual override: Authorized 15% discount for high-value VIP cohort to ensure conversion.");
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsSubmitting(true);
    try {
      await onApprove(action.id, selectedDiscount, notes);
      onClose();
    } catch (err) {
      alert("Error approving action: " + err.message);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/50 backdrop-blur-xs animate-fadeIn">
      <div className="bg-white border border-slate-200 rounded-2xl max-w-lg w-full p-6 shadow-2xl space-y-5">
        {/* Header */}
        <div className="flex items-start justify-between pb-3 border-b border-slate-100">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-amber-50 border border-amber-200 flex items-center justify-center text-amber-700">
              <ShieldAlert className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-base font-bold text-slate-900">Policy Review &amp; Approval</h3>
              <p className="text-xs text-slate-500">Autonomous action exceeded merchant guardrails</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="text-slate-400 hover:text-slate-600 p-1.5 rounded-lg hover:bg-slate-100 transition cursor-pointer"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Demonstrable Failure Box */}
        <div className="bg-amber-50/70 border border-amber-200 rounded-xl p-4 text-xs space-y-2">
          <div className="flex items-center gap-1.5 text-amber-900 font-bold">
            <AlertTriangle className="w-4 h-4 text-amber-600" />
            <span>POLICY REVIEW REQUIRED</span>
          </div>

          <div className="grid grid-cols-2 gap-2 text-slate-700 pt-1">
            <div>
              <span className="text-slate-500 block text-[11px]">Requested Discount:</span>
              <span className="font-bold text-rose-600 text-sm">15.0%</span>
            </div>
            <div>
              <span className="text-slate-500 block text-[11px]">Maximum Allowed:</span>
              <span className="font-bold text-slate-900 text-sm">10.0%</span>
            </div>
          </div>

          <p className="text-slate-600 text-[11px] leading-relaxed pt-1">
            <strong>Reason:</strong> Exceeds merchant-defined autonomous discount limit (10.0%). The agent proposed 15%
            to maximize reactivation across the 15 dormant VIPs, but the policy engine intercepted it to preserve profit margins.
          </p>
        </div>

        {/* Resolution Options */}
        <div className="space-y-2.5">
          <div className="text-xs font-semibold text-slate-700 uppercase tracking-wider text-[11px]">
            Select Approval Resolution:
          </div>

          {/* Option 1: Compliant 10% Alternative (Recommended) */}
          <div
            onClick={handleSelectAlternative}
            className={`p-3.5 rounded-xl border cursor-pointer transition flex items-center justify-between ${
              selectedDiscount === 10.0
                ? "bg-blue-50/60 border-blue-500 ring-1 ring-blue-500 text-slate-900"
                : "bg-white border-slate-200 text-slate-700 hover:bg-slate-50"
            }`}
          >
            <div className="flex items-center gap-3">
              <div
                className={`w-4 h-4 rounded-full border flex items-center justify-center ${
                  selectedDiscount === 10.0 ? "border-blue-600 bg-blue-600" : "border-slate-300 bg-white"
                }`}
              >
                {selectedDiscount === 10.0 && <Check className="w-3 h-3 text-white stroke-[3]" />}
              </div>
              <div>
                <div className="text-xs font-bold flex items-center gap-2">
                  <span>Adopt Recommended 10.0% Alternative</span>
                  <span className="text-[10px] bg-emerald-100 text-emerald-800 px-2 py-0.2 rounded-full font-semibold">
                    Policy Compliant
                  </span>
                </div>
                <div className="text-[11px] text-slate-500 mt-0.5">
                  Adjusted price: <strong className="text-slate-900">₹{compliantPrice}</strong> (Preserves margin, within policy)
                </div>
              </div>
            </div>
            <div className="text-right font-bold text-blue-700 text-xs">10% Off</div>
          </div>

          {/* Option 2: Override to 15% */}
          <div
            onClick={handleKeepViolationOverride}
            className={`p-3.5 rounded-xl border cursor-pointer transition flex items-center justify-between ${
              selectedDiscount === 15.0
                ? "bg-amber-50/60 border-amber-500 ring-1 ring-amber-500 text-slate-900"
                : "bg-white border-slate-200 text-slate-700 hover:bg-slate-50"
            }`}
          >
            <div className="flex items-center gap-3">
              <div
                className={`w-4 h-4 rounded-full border flex items-center justify-center ${
                  selectedDiscount === 15.0 ? "border-amber-600 bg-amber-600" : "border-slate-300 bg-white"
                }`}
              >
                {selectedDiscount === 15.0 && <Check className="w-3 h-3 text-white stroke-[3]" />}
              </div>
              <div>
                <div className="text-xs font-bold flex items-center gap-2">
                  <span>Merchant Manual Override: Authorize 15.0%</span>
                  <span className="text-[10px] bg-amber-100 text-amber-800 px-2 py-0.2 rounded-full font-semibold">
                    Manual Sign-off
                  </span>
                </div>
                <div className="text-[11px] text-slate-500 mt-0.5">
                  Discounted price: <strong className="text-slate-900">₹{overridePrice}</strong> (Prioritizes reactivation)
                </div>
              </div>
            </div>
            <div className="text-right font-bold text-amber-700 text-xs">15% Off</div>
          </div>
        </div>

        {/* Justification note */}
        <div>
          <label className="block text-[11px] font-medium text-slate-600 mb-1">
            Audit Trail Justification (Recorded in immutable log):
          </label>
          <input
            type="text"
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
            className="w-full bg-slate-50 border border-slate-200 rounded-lg px-3 py-2 text-xs text-slate-800 focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>

        {/* Footer Actions */}
        <div className="flex items-center justify-end gap-2.5 pt-3 border-t border-slate-100">
          <button
            type="button"
            onClick={onClose}
            className="px-4 py-2 text-xs font-medium text-slate-600 hover:text-slate-900 hover:bg-slate-100 rounded-lg transition cursor-pointer"
          >
            Cancel
          </button>
          <button
            onClick={handleSubmit}
            disabled={isSubmitting}
            className="flex items-center gap-1.5 bg-blue-600 hover:bg-blue-700 text-white text-xs font-semibold px-4 py-2.5 rounded-lg shadow-sm transition disabled:opacity-50 cursor-pointer"
          >
            <span>{isSubmitting ? "Generating Link..." : "Approve & Generate Razorpay Test Link"}</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>
    </div>
  );
}
