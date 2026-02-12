
# SecureCase – CI Security Case Engine

SecureCase is a backend service designed to automatically track security findings detected during CI/CD pipelines.

It integrates with container image scanners (e.g., Trivy) and creates or updates security cases based on vulnerability findings.  
The system is optimized for DevSecOps workflows and supports branch-based tracking and merge gating for pull requests.

---

## 🚀 Project Purpose

Modern CI pipelines build Docker images on every commit or pull request.  
SecureCase enables:

- Automatic ingestion of Trivy scan results
- Case tracking per branch or PR
- Merge blocking when HIGH / CRITICAL vulnerabilities are detected
- Centralized visibility of findings across repositories

This project is designed as a DevSecOps portfolio demonstration.

---

## 🏗 Architecture Overview

Developer Workflow:

1. Developer pushes code or opens a Pull Request
2. CI builds Docker image
3. Trivy scans image
4. Pipeline sends scan JSON to SecureCase API
5. SecureCase:
   - Creates or updates a case
   - Calculates severity counts
   - Decides if merge gate should block PR
   - Stores full Trivy report as JSONB

---

## 📦 Tech Stack

- Python 3.12
- FastAPI
- SQLAlchemy 2.x
- PostgreSQL (JSONB storage)
- Docker / Docker Compose

---

## 🗂 Project Structure

```
app/
 ├── main.py          # API routes
 ├── models.py        # SQLAlchemy models
 ├── schemas.py       # Pydantic schemas
 ├── db.py            # Database session & engine
 ├── settings.py      # Environment configuration
 ├── trivy_parser.py  # Trivy JSON parser
docker-compose.yml
Dockerfile
requirements.txt
```

---

## 🐳 Run with Docker

Build and start:

```bash
docker compose down -v
docker compose up --build
```

Services:

- API: http://localhost:8000
- Swagger UI: http://localhost:8000/docs
- pgAdmin: http://localhost:5050

---

## 🔐 Authentication

Requests to ingestion endpoint require an API key header:

```
X-API-Key: your_secret_key
```

Set it via environment variable:

```
API_KEY=your_secret_key
```

---

## 📥 Ingest Endpoint

POST `/api/v1/ingest/trivy`

This endpoint receives:

- Metadata (repo, branch, PR info, commit SHA, pipeline run info)
- Image information (name, tag, digest)
- Full Trivy JSON report

### Case Key Logic

- PR build:
```
provider::org::repo::PR::<pr_id>
```

- Branch build:
```
provider::org::repo::BR::<branch>
```

Each new commit updates the same case.

---

## 📊 Case Listing Endpoints

### List Cases

GET `/api/v1/cases`

Optional filters:

- `repo`
- `branch`
- `status`

Example:

```
GET /api/v1/cases?repo=autoreport-case-platform&status=OPEN
```

---

### Get Case by ID

GET `/api/v1/cases/{case_id}`

Returns full case metadata and severity counts.

---

## 🚧 Gate Logic

If:

- Build is for a PR
- Target branch is `main`
- HIGH or CRITICAL findings exist

Then:

```
"gate": true
```

CI pipeline should fail the job to block merge.

---

## 📂 Data Storage

Each case stores:

- Critical & High counts
- Max severity
- Latest commit SHA
- Latest pipeline run URL
- Latest image digest
- Full Trivy report (JSONB)
- Created / Updated timestamps

---

## 🧠 Future Improvements (Planned)

- Webhook notifications (Slack / Teams)
- Case history tracking per commit
- Severity trend analytics
- Role-based access control
- Repository-to-team mapping
- CI provider auto-detection
- Multi-tenant support

---

## 🧪 Example Use Case

Repository A → PR to main  
Pipeline builds image → Trivy finds 2 HIGH vulns  
Pipeline sends JSON to SecureCase →

Response:

```
{
  "case_status": "OPEN",
  "critical": 0,
  "high": 2,
  "gate": true
}
```

Pipeline fails → PR blocked until vulnerabilities resolved.

---

## 🛡 DevSecOps Portfolio Goal

SecureCase demonstrates:

- CI/CD security integration
- Vulnerability lifecycle tracking
- Backend architecture for security automation
- JSONB data modeling
- Merge gating logic
- Production-ready API structure

---

## 📄 License

This project is provided for portfolio and educational purposes.
