import ast
import re
import textwrap


def calculate_python_metrics(source_code):
    """
    Calculate software quality and testing metrics for Python source code.
    Includes structural, complexity, cohesion, coupling, defect, and security testing methods.
    """
    source_code = source_code or ""

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
    except (SyntaxError, IndentationError):
        try:
            tree = ast.parse(textwrap.dedent(source_code))
        except (SyntaxError, IndentationError):
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
            "coupling_between_objects": 0,
            "lack_of_cohesion": 0.0,
            "code_churn": 0,
            "past_defects": 0,
            "security_vulnerabilities": 0,
            "security_details": [],
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
    # 5 NEW QUALITY & TESTING METRICS
    # -----------------------------------------

    # 1. Coupling Between Objects (CBO)
    cbo = calculate_cbo(tree)

    # 2. Lack of Cohesion (LCOM)
    lcom = calculate_lcom(classes)

    # 3. Security Vulnerabilities
    security_issues = detect_security_vulnerabilities(tree, source_code)

    # 4. Past Defects
    past_defects = count_past_defects(source_code)

    # 5. Code Churn
    code_churn = estimate_code_churn(source_code)

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
        # 5 New Testing Metrics
        "coupling_between_objects": cbo,
        "lack_of_cohesion": lcom,
        "code_churn": code_churn,
        "past_defects": past_defects,
        "security_vulnerabilities": len(security_issues),
        "security_details": security_issues,
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

        elif hasattr(ast, "match_case") and isinstance(node, ast.match_case):
            complexity += 1

    return complexity


def calculate_max_nesting_depth(tree):
    """
    Calculate maximum nesting depth of control structures.
    """

    max_depth = 0

    def visit(node, depth):

        nonlocal max_depth

        is_control = isinstance(
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
        )
        if not is_control and hasattr(ast, "Match") and isinstance(node, ast.Match):
            is_control = True
        if not is_control and hasattr(ast, "match_case") and isinstance(node, ast.match_case):
            is_control = True

        if is_control:
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
    source_code = source_code or ""
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
    source_code = source_code or ""
    return len(
        re.findall(
            r"\bFIXME\b",
            source_code,
            flags=re.IGNORECASE
        )
    )


def calculate_cbo(tree):
    """
    Calculate Coupling Between Objects (CBO).
    Measures how dependent a module/class is on external modules, types, and classes.
    """

    coupled_entities = set()

    for node in ast.walk(tree):

        # Module and package imports
        if isinstance(node, ast.Import):
            for alias in node.names:
                coupled_entities.add(alias.name.split(".")[0])

        elif isinstance(node, ast.ImportFrom):
            if node.module:
                coupled_entities.add(node.module.split(".")[0])
            for alias in node.names:
                coupled_entities.add(alias.name)

        # Base classes inheritance coupling
        elif isinstance(node, ast.ClassDef):
            for base in node.bases:
                if isinstance(base, ast.Name):
                    coupled_entities.add(base.id)
                elif isinstance(base, ast.Attribute) and isinstance(base.value, ast.Name):
                    coupled_entities.add(f"{base.value.id}.{base.attr}")

        # Instantiations and external calls
        elif isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name) and node.func.id[:1].isupper():
                coupled_entities.add(node.func.id)
            elif isinstance(node.func, ast.Attribute) and isinstance(node.func.value, ast.Name):
                if node.func.value.id not in ("self", "cls"):
                    coupled_entities.add(f"{node.func.value.id}.{node.func.attr}")

    return len(coupled_entities)


def calculate_lcom(classes):
    """
    Calculate Lack of Cohesion of Methods (LCOM) across classes.
    Evaluates whether classes have unrelated responsibilities (God classes / Low cohesion).
    Returns a score between 0.0 (high cohesion) and 1.0 (disjoint/low cohesion).
    """

    if not classes:
        return 0.0

    class_lcom_scores = []

    for cls in classes:
        methods = [
            n for n in cls.body
            if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
        ]

        if len(methods) <= 1:
            class_lcom_scores.append(0.0)
            continue

        # Extract accessed self.attributes per method
        method_attrs = []
        for method in methods:
            attrs = set()
            for node in ast.walk(method):
                if isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name) and node.value.id == "self":
                    attrs.add(node.attr)
            method_attrs.append(attrs)

        # Count method pairs that do NOT share attributes vs pairs that do
        total_pairs = 0
        disjoint_pairs = 0

        for i in range(len(method_attrs)):
            for j in range(i + 1, len(method_attrs)):
                total_pairs += 1
                if not (method_attrs[i] & method_attrs[j]):
                    disjoint_pairs += 1

        if total_pairs > 0:
            lcom = round(disjoint_pairs / total_pairs, 2)
        else:
            lcom = 0.0

        class_lcom_scores.append(lcom)

    return round(sum(class_lcom_scores) / len(class_lcom_scores), 2)


def detect_security_vulnerabilities(tree, source_code):
    """
    Scan AST and source code for security vulnerabilities and dangerous patterns:
    - Code Injection (eval, exec)
    - Command Injection (subprocess shell=True, os.system, os.popen)
    - Insecure Deserialization (pickle, yaml without SafeLoader)
    - Hardcoded Secrets / Keys
    - Insecure Hashing (MD5, SHA1 for security)
    - SQL Injection string formatting
    """

    issues = []

    # 1. AST Checks for dangerous calls
    for node in ast.walk(tree):

        if isinstance(node, ast.Call):

            # eval() / exec()
            if isinstance(node.func, ast.Name):
                if node.func.id in ("eval", "exec", "compile"):
                    issues.append(f"Dangerous dynamic code execution ({node.func.id})")

            # os.system / os.popen
            elif isinstance(node.func, ast.Attribute) and isinstance(node.func.value, ast.Name):
                func_name = f"{node.func.value.id}.{node.func.attr}"
                if func_name in ("os.system", "os.popen", "os.spawn", "os.exec"):
                    issues.append(f"Insecure command execution via {func_name}")

                # subprocess shell=True
                elif node.func.value.id == "subprocess":
                    for kw in node.keywords:
                        if kw.arg == "shell" and isinstance(kw.value, ast.Constant) and kw.value.value is True:
                            issues.append("Subprocess executed with shell=True (Command Injection risk)")

                # pickle.loads / pickle.load
                elif func_name in ("pickle.loads", "pickle.load", "cPickle.loads", "cPickle.load"):
                    issues.append(f"Insecure object deserialization via {func_name}")

                # Insecure hashing
                elif func_name in ("hashlib.md5", "hashlib.sha1"):
                    issues.append(f"Weak/broken cryptographic hash function ({func_name})")

    # 2. Regex Checks for Hardcoded Secrets & SQL Injection
    secret_pattern = re.compile(
        r"""(?i)(?:api_key|secret_key|password|auth_token|access_token|private_key)\s*=\s*['"][a-zA-Z0-9_\-\.]{8,}['"]"""
    )
    if secret_pattern.search(source_code):
        issues.append("Potential hardcoded credential or secret key detected")

    sql_pattern = re.compile(
        r"""(?i)\.execute\s*\(\s*(?:f['"].*SELECT|f['"].*INSERT|f['"].*UPDATE|f['"].*DELETE|['"].*%s|['"].*format\()"""
    )
    if sql_pattern.search(source_code):
        issues.append("Possible SQL Injection vulnerability (unparameterized query)")

    # Deduplicate issues while preserving order
    unique_issues = list(dict.fromkeys(issues))
    return unique_issues


