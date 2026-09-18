import ast
import math


# ============================================================
# ADVANCED SOFTWARE QUALITY METRICS
# ============================================================


def calculate_cognitive_complexity(tree):
    """
    Calculate an approximate Cognitive Complexity score.

    Higher values indicate code that is harder for a human
    reader to understand.
    """

    complexity = 0

    control_nodes = (
        ast.If,
        ast.For,
        ast.AsyncFor,
        ast.While,
        ast.Try,
        ast.With,
        ast.AsyncWith,
    )

    def visit(node, nesting=0):
        nonlocal complexity

        for child in ast.iter_child_nodes(node):

            # Control-flow structures increase cognitive complexity.
            if isinstance(child, control_nodes):
                complexity += 1 + nesting
                visit(child, nesting + 1)

            # Boolean expressions add complexity when multiple
            # conditions are combined.
            elif isinstance(child, ast.BoolOp):
                complexity += max(0, len(child.values) - 1)
                visit(child, nesting)

            # Conditional expressions.
            elif isinstance(child, ast.IfExp):
                complexity += 1 + nesting
                visit(child, nesting + 1)

            # Exception handlers.
            elif isinstance(child, ast.ExceptHandler):
                complexity += 1 + nesting
                visit(child, nesting + 1)

            else:
                visit(child, nesting)

    visit(tree)

    return complexity


def calculate_parameter_count(tree):
    """
    Find the maximum number of parameters used by a function
    and the average number of parameters per function.
    """

    parameter_counts = []

    for node in ast.walk(tree):

        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):

            args = node.args

            count = (
                len(args.posonlyargs)
                + len(args.args)
                + len(args.kwonlyargs)
            )

            if args.vararg is not None:
                count += 1

            if args.kwarg is not None:
                count += 1

            parameter_counts.append(count)

    if not parameter_counts:
        return {
            "max_parameter_count": 0,
            "average_parameter_count": 0.0,
        }

    return {
        "max_parameter_count": max(parameter_counts),
        "average_parameter_count": round(
            sum(parameter_counts) / len(parameter_counts),
            2,
        ),
    }


def calculate_branch_count(tree):
    """
    Count decision/branch points in the source code.
    """

    branch_count = 0

    for node in ast.walk(tree):

        if isinstance(
            node,
            (
                ast.If,
                ast.For,
                ast.AsyncFor,
                ast.While,
                ast.IfExp,
                ast.ExceptHandler,
            ),
        ):
            branch_count += 1

        elif isinstance(node, ast.BoolOp):
            branch_count += max(0, len(node.values) - 1)

        elif hasattr(ast, "Match") and isinstance(node, ast.Match):
            branch_count += len(node.cases)

    return branch_count


def calculate_statement_count(tree):
    """
    Count executable statements in the Python AST.
    """

    statement_count = 0

    for node in ast.walk(tree):
        if isinstance(node, ast.stmt):
            statement_count += 1

    return statement_count


def calculate_maintainability_index(
    lines_of_code,
    cyclomatic_complexity,
    comment_density,
):
    """
    Calculate an approximate Maintainability Index.

    Result is normalized to a 0-100 scale.

    Higher values indicate better maintainability.
    """

    loc = max(1, lines_of_code)
    complexity = max(1, cyclomatic_complexity)

    # Convert comment percentage to a bounded value.
    comment_ratio = max(0.0, min(comment_density, 100.0))

    # Standard-style maintainability formula adapted to the
    # metrics available in this project.
    raw_index = (
        171
        - 3.42 * math.log(loc)
        - 0.23 * complexity
        + 0.99 * math.log(loc) * (comment_ratio / 100)
    )

    # Normalize to 0-100.
    maintainability = (raw_index / 171) * 100

    maintainability = max(
        0.0,
        min(100.0, maintainability),
    )

    return round(maintainability, 2)


def calculate_advanced_metrics(
    source_code,
    tree,
    lines_of_code,
    cyclomatic_complexity,
    comment_density,
):
    """
    Calculate all five advanced metrics.

    Metrics:
        1. Cognitive Complexity
        2. Maintainability Index
        3. Maximum Parameter Count
        4. Branch Count
        5. Statement Count
    """

    parameter_metrics = calculate_parameter_count(tree)

    cognitive_complexity = calculate_cognitive_complexity(tree)

    maintainability_index = calculate_maintainability_index(
        lines_of_code,
        cyclomatic_complexity,
        comment_density,
    )

    branch_count = calculate_branch_count(tree)

    statement_count = calculate_statement_count(tree)

    return {
        "cognitive_complexity": cognitive_complexity,

        "maintainability_index": maintainability_index,

        "max_parameter_count": parameter_metrics[
            "max_parameter_count"
        ],

        "average_parameter_count": parameter_metrics[
            "average_parameter_count"
        ],

        "branch_count": branch_count,

        "statement_count": statement_count,
    }