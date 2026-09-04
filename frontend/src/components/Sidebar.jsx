import React from "react";
import {
  LayoutDashboard,
  Sparkles,
  Megaphone,
  CreditCard,
  Users,
  BarChart3,
  History,
  ShieldCheck,
  Settings,
  Store,
  Zap,
} from "lucide-react";

export default function Sidebar({ activeTab, onTabChange, opportunitiesCount, blockedCount, activeLinksCount }) {
  const navItems = [
    { id: "overview", label: "Overview", icon: LayoutDashboard },
    {
      id: "opportunities",
      label: "AI Opportunities",
      icon: Sparkles,
      badge: blockedCount > 0 ? `${blockedCount} Review` : opportunitiesCount > 0 ? `${opportunitiesCount}` : null,
      badgeColor: blockedCount > 0 ? "bg-amber-100 text-amber-800" : "bg-blue-100 text-blue-700",
    },
    { id: "campaigns", label: "Campaigns", icon: Megaphone },
    {
      id: "razorpay",
      label: "Razorpay Payments",
      icon: CreditCard,
      badge: activeLinksCount > 0 ? `${activeLinksCount} Live` : null,
      badgeColor: "bg-emerald-100 text-emerald-800",
    },
    { id: "customers", label: "Customers", icon: Users },
    { id: "analytics", label: "Analytics", icon: BarChart3 },
    { id: "audit", label: "Audit Trail", icon: History },
    { id: "guardrails", label: "Guardrails", icon: ShieldCheck },
    { id: "settings", label: "Settings", icon: Settings },
  ];

  return (
    <aside className="w-64 bg-white border-r border-slate-200 flex flex-col justify-between shrink-0 h-screen sticky top-0 z-20">
      {/* Brand Header */}
      <div>
        <div className="h-16 flex items-center px-6 border-b border-slate-100 gap-3">
          <div className="w-8 h-8 rounded-lg bg-blue-600 flex items-center justify-center text-white shadow-sm shadow-blue-500/30">
            <Zap className="w-4 h-4 fill-white" />
          </div>
          <div>
            <div className="font-bold text-slate-900 text-base tracking-tight leading-tight">Revenue Pilot</div>
            <div className="text-[11px] text-slate-500 font-medium leading-tight">AI Revenue Growth</div>
          </div>
        </div>

        {/* Navigation items */}
        <nav className="p-3 space-y-0.5">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = activeTab === item.id;

            return (
              <button
                key={item.id}
                onClick={() => onTabChange(item.id)}
                className={`w-full flex items-center justify-between px-3.5 py-2.5 rounded-lg text-xs font-medium transition cursor-pointer ${
                  isActive
                    ? "bg-blue-50 text-blue-700 font-semibold border-r-2 border-blue-600 rounded-r-none"
                    : "text-slate-600 hover:text-slate-900 hover:bg-slate-50"
                }`}
              >
                <div className="flex items-center gap-3">
                  <Icon className={`w-4 h-4 ${isActive ? "text-blue-600" : "text-slate-400"}`} />
                  <span>{item.label}</span>
                </div>
                {item.badge && (
                  <span className={`text-[10px] font-semibold px-2 py-0.5 rounded-full ${item.badgeColor}`}>
                    {item.badge}
                  </span>
                )}
              </button>
            );
          })}
        </nav>
      </div>

      {/* Merchant / Store Footer */}
      <div className="p-4 border-t border-slate-100 bg-slate-50/60 m-3 rounded-xl">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-full bg-slate-200 flex items-center justify-center text-slate-600">
            <Store className="w-4 h-4" />
          </div>
          <div className="min-w-0 flex-1">
            <div className="text-xs font-bold text-slate-900 truncate">Aura Living Store</div>
            <div className="flex items-center gap-1.5 mt-0.5">
              <span className="w-2 h-2 rounded-full bg-emerald-500"></span>
              <span className="text-[11px] font-medium text-slate-500">Razorpay Test Mode</span>
            </div>
          </div>
        </div>
      </div>
    </aside>
  );
}
