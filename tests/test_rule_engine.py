import pytest

from src.rule_engine import detect_technical_debt
from src.code_metrics import (
    calculate_python_metrics,
    detect_security_vulnerabilities,
    count_past_defects,
    estimate_code_churn
)
from src.technical_debt_engine import calculate_technical_debt


# ============================================================
# 1. RULE ENGINE TESTS
# ============================================================

def test_clean_metrics_low_debt():
    """Acceptable metrics should produce zero debt."""

    row = {
        "cyclomatic_complexity": 10,
        "duplication_percentage": 5,
        "test_coverage": 90,
        "coupling_between_objects": 5,
        "lack_of_cohesion": 0.2,
        "code_churn": 100,
        "past_defects": 2,
        "security_vulnerabilities": 0,
    }

    result = detect_technical_debt(row)

    assert result["Debt Score"] == 0

    assert result["Debt Level"] == (
        "Low Technical Debt"
    )

    assert (
        "Software metrics are within acceptable limits."
        in result["Reasons"]
    )


def test_high_cyclomatic_complexity():
    """High complexity should increase technical debt."""

    row = {
        "cyclomatic_complexity": 35
    }

    result = detect_technical_debt(row)

    assert result["Debt Score"] == 15

    assert (
        "High Cyclomatic Complexity"
        in result["Reasons"]
    )


def test_moderate_cyclomatic_complexity():
    """Moderate complexity should be detected."""

    row = {
        "cyclomatic_complexity": 15
    }

    result = detect_technical_debt(row)

    assert result["Debt Score"] == 5

    assert (
        "Moderate Cyclomatic Complexity"
        in result["Reasons"]
    )


def test_high_duplication():
    """High duplication should increase debt."""

    row = {
        "duplication_percentage": 35
    }

    result = detect_technical_debt(row)

    assert result["Debt Score"] == 15

    assert (
        "High Code Duplication"
        in result["Reasons"]
    )


def test_fractional_duplication():
    """Duplication represented as a fraction should be supported."""

    row = {
        "duplication_percentage": 0.35
    }

    result = detect_technical_debt(row)

    assert result["Debt Score"] == 15


def test_low_test_coverage():
    """Low test coverage should increase debt."""

    row = {
        "test_coverage": 30
    }

    result = detect_technical_debt(row)

    assert result["Debt Score"] == 15

    assert (
        "Low Test Coverage"
        in result["Reasons"]
    )


def test_fractional_test_coverage():
    """Coverage represented as a fraction should be supported."""

    row = {
        "test_coverage": 0.30
    }

    result = detect_technical_debt(row)

    assert result["Debt Score"] == 15


def test_high_coupling():
    """High CBO should increase technical debt."""

    row = {
        "coupling_between_objects": 35
    }

    result = detect_technical_debt(row)

    assert result["Debt Score"] == 15

    assert (
        "High Coupling Between Objects (CBO)"
        in result["Reasons"]
    )


def test_high_lcom():
    """High LCOM should increase technical debt."""

    row = {
        "lack_of_cohesion": 0.85
    }

    result = detect_technical_debt(row)

    assert result["Debt Score"] == 15

    assert (
        "High Lack of Cohesion (LCOM)"
        in result["Reasons"]
    )


def test_high_code_churn():
    """High code churn should increase technical debt."""

    row = {
        "code_churn": 750
    }

    result = detect_technical_debt(row)

    assert result["Debt Score"] == 10

    assert (
        "High Code Churn"
        in result["Reasons"]
    )


def test_high_past_defects():
    """High defect history should increase technical debt."""

    row = {
        "past_defects": 38
    }

    result = detect_technical_debt(row)

    assert result["Debt Score"] == 15

    assert (
        "High Past Defects"
        in result["Reasons"]
    )


def test_security_vulnerabilities():
    """Security vulnerabilities should increase technical debt."""

    row = {
        "security_vulnerabilities": 3
    }

    result = detect_technical_debt(row)

    assert result["Debt Score"] == 20

    assert (
        "Security Vulnerabilities Detected"
        in result["Reasons"]
    )


def test_multiple_metrics_high_debt():
    """Multiple quality issues should produce high debt."""

    row = {
        "cyclomatic_complexity": 45,
        "duplication_percentage": 35,
        "test_coverage": 30,
        "coupling_between_objects": 40,
        "lack_of_cohesion": 0.90,
        "code_churn": 800,
        "past_defects": 30,
        "security_vulnerabilities": 5,
    }

    result = detect_technical_debt(row)

    assert result["Debt Score"] == 100

    assert result["Debt Level"] == (
        "High Technical Debt"
    )

    assert len(result["Reasons"]) == 8


