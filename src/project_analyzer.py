import os
import zipfile
import uuid

from src.code_metrics import calculate_python_metrics
from src.technical_debt_engine import calculate_technical_debt


# Source-code file types that our analyzer can currently read
SUPPORTED_EXTENSIONS = {
    ".py",
    ".java",
    ".c",
    ".cpp",
    ".h",
    ".hpp",
    ".js",
    ".html",
    ".css",
}


def is_safe_path(base_directory, target_path):
    """
    Prevent ZIP files from extracting files outside
    the intended project directory.
    """

    base_directory = os.path.abspath(base_directory)
    target_path = os.path.abspath(target_path)

    return (
        os.path.commonpath([base_directory, target_path])
        == base_directory
    )


def analyze_project(zip_path):

    project_id = str(uuid.uuid4())[:8]

    upload_directory = os.path.join(
        "uploads",
        project_id
    )

    os.makedirs(
        upload_directory,
        exist_ok=True
    )

    # =========================================================
    # SAFE ZIP EXTRACTION
    # =========================================================

    with zipfile.ZipFile(zip_path, "r") as zip_file:

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

                os.makedirs(
                    os.path.dirname(target_path),
                    exist_ok=True
                )

                with zip_file.open(member) as source:

                    with open(
                        target_path,
                        "wb"
                    ) as destination:

                        destination.write(
                            source.read()
                        )

    # =========================================================
    # FIND SOURCE FILES
    # =========================================================

    source_files = []

    for root, directories, files in os.walk(
        upload_directory
    ):

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

            # =================================================
            # READ SOURCE CODE
            # =================================================

            try:

                with open(
                    full_path,
                    "r",
                    encoding="utf-8",
                    errors="ignore"
                ) as file:

                    content = file.read()

            except Exception:
                continue

            # =================================================
            # BASIC LINE COUNT
            # =================================================

            lines = content.splitlines()

            code_lines = [
                line
                for line in lines
                if line.strip()
            ]

            # =================================================
            # CREATE FILE INFORMATION
            # =================================================

            file_data = {

                "name": filename,

                "path": relative_path,

                "extension": extension,

                "lines": len(code_lines),

                "metrics": {},

                "technical_debt": {}

            }

            # =================================================
            # PYTHON ANALYSIS
            # =================================================

            if extension == ".py":

                # ---------------------------------------------
                # Calculate quality metrics
                # ---------------------------------------------

                metrics = calculate_python_metrics(
                    content
                )

                file_data["metrics"] = metrics

                # ---------------------------------------------
                # Calculate technical debt
                # ---------------------------------------------

                debt_result = calculate_technical_debt(
                    metrics
                )

                file_data["technical_debt"] = (
                    debt_result
                )

            # =================================================
            # ADD FILE
            # =================================================

            source_files.append(
                file_data
            )

    # =========================================================
    # SORT FILES
    # =========================================================

    source_files.sort(
        key=lambda file: file["path"].lower()
    )

    # =========================================================
    # PROJECT LINE COUNT
    # =========================================================

    total_lines = sum(
        file["lines"]
        for file in source_files
    )

    # =========================================================
    # PROJECT RESULT
    # =========================================================

    return {

        "project_id": project_id,

        "project_directory": upload_directory,

        "files": source_files,

        "file_count": len(source_files),

        "total_lines": total_lines

    }