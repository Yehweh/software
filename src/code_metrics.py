import ast
import re
import textwrap


# =====================================================================
# COMMON HELPERS
# =====================================================================

def count_todos(source_code):
    source_code = source_code or ""
    return len(
        re.findall(
            r"\bTODO\b",
            source_code,
            flags=re.IGNORECASE
        )
    )


def count_fixmes(source_code):
    source_code = source_code or ""
    return len(
        re.findall(
            r"\bFIXME\b",
            source_code,
            flags=re.IGNORECASE
        )
    )


def count_past_defects(source_code):
    source_code = source_code or ""

    pattern = re.compile(
        r"\b(?:BUG|DEFECT|HOTFIX|PATCH|ISSUE)"
        r"[\s\-_:#]*\d+\b",
        flags=re.IGNORECASE
    )

    return len(pattern.findall(source_code))


def estimate_code_churn(source_code):
    source_code = source_code or ""

    return len(
        re.findall(
            r"\b(?:modified|revision|changelog|patch|"
            r"refactor|update|churn)\b",
            source_code,
            flags=re.IGNORECASE
        )
    )


def _empty_metrics(source_code=""):
    source_code = source_code or ""

    return {
        "lines_of_code": 0,
        "comment_density": 0.0,
        "num_functions": 0,
        "num_classes": 0,
        "avg_function_length": 0.0,
        "max_function_length": 0,
        "cyclomatic_complexity": 1,
        "max_nesting_depth": 0,
        "num_imports": 0,
        "todo_count": count_todos(source_code),
        "fixme_count": count_fixmes(source_code),
        "coupling_between_objects": 0,
        "lack_of_cohesion": 0.0,
        "code_churn": estimate_code_churn(source_code),
        "past_defects": count_past_defects(source_code),
        "security_vulnerabilities": 0,
        "security_details": [],
    }


def find_matching_paren(text, start_idx):
    depth = 0

    for i in range(start_idx, len(text)):

        if text[i] == "(":
            depth += 1

        elif text[i] == ")":
            depth -= 1

            if depth == 0:
                return i

    return len(text) - 1


def find_matching_brace(text, start_idx):
    depth = 0

    for i in range(start_idx, len(text)):

        if text[i] == "{":
            depth += 1

        elif text[i] == "}":
            depth -= 1

            if depth == 0:
                return i

    return len(text) - 1


def analyze_c_style_lines(source_code):
    source_code = source_code or ""

    lines = source_code.splitlines()
    total_lines = len(lines)

    if total_lines == 0:
        return 0, 0.0

    code_lines_count = 0
    comment_lines_count = 0

    in_block_comment = False
    in_string = None

    for line in lines:

        stripped = line.strip()

        if not stripped:
            continue

        has_code = False
        has_comment = False

        i = 0
        n = len(stripped)

        while i < n:

            char = stripped[i]

            next_two = (
                stripped[i:i + 2]
                if i + 1 < n
                else ""
            )

            if in_block_comment:

                has_comment = True

                if next_two == "*/":
                    in_block_comment = False
                    i += 2
                else:
                    i += 1

            elif in_string:

                has_code = True

                if char == "\\" and i + 1 < n:
                    i += 2

                elif char == in_string:
                    in_string = None
                    i += 1

                else:
                    i += 1

            else:

                if next_two == "/*":
                    in_block_comment = True
                    has_comment = True
                    i += 2

                elif next_two == "//":
                    has_comment = True
                    break

                elif char in ('"', "'", "`"):
                    in_string = char
                    has_code = True
                    i += 1

                else:

                    if not char.isspace():
                        has_code = True

                    i += 1

        if in_string and in_string != "`":
            in_string = None

        if has_code:
            code_lines_count += 1

        if has_comment:
            comment_lines_count += 1

    density = round(
        (comment_lines_count / total_lines) * 100,
        2
    )

    return code_lines_count, density


def mask_c_comments_and_strings(source_code, is_js=False):
    source_code = source_code or ""

    result = []

    i = 0
    n = len(source_code)

    state = "NORMAL"

    while i < n:

        char = source_code[i]

        next_two = (
            source_code[i:i + 2]
            if i + 1 < n
            else ""
        )

        if state == "NORMAL":

            if next_two == "//":
                state = "LINE_COMMENT"
                result.append("  ")
                i += 2

            elif next_two == "/*":
                state = "BLOCK_COMMENT"
                result.append("  ")
                i += 2

            elif char == '"':
                state = "DOUBLE_QUOTE"
                result.append(" ")
                i += 1

            elif char == "'":
                state = "SINGLE_QUOTE"
                result.append(" ")
                i += 1

            elif is_js and char == "`":
                state = "TEMPLATE_LITERAL"
                result.append(" ")
                i += 1

            else:
                result.append(char)
                i += 1

        elif state == "LINE_COMMENT":

            if char == "\n":
                state = "NORMAL"
                result.append("\n")
            else:
                result.append(" ")

            i += 1

        elif state == "BLOCK_COMMENT":

            if next_two == "*/":
                state = "NORMAL"
                result.append("  ")
                i += 2
            else:
                result.append(
                    "\n" if char == "\n" else " "
                )
                i += 1

        elif state == "DOUBLE_QUOTE":

            if char == "\\" and i + 1 < n:
                result.append("  ")
                i += 2

            elif char == '"':
                state = "NORMAL"
                result.append(" ")
                i += 1

            else:
                result.append(
                    "\n" if char == "\n" else " "
                )
                i += 1

        elif state == "SINGLE_QUOTE":

            if char == "\\" and i + 1 < n:
                result.append("  ")
                i += 2

            elif char == "'":
                state = "NORMAL"
                result.append(" ")
                i += 1

            else:
                result.append(
                    "\n" if char == "\n" else " "
                )
                i += 1

        elif state == "TEMPLATE_LITERAL":

            if char == "\\" and i + 1 < n:
                result.append("  ")
                i += 2

            elif char == "`":
                state = "NORMAL"
                result.append(" ")
                i += 1

            else:
                result.append(
                    "\n" if char == "\n" else " "
                )
                i += 1

    return "".join(result)


def strip_c_comments(source_code, is_js=False):
    source_code = source_code or ""

    result = []

    i = 0
    n = len(source_code)

    state = "NORMAL"

    while i < n:

        char = source_code[i]

        next_two = (
            source_code[i:i + 2]
            if i + 1 < n
            else ""
        )

        if state == "NORMAL":

            if next_two == "//":
                state = "LINE_COMMENT"
                result.append("  ")
                i += 2

            elif next_two == "/*":
                state = "BLOCK_COMMENT"
                result.append("  ")
                i += 2

            elif char == '"':
                state = "DOUBLE_QUOTE"
                result.append(char)
                i += 1

            elif char == "'":
                state = "SINGLE_QUOTE"
                result.append(char)
                i += 1

            elif is_js and char == "`":
                state = "TEMPLATE_LITERAL"
                result.append(char)
                i += 1

            else:
                result.append(char)
                i += 1

        elif state == "LINE_COMMENT":

            if char == "\n":
                state = "NORMAL"
                result.append("\n")
            else:
                result.append(" ")

            i += 1

        elif state == "BLOCK_COMMENT":

            if next_two == "*/":
                state = "NORMAL"
                result.append("  ")
                i += 2
            else:
                result.append(
                    "\n" if char == "\n" else " "
                )
                i += 1

        elif state == "DOUBLE_QUOTE":

            result.append(char)

            if char == "\\" and i + 1 < n:
                result.append(source_code[i + 1])
                i += 2

            elif char == '"':
                state = "NORMAL"
                i += 1

            else:
                i += 1

        elif state == "SINGLE_QUOTE":

            result.append(char)

            if char == "\\" and i + 1 < n:
                result.append(source_code[i + 1])
                i += 2

            elif char == "'":
                state = "NORMAL"
                i += 1

            else:
                i += 1

        elif state == "TEMPLATE_LITERAL":

            result.append(char)

            if char == "\\" and i + 1 < n:
                result.append(source_code[i + 1])
                i += 2

            elif char == "`":
                state = "NORMAL"
                i += 1

            else:
                i += 1

    return "".join(result)