def count_past_defects(source_code):
    """
    Count bug, issue, and defect markers indicating unstable or bug-prone code.
    """
    source_code = source_code or ""
    markers = re.findall(
        r"\b(?:BUG|DEFECT|HOTFIX|PATCH|ISSUE)[\s\-_:#]*\d*",
        source_code,
        flags=re.IGNORECASE
    )
    return len(markers)


def estimate_code_churn(source_code):
    """
    Estimate code churn from modification history and revision/changelog markers.
    """
    source_code = source_code or ""
    churn_markers = len(
        re.findall(
            r"\b(?:modified|revision|changelog|patch|refactor|update|churn)\b",
            source_code,
            flags=re.IGNORECASE
        )
    )
    return churn_markers


# =====================================================================
# MULTI-LANGUAGE CODE METRICS & STATIC ANALYSIS
# (JavaScript, HTML, CSS, Java, C, C++)
# =====================================================================

def _empty_metrics(source_code=""):
    """Return default zeroed metrics for empty files."""
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


def analyze_c_style_lines(source_code):
    """
    Count total lines, code lines, comment lines, and comment density
    for C-style comment syntax (// and /* ... */).
    Safely ignores // and /* when inside string literals.
    """
    source_code = source_code or ""
    lines = source_code.splitlines()
    total_lines = len(lines)
    if total_lines == 0:
        return 0, 0.0

    code_lines_count = 0
    comment_lines_count = 0
    in_block = False
    in_str = None

    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue

        has_code = False
        has_comment = False
        i = 0
        n = len(stripped)

        while i < n:
            c = stripped[i]
            c2 = stripped[i:i+2] if i + 1 < n else ""

            if in_block:
                has_comment = True
                if c2 == "*/":
                    in_block = False
                    i += 2
                else:
                    i += 1
            elif in_str:
                has_code = True
                if c == "\\" and i + 1 < n:
                    i += 2
                elif c == in_str:
                    in_str = None
                    i += 1
                else:
                    i += 1
            else:
                if c2 == "/*":
                    in_block = True
                    has_comment = True
                    i += 2
                elif c2 == "//":
                    has_comment = True
                    break
                elif c in ('"', "'", '`'):
                    in_str = c
                    has_code = True
                    i += 1
                else:
                    if not c.isspace():
                        has_code = True
                    i += 1

        if in_str and in_str != '`':
            in_str = None

        if has_code:
            code_lines_count += 1
        if has_comment:
            comment_lines_count += 1

    density = round((comment_lines_count / total_lines) * 100, 2) if total_lines > 0 else 0.0
    return code_lines_count, density


def mask_c_comments_and_strings(source_code, is_js=False):
    """
    Mask comments and string literals with whitespace, preserving line structure.
    """
    result = []
    i = 0
    n = len(source_code)
    state = "NORMAL"

    while i < n:
        c = source_code[i]
        c2 = source_code[i:i+2] if i + 1 < n else ""

        if state == "NORMAL":
            if c2 == "//":
                state = "LINE_COMMENT"
                result.append("  ")
                i += 2
            elif c2 == "/*":
                state = "BLOCK_COMMENT"
                result.append("  ")
                i += 2
            elif c == '"':
                state = "DOUBLE_QUOTE"
                result.append(" ")
                i += 1
            elif c == "'":
                state = "SINGLE_QUOTE"
                result.append(" ")
                i += 1
            elif is_js and c == '`':
                state = "TEMPLATE_LITERAL"
                result.append(" ")
                i += 1
            else:
                result.append(c)
                i += 1

        elif state == "LINE_COMMENT":
            if c == '\n':
                state = "NORMAL"
                result.append('\n')
            else:
                result.append(' ')
            i += 1

        elif state == "BLOCK_COMMENT":
            if c2 == "*/":
                state = "NORMAL"
                result.append("  ")
                i += 2
            else:
                result.append('\n' if c == '\n' else ' ')
                i += 1

        elif state == "DOUBLE_QUOTE":
            if c == '\\' and i + 1 < n:
                result.append('  ')
                i += 2
            elif c == '"':
                state = "NORMAL"
                result.append(' ')
                i += 1
            else:
                result.append('\n' if c == '\n' else ' ')
                i += 1

        elif state == "SINGLE_QUOTE":
            if c == '\\' and i + 1 < n:
                result.append('  ')
                i += 2
            elif c == "'":
                state = "NORMAL"
                result.append(' ')
                i += 1
            else:
                result.append('\n' if c == '\n' else ' ')
                i += 1

        elif state == "TEMPLATE_LITERAL":
            if c == '\\' and i + 1 < n:
                result.append('  ')
                i += 2
            elif c == '`':
                state = "NORMAL"
                result.append(' ')
                i += 1
            else:
                result.append('\n' if c == '\n' else ' ')
                i += 1

    return "".join(result)


