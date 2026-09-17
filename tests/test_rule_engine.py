import pytest
import pandas as pd
from src.rule_engine import detect_technical_debt
from src.code_metrics import (
    calculate_python_metrics,
    calculate_cbo,
    calculate_lcom,
    detect_security_vulnerabilities,
    count_past_defects,
    estimate_code_churn
)
from src.technical_debt_engine import calculate_technical_debt


# =====================================================================
# 1. RULE ENGINE TESTS (EXISTING & 5 NEW METRICS)
# =====================================================================

def test_clean_metrics_low_debt():
    """Test that acceptable metrics produce 0 debt score and low risk."""
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
    assert result["Debt Level"] == "Low Technical Debt"
    assert "Software metrics are within acceptable limits." in result["Reasons"]


def test_coupling_between_objects_metric():
    """Test that CBO > 25 triggers CBO penalty and reason."""
    row = {
        "cyclomatic_complexity": 10,
        "duplication_percentage": 5,
        "test_coverage": 90,
        "coupling_between_objects": 35,
        "lack_of_cohesion": 0.2,
        "code_churn": 100,
        "past_defects": 2,
        "security_vulnerabilities": 0,
    }
    result = detect_technical_debt(row)
    assert result["Debt Score"] == 15
    assert "High Coupling Between Objects (CBO)" in result["Reasons"]


def test_lack_of_cohesion_metric():
    """Test that LCOM > 0.70 triggers LCOM penalty and reason."""
    row = {
        "cyclomatic_complexity": 10,
        "duplication_percentage": 5,
        "test_coverage": 90,
        "coupling_between_objects": 5,
        "lack_of_cohesion": 0.85,
        "code_churn": 100,
        "past_defects": 2,
        "security_vulnerabilities": 0,
    }
    result = detect_technical_debt(row)
    assert result["Debt Score"] == 15
    assert "High Lack of Cohesion (LCOM)" in result["Reasons"]


def test_code_churn_metric():
    """Test that code churn > 600 triggers high churn penalty."""
    row = {
        "cyclomatic_complexity": 10,
        "duplication_percentage": 5,
        "test_coverage": 90,
        "coupling_between_objects": 5,
        "lack_of_cohesion": 0.2,
        "code_churn": 750,
        "past_defects": 2,
        "security_vulnerabilities": 0,
    }
    result = detect_technical_debt(row)
    assert result["Debt Score"] == 10
    assert "High Code Churn" in result["Reasons"]


def test_past_defects_metric():
    """Test that past defects > 25 triggers defect history penalty."""
    row = {
        "cyclomatic_complexity": 10,
        "duplication_percentage": 5,
        "test_coverage": 90,
        "coupling_between_objects": 5,
        "lack_of_cohesion": 0.2,
        "code_churn": 100,
        "past_defects": 38,
        "security_vulnerabilities": 0,
    }
    result = detect_technical_debt(row)
    assert result["Debt Score"] == 15
    assert "High Past Defects" in result["Reasons"]


def test_security_vulnerabilities_metric():
    """Test that security vulnerabilities > 0 triggers high security penalty."""
    row = {
        "cyclomatic_complexity": 10,
        "duplication_percentage": 5,
        "test_coverage": 90,
        "coupling_between_objects": 5,
        "lack_of_cohesion": 0.2,
        "code_churn": 100,
        "past_defects": 2,
        "security_vulnerabilities": 3,
    }
    result = detect_technical_debt(row)
    assert result["Debt Score"] == 20
    assert "Security Vulnerabilities Detected" in result["Reasons"]


def test_multiple_metrics_high_debt_and_score_cap():
    """Test that multiple triggered metrics accumulate and cap at 100."""
    row = {
        "cyclomatic_complexity": 45,       # +15
        "duplication_percentage": 35,      # +15
        "test_coverage": 30,               # +15
        "coupling_between_objects": 40,    # +15
        "lack_of_cohesion": 0.90,          # +15
        "code_churn": 800,                 # +10
        "past_defects": 30,                # +15
        "security_vulnerabilities": 5,     # +20 (sum = 120 -> capped at 100)
    }
    result = detect_technical_debt(row)
    assert result["Debt Score"] == 100
    assert result["Debt Level"] == "High Technical Debt"
    assert len(result["Reasons"]) == 8


