const API_BASE = "https://razorpay-revenue-pilot.onrender.com/api";

async function request(endpoint, options = {}) {
  const url = `${API_BASE}${endpoint}`;

  const config = {
    headers: {
      "Content-Type": "application/json",
      ...options.headers,
    },
    ...options,
  };

  const res = await fetch(url, config);

  if (!res.ok) {
    const errorText = await res.text();

    let errorDetail = "API Request failed";

    try {
      const errJson = JSON.parse(errorText);
      errorDetail = errJson.detail || errorText;
    } catch (_) {
      errorDetail = errorText || `HTTP ${res.status}`;
    }

    throw new Error(errorDetail);
  }

  return res.json();
}

export const api = {
  // Store & Analytics
  getStoreSummary: () => request("/analytics/summary"),
  getProducts: () => request("/analytics/products"),
  getCustomers: (segment) => request(`/analytics/customers${segment ? `?segment=${segment}` : ""}`),
  getCampaignStrategy: (budget = 20000) => request(`/analytics/campaigns?budget=${budget}`),
  resetDemoData: () => request("/analytics/reset-demo-data", { method: "POST" }),

  // Goals & Policies
  getActiveGoal: () => request("/goals/active"),
  setGoal: (prompt, target_amount) =>
    request("/goals", {
      method: "POST",
      body: JSON.stringify({ prompt, target_amount }),
    }),
  getPolicy: () => request("/goals/policy"),
  updatePolicy: (payload) =>
    request("/goals/policy", {
      method: "PUT",
      body: JSON.stringify(payload),
    }),

  // Opportunities
  getOpportunities: (goalId) => request(`/opportunities${goalId ? `?goal_id=${goalId}` : ""}`),
  triggerAnalysis: (goalId) =>
    request(`/opportunities/analyze${goalId ? `?goal_id=${goalId}` : ""}`, {
      method: "POST",
    }),
  triggerRecoveryProtocol: () => request("/opportunities/demo/recovery-protocol", { method: "POST" }),

  // Actions & HITL
  getActions: (goalId) => request(`/actions${goalId ? `?goal_id=${goalId}` : ""}`),
  approveAction: (actionId, overrideDiscountPct, notes) =>
    request("/actions/approve", {
      method: "POST",
      body: JSON.stringify({
        action_id: actionId,
        override_discount_pct: overrideDiscountPct,
        merchant_notes: notes,
      }),
    }),
  executeAction: (actionId, demoFailure = false) =>
    request(`/actions/${actionId}/execute${demoFailure ? "?demo_failure=true" : ""}`, { method: "POST" }),

  // Payment Webhook & Demo Simulator
  simulatePayment: (actionId) =>
    request("/webhooks/simulate", {
      method: "POST",
      body: JSON.stringify({ action_id: actionId }),
    }),

  // Audit Trail
  getAuditLogs: (goalId) => request(`/audit/logs${goalId ? `?goal_id=${goalId}` : ""}`),
};