# =====================================================================
# PYTHON ANALYSIS
# =====================================================================

def calculate_cyclomatic_complexity(tree):

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

        elif hasattr(ast, "Match") and isinstance(
            node,
            ast.Match
        ):
            complexity += len(node.cases)

    return complexity


def calculate_max_nesting_depth(tree):

    max_depth = 0

    def visit(node, depth):

        nonlocal max_depth

        control_nodes = (
            ast.If,
            ast.For,
            ast.AsyncFor,
            ast.While,
            ast.With,
            ast.AsyncWith,
            ast.Try,
        )

        if isinstance(node, control_nodes):

            depth += 1

            max_depth = max(
                max_depth,
                depth
            )

            for child in ast.iter_child_nodes(node):
                visit(child, depth)

            return

        if hasattr(ast, "Match") and isinstance(
            node,
            ast.Match
        ):

            depth += 1

            max_depth = max(
                max_depth,
                depth
            )

            for case in node.cases:

                case_depth = depth + 1

                max_depth = max(
                    max_depth,
                    case_depth
                )

                for child in case.body:
                    visit(
                        child,
                        case_depth
                    )

            return

        for child in ast.iter_child_nodes(node):
            visit(child, depth)

    visit(tree, 0)

    return max_depth


def calculate_cbo(tree):

    coupled_entities = set()

    for node in ast.walk(tree):

        if isinstance(node, ast.Import):

            for alias in node.names:
                coupled_entities.add(
                    alias.name.split(".")[0]
                )

        elif isinstance(node, ast.ImportFrom):

            if node.module:
                coupled_entities.add(
                    node.module.split(".")[0]
                )

            for alias in node.names:
                coupled_entities.add(alias.name)

        elif isinstance(node, ast.ClassDef):

            for base in node.bases:

                if isinstance(base, ast.Name):
                    coupled_entities.add(base.id)

                elif isinstance(base, ast.Attribute):

                    if isinstance(base.value, ast.Name):
                        coupled_entities.add(
                            f"{base.value.id}.{base.attr}"
                        )

        elif isinstance(node, ast.Call):

            if isinstance(node.func, ast.Name):

                if node.func.id[:1].isupper():
                    coupled_entities.add(node.func.id)

            elif isinstance(node.func, ast.Attribute):

                if isinstance(node.func.value, ast.Name):

                    if node.func.value.id not in (
                        "self",
                        "cls"
                    ):
                        coupled_entities.add(
                            f"{node.func.value.id}.{node.func.attr}"
                        )

    return len(coupled_entities)


def calculate_lcom(classes):

    if not classes:
        return 0.0

    class_lcom_scores = []

    for cls in classes:

        methods = [
            node
            for node in cls.body
            if isinstance(
                node,
                (
                    ast.FunctionDef,
                    ast.AsyncFunctionDef
                )
            )
        ]

        if len(methods) <= 1:
            class_lcom_scores.append(0.0)
            continue

        method_attributes = []

        for method in methods:

            attributes = set()

            for node in ast.walk(method):

                if (
                    isinstance(node, ast.Attribute)
                    and isinstance(node.value, ast.Name)
                    and node.value.id == "self"
                ):
                    attributes.add(node.attr)

            method_attributes.append(attributes)

        total_pairs = 0
        disjoint_pairs = 0

        for i in range(
            len(method_attributes)
        ):

            for j in range(
                i + 1,
                len(method_attributes)
            ):

                total_pairs += 1

                if not (
                    method_attributes[i]
                    & method_attributes[j]
                ):
                    disjoint_pairs += 1

        if total_pairs > 0:

            lcom = round(
                disjoint_pairs / total_pairs,
                2
            )

        else:
            lcom = 0.0

        class_lcom_scores.append(lcom)

    return round(
        sum(class_lcom_scores)
        / len(class_lcom_scores),
        2
    )


def detect_security_vulnerabilities(
    tree,
    source_code=None
):

    if source_code is None:

        if isinstance(tree, str):

            source_code = tree

            try:
                tree = ast.parse(source_code)

            except (
                SyntaxError,
                IndentationError
            ):

                try:
                    tree = ast.parse(
                        textwrap.dedent(
                            source_code
                        )
                    )

                except (
                    SyntaxError,
                    IndentationError
                ):
                    return []

        else:
            source_code = ""

    source_code = source_code or ""

    issues = []

    for node in ast.walk(tree):

        if not isinstance(
            node,
            ast.Call
        ):
            continue

        if isinstance(
            node.func,
            ast.Name
        ):

            if node.func.id in (
                "eval",
                "exec",
                "compile"
            ):

                issues.append(
                    f"Dangerous dynamic code execution "
                    f"({node.func.id})"
                )

        elif isinstance(
            node.func,
            ast.Attribute
        ):

            if isinstance(
                node.func.value,
                ast.Name
            ):

                module = node.func.value.id
                function = node.func.attr

                full_name = (
                    f"{module}.{function}"
                )

                if full_name in (
                    "os.system",
                    "os.popen",
                    "os.spawn",
                    "os.exec",
                ):

                    issues.append(
                        f"Insecure command execution "
                        f"via {full_name}"
                    )

                elif full_name in (
                    "pickle.loads",
                    "pickle.load",
                    "cPickle.loads",
                    "cPickle.load",
                ):

                    issues.append(
                        f"Insecure object deserialization "
                        f"via {full_name}"
                    )

                elif full_name in (
                    "hashlib.md5",
                    "hashlib.sha1",
                ):

                    issues.append(
                        f"Weak/broken cryptographic hash "
                        f"function ({full_name})"
                    )

                elif module == "subprocess":

                    for keyword in node.keywords:

                        if (
                            keyword.arg == "shell"
                            and isinstance(
                                keyword.value,
                                ast.Constant
                            )
                            and keyword.value.value is True
                        ):

                            issues.append(
                                "Subprocess executed with "
                                "shell=True "
                                "(Command Injection risk)"
                            )

    secret_pattern = re.compile(
        r"""(?i)
        (?:api_key|secret_key|password|auth_token|
        access_token|private_key)
        \s*=\s*
        ['"][a-zA-Z0-9_\-\.]{8,}['"]
        """,
        re.VERBOSE
    )

    if secret_pattern.search(source_code):

        issues.append(
            "Potential hardcoded credential "
            "or secret key detected"
        )

    sql_patterns = [
        r"""\.execute\s*\(\s*f['"]""",
        r"""\.execute\s*\(\s*['"][^'"]*%""",
        r"""\.execute\s*\(\s*['"][^'"]*['"]\s*%""",
        r'''\.execute\s*\(\s*['"][^'"]*['"]\s*\+''',
        r"""\.execute\s*\(\s*['"][^'"]*['"]\.format\s*\(""",
    ]

    if any(
        re.search(
            pattern,
            source_code,
            re.IGNORECASE
        )
        for pattern in sql_patterns
    ):

        issues.append(
            "Possible SQL Injection vulnerability "
            "(unparameterized query)"
        )

    return list(
        dict.fromkeys(issues)
    )


