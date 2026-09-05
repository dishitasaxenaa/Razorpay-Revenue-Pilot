import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_all_endpoints():
    print("Testing /api/health...")
    r = client.get("/api/health")
    assert r.status_code == 200, f"Health check failed: {r.text}"
    print("Health response:", r.json())

    print("\nTesting /api/analytics/summary...")
    r = client.get("/api/analytics/summary")
    assert r.status_code == 200
    print("Analytics Summary:", r.json())

    print("\nTesting /api/goals/active...")
    r = client.get("/api/goals/active")
    assert r.status_code == 200
    print("Active Goal:", r.json())

    print("\nTesting /api/goals/policy...")
    r = client.get("/api/goals/policy")
    assert r.status_code == 200
    print("Active Policy Guardrails:", r.json())

    print("\nTesting /api/opportunities/analyze...")
    r = client.post("/api/opportunities/analyze")
    assert r.status_code == 200
    print("Opportunities Analyzed:", r.json()["strategy_summary"])

    print("\nTesting /api/actions...")
    r = client.get("/api/actions")
    assert r.status_code == 200
    actions = r.json()
    print(f"Total Action Proposals: {len(actions)}")
    for a in actions:
        print(f"  - Action #{a['id']}: Status={a['status']}, Proposed Discount={a['proposed_discount_pct']}%, Final Price=₹{a['final_price']}")

    print("\nTesting /api/audit/logs...")
    r = client.get("/api/audit/logs")
    assert r.status_code == 200
    logs = r.json()
    print(f"Total Audit Trail Entries: {len(logs)}")

    print("\nALL HTTP API ENDPOINTS TESTED SUCCESSFULLY!")

if __name__ == "__main__":
    test_all_endpoints()
