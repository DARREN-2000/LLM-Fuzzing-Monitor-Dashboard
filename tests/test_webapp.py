import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
WEBAPP_DIR = REPO_ROOT / "webapp"


def test_webapp_assets_exist():
    assert (WEBAPP_DIR / "index.html").exists()
    assert (WEBAPP_DIR / "styles.css").exists()
    assert (WEBAPP_DIR / "app.js").exists()


def test_sample_sessions_json_schema():
    sample_data_file = WEBAPP_DIR / "sample-data" / "sessions.json"
    assert sample_data_file.exists()

    payload = json.loads(sample_data_file.read_text(encoding="utf-8"))
    assert isinstance(payload, list)
    assert len(payload) > 0

    required_fields = {
        "session_id",
        "llm_provider",
        "llm_model",
        "status",
        "fuzz_drivers_generated",
        "security_vulnerabilities_found",
        "total_duration_ms",
        "estimated_cost_usd",
        "total_tokens_consumed",
        "total_api_calls",
    }

    for session in payload:
        assert isinstance(session, dict)
        assert required_fields.issubset(session.keys())

        assert isinstance(session["session_id"], str)
        assert isinstance(session["llm_provider"], str)
        assert isinstance(session["llm_model"], str)
        assert isinstance(session["status"], str)

        assert isinstance(session["fuzz_drivers_generated"], (int, float))
        assert isinstance(session["security_vulnerabilities_found"], (int, float))
        assert isinstance(session["total_duration_ms"], (int, float))
        assert isinstance(session["estimated_cost_usd"], (int, float))
        assert isinstance(session["total_tokens_consumed"], (int, float))
        assert isinstance(session["total_api_calls"], (int, float))