def calculate_python_metrics(source_code):

    source_code = source_code or ""

    lines = source_code.splitlines()

    total_lines = len(lines)

    code_lines = [
        line
        for line in lines
        if line.strip()
        and not line.strip().startswith("#")
    ]

    comment_lines = [
        line
        for line in lines
        if line.strip().startswith("#")
    ]

    logical_lines = len(code_lines)

    comment_density = 0.0

    if total_lines > 0:

        comment_density = round(
            (
                len(comment_lines)
                / total_lines
            ) * 100,
            2
        )

    try:

        tree = ast.parse(
            source_code
        )

    except (
        SyntaxError,
        IndentationError
    ):

        try:

            tree = ast.parse(
                textwrap.dedent(
                    source_code
                )
            )

        except (
            SyntaxError,
            IndentationError
        ):

            return {
                "lines_of_code": logical_lines,
                "comment_density": comment_density,
                "num_functions": 0,
                "num_classes": 0,
                "avg_function_length": 0.0,
                "max_function_length": 0,
                "cyclomatic_complexity": 0,
                "max_nesting_depth": 0,
                "num_imports": 0,
                "todo_count": count_todos(
                    source_code
                ),
                "fixme_count": count_fixmes(
                    source_code
                ),
                "coupling_between_objects": 0,
                "lack_of_cohesion": 0.0,
                "code_churn": estimate_code_churn(
                    source_code
                ),
                "past_defects": count_past_defects(
                    source_code
                ),
                "security_vulnerabilities": 0,
                "security_details": [],
            }

    functions = []
    classes = []
    imports = 0

    for node in ast.walk(tree):

        if isinstance(
            node,
            (
                ast.FunctionDef,
                ast.AsyncFunctionDef
            )
        ):
            functions.append(node)

        elif isinstance(
            node,
            ast.ClassDef
        ):
            classes.append(node)

        elif isinstance(
            node,
            (
                ast.Import,
                ast.ImportFrom
            )
        ):
            imports += 1

    function_lengths = []

    for function in functions:

        if hasattr(
            function,
            "end_lineno"
        ):

            length = (
                function.end_lineno
                - function.lineno
                + 1
            )

        else:
            length = 1

        function_lengths.append(length)

    if function_lengths:

        avg_function_length = round(
            sum(function_lengths)
            / len(function_lengths),
            2
        )

        max_function_length = max(
            function_lengths
        )

    else:

        avg_function_length = 0.0
        max_function_length = 0

    complexity = (
        calculate_cyclomatic_complexity(
            tree
        )
    )

    nesting_depth = (
        calculate_max_nesting_depth(
            tree
        )
    )

    todo_count = count_todos(
        source_code
    )

    fixme_count = count_fixmes(
        source_code
    )

    cbo = calculate_cbo(tree)

    lcom = calculate_lcom(
        classes
    )

    security_issues = (
        detect_security_vulnerabilities(
            tree,
            source_code
        )
    )

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
        "coupling_between_objects": cbo,
        "lack_of_cohesion": lcom,
        "code_churn": estimate_code_churn(
            source_code
        ),
        "past_defects": count_past_defects(
            source_code
        ),
        "security_vulnerabilities": len(
            security_issues
        ),
        "security_details": security_issues,
    }


# =====================================================================
# C / C++ HELPERS
# =====================================================================

def calculate_c_nesting_depth(masked_code):

    pattern = re.compile(
        r"\b(?:if|for|while|switch|try|catch)\b"
    )

    intervals = []

    for match in pattern.finditer(
        masked_code
    ):

        start = match.start()

        after_keyword = match.end()

        paren_pos = masked_code.find(
            "(",
            after_keyword
        )

        if (
            paren_pos != -1
            and paren_pos < after_keyword + 10
        ):

            paren_end = find_matching_paren(
                masked_code,
                paren_pos
            )

            body_start = paren_end + 1

        else:

            body_start = after_keyword

        brace_pos = masked_code.find(
            "{",
            body_start
        )

        semi_pos = masked_code.find(
            ";",
            body_start
        )

        if (
            brace_pos != -1
            and (
                semi_pos == -1
                or brace_pos < semi_pos
            )
        ):

            end = find_matching_brace(
                masked_code,
                brace_pos
            )

            intervals.append(
                (start, end)
            )

        elif semi_pos != -1:

            intervals.append(
                (start, semi_pos)
            )

    if not intervals:
        return 0

    max_depth = 0

    for i, (
        start_1,
        end_1
    ) in enumerate(intervals):

        depth = 1

        for j, (
            start_2,
            end_2
        ) in enumerate(intervals):

            if i == j:
                continue

            if (
                start_2 < start_1
                and end_1 <= end_2
            ):

                depth += 1

        max_depth = max(
            max_depth,
            depth
        )

    return max_depth


# =====================================================================
# JAVASCRIPT
# =====================================================================

def extract_js_functions(
    source_code,
    masked_code
):

    function_spans = []
    seen_starts = set()

    pattern_func = re.compile(
        r"\b(?:async\s+)?function"
        r"(?:\s*\*)?"
        r"(?:\s+[A-Za-z_$][\w$]*)?"
        r"\s*\([^)]*\)"
    )

    for match in pattern_func.finditer(
        masked_code
    ):

        start = match.start()

        seen_starts.add(start)

        brace_pos = masked_code.find(
            "{",
            match.end()
        )

        if brace_pos != -1:

            end = find_matching_brace(
                masked_code,
                brace_pos
            )

        else:
            end = match.end()

        function_spans.append(
            (start, end)
        )

    for match in re.finditer(
        r"=>",
        masked_code
    ):

        start = match.start()

        index = match.end()

        while (
            index < len(masked_code)
            and masked_code[index].isspace()
        ):
            index += 1

        if (
            index < len(masked_code)
            and masked_code[index] == "{"
        ):

            end = find_matching_brace(
                masked_code,
                index
            )

        else:

            end = index

            while (
                end < len(masked_code)
                and masked_code[end]
                not in (
                    ";",
                    "\n",
                    "}",
                    ")"
                )
            ):
                end += 1

        function_spans.append(
            (start, end)
        )

    pattern_method = re.compile(
        r"(?<![.\w$])"
        r"(?:(?:async|get|set|static)\s+)?"
        r"([A-Za-z_$][\w$]*)"
        r"\s*\([^)]*\)\s*\{"
    )

    excluded = {
        "if",
        "for",
        "while",
        "switch",
        "catch",
        "with",
        "function",
        "return",
        "new",
    }

    for match in pattern_method.finditer(
        masked_code
    ):

        name = match.group(1)

        if name in excluded:
            continue

        start = match.start()

        if any(
            abs(start - existing) < 40
            for existing in seen_starts
        ):
            continue

        brace_pos = masked_code.find(
            "{",
            match.end() - 1
        )

        if brace_pos == -1:
            continue

        end = find_matching_brace(
            masked_code,
            brace_pos
        )

        seen_starts.add(start)

        function_spans.append(
            (start, end)
        )

    function_spans = list(
        dict.fromkeys(
            function_spans
        )
    )

    lengths = []

    for start, end in function_spans:

        start_line = (
            source_code[:start].count("\n")
            + 1
        )

        end_line = (
            source_code[:end + 1].count("\n")
            + 1
        )

        lengths.append(
            max(
                1,
                end_line - start_line + 1
            )
        )

    num_functions = len(
        function_spans
    )

    avg_length = (
        round(
            sum(lengths)
            / len(lengths),
            2
        )
        if lengths
        else 0.0
    )

    max_length = (
        max(lengths)
        if lengths
        else 0
    )

    return (
        num_functions,
        avg_length,
        max_length
    )


