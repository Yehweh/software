"""
Project Risk Prediction & Maintenance Risk Estimation Engine.

Calculates an estimated project maintenance risk score using a transparent,
weighted heuristic model combining code quality metrics.

DISCLAIMER:
This assessment is a heuristic risk estimate based on static code metrics,
not a guaranteed prediction of runtime defect occurrence or production failure.
"""


def _safe_number(value, default=0.0):
    if value is None or isinstance(value, bool):
        return default
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def calculate_project_risk(project_metrics, files=None):
    """
    Computes a project-level heuristic risk score (0-100) and risk level
    (LOW, MEDIUM, HIGH, CRITICAL) using a documented weighted scoring model.

    Weighted Model Composition:
    --------------------------
    1. Technical Debt Score:          25% weight
    2. Cyclomatic Complexity:         15% weight
    3. Security Vulnerabilities:      15% weight
    4. Architecture & Coupling (CBO): 10% weight
    5. Code Churn Frequency:          10% weight
    6. Code Duplication Ratio:        10% weight
    7. Past Defect Density:            8% weight
    8. Testing Coverage Deficit:       7% weight
    Total:                           100%

    Risk Tiers:
    - 0-30   : LOW
    - 31-60  : MEDIUM
    - 61-80  : HIGH
    - 81-100 : CRITICAL
    """
    pm = project_metrics or {}

    # Extract raw metrics with aliases
    debt_score = _safe_number(pm.get("average_debt_score", pm.get("debt_score", 0.0)))
    complexity = _safe_number(pm.get("cyclomatic_complexity", pm.get("average_cyclomatic_complexity", 1.0)))
    sec_vulns = _safe_number(pm.get("total_security_vulnerabilities", pm.get("security_vulnerabilities", 0)))
    cbo = _safe_number(pm.get("average_cbo", pm.get("coupling_between_objects", 0.0)))
    churn = _safe_number(pm.get("total_code_churn", pm.get("code_churn", 0)))
    duplication = _safe_number(pm.get("average_duplication", pm.get("code_duplication_ratio", pm.get("duplication_percentage", 0.0))))
    past_defects = _safe_number(pm.get("total_past_defects", pm.get("past_defects", 0)))
    has_tests = pm.get("has_tests")
    coverage = pm.get("test_coverage") or pm.get("average_test_coverage")

    # Aggregate from files if files is provided and metric is 0
    if files and isinstance(files, list):
        if sec_vulns == 0:
            sec_vulns = sum(
                _safe_number((f.get("metrics") or {}).get("security_vulnerabilities", 0))
                for f in files if isinstance(f, dict)
            )
        if past_defects == 0:
            past_defects = sum(
                _safe_number((f.get("metrics") or {}).get("past_defects", 0))
                for f in files if isinstance(f, dict)
            )
        if churn == 0:
            churn = sum(
                _safe_number((f.get("metrics") or {}).get("code_churn", 0))
                for f in files if isinstance(f, dict)
            )

    # 1. Normalize each factor to a 0-100 scale
    norm_debt = min(100.0, max(0.0, debt_score))
    norm_complexity = min(100.0, max(0.0, (complexity / 25.0) * 100.0))
    norm_security = min(100.0, sec_vulns * 40.0)
    norm_coupling = min(100.0, max(0.0, (cbo / 15.0) * 100.0))
    norm_churn = min(100.0, max(0.0, (churn / 25.0) * 100.0))
    norm_duplication = min(100.0, max(0.0, (duplication / 25.0) * 100.0))
    norm_defects = min(100.0, max(0.0, past_defects * 15.0))

    if coverage is not None:
        cov_val = _safe_number(coverage)
        norm_test_deficit = min(100.0, max(0.0, 100.0 - cov_val))
    elif has_tests is not None:
        norm_test_deficit = 15.0 if has_tests else 85.0
    else:
        # Moderate default penalty if no tests are tracked
        norm_test_deficit = 40.0

    # 2. Weighted Calculation
    factors = [
        {
            "key": "technical_debt",
            "name": "Technical Debt",
            "weight": 0.25,
            "score": round(norm_debt, 1),
            "weighted_impact": round(0.25 * norm_debt, 2),
            "raw_display": f"{debt_score:.1f}/100 Debt Score",
            "description": "Accumulated architectural and code-level debt index"
        },
        {
            "key": "cyclomatic_complexity",
            "name": "Code Complexity",
            "weight": 0.15,
            "score": round(norm_complexity, 1),
            "weighted_impact": round(0.15 * norm_complexity, 2),
            "raw_display": f"{complexity:.1f} Avg Complexity",
            "description": "Intricate branching paths and conditional control-flow"
        },
        {
            "key": "security_vulnerabilities",
            "name": "Security Exposure",
            "weight": 0.15,
            "score": round(norm_security, 1),
            "weighted_impact": round(0.15 * norm_security, 2),
            "raw_display": f"{int(sec_vulns)} Vulnerability Flags",
            "description": "Potential vulnerability exposures and risky API calls"
        },
        {
            "key": "coupling",
            "name": "Coupling & Cohesion",
            "weight": 0.10,
            "score": round(norm_coupling, 1),
            "weighted_impact": round(0.10 * norm_coupling, 2),
            "raw_display": f"{cbo:.1f} Avg CBO",
            "description": "Inter-module dependencies and ripple-effect change risk"
        },
        {
            "key": "code_churn",
            "name": "Code Churn",
            "weight": 0.10,
            "score": round(norm_churn, 1),
            "weighted_impact": round(0.10 * norm_churn, 2),
            "raw_display": f"{int(churn)} Churn Revisions",
            "description": "Volatility and high frequency of file revisions"
        },
        {
            "key": "duplication",
            "name": "Code Duplication",
            "weight": 0.10,
            "score": round(norm_duplication, 1),
            "weighted_impact": round(0.10 * norm_duplication, 2),
            "raw_display": f"{duplication:.1f}% Duplicated",
            "description": "Redundant code blocks increasing synchronization overhead"
        },
        {
            "key": "past_defects",
            "name": "Defect History",
            "weight": 0.08,
            "score": round(norm_defects, 1),
            "weighted_impact": round(0.08 * norm_defects, 2),
            "raw_display": f"{int(past_defects)} Past Defects",
            "description": "Historical fault incidence across modules"
        },
        {
            "key": "test_deficit",
            "name": "Test Deficit",
            "weight": 0.07,
            "score": round(norm_test_deficit, 1),
            "weighted_impact": round(0.07 * norm_test_deficit, 2),
            "raw_display": f"{100.0 - norm_test_deficit:.1f}% Coverage" if coverage is not None else "Uninstrumented",
            "description": "Uncovered code paths vulnerable to regressions"
        }
    ]

    total_risk = sum(f["weighted_impact"] for f in factors)
    risk_score = round(min(100.0, max(0.0, total_risk)), 1)

    # 3. Determine Risk Classification Level
    if risk_score >= 75.0:
        risk_level = "CRITICAL"
        risk_color = "#ef4444"
        maintenance_risk = "CRITICAL"
    elif risk_score >= 50.0:
        risk_level = "HIGH"
        risk_color = "#f97316"
        maintenance_risk = "HIGH"
    elif risk_score >= 30.0:
        risk_level = "MEDIUM"
        risk_color = "#eab308"
        maintenance_risk = "MEDIUM"
    else:
        risk_level = "LOW"
        risk_color = "#10b981"
        maintenance_risk = "LOW"

    # 4. Extract Top 3 Contributing Risk Drivers (sorted by weighted impact descending)
    sorted_factors = sorted(factors, key=lambda f: f["weighted_impact"], reverse=True)
    top_3_factors = sorted_factors[:3]
    top_drivers = [
        f"{f['name']}: {f['description']} (impact: {f['score']:.1f}/100)"
        for f in top_3_factors
    ]

    # 5. Build 4 Core Risk Dimensions
    def _level(s):
        return "CRITICAL" if s >= 75 else "HIGH" if s >= 50 else "MEDIUM" if s >= 30 else "LOW"

    dim_comp_score = round(min(100.0, (norm_complexity * 0.6 + norm_defects * 0.4)), 1)
    dim_maint_score = round(min(100.0, (norm_coupling * 0.5 + norm_churn * 0.3 + norm_duplication * 0.2)), 1)
    dim_debt_score = round(min(100.0, norm_debt), 1)
    dim_test_score = round(min(100.0, (norm_test_deficit * 0.7 + norm_security * 0.3)), 1)

    dimensions = {
        "complexity_defect": {
            "name": "Complexity & Defect Risk",
            "score": dim_comp_score,
            "level": _level(dim_comp_score),
            "description": f"Intricate branching paths (score: {complexity:.1f}) and historical defect incidence."
        },
        "maintainability": {
            "name": "Maintainability Risk",
            "score": dim_maint_score,
            "level": _level(dim_maint_score),
            "description": f"Inter-module coupling (CBO: {cbo:.1f}), code churn, and duplication overhead."
        },
        "technical_debt_growth": {
            "name": "Technical Debt Growth Risk",
            "score": dim_debt_score,
            "level": _level(dim_debt_score),
            "description": f"Accumulated architectural liabilities (Debt: {debt_score:.1f}/100) accelerating maintenance cost."
        },
        "testing_reliability": {
            "name": "Testing & Reliability Risk",
            "score": dim_test_score,
            "level": _level(dim_test_score),
            "description": "Uninstrumented execution paths and security vulnerability flags."
        }
    }

    dimension_list = [
        dimensions["complexity_defect"],
        dimensions["maintainability"],
        dimensions["technical_debt_growth"],
        dimensions["testing_reliability"]
    ]

    summary = (
        f"Project risk is estimated as {risk_level} ({risk_score}/100) based on weighted multi-factor analysis "
        f"of code complexity, technical debt, and maintainability indicators."
    )

    return {
        "risk_score": risk_score,
        "risk_level": risk_level,
        "risk_band": risk_level,
        "risk_badge_class": f"risk-{risk_level.lower()}",
        "risk_color": risk_color,
        "summary": summary,
        "maintenance_risk": maintenance_risk,
        "dimensions": dimensions,
        "dimension_list": dimension_list,
        "factors": factors,
        "top_factors": top_3_factors,
        "top_drivers": top_drivers,
        "disclaimer": "Risk estimation is a heuristic, predictive model based on static code metrics, architectural attributes, and technical debt indicators. It does not replace dynamic testing or human security audits."
    }
