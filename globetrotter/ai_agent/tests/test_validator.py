from ai_agent.proposal_schema import PlannerProposal, ProposalItem
from ai_agent.schedule_validator import validate_proposal


def _proposal(items, total):
    return PlannerProposal(summary="Test", estimated_total=total, items=items)


def test_validator_accepts_valid_catalog_schedule():
    stops = [{"id":"s1","city_id":"paris","start_date":"2026-09-01","end_date":"2026-09-02"}]
    activities = [{"id":"a1","city_id":"paris","name":"Museum","cost":20,"duration_hours":3}]
    item = ProposalItem(stop_id="s1", activity_id="a1", name="Museum", day_index=1, time_slot="10:00", cost=20)
    assert validate_proposal(_proposal([item], 20), stops, activities) == []


def test_validator_rejects_foreign_city_bad_day_cost_and_duration():
    stops = [{"id":"s1","city_id":"paris","start_date":"2026-09-01","end_date":"2026-09-01"}]
    activities = [{"id":"a1","city_id":"rome","name":"Long Tour","cost":20,"duration_hours":9}]
    item = ProposalItem(stop_id="s1", activity_id="a1", name="Long Tour", day_index=2, time_slot="10:00", cost=19)
    errors = validate_proposal(_proposal([item], 19), stops, activities)
    assert any("stop city" in error for error in errors)
    assert any("date range" in error for error in errors)
    assert any("cost" in error for error in errors)
    assert any("scheduled hours" in error for error in errors)
