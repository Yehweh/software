import os
import json
import sqlite3

from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash
)

from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)

import uuid

from src.data_loader import load_data
from src.rule_engine import detect_technical_debt
from src.project_analyzer import analyze_project
from src.compare_engine import compare_entities
from src.code_metrics import calculate_metrics_for_file
from src.technical_debt_engine import calculate_technical_debt


# ============================================================
# APPLICATION CONFIGURATION
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

app = Flask(
    __name__,
    static_folder=os.path.join(BASE_DIR, "static"),
    template_folder=os.path.join(BASE_DIR, "templates")
)

app.secret_key = "technical-debt-intelligence-secret-key"

DATABASE = os.path.join(
    BASE_DIR,
    "users.db"
)


# ============================================================
# DATABASE INITIALIZATION
# ============================================================

def init_db():

    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()

    # Create users table if it does not exist.
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL DEFAULT '',
            email TEXT UNIQUE,
            password TEXT
        )
    """)

    # Read existing columns.
    cursor.execute(
        "PRAGMA table_info(users)"
    )

    columns = [
        row[1]
        for row in cursor.fetchall()
    ]

    # --------------------------------------------------------
    # OLD DATABASE MIGRATION
    # --------------------------------------------------------

    # Older versions of the project used "username".
    # If that column exists, preserve the old account data.
    if "username" in columns and "email" not in columns:

        cursor.execute(
            "ALTER TABLE users ADD COLUMN email TEXT"
        )

        cursor.execute("""
            UPDATE users
            SET email = username
            WHERE email IS NULL
        """)

    # Add name if an older database does not have it.
    if "name" not in columns:

        cursor.execute("""
            ALTER TABLE users
            ADD COLUMN name TEXT NOT NULL DEFAULT ''
        """)

    # Add email if required.
    if "email" not in columns:

        cursor.execute("""
            ALTER TABLE users
            ADD COLUMN email TEXT
        """)

    # Add password if required.
    if "password" not in columns:

        cursor.execute("""
            ALTER TABLE users
            ADD COLUMN password TEXT
        """)

    connection.commit()
    connection.close()


init_db()


# ============================================================
# PROJECT METRIC CALCULATION
# ============================================================

def calculate_project_metrics(project):

    files = project.get(
        "files",
        []
    )

    # --------------------------------------------------------
    # FILE COUNTS
    # --------------------------------------------------------

    total_files = len(files)

    # Only files with actual metrics and actual
    # technical-debt analysis are included here.
    analyzed_files = [
        file
        for file in files
        if file.get("metrics") is not None
        and file.get("technical_debt") is not None
    ]

    # Python files
    python_files = [
        file
        for file in files
        if file.get("language") == "Python"
        or file.get("extension") == ".py"
    ]

    # Detected languages
    languages = sorted(list({
        file.get("language") or (
            file.get("extension", "")[1:].upper()
            if file.get("extension")
            else "Unknown"
        )
        for file in files
        if file.get("language") or file.get("extension")
    }))

    # --------------------------------------------------------
    # LINES OF CODE
    # --------------------------------------------------------

    total_lines = sum(
        (file.get("lines") or 0)
        for file in files
    )

    # --------------------------------------------------------
    # FUNCTIONS
    # --------------------------------------------------------

    total_functions = sum(
        (file.get("metrics", {}).get("num_functions") or 0)
        for file in analyzed_files
        if file.get("metrics")
    )

    # --------------------------------------------------------
    # CLASSES
    # --------------------------------------------------------

    total_classes = sum(
        (file.get("metrics", {}).get("num_classes") or 0)
        for file in analyzed_files
        if file.get("metrics")
    )

    # --------------------------------------------------------
    # IMPORTS / DEPENDENCIES
    # --------------------------------------------------------

    total_imports = sum(
        (file.get("metrics", {}).get("num_imports") or 0)
        for file in analyzed_files
        if file.get("metrics")
    )

    # --------------------------------------------------------
    # COMMENT DENSITY
    # --------------------------------------------------------

    comment_densities = [
        file.get("metrics", {}).get("comment_density")
        for file in analyzed_files
        if file.get("metrics") and file.get("metrics", {}).get("comment_density") is not None
    ]

    if comment_densities:
        average_comment_density = round(
            sum(comment_densities)
            / len(comment_densities),
            2
        )
    else:
        average_comment_density = 0.0

    # --------------------------------------------------------
    # AVERAGE FUNCTION LENGTH
    # --------------------------------------------------------

    function_lengths = [
        file.get("metrics", {}).get("avg_function_length")
        for file in analyzed_files
        if file.get("metrics") and (file.get("metrics", {}).get("avg_function_length") or 0) > 0
    ]

    if function_lengths:
        average_function_length = round(
            sum(function_lengths)
            / len(function_lengths),
            2
        )
    else:
        average_function_length = 0.0

    # --------------------------------------------------------
    # CYCLOMATIC COMPLEXITY
    # --------------------------------------------------------

    complexity_values = [
        (file.get("metrics", {}).get("cyclomatic_complexity") or 1)
        for file in analyzed_files
        if file.get("metrics")
    ]

    if complexity_values:
        average_cyclomatic_complexity = round(
            sum(complexity_values)
            / len(complexity_values),
            2
        )
        total_cyclomatic_complexity = sum(
            complexity_values
        )
    else:
        average_cyclomatic_complexity = 0.0
        total_cyclomatic_complexity = 0

    # --------------------------------------------------------
    # MAXIMUM NESTING DEPTH
    # --------------------------------------------------------

    nesting_values = [
        (file.get("metrics", {}).get("max_nesting_depth") or 0)
        for file in analyzed_files
        if file.get("metrics")
    ]

    if nesting_values:
        max_nesting_depth = max(
            nesting_values
        )
    else:
        max_nesting_depth = 0

    # --------------------------------------------------------
    # TODO ITEMS
    # --------------------------------------------------------

    todo_count = sum(
        (file.get("metrics", {}).get("todo_count") or 0)
        for file in analyzed_files
        if file.get("metrics")
    )

    # --------------------------------------------------------
    # FIXME ITEMS
    # --------------------------------------------------------

    fixme_count = sum(
        (file.get("metrics", {}).get("fixme_count") or 0)
        for file in analyzed_files
        if file.get("metrics")
    )

    # --------------------------------------------------------
    # COUPLING BETWEEN OBJECTS (CBO)
    # --------------------------------------------------------

    cbo_values = [
        (file.get("metrics", {}).get("coupling_between_objects") or 0)
        for file in analyzed_files
        if file.get("metrics")
    ]

    if cbo_values:
        average_cbo = round(
            sum(cbo_values) / len(cbo_values),
            2
        )
        total_cbo = sum(cbo_values)
    else:
        average_cbo = 0.0
        total_cbo = 0

    # --------------------------------------------------------
    # LACK OF COHESION (LCOM)
    # --------------------------------------------------------

    lcom_values = [
        file.get("metrics", {}).get("lack_of_cohesion")
        for file in analyzed_files
        if file.get("metrics")
        and (file.get("metrics", {}).get("num_classes") or 0) > 0
        and file.get("metrics", {}).get("lack_of_cohesion") is not None
    ]

    if lcom_values:
        average_lcom = round(
            sum(lcom_values) / len(lcom_values),
            2
        )
    else:
        average_lcom = 0.0

    # --------------------------------------------------------
    # SECURITY VULNERABILITIES
    # --------------------------------------------------------

    total_security_vulnerabilities = sum(
        (file.get("metrics", {}).get("security_vulnerabilities") or 0)
        for file in analyzed_files
        if file.get("metrics")
    )

    # --------------------------------------------------------
    # PAST DEFECTS
    # --------------------------------------------------------

    total_past_defects = sum(
        (file.get("metrics", {}).get("past_defects") or 0)
        for file in analyzed_files
        if file.get("metrics")
    )

    # --------------------------------------------------------
    # CODE CHURN
    # --------------------------------------------------------

    total_code_churn = sum(
        (file.get("metrics", {}).get("code_churn") or 0)
        for file in analyzed_files
        if file.get("metrics")
    )

    # ========================================================
    # TECHNICAL DEBT
    # ========================================================

    debt_scores = [
        file.get("technical_debt", {}).get("score")
        for file in analyzed_files
        if file.get("technical_debt") and file.get("technical_debt", {}).get("score") is not None
    ]

    # --------------------------------------------------------
    # HIGH DEBT
    # --------------------------------------------------------

    high_debt = sum(
        1
        for file in analyzed_files
        if file.get(
            "technical_debt",
            {}
        ).get("level") == "High Technical Debt"
    )

    # --------------------------------------------------------
    # MEDIUM DEBT
    # --------------------------------------------------------

    medium_debt = sum(
        1
        for file in analyzed_files
        if file.get(
            "technical_debt",
            {}
        ).get("level") == "Medium Technical Debt"
    )

    # --------------------------------------------------------
    # LOW DEBT
    # --------------------------------------------------------

    low_debt = sum(
        1
        for file in analyzed_files
        if file.get(
            "technical_debt",
            {}
        ).get("level") == "Low Technical Debt"
    )

    # --------------------------------------------------------
    # AVERAGE DEBT SCORE
    # --------------------------------------------------------

    if debt_scores:
        average_debt_score = round(
            sum(debt_scores)
            / len(debt_scores),
            2
        )
    else:
        average_debt_score = 0.0


    # --------------------------------------------------------
    # PROJECT DEBT LEVEL
    # --------------------------------------------------------

    if average_debt_score >= 61:

        project_debt_level = (
            "High Technical Debt"
        )

    elif average_debt_score >= 31:

        project_debt_level = (
            "Medium Technical Debt"
        )

    else:

        project_debt_level = (
            "Low Technical Debt"
        )


    # ========================================================
    # RETURN ALL PROJECT METRICS
    # ========================================================

    return {

        # File information
        "total_files": total_files,

        "analyzed_files": len(
            analyzed_files
        ),

        "python_files": len(
            python_files
        ),

        "language_count": len(
            languages
        ),

        "languages": languages,

        # Source-code metrics
        "total_lines": total_lines,

        "total_functions": total_functions,

        "total_classes": total_classes,

        "total_imports": total_imports,

        "average_comment_density":
            average_comment_density,

        "average_function_length":
            average_function_length,

        "cyclomatic_complexity":
            average_cyclomatic_complexity,

        "total_cyclomatic_complexity":
            total_cyclomatic_complexity,

        "max_nesting_depth":
            max_nesting_depth,

        "todo_count":
            todo_count,

        "fixme_count":
            fixme_count,

        # 5 New Testing Metrics
        "average_cbo":
            average_cbo,

        "total_cbo":
            total_cbo,

        "average_lcom":
            average_lcom,

        "total_security_vulnerabilities":
            total_security_vulnerabilities,

        "total_past_defects":
            total_past_defects,

        "total_code_churn":
            total_code_churn,

        # Technical debt
        "high_debt":
            high_debt,

        "medium_debt":
            medium_debt,

        "low_debt":
            low_debt,

        "average_debt_score":
            average_debt_score,

        "project_debt_level":
            project_debt_level
    }


# ============================================================
# SIGN UP
# ============================================================

@app.route(
    "/signup",
    methods=["GET", "POST"]
)
def signup():

    if request.method == "POST":

        name = request.form.get(
            "name",
            ""
        ).strip()

        email = request.form.get(
            "email",
            ""
        ).strip().lower()

        password = request.form.get(
            "password",
            ""
        )

        confirm_password = request.form.get(
            "confirm_password",
            ""
        )


        # ----------------------------------------------------
        # VALIDATION
        # ----------------------------------------------------

        if not name:

            flash(
                "Name is required.",
                "error"
            )

            return redirect(
                url_for("signup")
            )


        if not email:

            flash(
                "Email is required.",
                "error"
            )

            return redirect(
                url_for("signup")
            )


        if not password:

            flash(
                "Password is required.",
                "error"
            )

            return redirect(
                url_for("signup")
            )


        if password != confirm_password:

            flash(
                "Passwords do not match.",
                "error"
            )

            return redirect(
                url_for("signup")
            )


        if len(password) < 6:

            flash(
                "Password must be at least 6 characters.",
                "error"
            )

            return redirect(
                url_for("signup")
            )


        # ----------------------------------------------------
        # CHECK WHETHER ACCOUNT ALREADY EXISTS
        # ----------------------------------------------------

        connection = sqlite3.connect(
            DATABASE
        )

        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT id
            FROM users
            WHERE LOWER(email) = ?
            """,
            (email,)
        )

        existing_user = cursor.fetchone()

        connection.close()


        if existing_user:

            flash(
                "An account with this email already exists.",
                "error"
            )

            return redirect(
                url_for("signup")
            )


        # ----------------------------------------------------
        # HASH PASSWORD
        # ----------------------------------------------------

        password_hash = generate_password_hash(
            password
        )


        # ----------------------------------------------------
        # INSERT ACCOUNT
        # ----------------------------------------------------

        try:

            connection = sqlite3.connect(
                DATABASE
            )

            cursor = connection.cursor()

            cursor.execute(
                """
                INSERT INTO users
                (name, email, password)
                VALUES (?, ?, ?)
                """,
                (
                    name,
                    email,
                    password_hash
                )
            )

            connection.commit()
            connection.close()


            flash(
                "Account created successfully. Please sign in.",
                "success"
            )

            return redirect(
                url_for("login")
            )


        except sqlite3.IntegrityError:

            flash(
                "An account with this email already exists.",
                "error"
            )

            return redirect(
                url_for("signup")
            )

    return render_template(
        "signup.html"
    )


