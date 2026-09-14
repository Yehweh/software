def calculate_technical_debt(metrics):
    """
    Calculate technical debt using measurable source-code
    quality metrics.

    Score:
        0-30   -> Low Technical Debt
        31-60  -> Medium Technical Debt
        61-100 -> High Technical Debt
    """

    score = 0
    reasons = []

    # =========================================================
    # 1. CYCLOMATIC COMPLEXITY
    # =========================================================

    complexity = metrics.get(
        "cyclomatic_complexity",
        0
    )

    if complexity > 20:

        score += 25

        reasons.append(
            "High Cyclomatic Complexity"
        )

    elif complexity > 10:

        score += 15

        reasons.append(
            "Moderate Cyclomatic Complexity"
        )

    # =========================================================
    # 2. FUNCTION LENGTH
    # =========================================================

    max_function_length = metrics.get(
        "max_function_length",
        0
    )

    if max_function_length > 50:

        score += 20

        reasons.append(
            "Very Long Function"
        )

    elif max_function_length > 30:

        score += 10

        reasons.append(
            "Long Function"
        )

    # =========================================================
    # 3. NESTING DEPTH
    # =========================================================

    nesting_depth = metrics.get(
        "max_nesting_depth",
        0
    )

    if nesting_depth > 5:

        score += 20

        reasons.append(
            "Deeply Nested Code"
        )

    elif nesting_depth > 3:

        score += 10

        reasons.append(
            "Moderate Nesting Depth"
        )

    # =========================================================
    # 4. COMMENT DENSITY
    # =========================================================

    lines_of_code = metrics.get(
        "lines_of_code",
        0
    )

    comment_density = metrics.get(
        "comment_density",
        0
    )

    # Only evaluate comment density when there is
    # enough code to make the measurement meaningful.
    if lines_of_code >= 10:

        if comment_density < 5:

            score += 10

            reasons.append(
                "Low Comment Density"
            )

    # =========================================================
    # 5. TODO ITEMS
    # =========================================================

    todo_count = metrics.get(
        "todo_count",
        0
    )

    if todo_count >= 5:

        score += 10

        reasons.append(
            "Multiple TODO Items"
        )

    elif todo_count > 0:

        score += 5

        reasons.append(
            "Unresolved TODO Items"
        )

    # =========================================================
    # 6. FIXME ITEMS
    # =========================================================

    fixme_count = metrics.get(
        "fixme_count",
        0
    )

    if fixme_count >= 3:

        score += 10

        reasons.append(
            "Multiple FIXME Items"
        )

    elif fixme_count > 0:

        score += 5

        reasons.append(
            "Unresolved FIXME Items"
        )

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