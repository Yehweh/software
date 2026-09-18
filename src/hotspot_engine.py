"""
Technical Debt Hotspots & File Priority Engine.

Calculates file-level technical debt priority scores and ranks files
from highest to lowest priority to help developers identify where
remediation will have the greatest impact.
"""


def _safe_number(value, default=0.0):
    """Safely cast metric values to float, handling None, bools, and errors."""
    if value is None or isinstance(value, bool):
        return default
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def calculate_file_priority(file_info):
    """
    Calculates an objective Technical Debt Priority Score (0-100) and
    priority classification (CRITICAL, HIGH, MEDIUM, LOW) for an individual file.

    Priority Calculation Model:
    --------------------------
    Base Technical Debt Score: 40% weight
    Security Vulnerabilities:  20% weight (critical hazard multiplier)
    Cyclomatic Complexity:     15% weight (control-flow branch density)
    Code Churn & Churn Risk:   10% weight (frequency of modifications)
    Coupling (CBO) & Nesting:  10% weight (architectural ripple-effect)
    Duplication & Test Deficit: 5% weight (code cloning & missing tests)

    Classification Thresholds:
    - CRITICAL : Priority Score >= 70 OR Any Security Vulnerabilities
    - HIGH     : Priority Score >= 50
    - MEDIUM   : Priority Score >= 30
    - LOW      : Priority Score < 30
    """
    if not isinstance(file_info, dict):
        return {
            "name": "Unknown",
            "path": "",
            "priority_score": 0.0,
            "priority_level": "LOW",
            "debt_score": 0.0,
            "debt_level": "Low Technical Debt",
            "reasons": []
        }

    metrics = file_info.get("metrics") or {}
    debt = file_info.get("technical_debt") or {}

    debt_score = _safe_number(debt.get("score", file_info.get("debt_score", 0)))
    complexity = _safe_number(metrics.get("cyclomatic_complexity", 1.0))
    security_issues = int(_safe_number(metrics.get("security_vulnerabilities", 0)))
    code_churn = _safe_number(metrics.get("code_churn", 0))
    past_defects = _safe_number(metrics.get("past_defects", 0))
    max_nesting = int(_safe_number(metrics.get("max_nesting_depth", 0)))
    cbo = _safe_number(metrics.get("coupling_between_objects", 0))
    duplication = _safe_number(metrics.get("duplication_percentage", 0))
    lines_of_code = int(_safe_number(metrics.get("lines_of_code", file_info.get("lines", 0))))
    avg_func_len = _safe_number(metrics.get("avg_function_length", 0))

    maintainability = _safe_number(metrics.get("maintainability_index", 100.0))

    # Normalized component scores (0 to 100)
    norm_debt = min(100.0, max(0.0, debt_score))
    norm_security = min(100.0, security_issues * 50.0)
    norm_complexity = min(100.0, max(0.0, (complexity / 20.0) * 100.0))
    norm_maintainability = min(100.0, max(0.0, (100.0 - maintainability)))
    norm_churn = min(100.0, max(0.0, (code_churn / 10.0) * 100.0))
    norm_coupling = min(100.0, max(0.0, ((cbo + max_nesting * 2.0) / 15.0) * 100.0))
    norm_duplication = min(100.0, max(0.0, (duplication / 20.0) * 100.0))

    # Weighted combination
    priority_score = (
        0.35 * norm_debt +
        0.25 * norm_security +
        0.15 * norm_complexity +
        0.10 * norm_maintainability +
        0.05 * norm_churn +
        0.05 * norm_coupling +
        0.05 * norm_duplication
    )

    if security_issues > 0:
        priority_score = max(priority_score, 75.0)

    priority_score = round(min(100.0, max(0.0, priority_score)), 1)

    # Determine contributing factors / reasons
    reasons = []
    if security_issues > 0:
        reasons.append(f"{security_issues} security vulnerability{' issues' if security_issues > 1 else ' flag'} detected")
    if complexity > 20:
        reasons.append(f"High Cyclomatic Complexity ({complexity:.1f})")
    elif complexity > 12:
        reasons.append(f"Elevated Cyclomatic Complexity ({complexity:.1f})")
    if maintainability < 50:
        reasons.append(f"Low Maintainability Index ({maintainability:.1f}/100)")
    if max_nesting > 4:
        reasons.append(f"Deep control-flow nesting depth ({max_nesting} levels)")
    if cbo > 8:
        reasons.append(f"High coupling between objects ({int(cbo)} dependencies)")
    if code_churn > 10:
        reasons.append(f"High code churn rate ({int(code_churn)} revisions)")
    if past_defects > 3:
        reasons.append(f"History of recurring past defects ({int(past_defects)} bugs)")
    if duplication > 15:
        reasons.append(f"High duplicated code density ({duplication:.1f}%)")
    if lines_of_code > 250 and avg_func_len > 35:
        reasons.append(f"Large subroutines averaging {avg_func_len:.1f} lines per function")

    # Inherit rule engine reasons if none were generated above
    if not reasons and debt.get("reasons"):
        reasons.extend(debt.get("reasons"))

    if not reasons:
        reasons.append("Code metrics are within stable maintainability limits")

    # Priority level classification
    if security_issues > 0 or priority_score >= 70.0:
        priority_level = "CRITICAL"
    elif priority_score >= 50.0:
        priority_level = "HIGH"
    elif priority_score >= 30.0:
        priority_level = "MEDIUM"
    else:
        priority_level = "LOW"

    file_name = file_info.get("name") or file_info.get("file_name") or file_info.get("path") or file_info.get("file_path") or "Unknown"
    file_path = file_info.get("path") or file_info.get("file_path") or file_info.get("name") or ""

    return {
        "name": file_name,
        "file_name": file_name,
        "path": file_path,
        "file_path": file_path,
        "language": file_info.get("language", "Unknown"),
        "lines": lines_of_code,
        "debt_score": debt_score,
        "debt_level": debt.get("level", file_info.get("debt_level", "Low Technical Debt")),
        "priority_score": priority_score,
        "priority_level": priority_level,
        "priority_badge_class": f"priority-{priority_level.lower()}",
        "cyclomatic_complexity": complexity,
        "maintainability_index": maintainability,
        "reasons": reasons,
        "metrics": {
            "complexity": complexity,
            "security_issues": security_issues,
            "max_nesting": max_nesting,
            "coupling": cbo,
            "churn": code_churn,
            "maintainability_index": maintainability
        }
    }


def calculate_file_hotspots(files):
    """
    Analyzes a list of file dictionary objects and returns a sorted list
    of technical debt hotspots, ranked from highest to lowest priority.
    """
    if not files or not isinstance(files, list):
        return []

    hotspots = [calculate_file_priority(f) for f in files if isinstance(f, dict)]

    # Sort primarily by priority_score descending, secondarily by debt_score descending
    hotspots.sort(
        key=lambda h: (
            1 if h["priority_level"] == "CRITICAL" else
            2 if h["priority_level"] == "HIGH" else
            3 if h["priority_level"] == "MEDIUM" else 4,
            -h["priority_score"],
            -h["debt_score"]
        )
    )

    return hotspots
