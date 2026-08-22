from ai_agent.budget_estimator import estimate_budget, estimate_total


def test_budget_totals_by_trip_stop_and_day():
    items = [
        {"stop_id": "a", "day_index": 1, "cost": 12.25},
        {"stop_id": "a", "day_index": 1, "cost": 7.75},
        {"stop_id": "a", "day_index": 2, "cost": 5},
        {"stop_id": "b", "day_index": 1, "cost": 10},
    ]
    result = estimate_budget(items)
    assert estimate_total(items) == 35
    assert result == {
        "total": 35.0,
        "by_stop": {"a": 25.0, "b": 10.0},
        "by_day": {"a:1": 20.0, "a:2": 5.0, "b:1": 10.0},
    }
