def _safe_number(value, default=0.0):
try:
if value is None:
return default

    if isinstance(value, bool):
        return default

    number = float(value)

    if math.isnan(number) or math.isinf(number):
        return default

    return number

except (TypeError, ValueError):
    return default

def _get_metrics(entity):
if not isinstance(entity, dict):
return {}

metrics = entity.get("metrics")

if isinstance(metrics, dict):
    return metrics

return entity

def _get_name(entity, default="Unknown"):
if not isinstance(entity, dict):
return default

return (
    entity.get("name")
    or entity.get("filename")
    or entity.get("file_name")
    or entity.get("path")
    or default
)

def _get_language(entity):
if not isinstance(entity, dict):
return "Unknown"

language = (
    entity.get("language")
    or entity.get("Language")
)

if language:
    return str(language)

extension = str(
    entity.get(
        "extension",
        entity.get(
            "file_extension",
            ""
        )
    )
).lower()

language_map = {
    ".py": "Python",
    ".java": "Java",
    ".c": "C",
    ".h": "C",
    ".cpp": "C++",
    ".cc": "C++",
    ".cxx": "C++",
    ".hpp": "C++",
    ".hh": "C++",
    ".hxx": "C++",
    ".js": "JavaScript",
    ".html": "HTML",
    ".htm": "HTML",
    ".css": "CSS"
}

return language_map.get(
    extension,
    "Unknown"
)

def _get_debt_information(entity, metrics):
technical_debt = entity.get(
"technical_debt",
{}
)

if not isinstance(
    technical_debt,
    dict
):
    technical_debt = {}

score = technical_debt.get(
    "score"
)

if score is None:
    score = technical_debt.get(
        "Debt Score"
    )

if score is None:
    score = entity.get(
        "debt_score"
    )

if score is None:
    score = entity.get(
        "technical_debt_score"
    )

if score is None:
    score = metrics.get(
        "debt_score"
    )

if score is None:
    score = metrics.get(
        "technical_debt_score",
        0
    )

level = (
    technical_debt.get("level")
    or technical_debt.get(
        "Debt Level"
    )
    or entity.get("debt_level")
    or entity.get(
        "technical_debt_level"
    )
    or ""
)

reasons = (
    technical_debt.get("reasons")
    or technical_debt.get("Reasons")
    or []
)

return (
    _safe_number(score),
    str(level),
    reasons
)

def extract_standardized_metrics(
entity,
entity_type=None
):
if not isinstance(entity, dict):
entity = {}

metrics = _get_metrics(entity)

language = _get_language(
    entity
)

if entity_type is not None:
    normalized_type = str(
        entity_type
    ).lower()

    if normalized_type in (
        "project",
        "software_project"
    ):
        display_type = "Project"
    else:
        display_type = (
            f"File ({language})"
        )
else:
    display_type = (
        f"File ({language})"
    )

debt_score, debt_level, reasons = (
    _get_debt_information(
        entity,
        metrics
    )
)

