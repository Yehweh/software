# 🧠 Technical Debt Intelligence & Risk Analysis Platform
> **Software Teammate** — Automated multi-language technical debt assessment, defect prediction benchmarking, SonarQube-style quality gates, and predictive maintenance risk estimation.

[![Python Version](https://img.shields.io/badge/python-3.11%20%7C%203.12%20%7C%203.13-blue.svg)](https://python.org)
[![Framework](https://img.shields.io/badge/framework-Flask%203.1-green.svg)](https://flask.palletsprojects.com/)
[![Test Suite](https://img.shields.io/badge/tests-79%20passed-success.svg)](tests/)
[![Code Style](https://img.shields.io/badge/UI%2FUX-Glassmorphism%20Cyber-purple.svg)](static/css/style.css)
[![Deployment](https://img.shields.io/badge/deploy-Render%20%7C%20Docker-brightgreen.svg)](https://render.com)

---

## 📑 Table of Contents
1. [Executive Summary](#-executive-summary)
2. [Key Capabilities](#-key-capabilities)
3. [System Architecture](#-system-architecture)
4. [Intelligence & Risk Analysis Suite](#-intelligence--risk-analysis-suite)
5. [Baseline Benchmark Intelligence](#-baseline-benchmark-intelligence)
6. [Supported Languages & Metric Engine](#-supported-languages--metric-engine)
7. [Repository File Structure](#-repository-file-structure)
8. [Installation & Local Setup](#-installation--local-setup)
9. [Automated Testing](#-automated-testing)
10. [Production Cloud Deployment](#-production-cloud-deployment)
11. [API & Route Reference](#-api--route-reference)
12. [Default Credentials](#-default-credentials)

---

## 🎯 Executive Summary

**Technical Debt Intelligence (Software Teammate)** is an enterprise-grade static code analysis, defect benchmarking, and technical debt governance platform.

In software engineering, technical debt accumulates silently through hasty design choices, complex functions, lacking test coverage, elevated coupling, and unpatched security vulnerabilities. Left unchecked, it escalates development costs, slows release velocity, and induces severe runtime regressions.

This platform empowers engineering teams to:
* **Upload entire software project archives (.zip)** across multiple languages.
* **Derive granular metrics and AST-based measurements** per file and across the whole project.
* **Calculate weighted Technical Debt Scores (0–100)** and categorize risk levels.
* **Benchmark code against a 60,000-record historical defect prediction dataset**.
* **Prioritize remediation hotspots** using a composite 5-factor priority formula.
* **Enforce SonarQube-style Quality Gates** with 6 automated pass/fail criteria.
* **Predict long-term project maintenance risk** using an 8-factor weighted heuristic model.
* **Receive structured 3-part refactoring recommendations** (Problem $\rightarrow$ Impact $\rightarrow$ Recommended Action).
* **Compare two codebases or versions** side-by-side with diff and delta calculations.

---

## ✨ Key Capabilities

| Capability | Description |
| :--- | :--- |
| **Multi-Language AST Analysis** | Native Python AST parser alongside regex/structural parsers for JavaScript, Java, C, C++, HTML, and CSS. |
| **Comprehensive Metric Extraction** | LOC, Cyclomatic Complexity (McCabe), Maintainability Index (MI), Coupling Between Objects (CBO), Lack of Cohesion (LCOM), Nesting Depth, Duplication %, Test Coverage %, Code Churn, Past Defects, and Security Vulnerabilities. |
| **Dynamic Technical Debt Engine** | Multi-factor weighted score from 0 to 100 with categorical classification: *Low*, *Medium*, and *High* Technical Debt. |
| **Historical Baseline Benchmark** | Real empirical benchmarking against 60,000 defect prediction modules with an interactive searchable risk register. |
| **Hotspot Prioritization Engine** | Ranks codebase files from *Critical* to *Low* priority so developers remediate high-impact bottlenecks first. |
| **SonarQube-Style Quality Gate** | 6 automated checks with customizable thresholds: Security, Maintainability, Duplication, Testing, Complexity, and Technical Debt. |
| **Predictive Risk Assessment** | Project-level maintenance risk score, risk band, 4 dimension sub-scores, and top 3 primary risk drivers. |
| **Structured Recommendations** | Clear, 3-part actionable refactoring advisories paired directly with affected files. |
| **Dual Comparison Engine** | Side-by-side comparison of two projects or files with delta percentages and radar metrics. |
| **Modern Cyber UI/UX** | Responsive glassmorphism interface featuring interactive widgets, live search, and tab switching. |

---

## 🏗️ System Architecture

`mermaid
flowchart TD
    User([User / Browser]) <--> Auth[Session & SQLite Auth\nusers.db]
    User <--> WebUI[Glassmorphic UI / Jinja2\nindex.html]

    subgraph Ingestion [Ingestion Layer]
        Upload[ZIP Project Upload] --> ZipExtract[Safe Extraction & Filter\nis_safe_path]
        DatasetCSV[(data/software_defect_prediction_dataset.csv\n60,000 records)] --> DataLoader[src/data_loader.py]
    end

    subgraph Metrics [Metric & Parsing Layer]
        ZipExtract --> ASTParser[Multi-Language Metric Engine\nsrc/code_metrics.py]
        ASTParser --> Extractor[LOC, CC, MI, CBO, LCOM, Duplication, Churn, Security]
    end

    subgraph RuleAndDebt [Evaluation Layer]
        DataLoader --> RuleEngine[Multi-Criteria Rule Engine\nsrc/rule_engine.py]
        Extractor --> DebtEngine[Technical Debt Calculator\nsrc/technical_debt_engine.py]
    end

    subgraph Intelligence [Intelligence & Risk Suite]
        DebtEngine --> Hotspots[Hotspot Engine\nsrc/hotspot_engine.py]
        DebtEngine --> QualityGate[SonarQube Quality Gate\nsrc/quality_gate.py]
        DebtEngine --> RiskEngine[Predictive Risk Engine\nsrc/risk_engine.py]
        DebtEngine --> Recommender[Structured Recommendations\nsrc/recommendation.py]
    end

    subgraph Comparison [Comparison Engine]
        DebtEngine --> CompareEngine[Dual Comparison Engine\nsrc/compare_engine.py]
    end

    RuleEngine --> BenchmarkView[Baseline Benchmark Register]
    Hotspots & QualityGate & RiskEngine & Recommender --> IntelView[Intelligence & Risk Dashboard]
    CompareEngine --> CompareView[Comparison Matrix View]

    BenchmarkView & IntelView & CompareView --> WebUI
`

---

## 🧠 Intelligence & Risk Analysis Suite

The platform includes a dedicated standalone section: **Intelligence & Risk Analysis** (#intelligence), designed to turn raw metrics into actionable engineering decisions.

### 1. Hotspot Prioritization Engine (src/hotspot_engine.py)
Computes an objective **Priority Score (0–100)** for every file using a normalized multi-factor formula:
\text{Priority Score} = 0.30 \times \text{CC} + 0.25 \times \text{Debt Score} + 0.15 \times \text{Smells} + 0.15 \times \text{Duplication} + 0.15 \times \text{LOC}

* **Priority Bands**:
  * 🔴 **CRITICAL** ($\ge 70$): Immediate architectural refactoring required.
  * 🟠 **HIGH** ( - 69$): Urgent code smell and complexity remediation.
  * 🟡 **MEDIUM** ( - 49$): Watchlist items for subsequent sprint cycles.
  * 🟢 **LOW** ($< 30$): Well-structured, healthy module.
* Displays ranks, meter bars, metric snapshots, and contributing reasons for each file.

### 2. SonarQube-Style Quality Gate (src/quality_gate.py)
Enforces strict gate standards across 6 essential dimensions:
1. **Security & Vulnerabilities**: Max 0 vulnerabilities allowed (zero tolerance).
2. **Maintainability & Code Health**: Max average CBO $\le 15.0$, Max nesting depth $\le 5$, Min comment density $\ge 5\%$.
3. **Code Duplication**: Max duplication ratio $\le 15.0\%$.
4. **Testing & Reliability**: Active test suites and coverage verification.
5. **Cyclomatic Complexity**: Max average complexity $\le 15.0$.
6. **Technical Debt Ceiling**: Max average debt score $\le 50.0$.

Returns an overall **QUALITY GATE PASSED** or **QUALITY GATE FAILED** verdict with full metric vs. threshold breakdowns.

### 3. Predictive Risk Assessment Engine (src/risk_engine.py)
Calculates an estimated project maintenance risk score (0–100) and risk band (LOW, MEDIUM, HIGH, CRITICAL) using an 8-factor weighted heuristic model:
* **4 Core Dimensions**:
  * 🔬 *Complexity & Defect Risk*
  * 🏗️ *Maintainability Risk*
  * 📈 *Technical Debt Growth Risk*
  * 🧪 *Testing & Reliability Risk*
* Automatically identifies the **Top 3 Risk Drivers** in the codebase.
* Includes explicit heuristic disclaimers grounding assessments in measurable static metrics.

### 4. Structured 3-Part Recommendations (src/recommendation.py)
Every finding is rendered in an industry-standard advisory format:
1. **The Problem**: What was detected in the project metrics or code files.
2. **The Impact**: Why it matters to system stability, velocity, or operational risk.
3. **Recommended Action**: Concrete refactoring steps (e.g. Extract Class, Polymorphic Dispatch, Dependency Inversion).
Categorized by severity (CRITICAL, HIGH, MEDIUM, LOW) with clickable file tags.

---

## 📊 Baseline Benchmark Intelligence

The platform incorporates an empirical baseline dataset containing **60,000 software defect prediction records** (data/software_defect_prediction_dataset.csv).

* **Multi-Criteria Rule Engine (src/rule_engine.py)**:
  * Evaluates complexity, duplication, test coverage, CBO, LCOM, churn, past defects, and security indicators.
  * Flexible row handling supports pandas.Series, dictionaries, and mapping objects.
  * Hardened with math.isnan guards against empty or NaN records.
* **Interactive Risk Register**:
  * Displays module ID, debt score, risk badges (High, Medium, Low), and triggered findings.
  * Real-time client-side search by Module ID or text.

---

## 🌐 Supported Languages & Metric Engine

The multi-language metric parser (src/code_metrics.py) supports full project archives containing:

| Language | Extensions | Analysis Method |
| :--- | :--- | :--- |
| **Python** | .py | Full AST traversal (st module) + Regex + Structural analysis |
| **JavaScript** | .js | Lexical & structural syntax pattern scanning |
| **Java** | .java | Class hierarchy, method signatures, complexity & coupling |
| **C / C++** | .c, .cpp, .cc, .h, .hpp | Procedural & OOP control flow, pointer complexity, nesting depth |
| **HTML / CSS** | .html, .htm, .css | Tag density, script block isolation, rule count, selector depth |

### Calculated Code Quality Metrics:
* **Lines of Code (LOC)**: Total lines, code lines, comment lines, and blank lines.
* **Cyclomatic Complexity (CC)**: Decision point counting (if, elif, or, while, catch, logical operators).
* **Maintainability Index (MI)**: Halstead volume, cyclomatic complexity, and LOC logarithmic formulation ( - 100$).
* **Coupling Between Objects (CBO)**: External module, class, and library dependency tallying.
* **Lack of Cohesion in Methods (LCOM)**: Shared attribute and method access disparity.
* **Nesting Depth**: Maximum block indentation level.
* **Code Smells**: Detection of Long Functions, God Classes, Long Parameter Lists, Feature Envy, and TODO/FIXME comments.

---

## 📁 Repository File Structure

`	ext
software-teammate/
├── app.py                      # Flask Application controller, routes & database init
├── run.py                      # Production WSGI bootstrap with safe port binding
├── requirements.txt            # Python dependencies (Flask, pandas, scikit-learn, gunicorn, pytest)
├── Procfile                    # Cloud process definition (Gunicorn web worker)
├── Dockerfile                  # Production container definition (Python 3.11-slim)
├── .dockerignore               # Container build excludes
├── render.yaml                 # Render Infrastructure-as-Code Blueprint
├── pytest.ini                  # Pytest configuration and test paths
├── README.md                   # Complete project documentation
│
├── .github/
│   └── workflows/
│       └── ci.yml              # GitHub Actions CI automated testing pipeline
│
├── data/
│   └── software_defect_prediction_dataset.csv  # 60,000-row empirical benchmark dataset
│
├── src/                        # Core algorithmic engine modules
│   ├── __init__.py
│   ├── advanced_metrices.py    # AST visitor & complex metric helpers
│   ├── code_metrics.py         # Multi-language metric extraction engine
│   ├── compare_engine.py       # Dual-project & file comparison logic
│   ├── data_loader.py          # Benchmark dataset loader with memory caching
│   ├── hotspot_engine.py       # Hotspot ranking & file priority engine
│   ├── main.py                 # CLI demonstration runner
│   ├── project_analyzer.py     # ZIP extraction, file scanning & project aggregation
│   ├── quality_gate.py         # SonarQube-style 6-criteria quality gate
│   ├── recommendation.py       # 3-part structured recommendation generator
│   ├── risk_engine.py          # 8-factor predictive maintenance risk engine
│   ├── rule_engine.py          # Rule-based technical debt detection engine
│   └── technical_debt_engine.py# Project & file technical debt scoring engine
│
├── static/                     # Frontend static assets
│   ├── css/
│   │   └── style.css           # Glassmorphism cyber dark theme & responsive layout
│   └── js/
│       └── script.js           # Tab routing, search filtering & UI interactions
│
├── templates/                  # Jinja2 HTML templates
│   ├── index.html              # Main multi-view dashboard (Dashboard, About, Benchmark, Compare, Intelligence)
│   ├── login.html              # User login interface
│   └── signup.html             # User registration interface
│
└── tests/                      # Automated test suite (79 tests)
    ├── test_compare_engine.py  # 4 tests: comparison normalization & diffs
    ├── test_intelligence.py    # 12 tests: hotspots, quality gates, risk & recommendations
    ├── test_multi_language.py  # 31 tests: multi-language metric extraction
    └── test_rule_engine.py     # 32 tests: rule engine, pandas Series & safety guards
`

---

## 💻 Installation & Local Setup

### 1. Prerequisites
* **Python 3.11+** (Python 3.11, 3.12, or 3.13)
* **Git**

### 2. Clone the Repository
`ash
git clone https://github.com/Yehweh/software.git
cd software
`

### 3. Create & Activate Virtual Environment
* **Windows (PowerShell)**:
  `powershell
  python -m venv env
  .\env\Scripts\Activate.ps1
  `
* **Linux / macOS**:
  `ash
  python3 -m venv env
  source env/bin/activate
  `

### 4. Install Dependencies
`ash
pip install --upgrade pip
pip install -r requirements.txt
`

### 5. Launch the Application
* **Development Mode**:
  `ash
  python app.py
  `
* **Production / Docker-Simulated Mode**:
  `ash
  python run.py
  `
Open your browser and navigate to: **http://127.0.0.1:5000** (or port 10000 when using 
un.py).

---

## 🧪 Automated Testing

The project maintains a 100% test pass rate across 79 comprehensive tests covering unit, integration, and security edge cases.

To execute the test suite:
`ash
pytest
`

### Test Suite Breakdown:
* **	ests/test_rule_engine.py (32 tests)**:
  * Validates individual and composite metric triggers (Complexity, Duplication, Test Coverage, CBO, LCOM, Churn, Past Defects, Security).
  * Validates pandas.Series object compatibility, non-dict fallbacks, and NaN/inf resilience.
* **	ests/test_multi_language.py (31 tests)**:
  * AST extraction for Python, JavaScript, Java, C, C++, and Web formats.
  * Accurate calculation of maintainability index, nesting depth, and code smells.
* **	ests/test_intelligence.py (12 tests)**:
  * File priority scoring and hotspot sorting in descending order.
  * Quality gate categorical evaluation (PASS/FAIL) and threshold enforcement.
  * Predictive risk weighted score, dimensions, and driver extraction.
  * Structured recommendation 3-part formatting and severity grouping.
  * Route authorization and template rendering tests.
* **	ests/test_compare_engine.py (4 tests)**:
  * Comparison normalization, metric delta calculations, and edge cases.

---

## 🚀 Production Cloud Deployment

The repository is pre-configured for automated continuous deployment on **Render**, **Railway**, **Fly.io**, or any container platform.

### Deploying to Render (Connected to GitHub)
1. Fork or push this repository to GitHub.
2. Sign in to [Render](https://render.com) and click **New +** $\rightarrow$ **Web Service**.
3. Select your repository.
4. **Configuration Settings**:
   * **Language**: Docker (or Python 3)
   * **Branch**: main
   * **Region**: Nearest to your users
   * **Instance Type**: Free
   * **Environment Variables**:
     * SECRET_KEY: *(click Generate or enter a random string)*
     * PORT: 10000
5. Click **Deploy Web Service**.

### Why Zero Functionality Is Lost in Production:
* **Multi-Worker Database Safety**: pp.py uses INSERT OR IGNORE and 	imeout=15.0 to eliminate SQLite lock or unique constraint conflicts across Gunicorn workers.
* **Dynamic Port Resolution**: 
un.py parses $PORT safely with automatic fallback to port 10000.
* **Extended Worker Timeout**: Configured with --timeout 120 to allow thorough AST parsing of large repositories without gateway timeouts.
* **Dataset Persistence**: The 4.4MB CSV dataset is tracked directly in Git and automatically loads on start.

---

## 🔌 API & Route Reference

| Method | Endpoint | Auth Required | Description |
| :---: | :--- | :---: | :--- |
| GET | / | Yes | Main Dashboard: Overview stats, project file metrics, code smell breakdown |
| GET | /#about-metrics | Yes | Comprehensive educational guide to all metrics and thresholds |
| GET | /#benchmark | Yes | Baseline Benchmark Register (60K historical defect prediction modules) |
| GET | /#compare | Yes | Side-by-side technical debt comparison interface |
| GET | /#intelligence | Yes | Standalone Intelligence & Risk Analysis Suite (Hotspots, Gates, Risk, Recs) |
| GET | /intelligence | Yes | Convenience redirect to /#intelligence |
| GET | /login | No | User login portal |
| POST| /login | No | Validates user credentials and initiates session |
| GET | /signup | No | User registration interface |
| POST| /signup | No | Registers new user account with hashed password |
| GET | /logout | Yes | Clears session data and redirects to /login |
| POST| /upload-project | Yes | Uploads .zip file, analyzes multi-language codebase, computes metrics |
| POST| /compare-projects | Yes | Uploads two project archives and computes comparative delta matrix |

---

## 🔑 Default Credentials

For demonstration, evaluation, and grading purposes, the database automatically seeds a demo account upon first run:

* **Email:** 	ester@example.com
* **Password:** password123

*(You can also click **Sign Up** at /signup to register any custom username and password).*

---

## 📄 License & Academic Attribution
Developed as part of the **Software Teammate** initiative for Software Engineering & Quality Assurance.
All code and dataset benchmarks are intended for educational, research, and engineering analysis purposes.