def strip_c_comments(source_code, is_js=False):
    """
    Strip C-style single-line (//) and multi-line (/* ... */) comments,
    replacing comment text with whitespace to preserve character offsets and line structure,
    while leaving string literals (including URLs and code in strings) intact.
    """
    source_code = source_code or ""
    result = []
    i = 0
    n = len(source_code)
    state = "NORMAL"

    while i < n:
        c = source_code[i]
        c2 = source_code[i:i+2] if i + 1 < n else ""

        if state == "NORMAL":
            if c2 == "//":
                state = "LINE_COMMENT"
                result.append("  ")
                i += 2
            elif c2 == "/*":
                state = "BLOCK_COMMENT"
                result.append("  ")
                i += 2
            elif c == '"':
                state = "DOUBLE_QUOTE"
                result.append(c)
                i += 1
            elif c == "'":
                state = "SINGLE_QUOTE"
                result.append(c)
                i += 1
            elif is_js and c == '`':
                state = "TEMPLATE_LITERAL"
                result.append(c)
                i += 1
            else:
                result.append(c)
                i += 1

        elif state == "LINE_COMMENT":
            if c == '\n':
                state = "NORMAL"
                result.append('\n')
            else:
                result.append(' ')
            i += 1

        elif state == "BLOCK_COMMENT":
            if c2 == "*/":
                state = "NORMAL"
                result.append("  ")
                i += 2
            else:
                result.append('\n' if c == '\n' else ' ')
                i += 1

        elif state == "DOUBLE_QUOTE":
            result.append(c)
            if c == '\\' and i + 1 < n:
                result.append(source_code[i+1])
                i += 2
            elif c == '"':
                state = "NORMAL"
                i += 1
            else:
                i += 1

        elif state == "SINGLE_QUOTE":
            result.append(c)
            if c == '\\' and i + 1 < n:
                result.append(source_code[i+1])
                i += 2
            elif c == "'":
                state = "NORMAL"
                i += 1
            else:
                i += 1

        elif state == "TEMPLATE_LITERAL":
            result.append(c)
            if c == '\\' and i + 1 < n:
                result.append(source_code[i+1])
                i += 2
            elif c == '`':
                state = "NORMAL"
                i += 1
            else:
                i += 1

    return "".join(result)


def find_matching_paren(text, start_idx):
    """Find matching closing parenthesis for opening '(' at or after start_idx."""
    depth = 0
    for i in range(start_idx, len(text)):
        if text[i] == '(':
            depth += 1
        elif text[i] == ')':
            depth -= 1
            if depth == 0:
                return i
    return len(text) - 1


def find_matching_brace(text, start_idx):
    """Find matching closing brace for opening '{' at or after start_idx."""
    depth = 0
    for i in range(start_idx, len(text)):
        if text[i] == '{':
            depth += 1
        elif text[i] == '}':
            depth -= 1
            if depth == 0:
                return i
    return len(text) - 1


def calculate_c_nesting_depth(masked_code):
    """
    Calculate maximum nesting depth of control flow structures
    (if, for, while, switch, try, catch) in masked code.
    """
    pattern = re.compile(r'\b(?:if|for|while|switch|try|catch)\b')
    intervals = []
    for m in pattern.finditer(masked_code):
        start = m.start()
        after_kw = m.end()
        paren_pos = masked_code.find('(', after_kw)
        if paren_pos != -1 and paren_pos < after_kw + 10:
            paren_end = find_matching_paren(masked_code, paren_pos)
            body_start = paren_end + 1
        else:
            body_start = after_kw

        brace_pos = masked_code.find('{', body_start)
        semi_pos = masked_code.find(';', body_start)
        if brace_pos != -1 and (semi_pos == -1 or brace_pos < semi_pos):
            end = find_matching_brace(masked_code, brace_pos)
            intervals.append((start, end))
        elif semi_pos != -1:
            intervals.append((start, semi_pos))

    if not intervals:
        return 0

    max_depth = 0
    for i, (s1, e1) in enumerate(intervals):
        d = 1 + sum(1 for j, (s2, e2) in enumerate(intervals) if i != j and s2 < s1 and e1 <= e2)
        if d > max_depth:
            max_depth = d
    return max_depth


# ---------------------------------------------------------------------
# 1. JAVASCRIPT STATIC ANALYSIS
# ---------------------------------------------------------------------

def extract_js_functions(source_code, masked_code):
    """
    Extract functions and calculate their lengths in JavaScript code.
    Supports standard functions, arrow functions, and class/object methods.
    """
    function_spans = []
    seen_starts = set()

    # 1. Standard function declarations & expressions
    pattern_func = re.compile(r'\b(?:async\s+)?function(?:\s*\*)?(?:\s+[a-zA-Z_$][\w$]*)?\s*\([^)]*\)', re.MULTILINE)
    for m in pattern_func.finditer(masked_code):
        start = m.start()
        seen_starts.add(start)
        brace_pos = masked_code.find('{', m.end())
        if brace_pos != -1 and brace_pos < m.end() + 20:
            end = find_matching_brace(masked_code, brace_pos)
            function_spans.append((start, end))
        else:
            function_spans.append((start, m.end()))

    # 2. Arrow functions: (...) => or param =>
    pattern_arrow = re.compile(r'=>')
    for m in pattern_arrow.finditer(masked_code):
        start = m.start()
        after = m.end()
        # Scan forward to find start of body
        idx = after
        while idx < len(masked_code) and masked_code[idx].isspace():
            idx += 1
        if idx < len(masked_code) and masked_code[idx] == '{':
            end = find_matching_brace(masked_code, idx)
            function_spans.append((start, end))
        else:
            # Single-expression arrow function up to delimiter
            end_pos = idx
            while end_pos < len(masked_code) and masked_code[end_pos] not in (';', '\n', '}', ')'):
                end_pos += 1
            function_spans.append((start, end_pos))

    # 3. Method declarations inside classes/objects: e.g. render() { or async run() {
    pattern_method = re.compile(r'(?<![.\w$])(?:(?:async|get|set|static)\s+)*([a-zA-Z_$][\w$]*)\s*\([^)]*\)\s*\{')
    exclude_keywords = {'if', 'for', 'while', 'switch', 'catch', 'with', 'function', 'return', 'new'}
    for m in pattern_method.finditer(masked_code):
        name = m.group(1)
        if name in exclude_keywords:
            continue
        start = m.start()
        # Check if preceding token was "function" or "function*"
        prefix = masked_code[max(0, start - 40):start].strip()
        if prefix.endswith("function") or prefix.endswith("function*"):
            continue
        if any(s <= start <= s + 40 for s in seen_starts):
            continue
        seen_starts.add(start)
        brace_pos = masked_code.find('{', m.end() - 1)
        if brace_pos != -1:
            end = find_matching_brace(masked_code, brace_pos)
            function_spans.append((start, end))

    # Calculate function lengths
    lengths = []
    for s, e in function_spans:
        start_line = source_code[:s].count('\n') + 1
        end_line = source_code[:e + 1].count('\n') + 1
        lengths.append(max(1, end_line - start_line + 1))

    num_functions = len(function_spans)
    avg_length = round(sum(lengths) / len(lengths), 2) if lengths else 0.0
    max_length = max(lengths) if lengths else 0

    return num_functions, avg_length, max_length


