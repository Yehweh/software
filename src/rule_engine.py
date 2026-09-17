"""
Rule-based technical debt detection engine.
"""


def _get_value(row, key, default=0):
    try:
        value = row.get(key, default)

        if value is None:
            return default

        if isinstance(value, bool):
            return default

        if isinstance(value, str):
            value = value.strip()

            if not value:
                return default

        return float(value)

    except (TypeError, ValueError):
        return default


def detect_technical_debt(row):
    """
    Detect technical debt using measurable software quality metrics.
    """

    if not isinstance(row, dict):
        row = {}

    score = 0
    reasons = []

    complexity = _get_value(
        row,
        "cyclomatic_complexity"
    )

    duplication = _get_value(
        row,
        "duplication_percentage"
    )

    coverage = _get_value(
        row,
        "test_coverage"
    )

    cbo = _get_value(
        row,
        "coupling_between_objects"
    )

    lcom = _get_value(
        row,
        "lack_of_cohesion"
    )

    churn = _get_value(
        row,
        "code_churn"
    )

    past_defects = _get_value(
        row,
        "past_defects"
    )

    security = _get_value(
        row,
        "security_vulnerabilities"
    )

    if 0 < duplication <= 1:
        duplication *= 100

    if 0 < coverage <= 1:
        coverage *= 100

    # Cyclomatic Complexity
    if complexity >= 30:
        score += 15
        reasons.append(
            "High Cyclomatic Complexity"
        )

    elif complexity > 20:
        score += 10
        reasons.append(
            "High Cyclomatic Complexity"
        )

    elif complexity > 10:
        score += 5
        reasons.append(
            "Moderate Cyclomatic Complexity"
        )

    # Duplication
    if duplication > 25:
        score += 15
        reasons.append(
            "High Code Duplication"
        )

    elif duplication > 10:
        score += 8
        reasons.append(
            "Moderate Code Duplication"
        )

    # Test Coverage
    coverage_raw = row.get(
        "test_coverage"
    )

    coverage_valid = True

    if coverage_raw is None:
        coverage_valid = False

    elif isinstance(
        coverage_raw,
        str
    ):

        try:
            float(coverage_raw)

        except (
            TypeError,
            ValueError
        ):
            coverage_valid = False

    if coverage_valid:

        if coverage < 60:
            score += 15
            reasons.append(
                "Low Test Coverage"
            )

        elif coverage < 75:
            score += 8
            reasons.append(
                "Moderate Test Coverage"
            )

    # CBO
    if cbo > 25:
        score += 15
        reasons.append(
            "High Coupling Between Objects (CBO)"
        )

    elif cbo > 10:
        score += 8
        reasons.append(
            "High Coupling Between Objects (CBO)"
        )

    # LCOM
    if lcom > 0.70:
        score += 15
        reasons.append(
            "High Lack of Cohesion (LCOM)"
        )

    elif lcom > 0.40:
        score += 8
        reasons.append(
            "High Lack of Cohesion (LCOM)"
        )

    # Code Churn
    if churn > 600:
        score += 10
        reasons.append(
            "High Code Churn"
        )

    elif churn >= 300:
        score += 5
        reasons.append(
            "High Code Churn"
        )

    # Past Defects
    if past_defects > 25:
        score += 15
        reasons.append(
            "High Past Defects"
        )

    elif past_defects > 10:
        score += 8
        reasons.append(
            "High Past Defects"
        )

    # Security Vulnerabilities
    if security >= 3:
        score += 20
        reasons.append(
            "Security Vulnerabilities Detected"
        )

    elif security > 0:
        score += 20
        reasons.append(
            "Security Vulnerabilities Detected"
        )

    score = min(
        int(score),
        100
    )

    if score >= 61:
        debt_level = (
            "High Technical Debt"
        )

    elif score >= 31:
        debt_level = (
            "Medium Technical Debt"
        )

    else:
        debt_level = (
            "Low Technical Debt"
        )

    if not reasons:
        reasons.append(
            "Software metrics are within acceptable limits."
        )

    return {
        "Debt Score": score,
        "Debt Level": debt_level,
        "Reasons": reasons
    }