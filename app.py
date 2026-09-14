import os
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

from src.data_loader import load_data
from src.rule_engine import detect_technical_debt
from src.project_analyzer import analyze_project


app = Flask(__name__)


# ============================================================
# APPLICATION CONFIGURATION
# ============================================================

app.secret_key = "technical-debt-intelligence-secret-key"

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

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

    # --------------------------------------------------------
    # LINES OF CODE
    # --------------------------------------------------------

    total_lines = sum(
        file.get("lines", 0)
        for file in files
    )

    # --------------------------------------------------------
    # FUNCTIONS
    # --------------------------------------------------------

    total_functions = sum(
        file.get("metrics", {}).get(
            "num_functions",
            0
        )
        for file in analyzed_files
    )

    # --------------------------------------------------------
    # CLASSES
    # --------------------------------------------------------

    total_classes = sum(
        file.get("metrics", {}).get(
            "num_classes",
            0
        )
        for file in analyzed_files
    )

    # --------------------------------------------------------
    # IMPORTS / DEPENDENCIES
    # --------------------------------------------------------

    total_imports = sum(
        file.get("metrics", {}).get(
            "num_imports",
            0
        )
        for file in analyzed_files
    )

    # --------------------------------------------------------
    # COMMENT DENSITY
    # --------------------------------------------------------

    comment_densities = [
        file.get("metrics", {}).get(
            "comment_density",
            0
        )
        for file in analyzed_files
    ]

    if comment_densities:

        average_comment_density = round(
            sum(comment_densities)
            / len(comment_densities),
            2
        )

    else:

        average_comment_density = 0


    # --------------------------------------------------------
    # AVERAGE FUNCTION LENGTH
    # --------------------------------------------------------

    function_lengths = [
        file.get("metrics", {}).get(
            "avg_function_length",
            0
        )
        for file in analyzed_files
        if file.get("metrics", {}).get(
            "avg_function_length",
            0
        ) > 0
    ]

    if function_lengths:

        average_function_length = round(
            sum(function_lengths)
            / len(function_lengths),
            2
        )

    else:

        average_function_length = 0


    # --------------------------------------------------------
    # CYCLOMATIC COMPLEXITY
    # --------------------------------------------------------

    complexity_values = [
        file.get("metrics", {}).get(
            "cyclomatic_complexity",
            0
        )
        for file in analyzed_files
        if file.get("metrics") is not None
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

        average_cyclomatic_complexity = 0
        total_cyclomatic_complexity = 0


    # --------------------------------------------------------
    # MAXIMUM NESTING DEPTH
    # --------------------------------------------------------

    nesting_values = [
        file.get("metrics", {}).get(
            "max_nesting_depth",
            0
        )
        for file in analyzed_files
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
        file.get("metrics", {}).get(
            "todo_count",
            0
        )
        for file in analyzed_files
    )


    # --------------------------------------------------------
    # FIXME ITEMS
    # --------------------------------------------------------

    fixme_count = sum(
        file.get("metrics", {}).get(
            "fixme_count",
            0
        )
        for file in analyzed_files
    )


    # ========================================================
    # TECHNICAL DEBT
    # ========================================================

    debt_scores = [
        file.get("technical_debt", {}).get(
            "score",
            0
        )
        for file in analyzed_files
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

        average_debt_score = 0


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

    try:

        dataframe = load_data()

        for _, row in dataframe.head(
            10
        ).iterrows():

            result = detect_technical_debt(
                row
            )

            dataset_results.append(
                result
            )

    except Exception as error:

        flash(
            f"Dataset analysis unavailable: {error}",
            "error"
        )


    # --------------------------------------------------------
    # UPLOADED PROJECT
    # --------------------------------------------------------

    project = session.get(
        "project_analysis"
    )

    project_metrics = None


    if project:

        project_metrics = (
            calculate_project_metrics(
                project
            )
        )


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

        project=project,

        project_metrics=project_metrics
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


        # Store complete analysis in session.
        session[
            "project_analysis"
        ] = analysis


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
# APPLICATION START
# ============================================================

if __name__ == "__main__":

    app.run(
        debug=True,
        host="127.0.0.1",
        port=5000
    )