def extract_js_classes(masked_code):
    """Extract classes, constructors, and component definitions in JavaScript."""
    raw_classes = set(re.findall(r'\bclass\s+([a-zA-Z_$][\w$]*)', masked_code))
    classes = {c for c in raw_classes if c not in ('extends', 'implements')}
    anon_matches = re.findall(r'\bclass\s+(?:extends\s+[a-zA-Z_$][\w$.]*\s*)?\{', masked_code)
    classes.update(f"__anon_class_{i}" for i in range(len(anon_matches)))
    comp_funcs = set(re.findall(r'\bfunction\s+([A-Z][\w$]*)', masked_code))
    classes.update(comp_funcs)
    obj_modules = set(re.findall(r'\b(?:const|let|var)\s+([A-Z][\w$]*)\s*=\s*\{', masked_code))
    classes.update(obj_modules)
    arrow_comps = set(re.findall(r'\b(?:const|let|var)\s+([A-Z][\w$]*)\s*=\s*(?:function|\([^)]*\)\s*=>|[a-zA-Z_$][\w$]*\s*=>)', masked_code))
    classes.update(arrow_comps)
    return len(classes)


def extract_js_imports_and_cbo(source_code, masked_code):
    """Extract imports, modules, and Coupling Between Objects (CBO) in JavaScript."""
    modules = set()
    num_imports = 0

    req_matches = re.findall(r"""require\s*\(\s*['"]([^'"]+)['"]\s*\)""", source_code)
    for mod in req_matches:
        modules.add(mod.split('/')[-1])
        num_imports += 1

    import_matches = re.findall(r"""import\s+(?:.*?\s+from\s+)?['"]([^'"]+)['"]""", source_code)
    for mod in import_matches:
        modules.add(mod.split('/')[-1])
        num_imports += 1

    dyn_matches = re.findall(r"""import\s*\(\s*['"]([^'"]+)['"]\s*\)""", source_code)
    for mod in dyn_matches:
        modules.add(mod.split('/')[-1])
        num_imports += 1

    export_matches = re.findall(r"""export\s+.*?\s+from\s+['"]([^'"]+)['"]""", source_code)
    for mod in export_matches:
        modules.add(mod.split('/')[-1])
        num_imports += 1

    new_instantiations = set(re.findall(r"""\bnew\s+([A-Z][a-zA-Z0-9_$]*)""", masked_code))
    modules.update(new_instantiations)

    cbo = len(modules)
    return num_imports, cbo


def calculate_js_complexity(masked_code):
    """Calculate cyclomatic complexity for JavaScript."""
    complexity = 1
    complexity += len(re.findall(r'\b(?:if|for|while|case|catch)\b', masked_code))
    complexity += len(re.findall(r'&&|\|\||\?\?', masked_code))
    complexity += len(re.findall(r'(?<!\?)\?(?!\.|\?)', masked_code))
    return complexity


def detect_js_security_vulnerabilities(source_code, masked_code):
    """Scan JavaScript source code for security vulnerabilities."""
    issues = []
    if re.search(r'\beval\s*\(', masked_code):
        issues.append("Dangerous dynamic code execution (eval)")
    if re.search(r'\bnew\s+Function\s*\(', masked_code):
        issues.append("Dangerous dynamic function constructor (new Function)")
    if re.search(r'\bdocument\.write\s*\(', masked_code):
        issues.append("Unsafe DOM manipulation (document.write)")
    if re.search(r'\.innerHTML\s*=|dangerouslySetInnerHTML', source_code):
        issues.append("DOM-based Cross-Site Scripting (XSS) risk via innerHTML")
    if re.search(r'\bchild_process(?:\.(?:exec|execSync|spawn))\s*\(', source_code):
        issues.append("Command execution risk via child_process")
    secret_pattern = re.compile(
        r"""(?i)(?:api_key|secret_key|password|auth_token|access_token|private_key)\s*=\s*['"][a-zA-Z0-9_\-\.]{8,}['"]"""
    )
    if secret_pattern.search(source_code):
        issues.append("Potential hardcoded credential or secret key detected")
    sql_pattern = re.compile(
        r"""(?i)(?:\.query|\.execute|\.run)\s*\(\s*(?:`.*?\$\{|['"].*?\+|f['"].*?)"""
    )
    if sql_pattern.search(source_code):
        issues.append("Possible SQL Injection vulnerability (unparameterized query)")

    return list(dict.fromkeys(issues))


def calculate_javascript_metrics(source_code):
    """
    Calculate software quality and testing metrics for JavaScript source code.
    """
    source_code = source_code or ""
    if not source_code.strip():
        return _empty_metrics(source_code)

    logical_lines, comment_density = analyze_c_style_lines(source_code)
    masked = mask_c_comments_and_strings(source_code, is_js=True)
    clean_code = strip_c_comments(source_code, is_js=True)
    num_functions, avg_fn_len, max_fn_len = extract_js_functions(source_code, masked)
    num_classes = extract_js_classes(masked)
    num_imports, cbo = extract_js_imports_and_cbo(clean_code, masked)
    complexity = calculate_js_complexity(masked)
    nesting_depth = calculate_c_nesting_depth(masked)
    todo_count = count_todos(source_code)
    fixme_count = count_fixmes(source_code)
    past_defects = count_past_defects(source_code)
    code_churn = estimate_code_churn(source_code)
    sec_issues = detect_js_security_vulnerabilities(clean_code, masked)

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
        "todo_count": todo_count,
        "fixme_count": fixme_count,
        "coupling_between_objects": cbo,
        "lack_of_cohesion": 0.0,
        "code_churn": code_churn,
        "past_defects": past_defects,
        "security_vulnerabilities": len(sec_issues),
        "security_details": sec_issues,
    }