def extract_js_classes(masked_code):

    classes = set()

    named_classes = re.findall(
        r"\bclass\s+(?!extends\b)"
        r"([A-Za-z_$][\w$]*)",
        masked_code
    )

    classes.update(
        named_classes
    )

    anonymous_count = 0

    for match in re.finditer(
        r"\bclass\s+",
        masked_code
    ):

        position = match.end()

        while (
            position < len(masked_code)
            and masked_code[position].isspace()
        ):
            position += 1

        if masked_code.startswith(
            "extends",
            position
        ):

            after_extends = (
                position
                + len("extends")
            )

            if (
                after_extends >= len(masked_code)
                or not (
                    masked_code[
                        after_extends
                    ].isalnum()
                    or masked_code[
                        after_extends
                    ] in "_$"
                )
            ):

                anonymous_count += 1

        elif (
            position < len(masked_code)
            and masked_code[position] == "{"
        ):

            anonymous_count += 1

    for index in range(
        anonymous_count
    ):

        classes.add(
            f"__anonymous_class_{index}"
        )

    components = re.findall(
        r"\bfunction\s+([A-Z][\w$]*)",
        masked_code
    )

    classes.update(
        components
    )

    object_components = re.findall(
        r"\b(?:const|let|var)\s+"
        r"([A-Z][\w$]*)\s*=\s*\{",
        masked_code
    )

    classes.update(
        object_components
    )

    arrow_components = re.findall(
        r"\b(?:const|let|var)\s+"
        r"([A-Z][\w$]*)\s*=\s*"
        r"(?:function|\([^)]*\)\s*=>|"
        r"[A-Za-z_$][\w$]*\s*=>)",
        masked_code
    )

    classes.update(
        arrow_components
    )

    return len(classes)


def extract_js_imports_and_cbo(
    source_code,
    masked_code
):

    modules = set()

    num_imports = 0

    require_matches = re.findall(
        r"""require\s*\(\s*['"]([^'"]+)['"]\s*\)""",
        source_code
    )

    for module in require_matches:

        modules.add(
            module.split("/")[-1]
        )

        num_imports += 1

    import_matches = re.findall(
        r"""import\s+(?:[\s\S]*?\s+from\s+)?['"]([^'"]+)['"]""",
        source_code
    )

    for module in import_matches:

        modules.add(
            module.split("/")[-1]
        )

        num_imports += 1

    dynamic_matches = re.findall(
        r"""import\s*\(\s*['"]([^'"]+)['"]\s*\)""",
        source_code
    )

    for module in dynamic_matches:

        modules.add(
            module.split("/")[-1]
        )

        num_imports += 1

    export_matches = re.findall(
        r"""export\s+.*?\s+from\s+['"]([^'"]+)['"]""",
        source_code
    )

    for module in export_matches:

        modules.add(
            module.split("/")[-1]
        )

        num_imports += 1

    instantiations = set(
        re.findall(
            r"\bnew\s+([A-Z][A-Za-z0-9_$]*)",
            masked_code
        )
    )

    modules.update(
        instantiations
    )

    return (
        num_imports,
        len(modules)
    )


def calculate_js_complexity(masked_code):

    complexity = 1

    complexity += len(
        re.findall(
            r"\b(?:if|for|while|case|catch)\b",
            masked_code
        )
    )

    complexity += len(
        re.findall(
            r"&&|\|\||\?\?",
            masked_code
        )
    )

    complexity += len(
        re.findall(
            r"(?<!\?)\?(?![.?])",
            masked_code
        )
    )

    return complexity


def detect_js_security_vulnerabilities(
    source_code,
    masked_code
):

    issues = []

    if re.search(
        r"\beval\s*\(",
        masked_code
    ):

        issues.append(
            "Dangerous dynamic code execution (eval)"
        )

    if re.search(
        r"\bnew\s+Function\s*\(",
        masked_code
    ):

        issues.append(
            "Dangerous dynamic function constructor "
            "(new Function)"
        )

    if re.search(
        r"\bdocument\.write\s*\(",
        masked_code
    ):

        issues.append(
            "Unsafe DOM manipulation "
            "(document.write)"
        )

    if (
        re.search(
            r"\.innerHTML\s*=",
            source_code
        )
        or re.search(
            r"dangerouslySetInnerHTML",
            source_code
        )
    ):

        issues.append(
            "DOM-based Cross-Site Scripting (XSS) "
            "risk via innerHTML"
        )

    if re.search(
        r"\bchild_process\."
        r"(?:exec|execSync|spawn)\s*\(",
        source_code
    ):

        issues.append(
            "Command execution risk via child_process"
        )

    secret_pattern = re.compile(
        r"""(?i)
        (?:api_key|secret_key|password|auth_token|
        access_token|private_key)
        \s*=\s*
        ['"][a-zA-Z0-9_\-\.]{8,}['"]
        """,
        re.VERBOSE
    )

    if secret_pattern.search(
        source_code
    ):

        issues.append(
            "Potential hardcoded credential "
            "or secret key detected"
        )

    sql_pattern = re.compile(
        r"""(?i)
        (?:\.query|\.execute|\.run)
        \s*\(
        \s*(?:`
        .*?\$\{
        |
        ['"].*?\+
        |
        f['"]
        )
        """,
        re.VERBOSE
    )

    if sql_pattern.search(
        source_code
    ):

        issues.append(
            "Possible SQL Injection vulnerability "
            "(unparameterized query)"
        )

    return list(
        dict.fromkeys(issues)
    )


def calculate_javascript_metrics(
    source_code
):

    source_code = source_code or ""

    if not source_code.strip():
        return _empty_metrics(
            source_code
        )

    logical_lines, comment_density = (
        analyze_c_style_lines(
            source_code
        )
    )

    masked = mask_c_comments_and_strings(
        source_code,
        is_js=True
    )

    clean_code = strip_c_comments(
        source_code,
        is_js=True
    )

    (
        num_functions,
        avg_fn_len,
        max_fn_len
    ) = extract_js_functions(
        source_code,
        masked
    )

    num_classes = extract_js_classes(
        masked
    )

    (
        num_imports,
        cbo
    ) = extract_js_imports_and_cbo(
        clean_code,
        masked
    )

    complexity = calculate_js_complexity(
        masked
    )

    nesting_depth = calculate_c_nesting_depth(
        masked
    )

    security_issues = (
        detect_js_security_vulnerabilities(
            clean_code,
            masked
        )
    )

    return {
        "lines_of_code": logical_lines,
        "comment_density": comment_density,
        "num_functions": num_functions,
        "num_classes": num_classes,
        "avg_function_length": avg_fn_len,
        "max_function_length": max_fn_len,
        "cyclomatic_complexity": complexity,
        "max_nesting_depth": nesting_depth,
        "num_imports": num_imports,
        "todo_count": count_todos(
            source_code
        ),
        "fixme_count": count_fixmes(
            source_code
        ),
        "coupling_between_objects": cbo,
        "lack_of_cohesion": 0.0,
        "code_churn": estimate_code_churn(
            source_code
        ),
        "past_defects": count_past_defects(
            source_code
        ),
        "security_vulnerabilities": len(
            security_issues
        ),
        "security_details": security_issues,
    }


# =====================================================================
# HTML
# =====================================================================

