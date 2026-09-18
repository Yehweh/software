import os
import pytest
from flask import render_template

from app import app, calculate_project_metrics
from src.code_metrics import (
    calculate_python_metrics,
    calculate_javascript_metrics,
    calculate_html_metrics,
    calculate_css_metrics,
    calculate_java_metrics,
    calculate_c_metrics,
    calculate_cpp_metrics,
    calculate_metrics_for_file,
)
from src.technical_debt_engine import calculate_technical_debt
from src.project_analyzer import analyze_project


# =====================================================================
# 1. JAVASCRIPT METRICS EXTRACTION TESTS
# =====================================================================

def test_javascript_metrics_extraction():
    """Verify JavaScript metric extraction for functions, imports, comments, and complexity."""
    js_code = """
    // Configuration import
    const config = require('./config');
    import { Router } from 'express';
    import authService from './authService';

    /*
     * Main Controller class
     */
    class UserController {
        constructor() {
            this.router = Router();
        }

        async getUser(req, res) {
            if (req.params.id) {
                const user = await authService.find(req.params.id);
                return res.json(user);
            } else {
                return res.status(400).send('Missing ID');
            }
        }
    }

    const helper = (val) => {
        return val ? val.trim() : '';
    };

    // TODO: implement caching
    // FIXME: fix race condition
    module.exports = UserController;
    """
    metrics = calculate_javascript_metrics(js_code)

    assert metrics["lines_of_code"] > 10
    assert metrics["comment_density"] > 0
    # Functions: constructor, getUser, helper arrow function
    assert metrics["num_functions"] >= 2
    # Classes: UserController
    assert metrics["num_classes"] >= 1
    # Imports: require('./config'), import { Router }, import authService
    assert metrics["num_imports"] == 3
    # Cyclomatic complexity: if/else, ternary
    assert metrics["cyclomatic_complexity"] >= 3
    # Nesting depth: if inside method
    assert metrics["max_nesting_depth"] >= 1
    # TODO and FIXME
    assert metrics["todo_count"] == 1
    assert metrics["fixme_count"] == 1
    # Function length
    assert metrics["max_function_length"] > 0
    assert metrics["avg_function_length"] > 0


def test_javascript_security_vulnerabilities():
    """Verify detection of JavaScript security vulnerabilities like eval and innerHTML."""
    insecure_js = """
    function renderContent(userInput) {
        eval(userInput);
        document.write("<div>" + userInput + "</div>");
        element.innerHTML = userInput;
        const api_key = "secret_key_123456789";
    }
    """
    metrics = calculate_javascript_metrics(insecure_js)
    assert metrics["security_vulnerabilities"] >= 3
    assert any("eval" in issue for issue in metrics["security_details"])
    assert any("innerHTML" in issue for issue in metrics["security_details"])
    assert any("document.write" in issue for issue in metrics["security_details"])


# =====================================================================
# 2. HTML METRICS EXTRACTION TESTS
# =====================================================================