# ---------------------------------------------------------------------
# 2. HTML STATIC ANALYSIS
# ---------------------------------------------------------------------

def calculate_html_tag_nesting(source_code):
    """Calculate maximum DOM tag hierarchy nesting depth."""
    void_tags = {
        'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input',
        'link', 'meta', 'param', 'source', 'track', 'wbr', '!doctype'
    }
    # Strip comments so commented out tags do not affect nesting
    cleaned = re.sub(r'<!--.*?-->', '', source_code or "", flags=re.DOTALL)
    # Strip script and style blocks so js/css relational operators do not match as tags
    cleaned = re.sub(r'<(?:script|style)(?:\s+[^>]*)?>.*?</(?:script|style)>', '', cleaned, flags=re.DOTALL | re.IGNORECASE)

    tag_matches = re.finditer(r'<(/)?([a-zA-Z0-9_-]+)(?:\s+[^>]*)?>', cleaned)
    max_depth = 0
    current_depth = 0
    for m in tag_matches:
        full_tag = m.group(0).strip()
        is_closing = bool(m.group(1))
        tag_name = m.group(2).lower()
        if tag_name in void_tags or full_tag.endswith("/>") or full_tag.rstrip(">").endswith("/"):
            continue
        if is_closing:
            if current_depth > 0:
                current_depth -= 1
        else:
            current_depth += 1
            if current_depth > max_depth:
                max_depth = current_depth
    return max_depth


def calculate_html_metrics(source_code):
    """
    Calculate software quality and testing metrics for HTML markup and templates.
    Analyzes structure, semantic containers, styles, scripts, and security.
    """
    source_code = source_code or ""
    lines = source_code.splitlines()
    total_lines = len(lines)
    if total_lines == 0 or not source_code.strip():
        return _empty_metrics(source_code)

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
                after = stripped.split("-->", 1)[1].strip()
                if after:
                    code_lines_count += 1
        elif stripped.startswith("<!--"):
            comment_lines_count += 1
            if "-->" not in stripped:
                in_html_comment = True
            else:
                after = stripped.split("-->", 1)[1].strip()
                if after:
                    code_lines_count += 1
        else:
            code_lines_count += 1
            if "<!--" in stripped:
                comment_lines_count += 1
                if "-->" not in stripped:
                    in_html_comment = True

    comment_density = round((comment_lines_count / total_lines) * 100, 2) if total_lines > 0 else 0.0

    # Clean HTML without comments for structure, dependencies, scripts, and security analysis
    cleaned_html = re.sub(r'<!--.*?-->', '', source_code or "", flags=re.DOTALL)

    # Dependencies / Imports
    ext_scripts = len(re.findall(r'<script\s+[^>]*src=["\']([^"\']+)["\']', cleaned_html, re.IGNORECASE))
    ext_links = len(re.findall(r'<link\s+[^>]*href=["\']([^"\']+)["\']', cleaned_html, re.IGNORECASE))
    ext_media = len(re.findall(r'<(?:img|iframe|video|audio|source)\s+[^>]*src=["\']([^"\']+)["\']', cleaned_html, re.IGNORECASE))
    num_imports = ext_scripts + ext_links + ext_media

    dep_urls = set(re.findall(r'(?:src|href)=["\']([^"\']+)["\']', cleaned_html, re.IGNORECASE))
    cbo = len({u.split('?')[0].split('/')[-1] for u in dep_urls if u and not u.startswith('#')})

    # Embedded scripts
    script_blocks = re.findall(r'<script(?:\s+[^>]*)?>(.*?)</script>', cleaned_html, re.DOTALL | re.IGNORECASE)
    script_funcs = 0
    script_complexity = 0
    script_fn_lengths = []
    script_sec_issues = []
    script_nesting = 0

    for script_content in script_blocks:
        if script_content.strip():
            sm = calculate_javascript_metrics(script_content)
            script_funcs += sm["num_functions"]
            script_complexity += (sm["cyclomatic_complexity"] - 1)
            if sm["max_function_length"] > 0:
                script_fn_lengths.append(sm["max_function_length"])
            script_sec_issues.extend(sm["security_details"])
            script_nesting = max(script_nesting, sm["max_nesting_depth"])

    inline_handlers = len(re.findall(r'\bon[a-z]+\s*=\s*["\'][^"\']+["\']', cleaned_html, re.IGNORECASE))
    num_functions = script_funcs + inline_handlers

    if script_fn_lengths:
        avg_fn_len = round(sum(script_fn_lengths) / len(script_fn_lengths), 2)
        max_fn_len = max(script_fn_lengths)
    else:
        avg_fn_len = 0.0
        max_fn_len = 0

    # Semantic containers & components
    semantic_tags = len(re.findall(
        r'<(?:header|nav|main|section|article|footer|aside|form|template|dialog|table|fieldset)\b',
        cleaned_html,
        re.IGNORECASE
    ))
    class_attr_matches = re.findall(r'class=["\']([^"\']+)["\']', cleaned_html)
    unique_classes = set()
    for cm in class_attr_matches:
        unique_classes.update(cm.split())
    num_classes = semantic_tags + (len(unique_classes) if unique_classes else 0)

    # Complexity: interactive branch points + template conditionals + script branches
    interactive_elements = len(re.findall(
        r'<(?:input\s+[^>]*type=["\'](?:checkbox|radio|submit|button)["\']|select|option|details|dialog)\b',
        cleaned_html,
        re.IGNORECASE
    ))
    template_conditionals = len(re.findall(r'\{%\s*if\b|\bv-if\b|\*ngIf\b', cleaned_html, re.IGNORECASE))
    complexity = 1 + script_complexity + interactive_elements + template_conditionals

    dom_nesting = calculate_html_tag_nesting(source_code)
    nesting_depth = max(script_nesting, dom_nesting)

    # Security
    sec_issues = list(script_sec_issues)
    for a_tag in re.finditer(r'<a\s+([^>]+)>', cleaned_html, re.IGNORECASE):
        attrs = a_tag.group(1)
        if re.search(r'target=["\']_blank["\']', attrs, re.IGNORECASE):
            if not re.search(r'rel=["\'][^"\']*(?:noopener|noreferrer)', attrs, re.IGNORECASE):
                sec_issues.append("Reverse tabnabbing vulnerability (target=_blank without rel=noopener)")
                break
    if re.search(r'href=["\']javascript:', cleaned_html, re.IGNORECASE):
        sec_issues.append("Inline javascript: pseudo-protocol URL detected")
    if re.search(r'<form\s+[^>]*action=["\']http://', cleaned_html, re.IGNORECASE):
        sec_issues.append("Insecure plain HTTP form submission action")
    for input_tag in re.finditer(r'<input\s+([^>]+)>', cleaned_html, re.IGNORECASE):
        attrs = input_tag.group(1)
        if re.search(r'type=["\']password["\']', attrs, re.IGNORECASE):
            if re.search(r'value=["\'][^"\']+["\']', attrs, re.IGNORECASE):
                sec_issues.append("Hardcoded password value in input element")
                break
    if re.search(r'\bon[a-z]+\s*=\s*["\'][^"\']*eval\s*\(', cleaned_html, re.IGNORECASE):
        sec_issues.append("Dangerous dynamic code execution (eval) in event handler")

    unique_sec_issues = list(dict.fromkeys(sec_issues))

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
        "todo_count": count_todos(source_code),
        "fixme_count": count_fixmes(source_code),
        "coupling_between_objects": cbo,
        "lack_of_cohesion": 0.0,
        "code_churn": estimate_code_churn(source_code),
        "past_defects": count_past_defects(source_code),
        "security_vulnerabilities": len(unique_sec_issues),
        "security_details": unique_sec_issues,
    }


