import os
import zipfile
import uuid

from src.code_metrics import calculate_metrics_for_file
from src.technical_debt_engine import calculate_technical_debt


# ============================================================
# SUPPORTED SOURCE FILES
# ============================================================

SUPPORTED_EXTENSIONS = {
    ".py",
    ".java",
    ".c",
    ".cpp",
    ".cc",
    ".cxx",
    ".h",
    ".hpp",
    ".hh",
    ".hxx",
    ".js",
    ".html",
    ".htm",
    ".css",
}


# ============================================================
# LANGUAGE MAPPING
# ============================================================

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


# ============================================================
# SAFE PATH VALIDATION
# ============================================================

def is_safe_path(base_directory, target_path):
    """
    Prevent ZIP extraction from writing files outside
    the intended project directory.
    """

    base_directory = os.path.abspath(
        base_directory
    )

    target_path = os.path.abspath(
        target_path
    )

    try:
        return (
            os.path.commonpath(
                [base_directory, target_path]
            )
            == base_directory
        )

    except ValueError:
        return False


# ============================================================
# LANGUAGE DETECTION
# ============================================================

def get_language(extension):
    """
    Convert a source-file extension into a readable
    programming language name.
    """

    return LANGUAGE_MAP.get(
        extension,
        extension[1:].upper()
        if extension
        else "Unknown"
    )


# ============================================================
# SOURCE FILE ANALYSIS
# ============================================================

def analyze_source_file(
    full_path,
    relative_path,
    filename,
    extension
):
    """
    Read and analyze one supported source-code file.
    """

    try:

        with open(
            full_path,
            "r",
            encoding="utf-8",
            errors="ignore"
        ) as source_file:

            content = source_file.read()

    except Exception as error:

        return {
            "name": filename,
            "path": relative_path,
            "extension": extension,
            "language": get_language(extension),
            "lines": 0,
            "metrics": {},
            "technical_debt": {
                "score": 0,
                "level": "Low Technical Debt",
                "reasons": [
                    f"Unable to analyze file: {error}"
                ],
            },
            "analysis_status": "ERROR",
        }

    # --------------------------------------------------------
    # BASIC LINE COUNT
    # --------------------------------------------------------

    non_empty_lines = [
        line
        for line in content.splitlines()
        if line.strip()
    ]

    basic_line_count = len(
        non_empty_lines
    )

    # --------------------------------------------------------
    # CALCULATE METRICS
    # --------------------------------------------------------

    try:

        metrics = calculate_metrics_for_file(
            content,
            extension
        )

    except Exception as error:

        metrics = {}

        debt_result = {
            "score": 0,
            "level": "Low Technical Debt",
            "reasons": [
                f"Metric analysis failed: {error}"
            ],
        }

        return {
            "name": filename,
            "path": relative_path,
            "extension": extension,
            "language": get_language(extension),
            "lines": basic_line_count,
            "metrics": metrics,
            "technical_debt": debt_result,
            "analysis_status": "ERROR",
        }

    # --------------------------------------------------------
    # CALCULATE TECHNICAL DEBT
    # --------------------------------------------------------

    try:

        debt_result = calculate_technical_debt(
            metrics
        )

    except Exception as error:

        debt_result = {
            "score": 0,
            "level": "Low Technical Debt",
            "reasons": [
                f"Technical debt calculation failed: {error}"
            ],
        }

    # --------------------------------------------------------
    # DETERMINE LINE COUNT
    # --------------------------------------------------------

    metric_line_count = metrics.get(
        "lines_of_code",
        0
    )

    if metric_line_count and metric_line_count > 0:

        file_lines = metric_line_count

    else:

        file_lines = basic_line_count

    # --------------------------------------------------------
    # RESULT
    # --------------------------------------------------------

    return {
        "name": filename,
        "path": relative_path,
        "extension": extension,
        "language": get_language(extension),
        "lines": file_lines,
        "metrics": metrics,
        "technical_debt": debt_result,
        "analysis_status": "ANALYZED",
    }


# ============================================================
# PROJECT ANALYSIS
# ============================================================