def test_html_metrics_extraction():
    """Verify HTML metric extraction for structure, scripts, links, and forms."""
    html_code = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <!-- Page metadata and dependencies -->
        <meta charset="UTF-8">
        <link rel="stylesheet" href="style.css">
        <script src="app.js"></script>
        <title>Dashboard</title>
    </head>
    <body>
        <!-- Header Section -->
        <header>
            <nav class="navbar main-nav">
                <a href="/">Home</a>
            </nav>
        </header>

        <main>
            <section class="card profile-card">
                <h2>User Profile</h2>
                <form action="submit" method="POST">
                    <input type="checkbox" name="agree">
                    <select name="role">
                        <option value="user">User</option>
                        <option value="admin">Admin</option>
                    </select>
                    <button type="submit" onclick="handleClick()">Submit</button>
                </form>
            </section>
        </main>

        <script>
            function handleClick() {
                if (window.confirm("Sure?")) {
                    console.log("Submitted");
                }
            }
        </script>
    </body>
    </html>
    """
    metrics = calculate_html_metrics(html_code)

    assert metrics["lines_of_code"] > 20
    assert metrics["comment_density"] > 0
    # Functions: embedded handleClick() + inline onclick
    assert metrics["num_functions"] >= 1
    # Semantic containers / classes
    assert metrics["num_classes"] >= 4
    # Imports: link, script src
    assert metrics["num_imports"] >= 2
    # Complexity: interactive form controls + script if
    assert metrics["cyclomatic_complexity"] >= 3
    # DOM nesting depth
    assert metrics["max_nesting_depth"] >= 3


# =====================================================================
# 3. CSS METRICS EXTRACTION TESTS
# =====================================================================

def test_css_metrics_extraction():
    """Verify CSS metric extraction for rulesets, functional notation, responsive branching."""
    css_code = """
    /* Theme Stylesheet */
    @import url("https://fonts.googleapis.com/css?family=Inter");

    :root {
        --primary-color: #3b82f6;
        --card-bg: rgba(255, 255, 255, 0.9);
    }

    /* Base layout */
    .container {
        width: 100%;
        max-width: 1200px;
        background-color: var(--card-bg);
    }

    .btn {
        padding: calc(8px + 2px);
        background: var(--primary-color);
        transition: all 0.3s ease;
    }

    .btn:hover {
        opacity: 0.85;
    }

    .btn:focus {
        outline: 2px solid #2563eb;
    }

    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }

    @media (max-width: 768px) {
        .container {
            padding: 10px;
        }
        .btn {
            width: 100%;
        }
    }
    """
    metrics = calculate_css_metrics(css_code)

    assert metrics["lines_of_code"] > 20
    assert metrics["comment_density"] > 0
    # CSS functions: var, calc, rgba, keyframes
    assert metrics["num_functions"] >= 4
    # Classes: .container, .btn
    assert metrics["num_classes"] >= 2
    # Imports: @import
    assert metrics["num_imports"] >= 1
    # Cyclomatic complexity: @media + pseudo-classes :hover, :focus
    assert metrics["cyclomatic_complexity"] >= 3
    # Nesting depth: @media { .selector { ... } }
    assert metrics["max_nesting_depth"] >= 2


# =====================================================================
# 4. JAVA METRICS EXTRACTION TESTS
# =====================================================================

def test_java_metrics_extraction():
    """Verify Java metric extraction for classes, methods, imports, and complexity."""
    java_code = """
    package com.example.service;

    // Standard imports
    import java.util.List;
    import java.util.ArrayList;
    import java.io.IOException;

    /*
     * Account Service implementation
     */
    public class AccountService {
        private List<String> accounts;

        public AccountService() {
            this.accounts = new ArrayList<>();
        }

        public boolean processTransaction(String id, double amount) {
            if (amount <= 0) {
                return false;
            }
            for (String account : accounts) {
                if (account.equals(id)) {
                    return true;
                }
            }
            return false;
        }

        // TODO: add database persistence
    }
    """
    metrics = calculate_java_metrics(java_code)

    assert metrics["lines_of_code"] > 15
    assert metrics["comment_density"] > 0
    # Classes: AccountService
    assert metrics["num_classes"] >= 1
    # Methods: constructor + processTransaction
    assert metrics["num_functions"] >= 2
    # Imports: 3 imports + package
    assert metrics["num_imports"] >= 3
    # Complexity: if, for, nested if
    assert metrics["cyclomatic_complexity"] >= 3
    # Nesting depth: for inside method, if inside for
    assert metrics["max_nesting_depth"] >= 2
    # TODO
    assert metrics["todo_count"] == 1


# =====================================================================
# 5. C AND C++ METRICS EXTRACTION TESTS
# =====================================================================

def test_c_and_cpp_metrics_extraction():
    """Verify C and C++ metric extraction for functions, structs/classes, includes, and security."""
    c_code = """
    #include <stdio.h>
    #include <stdlib.h>
    #include <string.h>

    // Buffer structure
    struct DataBuffer {
        char *data;
        int size;
    };

    int process_buffer(struct DataBuffer *buf) {
        if (!buf || buf->size <= 0) {
            return -1;
        }
        for (int i = 0; i < buf->size; i++) {
            if (buf->data[i] == '\\0') {
                break;
            }
        }
        return 0;
    }

    int main() {
        struct DataBuffer buf;
        buf.size = 10;
        return process_buffer(&buf);
    }
    """
    c_metrics = calculate_c_metrics(c_code)
    assert c_metrics["lines_of_code"] > 15
    assert c_metrics["comment_density"] > 0
    assert c_metrics["num_functions"] >= 2
    assert c_metrics["num_classes"] >= 1  # DataBuffer struct
    assert c_metrics["num_imports"] >= 3  # stdio, stdlib, string
    assert c_metrics["cyclomatic_complexity"] >= 3

    # C security checks
    insecure_c = """
    #include <stdio.h>
    #include <string.h>

    void vulnerable(char *input) {
        char buf[64];
        gets(buf);
        strcpy(buf, input);
        system(buf);
    }
    """
    sec_metrics = calculate_c_metrics(insecure_c)
    assert sec_metrics["security_vulnerabilities"] >= 3
    assert any("gets" in s for s in sec_metrics["security_details"])
    assert any("strcpy" in s for s in sec_metrics["security_details"])
    assert any("system" in s for s in sec_metrics["security_details"])


# =====================================================================
# 6. UNIVERSAL DISPATCHER & TECHNICAL DEBT ENGINE INTEGRATION
# =====================================================================

def test_universal_dispatcher_all_languages():
    """Verify calculate_metrics_for_file correctly dispatches to each language parser."""
    extensions = [".py", ".js", ".html", ".css", ".java", ".c", ".h", ".cpp", ".hpp"]
    for ext in extensions:
        m = calculate_metrics_for_file("// test comment\nint x = 1;", ext)
        assert isinstance(m, dict)
        assert "lines_of_code" in m
        assert "cyclomatic_complexity" in m
        assert "num_functions" in m
        assert "num_classes" in m
        assert "num_imports" in m
        assert "comment_density" in m


def test_technical_debt_evaluation_multi_language():
    """Verify technical debt engine computes scores and risk tiers for multi-language metrics."""
    # High debt JS metrics
    high_debt_js = {
        "cyclomatic_complexity": 25,     # > 20 -> +20
        "max_function_length": 60,       # > 50 -> +15
        "max_nesting_depth": 6,          # > 5 -> +15
        "lines_of_code": 100,
        "comment_density": 2.0,          # < 5 -> +10
        "todo_count": 6,                 # >= 5 -> +10
        "fixme_count": 4,                # >= 3 -> +10
        "coupling_between_objects": 22,  # > 20 -> +20
        "lack_of_cohesion": 0.0,
        "security_vulnerabilities": 2,   # > 0 -> +20
        "past_defects": 1,               # > 0 -> +5
        "code_churn": 12,                # >= 10 -> +10
    }
    debt = calculate_technical_debt(high_debt_js)
    assert debt["score"] >= 61
    assert debt["level"] == "High Technical Debt"
    assert "High Cyclomatic Complexity" in debt["reasons"]
    assert "Very Long Function" in debt["reasons"]
    assert "Deeply Nested Code" in debt["reasons"]
    assert "Low Comment Density" in debt["reasons"]

    # Low debt clean CSS metrics
    clean_css = {
        "cyclomatic_complexity": 3,
        "max_function_length": 15,
        "max_nesting_depth": 1,
        "lines_of_code": 50,
        "comment_density": 15.0,
        "todo_count": 0,
        "fixme_count": 0,
        "coupling_between_objects": 2,
        "lack_of_cohesion": 0.0,
        "security_vulnerabilities": 0,
        "past_defects": 0,
        "code_churn": 0,
    }
    clean_debt = calculate_technical_debt(clean_css)
    assert clean_debt["score"] <= 30
    assert clean_debt["level"] == "Low Technical Debt"


# =====================================================================
# 7. REAL-WORLD PROJECT ANALYSIS & DASHBOARD INTEGRATION
# =====================================================================

def _ensure_turf_booking_zip():
    zip_path = os.path.join("uploads", "turf-booking.zip")
    if not os.path.exists(zip_path):
        alt = "F:/turf-booking.zip"
        if os.path.exists(alt):
            import shutil
            os.makedirs("uploads", exist_ok=True)
            shutil.copy(alt, zip_path)
    return zip_path


def test_turf_booking_project_analysis_and_aggregation():
    """Verify that uploading turf-booking.zip extracts real metrics and populated debt assessments."""
    zip_path = _ensure_turf_booking_zip()
    if not os.path.exists(zip_path):
        pytest.skip("uploads/turf-booking.zip not available")

    analysis = analyze_project(zip_path)
    assert analysis["file_count"] == 11
    assert analysis["total_lines"] > 0

    # Ensure every single file has non-None metrics and technical_debt
    for file_info in analysis["files"]:
        assert file_info["metrics"] is not None, f"Metrics missing for {file_info['name']}"
        assert file_info["technical_debt"] is not None, f"Debt missing for {file_info['name']}"
        assert file_info["language"] in ("JavaScript", "HTML", "CSS"), f"Unexpected lang: {file_info['language']}"
        assert file_info["lines"] > 0
        assert file_info["technical_debt"]["level"] in (
            "Low Technical Debt", "Medium Technical Debt", "High Technical Debt"
        )
        assert len(file_info["technical_debt"]["reasons"]) > 0

    # Project-level aggregation
    pm = calculate_project_metrics(analysis)

    assert pm["total_files"] == 11
    assert pm["analyzed_files"] == 11
    assert pm["total_lines"] > 3000
    assert pm["total_functions"] > 0
    assert pm["total_classes"] > 0
    assert pm["total_imports"] > 0
    assert pm["average_comment_density"] > 0
    assert pm["cyclomatic_complexity"] > 0
    assert pm["max_nesting_depth"] > 0
    assert pm["average_debt_score"] > 0
    assert pm["high_debt"] + pm["medium_debt"] + pm["low_debt"] == 11
    assert pm["language_count"] >= 3


def test_dashboard_template_rendering_turf_booking():
    """Verify that rendering index.html produces no dashes ('—') or 'Language analysis pending'."""
    zip_path = _ensure_turf_booking_zip()
    if not os.path.exists(zip_path):
        pytest.skip("uploads/turf-booking.zip not available")

    analysis = analyze_project(zip_path)
    project_metrics = calculate_project_metrics(analysis)

    with app.test_request_context("/"):
        html = render_template(
            "index.html",
            project=analysis,
            project_metrics=project_metrics,
            results=[],
            high=0,
            medium=0,
            low=0
        )

    # Ensure placeholder tags are not present in rendered HTML
    assert "Language analysis pending" not in html
    assert "NOT ANALYZED" not in html

    # Ensure no placeholder dashes in fileResultsTable rows
    import re
    table_match = re.search(r'<table id="fileResultsTable">(.*?)</table>', html, re.DOTALL)
    assert table_match is not None
    table_html = table_match.group(1)
    assert "—" not in table_html
    assert "Language analysis pending" not in table_html
    assert "NOT ANALYZED" not in table_html

    # Check that overview cards render real numbers
    assert f"{project_metrics['average_debt_score']}" in html
    assert f"{project_metrics['analyzed_files']} Files Analysed" in html
    # File table rows should contain risk badges
    assert "risk-high" in html or "risk-medium" in html or "risk-low" in html


def test_empty_and_whitespace_files():
    """Ensure empty or whitespace-only files return valid zeroed metrics without errors."""
    for ext in [".js", ".html", ".css", ".java", ".c", ".cpp"]:
        m = calculate_metrics_for_file("   \n\t  \n", ext)
        assert m["lines_of_code"] == 0
        assert m["comment_density"] == 0.0
        assert m["num_functions"] == 0
        assert m["cyclomatic_complexity"] == 1
        debt = calculate_technical_debt(m)
        assert debt["score"] == 0
        assert debt["level"] == "Low Technical Debt"


def test_full_upload_workflow_end_to_end():
    """Test full HTTP upload route /upload-project and verify dashboard rendering."""
    zip_path = _ensure_turf_booking_zip()
    if not os.path.exists(zip_path):
        pytest.skip("uploads/turf-booking.zip not available")

    app.config["TESTING"] = True
    with app.test_client() as client:
        with client.session_transaction() as sess:
            sess["user_id"] = 1
            sess["username"] = "TestUser"

        with open(zip_path, "rb") as zf:
            response = client.post(
                "/upload-project",
                data={"project_file": (zf, "turf-booking.zip")},
                content_type="multipart/form-data",
                follow_redirects=True
            )

        assert response.status_code == 200
        html = response.get_data(as_text=True)

        assert "Language analysis pending" not in html
        assert "NOT ANALYZED" not in html
        assert "Project Debt Assessment" in html
        assert "File-Level Debt Assessment" in html
        assert "risk-badge" in html


# =====================================================================
# 8. ADVERSARIAL EDGE CASE TESTS
# =====================================================================

def test_javascript_async_dedup_and_constructor():
    """Verify that async functions are not double-counted and class constructors are captured."""
    js = """
    class Service {
        constructor() {
            this.active = true;
        }
        async fetchData() {
            return true;
        }
    }
    async function globalAsync() {
        return 42;
    }
    export async function exportedAsync() {
        return 100;
    }
    """
    m = calculate_javascript_metrics(js)
    # constructor + fetchData + globalAsync + exportedAsync = exactly 4
    assert m["num_functions"] == 4
    assert m["num_classes"] == 1


def test_java_package_private_and_annotated_methods():
    """Verify package-private constructors, methods, and annotated methods are extracted in Java."""
    java = """
    package com.example;

    public class Engine {
        Engine() {
            this.state = 0;
        }
        public Engine(int state) {
            this.state = state;
        }
        void process() {
            state++;
        }
        @Override
        public String toString() {
            return "Engine";
        }
        @Test
        void testEngine() {
            assert state == 0;
        }
    }
    """
    m = calculate_java_metrics(java)
    # 2 ctors (1 package-private, 1 public) + 3 methods (1 package-private, 1 public, 1 annotated)
    assert m["num_functions"] == 5
    assert m["num_classes"] == 1


def test_c_and_cpp_pointer_returns_and_ctor_initializers():
    """Verify C/C++ pointer return types (* attached to name) and C++ initializer lists."""
    c_code = """
    char *get_name() { return "test"; }
    char **get_matrix() { return NULL; }
    const char *get_const() { return ""; }
    int plain() { return 1; }
    """
    c_m = calculate_c_metrics(c_code)
    assert c_m["num_functions"] == 4

    cpp_code = """
    class Widget {
    public:
        Widget() : count(0), name("default") {
            init();
        }
        Widget(int x) {
            count = x;
        }
        ~Widget() {
            cleanup();
        }
        void init() { }
        void cleanup() noexcept { }
    };
    """
    cpp_m = calculate_cpp_metrics(cpp_code)
    # 2 ctors + 1 dtor + 2 methods = 5
    assert cpp_m["num_functions"] == 5
    assert cpp_m["num_classes"] == 1


def test_comment_density_with_embedded_urls():
    """Verify that URL strings (http://, https://) are not misclassified as comment lines."""
    code = """
    const api1 = "https://api.example.com/v1";
    const api2 = "http://localhost:8080/data";
    function callApi() {
        return fetch(api1);
    }
    """
    m = calculate_javascript_metrics(code)
    # 0 comment lines in the code above
    assert m["comment_density"] == 0.0


def test_html_tabnabbing_attribute_order_and_svg_nesting():
    """Verify rel before target=_blank is not flagged as tabnabbing, and self-closing tags don't inflate depth."""
    html = """
    <!DOCTYPE html>
    <html>
    <body>
        <a rel="noopener" target="_blank" href="https://example.com">Safe Link</a>
        <div>
            <svg viewBox="0 0 100 100">
                <path d="M10 10" />
                <circle cx="20" cy="20" r="5" />
            </svg>
        </div>
    </body>
    </html>
    """
    m = calculate_html_metrics(html)
    assert not any("Reverse tabnabbing" in issue for issue in m["security_details"])
    # DOM nesting: html -> body -> div -> svg = 4 (self-closing path/circle should not push to 6)
    assert m["max_nesting_depth"] <= 4


def test_project_metrics_language_count_python_vs_multilang():
    """Verify calculate_project_metrics does not double-count languages with file extensions."""
    # Pure Python project
    py_project = {
        "project_id": "test_py",
        "files": [
            {
                "name": "app.py",
                "path": "app.py",
                "extension": ".py",
                "language": "Python",
                "lines": 50,
                "metrics": calculate_metrics_for_file("def hello(): pass", ".py"),
                "technical_debt": {"score": 10, "level": "Low Technical Debt", "reasons": ["OK"]}
            },
            {
                "name": "utils.py",
                "path": "utils.py",
                "extension": ".py",
                "language": "Python",
                "lines": 30,
                "metrics": calculate_metrics_for_file("def util(): pass", ".py"),
                "technical_debt": {"score": 10, "level": "Low Technical Debt", "reasons": ["OK"]}
            }
        ]
    }
    pm_py = calculate_project_metrics(py_project)
    assert pm_py["language_count"] == 1
    assert pm_py["languages"] == ["Python"]
    assert pm_py["python_files"] == 2

    # Multi-language project (HTML, CSS, JS)
    multi_project = {
        "project_id": "test_multi",
        "files": [
            {
                "name": "index.html",
                "path": "index.html",
                "extension": ".html",
                "language": "HTML",
                "lines": 20,
                "metrics": calculate_metrics_for_file("<html></html>", ".html"),
                "technical_debt": {"score": 5, "level": "Low Technical Debt", "reasons": ["OK"]}
            },
            {
                "name": "style.css",
                "path": "style.css",
                "extension": ".css",
                "language": "CSS",
                "lines": 20,
                "metrics": calculate_metrics_for_file(".a { color: red; }", ".css"),
                "technical_debt": {"score": 5, "level": "Low Technical Debt", "reasons": ["OK"]}
            },
            {
                "name": "main.js",
                "path": "main.js",
                "extension": ".js",
                "language": "JavaScript",
                "lines": 20,
                "metrics": calculate_metrics_for_file("function run() {}", ".js"),
                "technical_debt": {"score": 5, "level": "Low Technical Debt", "reasons": ["OK"]}
            }
        ]
    }
    pm_multi = calculate_project_metrics(multi_project)
    assert pm_multi["language_count"] == 3
    assert pm_multi["languages"] == ["CSS", "HTML", "JavaScript"]


def test_none_and_null_inputs_graceful_handling():
    """Verify all language analyzers and technical debt engine safely handle None inputs."""
    for ext in [".py", ".js", ".html", ".css", ".java", ".c", ".h", ".cpp", ".hpp"]:
        m = calculate_metrics_for_file(None, ext)
        assert isinstance(m, dict)
        assert m["lines_of_code"] == 0
        assert m["num_functions"] == 0

    debt = calculate_technical_debt(None)
    assert isinstance(debt, dict)
    assert debt["score"] == 0
    assert debt["level"] == "Low Technical Debt"


def test_dashboard_template_rendering_pure_python_project():
    """Verify that a single-language Python project displays 'Python Files' with 🐍 in the overview card."""
    py_analysis = {
        "project_id": "py_single",
        "file_count": 2,
        "total_lines": 80,
        "files": [
            {
                "name": "main.py",
                "path": "main.py",
                "extension": ".py",
                "language": "Python",
                "lines": 50,
                "metrics": calculate_metrics_for_file("def hello(): pass", ".py"),
                "technical_debt": {"score": 10, "level": "Low Technical Debt", "reasons": ["Software quality metrics are within acceptable limits."]}
            },
            {
                "name": "helper.py",
                "path": "helper.py",
                "extension": ".py",
                "language": "Python",
                "lines": 30,
                "metrics": calculate_metrics_for_file("def util(): pass", ".py"),
                "technical_debt": {"score": 10, "level": "Low Technical Debt", "reasons": ["Software quality metrics are within acceptable limits."]}
            }
        ]
    }
    pm = calculate_project_metrics(py_analysis)
    with app.test_request_context("/"):
        html = render_template(
            "index.html",
            project=py_analysis,
            project_metrics=pm,
            results=[],
            high=0,
            medium=0,
            low=0
        )
    assert "Python Files" in html
    assert "🐍" in html
    assert "Languages" not in html


def test_c_and_cpp_trailing_return_and_operator_overloading():
    """Verify modern C++ trailing return types, operator overloading, and qualifier ordering."""
    cpp_code = """
    struct Point {
        int x, y;
        auto get_x() -> int { return x; }
        bool operator==(const Point& other) const {
            return x == other.x && y == other.y;
        }
        Point& operator=(const Point& other) {
            x = other.x;
            y = other.y;
            return *this;
        }
        void cleanup() override noexcept { }
        void safe() noexcept(true) { }
    };
    bool Point::operator<(const Point& other) const {
        return x < other.x;
    }
    """
    m = calculate_cpp_metrics(cpp_code)
    # 5 methods in Point + 1 out-of-class operator< = 6
    assert m["num_functions"] == 6
    assert m["num_classes"] == 1


def test_java_package_qualified_throws_and_dotted_annotations():
    """Verify Java package-qualified exceptions in throws clause and dotted annotations."""
    java_code = """
    package com.example.service;

    public class DataService {
        public DataService() throws java.io.IOException, java.lang.Exception {
            init();
        }

        @org.junit.jupiter.api.Test
        public void execute() throws java.io.IOException {
            load();
        }

        @jakarta.annotation.Nullable
        String getStatus() throws java.lang.RuntimeException {
            return "OK";
        }
    }
    """
    m = calculate_java_metrics(java_code)
    # 1 constructor + 2 methods = 3
    assert m["num_functions"] == 3
    assert m["num_classes"] == 1


def test_none_values_in_metrics_and_project_metrics_no_type_error():
    """Verify that None values inside metric dicts do not raise TypeError in debt engine or project aggregator."""
    corrupt_metrics = {
        "cyclomatic_complexity": None,
        "max_function_length": None,
        "max_nesting_depth": None,
        "lines_of_code": 20,
        "comment_density": None,
        "todo_count": None,
        "fixme_count": None,
        "coupling_between_objects": None,
        "lack_of_cohesion": None,
        "security_vulnerabilities": None,
        "past_defects": None,
        "code_churn": None,
    }
    debt = calculate_technical_debt(corrupt_metrics)
    assert isinstance(debt, dict)
    assert debt["score"] >= 0
    assert "Low Comment Density" in debt["reasons"]

    # Project with None metric values
    project_with_nones = {
        "files": [
            {
                "name": "a.js",
                "path": "a.js",
                "extension": ".js",
                "lines": None,
                "metrics": {
                    "num_functions": None,
                    "num_classes": None,
                    "num_imports": None,
                    "comment_density": None,
                    "avg_function_length": None,
                    "cyclomatic_complexity": None,
                    "max_nesting_depth": None,
                    "todo_count": None,
                    "fixme_count": None,
                    "coupling_between_objects": None,
                    "lack_of_cohesion": None,
                    "security_vulnerabilities": None,
                    "past_defects": None,
                    "code_churn": None,
                },
                "technical_debt": {
                    "score": None,
                    "level": None,
                    "reasons": []
                }
            }
        ]
    }
    pm = calculate_project_metrics(project_with_nones)
    assert isinstance(pm, dict)
    assert pm["total_lines"] == 0
    assert pm["total_functions"] == 0
    assert pm["average_debt_score"] == 0.0


def test_html_comments_and_scripts_do_not_inflate_dom_nesting():
    """Verify commented-out HTML tags and script comparisons do not artificially inflate DOM nesting depth."""
    html = """
    <div>
        <!--
        <section>
            <article>
                <aside>
                    <p>Commented out nested tags</p>
                </aside>
            </article>
        </section>
        -->
        <script>
            if (a < b && c > d) {
                console.log("valid");
            }
        </script>
    </div>
    """
    m = calculate_html_metrics(html)
    # The active DOM hierarchy is only div (depth 1) + script (depth 2)
    assert m["max_nesting_depth"] <= 2


def test_python_ast_match_case_and_self_cbo():
    """Verify Python 3.10+ match-case branching and exclusion of self/cls from external CBO."""
    py_code = """
    class Dispatcher:
        def handle(self, action):
            self.internal_step_one()
            self.internal_step_two()
            match action:
                case "start":
                    return True
                case "stop":
                    return False
                case _:
                    return None

        def internal_step_one(self): pass
        def internal_step_two(self): pass
    """
    m = calculate_python_metrics(py_code)
    # self calls should not be counted as external coupling
    assert m["coupling_between_objects"] == 0
    # match with 3 cases should add cyclomatic complexity
    assert m["cyclomatic_complexity"] >= 4
    assert m["max_nesting_depth"] >= 2


def test_javascript_react_arrow_component_detection():
    """Verify React functional components declared with arrow functions are captured as classes/components."""
    js = """
    import React from 'react';

    const UserCard = (props) => {
        return <div>{props.name}</div>;
    };

    const Navbar = function(props) {
        return <nav></nav>;
    };

    export default UserCard;
    """
    m = calculate_javascript_metrics(js)
    # UserCard and Navbar should be captured as components/classes
    assert m["num_classes"] >= 2


def test_additional_c_cpp_html_file_extensions():
    """Verify .htm, .cc, .cxx, .hh, .hxx are recognized and analyzed by calculate_metrics_for_file."""
    for ext in [".htm", ".cc", ".cxx", ".hh", ".hxx"]:
        m = calculate_metrics_for_file("int main() { return 0; }", ext)
        assert isinstance(m, dict)
        assert "lines_of_code" in m
        assert "cyclomatic_complexity" in m


def test_jinja_rendering_with_none_metric_values():
    """Verify that Jinja template renders fallback defaults (not literal 'None') when metrics contain None."""
    analysis = {
        "project_id": "test_nones",
        "file_count": 1,
        "total_lines": 10,
        "files": [
            {
                "name": "data.js",
                "path": "data.js",
                "extension": ".js",
                "language": "JavaScript",
                "lines": None,
                "metrics": {
                    "lines_of_code": None,
                    "comment_density": None,
                    "num_functions": None,
                    "avg_function_length": None,
                    "max_function_length": None,
                    "cyclomatic_complexity": None,
                    "max_nesting_depth": None,
                    "num_imports": None,
                    "todo_count": None,
                    "fixme_count": None,
                    "coupling_between_objects": None,
                    "lack_of_cohesion": None,
                    "security_vulnerabilities": 0,
                    "security_details": [],
                    "past_defects": None,
                    "code_churn": None,
                },
                "technical_debt": {
                    "score": None,
                    "level": "Low Technical Debt",
                    "reasons": ["Acceptable"]
                }
            }
        ]
    }
    pm = calculate_project_metrics(analysis)
    with app.test_request_context("/"):
        html = render_template(
            "index.html",
            project=analysis,
            project_metrics=pm,
            results=[],
            high=0,
            medium=0,
            low=0
        )
    # Ensure no literal "None%" or "None/100" rendered in HTML
    assert "None%" not in html
    assert "None/100" not in html
    assert "0%" in html
    assert "0/100" in html


def test_commented_out_imports_and_security_not_flagged():
    """Verify commented-out imports and security calls in C, C++, Java, JS, HTML do not trigger false positives."""
    # 1. C code with commented includes and commented dangerous functions
    c_code = """
    // #include <stdio.h>
    /* #include <stdlib.h> */
    // gets(buf) is obsolete and unsafe
    /* strcpy(dest, src) is deprecated */
    int compute() {
        return 42;
    }
    """
    c_m = calculate_c_metrics(c_code)
    assert c_m["num_imports"] == 0
    assert c_m["coupling_between_objects"] == 0
    assert c_m["security_vulnerabilities"] == 0

    # 2. Java code with commented imports and commented Runtime.exec
    java_code = """
    // import java.util.List;
    /* import java.util.Map; */
    // Runtime.getRuntime().exec("rm -rf");
    public class Service {
        public void execute() {}
    }
    """
    java_m = calculate_java_metrics(java_code)
    assert java_m["num_imports"] == 0
    assert java_m["coupling_between_objects"] == 0
    assert java_m["security_vulnerabilities"] == 0

    # 3. JavaScript code with commented require and innerHTML
    js_code = """
    // const fs = require('fs');
    /* import express from 'express'; */
    // element.innerHTML = userInput;
    // child_process.exec("whoami");
    function main() {
        return 1;
    }
    """
    js_m = calculate_javascript_metrics(js_code)
    assert js_m["num_imports"] == 0
    assert js_m["coupling_between_objects"] == 0
    assert js_m["security_vulnerabilities"] == 0

    # 4. HTML code with commented form and inputs
    html_code = """
    <!-- <form action="http://insecure.example.com"><input type="password" value="secret"></form> -->
    <!-- <a href="http://example.com" target="_blank"></a> -->
    <div>
        <p>Clean HTML</p>
    </div>
    """
    html_m = calculate_html_metrics(html_code)
    assert html_m["num_imports"] == 0
    assert html_m["security_vulnerabilities"] == 0


def test_javascript_anonymous_class_and_keyword_exclusion():
    """Verify anonymous JS classes extending bases count correctly without adding 'extends' keyword."""
    js_code = """
    export default class extends React.Component {
        render() {
            return null;
        }
    }

    class NamedService {
        constructor() {}
    }
    """
    m = calculate_javascript_metrics(js_code)
    assert m["num_classes"] == 2


def test_indented_python_snippets_ast_parsing():
    """Verify Python code blocks with leading indentation parse correctly and extract functions, classes, complexity."""
    py_code = """
        class DataProcessor:
            def __init__(self, items):
                self.items = items

            def process(self):
                result = []
                for item in self.items:
                    if item > 0:
                        result.append(item * 2)
                return result
    """
    m = calculate_python_metrics(py_code)
    assert m["num_classes"] == 1
    assert m["num_functions"] == 2
    assert m["cyclomatic_complexity"] >= 3
    assert m["lines_of_code"] >= 8