# ---------------------------------------------------------------------
# 3. CSS STATIC ANALYSIS
# ---------------------------------------------------------------------

def calculate_css_metrics(source_code):
    """
    Calculate software quality and architectural metrics for CSS stylesheets.
    """
    source_code = source_code or ""
    if not source_code.strip():
        return _empty_metrics(source_code)

    logical_lines, comment_density = analyze_c_style_lines(source_code)
    masked = mask_c_comments_and_strings(source_code, is_js=False)
    clean_code = strip_c_comments(source_code, is_js=False)

    # Functions: CSS functions + keyframe animations
    css_funcs = len(re.findall(r'\b(?:calc|var|rgba?|hsla?|linear-gradient|radial-gradient|min|max|clamp|url)\s*\(', clean_code))
    keyframes = re.findall(r'@keyframes\s+([a-zA-Z0-9_-]+)', clean_code)
    num_functions = css_funcs + len(keyframes)

    # Classes and rulesets
    unique_class_selectors = set(re.findall(r'\.([a-zA-Z_-][\w-]*)', masked))
    rule_blocks_count = len(re.findall(r'\{', masked))
    num_classes = len(unique_class_selectors) if unique_class_selectors else rule_blocks_count

    # Imports and dependencies
    import_matches = re.findall(r'@import\s+(?:url\([\'"]?([^"\'\)]+)[\'"]?\)|[\'"]([^\'"]+)[\'"])', clean_code)
    ext_urls = re.findall(r'url\([\'"]?([^"\'\)]+)[\'"]?\)', clean_code)
    num_imports = len(import_matches) + len(ext_urls)

    all_refs = {m[0] or m[1] for m in import_matches} | set(ext_urls)
    cbo = len({ref.split('?')[0].split('/')[-1] for ref in all_refs if ref and not ref.startswith('data:')})

    # Cyclomatic complexity: responsive & conditional branches
    media_queries = len(re.findall(r'@media\b', masked))
    supports_queries = len(re.findall(r'@supports\b', masked))
    container_queries = len(re.findall(r'@container\b', masked))
    pseudo_classes = len(re.findall(r':(?:hover|focus|active|disabled|checked|nth-child|not|is|has)\b', masked))
    complexity = 1 + media_queries + supports_queries + container_queries + pseudo_classes

    # Nesting depth: maximum brace depth
    max_depth = 0
    curr_depth = 0
    for char in masked:
        if char == '{':
            curr_depth += 1
            if curr_depth > max_depth:
                max_depth = curr_depth
        elif char == '}':
            if curr_depth > 0:
                curr_depth -= 1
    nesting_depth = max_depth

    # Rule block lengths
    rule_lengths = []
    for m in re.finditer(r'\{', masked):
        start_idx = m.start()
        end_idx = find_matching_brace(masked, start_idx)
        start_line = source_code[:start_idx].count('\n') + 1
        end_line = source_code[:end_idx + 1].count('\n') + 1
        rule_lengths.append(max(1, end_line - start_line + 1))

    if rule_lengths:
        avg_fn_len = round(sum(rule_lengths) / len(rule_lengths), 2)
        max_fn_len = max(rule_lengths)
    else:
        avg_fn_len = 0.0
        max_fn_len = 0

    # Security
    sec_issues = []
    if re.search(r'expression\s*\(', clean_code, re.IGNORECASE):
        sec_issues.append("Dynamic CSS expression execution vulnerability (expression())")
    if re.search(r'url\s*\(\s*[\'"]?javascript:', clean_code, re.IGNORECASE):
        sec_issues.append("CSS injection via javascript: pseudo-protocol in url()")
    if re.search(r'@import\s+(?:url\([\'"]?http://|[\'"]http://)', clean_code, re.IGNORECASE):
        sec_issues.append("Insecure stylesheet import via unencrypted HTTP")

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
        "todo_count": count_todos(source_code),
        "fixme_count": count_fixmes(source_code),
        "coupling_between_objects": cbo,
        "lack_of_cohesion": 0.0,
        "code_churn": estimate_code_churn(source_code),
        "past_defects": count_past_defects(source_code),
        "security_vulnerabilities": len(sec_issues),
        "security_details": sec_issues,
    }


# ---------------------------------------------------------------------
# 4. JAVA STATIC ANALYSIS
# ---------------------------------------------------------------------

