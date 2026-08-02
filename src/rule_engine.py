def detect_technical_debt(row):

    score = 0
    reasons = []

    complexity = row["cyclomatic_complexity"]
    duplication = row["duplication_percentage"]
    coverage = row["test_coverage"]

    if complexity > 30:
        score += 40
        reasons.append("High Cyclomatic Complexity")

    if duplication > 25:
        score += 35
        reasons.append("High Code Duplication")

    if coverage < 60:
        score += 25
        reasons.append("Low Test Coverage")

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