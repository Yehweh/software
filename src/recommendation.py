def generate_recommendations(metrics, technical_debt):
    """
    Generate actionable recommendations based on
    source-code quality metrics and technical debt findings.
    """

    metrics = metrics or {}
    technical_debt = technical_debt or {}

    recommendations = []

    # =========================================================
    # 1. CYCLOMATIC COMPLEXITY
    # =========================================================

    complexity = metrics.get("cyclomatic_complexity", 0)

    if complexity > 20:
        recommendations.append(
            "Refactor highly complex functions into smaller functions "
            "with simpler control flow."
        )
    elif complexity > 10:
        recommendations.append(
            "Consider simplifying conditional logic and splitting "
            "complex functions."
        )

    # =========================================================
    # 2. FUNCTION LENGTH
    # =========================================================

    max_function_length = metrics.get(
        "max_function_length",
        0
    )

    if max_function_length > 50:
        recommendations.append(
            "Break very long functions into smaller, focused functions "
            "following the Single Responsibility Principle."
        )
    elif max_function_length > 30:
        recommendations.append(
            "Consider refactoring long functions to improve readability "
            "and maintainability."
        )

    # =========================================================
    # 3. NESTING DEPTH
    # =========================================================

    nesting_depth = metrics.get(
        "max_nesting_depth",
        0
    )

    if nesting_depth > 5:
        recommendations.append(
            "Reduce deeply nested control structures by using early "
            "returns, helper functions, or simpler conditions."
        )
    elif nesting_depth > 3:
        recommendations.append(
            "Consider reducing nested conditions to improve code clarity."
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

    if lines_of_code >= 20 and comment_density < 5:
        recommendations.append(
            "Add meaningful comments or documentation around complex "
            "logic and important implementation decisions."
        )

    # =========================================================
    # 5. TODO ITEMS
    # =========================================================

    todo_count = metrics.get(
        "todo_count",
        0
    )

    if todo_count > 0:
        recommendations.append(
            "Review and resolve outstanding TODO items before they "
            "accumulate into maintenance debt."
        )

    # =========================================================
    # 6. FIXME ITEMS
    # =========================================================

    fixme_count = metrics.get(
        "fixme_count",
        0
    )

    if fixme_count > 0:
        recommendations.append(
            "Prioritize FIXME items because they may represent known "
            "implementation problems or incomplete code."
        )

    # =========================================================
    # 7. COUPLING
    # =========================================================

    cbo = metrics.get(
        "coupling_between_objects",
        0
    )

    if cbo > 20:
        recommendations.append(
            "Reduce excessive coupling by introducing abstractions "
            "and separating tightly dependent components."
        )
    elif cbo > 10:
        recommendations.append(
            "Review dependencies between classes and modules to "
            "prevent unnecessary coupling."
        )

    # =========================================================
    # 8. LACK OF COHESION
    # =========================================================

    lcom = metrics.get(
        "lack_of_cohesion",
        0
    )

    if lcom > 0.70:
        recommendations.append(
            "Consider splitting classes with low cohesion into "
            "smaller classes with clearly defined responsibilities."
        )
    elif lcom > 0.40:
        recommendations.append(
            "Review class responsibilities and improve cohesion "
            "where possible."
        )

    # =========================================================
    # 9. SECURITY VULNERABILITIES
    # =========================================================

    security_vulnerabilities = metrics.get(
        "security_vulnerabilities",
        0
    )

    if security_vulnerabilities >= 3:
        recommendations.append(
            "Immediately review and remediate detected security "
            "vulnerabilities before deploying the affected code."
        )
    elif security_vulnerabilities > 0:
        recommendations.append(
            "Review detected security vulnerabilities and apply "
            "appropriate secure-coding practices."
        )

    # =========================================================
    # 10. PAST DEFECTS
    # =========================================================

    past_defects = metrics.get(
        "past_defects",
        0
    )

    if past_defects >= 5:
        recommendations.append(
            "Investigate areas with repeated defect indicators and "
            "increase automated testing and code review coverage."
        )
    elif past_defects > 0:
        recommendations.append(
            "Review defect-prone sections and add targeted test cases."
        )

    # =========================================================
    # 11. CODE CHURN
    # =========================================================

    code_churn = metrics.get(
        "code_churn",
        0
    )

    if code_churn >= 100:
        recommendations.append(
            "Review frequently changing code for instability and "
            "consider refactoring heavily modified sections."
        )
    elif code_churn >= 50:
        recommendations.append(
            "Monitor frequently modified sections and strengthen "
            "testing around them."
        )

    # =========================================================
    # 12. LARGE FILE
    # =========================================================

    if lines_of_code > 1000:
        recommendations.append(
            "Consider splitting very large source files into smaller "
            "modules with clear responsibilities."
        )
    elif lines_of_code > 500:
        recommendations.append(
            "Review large source files for opportunities to improve "
            "modularity."
        )

    # =========================================================
    # 13. STATIC ANALYSIS WARNINGS
    # =========================================================

    static_warnings = metrics.get(
        "static_analysis_warnings",
        0
    )

    if static_warnings >= 10:
        recommendations.append(
            "Run a static analysis tool and systematically resolve "
            "high-priority warnings."
        )
    elif static_warnings > 0:
        recommendations.append(
            "Review and resolve static analysis warnings where "
            "they indicate genuine code-quality problems."
        )

    # =========================================================
    # 14. PERFORMANCE ISSUES
    # =========================================================

    performance_issues = metrics.get(
        "performance_issues",
        0
    )

    if performance_issues >= 3:
        recommendations.append(
            "Profile performance-critical code and optimize the "
            "identified bottlenecks."
        )
    elif performance_issues > 0:
        recommendations.append(
            "Review detected performance issues and optimize "
            "inefficient operations."
        )

    # =========================================================
    # 15. TEST COVERAGE
    # =========================================================

    test_coverage = metrics.get(
        "test_coverage",
        None
    )

    if test_coverage is not None:

        if test_coverage < 50:
            recommendations.append(
                "Increase automated test coverage, especially for "
                "critical and frequently changing code."
            )
        elif test_coverage < 70:
            recommendations.append(
                "Increase test coverage for important and "
                "defect-prone functionality."
            )

    # =========================================================
    # 16. DUPLICATION
    # =========================================================

    duplication = metrics.get(
        "duplication_percentage",
        0
    )

    if duplication > 25:
        recommendations.append(
            "Reduce duplicated code by extracting reusable functions "
            "or common modules."
        )
    elif duplication > 10:
        recommendations.append(
            "Review duplicated code and identify opportunities for "
            "reuse and refactoring."
        )

    # =========================================================
    # DEFAULT RECOMMENDATION
    # =========================================================

    if not recommendations:
        recommendations.append(
            "Maintain the current code quality and continue regular "
            "testing, code reviews, and static analysis."
        )

    # =========================================================
    # REMOVE DUPLICATES
    # =========================================================

    unique_recommendations = []

    for recommendation in recommendations:

        if recommendation not in unique_recommendations:
            unique_recommendations.append(
                recommendation
            )

    # =========================================================
    # RETURN RESULT
    # =========================================================

    return {
        "recommendations": unique_recommendations,
        "technical_debt_score": technical_debt.get(
            "score",
            0
        ),
        "technical_debt_level": technical_debt.get(
            "level",
            "Low Technical Debt"
        )
    }


class StructuredRecommendations(list):
    """
    List wrapper that behaves as a list of recommendation dicts when iterated,
    while also supporting dict-style key access ('all', 'by_severity', 'total_count', etc.).
    """
    def __init__(self, items, by_severity=None):
        super().__init__(items)
        self.by_severity = by_severity or {}
        self.critical_count = len(self.by_severity.get("CRITICAL", []))
        self.high_count = len(self.by_severity.get("HIGH", []))
        self.medium_count = len(self.by_severity.get("MEDIUM", []))
        self.low_count = len(self.by_severity.get("LOW", []))
        self.total_count = len(items)

    def get(self, key, default=None):
        if key == "all":
            return list(self)
        if key == "by_severity":
            return self.by_severity
        if key == "total_count":
            return self.total_count
        if key == "critical_count":
            return self.critical_count
        if key == "high_count":
            return self.high_count
        if key == "medium_count":
            return self.medium_count
        if key == "low_count":
            return self.low_count
        return default

    def __getitem__(self, key):
        if isinstance(key, str):
            val = self.get(key)
            if val is not None:
                return val
            raise KeyError(key)
        return super().__getitem__(key)


def generate_structured_recommendations(metrics, technical_debt=None, files=None):
    """
    Generates actionable, structured recommendations adhering to the 3-part format:
    Problem -> Impact -> Recommended Action.

    Recommendations are prioritized and grouped into severity tiers:
    CRITICAL, HIGH, MEDIUM, and LOW.
    """
    metrics = metrics or {}
    technical_debt = technical_debt or {}

    def _safe(val, default=0.0):
        if val is None or isinstance(val, bool):
            return default
        try:
            return float(val)
        except (TypeError, ValueError):
            return default

    complexity = _safe(metrics.get("cyclomatic_complexity", metrics.get("average_cyclomatic_complexity", 0)))
    sec_vulns = int(_safe(metrics.get("total_security_vulnerabilities", metrics.get("security_vulnerabilities", 0))))
    cbo = _safe(metrics.get("average_cbo", metrics.get("coupling_between_objects", 0)))
    duplication = _safe(metrics.get("average_duplication", metrics.get("code_duplication_ratio", metrics.get("duplication_percentage", 0))))
    max_nesting = int(_safe(metrics.get("max_nesting_depth", 0)))
    max_func_len = int(_safe(metrics.get("max_function_length", metrics.get("avg_function_length", 0))))
    todo_count = int(_safe(metrics.get("todo_count", 0)))
    fixme_count = int(_safe(metrics.get("fixme_count", 0)))
    past_defects = int(_safe(metrics.get("total_past_defects", metrics.get("past_defects", 0))))
    churn = int(_safe(metrics.get("total_code_churn", metrics.get("code_churn", 0))))
    coverage = metrics.get("test_coverage") or metrics.get("average_test_coverage")
    has_tests = metrics.get("has_tests")
    debt_score = _safe(technical_debt.get("score", metrics.get("average_debt_score", 0)))
    mi = _safe(metrics.get("average_maintainability_index", metrics.get("maintainability_index", 75.0)))
    comment_density = _safe(metrics.get("average_comment_density", metrics.get("comment_density", 20.0)))

    recommendations = []

    # 1. SECURITY VULNERABILITIES (Highest priority)
    if sec_vulns > 0:
        recommendations.append({
            "id": "rec-sec-1",
            "title": "Security Vulnerability Exposure",
            "category": "Security",
            "severity": "CRITICAL",
            "problem": f"{sec_vulns} potential security vulnerability flag{'s' if sec_vulns > 1 else ''} detected in codebase files.",
            "impact": "Unpatched vulnerabilities and risky standard API invocations create exposure to remote exploitation, privilege escalation, or unauthorized data access.",
            "recommendation": "Review the flagged source files immediately. Replace unsafe subroutines (such as unparameterized queries, raw command execution, or deprecated APIs) with safe standard library alternatives and validate all external input boundaries."
        })

    # 2. CYCLOMATIC COMPLEXITY
    if complexity > 20:
        recommendations.append({
            "id": "rec-comp-1",
            "title": "High Cyclomatic Complexity",
            "category": "Complexity",
            "severity": "CRITICAL" if complexity > 30 else "HIGH",
            "problem": f"Average cyclomatic complexity is elevated at {complexity:.1f} points per module.",
            "impact": "Functions with numerous conditional branches and deep execution paths are difficult to maintain, reason about, and test exhaustively, resulting in higher defect density.",
            "recommendation": "Refactor monolithic functions into smaller, single-purpose subroutines. Apply guard clauses with early returns, replace nested switch/if chains with polymorphism or dispatch tables, and separate validation logic from core computation."
        })
    elif complexity > 10:
        recommendations.append({
            "id": "rec-comp-2",
            "title": "Moderate Cyclomatic Complexity",
            "category": "Complexity",
            "severity": "MEDIUM",
            "problem": f"Average cyclomatic complexity is moderately elevated ({complexity:.1f} points).",
            "impact": "Code branches are accumulating complexity, making upcoming feature extensions increasingly prone to logic bugs.",
            "recommendation": "Consider simplifying nested conditional logic and breaking larger functions into concise helper utilities."
        })

    # 3. MAINTAINABILITY INDEX
    if mi < 55.0:
        recommendations.append({
            "id": "rec-mi-1",
            "title": "Low Maintainability Index",
            "category": "Maintainability",
            "severity": "CRITICAL" if mi < 40 else "HIGH",
            "problem": f"Overall maintainability index is low at {mi:.1f}/100 across analyzed source files.",
            "impact": "Low maintainability increases developer cognitive load, slows feature delivery velocity, and multiplies defect probability.",
            "recommendation": "Perform focused refactoring on modules with high technical debt, reduce cyclomatic complexity, and improve modular encapsulation."
        })

    # 4. CODE DUPLICATION
    if duplication > 10:
        recommendations.append({
            "id": "rec-dup-1",
            "title": "Elevated Code Duplication",
            "category": "Duplication",
            "severity": "HIGH" if duplication > 25 else "MEDIUM",
            "problem": f"Code duplication is measured at {duplication:.1f}%, exceeding the healthy threshold.",
            "impact": "Duplicated blocks require identical changes in multiple locations. When fixes or feature changes are applied to one copy, orphaned duplicates remain unpatched and induce regressions.",
            "recommendation": "Extract common logic, utility algorithms, and template structures into centralized reusable functions or shared services following the Don't Repeat Yourself (DRY) principle."
        })

    # 5. TESTING & DEFECT RESILIENCE
    if has_tests is False:
        recommendations.append({
            "id": "rec-test-1",
            "title": "Missing Automated Test Suite",
            "category": "Testing",
            "severity": "HIGH",
            "problem": "No verified automated test cases or test frameworks were detected in this codebase.",
            "impact": "Modifications cannot be automatically validated for regressions, dramatically increasing the risk of shipping undetected defect bugs to production.",
            "recommendation": "Establish unit and integration test suites starting with high-priority technical debt hotspots and core business domain logic."
        })
    elif coverage is not None and _safe(coverage) < 50:
        cov_val = _safe(coverage)
        recommendations.append({
            "id": "rec-test-1",
            "title": "Insufficient Test Coverage",
            "category": "Testing",
            "severity": "HIGH",
            "problem": f"Automated test coverage is currently low at {cov_val:.1f}%.",
            "impact": "Changes to critical workflows cannot be automatically validated, dramatically increasing the risk of shipping undetected regression bugs.",
            "recommendation": "Establish unit and integration test suites starting with high-priority technical debt hotspots and core business domain logic."
        })
    elif past_defects > 3:
        recommendations.append({
            "id": "rec-test-2",
            "title": "Recurring Defect Incidence",
            "category": "Testing",
            "severity": "MEDIUM",
            "problem": f"A history of recurring past defects ({past_defects} reported) was detected without verified test suites.",
            "impact": "Modules with a history of defects are statistically more likely to generate new defects upon modification.",
            "recommendation": "Implement regression tests for every historically reported defect to prevent recurring regressions during subsequent maintenance cycles."
        })

    # 6. COUPLING & ARCHITECTURE
    if cbo > 8:
        recommendations.append({
            "id": "rec-cbo-1",
            "title": "Tight Architectural Coupling (CBO)",
            "category": "Architecture",
            "severity": "HIGH" if cbo > 15 else "MEDIUM",
            "problem": f"High Coupling Between Objects averaging {cbo:.1f} dependencies per module.",
            "impact": "Tightly coupled classes create architectural fragility where modifying one module causes unexpected side-effects and ripple failures across dependent components.",
            "recommendation": "Introduce dependency inversion, programming to interfaces rather than concrete implementations. Decouple cross-module communication using event dispatchers or lightweight service layers."
        })

    # 7. NESTING DEPTH
    if max_nesting > 4:
        recommendations.append({
            "id": "rec-nest-1",
            "title": "Deep Control Flow Nesting",
            "category": "Complexity",
            "severity": "MEDIUM",
            "problem": f"Control structures reach a maximum nesting depth of {max_nesting} levels.",
            "impact": "Heavily indented code pyramids obscure the primary execution path, significantly increasing developer cognitive load and error rates.",
            "recommendation": "Invert conditional checks using early returns (guard clauses), extract deeply nested loop bodies into dedicated helper functions, and flatten control hierarchies."
        })

    # 8. FUNCTION LENGTH
    if max_func_len > 40:
        recommendations.append({
            "id": "rec-len-1",
            "title": "Long Monolithic Functions",
            "category": "Maintainability",
            "severity": "MEDIUM",
            "problem": f"Maximum function length reaches {max_func_len} lines of code.",
            "impact": "Overly long subroutines tend to combine multiple responsibilities, violating Single Responsibility principles and complicating isolated unit testing.",
            "recommendation": "Decompose oversized functions into cohesive, well-named helper methods that each perform a single distinct task."
        })

    # 9. CODE CHURN
    if churn > 12:
        recommendations.append({
            "id": "rec-churn-1",
            "title": "High Code Churn Frequency",
            "category": "Maintainability",
            "severity": "LOW",
            "problem": f"High rate of code churn ({churn} recorded revision events) observed.",
            "impact": "Constantly rewritten code files indicate evolving requirements or unstable design interfaces that require stabilizing.",
            "recommendation": "Refactor volatile interfaces to establish stable abstraction layers and isolate frequently changing business requirements."
        })

    # 10. UNRESOLVED WORKAROUNDS (TODO / FIXME)
    total_markers = todo_count + fixme_count
    if total_markers > 0:
        recommendations.append({
            "id": "rec-markers-1",
            "title": "Accumulation of TODO / FIXME Debt",
            "category": "Maintainability",
            "severity": "MEDIUM" if fixme_count > 0 or total_markers > 5 else "LOW",
            "problem": f"{total_markers} unresolved marker tags detected ({todo_count} TODOs, {fixme_count} FIXMEs).",
            "impact": "Unaddressed markers indicate deferred edge cases, incomplete error handling, and temporary workarounds that have accumulated in the production codebase.",
            "recommendation": "Conduct a triage pass to audit all TODO and FIXME comments. Convert critical work items into tracked backlog issues and remove obsolete annotations."
        })

    # 11. DOCUMENTATION DENSITY
    if comment_density < 6.0 and metrics.get("total_lines", 100) >= 50:
        recommendations.append({
            "id": "rec-doc-1",
            "title": "Sparse Source Documentation",
            "category": "Documentation",
            "severity": "LOW",
            "problem": f"Comment density is low at {comment_density:.1f}% across analyzed codebase files.",
            "impact": "Undocumented module APIs and business assumptions make code comprehension slower and increase onboarding overhead.",
            "recommendation": "Add structured docstrings and comments detailing assumptions, input contracts, and error conditions."
        })

    # Fallback optimal baseline recommendation if no issues were detected
    if not recommendations:
        recommendations.append({
            "id": "rec-optimal-1",
            "title": "Maintain High Code Quality Standards",
            "category": "General",
            "severity": "LOW",
            "problem": "Software metrics are currently within optimal quality and maintainability limits.",
            "impact": "The analyzed codebase demonstrates clean design, manageable complexity, and minimal accumulated technical debt.",
            "recommendation": "Continue following established coding standards, enforce automated linter checks on pull requests, and keep complexity metrics within current baseline thresholds."
        })

    # Find involved files if files list is provided
    problem_files = []
    if files and isinstance(files, list):
        for f in files:
            fname = f.get("name") or f.get("file_name") or f.get("path") or f.get("file_path") or ""
            f_cc = _safe((f.get("metrics") or {}).get("cyclomatic_complexity", 0))
            f_debt = _safe((f.get("technical_debt") or {}).get("score", 0))
            if f_cc > 12 or f_debt > 50:
                if fname and fname not in problem_files:
                    problem_files.append(fname)

    # Attach aliases to each recommendation dict
    for r in recommendations:
        r["action"] = r["recommendation"]
        r["severity_class"] = f"severity-{r['severity'].lower()}"
        r["files"] = problem_files[:3]

    # Group by severity
    by_severity = {
        "CRITICAL": [r for r in recommendations if r["severity"] == "CRITICAL"],
        "HIGH": [r for r in recommendations if r["severity"] == "HIGH"],
        "MEDIUM": [r for r in recommendations if r["severity"] == "MEDIUM"],
        "LOW": [r for r in recommendations if r["severity"] == "LOW"]
    }

    return StructuredRecommendations(recommendations, by_severity)