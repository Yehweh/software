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