# ============================================================
# LOGIN
# ============================================================

@app.route(
    "/login",
    methods=["GET", "POST"]
)
def login():

    if request.method == "POST":

        email = request.form.get(
            "email",
            ""
        ).strip().lower()

        password = request.form.get(
            "password",
            ""
        )


        # ----------------------------------------------------
        # VALIDATION
        # ----------------------------------------------------

        if not email or not password:

            flash(
                "Email and password are required.",
                "error"
            )

            return redirect(
                url_for("login")
            )


        # ----------------------------------------------------
        # FIND ACCOUNT
        # ----------------------------------------------------

        connection = sqlite3.connect(
            DATABASE
        )

        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT id, name, email, password
            FROM users
            WHERE LOWER(email) = ?
            """,
            (email,)
        )

        user = cursor.fetchone()

        connection.close()


        # ----------------------------------------------------
        # VERIFY PASSWORD
        # ----------------------------------------------------

        if user:

            stored_password = user[3]

            if stored_password:

                try:

                    password_valid = (
                        check_password_hash(
                            stored_password,
                            password
                        )
                    )

                except ValueError:

                    password_valid = False

            else:

                password_valid = False

        else:

            password_valid = False


        # ----------------------------------------------------
        # SUCCESSFUL LOGIN
        # ----------------------------------------------------

        if user and password_valid:

            session.clear()

            session["user_id"] = user[0]

            # Store the name under both keys so that
            # older and newer templates both work.
            session["username"] = user[1]

            session["user_name"] = user[1]

            session["email"] = user[2]


            return redirect(
                url_for("index")
            )


        # ----------------------------------------------------
        # FAILED LOGIN
        # ----------------------------------------------------

        flash(
            "Invalid email or password.",
            "error"
        )

        return redirect(
            url_for("login")
        )


    return render_template(
        "login.html"
    )


# ============================================================
# LOGOUT
# ============================================================

@app.route("/logout")
def logout():

    session.clear()

    return redirect(
        url_for("login")
    )


# ============================================================
# CONVENIENCE ROUTES FOR ABOUT METRICS & BENCHMARK
# ============================================================

@app.route("/about-metrics")
def about_metrics():

    if "user_id" not in session:

        return redirect(
            url_for("login")
        )

    return redirect(
        url_for("index") + "#about-metrics"
    )


@app.route("/benchmark")
def benchmark():

    if "user_id" not in session:

        return redirect(
            url_for("login")
        )

    return redirect(
        url_for("index") + "#benchmark"
    )


@app.route("/compare")
def compare():

    if "user_id" not in session:

        return redirect(
            url_for("login")
        )

    return redirect(
        url_for("index") + "#compare"
    )


# ============================================================
# DASHBOARD
# ============================================================

@app.route("/")
def index():

    # --------------------------------------------------------
    # LOGIN PROTECTION
    # --------------------------------------------------------

    if "user_id" not in session:

        return redirect(
            url_for("login")
        )


    # --------------------------------------------------------
    # DATASET BASELINE ANALYSIS
    # --------------------------------------------------------

    dataset_results = []
    dataset_high = 0
    dataset_medium = 0
    dataset_low = 0

    try:

        dataframe = load_data()

        for i, (_, row) in enumerate(
            dataframe.head(10).iterrows(),
            1
        ):

            result = detect_technical_debt(
                row
            )

            score = result.get("Debt Score", 0)
            level = result.get("Debt Level", "Low Technical Debt")
            reasons = result.get("Reasons", [])

            if level == "High Technical Debt":
                dataset_high += 1
            elif level == "Medium Technical Debt":
                dataset_medium += 1
            else:
                dataset_low += 1

            dataset_results.append({
                "record": i,
                "score": score,
                "level": level,
                "reasons": reasons,
                "Debt Score": score,
                "Debt Level": level,
                "Reasons": reasons
            })

    except Exception as error:

        flash(
            f"Dataset analysis unavailable: {error}",
            "error"
        )


    # --------------------------------------------------------
    # UPLOADED PROJECT
    # --------------------------------------------------------

    project = None
    project_metrics = None

    analysis_filename = session.get("project_analysis_file")

    if analysis_filename:

        analysis_path = os.path.join(
            BASE_DIR,
            "uploads",
            analysis_filename
        )

        if os.path.exists(analysis_path):

            try:

                with open(
                    analysis_path, "r", encoding="utf-8"
                ) as fh:
                    project = json.load(fh)

                project_metrics = (
                    calculate_project_metrics(project)
                )

            except Exception as load_error:

                flash(
                    f"Could not load previous analysis: {load_error}",
                    "error"
                )

    elif session.get("project_analysis"):

        # Fallback: small projects whose summary fitted in the
        # session cookie (should not normally happen after the fix).
        project = session["project_analysis"]

        if project:
            project_metrics = (
                calculate_project_metrics(project)
            )


    # --------------------------------------------------------
    # COMPARISON RESULT
    # --------------------------------------------------------

    comparison = None
    comparison_filename = session.get("comparison_result_file")

    if comparison_filename:

        cmp_path = os.path.join(
            BASE_DIR,
            "uploads",
            comparison_filename
        )

        if os.path.exists(cmp_path):

            try:

                with open(
                    cmp_path, "r", encoding="utf-8"
                ) as fh:
                    comparison = json.load(fh)

            except Exception:
                comparison = None


    # --------------------------------------------------------
    # RENDER DASHBOARD
    # --------------------------------------------------------

    return render_template(

        "index.html",

        username=session.get(
            "username",
            "User"
        ),

        user_name=session.get(
            "user_name",
            session.get(
                "username",
                "User"
            )
        ),

        results=dataset_results,

        high=dataset_high,

        medium=dataset_medium,

        low=dataset_low,

        project=project,

        project_metrics=project_metrics,

        comparison=comparison
    )


# ============================================================
# PROJECT UPLOAD
# ============================================================

@app.route(
    "/upload-project",
    methods=["POST"]
)
def upload_project():

    # --------------------------------------------------------
    # LOGIN PROTECTION
    # --------------------------------------------------------

    if "user_id" not in session:

        return redirect(
            url_for("login")
        )


    # --------------------------------------------------------
    # GET UPLOADED FILE
    # --------------------------------------------------------

    uploaded_file = request.files.get(
        "project_file"
    )


    if uploaded_file is None:

        flash(
            "Please select a project ZIP file.",
            "error"
        )

        return redirect(
            url_for("index")
        )


    if uploaded_file.filename == "":

        flash(
            "Please select a project ZIP file.",
            "error"
        )

        return redirect(
            url_for("index")
        )


    # --------------------------------------------------------
    # VALIDATE FILE TYPE
    # --------------------------------------------------------

    filename = uploaded_file.filename.lower()


    if not filename.endswith(".zip"):

        flash(
            "Only ZIP project files are supported.",
            "error"
        )

        return redirect(
            url_for("index")
        )


    # --------------------------------------------------------
    # UPLOAD DIRECTORY
    # --------------------------------------------------------

    upload_directory = os.path.join(
        BASE_DIR,
        "uploads"
    )

    os.makedirs(
        upload_directory,
        exist_ok=True
    )


    # --------------------------------------------------------
    # SAVE ZIP
    # --------------------------------------------------------

    zip_path = os.path.join(
        upload_directory,
        uploaded_file.filename
    )

    uploaded_file.save(
        zip_path
    )


    # --------------------------------------------------------
    # ANALYZE PROJECT
    # --------------------------------------------------------

    try:

        analysis = analyze_project(
            zip_path
        )


        # Calculate fresh project-level metrics.
        project_metrics = (
            calculate_project_metrics(
                analysis
            )
        )


        # Store them inside the analysis object too.
        analysis[
            "project_metrics"
        ] = project_metrics


        # ----------------------------------------------------------
        # PERSIST ANALYSIS TO DISK
        # Flask sessions are cookie-based and limited to ~4 KB.
        # Storing the full file list in the session silently truncates
        # or rejects it for any non-trivial project, which means
        # project_analysis comes back as None on the next request and
        # every metric shows 0.  We write the data to a small JSON file
        # on disk and only keep the filename key in the session cookie.
        # ----------------------------------------------------------

        analysis_filename = (
            f"analysis_{analysis['project_id']}.json"
        )

        analysis_path = os.path.join(
            BASE_DIR,
            "uploads",
            analysis_filename
        )

        with open(analysis_path, "w", encoding="utf-8") as fh:
            json.dump(analysis, fh)

        # Store only the lightweight reference in the session.
        session["project_analysis_file"] = analysis_filename

        # Keep a tiny summary in the session for quick access.
        session["project_analysis"] = {
            "project_id":       analysis["project_id"],
            "project_directory": analysis["project_directory"],
            "file_count":       analysis["file_count"],
            "total_lines":      analysis["total_lines"],
            "files":            [],          # loaded from disk when needed
            "project_metrics":  project_metrics,
        }


        flash(
            "Project uploaded and analyzed successfully.",
            "success"
        )


    except Exception as error:

        flash(
            f"Project analysis failed: {error}",
            "error"
        )


    return redirect(
        url_for("index")
    )


# ============================================================
# PROJECT & FILE COMPARISON
# ============================================================

def analyze_uploaded_item(uploaded_file, upload_directory):
    """
    Analyzes an uploaded candidate for technical debt comparison.
    Supports either:
      - A full project ZIP file (extracted and analyzed)
      - A standalone source code file (.py, .js, .html, .css, .java, .c, .cpp, etc.)
    """
    original_filename = uploaded_file.filename
    clean_filename = os.path.basename(original_filename)
    extension = os.path.splitext(clean_filename)[1].lower()

    if extension == ".zip":
        unique_prefix = uuid.uuid4().hex[:8]
        saved_zip_path = os.path.join(
            upload_directory,
            f"cmp_{unique_prefix}_{clean_filename}"
        )
        uploaded_file.save(saved_zip_path)
        analysis = analyze_project(saved_zip_path)
        pm = calculate_project_metrics(analysis)
        analysis["project_metrics"] = pm
        analysis["project_name"] = clean_filename
        return analysis

    # Standalone single source code file
    content_bytes = uploaded_file.read()
    content = content_bytes.decode("utf-8", errors="ignore")
    metrics = calculate_metrics_for_file(content, extension)
    debt = calculate_technical_debt(metrics)
    code_lines = [line for line in content.splitlines() if line.strip()]

    LANGUAGE_MAP = {
        ".py": "Python",
        ".js": "JavaScript",
        ".html": "HTML",
        ".htm": "HTML",
        ".css": "CSS",
        ".java": "Java",
        ".c": "C",
        ".h": "C",
        ".cpp": "C++",
        ".cc": "C++",
        ".cxx": "C++",
        ".hpp": "C++",
        ".hh": "C++",
        ".hxx": "C++",
    }
    language = LANGUAGE_MAP.get(
        extension,
        extension[1:].upper() if extension else "Source"
    )

    return {
        "name": clean_filename,
        "path": clean_filename,
        "extension": extension,
        "language": language,
        "lines": len(code_lines),
        "metrics": metrics,
        "technical_debt": debt
    }


@app.route(
    "/compare-files",
    methods=["POST"]
)
def compare_files():

    if "user_id" not in session:
        return redirect(url_for("login"))

    file_a = request.files.get("file_a")
    file_b = request.files.get("file_b")

    if not file_a or not file_b or file_a.filename == "" or file_b.filename == "":
        flash(
            "Please select both File/Project A and File/Project B to perform a comparison.",
            "error"
        )
        return redirect(url_for("index") + "#compare")

    upload_directory = os.path.join(
        BASE_DIR,
        "uploads"
    )
    os.makedirs(upload_directory, exist_ok=True)

    try:
        analyzed_a = analyze_uploaded_item(file_a, upload_directory)
        analyzed_b = analyze_uploaded_item(file_b, upload_directory)

        comparison_result = compare_entities(
            analyzed_a,
            analyzed_b,
            label_a=file_a.filename,
            label_b=file_b.filename
        )

        cmp_filename = f"comparison_{uuid.uuid4().hex[:8]}.json"
        cmp_path = os.path.join(upload_directory, cmp_filename)
        with open(cmp_path, "w", encoding="utf-8") as fh:
            json.dump(comparison_result, fh)

        session["comparison_result_file"] = cmp_filename
        flash("Comparison generated successfully. Review the report below.", "success")

    except Exception as error:
        flash(f"Comparison failed: {error}", "error")

    return redirect(url_for("index") + "#compare")


@app.route("/clear-comparison")
def clear_comparison():

    if "user_id" not in session:
        return redirect(url_for("login"))

    session.pop("comparison_result_file", None)
    flash("Previous comparison cleared.", "success")
    return redirect(url_for("index") + "#compare")


# ============================================================
# APPLICATION START
# ============================================================

if __name__ == "__main__":

    app.run(
        debug=True,
        host="127.0.0.1",
        port=5000
    )