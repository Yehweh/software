def detect_technical_debt(row):
    """
    Detect technical debt from software quality metrics.
    Evaluates both dataset benchmarks and project-level measurements:
    - Cyclomatic Complexity
    - Code Duplication
    - Test Coverage
    - Coupling Between Objects (CBO)
    - Lack of Cohesion (LCOM)
    - Code Churn
    - Past Defects
    - Security Vulnerabilities
    """

    score = 0
    reasons = []

    def get_val(key, default=0):
        try:
            val = row[key]
            return float(val) if val is not None else default
        except (KeyError, IndexError, TypeError, ValueError):
            return default

    complexity = get_val("cyclomatic_complexity", 0)
    duplication = get_val("duplication_percentage", 0)
    coverage = get_val("test_coverage", 100)
    cbo = get_val("coupling_between_objects", 0)
    lcom = get_val("lack_of_cohesion", 0)
    churn = get_val("code_churn", 0)
    past_defects = get_val("past_defects", 0)
    security_vulnerabilities = get_val("security_vulnerabilities", 0)

    # 1. Cyclomatic Complexity
    if complexity > 30:
        score += 15
        reasons.append("High Cyclomatic Complexity")

    # 2. Code Duplication (handles both 0-100% and 0.0-1.0 proportions)
    if duplication > 25 or (0 < duplication <= 1.0 and duplication > 0.25):
        score += 15
        reasons.append("High Code Duplication")

    # 3. Test Coverage (handles both 0-100% and 0.0-1.0 proportions)
    if (coverage < 60 and coverage > 1.0) or (0 <= coverage <= 1.0 and coverage < 0.60):
        score += 15
        reasons.append("Low Test Coverage")

    # 4. Coupling Between Objects (CBO)
    if cbo > 25:
        score += 15
        reasons.append("High Coupling Between Objects (CBO)")

    # 5. Lack of Cohesion (LCOM)
    if lcom > 70 or (0 < lcom <= 1.0 and lcom > 0.70):
        score += 15
        reasons.append("High Lack of Cohesion (LCOM)")

    # 6. Code Churn
    if churn > 600:
        score += 10
        reasons.append("High Code Churn")

    # 7. Past Defects
    if past_defects > 25:
        score += 15
        reasons.append("High Past Defects")

    # 8. Security Vulnerabilities
    if security_vulnerabilities > 0:
        score += 20
        reasons.append("Security Vulnerabilities Detected")

    # Limit score to 100
    score = min(score, 100)

    # Risk Classification
    if score >= 61:
        level = "High Technical Debt"
    elif score >= 31:
        level = "Medium Technical Debt"
    else:
        level = "Low Technical Debt"

    if len(reasons) == 0:
        reasons.append("Software metrics are within acceptable limits.")

    return {
        "Debt Score": score,
        "Debt Level": level,
        "Reasons": reasons
    }