from datetime import date

from ai_agent.recommender import build_rule_proposal, rank_activities


ACTIVITIES = [
    {"id": "museum", "city_id": "paris", "name": "Museum", "category": "culture", "cost": 20, "duration_hours": 3},
    {"id": "food", "city_id": "paris", "name": "Food Tour", "category": "food", "cost": 50, "duration_hours": 2},
    {"id": "forum", "city_id": "rome", "name": "Forum", "category": "culture", "cost": 15, "duration_hours": 3},
]


def test_rank_activities_filters_city_and_prefers_requested_category():
    ranked = rank_activities(ACTIVITIES, "paris", ["food"], 100)
    assert [item["id"] for item in ranked] == ["food", "museum"]


def test_rule_proposal_uses_only_catalog_activities_within_budget():
    stops = [{"id": "stop-1", "city_id": "paris", "start_date": date(2026, 9, 1), "end_date": date(2026, 9, 2), "sequence": 10}]
    proposal = build_rule_proposal(stops, ACTIVITIES, {"goal": "balanced", "preferences": ["culture"], "daily_budget": 30})
    assert proposal.items
    assert {item.activity_id for item in proposal.items} == {"museum"}
    assert all(item.stop_id == "stop-1" for item in proposal.items)
    assert proposal.estimated_total == 20