def calculate_html_tag_nesting(
    source_code
):

    void_tags = {
        "area",
        "base",
        "br",
        "col",
        "embed",
        "hr",
        "img",
        "input",
        "link",
        "meta",
        "param",
        "source",
        "track",
        "wbr",
        "!doctype",
    }

    cleaned = re.sub(
        r"<!--.*?-->",
        "",
        source_code or "",
        flags=re.DOTALL
    )

    cleaned = re.sub(
        r"<(?:script|style)"
        r"(?:\s+[^>]*)?>"
        r".*?"
        r"</(?:script|style)>",
        "",
        cleaned,
        flags=re.DOTALL | re.IGNORECASE
    )

    tag_matches = re.finditer(
        r"<(/)?([A-Za-z0-9_-]+)"
        r"(?:\s+[^>]*)?>",
        cleaned
    )

    max_depth = 0
    current_depth = 0

    for match in tag_matches:

        full_tag = (
            match.group(0).strip()
        )

        is_closing = bool(
            match.group(1)
        )

        tag_name = (
            match.group(2).lower()
        )

        if (
            tag_name in void_tags
            or full_tag.endswith("/>")
        ):
            continue

        if is_closing:

            if current_depth > 0:
                current_depth -= 1

        else:

            current_depth += 1

            max_depth = max(
                max_depth,
                current_depth
            )

    return max_depth


def calculate_html_metrics(
    source_code
):

    source_code = source_code or ""

    lines = source_code.splitlines()

    total_lines = len(lines)

    if (
        total_lines == 0
        or not source_code.strip()
    ):

        return _empty_metrics(
            source_code
        )

    code_lines_count = 0
    comment_lines_count = 0

    in_html_comment = False

    for line in lines:

        stripped = line.strip()

        if not stripped:
            continue

        if in_html_comment:

            comment_lines_count += 1

            if "-->" in stripped:
                in_html_comment = False

        elif stripped.startswith(
            "<!--"
        ):

            comment_lines_count += 1

            if "-->" not in stripped:
                in_html_comment = True

        else:

            code_lines_count += 1

            if "<!--" in stripped:

                comment_lines_count += 1

                if "-->" not in stripped:
                    in_html_comment = True

    comment_density = round(
        (
            comment_lines_count
            / total_lines
        ) * 100,
        2
    )

    cleaned_html = re.sub(
        r"<!--.*?-->",
        "",
        source_code,
        flags=re.DOTALL
    )

    ext_scripts = len(
        re.findall(
            r'<script\s+[^>]*src=["\']'
            r'([^"\']+)["\']',
            cleaned_html,
            re.IGNORECASE
        )
    )

    ext_links = len(
        re.findall(
            r'<link\s+[^>]*href=["\']'
            r'([^"\']+)["\']',
            cleaned_html,
            re.IGNORECASE
        )
    )

    ext_media = len(
        re.findall(
            r'<(?:img|iframe|video|audio|source)'
            r'\s+[^>]*src=["\']'
            r'([^"\']+)["\']',
            cleaned_html,
            re.IGNORECASE
        )
    )

    num_imports = (
        ext_scripts
        + ext_links
        + ext_media
    )

    dependency_urls = set(
        re.findall(
            r'(?:src|href)=["\']'
            r'([^"\']+)["\']',
            cleaned_html,
            re.IGNORECASE
        )
    )

    cbo = len(
        {
            url.split("?")[0].split("/")[-1]
            for url in dependency_urls
            if (
                url
                and not url.startswith("#")
            )
        }
    )

    script_blocks = re.findall(
        r"<script(?:\s+[^>]*)?>"
        r"(.*?)"
        r"</script>",
        cleaned_html,
        flags=re.DOTALL | re.IGNORECASE
    )

    script_functions = 0
    script_complexity = 0
    script_function_lengths = []
    script_security_issues = []
    script_nesting = 0

    for script_content in script_blocks:

        if not script_content.strip():
            continue

        metrics = (
            calculate_javascript_metrics(
                script_content
            )
        )

        script_functions += (
            metrics["num_functions"]
        )

        script_complexity += (
            metrics["cyclomatic_complexity"]
            - 1
        )

        if (
            metrics["max_function_length"]
            > 0
        ):

            script_function_lengths.append(
                metrics["max_function_length"]
            )

        script_security_issues.extend(
            metrics["security_details"]
        )

        script_nesting = max(
            script_nesting,
            metrics["max_nesting_depth"]
        )

    inline_handlers = len(
        re.findall(
            r'\bon[a-z]+\s*=\s*'
            r'["\'][^"\']+["\']',
            cleaned_html,
            re.IGNORECASE
        )
    )

    num_functions = (
        script_functions
        + inline_handlers
    )

    if script_function_lengths:

        avg_fn_len = round(
            sum(script_function_lengths)
            / len(script_function_lengths),
            2
        )

        max_fn_len = max(
            script_function_lengths
        )

    else:

        avg_fn_len = 0.0
        max_fn_len = 0

    semantic_tags = len(
        re.findall(
            r"<(?:header|nav|main|section|article|"
            r"footer|aside|form|template|dialog|"
            r"table|fieldset)\b",
            cleaned_html,
            re.IGNORECASE
        )
    )

    class_attributes = re.findall(
        r'class=["\']([^"\']+)["\']',
        cleaned_html
    )

    unique_classes = set()

    for value in class_attributes:
        unique_classes.update(
            value.split()
        )

    num_classes = (
        semantic_tags
        + len(unique_classes)
    )

    interactive_elements = len(
        re.findall(
            r"<(?:select|option|details|dialog)\b"
            r"|<input\s+[^>]*"
            r'type=["\'](?:checkbox|radio|'
            r'submit|button)["\']',
            cleaned_html,
            re.IGNORECASE
        )
    )

    template_conditionals = len(
        re.findall(
            r"\{%\s*if\b"
            r"|\bv-if\b"
            r"|\bngIf\b",
            cleaned_html,
            re.IGNORECASE
        )
    )

    complexity = (
        1
        + script_complexity
        + interactive_elements
        + template_conditionals
    )

    dom_nesting = (
        calculate_html_tag_nesting(
            source_code
        )
    )

    nesting_depth = max(
        script_nesting,
        dom_nesting
    )

    security_issues = list(
        script_security_issues
    )

    if re.search(
        r'href=["\']\s*javascript:',
        cleaned_html,
        re.IGNORECASE
    ):

        security_issues.append(
            "Inline javascript: pseudo-protocol "
            "URL detected"
        )

    security_issues = list(
        dict.fromkeys(
            security_issues
        )
    )

    return {
        "lines_of_code": code_lines_count,
        "comment_density": comment_density,
        "num_functions": num_functions,
        "num_classes": num_classes,
        "avg_function_length": avg_fn_len,
        "max_function_length": max_fn_len,
        "cyclomatic_complexity": complexity,
        "max_nesting_depth": nesting_depth,
        "num_imports": num_imports,
        "todo_count": count_todos(
            source_code
        ),
        "fixme_count": count_fixmes(
            source_code
        ),
        "coupling_between_objects": cbo,
        "lack_of_cohesion": 0.0,
        "code_churn": estimate_code_churn(
            source_code
        ),
        "past_defects": count_past_defects(
            source_code
        ),
        "security_vulnerabilities": len(
            security_issues
        ),
        "security_details": security_issues,
    }


# =====================================================================
# CSS
# =====================================================================

