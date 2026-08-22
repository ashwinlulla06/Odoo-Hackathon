import pytest

from ai_agent.llm_planner import PlannerUnavailableError, generate_llm_proposal


def test_missing_key_is_a_controlled_fallback_signal(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    with pytest.raises(PlannerUnavailableError, match="not configured"):
        generate_llm_proposal([], [], api_key=None)
