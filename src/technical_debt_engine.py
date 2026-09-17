def calculate_technical_debt(metrics):
    """
    Calculate technical debt using measurable source-code
    quality and testing metrics.

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

    complexity = metrics.get("cyclomatic_complexity")
    if complexity is None:
        complexity = 0

    if complexity > 20:
        score += 20
        reasons.append("High Cyclomatic Complexity")
    elif complexity > 10:
        score += 10
        reasons.append("Moderate Cyclomatic Complexity")

    # =========================================================
    # 2. FUNCTION LENGTH
    # =========================================================

    max_function_length = metrics.get("max_function_length")
    if max_function_length is None:
        max_function_length = 0

    if max_function_length > 50:
        score += 15
        reasons.append("Very Long Function")
    elif max_function_length > 30:
        score += 10
        reasons.append("Long Function")

    # =========================================================
    # 3. NESTING DEPTH
    # =========================================================

    nesting_depth = metrics.get("max_nesting_depth")
    if nesting_depth is None:
        nesting_depth = 0

    if nesting_depth > 5:
        score += 15
        reasons.append("Deeply Nested Code")
    elif nesting_depth > 3:
        score += 10
        reasons.append("Moderate Nesting Depth")

    # =========================================================
    # 4. COMMENT DENSITY
    # =========================================================

    lines_of_code = metrics.get("lines_of_code")
    if lines_of_code is None:
        lines_of_code = 0

    comment_density = metrics.get("comment_density")
    if comment_density is None:
        comment_density = 0

    if lines_of_code >= 10:
        if comment_density < 5:
            score += 10
            reasons.append("Low Comment Density")

    # =========================================================
    # 5. TODO ITEMS
    # =========================================================

    todo_count = metrics.get("todo_count")
    if todo_count is None:
        todo_count = 0

    if todo_count >= 5:
        score += 10
        reasons.append("Multiple TODO Items")
    elif todo_count > 0:
        score += 5
        reasons.append("Unresolved TODO Items")

    # =========================================================
    # 6. FIXME ITEMS
    # =========================================================

    fixme_count = metrics.get("fixme_count")
    if fixme_count is None:
        fixme_count = 0

    if fixme_count >= 3:
        score += 10
        reasons.append("Multiple FIXME Items")
    elif fixme_count > 0:
        score += 5
        reasons.append("Unresolved FIXME Items")

    # =========================================================
    # 7. COUPLING BETWEEN OBJECTS (CBO)
    # =========================================================

    cbo = metrics.get("coupling_between_objects")
    if cbo is None:
        cbo = 0

    if cbo > 20:
        score += 20
        reasons.append("High Coupling Between Objects (CBO)")
    elif cbo > 10:
        score += 10
        reasons.append("Moderate Coupling Between Objects (CBO)")

    # =========================================================
    # 8. LACK OF COHESION (LCOM)
    # =========================================================

    lcom = metrics.get("lack_of_cohesion")
    if lcom is None:
        lcom = 0.0

    if lcom > 0.70:
        score += 20
        reasons.append("High Lack of Cohesion (LCOM)")
    elif lcom > 0.40:
        score += 10
        reasons.append("Moderate Lack of Cohesion (LCOM)")

    # =========================================================
    # 9. SECURITY VULNERABILITIES
    # =========================================================

    sec_vulns = metrics.get("security_vulnerabilities")
    if sec_vulns is None:
        sec_vulns = 0

    if sec_vulns >= 3:
        score += 25
        reasons.append("Critical Security Vulnerabilities Detected")
    elif sec_vulns > 0:
        score += 20
        reasons.append("Security Vulnerabilities Detected")

    # =========================================================
    # 10. PAST DEFECTS
    # =========================================================

    past_defects = metrics.get("past_defects")
    if past_defects is None:
        past_defects = 0

    if past_defects >= 5:
        score += 15
        reasons.append("High Past Defects")
    elif past_defects > 0:
        score += 5
        reasons.append("Unresolved Defect References")

    # =========================================================
    # 11. CODE CHURN
    # =========================================================

    churn = metrics.get("code_churn")
    if churn is None:
        churn = 0

    if churn > 500 or churn >= 10:
        score += 10
        reasons.append("High Code Churn")

    # =========================================================
    # LIMIT SCORE TO 100
    # =========================================================

    score = min(
        score,
        100
    )

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
    # NO ISSUES
    # =========================================================

    if not reasons:
        reasons.append(
            "Software quality metrics are within acceptable limits."
        )

    # =========================================================
    # RETURN RESULT
    # =========================================================

    return {
        "score": score,
        "level": level,
        "reasons": reasons
    }