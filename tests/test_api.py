import sys
import json
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)


def test_health():
    print("Testing /api/health...")
    response = client.get("/api/health")
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    data = response.json()
    assert data["status"] == "healthy"
    print("  [OK] Health check passed:", data)


def test_frontend_static():
    print("Testing static frontend /...")
    response = client.get("/")
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    assert "GigPitch" in response.text
    assert "Hacktoberfest 2026" in response.text
    print("  [OK] Static frontend served correctly.")


def test_generate_stream():
    print("Testing /api/generate streaming endpoint...")
    payload = {
        "job_description": "Need a React landing page for a SaaS product. Budget $500.",
        "skills": "React, Tailwind CSS, 3 years experience.",
        "tone": "professional"
    }
    with client.stream("POST", "/api/generate", json=payload) as response:
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        lines = []
        for line in response.iter_lines():
            if line:
                lines.append(line)
        
        full_text = "".join(lines)
        assert len(lines) > 2, "Expected multiple SSE streaming lines"
        assert "data:" in full_text
        print(f"  [OK] Streaming generation passed ({len(lines)} chunks received).")


if __name__ == "__main__":
    test_health()
    test_frontend_static()
    test_generate_stream()
    print("\nALL AUTOMATED TESTS PASSED SUCCESSFULLY! [PASS]")