def analyze_project(zip_path):
    """
    Extract and analyze a complete software project ZIP file.

    The analyzer:
        1. Safely extracts the ZIP.
        2. Finds supported source files.
        3. Calculates source-code metrics.
        4. Calculates technical debt for every file.
        5. Aggregates project-level statistics.
    """

    project_id = str(
        uuid.uuid4()
    )[:8]

    upload_directory = os.path.join(
        "uploads",
        project_id
    )

    os.makedirs(
        upload_directory,
        exist_ok=True
    )

    # ========================================================
    # SAFE ZIP EXTRACTION
    # ========================================================

    with zipfile.ZipFile(
        zip_path,
        "r"
    ) as zip_file:

        for member in zip_file.infolist():

            target_path = os.path.join(
                upload_directory,
                member.filename
            )

            if not is_safe_path(
                upload_directory,
                target_path
            ):

                raise ValueError(
                    "The uploaded project contains an unsafe file path."
                )

            if member.is_dir():

                os.makedirs(
                    target_path,
                    exist_ok=True
                )

            else:

                parent_directory = os.path.dirname(
                    target_path
                )

                if parent_directory:

                    os.makedirs(
                        parent_directory,
                        exist_ok=True
                    )

                with zip_file.open(
                    member
                ) as source:

                    with open(
                        target_path,
                        "wb"
                    ) as destination:

                        destination.write(
                            source.read()
                        )

    # ========================================================
    # FIND AND ANALYZE SOURCE FILES
    # ========================================================

    source_files = []

    for root, directories, files in os.walk(
        upload_directory
    ):

        # Ignore Python cache directories.
        directories[:] = [
            directory
            for directory in directories
            if directory != "__pycache__"
            and directory != ".git"
            and directory != ".venv"
            and directory != "venv"
            and directory != "node_modules"
        ]

        for filename in files:

            extension = os.path.splitext(
                filename
            )[1].lower()

            if extension not in SUPPORTED_EXTENSIONS:
                continue

            full_path = os.path.join(
                root,
                filename
            )

            relative_path = os.path.relpath(
                full_path,
                upload_directory
            )

            file_data = analyze_source_file(
                full_path,
                relative_path,
                filename,
                extension
            )

            source_files.append(
                file_data
            )

    # ========================================================
    # SORT FILES
    # ========================================================

    source_files.sort(
        key=lambda file: file["path"].lower()
    )

    # ========================================================
    # PROJECT LINE COUNT
    # ========================================================

    total_lines = sum(
        file.get("lines", 0)
        for file in source_files
    )

    # ========================================================
    # ANALYSIS COUNTS
    # ========================================================

    analyzed_files = [
        file
        for file in source_files
        if file.get("analysis_status") == "ANALYZED"
    ]

    error_files = [
        file
        for file in source_files
        if file.get("analysis_status") == "ERROR"
    ]

    # ========================================================
    # LANGUAGE COUNTS
    # ========================================================

    language_counts = {}

    for file in source_files:

        language = file.get(
            "language",
            "Unknown"
        )

        language_counts[language] = (
            language_counts.get(
                language,
                0
            ) + 1
        )

    # ========================================================
    # DEBT COUNTS
    # ========================================================

    high_debt_files = [
        file
        for file in analyzed_files
        if file.get(
            "technical_debt",
            {}
        ).get("level")
        == "High Technical Debt"
    ]

    medium_debt_files = [
        file
        for file in analyzed_files
        if file.get(
            "technical_debt",
            {}
        ).get("level")
        == "Medium Technical Debt"
    ]

    low_debt_files = [
        file
        for file in analyzed_files
        if file.get(
            "technical_debt",
            {}
        ).get("level")
        == "Low Technical Debt"
    ]

    # ========================================================
    # DEBT SCORES
    # ========================================================

    debt_scores = [
        file.get(
            "technical_debt",
            {}
        ).get(
            "score",
            0
        )
        for file in analyzed_files
    ]

    if debt_scores:

        average_debt_score = round(
            sum(debt_scores)
            / len(debt_scores),
            2
        )

    else:

        average_debt_score = 0.0

    # ========================================================
    # PROJECT DEBT LEVEL
    # ========================================================

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
    # RETURN PROJECT RESULT
    # ========================================================

    return {

        "project_id": project_id,

        "project_directory": upload_directory,

        "files": source_files,

        "file_count": len(
            source_files
        ),

        "analyzed_files": len(
            analyzed_files
        ),

        "error_files": len(
            error_files
        ),

        "total_lines": total_lines,

        "language_counts": language_counts,

        "high_debt_files": len(
            high_debt_files
        ),

        "medium_debt_files": len(
            medium_debt_files
        ),

        "low_debt_files": len(
            low_debt_files
        ),

        "average_debt_score":
            average_debt_score,

        "project_debt_level":
            project_debt_level
    }