def calculate_css_metrics(
    source_code
):

    source_code = source_code or ""

    if not source_code.strip():
        return _empty_metrics(
            source_code
        )

    logical_lines, comment_density = (
        analyze_c_style_lines(
            source_code
        )
    )

    masked = mask_c_comments_and_strings(
        source_code,
        is_js=False
    )

    clean_code = strip_c_comments(
        source_code,
        is_js=False
    )

    css_functions = len(
        re.findall(
            r"\b(?:calc|var|rgba?|hsla?|"
            r"linear-gradient|radial-gradient|"
            r"min|max|clamp|url)\s*\(",
            clean_code,
            re.IGNORECASE
        )
    )

    keyframes = re.findall(
        r"@keyframes\s+"
        r"([A-Za-z0-9_-]+)",
        clean_code,
        re.IGNORECASE
    )

    num_functions = (
        css_functions
        + len(keyframes)
    )

    unique_class_selectors = set(
        re.findall(
            r"\.([A-Za-z_-][\w-]*)",
            masked
        )
    )

    rule_blocks_count = len(
        re.findall(
            r"\{",
            masked
        )
    )

    num_classes = (
        len(unique_class_selectors)
        if unique_class_selectors
        else rule_blocks_count
    )

    import_matches = re.findall(
        r"""@import\s+(?:url\s*\(\s*['"]?([^'")]+)['"]?\s*\)|['"]([^'"]+)['"])""",
        clean_code,
        re.IGNORECASE
    )

    external_urls = re.findall(
        r"""url\s*\(\s*['"]?([^'")]+)['"]?\s*\)""",
        clean_code,
        re.IGNORECASE
    )

    num_imports = (
        len(import_matches)
        + len(external_urls)
    )

    all_references = set(
        external_urls
    )

    for first, second in import_matches:

        if first:
            all_references.add(first)

        if second:
            all_references.add(second)

    cbo = len(
        {
            reference.split("?")[0].split("/")[-1]
            for reference in all_references
            if (
                reference
                and not reference.startswith(
                    "data:"
                )
            )
        }
    )

    media_queries = len(
        re.findall(
            r"@media\b",
            masked,
            re.IGNORECASE
        )
    )

    supports_queries = len(
        re.findall(
            r"@supports\b",
            masked,
            re.IGNORECASE
        )
    )

    container_queries = len(
        re.findall(
            r"@container\b",
            masked,
            re.IGNORECASE
        )
    )

    pseudo_classes = len(
        re.findall(
            r":(?:hover|focus|active|disabled|"
            r"checked|nth-child|not|is|has)\b",
            masked,
            re.IGNORECASE
        )
    )

    complexity = (
        1
        + media_queries
        + supports_queries
        + container_queries
        + pseudo_classes
    )

    max_depth = 0
    current_depth = 0

    for char in masked:

        if char == "{":

            current_depth += 1

            max_depth = max(
                max_depth,
                current_depth
            )

        elif char == "}":

            if current_depth > 0:
                current_depth -= 1

    rule_lengths = []

    for match in re.finditer(
        r"\{",
        masked
    ):

        start_idx = match.start()

        end_idx = find_matching_brace(
            masked,
            start_idx
        )

        start_line = (
            source_code[:start_idx].count("\n")
            + 1
        )

        end_line = (
            source_code[:end_idx + 1].count("\n")
            + 1
        )

        rule_lengths.append(
            max(
                1,
                end_line - start_line + 1
            )
        )

    if rule_lengths:

        avg_fn_len = round(
            sum(rule_lengths)
            / len(rule_lengths),
            2
        )

        max_fn_len = max(
            rule_lengths
        )

    else:

        avg_fn_len = 0.0
        max_fn_len = 0

    return {
        "lines_of_code": logical_lines,
        "comment_density": comment_density,
        "num_functions": num_functions,
        "num_classes": num_classes,
        "avg_function_length": avg_fn_len,
        "max_function_length": max_fn_len,
        "cyclomatic_complexity": complexity,
        "max_nesting_depth": max_depth,
        "num_imports": num_imports,
        "todo_count": count_todos(
            source_code
        ),
        "fixme_count": count_fixmes(
            source_code
        ),
        "coupling_between_objects": cbo,
        "lack_of_cohesion": 0.0,
        "code_churn": estimate_code_churn(
            source_code
        ),
        "past_defects": count_past_defects(
            source_code
        ),
        "security_vulnerabilities": 0,
        "security_details": [],
    }


# =====================================================================
# JAVA
# =====================================================================

def calculate_java_metrics(
    source_code
):

    source_code = source_code or ""

    if not source_code.strip():
        return _empty_metrics(
            source_code
        )

    logical_lines, comment_density = (
        analyze_c_style_lines(
            source_code
        )
    )

    masked = mask_c_comments_and_strings(
        source_code,
        is_js=False
    )

    clean_code = strip_c_comments(
        source_code,
        is_js=False
    )

    classes = set(
        re.findall(
            r"\b(?:class|interface|enum|record)"
            r"\s+([A-Za-z_$][\w$]*)",
            masked
        )
    )

    num_classes = len(classes)

    function_spans = []
    seen_starts = set()

    constructor_pattern = re.compile(
        r"""
        (?:(?:public|protected|private)\s+)?
        ([A-Z_$][\w$]*)
        \s*
        \([^;{}]*\)
        (?:\s+throws\s+
            [\w.$]+
            (?:\s*,\s*[\w.$]+)*
        )?
        \s*\{
        """,
        re.VERBOSE
    )

    for match in constructor_pattern.finditer(
        masked
    ):

        name = match.group(1)

        if name not in classes:
            continue

        start = match.start()

        brace_pos = masked.find(
            "{",
            match.end() - 1
        )

        if brace_pos == -1:
            continue

        end = find_matching_brace(
            masked,
            brace_pos
        )

        function_spans.append(
            (start, end)
        )

        seen_starts.add(start)

    method_pattern = re.compile(
        r"""
        (?:
            (?:public|protected|private|static|final|
            abstract|synchronized|native|strictfp|
            default|transient|volatile)\s+
        )*
        (?:<[^>{};]+>\s+)?
        [A-Za-z_$][\w$<>\[\],.?]*\s+
        ([A-Za-z_$][\w$]*)
        \s*
        \(
            [^;{}()]*
        \)
        (?:
            \s+throws\s+
            [A-Za-z_$][\w$]*
            (?:\.[A-Za-z_$][\w$]*)*
            (?:\s*,\s*
                [A-Za-z_$][\w$]*
                (?:\.[A-Za-z_$][\w$]*)*
            )*
        )?
        \s*\{
        """,
        re.VERBOSE
    )

    for match in method_pattern.finditer(
        masked
    ):

        start = match.start()

        if any(
            abs(start - existing) < 10
            for existing in seen_starts
        ):
            continue

        brace_pos = masked.find(
            "{",
            match.end() - 1
        )

        if brace_pos == -1:
            continue

        end = find_matching_brace(
            masked,
            brace_pos
        )

        function_spans.append(
            (start, end)
        )

        seen_starts.add(start)

    function_spans = list(
        dict.fromkeys(
            function_spans
        )
    )

    lengths = []

    for start, end in function_spans:

        start_line = (
            source_code[:start].count("\n")
            + 1
        )

        end_line = (
            source_code[:end + 1].count("\n")
            + 1
        )

        lengths.append(
            max(
                1,
                end_line - start_line + 1
            )
        )

    num_functions = len(
        function_spans
    )

    avg_fn_len = (
        round(
            sum(lengths)
            / len(lengths),
            2
        )
        if lengths
        else 0.0
    )

    max_fn_len = (
        max(lengths)
        if lengths
        else 0
    )

    imports = re.findall(
        r"\bimport\s+"
        r"(?:static\s+)?"
        r"([\w.*]+)\s*;",
        clean_code
    )

    num_imports = len(imports)

    imported_types = {
        item.split(".")[-1]
        for item in imports
    }

    instantiations = set(
        re.findall(
            r"\bnew\s+"
            r"([A-Z][\w$]*)",
            masked
        )
    )

    cbo = len(
        imported_types
        | instantiations
    )

    complexity = 1

    complexity += len(
        re.findall(
            r"\b(?:if|for|while|case|catch)\b",
            masked
        )
    )

    complexity += len(
        re.findall(
            r"&&|\|\|",
            masked
        )
    )

    complexity += len(
        re.findall(
            r"(?<!\?)\?(?![.?])",
            masked
        )
    )

    nesting_depth = (
        calculate_c_nesting_depth(
            masked
        )
    )

    security_issues = []

    if re.search(
        r"Runtime\.getRuntime\(\)\.exec"
        r"|\bProcessBuilder\b",
        clean_code
    ):

        security_issues.append(
            "Dangerous system command execution "
            "(Runtime.exec / ProcessBuilder)"
        )

    if re.search(
        r"""(?:executeQuery|executeUpdate|execute)
        \s*\(\s*['"][^'"]*['"]\s*\+""",
        clean_code,
        re.VERBOSE
    ):

        security_issues.append(
            "Possible SQL Injection via "
            "string concatenation in JDBC statement"
        )

    if re.search(
        r'MessageDigest\.getInstance\s*\(\s*'
        r'["\'](?:MD5|SHA-1)["\']',
        clean_code,
        re.IGNORECASE
    ):

        security_issues.append(
            "Weak cryptographic hash algorithm "
            "(MD5/SHA-1)"
        )

    if re.search(
        r'Cipher\.getInstance\s*\(\s*'
        r'["\']DES["\']',
        clean_code,
        re.IGNORECASE
    ):

        security_issues.append(
            "Insecure cipher algorithm (DES)"
        )

    secret_pattern = re.compile(
        r"""(?i)
        (?:api_key|secret_key|password|auth_token|
        access_token|private_key)
        \s*=\s*
        ['"][a-zA-Z0-9_\-\.]{8,}['"]
        """,
        re.VERBOSE
    )

    if secret_pattern.search(
        clean_code
    ):

        security_issues.append(
            "Potential hardcoded credential "
            "or secret key detected"
        )

    security_issues = list(
        dict.fromkeys(
            security_issues
        )
    )

    return {
        "lines_of_code": logical_lines,
        "comment_density": comment_density,
        "num_functions": num_functions,
        "num_classes": num_classes,
        "avg_function_length": avg_fn_len,
        "max_function_length": max_fn_len,
        "cyclomatic_complexity": complexity,
        "max_nesting_depth": nesting_depth,
        "num_imports": num_imports,
        "todo_count": count_todos(
            source_code
        ),
        "fixme_count": count_fixmes(
            source_code
        ),
        "coupling_between_objects": cbo,
        "lack_of_cohesion": 0.0,
        "code_churn": estimate_code_churn(
            source_code
        ),
        "past_defects": count_past_defects(
            source_code
        ),
        "security_vulnerabilities": len(
            security_issues
        ),
        "security_details": security_issues,
    }


