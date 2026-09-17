def _safe_number(value, default=0):
    """
    Safely convert a metric value to a number.

    Handles:
    - None
    - empty values
    - invalid strings
    - normal integers/floats
    """

    if value is None:
        return default

    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def calculate_technical_debt(metrics):
    """
    Calculate technical debt using measurable source-code
    quality and maintainability metrics.

    Score:
        0-30   -> Low Technical Debt
        31-60  -> Medium Technical Debt
        61-100 -> High Technical Debt
    """

    metrics = metrics or {}

    score = 0
    reasons = []

    # =========================================================
    # 1. CYCLOMATIC COMPLEXITY
    # =========================================================

    complexity = _safe_number(
        metrics.get("cyclomatic_complexity")
    )

    if complexity > 20:
        score += 20
        reasons.append("High Cyclomatic Complexity")

    elif complexity > 10:
        score += 10
        reasons.append("Moderate Cyclomatic Complexity")

    # =========================================================
    # 2. FUNCTION LENGTH
    # =========================================================

    max_function_length = _safe_number(
        metrics.get("max_function_length")
    )

    if max_function_length > 50:
        score += 15
        reasons.append("Very Long Function")

    elif max_function_length > 30:
        score += 10
        reasons.append("Long Function")

    # =========================================================
    # 3. NESTING DEPTH
    # =========================================================

    nesting_depth = _safe_number(
        metrics.get("max_nesting_depth")
    )

    if nesting_depth > 5:
        score += 15
        reasons.append("Deeply Nested Code")

    elif nesting_depth > 3:
        score += 10
        reasons.append("Moderate Nesting Depth")

    # =========================================================
    # 4. COMMENT DENSITY
    # =========================================================

    lines_of_code = _safe_number(
        metrics.get("lines_of_code")
    )

    comment_density = _safe_number(
        metrics.get("comment_density")
    )

    if (
        lines_of_code >= 20
        and comment_density < 5
    ):
        score += 10
        reasons.append("Low Comment Density")

    # =========================================================
    # 5. TODO ITEMS
    # =========================================================

    todo_count = _safe_number(
        metrics.get("todo_count")
    )

    if todo_count >= 5:
        score += 10
        reasons.append("Multiple TODO Items")

    elif todo_count > 0:
        score += 5
        reasons.append("Unresolved TODO Items")

    # =========================================================
    # 6. FIXME ITEMS
    # =========================================================

    fixme_count = _safe_number(
        metrics.get("fixme_count")
    )

    if fixme_count >= 3:
        score += 10
        reasons.append("Multiple FIXME Items")

    elif fixme_count > 0:
        score += 5
        reasons.append("Unresolved FIXME Items")

    # =========================================================
    # 7. COUPLING BETWEEN OBJECTS
    # =========================================================

    cbo = _safe_number(
        metrics.get("coupling_between_objects")
    )

    if cbo > 20:
        score += 15
        reasons.append(
            "High Coupling Between Objects (CBO)"
        )

    elif cbo > 10:
        score += 8
        reasons.append(
            "Moderate Coupling Between Objects (CBO)"
        )

    # =========================================================
    # 8. LACK OF COHESION
    # =========================================================

    lcom = _safe_number(
        metrics.get("lack_of_cohesion")
    )

    if lcom > 0.70:
        score += 15
        reasons.append(
            "High Lack of Cohesion (LCOM)"
        )

    elif lcom > 0.40:
        score += 8
        reasons.append(
            "Moderate Lack of Cohesion (LCOM)"
        )

    # =========================================================
    # 9. SECURITY VULNERABILITIES
    # =========================================================

    security_vulnerabilities = _safe_number(
        metrics.get("security_vulnerabilities")
    )

    if security_vulnerabilities >= 3:
        score += 25

        # Keep the standard reason wording expected by
        # existing rule-engine tests.
        reasons.append(
            "Security Vulnerabilities Detected"
        )

    elif security_vulnerabilities > 0:
        score += 15

        reasons.append(
            "Security Vulnerabilities Detected"
        )

    # =========================================================
    # 10. PAST DEFECTS
    # =========================================================

    past_defects = _safe_number(
        metrics.get("past_defects")
    )

    if past_defects >= 5:
        score += 15
        reasons.append("High Past Defects")

    elif past_defects > 0:
        score += 5
        reasons.append(
            "Defect References Detected"
        )

    # =========================================================
    # 11. CODE CHURN
    # =========================================================

    code_churn = _safe_number(
        metrics.get("code_churn")
    )

    if code_churn >= 100:
        score += 10
        reasons.append("High Code Churn")

    elif code_churn >= 50:
        score += 5
        reasons.append("Moderate Code Churn")

    # =========================================================
    # 12. LARGE SOURCE FILE
    # =========================================================

    if lines_of_code > 1000:
        score += 10
        reasons.append("Very Large Source File")

    elif lines_of_code > 500:
        score += 5
        reasons.append("Large Source File")

    # =========================================================
    # 13. STATIC ANALYSIS WARNINGS
    # =========================================================

    static_warnings = _safe_number(
        metrics.get("static_analysis_warnings")
    )

    if static_warnings >= 10:
        score += 15
        reasons.append(
            "High Static Analysis Warnings"
        )

    elif static_warnings > 0:
        score += 5
        reasons.append(
            "Static Analysis Warnings Detected"
        )

    # =========================================================
    # 14. PERFORMANCE ISSUES
    # =========================================================

    performance_issues = _safe_number(
        metrics.get("performance_issues")
    )

    if performance_issues >= 3:
        score += 15
        reasons.append(
            "Multiple Performance Issues"
        )

    elif performance_issues > 0:
        score += 8
        reasons.append(
            "Performance Issues Detected"
        )

    # =========================================================
    # LIMIT SCORE
    # =========================================================

    score = min(score, 100)

    # Return integer when possible so the existing UI/tests
    # continue to receive the expected format.
    if score.is_integer():
        score = int(score)

    # =========================================================
    # RISK CLASSIFICATION
    # =========================================================

    if score >= 61:
        level = "High Technical Debt"

    elif score >= 31:
        level = "Medium Technical Debt"

    else:
        level = "Low Technical Debt"

    # =========================================================
    # NO ISSUES DETECTED
    # =========================================================

    if not reasons:
        reasons.append(
            "Software quality metrics are within acceptable limits."
        )

    return {
        "score": score,
        "level": level,
        "reasons": reasons
    }