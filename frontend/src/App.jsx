import React, { useState, useEffect, useCallback } from "react";
import { api } from "./api";
import Sidebar from "./components/Sidebar";
import Header from "./components/Header";
import AnalysisProgressModal from "./components/AnalysisProgressModal";
import ApprovalModal from "./components/ApprovalModal";

import OverviewPage from "./pages/OverviewPage";
import OpportunitiesPage from "./pages/OpportunitiesPage";
import CampaignsPage from "./pages/CampaignsPage";
import PaymentsPage from "./pages/PaymentsPage";
import CustomersPage from "./pages/CustomersPage";
import AnalyticsPage from "./pages/AnalyticsPage";
import AuditTrailPage from "./pages/AuditTrailPage";
import GuardrailsPage from "./pages/GuardrailsPage";
import SettingsPage from "./pages/SettingsPage";
import { Loader2 } from "lucide-react";

export default function App() {
  const [activeTab, setActiveTab] = useState("overview");

  const [summary, setSummary] = useState(null);
  const [goal, setGoal] = useState(null);
  const [policy, setPolicy] = useState(null);
  const [opportunities, setOpportunities] = useState([]);
  const [actions, setActions] = useState([]);
  const [auditLogs, setAuditLogs] = useState([]);
  const [customers, setCustomers] = useState([]);
  const [products, setProducts] = useState([]);
  const [campaignData, setCampaignData] = useState(null);

  const [selectedAction, setSelectedAction] = useState(null);
  const [selectedOpportunity, setSelectedOpportunity] = useState(null);
  const [isApprovalOpen, setIsApprovalOpen] = useState(false);
  const [isProgressModalOpen, setIsProgressModalOpen] = useState(false);

  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [isRecovering, setIsRecovering] = useState(false);
  const [isSimulating, setIsSimulating] = useState(false);
  const [isResetting, setIsResetting] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  // Load core application data
  const loadData = useCallback(async () => {
    try {
      const [sumRes, goalRes, polRes, oppRes, actRes, audRes, campRes] = await Promise.all([
        api.getStoreSummary(),
        api.getActiveGoal(),
        api.getPolicy(),
        api.getOpportunities(),
        api.getActions(),
        api.getAuditLogs(),
        api.getCampaignStrategy(20000),
      ]);
      setSummary(sumRes);
      setGoal(goalRes);
      setPolicy(polRes);
      setOpportunities(oppRes);
      setActions(actRes);
      setAuditLogs(audRes);
      setCampaignData(campRes);
    } catch (err) {
      console.error("Failed to load data:", err);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    loadData();
  }, [loadData]);

  // Load customer and product datasets if navigated to those tabs
  const handleTabChange = async (tab) => {
    setActiveTab(tab);
    if (tab === "customers" && customers.length === 0) {
      try {
        const custs = await api.getCustomers();
        setCustomers(custs);
      } catch (e) {
        console.error("Error loading customers", e);
      }
    }
    if (tab === "analytics" && products.length === 0) {
      try {
        const prods = await api.getProducts();
        setProducts(prods);
      } catch (e) {
        console.error("Error loading products", e);
      }
    }
  };

  // Run AI Growth Analysis with clean progress experience
  const handleRunAnalysis = async () => {
    setIsAnalyzing(true);
    setIsProgressModalOpen(true);
    try {
      await api.triggerAnalysis(goal?.id);
      await loadData();
    } catch (err) {
      alert("Analysis failed: " + err.message);
      setIsProgressModalOpen(false);
      setIsAnalyzing(false);
    }
  };

  const handleAnalysisComplete = () => {
    setIsProgressModalOpen(false);
    setIsAnalyzing(false);
    setActiveTab("opportunities");
  };

  const handleRecoveryProtocol = async () => {
    setIsRecovering(true);
    try {
      const result = await api.triggerRecoveryProtocol();
      await loadData();
      setActiveTab("opportunities");
      alert(`Recovery Protocol activated: ${result.opportunity_title}`);
    } catch (err) {
      alert("Recovery Protocol failed: " + err.message);
    } finally {
      setIsRecovering(false);
    }
  };

  // Set or update revenue directive
  const handleSetGoal = async (prompt, amount) => {
    try {
      const newGoal = await api.setGoal(prompt, amount);
      setGoal(newGoal);
      handleRunAnalysis();
    } catch (err) {
      alert("Failed to set goal: " + err.message);
    }
  };

  // Human-in-the-loop approval modal
  const handleOpenApproval = (action, opp) => {
    setSelectedAction(action);
    setSelectedOpportunity(opp);
    setIsApprovalOpen(true);
  };

  const handleApproveAction = async (actionId, overrideDiscount, notes) => {
    await api.approveAction(actionId, overrideDiscount, notes);
    await loadData();
    setActiveTab("opportunities");
  };

  const handleExecuteDirectly = async (actionId) => {
    try {
      await api.executeAction(actionId);
      await loadData();
      setActiveTab("razorpay");
    } catch (err) {
      alert("Execution failed: " + err.message);
    }
  };

  const handleDemoExecutionFailure = async (actionId) => {
    try {
      await api.executeAction(actionId, true);
    } catch (err) {
      alert("[DEMO / TESTING UTILITY] " + err.message);
    } finally {
      await loadData();
    }
  };

  // Simulate payment (DEMO / TESTING UTILITY)
  const handleSimulatePayment = async (actionId) => {
    setIsSimulating(true);
    try {
      await api.simulatePayment(actionId);
      await loadData();
    } catch (err) {
      alert("Simulation error: " + err.message);
    } finally {
      setIsSimulating(false);
    }
  };

  // Reset demo
  const handleResetDemo = async () => {
    if (!confirm("Reset database to clean initial state (60 customers, 12 products, ₹1,00,000 goal)?")) return;
    setIsResetting(true);
    try {
      await api.resetDemoData();
      setSelectedAction(null);
      setSelectedOpportunity(null);
      setIsApprovalOpen(false);
      setCustomers([]);
      setProducts([]);
      await loadData();
      setActiveTab("overview");
    } catch (err) {
      alert("Reset error: " + err.message);
    } finally {
      setIsResetting(false);
    }
  };

  const handleUpdatePolicy = async (newPolicy) => {
    await api.updatePolicy(newPolicy);
    await loadData();
  };

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-50 text-slate-800">
        <div className="flex items-center gap-3">
          <Loader2 className="w-6 h-6 text-blue-600 animate-spin" />
          <span className="font-semibold text-sm">Initializing Revenue Pilot Agent...</span>
        </div>
      </div>
    );
  }

  const blockedCount = actions.filter((a) => a.status === "BLOCKED").length;
  const activeLinksCount = actions.filter((a) => a.status === "EXECUTED" || a.razorpay_link_id).length;

  return (
    <div className="min-h-screen flex bg-slate-50 text-slate-900 antialiased">
      {/* Persistent Desktop Sidebar */}
      <Sidebar
        activeTab={activeTab}
        onTabChange={handleTabChange}
        opportunitiesCount={opportunities.length}
        blockedCount={blockedCount}
        activeLinksCount={activeLinksCount}
      />

      {/* Main App Area */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Top Header */}
        <Header
          activeTab={activeTab}
          onResetDemo={handleResetDemo}
          isResetting={isResetting}
        />

        {/* Dynamic Page Content */}
        <main className="flex-1 p-6 sm:p-8 max-w-7xl w-full mx-auto">
          {activeTab === "overview" && (
            <OverviewPage
              goal={goal}
              summary={summary}
              opportunities={opportunities}
              actions={actions}
              onRunAnalysis={handleRunAnalysis}
              onTriggerRecovery={handleRecoveryProtocol}
              onNavigateToTab={handleTabChange}
              isAnalyzing={isAnalyzing}
              isRecovering={isRecovering}
            />
          )}

          {activeTab === "opportunities" && (
            <OpportunitiesPage
              opportunities={opportunities}
              actions={actions}
              onSelectActionForApproval={handleOpenApproval}
              onExecuteDirectly={handleExecuteDirectly}
              onDemoExecutionFailure={handleDemoExecutionFailure}
              onNavigateToTab={handleTabChange}
            />
          )}

          {activeTab === "campaigns" && (
            <CampaignsPage
              campaignData={campaignData}
              onBudgetChange={async (b) => {
                const res = await api.getCampaignStrategy(b);
                setCampaignData(res);
              }}
            />
          )}

          {activeTab === "razorpay" && (
            <PaymentsPage
              actions={actions}
              onSimulatePayment={handleSimulatePayment}
              isSimulating={isSimulating}
            />
          )}

          {activeTab === "customers" && <CustomersPage customers={customers} />}

          {activeTab === "analytics" && (
            <AnalyticsPage
              summary={summary}
              goal={goal}
              products={products}
            />
          )}

          {activeTab === "audit" && <AuditTrailPage logs={auditLogs} />}

          {activeTab === "guardrails" && (
            <GuardrailsPage
              policy={policy}
              onUpdatePolicy={handleUpdatePolicy}
            />
          )}

          {activeTab === "settings" && <SettingsPage />}
        </main>
      </div>

      {/* Human-In-The-Loop Approval Modal */}
      <ApprovalModal
        action={selectedAction}
        opportunity={selectedOpportunity}
        isOpen={isApprovalOpen}
        onClose={() => setIsApprovalOpen(false)}
        onApprove={handleApproveAction}
      />

      {/* Step-by-Step AI Growth Progress Checklist Modal */}
      <AnalysisProgressModal
        isOpen={isProgressModalOpen}
        onComplete={handleAnalysisComplete}
        opportunitiesCount={opportunities.length || 4}
      />
    </div>
  );
}