def test_medium_debt_classification():
    """Scores between 31 and 60 should be medium debt."""

    row = {
        "cyclomatic_complexity": 35,
        "security_vulnerabilities": 1,
    }

    result = detect_technical_debt(row)

    assert result["Debt Score"] == 35

    assert result["Debt Level"] == (
        "Medium Technical Debt"
    )


def test_missing_fields():
    """Missing fields should not crash the engine."""

    result = detect_technical_debt({})

    assert result["Debt Score"] == 0

    assert result["Debt Level"] == (
        "Low Technical Debt"
    )


def test_invalid_fields():
    """Invalid metric values should be handled safely."""

    row = {
        "cyclomatic_complexity": "invalid",
        "duplication_percentage": None,
        "test_coverage": "unknown",
        "security_vulnerabilities": "abc"
    }

    result = detect_technical_debt(row)

    assert result["Debt Score"] == 0

    assert result["Debt Level"] == (
        "Low Technical Debt"
    )


# ============================================================
# 2. PYTHON SOURCE ANALYSIS TESTS
# ============================================================

def test_ast_cbo_detection():
    """CBO should detect external dependencies."""

    code = """
import os
import json
from datetime import datetime

class ReportGenerator(BaseReport):

    def run(self):
        client = HttpClient()
        data = json.loads("{}")
        return client.send(data)
"""

    metrics = calculate_python_metrics(
        code
    )

    assert (
        metrics["coupling_between_objects"]
        >= 3
    )

    assert metrics["num_classes"] == 1


def test_ast_lcom_detection():
    """LCOM should distinguish cohesive and non-cohesive classes."""

    low_cohesion_code = """
class MultiPurposeClass:

    def method_a(self):
        self.attr_a = 1
        return self.attr_a

    def method_b(self):
        self.attr_b = 2
        return self.attr_b
"""

    metrics_low = calculate_python_metrics(
        low_cohesion_code
    )

    assert (
        metrics_low["lack_of_cohesion"]
        == 1.0
    )

    high_cohesion_code = """
class CohesiveClass:

    def method_a(self):
        return self.shared_var + 1

    def method_b(self):
        return self.shared_var * 2
"""

    metrics_high = calculate_python_metrics(
        high_cohesion_code
    )

    assert (
        metrics_high["lack_of_cohesion"]
        == 0.0
    )


def test_security_vulnerability_detection():
    """Security-sensitive operations should be detected."""

    vuln_code = """
import os
import subprocess

def insecure_runner(user_input):

    eval(user_input)

    os.system(
        "rm -rf " + user_input
    )

    subprocess.run(
        "ls " + user_input,
        shell=True
    )

    api_key = "secret_token_1234567890"
"""

    metrics = calculate_python_metrics(
        vuln_code
    )

    assert (
        metrics["security_vulnerabilities"]
        >= 3
    )

    assert any(
        "eval" in issue
        for issue in metrics["security_details"]
    )

    assert any(
        "shell=True" in issue
        for issue in metrics["security_details"]
    )


def test_past_defects_and_churn():
    """Defect markers and churn should be detected."""

    code = """
# BUG-101: fixed edge case
# FIXME: investigate memory leak
# DEFECT-404: patched race condition
# revision 2.1: refactor database handler

def process():
    pass
"""

    metrics = calculate_python_metrics(
        code
    )

    assert (
        metrics["past_defects"]
        >= 2
    )

    assert (
        metrics["code_churn"]
        >= 2
    )


# ============================================================
# 3. TECHNICAL DEBT ENGINE TESTS
# ============================================================

def test_technical_debt_engine_multiple_metrics():
    """
    Technical debt engine should incorporate
    multiple source-code quality metrics.
    """

    metrics = {

        "cyclomatic_complexity": 25,

        "max_function_length": 60,

        "max_nesting_depth": 6,

        "lines_of_code": 100,

        "comment_density": 20.0,

        "todo_count": 5,

        "fixme_count": 3,

        "coupling_between_objects": 25,

        "lack_of_cohesion": 0.85,

        "security_vulnerabilities": 2,

        "past_defects": 6,

        "code_churn": 600,

        "static_analysis_warnings": 10,

        "performance_issues": 3,
    }

    result = calculate_technical_debt(
        metrics
    )

    assert result["score"] >= 61

    assert result["level"] == (
        "High Technical Debt"
    )

    assert (
        "High Coupling Between Objects (CBO)"
        in result["reasons"]
    )

    assert (
        "High Lack of Cohesion (LCOM)"
        in result["reasons"]
    )

    assert (
        "Security Vulnerabilities Detected"
        in result["reasons"]
    )


