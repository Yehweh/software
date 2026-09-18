"""
Comparison engine for evaluating and contrasting code quality metrics
and technical debt scores between two software projects or individual files.
"""


def extract_standardized_metrics(entity, name_fallback="Target"):
    """
    Normalizes either a project analysis dict or a single file data dict
    into a consistent metrics dictionary for comparison.
    """
    if not entity:
        return {}

    # Case 1: Full project analysis (has 'project_metrics')
    if "project_metrics" in entity:
        pm = entity["project_metrics"]
        return {
            "name": entity.get("project_name") or entity.get("name") or name_fallback,
            "type": "Project",
            "file_count": entity.get("file_count", 1),
            "lines_of_code": pm.get("total_lines", entity.get("total_lines", 0)),
            "num_functions": pm.get("total_functions", 0),
            "num_classes": pm.get("total_classes", 0),
            "num_imports": pm.get("total_imports", 0),
            "comment_density": pm.get("average_comment_density", 0.0),
            "avg_function_length": pm.get("average_function_length", 0.0),
            "cyclomatic_complexity": pm.get("cyclomatic_complexity", 0.0),
            "max_nesting_depth": pm.get("max_nesting_depth", 0),
            "todo_count": pm.get("todo_count", 0),
            "fixme_count": pm.get("fixme_count", 0),
            "coupling_between_objects": pm.get("average_cbo", pm.get("total_cbo", 0)),
            "lack_of_cohesion": pm.get("average_lcom", 0.0),
            "security_vulnerabilities": pm.get("total_security_vulnerabilities", 0),
            "past_defects": pm.get("total_past_defects", 0),
            "code_churn": pm.get("total_code_churn", 0),
            "debt_score": pm.get("average_debt_score", 0),
            "debt_level": pm.get("project_debt_level", "Low Technical Debt"),
            "high_debt": pm.get("high_debt", 0),
            "medium_debt": pm.get("medium_debt", 0),
            "low_debt": pm.get("low_debt", 0),
            "reasons": []
        }

    # Case 2: Single file analysis
    metrics = entity.get("metrics") or {}
    debt = entity.get("technical_debt") or {}

    return {
        "name": entity.get("name") or entity.get("path") or name_fallback,
        "type": f"File ({entity.get('language', entity.get('extension', 'Code'))})",
        "file_count": 1,
        "lines_of_code": metrics.get("lines_of_code", entity.get("lines", 0)),
        "num_functions": metrics.get("num_functions", 0),
        "num_classes": metrics.get("num_classes", 0),
        "num_imports": metrics.get("num_imports", 0),
        "comment_density": metrics.get("comment_density", 0.0),
        "avg_function_length": metrics.get("avg_function_length", 0.0),
        "cyclomatic_complexity": metrics.get("cyclomatic_complexity", 1.0),
        "max_nesting_depth": metrics.get("max_nesting_depth", 0),
        "todo_count": metrics.get("todo_count", 0),
        "fixme_count": metrics.get("fixme_count", 0),
        "coupling_between_objects": metrics.get("coupling_between_objects", 0),
        "lack_of_cohesion": metrics.get("lack_of_cohesion", 0.0),
        "security_vulnerabilities": metrics.get("security_vulnerabilities", 0),
        "past_defects": metrics.get("past_defects", 0),
        "code_churn": metrics.get("code_churn", 0),
        "debt_score": debt.get("score", 0),
        "debt_level": debt.get("level", "Low Technical Debt"),
        "high_debt": 1 if debt.get("level") == "High Technical Debt" else 0,
        "medium_debt": 1 if debt.get("level") == "Medium Technical Debt" else 0,
        "low_debt": 1 if debt.get("level") == "Low Technical Debt" else 0,
        "reasons": debt.get("reasons", [])
    }


