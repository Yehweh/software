"""
Project Quality Gate Engine.

Enforces configurable quality and maintainability thresholds across 6 core categories:
1. Security
2. Maintainability
3. Duplication
4. Testing
5. Complexity
6. Technical Debt

Determines categorical PASS/FAIL statuses and an OVERALL project gate status.
"""

# ============================================================
# QUALITY GATE CONFIGURATION & THRESHOLDS
# ============================================================
QUALITY_THRESHOLDS = {
    "security": {
        "label": "Security",
        "icon": "🛡️",
        "max_vulnerabilities": 0,
        "description": "Zero security vulnerabilities allowed across all codebase files."
    },
    "maintainability": {
        "label": "Maintainability",
        "icon": "🏗️",
        "max_avg_cbo": 15.0,
        "max_nesting_depth": 5,
        "min_comment_density": 5.0,
        "description": "Codebase coupling, nesting depth, and documentation must remain within maintainable limits."
    },
    "duplication": {
        "label": "Duplication",
        "icon": "📋",
        "max_duplication_pct": 15.0,
        "description": "Duplicated code ratio must not exceed 15% to minimize copy-paste technical debt."
    },
    "testing": {
        "label": "Testing",
        "icon": "🧪",
        "min_coverage_pct": 50.0,
        "max_defects_without_tests": 5,
        "description": "Requires adequate test coverage and minimal unresolved defect density."
    },
    "complexity": {
        "label": "Complexity",
        "icon": "⚡",
        "max_avg_complexity": 15.0,
        "description": "Average cyclomatic complexity must stay below 15 points per module/file."
    },
    "technical_debt": {
        "label": "Technical Debt",
        "icon": "📉",
        "max_debt_score": 50.0,
        "description": "Average project technical debt score must remain within acceptable bounds (<= 50/100)."
    }
}