# =====================================================================
# C / C++
# =====================================================================

def calculate_c_nesting_depth_for_source(
    source_code
):
    masked = mask_c_comments_and_strings(
        source_code,
        is_js=False
    )

    return calculate_c_nesting_depth(
        masked
    )


def calculate_c_or_cpp_metrics(
    source_code,
    is_cpp=False
):

    source_code = source_code or ""

    if not source_code.strip():
        return _empty_metrics(
            source_code
        )

    logical_lines, comment_density = (
        analyze_c_style_lines(
            source_code
        )
    )

    masked = mask_c_comments_and_strings(
        source_code,
        is_js=False
    )

    clean_code = strip_c_comments(
        source_code,
        is_js=False
    )

    classes = set(
        re.findall(
            r"\b(?:class|struct|union|namespace)"
            r"\s+([A-Za-z_]\w*)",
            masked
        )
    )

    num_classes = len(classes)

    function_spans = []
    seen_starts = set()

    # -------------------------------------------------------------
    # C++ TRAILING RETURN TYPE
    #
    # auto get_x() -> int { ... }
    # -------------------------------------------------------------

    if is_cpp:

        trailing_return_pattern = re.compile(
            r"""
            \bauto\s+
            ([A-Za-z_~][\w]*(?:::[A-Za-z_~][\w]*)?)
            \s*
            \(
                [^;{}()]*
            \)
            \s*
            ->
            \s*
            [A-Za-z_~][\w:<>*&,\s]*
            \{
            """,
            re.VERBOSE
        )

        for match in trailing_return_pattern.finditer(
            masked
        ):

            start = match.start()

            brace_pos = masked.find(
                "{",
                match.end() - 1
            )

            if brace_pos == -1:
                continue

            end = find_matching_brace(
                masked,
                brace_pos
            )

            function_spans.append(
                (start, end)
            )

            seen_starts.add(start)

    # -------------------------------------------------------------
    # C++ OPERATOR OVERLOADING
    #
    # Examples:
    # operator==(...)
    # operator=(...)
    # Point::operator<(...)
    # -------------------------------------------------------------

    if is_cpp:

        operator_pattern = re.compile(
            r"""
            (?<![\w.])
            (?:
                (?:inline|static|virtual|explicit|
                constexpr|friend)
                \s+
            )*
            [A-Za-z_~][\w:<>*&,\s]*?
            \boperator\s*
            (?:
                <=>|==|!=|<=|>=|
                <<|>>|<<=|>>=|
                \+=|-=|\*=|/=|%=|
                &=|\|=|\^=|
                \+\+|--|
                &&|\|\||
                \[\]|\(\)|
                ->\*|->|
                [+\-*/%&|^<>=!~]
            )
            \s*
            \(
                [^;{}()]*
            \)
            \s*
            (?:
                const\s*
            )?
            (?:
                volatile\s*
            )?
            (?:
                override\s*
            )?
            (?:
                final\s*
            )?
            (?:
                noexcept(?:\s*\([^)]*\))?\s*
            )?
            (?:
                override\s*
            )?
            (?:
                final\s*
            )?
            \{
            """,
            re.VERBOSE
        )

        for match in operator_pattern.finditer(
            masked
        ):

            start = match.start()

            if start in seen_starts:
                continue

            brace_pos = masked.find(
                "{",
                match.end() - 1
            )

            if brace_pos == -1:
                continue

            end = find_matching_brace(
                masked,
                brace_pos
            )

            function_spans.append(
                (start, end)
            )

            seen_starts.add(start)

    # -------------------------------------------------------------
    # NORMAL C / C++ FUNCTIONS
    #
    # Handles:
    # void cleanup() override noexcept { }
    # void safe() noexcept(true) { }
    # Point::foo() { }
    # -------------------------------------------------------------

    normal_function_pattern = re.compile(
        r"""
        (?<![\w.])
        (?:
            (?:inline|static|virtual|explicit|extern|
            constexpr|consteval|friend|typename)
            \s+
        )*
        (?:
            [A-Za-z_~][\w:<>*&,\s]*?
        )
        ([A-Za-z_~]\w*(?:::[A-Za-z_~]\w*)?)
        \s*
        \(
            [^;{}()]*
        \)
        \s*
        (?:
            const\s*
        )?
        (?:
            volatile\s*
        )?
        (?:
            override\s*
        )?
        (?:
            final\s*
        )?
        (?:
            noexcept(?:\s*\([^)]*\))?\s*
        )?
        (?:
            override\s*
        )?
        (?:
            final\s*
        )?
        \{
        """,
        re.VERBOSE
    )

    excluded_names = {
        "if",
        "for",
        "while",
        "switch",
        "catch",
        "else",
        "return",
        "sizeof",
        "throw",
        "new",
        "delete",
    }

    for match in normal_function_pattern.finditer(
        masked
    ):

        start = match.start()

        if any(
            abs(start - existing) < 8
            for existing in seen_starts
        ):
            continue

        raw_name = match.group(1).strip()

        name = (
            raw_name
            .split("::")[-1]
            .strip()
            .lstrip("~")
        )

        if name in excluded_names:
            continue

        if raw_name == "operator":
            continue

        brace_pos = masked.find(
            "{",
            match.end() - 1
        )

        if brace_pos == -1:
            continue

        end = find_matching_brace(
            masked,
            brace_pos
        )

        function_spans.append(
            (start, end)
        )

        seen_starts.add(start)

    # -------------------------------------------------------------
    # C++ CONSTRUCTORS / DESTRUCTORS
    # -------------------------------------------------------------

    if is_cpp:

        constructor_pattern = re.compile(
            r"""
            (?<![\w.])
            ([A-Z_][A-Za-z0-9_]*)
            \s*
            \(
                [^;{}()]*
            \)
            \s*
            (?:
                noexcept(?:\s*\([^)]*\))?\s*
            )?
            \{
            """,
            re.VERBOSE
        )

        for match in constructor_pattern.finditer(
            masked
        ):

            name = match.group(1)

            if name not in classes:
                continue

            start = match.start()

            if any(
                abs(start - existing) < 8
                for existing in seen_starts
            ):
                continue

            brace_pos = masked.find(
                "{",
                match.end() - 1
            )

            if brace_pos == -1:
                continue

            end = find_matching_brace(
                masked,
                brace_pos
            )

            function_spans.append(
                (start, end)
            )

            seen_starts.add(start)

    # -------------------------------------------------------------
    # REMOVE DUPLICATES
    # -------------------------------------------------------------

    function_spans = list(
        dict.fromkeys(
            function_spans
        )
    )

    lengths = []

    for start, end in function_spans:

        start_line = (
            source_code[:start].count("\n")
            + 1
        )

        end_line = (
            source_code[:end + 1].count("\n")
            + 1
        )

        lengths.append(
            max(
                1,
                end_line - start_line + 1
            )
        )

    num_functions = len(
        function_spans
    )

    avg_fn_len = (
        round(
            sum(lengths)
            / len(lengths),
            2
        )
        if lengths
        else 0.0
    )

    max_fn_len = (
        max(lengths)
        if lengths
        else 0
    )

    includes = re.findall(
        r'#\s*include\s*[<"]'
        r'([^>"]+)[>"]',
        clean_code
    )

    cpp_modules = []

    if is_cpp:

        cpp_modules = re.findall(
            r"\bimport\s+[\w.]+;",
            masked
        )

    num_imports = (
        len(includes)
        + len(cpp_modules)
    )

    headers = set(includes)

    cbo = len(
        headers | classes
    )

    complexity = 1

    complexity += len(
        re.findall(
            r"\b(?:if|for|while|case|catch)\b",
            masked
        )
    )

    complexity += len(
        re.findall(
            r"&&|\|\|",
            masked
        )
    )

    complexity += len(
        re.findall(
            r"(?<!\?)\?(?![.?])",
            masked
        )
    )

    nesting_depth = (
        calculate_c_nesting_depth(
            masked
        )
    )

    security_issues = []

    if re.search(
        r"\bgets\s*\(",
        clean_code
    ):

        security_issues.append(
            "Critical buffer overflow vulnerability "
            "(gets() function is obsolete and unsafe)"
        )

    if re.search(
        r"\bstrcpy\s*\(",
        clean_code
    ):

        security_issues.append(
            "Unbounded memory copy "
            "(strcpy risk; prefer bounded alternatives)"
        )

    if re.search(
        r"\bstrcat\s*\(",
        clean_code
    ):

        security_issues.append(
            "Unbounded string concatenation "
            "(strcat risk)"
        )

    if re.search(
        r"\bsprintf\s*\(",
        clean_code
    ):

        security_issues.append(
            "Unbounded string formatting "
            "(sprintf risk; prefer snprintf)"
        )

    if re.search(
        r"\bvsprintf\s*\(",
        clean_code
    ):

        security_issues.append(
            "Unbounded varargs formatting "
            "(vsprintf risk)"
        )

    if re.search(
        r"\bsystem\s*\(",
        clean_code
    ):

        security_issues.append(
            "Insecure command execution via system()"
        )

    if re.search(
        r'\bscanf\s*\([^;]*["\'][^"\']*%s',
        clean_code
    ):

        security_issues.append(
            "Unbounded format specifier "
            "(%s in scanf without width specifier)"
        )

    secret_pattern = re.compile(
        r"""(?i)
        (?:api_key|secret_key|password|auth_token|
        access_token|private_key)
        \s*=\s*
        ['"][a-zA-Z0-9_\-\.]{8,}['"]
        """,
        re.VERBOSE
    )

    if secret_pattern.search(
        clean_code
    ):

        security_issues.append(
            "Potential hardcoded credential "
            "or secret key detected"
        )

    security_issues = list(
        dict.fromkeys(
            security_issues
        )
    )

    return {
        "lines_of_code": logical_lines,
        "comment_density": comment_density,
        "num_functions": num_functions,
        "num_classes": num_classes,
        "avg_function_length": avg_fn_len,
        "max_function_length": max_fn_len,
        "cyclomatic_complexity": complexity,
        "max_nesting_depth": nesting_depth,
        "num_imports": num_imports,
        "todo_count": count_todos(
            source_code
        ),
        "fixme_count": count_fixmes(
            source_code
        ),
        "coupling_between_objects": cbo,
        "lack_of_cohesion": 0.0,
        "code_churn": estimate_code_churn(
            source_code
        ),
        "past_defects": count_past_defects(
            source_code
        ),
        "security_vulnerabilities": len(
            security_issues
        ),
        "security_details": security_issues,
    }