def compare_entities(entity_a, entity_b, label_a="Version A", label_b="Version B", name_a=None, name_b=None):
    """
    Compares two software entities (A and B) and produces a comprehensive
    comparison report detailing metric deltas, better/worse statuses,
    and an executive summary declaring the winner.
    """
    if name_a is not None:
        label_a = name_a
    if name_b is not None:
        label_b = name_b

    std_a = extract_standardized_metrics(entity_a, label_a)
    std_b = extract_standardized_metrics(entity_b, label_b)

    score_a = std_a.get("debt_score", 0)
    score_b = std_b.get("debt_score", 0)

    # 1. Winner determination (Lower debt score is better)
    if score_a < score_b:
        winner = "A"
        winner_name = std_a["name"]
        loser_name = std_b["name"]
        diff_points = round(score_b - score_a, 2)
        pct_improvement = round((diff_points / score_b) * 100, 1) if score_b > 0 else 0
        headline = f"🏆 {winner_name} has Lower Technical Debt ({diff_points} points lower)"
    elif score_b < score_a:
        winner = "B"
        winner_name = std_b["name"]
        loser_name = std_a["name"]
        diff_points = round(score_a - score_b, 2)
        pct_improvement = round((diff_points / score_a) * 100, 1) if score_a > 0 else 0
        headline = f"🏆 {winner_name} has Lower Technical Debt ({diff_points} points lower)"
    else:
        winner = "TIE"
        winner_name = "Both versions"
        loser_name = ""
        diff_points = 0
        pct_improvement = 0
        headline = "⚖️ Both items have identical Technical Debt Scores"

    # 2. Metric comparison configuration
    # direction: "lower_is_better", "higher_is_better", "neutral"
    metrics_config = [
        ("debt_score", "Technical Debt Score", "lower_is_better", "points"),
        ("cyclomatic_complexity", "Cyclomatic Complexity", "lower_is_better", "score"),
        ("security_vulnerabilities", "Security Issues", "lower_is_better", "issues"),
        ("comment_density", "Comment Density", "higher_is_better", "%"),
        ("avg_function_length", "Avg Function Length", "lower_is_better", "lines"),
        ("max_nesting_depth", "Max Nesting Depth", "lower_is_better", "levels"),
        ("coupling_between_objects", "Coupling (CBO)", "lower_is_better", "deps"),
        ("lack_of_cohesion", "Lack of Cohesion (LCOM)", "lower_is_better", "ratio"),
        ("todo_count", "TODO Markers", "lower_is_better", "tags"),
        ("fixme_count", "FIXME Markers", "lower_is_better", "tags"),
        ("past_defects", "Past Defects", "lower_is_better", "markers"),
        ("code_churn", "Code Churn", "lower_is_better", "revisions"),
        ("lines_of_code", "Lines of Code (LOC)", "neutral", "lines"),
        ("num_functions", "Declared Functions", "neutral", "functions"),
        ("num_classes", "Declared Classes", "neutral", "classes"),
        ("num_imports", "Dependencies / Imports", "neutral", "modules"),
    ]

    metrics_comparison = []
    highlights = []

    for key, display_name, direction, unit in metrics_config:
        val_a = std_a.get(key, 0)
        val_b = std_b.get(key, 0)

        delta = round(val_b - val_a, 2)
        if isinstance(val_a, int) and isinstance(val_b, int):
            delta = val_b - val_a

        if direction == "lower_is_better":
            if val_a < val_b:
                advantage = "A"
            elif val_b < val_a:
                advantage = "B"
            else:
                advantage = "Equal"
        elif direction == "higher_is_better":
            if val_a > val_b:
                advantage = "A"
            elif val_b > val_a:
                advantage = "B"
            else:
                advantage = "Equal"
        else:
            advantage = "Neutral"

        metrics_comparison.append({
            "key": key,
            "display_name": display_name,
            "value_a": val_a,
            "value_b": val_b,
            "delta": delta,
            "direction": direction,
            "advantage": advantage,
            "unit": unit
        })

    # 3. Generate key narrative insights
    if winner in ("A", "B"):
        w_metrics = std_a if winner == "A" else std_b
        l_metrics = std_b if winner == "A" else std_a

        # Check Complexity
        if w_metrics["cyclomatic_complexity"] < l_metrics["cyclomatic_complexity"]:
            diff = round(l_metrics["cyclomatic_complexity"] - w_metrics["cyclomatic_complexity"], 1)
            highlights.append(f"Lower cyclomatic complexity by {diff} points (easier to maintain and test).")

        # Check Security
        if w_metrics["security_vulnerabilities"] < l_metrics["security_vulnerabilities"]:
            diff = l_metrics["security_vulnerabilities"] - w_metrics["security_vulnerabilities"]
            highlights.append(f"{diff} fewer security vulnerability flags detected.")

        # Check Comment density
        if w_metrics["comment_density"] > l_metrics["comment_density"]:
            diff = round(w_metrics["comment_density"] - l_metrics["comment_density"], 1)
            highlights.append(f"Higher documentation density (+{diff}% more commented lines).")

        # Check Nesting
        if w_metrics["max_nesting_depth"] < l_metrics["max_nesting_depth"]:
            highlights.append(f"Shallower control flow nesting depth ({w_metrics['max_nesting_depth']} vs {l_metrics['max_nesting_depth']}).")

        # Check Function length
        if w_metrics["avg_function_length"] < l_metrics["avg_function_length"]:
            diff = round(l_metrics["avg_function_length"] - w_metrics["avg_function_length"], 1)
            highlights.append(f"More concise subroutines (average function length is {diff} lines shorter).")

        # Check TODO/FIXME
        w_todos = w_metrics["todo_count"] + w_metrics["fixme_count"]
        l_todos = l_metrics["todo_count"] + l_metrics["fixme_count"]
        if w_todos < l_todos:
            highlights.append(f"Fewer unresolved TODO/FIXME markers ({w_todos} vs {l_todos}).")

        # Check CBO/Cohesion
        if w_metrics["coupling_between_objects"] < l_metrics["coupling_between_objects"]:
            highlights.append("Lower coupling between objects indicating a more modular architecture.")

    if not highlights:
        if winner == "TIE":
            highlights.append("Both analyzed candidates share equivalent technical debt ratings.")
        else:
            highlights.append(f"{winner_name} demonstrates superior overall maintainability and risk metrics.")

    # 4. Assembled Summary Report
    summary = {
        "winner": winner,
        "winner_name": winner_name,
        "loser_name": loser_name,
        "headline": headline,
        "diff_points": diff_points,
        "pct_improvement": pct_improvement,
        "highlights": highlights,
        "score_a": score_a,
        "score_b": score_b,
        "level_a": std_a.get("debt_level", "Unknown"),
        "level_b": std_b.get("debt_level", "Unknown"),
    }

    return {
        "item_a": std_a,
        "item_b": std_b,
        "metrics": metrics_comparison,
        "summary": summary
    }


def compare_projects(project_a, project_b, label_a="Project A", label_b="Project B", name_a=None, name_b=None):
    return compare_entities(project_a, project_b, label_a=label_a, label_b=label_b, name_a=name_a, name_b=name_b)


def compare_files(file_a, file_b, label_a="File A", label_b="File B", name_a=None, name_b=None):
    return compare_entities(file_a, file_b, label_a=label_a, label_b=label_b, name_a=name_a, name_b=name_b)


def compare(entity_a, entity_b, label_a="Version A", label_b="Version B", name_a=None, name_b=None):
    return compare_entities(entity_a, entity_b, label_a=label_a, label_b=label_b, name_a=name_a, name_b=name_b)

