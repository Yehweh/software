import pytest
from app import app
from src.hotspot_engine import calculate_file_priority, calculate_file_hotspots
from src.quality_gate import evaluate_quality_gate, QUALITY_THRESHOLDS
from src.risk_engine import calculate_project_risk
from src.recommendation import generate_structured_recommendations


# ============================================================
# 1. HOTSPOT ENGINE TESTS
# ============================================================

def test_calculate_file_priority_critical():
    file_data = {
        "file_path": "src/heavy_module.py",
        "name": "heavy_module.py",
        "language": "Python",
        "lines": 750,
        "metrics": {
            "lines_of_code": 650,
            "cyclomatic_complexity": 22.0,
            "maintainability_index": 35.0,
            "todo_count": 5,
            "fixme_count": 3,
            "security_vulnerabilities": 2,
            "code_churn": 4
        },
        "technical_debt": {
            "score": 85.0,
            "level": "High Technical Debt",
            "reasons": ["High complexity", "Poor maintainability"]
        }
    }

    result = calculate_file_priority(file_data)
    assert result["priority_level"] == "CRITICAL"
    assert result["priority_score"] >= 75.0
    assert result["priority_badge_class"] == "priority-critical"
    assert len(result["reasons"]) >= 2
    assert "High Cyclomatic Complexity (22.0)" in result["reasons"]


def test_calculate_file_priority_low():
    file_data = {
        "file_path": "src/utils.py",
        "name": "utils.py",
        "language": "Python",
        "lines": 35,
        "metrics": {
            "lines_of_code": 25,
            "cyclomatic_complexity": 2.0,
            "maintainability_index": 88.0,
            "todo_count": 0,
            "fixme_count": 0,
            "security_vulnerabilities": 0
        },
        "technical_debt": {
            "score": 10.0,
            "level": "Low Technical Debt",
            "reasons": []
        }
    }

    result = calculate_file_priority(file_data)
    assert result["priority_level"] == "LOW"
    assert result["priority_score"] < 40.0
    assert result["priority_badge_class"] == "priority-low"


def test_calculate_file_hotspots_sorting():
    files = [
        {
            "file_path": "low.py",
            "name": "low.py",
            "lines": 20,
            "metrics": {"cyclomatic_complexity": 1.0, "lines_of_code": 15},
            "technical_debt": {"score": 5.0}
        },
        {
            "file_path": "crit.py",
            "name": "crit.py",
            "lines": 800,
            "metrics": {"cyclomatic_complexity": 30.0, "lines_of_code": 750, "security_vulnerabilities": 2},
            "technical_debt": {"score": 90.0}
        },
        {
            "file_path": "med.py",
            "name": "med.py",
            "lines": 250,
            "metrics": {"cyclomatic_complexity": 12.0, "lines_of_code": 200},
            "technical_debt": {"score": 45.0}
        }
    ]

    hotspots = calculate_file_hotspots(files)
    assert len(hotspots) == 3
    assert hotspots[0]["file_name"] == "crit.py"
    assert hotspots[0]["priority_score"] >= hotspots[1]["priority_score"]
    assert hotspots[1]["priority_score"] >= hotspots[2]["priority_score"]


# ============================================================
# 2. QUALITY GATE TESTS
# ============================================================

def test_evaluate_quality_gate_passed():
    metrics = {
        "average_debt_score": 25.0,
        "average_maintainability_index": 78.0,
        "average_cyclomatic_complexity": 4.5,
        "high_complexity_file_ratio": 0.0,
        "average_comment_density": 18.0,
        "code_duplication_ratio": 2.0,
        "test_coverage_status": "Tests Detected",
        "has_tests": True
    }
    files = [
        {"lines": 50, "metrics": {"cyclomatic_complexity": 3.0}, "technical_debt": {"score": 20.0}}
    ]

    gate = evaluate_quality_gate(metrics, files)
    assert gate["overall_status"] == "PASSED"
    assert gate["passed_count"] == gate["total_conditions"]
    assert gate["failed_count"] == 0
    assert len(gate["failed_reasons"]) == 0


def test_evaluate_quality_gate_failed():
    metrics = {
        "average_debt_score": 68.0,
        "average_maintainability_index": 42.0,
        "average_cyclomatic_complexity": 16.5,
        "high_complexity_file_ratio": 35.0,
        "code_duplication_ratio": 12.0,
        "has_tests": False
    }
    files = [
        {
            "lines": 900,
            "metrics": {"cyclomatic_complexity": 32.0, "security_vulnerabilities": 3},
            "technical_debt": {"score": 90.0}
        }
    ]

    gate = evaluate_quality_gate(metrics, files)
    assert gate["overall_status"] == "FAILED"
    assert gate["failed_count"] > 0
    assert len(gate["failed_reasons"]) > 0
    assert any("Average Technical Debt Score" in r for r in gate["failed_reasons"])


# ============================================================
# 3. RISK ENGINE TESTS
# ============================================================

def test_calculate_project_risk_low():
    metrics = {
        "average_debt_score": 15.0,
        "average_cyclomatic_complexity": 3.0,
        "average_maintainability_index": 82.0,
        "high_complexity_file_ratio": 0.0,
        "has_tests": True
    }
    files = []

    risk = calculate_project_risk(metrics, files)
    assert risk["risk_band"] == "LOW"
    assert risk["risk_score"] < 30.0
    assert "disclaimer" in risk
    assert len(risk["dimension_list"]) == 4


