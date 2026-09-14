import ast
import re


def calculate_python_metrics(source_code):
    """
    Calculate software quality metrics for Python source code.
    """

    lines = source_code.splitlines()

    # -----------------------------------------
    # Basic line metrics
    # -----------------------------------------

    total_lines = len(lines)

    code_lines = [
        line for line in lines
        if line.strip() and not line.strip().startswith("#")
    ]

    comment_lines = [
        line for line in lines
        if line.strip().startswith("#")
    ]

    logical_lines = len(code_lines)

    comment_density = 0

    if total_lines > 0:
        comment_density = round(
            (len(comment_lines) / total_lines) * 100, 2
        )

    # -----------------------------------------
    # Parse Python source code
    # -----------------------------------------

    try:
        tree = ast.parse(source_code)
    except SyntaxError:
        return {
            "lines_of_code": logical_lines,
            "comment_density": comment_density,
            "num_functions": 0,
            "num_classes": 0,
            "avg_function_length": 0,
            "max_function_length": 0,
            "cyclomatic_complexity": 0,
            "max_nesting_depth": 0,
            "num_imports": 0,
            "todo_count": count_todos(source_code),
            "fixme_count": count_fixmes(source_code),
        }

    # -----------------------------------------
    # Functions and classes
    # -----------------------------------------

    functions = []
    classes = []
    imports = 0

    for node in ast.walk(tree):

        if isinstance(
            node,
            (ast.FunctionDef, ast.AsyncFunctionDef)
        ):
            functions.append(node)

        elif isinstance(node, ast.ClassDef):
            classes.append(node)

        elif isinstance(
            node,
            (ast.Import, ast.ImportFrom)
        ):
            imports += 1

    # -----------------------------------------
    # Function length
    # -----------------------------------------

    function_lengths = []

    for function in functions:

        if hasattr(function, "end_lineno"):
            length = function.end_lineno - function.lineno + 1
        else:
            length = 1

        function_lengths.append(length)

    if function_lengths:

        avg_function_length = round(
            sum(function_lengths) / len(function_lengths),
            2
        )

        max_function_length = max(function_lengths)

    else:

        avg_function_length = 0
        max_function_length = 0

    # -----------------------------------------
    # Cyclomatic complexity
    # -----------------------------------------

    complexity = calculate_cyclomatic_complexity(tree)

    # -----------------------------------------
    # Maximum nesting depth
    # -----------------------------------------

    nesting_depth = calculate_max_nesting_depth(tree)

    # -----------------------------------------
    # TODO / FIXME detection
    # -----------------------------------------

    todo_count = count_todos(source_code)
    fixme_count = count_fixmes(source_code)

    # -----------------------------------------
    # Return metrics
    # -----------------------------------------

    return {
        "lines_of_code": logical_lines,
        "comment_density": comment_density,
        "num_functions": len(functions),
        "num_classes": len(classes),
        "avg_function_length": avg_function_length,
        "max_function_length": max_function_length,
        "cyclomatic_complexity": complexity,
        "max_nesting_depth": nesting_depth,
        "num_imports": imports,
        "todo_count": todo_count,
        "fixme_count": fixme_count,
    }


def calculate_cyclomatic_complexity(tree):
    """
    Estimate cyclomatic complexity using Python AST.
    """

    complexity = 1

    for node in ast.walk(tree):

        if isinstance(
            node,
            (
                ast.If,
                ast.For,
                ast.AsyncFor,
                ast.While,
                ast.IfExp,
                ast.comprehension,
            )
        ):
            complexity += 1

        elif isinstance(node, ast.ExceptHandler):
            complexity += 1

        elif isinstance(node, ast.BoolOp):
            complexity += len(node.values) - 1

    return complexity


def calculate_max_nesting_depth(tree):
    """
    Calculate maximum nesting depth of control structures.
    """

    max_depth = 0

    def visit(node, depth):

        nonlocal max_depth

        if isinstance(
            node,
            (
                ast.If,
                ast.For,
                ast.AsyncFor,
                ast.While,
                ast.With,
                ast.AsyncWith,
                ast.Try,
            )
        ):
            depth += 1
            max_depth = max(max_depth, depth)

        for child in ast.iter_child_nodes(node):
            visit(child, depth)

    visit(tree, 0)

    return max_depth


def count_todos(source_code):
    """
    Count TODO comments.
    """

    return len(
        re.findall(
            r"\bTODO\b",
            source_code,
            flags=re.IGNORECASE
        )
    )


def count_fixmes(source_code):
    """
    Count FIXME comments.
    """

    return len(
        re.findall(
            r"\bFIXME\b",
            source_code,
            flags=re.IGNORECASE
        )
    )