def calculate_c_metrics(
    source_code
):
    return calculate_c_or_cpp_metrics(
        source_code,
        is_cpp=False
    )


def calculate_cpp_metrics(
    source_code
):
    return calculate_c_or_cpp_metrics(
        source_code,
        is_cpp=True
    )


# =====================================================================
# GENERIC
# =====================================================================

def calculate_generic_metrics(
    source_code
):

    source_code = source_code or ""

    lines = source_code.splitlines()

    code_lines = [
        line
        for line in lines
        if line.strip()
    ]

    return {
        "lines_of_code": len(code_lines),
        "comment_density": 0.0,
        "num_functions": 0,
        "num_classes": 0,
        "avg_function_length": 0.0,
        "max_function_length": 0,
        "cyclomatic_complexity": 1,
        "max_nesting_depth": 0,
        "num_imports": 0,
        "todo_count": count_todos(
            source_code
        ),
        "fixme_count": count_fixmes(
            source_code
        ),
        "coupling_between_objects": 0,
        "lack_of_cohesion": 0.0,
        "code_churn": estimate_code_churn(
            source_code
        ),
        "past_defects": count_past_defects(
            source_code
        ),
        "security_vulnerabilities": 0,
        "security_details": [],
    }


# =====================================================================
# UNIVERSAL DISPATCHER
# =====================================================================

def calculate_metrics_for_file(
    source_code,
    extension
):

    ext = (
        extension or ""
    ).lower()

    if ext == ".py":

        return calculate_python_metrics(
            source_code
        )

    elif ext == ".js":

        return calculate_javascript_metrics(
            source_code
        )

    elif ext in (
        ".html",
        ".htm"
    ):

        return calculate_html_metrics(
            source_code
        )

    elif ext == ".css":

        return calculate_css_metrics(
            source_code
        )

    elif ext == ".java":

        return calculate_java_metrics(
            source_code
        )

    elif ext in (
        ".c",
        ".h"
    ):

        return calculate_c_metrics(
            source_code
        )

    elif ext in (
        ".cpp",
        ".hpp",
        ".cc",
        ".cxx",
        ".hh",
        ".hxx",
    ):

        return calculate_cpp_metrics(
            source_code
        )

    else:

        return calculate_generic_metrics(
            source_code
        )