def _safe_number(value, default=0.0):
    if value is None or isinstance(value, bool):
        return default
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def evaluate_quality_gate(project_metrics, files=None):
    """
    Evaluates project-level metrics against the defined Quality Gate thresholds.

    Returns:
    {
        "overall_status": "PASSED" | "FAILED",
        "passed_count": int,
        "failed_count": int,
        "total_count": 6,
        "categories": [
            {
                "key": str,
                "label": str,
                "icon": str,
                "status": "PASSED" | "FAILED",
                "value_display": str,
                "threshold_display": str,
                "reason": str
            }, ...
        ]
    }
    """
    pm = project_metrics or {}
    categories = []

    # --------------------------------------------------------
    # 1. SECURITY GATE
    # --------------------------------------------------------
    sec_vulns = int(_safe_number(pm.get("total_security_vulnerabilities", 0)))
    sec_thresh = QUALITY_THRESHOLDS["security"]["max_vulnerabilities"]
    if sec_vulns <= sec_thresh:
        sec_status = "PASSED"
        sec_reason = "PASSED: Zero security vulnerability flags detected."
    else:
        sec_status = "FAILED"
        sec_reason = f"FAILED: {sec_vulns} security vulnerability flag{'s' if sec_vulns > 1 else ''} detected (threshold: {sec_thresh})."

    categories.append({
        "key": "security",
        "label": QUALITY_THRESHOLDS["security"]["label"],
        "icon": QUALITY_THRESHOLDS["security"]["icon"],
        "status": sec_status,
        "value_display": f"{sec_vulns} Vulnerabilities",
        "threshold_display": f"Max {sec_thresh}",
        "reason": sec_reason
    })

    # --------------------------------------------------------
    # 2. MAINTAINABILITY GATE
    # --------------------------------------------------------
    avg_cbo = _safe_number(pm.get("average_cbo", pm.get("coupling_between_objects", 0.0)))
    max_nesting = int(_safe_number(pm.get("max_nesting_depth", 0)))
    avg_comment = _safe_number(pm.get("average_comment_density", pm.get("comment_density", 0.0)))
    avg_mi = _safe_number(pm.get("average_maintainability_index", pm.get("maintainability_index", 75.0)))
    total_lines = _safe_number(pm.get("total_lines", pm.get("lines_of_code", 0)))

    maint_failures = []
    if avg_mi < 60.0:
        maint_failures.append(f"Maintainability Index is low ({avg_mi:.1f} < 60.0)")
    if avg_cbo > QUALITY_THRESHOLDS["maintainability"]["max_avg_cbo"]:
        maint_failures.append(f"Average coupling CBO is high ({avg_cbo:.1f} > {QUALITY_THRESHOLDS['maintainability']['max_avg_cbo']})")
    if max_nesting > QUALITY_THRESHOLDS["maintainability"]["max_nesting_depth"]:
        maint_failures.append(f"Max nesting depth exceeds threshold ({max_nesting} > {QUALITY_THRESHOLDS['maintainability']['max_nesting_depth']})")
    if total_lines >= 100 and avg_comment < QUALITY_THRESHOLDS["maintainability"]["min_comment_density"]:
        maint_failures.append(f"Comment density is low ({avg_comment:.1f}% < {QUALITY_THRESHOLDS['maintainability']['min_comment_density']}%)")

    if not maint_failures:
        maint_status = "PASSED"
        maint_reason = "PASSED: Coupling, maintainability index, and code documentation are within healthy limits."
    else:
        maint_status = "FAILED"
        maint_reason = f"FAILED: {'; '.join(maint_failures)}."

    categories.append({
        "key": "maintainability",
        "name": "Maintainability & Code Health",
        "label": QUALITY_THRESHOLDS["maintainability"]["label"],
        "category": QUALITY_THRESHOLDS["maintainability"]["label"],
        "icon": QUALITY_THRESHOLDS["maintainability"]["icon"],
        "status": maint_status,
        "value_display": f"MI: {avg_mi:.1f} | Nesting: {max_nesting}",
        "actual_display": f"MI: {avg_mi:.1f} | Nesting: {max_nesting}",
        "threshold_display": "MI >= 60, Nesting <= 5",
        "threshold_description": "MI >= 60, Nesting <= 5",
        "reason": maint_reason
    })

    # --------------------------------------------------------
    # 3. DUPLICATION GATE
    # --------------------------------------------------------
    duplication = _safe_number(pm.get("average_duplication", pm.get("code_duplication_ratio", 0.0)))
    dup_thresh = QUALITY_THRESHOLDS["duplication"]["max_duplication_pct"]
    if duplication <= dup_thresh:
        dup_status = "PASSED"
        dup_reason = f"PASSED: Code duplication ({duplication:.1f}%) is within acceptable threshold (<= {dup_thresh}%)."
    else:
        dup_status = "FAILED"
        dup_reason = f"FAILED: Code duplication exceeds acceptable threshold ({duplication:.1f}% > {dup_thresh}%)."

    categories.append({
        "key": "duplication",
        "name": "Code Duplication",
        "label": QUALITY_THRESHOLDS["duplication"]["label"],
        "category": QUALITY_THRESHOLDS["duplication"]["label"],
        "icon": QUALITY_THRESHOLDS["duplication"]["icon"],
        "status": dup_status,
        "value_display": f"{duplication:.1f}%",
        "actual_display": f"{duplication:.1f}%",
        "threshold_display": f"<= {dup_thresh}%",
        "threshold_description": f"<= {dup_thresh}%",
        "reason": dup_reason
    })

    # --------------------------------------------------------
    # 4. TESTING GATE
    # --------------------------------------------------------
    coverage = pm.get("test_coverage") or pm.get("average_test_coverage")
    past_defects = int(_safe_number(pm.get("total_past_defects", 0)))
    has_tests = pm.get("has_tests")
    cov_thresh = QUALITY_THRESHOLDS["testing"]["min_coverage_pct"]

    if coverage is not None:
        cov_val = _safe_number(coverage)
        if cov_val >= cov_thresh:
            test_status = "PASSED"
            test_reason = f"PASSED: Test coverage ({cov_val:.1f}%) satisfies requirement (>= {cov_thresh}%)."
        else:
            test_status = "FAILED"
            test_reason = f"FAILED: Test coverage is low ({cov_val:.1f}% < {cov_thresh}%)."
        cov_disp = f"{cov_val:.1f}% Coverage"
    elif has_tests is not None:
        if has_tests:
            test_status = "PASSED"
            test_reason = "PASSED: Automated tests verified in project."
            cov_disp = "Tests Detected"
        else:
            test_status = "FAILED"
            test_reason = "FAILED: No automated test cases detected in project."
            cov_disp = "No Tests"
    else:
        # If test coverage is not explicitly instrumented, check past defects
        if past_defects <= QUALITY_THRESHOLDS["testing"]["max_defects_without_tests"]:
            test_status = "PASSED"
            test_reason = f"PASSED: Low defect incidence ({past_defects} past defects reported)."
            cov_disp = f"{past_defects} Past Defects"
        else:
            test_status = "FAILED"
            test_reason = f"FAILED: Elevated past defect count ({past_defects}) without verified test suite."
            cov_disp = f"{past_defects} Defects (Unverified)"

    categories.append({
        "key": "testing",
        "name": "Testing & Reliability",
        "label": QUALITY_THRESHOLDS["testing"]["label"],
        "category": QUALITY_THRESHOLDS["testing"]["label"],
        "icon": QUALITY_THRESHOLDS["testing"]["icon"],
        "status": test_status,
        "value_display": cov_disp,
        "actual_display": cov_disp,
        "threshold_display": f">= {cov_thresh}% Cov / Verified Suite",
        "threshold_description": f">= {cov_thresh}% Cov / Verified Suite",
        "reason": test_reason
    })

    # --------------------------------------------------------
    # 5. COMPLEXITY GATE
    # --------------------------------------------------------
    complexity = _safe_number(pm.get("cyclomatic_complexity", pm.get("average_cyclomatic_complexity", 1.0)))
    comp_thresh = QUALITY_THRESHOLDS["complexity"]["max_avg_complexity"]
    if complexity <= comp_thresh:
        comp_status = "PASSED"
        comp_reason = f"PASSED: Average cyclomatic complexity ({complexity:.1f}) is within acceptable threshold (<= {comp_thresh})."
    else:
        comp_status = "FAILED"
        comp_reason = f"FAILED: Average cyclomatic complexity exceeds threshold ({complexity:.1f} > {comp_thresh})."

    categories.append({
        "key": "complexity",
        "name": "Cyclomatic Complexity",
        "label": QUALITY_THRESHOLDS["complexity"]["label"],
        "category": QUALITY_THRESHOLDS["complexity"]["label"],
        "icon": QUALITY_THRESHOLDS["complexity"]["icon"],
        "status": comp_status,
        "value_display": f"{complexity:.1f}",
        "actual_display": f"{complexity:.1f}",
        "threshold_display": f"<= {comp_thresh}",
        "threshold_description": f"<= {comp_thresh}",
        "reason": comp_reason
    })

    # --------------------------------------------------------
    # 6. TECHNICAL DEBT GATE
    # --------------------------------------------------------
    debt_score = _safe_number(pm.get("average_debt_score", pm.get("technical_debt_score", 0.0)))
    debt_thresh = QUALITY_THRESHOLDS["technical_debt"]["max_debt_score"]
    if debt_score <= debt_thresh:
        debt_status = "PASSED"
        debt_reason = f"PASSED: Average Technical Debt Score ({debt_score:.1f}/100) is within manageable range (<= {debt_thresh})."
    else:
        debt_status = "FAILED"
        debt_reason = f"FAILED: Average Technical Debt Score exceeds threshold ({debt_score:.1f} > {debt_thresh})."

    categories.append({
        "key": "technical_debt",
        "name": "Average Technical Debt Score",
        "label": QUALITY_THRESHOLDS["technical_debt"]["label"],
        "category": QUALITY_THRESHOLDS["technical_debt"]["label"],
        "icon": QUALITY_THRESHOLDS["technical_debt"]["icon"],
        "status": debt_status,
        "value_display": f"{debt_score:.1f} / 100",
        "actual_display": f"{debt_score:.1f} / 100",
        "threshold_display": f"<= {debt_thresh}",
        "threshold_description": f"<= {debt_thresh}",
        "reason": debt_reason
    })

    # --------------------------------------------------------
    # OVERALL QUALITY GATE STATUS
    # --------------------------------------------------------
    passed_count = sum(1 for c in categories if c["status"] in ("PASSED", "PASS"))
    failed_count = sum(1 for c in categories if c["status"] in ("FAILED", "FAIL"))
    overall_status = "PASSED" if failed_count == 0 else "FAILED"
    failed_reasons = [c["reason"] for c in categories if c["status"] in ("FAILED", "FAIL")]

    # Normalize status values
    for c in categories:
        c["category"] = c.get("label", "")
        c["name"] = c.get("name") or c.get("label", "")
        c["actual_display"] = c.get("value_display", "")
        c["threshold_description"] = c.get("threshold_display", "")
        c["status_long"] = "PASSED" if c["status"] in ("PASSED", "PASS") else "FAILED"
        c["status"] = "PASS" if c["status"] in ("PASSED", "PASS") else "FAIL"

    return {
        "overall_status": overall_status,
        "passed_count": passed_count,
        "failed_count": failed_count,
        "total_count": len(categories),
        "total_conditions": len(categories),
        "categories": categories,
        "conditions": categories,
        "failed_reasons": failed_reasons
    }
