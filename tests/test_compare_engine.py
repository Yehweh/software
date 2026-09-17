import io
import pytest
from app import app
from src.compare_engine import extract_standardized_metrics, compare_entities


def test_extract_standardized_metrics_file():
    sample_file = {
        "name": "calc.py",
        "language": "Python",
        "lines": 100,
        "metrics": {
            "lines_of_code": 85,
            "num_functions": 8,
            "num_classes": 1,
            "num_imports": 4,
            "comment_density": 15.0,
            "avg_function_length": 10.5,
            "cyclomatic_complexity": 5.0,
            "max_nesting_depth": 2,
            "todo_count": 1,
            "fixme_count": 0,
            "coupling_between_objects": 3,
            "lack_of_cohesion": 0.1,
            "security_vulnerabilities": 0,
            "past_defects": 0,
            "code_churn": 1,
        },
        "technical_debt": {
            "score": 25,
            "level": "Low Technical Debt",
            "reasons": ["Software quality metrics are within acceptable limits."]
        }
    }

    res = extract_standardized_metrics(sample_file, "Candidate 1")
    assert res["name"] == "calc.py"
    assert res["type"] == "File (Python)"
    assert res["debt_score"] == 25
    assert res["debt_level"] == "Low Technical Debt"
    assert res["num_functions"] == 8
    assert res["cyclomatic_complexity"] == 5.0


def test_compare_entities_winner_b():
    entity_a = {
        "name": "legacy_service.js",
        "language": "JavaScript",
        "lines": 350,
        "metrics": {
            "lines_of_code": 300,
            "num_functions": 25,
            "cyclomatic_complexity": 28.0,
            "security_vulnerabilities": 2,
            "comment_density": 2.5,
            "avg_function_length": 35.0,
            "max_nesting_depth": 6,
            "todo_count": 4,
            "fixme_count": 2,
        },
        "technical_debt": {
            "score": 75,
            "level": "High Technical Debt",
            "reasons": ["High Cyclomatic Complexity", "Deeply Nested Code"]
        }
    }

    entity_b = {
        "name": "refactored_service.js",
        "language": "JavaScript",
        "lines": 180,
        "metrics": {
            "lines_of_code": 150,
            "num_functions": 18,
            "cyclomatic_complexity": 8.0,
            "security_vulnerabilities": 0,
            "comment_density": 18.0,
            "avg_function_length": 9.5,
            "max_nesting_depth": 2,
            "todo_count": 0,
            "fixme_count": 0,
        },
        "technical_debt": {
            "score": 20,
            "level": "Low Technical Debt",
            "reasons": ["Software quality metrics are within acceptable limits."]
        }
    }

    result = compare_entities(entity_a, entity_b)
    summary = result["summary"]

    assert summary["winner"] == "B"
    assert summary["winner_name"] == "refactored_service.js"
    assert summary["loser_name"] == "legacy_service.js"
    assert summary["diff_points"] == 55
    assert summary["pct_improvement"] > 70  # ~73.3%
    assert "🏆 refactored_service.js has Lower Technical Debt" in summary["headline"]
    assert len(summary["highlights"]) > 0

    # Verify metrics comparison table list
    metric_keys = [m["key"] for m in result["metrics"]]
    assert "debt_score" in metric_keys
    assert "cyclomatic_complexity" in metric_keys
    assert "security_vulnerabilities" in metric_keys

    # Check advantages
    debt_m = next(m for m in result["metrics"] if m["key"] == "debt_score")
    assert debt_m["advantage"] == "B"
    assert debt_m["delta"] == -55


def test_compare_entities_tie():
    entity_a = {
        "name": "mod_a.py",
        "metrics": {"cyclomatic_complexity": 5.0},
        "technical_debt": {"score": 30, "level": "Low Technical Debt"}
    }
    entity_b = {
        "name": "mod_b.py",
        "metrics": {"cyclomatic_complexity": 5.0},
        "technical_debt": {"score": 30, "level": "Low Technical Debt"}
    }

    result = compare_entities(entity_a, entity_b)
    assert result["summary"]["winner"] == "TIE"
    assert result["summary"]["diff_points"] == 0


def test_flask_compare_files_endpoint():
    app.config["TESTING"] = True
    app.secret_key = "test-secret"

    client = app.test_client()

    with client.session_transaction() as sess:
        sess["user_id"] = 1
        sess["username"] = "TestUser"

    file_a = (io.BytesIO(b"function oldCode() { if (true) { for(;;) {} } }"), "old.js")
    file_b = (io.BytesIO(b"function cleanCode() { return 42; }"), "clean.js")

    response = client.post(
        "/compare-files",
        data={
            "file_a": file_a,
            "file_b": file_b
        },
        content_type="multipart/form-data",
        follow_redirects=True
    )

    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert "Executive Summary Report" in html or "EXECUTIVE SUMMARY REPORT" in html
    assert "old.js" in html
    assert "clean.js" in html
    assert "Metric Differential Comparison" in html
