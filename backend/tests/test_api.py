"""
Integration tests for Scam Shield API endpoints (backend/main.py).
Tests health, text analysis endpoint, persistence in SQLite, history retrieval, stats,
LLM provider mocking (success, retry, fallback), and image upload endpoint.
"""

import io
import json
import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from backend.main import app, llm_analyzer
from backend.database import get_session
from backend.provider import BaseLLMProvider


# Mock LLM Provider
class MockLLMProvider(BaseLLMProvider):
    def __init__(self, mode="success"):
        self.mode = mode
        self.call_count = 0
        self.model_name = "gemini-3.8-flash-mock"

    def is_available(self) -> bool:
        return self.mode != "unavailable"

    def generate_text(self, prompt: str, system_instruction: str) -> str:
        self.call_count += 1
        if self.mode == "fail":
            raise RuntimeError("API quota exceeded")
        if self.mode == "invalid_json_then_success":
            if self.call_count == 1:
                return "Not valid json at all!"
            # On second call (retry) return valid json
            return json.dumps({
                "verdict": "SCAM",
                "risk_score": 90,
                "scam_category": "KYC_BANK",
                "red_flags": ["Impersonates SBI", "Phishing link detected"],
                "explanation": "This is a bank impersonation phishing message.",
                "what_to_do": ["Do not click link", "Call 1930"],
                "confidence": 0.95
            })

        # Default success response
        return json.dumps({
            "verdict": "SCAM",
            "risk_score": 88,
            "scam_category": "UTILITY_BILL",
            "red_flags": ["Electricity disconnection threat", "Unregistered mobile phone"],
            "explanation": "This message is a fraudulent electricity bill disconnection notice.",
            "what_to_do": ["Do not call the number", "Verify bill on official portal", "Report to 1930"],
            "confidence": 0.92
        })

    def generate_vision(self, image_bytes: bytes, mime_type: str, prompt: str, system_instruction: str) -> str:
        if self.mode == "fail":
            raise RuntimeError("Vision model error")
        return json.dumps({
            "extracted_text": "Dear customer, your electricity power will be disconnected at 9:30 PM. Call 9876543210.",
            "verdict": "SCAM",
            "risk_score": 92,
            "scam_category": "UTILITY_BILL",
            "red_flags": ["Fake power disconnection threat", "Personal phone listed"],
            "explanation": "Transcribed screenshot reveals an urgent fake electricity disconnection threat.",
            "what_to_do": ["Do not contact the fraudster", "Report to cyber helpline 1930"],
            "confidence": 0.96
        })


@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session: Session):
    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


def test_health_check(client: TestClient):
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "timestamp" in data
    assert "ai_provider" in data


def test_analyze_text_with_mock_llm(client: TestClient):
    orig_provider = llm_analyzer.provider
    llm_analyzer.provider = MockLLMProvider(mode="success")

    payload = {
        "text": "Dear customer, your electricity power supply will be disconnected at 9:30 tonight. Call officer 9876543210 immediately.",
        "sender": None,
        "language": "en",
        "save_history": True
    }
    response = client.post("/api/analyze/text", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["verdict"] == "SCAM"
    assert data["scam_category"] == "UTILITY_BILL"
    assert data["risk_score"] >= 70
    assert data["rule_score"] > 0
    assert data["llm_score"] == 88
    assert data["report_draft"] is not None
    assert "9876543210" in data["entities"]["phones"]

    llm_analyzer.provider = orig_provider


def test_analyze_text_llm_retry_on_invalid_json(client: TestClient):
    orig_provider = llm_analyzer.provider
    mock = MockLLMProvider(mode="invalid_json_then_success")
    llm_analyzer.provider = mock

    payload = {
        "text": "Your SBI account is blocked due to KYC. Visit http://sbi-kyc.xyz immediately.",
        "sender": "+919876543210",
        "language": "en",
        "save_history": False
    }
    response = client.post("/api/analyze/text", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["verdict"] == "SCAM"
    assert mock.call_count == 2  # Proves retry was invoked

    llm_analyzer.provider = orig_provider


def test_analyze_text_fallback_on_llm_error(client: TestClient):
    orig_provider = llm_analyzer.provider
    llm_analyzer.provider = MockLLMProvider(mode="fail")

    payload = {
        "text": "Congratulations you won Rs. 25 Lakh in KBC lottery. Contact 9845012345.",
        "sender": None,
        "language": "en",
        "save_history": True
    }
    response = client.post("/api/analyze/text", json=payload)
    assert response.status_code == 200
    data = response.json()
    # Confirms it fell back to rule engine without crashing
    assert data["verdict"] in ("SCAM", "SUSPICIOUS")
    assert data["model_used"] == "deterministic_rule_engine"

    llm_analyzer.provider = orig_provider


def test_analyze_image_success(client: TestClient):
    orig_provider = llm_analyzer.provider
    llm_analyzer.provider = MockLLMProvider(mode="success")

    fake_image = io.BytesIO(b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDRfakeimagebytes")
    files = {"file": ("screenshot.png", fake_image, "image/png")}
    data = {"sender": "+919876543210", "language": "en", "save_history": "true"}

    response = client.post("/api/analyze/image", files=files, data=data)
    assert response.status_code == 200
    res = response.json()
    assert res["verdict"] == "SCAM"
    assert res["ocr_extracted_text"] is not None
    assert "electricity" in res["ocr_extracted_text"].lower()

    llm_analyzer.provider = orig_provider


def test_analyze_image_invalid_type(client: TestClient):
    fake_doc = io.BytesIO(b"%PDF-1.4 fake pdf")
    files = {"file": ("document.pdf", fake_doc, "application/pdf")}

    response = client.post("/api/analyze/image", files=files)
    assert response.status_code == 400
    assert "Unsupported image type" in response.json()["detail"]


def test_history_and_stats_flow(client: TestClient):
    orig_provider = llm_analyzer.provider
    llm_analyzer.provider = MockLLMProvider(mode="success")

    payload = {
        "text": "Your netbanking profile has expired. Re-authenticate now at http://192.168.1.105/auth.",
        "sender": None,
        "language": "en",
        "save_history": True
    }
    client.post("/api/analyze/text", json=payload)

    # Check history
    h_resp = client.get("/api/history")
    assert h_resp.status_code == 200
    h_data = h_resp.json()
    assert h_data["total"] >= 1

    # Check stats
    s_resp = client.get("/api/stats")
    assert s_resp.status_code == 200
    s_data = s_resp.json()
    assert s_data["total_scans"] >= 1
    assert s_data["avg_risk_score"] > 0

    llm_analyzer.provider = orig_provider