return {
    "name": _get_name(entity),

    "type": display_type,

    "debt_score": debt_score,

    "debt_level": debt_level,

    "reasons": reasons,

    "lines_of_code": _safe_number(
        metrics.get(
            "lines_of_code",
            metrics.get(
                "loc",
                metrics.get(
                    "lines",
                    0
                )
            )
        )
    ),

    "comment_density": _safe_number(
        metrics.get(
            "comment_density",
            0
        )
    ),

    "num_functions": _safe_number(
        metrics.get(
            "num_functions",
            metrics.get(
                "functions",
                0
            )
        )
    ),

    "num_classes": _safe_number(
        metrics.get(
            "num_classes",
            metrics.get(
                "classes",
                0
            )
        )
    ),

    "num_imports": _safe_number(
        metrics.get(
            "num_imports",
            metrics.get(
                "imports",
                0
            )
        )
    ),

    "avg_function_length": _safe_number(
        metrics.get(
            "avg_function_length",
            0
        )
    ),

    "max_function_length": _safe_number(
        metrics.get(
            "max_function_length",
            0
        )
    ),

    "cyclomatic_complexity": _safe_number(
        metrics.get(
            "cyclomatic_complexity",
            metrics.get(
                "complexity",
                0
            )
        )
    ),

    "max_nesting_depth": _safe_number(
        metrics.get(
            "max_nesting_depth",
            metrics.get(
                "nesting_depth",
                0
            )
        )
    ),

    "todo_count": _safe_number(
        metrics.get(
            "todo_count",
            metrics.get(
                "todos",
                0
            )
        )
    ),

    "fixme_count": _safe_number(
        metrics.get(
            "fixme_count",
            metrics.get(
                "fixmes",
                0
            )
        )
    ),

    "coupling_between_objects": _safe_number(
        metrics.get(
            "coupling_between_objects",
            metrics.get(
                "cbo",
                0
            )
        )
    ),

    "lack_of_cohesion": _safe_number(
        metrics.get(
            "lack_of_cohesion",
            metrics.get(
                "lcom",
                0
            )
        )
    ),

    "security_vulnerabilities": _safe_number(
        metrics.get(
            "security_vulnerabilities",
            metrics.get(
                "security_issues",
                0
            )
        )
    ),

    "past_defects": _safe_number(
        metrics.get(
            "past_defects",
            metrics.get(
                "defects",
                0
            )
        )
    ),

    "code_churn": _safe_number(
        metrics.get(
            "code_churn",
            metrics.get(
                "churn",
                0
            )
        )
    ),

    "duplication_percentage": _safe_number(
        metrics.get(
            "duplication_percentage",
            metrics.get(
                "duplication",
                0
            )
        )
    ),

    "test_coverage": _safe_number(
        metrics.get(
            "test_coverage",
            metrics.get(
                "coverage",
                0
            )
        )
    )
}

COMPARISON_METRICS = [
(
"debt_score",
"Technical Debt Score",
"lower_is_better"
),
(
"lines_of_code",
"Lines of Code",
"lower_is_better"
),
(
"cyclomatic_complexity",
"Cyclomatic Complexity",
"lower_is_better"
),
(
"num_functions",
"Number of Functions",
"neutral"
),
(
"num_classes",
"Number of Classes",
"neutral"
),
(
"comment_density",
"Comment Density",
"higher_is_better"
),
(
"avg_function_length",
"Average Function Length",
"lower_is_better"
),
(
"max_function_length",
"Maximum Function Length",
"lower_is_better"
),
(
"max_nesting_depth",
"Maximum Nesting Depth",
"lower_is_better"
),
(
"todo_count",
"TODO Count",
"lower_is_better"
),
(
"fixme_count",
"FIXME Count",
"lower_is_better"
),
(
"coupling_between_objects",
"Coupling Between Objects",
"lower_is_better"
),
(
"lack_of_cohesion",
"Lack of Cohesion",
"lower_is_better"
),
(
"security_vulnerabilities",
"Security Vulnerabilities",
"lower_is_better"
),
(
"past_defects",
"Past Defects",
"lower_is_better"
),
(
"code_churn",
"Code Churn",
"lower_is_better"
),
(
"duplication_percentage",
"Duplication Percentage",
"lower_is_better"
),
(
"test_coverage",
"Test Coverage",
"higher_is_better"
)
]

def _get_advantage(
value_a,
value_b,
direction
):
if value_a == value_b:
return "Equal"

if direction == "higher_is_better":

    if value_a > value_b:
        return "A"

    return "B"

if direction == "lower_is_better":

    if value_a < value_b:
        return "A"

    return "B"

return "Equal"

def _build_metrics(
metrics_a,
metrics_b
):
results = []