def calculate_java_metrics(source_code):
    """
    Calculate software quality and testing metrics for Java source code.
    """
    source_code = source_code or ""
    if not source_code.strip():
        return _empty_metrics(source_code)

    logical_lines, comment_density = analyze_c_style_lines(source_code)
    masked = mask_c_comments_and_strings(source_code, is_js=False)
    clean_code = strip_c_comments(source_code, is_js=False)

    classes = set(re.findall(r'\b(?:class|interface|enum|record)\s+([a-zA-Z_$][\w$]*)', masked))
    num_classes = len(classes)

    exclude_keywords = {
        'if', 'for', 'while', 'switch', 'catch', 'synchronized',
        'return', 'throw', 'new', 'assert', 'else', 'do', 'try', 'finally',
        'class', 'interface', 'enum', 'record'
    }

    ctor_pattern = re.compile(
        r'(?<![.\w$])(?:@[\w.]+(?:\([^)]*\))?\s+)*(?:(?:public|protected|private)\s+)?([A-Z][\w$]*)\s*\([^;{}]*\)\s*(?:throws\s+[\w.,\s]+)?\s*\{'
    )
    method_pattern = re.compile(
        r'(?<![.\w$])(?:@[\w.]+(?:\([^)]*\))?\s+)*(?:(?:public|protected|private|static|final|synchronized|abstract|default|native)\s+)*[\w<>\[\],\s]+\s+([a-zA-Z_$][\w$]*)\s*\([^;{}]*\)\s*(?:throws\s+[\w.,\s]+)?\s*\{'
    )

    func_spans = []
    seen = set()

    for m in ctor_pattern.finditer(masked):
        name = m.group(1)
        if name in classes:
            start = m.start()
            brace_pos = masked.find('{', m.end() - 1)
            if brace_pos != -1:
                end = find_matching_brace(masked, brace_pos)
                seen.add(start)
                func_spans.append((start, end))

    for m in method_pattern.finditer(masked):
        name = m.group(1)
        if name in exclude_keywords or name in classes:
            continue
        start = m.start()
        if any(abs(start - s) < 15 for s in seen):
            continue
        brace_pos = masked.find('{', m.end() - 1)
        if brace_pos != -1:
            end = find_matching_brace(masked, brace_pos)
            seen.add(start)
            func_spans.append((start, end))

    lengths = []
    for s, e in func_spans:
        start_line = source_code[:s].count('\n') + 1
        end_line = source_code[:e + 1].count('\n') + 1
        lengths.append(max(1, end_line - start_line + 1))

    num_functions = len(func_spans)
    avg_fn_len = round(sum(lengths) / len(lengths), 2) if lengths else 0.0
    max_fn_len = max(lengths) if lengths else 0

    imports = re.findall(r'\bimport\s+(?:static\s+)?([\w\.\*]+);', clean_code)
    num_imports = len(imports)

    instantiations = set(re.findall(r'\bnew\s+([A-Z][\w$]*)', masked))
    imported_types = {imp.split('.')[-1] for imp in imports}
    cbo = len(imported_types | instantiations)

    complexity = 1
    complexity += len(re.findall(r'\b(?:if|for|while|case|catch)\b', masked))
    complexity += len(re.findall(r'&&|\|\|', masked))
    complexity += len(re.findall(r'(?<!\?)\?(?!\.|\?)', masked))

    nesting_depth = calculate_c_nesting_depth(masked)

    sec_issues = []
    if re.search(r'Runtime\.getRuntime\(\)\.exec|\bProcessBuilder\b', clean_code):
        sec_issues.append("Dangerous system command execution (Runtime.exec / ProcessBuilder)")
    if re.search(r'(?:executeQuery|executeUpdate|execute)\s*\(\s*["\'].*?\+', clean_code):
        sec_issues.append("Possible SQL Injection via string concatenation in JDBC statement")
    if re.search(r'MessageDigest\.getInstance\s*\(\s*["\'](?:MD5|SHA-1)["\']', clean_code, re.IGNORECASE):
        sec_issues.append("Weak cryptographic hash algorithm (MD5/SHA-1)")
    if re.search(r'Cipher\.getInstance\s*\(\s*["\']DES["\']', clean_code, re.IGNORECASE):
        sec_issues.append("Insecure cipher algorithm (DES)")
    secret_pattern = re.compile(
        r"""(?i)(?:api_key|secret_key|password|auth_token|access_token|private_key)\s*=\s*['"][a-zA-Z0-9_\-\.]{8,}['"]"""
    )
    if secret_pattern.search(clean_code):
        sec_issues.append("Potential hardcoded credential or secret key detected")

    unique_sec_issues = list(dict.fromkeys(sec_issues))

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
        "todo_count": count_todos(source_code),
        "fixme_count": count_fixmes(source_code),
        "coupling_between_objects": cbo,
        "lack_of_cohesion": 0.0,
        "code_churn": estimate_code_churn(source_code),
        "past_defects": count_past_defects(source_code),
        "security_vulnerabilities": len(unique_sec_issues),
        "security_details": unique_sec_issues,
    }


# ---------------------------------------------------------------------
# 5. C AND C++ STATIC ANALYSIS
# ---------------------------------------------------------------------

