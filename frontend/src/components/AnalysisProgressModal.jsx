import React, { useState, useEffect } from "react";
import { Sparkles, Check, Loader2 } from "lucide-react";

export default function AnalysisProgressModal({ isOpen, onComplete, opportunitiesCount = 4 }) {
  const [step, setStep] = useState(0);

  const steps = [
    "Analyzing historical transactions (210 orders)...",
    "Evaluating customer RFM profiles (60 customers)...",
    "Calculating product affinities and consumable replenishment...",
    "Benchmarking historical campaign ROAS performance...",
    "Synthesizing revenue opportunities and projecting pipeline...",
    "Validating proposed actions against merchant guardrails (10% limit)...",
  ];

  useEffect(() => {
    if (!isOpen) {
      setStep(0);
      return;
    }

    const interval = setInterval(() => {
      setStep((prev) => {
        if (prev < steps.length) {
          return prev + 1;
        } else {
          clearInterval(interval);
          setTimeout(() => {
            onComplete?.();
          }, 600);
          return prev;
        }
      });
    }, 450);

    return () => clearInterval(interval);
  }, [isOpen]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/40 backdrop-blur-xs">
      <div className="bg-white border border-slate-200 rounded-2xl max-w-md w-full p-6 shadow-xl space-y-5 animate-fadeIn">
        {/* Header */}
        <div className="flex items-center gap-3 pb-3 border-b border-slate-100">
          <div className="w-10 h-10 rounded-xl bg-blue-50 border border-blue-100 flex items-center justify-center text-blue-600">
            <Sparkles className="w-5 h-5 animate-pulse" />
          </div>
          <div>
            <h3 className="text-base font-bold text-slate-900">AI Growth Engine Active</h3>
            <p className="text-xs text-slate-500">Autonomous data synthesis and opportunity modeling</p>
          </div>
        </div>

        {/* Steps List */}
        <div className="space-y-2.5">
          {steps.map((text, idx) => {
            const isDone = step > idx;
            const isCurrent = step === idx;

            return (
              <div
                key={idx}
                className={`flex items-center gap-3 p-2.5 rounded-lg text-xs transition ${
                  isDone
                    ? "bg-slate-50 text-slate-700 font-medium"
                    : isCurrent
                    ? "bg-blue-50/80 text-blue-800 font-semibold border border-blue-100"
                    : "text-slate-400 opacity-60"
                }`}
              >
                <div className="w-5 h-5 rounded-full flex items-center justify-center shrink-0">
                  {isDone ? (
                    <div className="w-5 h-5 rounded-full bg-emerald-100 text-emerald-700 flex items-center justify-center">
                      <Check className="w-3 h-3 stroke-[3]" />
                    </div>
                  ) : isCurrent ? (
                    <Loader2 className="w-4 h-4 text-blue-600 animate-spin" />
                  ) : (
                    <div className="w-2 h-2 rounded-full bg-slate-300"></div>
                  )}
                </div>
                <span>{text}</span>
              </div>
            );
          })}
        </div>

        {/* Conclusion when done */}
        {step >= steps.length && (
          <div className="p-3 bg-emerald-50 border border-emerald-200 rounded-xl text-xs font-bold text-emerald-800 text-center animate-fadeIn">
            ✓ {opportunitiesCount} Growth Opportunities Identified &amp; Policy-Evaluated
          </div>
        )}
      </div>
    </div>
  );
}