for key, display_name, direction in COMPARISON_METRICS:

    value_a = _safe_number(
        metrics_a.get(
            key,
            0
        )
    )

    value_b = _safe_number(
        metrics_b.get(
            key,
            0
        )
    )

    delta = round(
        value_b - value_a,
        2
    )

    advantage = _get_advantage(
        value_a,
        value_b,
        direction
    )

    results.append(
        {
            "key": key,
            "display_name": display_name,
            "label": display_name,
            "name": display_name,
            "value_a": value_a,
            "value_b": value_b,
            "delta": delta,
            "advantage": advantage,
            "direction": direction
        }
    )

return results

def _build_highlights(
metrics_a,
metrics_b,
name_a,
name_b
):
highlights = []

important_metrics = [
    (
        "cyclomatic_complexity",
        "Cyclomatic Complexity",
        "lower_is_better"
    ),
    (
        "security_vulnerabilities",
        "Security Vulnerabilities",
        "lower_is_better"
    ),
    (
        "max_nesting_depth",
        "Maximum Nesting Depth",
        "lower_is_better"
    ),
    (
        "comment_density",
        "Comment Density",
        "higher_is_better"
    ),
    (
        "code_churn",
        "Code Churn",
        "lower_is_better"
    ),
    (
        "debt_score",
        "Technical Debt Score",
        "lower_is_better"
    )
]

for key, label, direction in important_metrics:

    value_a = _safe_number(
        metrics_a.get(
            key,
            0
        )
    )

    value_b = _safe_number(
        metrics_b.get(
            key,
            0
        )
    )

    if value_a == value_b:
        continue

    if direction == "higher_is_better":

        better = (
            name_a
            if value_a > value_b
            else name_b
        )

    else:

        better = (
            name_a
            if value_a < value_b
            else name_b
        )

    highlights.append(
        f"{better} has better {label}."
    )

if not highlights:
    highlights.append(
        "Both candidates have equivalent values for the compared metrics."
    )

return highlights

def compare_entities(
entity_a,
entity_b,
name_a=None,
name_b=None
):
item_a = extract_standardized_metrics(
entity_a
)

item_b = extract_standardized_metrics(
    entity_b
)

if name_a is None:
    name_a = item_a["name"]

if name_b is None:
    name_b = item_b["name"]

item_a["name"] = name_a
item_b["name"] = name_b

score_a = item_a[
    "debt_score"
]

score_b = item_b[
    "debt_score"
]

if score_a < score_b:

    winner = "B"
    winner_name = name_b
    loser_name = name_a

elif score_a > score_b:

    winner = "A"
    winner_name = name_a
    loser_name = name_b

else:

    winner = "TIE"
    winner_name = "Tie"
    loser_name = None

diff_points = round(
    abs(
        score_a - score_b
    ),
    2
)

highest_score = max(
    score_a,
    score_b
)

if highest_score > 0:

    pct_improvement = round(
        (
            diff_points
            / highest_score
        ) * 100,
        2
    )

else:

    pct_improvement = 0

if winner == "TIE":

    headline = (
        "Both candidates have Equal Technical Debt"
    )

else:

    headline = (
        f"🏆 {winner_name} has Lower Technical Debt"
    )

highlights = _build_highlights(
    item_a,
    item_b,
    name_a,
    name_b
)

summary = {
    "winner": winner,
    "winner_name": winner_name,
    "loser_name": loser_name,
    "diff_points": diff_points,
    "pct_improvement": pct_improvement,
    "percentage_improvement": pct_improvement,
    "headline": headline,
    "highlights": highlights
}

return {
    "summary": summary,
    "metrics": _build_metrics(
        item_a,
        item_b
    ),
    "item_a": item_a,
    "item_b": item_b,
    "candidate_a": name_a,
    "candidate_b": name_b,
    "metrics_a": item_a,
    "metrics_b": item_b,
    "comparison_status": "COMPARISON COMPLETE"
}

def compare_projects(
project_a,
project_b
):
return compare_entities(
project_a,
project_b
)

def compare_files(
file_a,
file_b
):
return compare_entities(
file_a,
file_b
)

def compare(
entity_a,
entity_b,
name_a=None,
name_b=None
):
return compare_entities(
entity_a,
entity_b,
name_a,
name_b
)