def test_medium_debt_classification():
    """Test threshold classification for Medium Debt (31 - 60)."""
    row = {
        "cyclomatic_complexity": 35,       # +15
        "security_vulnerabilities": 1,     # +20 (sum = 35 -> Medium)
    }
    result = detect_technical_debt(row)
    assert result["Debt Score"] == 35
    assert result["Debt Level"] == "Medium Technical Debt"


def test_missing_or_corrupt_fields_graceful_handling():
    """Test that missing keys in row do not crash the engine."""
    result = detect_technical_debt({})
    assert result["Debt Score"] == 0
    assert result["Debt Level"] == "Low Technical Debt"


# =====================================================================
# 2. STATIC SOURCE CODE ANALYSIS TESTS (5 NEW METRICS)
# =====================================================================

def test_ast_cbo_detection():
    """Test AST detection of coupling between objects."""
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
    metrics = calculate_python_metrics(code)
    assert metrics["coupling_between_objects"] >= 3
    assert metrics["num_classes"] == 1


def test_ast_lcom_detection():
    """Test LCOM calculation on low cohesion (God class) vs cohesive class."""
    # Low cohesion: disjoint methods operating on distinct variables
    low_cohesion_code = """
class MultiPurposeClass:
    def method_a(self):
        self.attr_a = 1
        return self.attr_a

    def method_b(self):
        self.attr_b = 2
        return self.attr_b
"""
    metrics_low = calculate_python_metrics(low_cohesion_code)
    assert metrics_low["lack_of_cohesion"] == 1.0

    # High cohesion: methods share instance variables
    high_cohesion_code = """
class CohesiveClass:
    def method_a(self):
        return self.shared_var + 1

    def method_b(self):
        return self.shared_var * 2
"""
    metrics_high = calculate_python_metrics(high_cohesion_code)
    assert metrics_high["lack_of_cohesion"] == 0.0


def test_ast_security_vulnerability_detection():
    """Test detection of security vulnerabilities in source code."""
    vuln_code = """
import os
import subprocess

def insecure_runner(user_input):
    eval(user_input)
    os.system("rm -rf " + user_input)
    subprocess.run("ls " + user_input, shell=True)
    api_key = "secret_token_1234567890"
"""
    metrics = calculate_python_metrics(vuln_code)
    assert metrics["security_vulnerabilities"] >= 3
    assert any("eval" in issue for issue in metrics["security_details"])
    assert any("shell=True" in issue for issue in metrics["security_details"])


def test_past_defects_and_churn_detection():
    """Test past defect tag counting and churn estimation."""
    code = """
# BUG-101: fixed edge case for null inputs
# FIXME: investigate memory leak
# DEFECT-404: patched race condition
# revision 2.1: refactor database handler
def process():
    pass
"""
    metrics = calculate_python_metrics(code)
    assert metrics["past_defects"] >= 2
    assert metrics["code_churn"] >= 2


# =====================================================================
# 3. TECHNICAL DEBT ENGINE INTEGRATION
# =====================================================================

def test_technical_debt_engine_with_new_metrics():
    """Test that technical debt engine incorporates the 5 new metrics."""
    metrics = {
        "cyclomatic_complexity": 5,
        "max_function_length": 15,
        "max_nesting_depth": 2,
        "lines_of_code": 50,
        "comment_density": 20.0,
        "todo_count": 0,
        "fixme_count": 0,
        "coupling_between_objects": 25,     # High CBO -> +20
        "lack_of_cohesion": 0.85,           # High LCOM -> +20
        "security_vulnerabilities": 2,      # Security -> +20
        "past_defects": 6,                  # Past Defects -> +15
        "code_churn": 600,                  # Churn -> +10
    }
    result = calculate_technical_debt(metrics)
    assert result["score"] >= 61
    assert result["level"] == "High Technical Debt"
    assert "High Coupling Between Objects (CBO)" in result["reasons"]
    assert "High Lack of Cohesion (LCOM)" in result["reasons"]
    assert "Security Vulnerabilities Detected" in result["reasons"]
