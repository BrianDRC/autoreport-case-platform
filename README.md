# AutoReport Case Platform

AutoReport Case Platform is a lightweight Vulnerability Case Management
API designed to integrate directly with CI/CD pipelines.

It automatically creates or updates security cases when container image
scans (e.g., Trivy) detect vulnerabilities during builds.

This project demonstrates practical DevSecOps automation patterns
including automated reporting, case tracking, and PR security gating.

------------------------------------------------------------------------

# 🎯 Purpose

Modern DevSecOps teams require automated enforcement of security
policies during software delivery.

This platform enables:

-   Automated vulnerability case creation from pipeline scans
-   Tracking vulnerabilities per branch or PR
-   Storing normalized findings
-   Enforcing severity thresholds
-   Blocking PR merges when policy violations occur

It is designed to simulate a real-world vulnerability management
workflow integrated into CI/CD.

------------------------------------------------------------------------

# 🏗 High-Level Architecture

Developer → Pull Request\
↓\
GitHub Actions Pipeline\
↓\
Docker Build\
↓\
Trivy Image Scan\
↓\
POST /api/v1/ingest/trivy\
↓\
Case Created / Updated\
↓\
(Optional) PR Blocked if HIGH/CRITICAL found

------------------------------------------------------------------------

# 🧱 Technology Stack

-   Python 3.12
-   FastAPI
-   SQLAlchemy 2.x
-   PostgreSQL
-   Docker
-   Trivy (Container Security Scanner)
-   GitHub Actions (CI/CD)

------------------------------------------------------------------------

# 📦 Repository Structure

autoreport-case-platform/ │ ├── app/ │ ├── main.py │ ├── db.py │ ├──
models.py │ ├── schemas.py │ └── trivy_parser.py │ ├── docker/ │ └──
Dockerfile │ ├── docker-compose.yml ├── requirements.txt ├──
.env.example └── README.md

------------------------------------------------------------------------

# 🚀 Getting Started (Local Development)

## 1️⃣ Clone the repository

git clone https://github.com/YOUR_USERNAME/autoreport-case-platform.git\
cd autoreport-case-platform

------------------------------------------------------------------------

## 2️⃣ Configure environment variables

Copy the example file:

cp .env.example .env

Adjust values if needed.

Example configuration:

API_PORT=8000\
API_KEY=dev-secret-change-me\
API_KEY_HEADER=X-API-Key

POSTGRES_USER=securecase_user\
POSTGRES_PASSWORD=securecase_pass\
POSTGRES_DB=securecase_db\
POSTGRES_PORT=5433

DATABASE_URL=postgresql+psycopg2://securecase_user:securecase_pass@db:5432/securecase_db

PGADMIN_DEFAULT_EMAIL=system@gmail.com\
PGADMIN_DEFAULT_PASSWORD=root\
PGADMIN_PORT=5051

------------------------------------------------------------------------

## 3️⃣ Start the platform

docker compose up -d --build

Services:

-   API → http://localhost:8000/docs
-   pgAdmin → http://localhost:5051

------------------------------------------------------------------------

# 🔐 Authentication

All ingestion requests require an API key.

Header format:

X-API-Key: `<your-secret>`{=html}

The value must match the API_KEY defined in your .env file.

------------------------------------------------------------------------

# 📡 Core Endpoint

## POST /api/v1/ingest/trivy

Receives Trivy JSON output and performs:

-   Case upsert (per branch or PR)
-   Vulnerability normalization
-   Severity calculation
-   Policy gate evaluation
-   Audit event logging

### Case Identification Logic

If Pull Request exists: case_key = repo::PR::`<pr_id>`{=html}

Otherwise: case_key = repo::BR::`<branch_name>`{=html}

Each new commit updates the existing case instead of creating
duplicates.

------------------------------------------------------------------------

# 🛡 PR Gating Logic

The system supports two pipeline modes:

CI Mode: - Reports vulnerabilities - Does NOT fail pipeline

PR_GATE Mode: - Reports vulnerabilities - Fails pipeline if severity
threshold exceeded

Typical policy: - Block PR if HIGH or CRITICAL vulnerabilities are
found.

------------------------------------------------------------------------

# 📊 Stored Case Data

Each case stores:

-   Repository
-   Branch or PR reference
-   Latest commit SHA
-   Pipeline run metadata
-   Docker image digest
-   Normalized vulnerability findings
-   Severity counters
-   Raw Trivy JSON report
-   Audit history

------------------------------------------------------------------------

# 🔄 Example Workflow

1.  Developer pushes branch
2.  Pipeline builds Docker image
3.  Trivy scans image
4.  Findings sent to AutoReport Case Platform
5.  Case updated automatically
6.  If PR → main and severity threshold exceeded → merge blocked

------------------------------------------------------------------------

# 🔧 Development Mode (Without Docker)

You can also run locally:

pip install -r requirements.txt\
uvicorn app.main:app --reload

Make sure your DATABASE_URL points to a reachable Postgres instance.

------------------------------------------------------------------------

# 📈 Future Enhancements

-   Webhook notifications (Slack / Teams)
-   Case ownership & assignment
-   Severity override workflow
-   Historical comparison between builds
-   SBOM storage & correlation
-   Dashboard frontend
-   Authentication via JWT / OAuth
-   Multi-repository configuration management

------------------------------------------------------------------------

# 📜 License

MIT License

------------------------------------------------------------------------

# 👤 Author

Developed as a DevSecOps portfolio project to demonstrate automated
vulnerability management and CI/CD security enforcement.