def calculate_c_or_cpp_metrics(source_code, is_cpp=False):
    """
    Calculate software quality and testing metrics for C or C++ source code.
    """
    source_code = source_code or ""
    if not source_code.strip():
        return _empty_metrics(source_code)

    logical_lines, comment_density = analyze_c_style_lines(source_code)
    masked = mask_c_comments_and_strings(source_code, is_js=False)
    clean_code = strip_c_comments(source_code, is_js=False)

    classes = set(re.findall(r'\b(?:class|struct|union|namespace)\s+([a-zA-Z_]\w*)', masked))
    num_classes = len(classes)

    func_pattern = re.compile(
        r'(?<![.\w])(?:(?:inline|static|virtual|explicit|extern|constexpr|const|volatile|friend)\s+)*'
        r'(?:(?:struct|class|union|enum)\s+)?'
        r'(?:[\w:*&<>]+\s+)*[*&]*\s*'
        r'([a-zA-Z_~]\w*(?:::~?[a-zA-Z_]\w*)*(?:::operator\s*(?:[+\-*/%^&|~!=<>,]+|\[\]|\(\)|->\*?|<=>))?|operator\s*(?:[+\-*/%^&|~!=<>,]+|\[\]|\(\)|->\*?|<=>))\s*'
        r'\([^;{}]*\)\s*'
        r'(?:(?:const|noexcept(?:\s*\([^)]*\))?|override|final)\s*)*'
        r'(?:->\s*[\w:*&<>]+\s*)?'
        r'(?::\s*[^{;]+)?'
        r'\{'
    )
    exclude_keywords = {
        'if', 'for', 'while', 'switch', 'catch', 'do', 'else',
        'struct', 'class', 'union', 'enum', 'return', 'sizeof',
        'throw', 'new', 'delete'
    }

    func_spans = []
    seen = set()

    for m in func_pattern.finditer(masked):
        raw_name = m.group(1).split("::")[-1].lstrip("~")
        if raw_name in exclude_keywords or not raw_name:
            continue
        start = m.start()
        if any(abs(start - s) < 10 for s in seen):
            continue
        brace_pos = masked.find('{', m.end() - 1)
        if brace_pos != -1:
            end = find_matching_brace(masked, brace_pos)
            seen.add(start)
            func_spans.append((start, end))

    lengths = []
    for s, e in func_spans:
        start_line = source_code[:s].count('\n') + 1
        end_line = source_code[:e + 1].count('\n') + 1
        lengths.append(max(1, end_line - start_line + 1))

    num_functions = len(func_spans)
    avg_fn_len = round(sum(lengths) / len(lengths), 2) if lengths else 0.0
    max_fn_len = max(lengths) if lengths else 0

    includes = re.findall(r'#\s*include\s*([<"][^>"]+[>"])', clean_code)
    cpp_modules = re.findall(r'\bimport\s+[\w\.]+;', masked) if is_cpp else []
    num_imports = len(includes) + len(cpp_modules)

    headers = {inc.strip('<>"') for inc in includes}
    cbo = len(headers | classes)

    complexity = 1
    complexity += len(re.findall(r'\b(?:if|for|while|case|catch)\b', masked))
    complexity += len(re.findall(r'&&|\|\|', masked))
    complexity += len(re.findall(r'(?<!\?)\?(?!\.|\?)', masked))

    nesting_depth = calculate_c_nesting_depth(masked)

    sec_issues = []
    if re.search(r'\bgets\s*\(', clean_code):
        sec_issues.append("Critical buffer overflow vulnerability (gets() function is obsolete and unsafe)")
    if re.search(r'\bstrcpy\s*\(', clean_code):
        sec_issues.append("Unbounded memory copy (strcpy risk; prefer strncpy or strlcpy)")
    if re.search(r'\bstrcat\s*\(', clean_code):
        sec_issues.append("Unbounded string concatenation (strcat risk)")
    if re.search(r'\bsprintf\s*\(', clean_code):
        sec_issues.append("Unbounded string formatting (sprintf risk; prefer snprintf)")
    if re.search(r'\bvsprintf\s*\(', clean_code):
        sec_issues.append("Unbounded varargs formatting (vsprintf risk; prefer vsnprintf)")
    if re.search(r'\bsystem\s*\(', clean_code):
        sec_issues.append("Insecure command execution via system()")
    if re.search(r'scanf\s*\(\s*["\'][^"\']*%s', clean_code):
        sec_issues.append("Unbounded format specifier (%s in scanf without width specifier)")
    secret_pattern = re.compile(
        r"""(?i)(?:api_key|secret_key|password|auth_token|access_token|private_key)\s*=\s*['"][a-zA-Z0-9_\-\.]{8,}['"]"""
    )
    if secret_pattern.search(clean_code):
        sec_issues.append("Potential hardcoded credential or secret key detected")

    unique_sec_issues = list(dict.fromkeys(sec_issues))

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
        "todo_count": count_todos(source_code),
        "fixme_count": count_fixmes(source_code),
        "coupling_between_objects": cbo,
        "lack_of_cohesion": 0.0,
        "code_churn": estimate_code_churn(source_code),
        "past_defects": count_past_defects(source_code),
        "security_vulnerabilities": len(unique_sec_issues),
        "security_details": unique_sec_issues,
    }


def calculate_c_metrics(source_code):
    """Calculate software quality metrics for C source code."""
    return calculate_c_or_cpp_metrics(source_code, is_cpp=False)


def calculate_cpp_metrics(source_code):
    """Calculate software quality metrics for C++ source code."""
    return calculate_c_or_cpp_metrics(source_code, is_cpp=True)


# ---------------------------------------------------------------------
# 6. UNIVERSAL METRIC DISPATCHER
# ---------------------------------------------------------------------

def calculate_generic_metrics(source_code):
    """Fallback metric calculation for unsupported or plain text source files."""
    source_code = source_code or ""
    lines = source_code.splitlines()
    code_lines = [l for l in lines if l.strip()]
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
        "todo_count": count_todos(source_code),
        "fixme_count": count_fixmes(source_code),
        "coupling_between_objects": 0,
        "lack_of_cohesion": 0.0,
        "code_churn": estimate_code_churn(source_code),
        "past_defects": count_past_defects(source_code),
        "security_vulnerabilities": 0,
        "security_details": [],
    }


def calculate_metrics_for_file(source_code, extension):
    """
    Dispatch static analysis and metric extraction for any supported language.
    Supports Python, JavaScript, HTML, CSS, Java, C, and C++.
    """
    ext = (extension or "").lower()
    if ext == ".py":
        return calculate_python_metrics(source_code)
    elif ext == ".js":
        return calculate_javascript_metrics(source_code)
    elif ext in (".html", ".htm"):
        return calculate_html_metrics(source_code)
    elif ext == ".css":
        return calculate_css_metrics(source_code)
    elif ext == ".java":
        return calculate_java_metrics(source_code)
    elif ext in (".c", ".h"):
        return calculate_c_metrics(source_code)
    elif ext in (".cpp", ".hpp", ".cc", ".cxx", ".hh", ".hxx"):
        return calculate_cpp_metrics(source_code)
    else:
        return calculate_generic_metrics(source_code)