def test_calculate_project_risk_high():
    metrics = {
        "average_debt_score": 75.0,
        "average_cyclomatic_complexity": 24.0,
        "average_maintainability_index": 38.0,
        "high_complexity_file_ratio": 45.0,
        "code_duplication_ratio": 15.0,
        "has_tests": False
    }
    files = [
        {"lines": 1200, "metrics": {"cyclomatic_complexity": 28.0, "security_vulnerabilities": 2}, "technical_debt": {"score": 85.0}}
    ]

    risk = calculate_project_risk(metrics, files)
    assert risk["risk_band"] in ["HIGH", "CRITICAL"]
    assert risk["risk_score"] >= 55.0
    assert len(risk["top_drivers"]) > 0
    assert "complexity_defect" in risk["dimensions"]
    assert "maintainability" in risk["dimensions"]


# ============================================================
# 4. STRUCTURED RECOMMENDATIONS TESTS
# ============================================================

def test_generate_structured_recommendations_fields():
    metrics = {
        "average_cyclomatic_complexity": 18.0,
        "average_maintainability_index": 45.0,
        "high_complexity_file_ratio": 25.0,
        "code_duplication_ratio": 14.0,
        "average_comment_density": 4.0,
        "has_tests": False
    }
    debt = {"score": 65.0, "level": "High Technical Debt"}
    files = [
        {"file_path": "core/engine.py", "lines": 600, "metrics": {"cyclomatic_complexity": 22.0}}
    ]

    recs = generate_structured_recommendations(metrics, debt, files)
    assert len(recs) >= 3
    for rec in recs:
        assert "id" in rec
        assert "title" in rec
        assert "category" in rec
        assert "severity" in rec
        assert rec["severity"] in ["CRITICAL", "HIGH", "MEDIUM", "LOW"]
        assert "problem" in rec
        assert "impact" in rec
        assert "action" in rec
        assert isinstance(rec["problem"], str) and len(rec["problem"]) > 0
        assert isinstance(rec["impact"], str) and len(rec["impact"]) > 0
        assert isinstance(rec["action"], str) and len(rec["action"]) > 0


# ============================================================
# 5. ROUTE INTEGRATION TESTS
# ============================================================

def test_intelligence_route_unauthorized():
    with app.test_client() as client:
        response = client.get("/intelligence")
        assert response.status_code == 302
        assert "/login" in response.headers["Location"]


def test_intelligence_route_authorized():
    with app.test_client() as client:
        with client.session_transaction() as sess:
            sess["user_id"] = 1
            sess["username"] = "Tester"
        response = client.get("/intelligence")
        assert response.status_code == 302
        assert "#intelligence" in response.headers["Location"]


def test_index_renders_intelligence_empty_state():
    with app.test_client() as client:
        with client.session_transaction() as sess:
            sess["user_id"] = 1
            sess["username"] = "Tester"
        response = client.get("/")
        assert response.status_code == 200
        html = response.get_data(as_text=True)
        assert 'id="view-intelligence"' in html
        assert "Upload and analyze a project to view Intelligence &amp; Risk Analysis" in html
        assert 'href="#intelligence"' in html


def test_index_renders_intelligence_with_project(monkeypatch, tmp_path):
    import json
    import os

    # Create dummy project analysis file
    dummy_project = {
        "project_id": "test_proj_123",
        "project_directory": str(tmp_path),
        "project_name": "DemoApp",
        "file_count": 2,
        "total_lines": 500,
        "files": [
            {
                "file_path": "main.py",
                "name": "main.py",
                "language": "Python",
                "lines": 350,
                "analysis_status": "ANALYZED",
                "metrics": {
                    "lines_of_code": 300,
                    "cyclomatic_complexity": 18.0,
                    "maintainability_index": 45.0,
                    "num_functions": 12,
                    "num_classes": 2,
                    "num_imports": 5,
                    "comment_density": 8.0,
                    "avg_function_length": 25.0,
                    "max_nesting_depth": 4,
                    "todo_count": 3,
                    "fixme_count": 1,
                    "security_vulnerabilities": 1,
                    "code_churn": 2
                },
                "technical_debt": {
                    "score": 75.0,
                    "level": "High Technical Debt",
                    "reasons": ["High complexity"]
                }
            },
            {
                "file_path": "helpers.py",
                "name": "helpers.py",
                "language": "Python",
                "lines": 150,
                "analysis_status": "ANALYZED",
                "metrics": {
                    "lines_of_code": 120,
                    "cyclomatic_complexity": 3.0,
                    "maintainability_index": 80.0,
                    "num_functions": 6,
                    "num_classes": 0,
                    "num_imports": 2,
                    "comment_density": 20.0,
                    "avg_function_length": 10.0,
                    "max_nesting_depth": 1,
                    "todo_count": 0,
                    "fixme_count": 0,
                    "security_vulnerabilities": 0,
                    "code_churn": 0
                },
                "technical_debt": {
                    "score": 15.0,
                    "level": "Low Technical Debt",
                    "reasons": []
                }
            }
        ]
    }

    # Save to uploads dir
    from app import UPLOADS_DIRECTORY
    test_analysis_file = "analysis_test_proj_123.json"
    analysis_path = os.path.join(UPLOADS_DIRECTORY, test_analysis_file)
    with open(analysis_path, "w", encoding="utf-8") as f:
        json.dump(dummy_project, f)

    try:
        with app.test_client() as client:
            with client.session_transaction() as sess:
                sess["user_id"] = 1
                sess["username"] = "Tester"
                sess["project_analysis_file"] = test_analysis_file

            response = client.get("/")
            assert response.status_code == 200
            html = response.get_data(as_text=True)

            # Check for intelligence components
            assert "Technical Debt Hotspots &amp; Priority Score" in html
            assert "main.py" in html
            assert "helpers.py" in html
            assert "Quality Gate" in html
            assert "Predictive Project Risk Assessment" in html
            assert "Intelligent Recommendations" in html
    finally:
        if os.path.exists(analysis_path):
            os.remove(analysis_path)