def test_technical_debt_score_never_exceeds_100():
    """Technical debt score must always remain between 0 and 100."""

    metrics = {

        "cyclomatic_complexity": 100,

        "max_function_length": 1000,

        "max_nesting_depth": 100,

        "lines_of_code": 5000,

        "comment_density": 0,

        "todo_count": 100,

        "fixme_count": 100,

        "coupling_between_objects": 100,

        "lack_of_cohesion": 1.0,

        "security_vulnerabilities": 100,

        "past_defects": 100,

        "code_churn": 10000,

        "static_analysis_warnings": 100,

        "performance_issues": 100,
    }

    result = calculate_technical_debt(
        metrics
    )

    assert 0 <= result["score"] <= 100

    assert result["level"] == (
        "High Technical Debt"
    )


# ============================================================
# 4. DIRECT METRIC FUNCTION TESTS
# ============================================================

def test_calculate_cbo_function():

    code = """
import os
import json
import sys

class Example:

    def run(self):
        return json.dumps(os.getcwd())
"""

    result = calculate_python_metrics(
        code
    )

    assert (
        "coupling_between_objects"
        in result
    )


def test_calculate_lcom_function():

    code = """
class Example:

    def first(self):
        self.a = 1

    def second(self):
        self.b = 2
"""

    result = calculate_python_metrics(
        code
    )

    assert (
        "lack_of_cohesion"
        in result
    )


def test_security_function_exists():

    code = """
eval(user_input)
"""

    result = detect_security_vulnerabilities(
        code
    )

    assert result is not None


def test_past_defect_function():

    code = """
# BUG-101
# DEFECT-202
"""

    result = count_past_defects(
        code
    )

    assert result >= 2


def test_churn_function():

    code = """
# BUG
# FIXME
# TODO
def process():
    pass
"""

    result = estimate_code_churn(
        code
    )

    assert result >= 0


# ============================================================
# 5. RETURN STRUCTURE TESTS
# ============================================================

def test_technical_debt_return_structure():

    result = calculate_technical_debt({})

    assert "score" in result

    assert "level" in result

    assert "reasons" in result

    assert isinstance(
        result["score"],
        (int, float)
    )

    assert isinstance(
        result["level"],
        str
    )

    assert isinstance(
        result["reasons"],
        list
    )


def test_rule_engine_return_structure():

    result = detect_technical_debt({})

    assert "Debt Score" in result

    assert "Debt Level" in result

    assert "Reasons" in result

    assert isinstance(
        result["Reasons"],
        list
    )


def test_detect_technical_debt_pandas_series():
    """Verify that detect_technical_debt properly processes pandas Series objects."""
    import pandas as pd

    series = pd.Series({
        "cyclomatic_complexity": 35,
        "duplication_percentage": 30,
        "test_coverage": 40,
        "coupling_between_objects": 15,
        "lack_of_cohesion": 0.8,
        "code_churn": 400,
        "past_defects": 15,
        "security_vulnerabilities": 2
    })

    result = detect_technical_debt(series)

    assert result["Debt Score"] > 0
    assert result["Debt Level"] == "High Technical Debt"
    assert "High Cyclomatic Complexity" in result["Reasons"]
    assert "High Code Duplication" in result["Reasons"]
    assert "Low Test Coverage" in result["Reasons"]


def test_detect_technical_debt_non_dict_inputs():
    """Verify that detect_technical_debt safely handles non-dict/invalid inputs."""
    for bad_input in [None, "string", 42, [1, 2, 3], True]:
        result = detect_technical_debt(bad_input)
        assert result["Debt Score"] == 0
        assert result["Debt Level"] == "Low Technical Debt"
        assert "Software metrics are within acceptable limits." in result["Reasons"]


def test_detect_technical_debt_nan_handling():
    """Verify that detect_technical_debt safely handles NaN values."""
    import math

    row = {
        "cyclomatic_complexity": float("nan"),
        "test_coverage": float("nan"),
        "duplication_percentage": float("nan")
    }
    result = detect_technical_debt(row)
    assert result["Debt Score"] == 0
    assert result["Debt Level"] == "Low Technical Debt"