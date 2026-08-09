
# AI Resume Screening & Candidate Ranking System

An end-to-end AI-powered system that parses resumes (PDF/DOCX, including scanned
PDFs via OCR), extracts structured requirements from job descriptions, produces
deterministic and explainable candidate scores and rankings, and automates
recruiter follow-up through email notifications and interview scheduling — all
backed by a relational PostgreSQL schema.

## 🎥 Demo Video

[Watch the full walkthrough](https://drive.google.com/file/d/17bsRLoGs9pb8-Oto40N4FDz5EY4KRg1j/view?usp=drive_link)

## 1. Project Overview

Recruiters spend hours manually reading resumes and comparing them against job
requirements. This system automates that pipeline end-to-end: upload a resume,
create a job description, get an explainable 0–100 match score with matched/missing
skills, strengths, and gaps, see a ranked leaderboard across all candidates for a
role — and automatically notify candidates by email based on their score, with an
interview scheduling link attached for strong matches.

## 2. Problem Statement

Given a pool of resumes and one or more job descriptions, produce a transparent,
relationally-queryable candidate ranking that a recruiter can trust and audit,
without hallucinated experience or opaque black-box scores — and automate the
communication loop back to candidates.

## 3. Features

- PDF and DOCX resume parsing, with automatic OCR fallback for scanned PDFs
- LLM-based structured extraction of candidate and job information (provider-agnostic)
- Deterministic, weighted, explainable scoring (skills / experience / education / other)
- Relational skill storage and matching (no core search over JSON blobs)
- Candidate search & filtering (name, email, skill, experience range, status)
- Candidate status tracking (pending / shortlisted / rejected) with manual override
- Candidate detail view with full extracted profile and score history
- Job-based ranking dashboard
- **Automated email notifications** — shortlist, rejection, or under-review emails
  sent automatically based on score thresholds, with AI-derived feedback
- **Automated interview scheduling links** (via Cal.com) attached to shortlist
  emails for top-scoring candidates
- Streamlit UI with a modern recruiter-facing design across 7 pages, calling a
  FastAPI backend over HTTP
- Dockerized (FastAPI + Streamlit + PostgreSQL)
- Alembic migrations, pytest test suite (35 tests, fully mocked — no API keys required)

## 4. Architecture

```mermaid
flowchart LR
    U[User] --> ST[Streamlit UI]
    ST -- HTTP/JSON --> API[FastAPI Backend]
    API --> DB[(PostgreSQL)]
    API --> LLM[LLM Provider<br/>Gemini / OpenAI / Anthropic / Groq / Mock]
    API --> OCR[OCR Service<br/>pytesseract + poppler]
    API --> EMAIL[Email Service<br/>SMTP / SendGrid]
    API --> CAL[Cal.com Scheduling Link]
```

The Streamlit frontend never talks to PostgreSQL directly. All validation, parsing,
extraction, scoring, persistence, ranking, search, and notification logic live in
the backend.

### Backend layering

```mermaid
flowchart TB
    Routes[api/routes] --> Services[services/*]
    Services --> Repos[db/repositories]
    Repos --> Models[db/models]
    Services --> LLMLayer[services/llm]
    Services --> Parsing[services/parsing + services/ocr]
    Services --> Scoring[services/scoring]
    Services --> Notifications[services/notifications]
```

## 5. Tech Stack

| Layer | Technology |
|---|---|
| Backend framework | FastAPI, Uvicorn, Pydantic v2 |
| ORM / Migrations | SQLAlchemy 2.x, Alembic |
| Database | PostgreSQL (SQLite supported for local dev/tests) |
| Frontend | Streamlit |
| PDF parsing | pdfplumber |
| DOCX parsing | python-docx |
| OCR | pytesseract + pdf2image (poppler) |
| LLM | Provider-agnostic abstraction — Gemini / OpenAI / Anthropic / Groq / OpenRouter / Ollama, via `httpx` |
| Email notifications | SMTP (e.g. Gmail) or SendGrid, provider-agnostic |
| Interview scheduling | Cal.com (public booking link, no API key required) |
| Background processing | FastAPI `BackgroundTasks` (non-blocking email/status updates) |
| Testing | pytest, FastAPI TestClient, reportlab (test fixture generation) |
| Containerization | Docker, docker-compose |

## 6. Project Structure

```
ai-resume-screener/
├── backend/
│   ├── app/
│   │   ├── main.py                     (FastAPI app entrypoint)
│   │   ├── api/
│   │   │   ├── dependencies.py
│   │   │   └── routes/                 (health, resumes, jobs, candidates, screenings)
│   │   ├── core/                       (config, exceptions, logging)
│   │   ├── db/
│   │   │   ├── database.py
│   │   │   ├── models/                 (Job, Candidate, Skill, CandidateSkill,
│   │   │   │                            ResumeFile, Score, ScoreSkill)
│   │   │   └── repositories/
│   │   ├── schemas/                    (Pydantic request/response models)
│   │   ├── services/
│   │   │   ├── parsing/                (pdf_parser, docx_parser, text_cleaner, resume_extractor)
│   │   │   ├── ocr/                    (pytesseract + pdf2image)
│   │   │   ├── llm/                    (provider abstraction: gemini / openai / anthropic /
│   │   │   │                            groq / openrouter / ollama / mock)
│   │   │   ├── scoring/                (skill_matcher, experience_matcher,
│   │   │   │                            education_matcher, scorer)
│   │   │   ├── screening/              (screening_service)
│   │   │   ├── notifications/          (email_service, smtp_provider, sendgrid_provider,
│   │   │   │                            templates, scheduling, notification_service)
│   │   │   ├── resume_service.py
│   │   │   ├── job_service.py
│   │   │   └── candidate_service.py
│   │   └── utils/                      (file_validation, normalization, explanation_parser)
│   ├── tests/                          (35 tests — parsing, OCR, scoring, screening,
│   │                                    notifications, candidates, jobs)
│   ├── alembic/
│   │   ├── env.py
│   │   └── versions/                   (schema migrations)
│   ├── requirements.txt
│   ├── requirements-dev.txt
│   ├── pyproject.toml
│   ├── .env.example
│   └── Dockerfile
│
├── frontend/
│   ├── app.py                          (entrypoint — st.navigation page registry)
│   ├── pages/
│   │   ├── dashboard.py
│   │   ├── upload_resume.py
│   │   ├── create_job.py
│   │   ├── candidates.py
│   │   ├── screen_candidate.py
│   │   ├── ranking_dashboard.py
│   │   └── candidate_details.py
│   ├── components/
│   │   └── theme.py                    (shared CSS, KPI cards, status/skill chips)
│   ├── services/
│   │   └── api_client.py               (all backend HTTP calls)
│   ├── .streamlit/
│   │   └── config.toml                 (theme config)
│   ├── requirements.txt
│   └── Dockerfile
│
├── docs/
│   └── screenshots/                    (dashboard.png, resume.png, screening.png,
│                                        ranking.png, candidates.png)
│
├── docker-compose.yml
├── .gitignore
└── README.md
```

## 7. Database Schema

```mermaid
erDiagram
    JOBS ||--o{ SCORES : has
    CANDIDATES ||--o{ SCORES : has
    CANDIDATES ||--o{ CANDIDATE_SKILLS : has
    SKILLS ||--o{ CANDIDATE_SKILLS : has
    CANDIDATES ||--o{ RESUME_FILES : has
    SCORES ||--o{ SCORE_SKILLS : has
    SKILLS ||--o{ SCORE_SKILLS : has

    JOBS {
        uuid id PK
        string title
        text raw_description
        text required_skills
        text preferred_skills
        float minimum_experience_years
        string education_requirement
    }
    CANDIDATES {
        uuid id PK
        string name
        string email
        string phone
        float total_experience_years
        text education_summary
        text summary
        string status
    }
    SKILLS {
        uuid id PK
        string name
        string normalized_name UK
    }
    CANDIDATE_SKILLS {
        uuid id PK
        uuid candidate_id FK
        uuid skill_id FK
        string proficiency
    }
    RESUME_FILES {
        uuid id PK
        uuid candidate_id FK
        string filename
        string extraction_status
        string extraction_method
        text raw_text
    }
    SCORES {
        uuid id PK
        uuid candidate_id FK
        uuid job_id FK
        float overall_score
        float skills_score
        float experience_score
        float education_score
        text explanation
    }
    SCORE_SKILLS {
        uuid id PK
        uuid score_id FK
        uuid skill_id FK
        string match_type
        float match_score
    }
```

Candidate skill search and filtering query the relational
`candidates → candidate_skills → skills` path directly (see
`CandidateRepository.search`); no core search depends on JSON blobs.

## 8. Data Flow — Resume Processing

```mermaid
flowchart TD
    A[Upload] --> B[Validate extension & size]
    B --> C[Detect file type]
    C -->|docx| D[python-docx extraction]
    C -->|pdf| E[pdfplumber extraction]
    E --> F{Meaningful text?}
    F -->|Yes| G[Clean text]
    F -->|No| H[OCR via pytesseract + poppler]
    H --> G
    D --> G
    G --> I[LLM structured extraction]
    I --> J[Persist Candidate + Skills relationally]
```

## 9. LLM Architecture

The system is provider-agnostic via a small `LLMProvider` abstraction
(`services/llm/base.py`) with concrete implementations calling each provider's
REST API directly over `httpx` (no heavyweight SDK lock-in):

- `GeminiProvider` — `generateContent` with `responseSchema`
- `OpenAIProvider` — also powers Groq, OpenRouter, and Ollama, since all four
  speak the same OpenAI-compatible chat completions format (switch provider by
  changing one environment variable, no code change needed)
- `AnthropicProvider` — Messages API with schema embedded in the system prompt
- `MockProvider` — deterministic heuristic extraction (regex + keyword matching),
  used automatically when `LLM_PROVIDER=mock` or in tests, so the whole system is
  runnable and testable **without any API key**

Selected via the `LLM_PROVIDER` environment variable. All extraction goes through
Pydantic models (`ResumeExtraction`, `JobExtraction`) with validation and a bounded
retry; a failure raises a controlled `LLMProviderError` (HTTP 502) instead of
crashing the API.

Screening itself never re-sends raw resume/JD text to the LLM — it operates on the
already-extracted structured Candidate and Job records, and the actual 0–100 score
is computed by deterministic application code (`services/scoring/scorer.py`), not
by the LLM. This guarantees the same candidate scored against the same job always
produces the same score.

## 10. OCR Architecture

`services/parsing/resume_extractor.py` implements the decision:

1. DOCX → always `python-docx`.
2. PDF → try `pdfplumber` first.
3. If extracted text length is below `OCR_MIN_TEXT_CHARS` (default 50), fall back to
   OCR: `pdf2image.convert_from_path` (requires the `poppler-utils` system package)
   rasterizes each page, then `pytesseract.image_to_string` (requires the
   `tesseract-ocr` system package) extracts text.

Both system dependencies are installed automatically in `backend/Dockerfile`.

## 11. Email Notifications & Interview Scheduling

After every screening, a background task (`services/notifications/notification_service.py`)
decides what happens next based on the candidate's score — this runs *after* the
HTTP response is already sent, so it never slows down the recruiter's screen:

| Score | Action |
|---|---|
| ≥ `SHORTLIST_SCORE_THRESHOLD` (default 70) | Shortlist email sent; candidate status auto-updated to `shortlisted` |
| ≥ `SCHEDULE_LINK_SCORE_THRESHOLD` (default 80) | Shortlist email additionally includes a Cal.com interview scheduling link |
| < `REJECT_SCORE_THRESHOLD` (default 40) | Rejection email sent with specific, AI-derived feedback on the skill gap; status auto-updated to `rejected` |
| In between | "Under review" email sent; status unchanged |

**Email delivery** is provider-agnostic (`services/notifications/email_service.py`):
supports SMTP (e.g. Gmail with an App Password) or SendGrid — selected via
`EMAIL_PROVIDER`. All three email templates (shortlist / rejection / under-review)
are styled HTML with a score badge and clear next steps.

**Interview scheduling** uses a Cal.com public booking link — no OAuth or API key
required, just your event URL, with the candidate's name and email pre-filled via
query parameters.

Notifications are **off by default** (`NOTIFICATIONS_ENABLED=false`) so the system
runs fully without any email setup; enable it once SMTP/SendGrid credentials are
configured.

## 12. Prerequisites — What You Need to Run This

- **Docker & Docker Compose** (recommended — runs backend, frontend, and PostgreSQL
  together with one command), *or* Python 3.11+ and a local/managed PostgreSQL
  instance if running without Docker
- **One LLM API key** (only one is required):
  - Gemini — free tier available at [ai.google.dev](https://ai.google.dev)
  - Groq — free tier, OpenAI-compatible, at [console.groq.com](https://console.groq.com)
  - OpenAI or Anthropic (paid)
  - Or skip this entirely — `LLM_PROVIDER=mock` runs the whole system with no API
    key at all, using deterministic heuristic extraction
- **Optional, for email notifications**: an SMTP account (e.g. Gmail with a
  2FA-enabled App Password) or a SendGrid API key
- **Optional, for interview scheduling links**: a free [Cal.com](https://cal.com)
  account with one event type set up

## 13. Setup

### Environment Variables

Copy `backend/.env.example` to `backend/.env` and fill in values:

| Variable | Purpose |
|---|---|
| `APP_ENV` | `development` / `production` |
| `DATABASE_URL` | SQLAlchemy connection string (Postgres or SQLite) |
| `LLM_PROVIDER` | `mock` / `gemini` / `openai` / `anthropic` / `groq` / `openrouter` / `ollama` |
| `LLM_MODEL` | Model name for the selected provider |
| `GEMINI_API_KEY` / `OPENAI_API_KEY` / `ANTHROPIC_API_KEY` / `GROQ_API_KEY` | Only the key matching `LLM_PROVIDER` is required |
| `MAX_UPLOAD_SIZE_MB` | Upload size limit |
| `NOTIFICATIONS_ENABLED` | `true`/`false` — enables the email automation layer |
| `EMAIL_PROVIDER` | `none` / `smtp` / `sendgrid` |
| `SMTP_HOST` / `SMTP_USERNAME` / `SMTP_PASSWORD` / `SMTP_FROM_EMAIL` | Required if `EMAIL_PROVIDER=smtp` |
| `SENDGRID_API_KEY` / `SENDGRID_FROM_EMAIL` | Required if `EMAIL_PROVIDER=sendgrid` |
| `SHORTLIST_SCORE_THRESHOLD` / `REJECT_SCORE_THRESHOLD` / `SCHEDULE_LINK_SCORE_THRESHOLD` | Score cutoffs for notification tiers |
| `CALCOM_SCHEDULING_URL` | Your public Cal.com event link, for interview scheduling |
| `COMPANY_NAME` | Used in email templates |

`LLM_PROVIDER=mock` requires **no API key** and is the default — the whole system
is fully runnable and demoable without any LLM subscription.

## 14. Database Migrations

```bash
cd backend
alembic upgrade head
```

Migrations create all tables — Jobs, Candidates, Skills, CandidateSkills,
ResumeFiles, Scores, ScoreSkills — with foreign keys, indexes, and the unique
constraint on `skills.normalized_name`.

## 15. Running Locally

### Backend
```bash
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # edit DATABASE_URL, LLM_PROVIDER, etc.
alembic upgrade head
uvicorn app.main:app --reload --port 8000
```

### Frontend
```bash
cd frontend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
export API_BASE_URL=http://localhost:8000
streamlit run app.py
```

## 16. Running with Docker

```bash
docker compose up --build
```

This starts PostgreSQL, the FastAPI backend (running migrations automatically on
startup), and the Streamlit frontend.

- Backend: http://localhost:8000 (Swagger at `/docs`)
- Frontend: http://localhost:8501

## 17. Streamlit Usage

1. **Dashboard** — recruitment metrics: totals, average score, score distribution
   and top-skills charts, top and recent candidates.
2. **Upload Resume** — upload PDF/DOCX, see extraction status and the created candidate.
3. **Create Job** — paste a JD, see extracted required/preferred skills.
4. **Candidates** — search/filter by name, email, skill, experience range, and
   status; shortlist or reject candidates directly from the table.
5. **Candidate Details** — full profile, skills, and screening history.
6. **Screen Candidate** — pick a candidate + job, get an explainable score.
7. **Ranking Dashboard** — pick a job, see all screened candidates ranked by score.

## 18. Screenshots

### Dashboard
![Dashboard](docs/screenshots/dashboard.png)

### Upload Resume
![Upload Resume](docs/screenshots/resume.png)

### Screening Result
![Screening Result](docs/screenshots/screening.png)

### Ranking Dashboard
![Ranking Dashboard](docs/screenshots/ranking.png)

### Candidates
![Candidates](docs/screenshots/candidates.png)

## 19. API Documentation

Swagger UI: `http://localhost:8000/docs` · ReDoc: `http://localhost:8000/redoc`
Full OpenAPI schema is generated from the FastAPI routes/Pydantic models, including
request bodies, response schemas, and validation error shapes.

## 20. API Examples

**Create a job**
```bash
curl -X POST http://localhost:8000/api/jobs \
  -H "Content-Type: application/json" \
  -d '{"title": "Backend Engineer", "raw_description": "Need Python, FastAPI, SQL. 2+ years. Bachelor degree."}'
```

**Upload a resume**
```bash
curl -X POST http://localhost:8000/api/resumes/upload \
  -F "file=@/path/to/resume.pdf"
```

**Run a screening** (triggers email notification automatically if enabled)
```bash
curl -X POST http://localhost:8000/api/screenings \
  -H "Content-Type: application/json" \
  -d '{"candidate_id": "<uuid>", "job_id": "<uuid>"}'
```

**Update candidate status**
```bash
curl -X PATCH http://localhost:8000/api/candidates/<candidate_id>/status \
  -H "Content-Type: application/json" \
  -d '{"status": "shortlisted"}'
```

**Search candidates**
```bash
curl "http://localhost:8000/api/candidates/search?skill=python&min_experience=2&status=shortlisted"
```

**Get job rankings**
```bash
curl http://localhost:8000/api/jobs/<job_id>/rankings
```

## 21. Testing

```bash
cd backend
pip install -r requirements.txt -r requirements-dev.txt
pytest tests/ -v
```

35 tests, all passing, none requiring a real API key (`LLM_PROVIDER=mock` is forced
in `tests/conftest.py`). Coverage includes: health check, PDF and DOCX extraction,
OCR fallback (exercising the real `pytesseract`/`poppler` pipeline against a
generated image-only PDF), file validation edge cases, JD and candidate creation,
candidate search and status filtering, screening creation and score range
validation, job rankings, email notification decision logic and templates, and
not-found error handling across all resources.

## 22. Deployment

### Render / Railway

**PostgreSQL**: provision a managed Postgres instance; copy its connection string.

**Backend (FastAPI)**
- Build command: `pip install -r backend/requirements.txt`
- Start command: `alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- Root directory: `backend`
- Env vars: as listed in section 13
- Health check path: `/api/health`

**Frontend (Streamlit)**
- Build command: `pip install -r frontend/requirements.txt`
- Start command: `streamlit run app.py --server.port $PORT --server.address 0.0.0.0`
- Root directory: `frontend`
- Env vars: `API_BASE_URL` = the deployed backend's public URL

## 23. Design Decisions

- **Provider-agnostic LLM via direct REST calls**, not a heavy SDK/LangChain
  dependency — keeps the dependency surface small and the abstraction easy to audit.
- **Deterministic scoring in application code**, LLM only for structured extraction
  — required for explainability and reproducibility; a rerun of the same screening
  input always yields the same score.
- **Skills stored relationally** with a `normalized_name` unique constraint and a
  small alias table rather than a large synonym database — maintainable,
  extensible, and keeps search on indexed columns.
- **Notifications run as background tasks**, decoupled from the request/response
  cycle — a slow or failed email send never blocks or delays the recruiter seeing
  the screening result.
- **Cal.com over Google Calendar API** for scheduling — a public booking link
  requires no OAuth setup, making the feature usable in minutes rather than requiring
  a full calendar integration flow.
- **SQLite supported alongside PostgreSQL** for local dev/tests via a portable `GUID`
  TypeDecorator — production targets PostgreSQL by default in `docker-compose.yml`
  and `.env.example`.

## 24. Security Considerations

- Upload validation: extension allow-list (`pdf`, `docx`), size cap, empty-file rejection.
- No secrets logged; API keys and SMTP credentials read only from environment
  variables, never committed (`.env` is git-ignored, `.env.example` has empty values).
- SQLAlchemy ORM used throughout — no raw string-interpolated SQL, parameterized
  queries by construction.
- Exception handling never leaks stack traces, SQL, or internal error text to the
  client.
- No sensitive personal attributes beyond name/email/phone (necessary for
  identification) are used in the scoring calculation.
- No authentication layer is included by default; recommended to add before
  exposing any deployment publicly with real candidate data.

## 25. Roadmap

- Authentication and role-based access (recruiter vs. admin).
- Real deduplication of candidates by email/phone across multiple resume uploads.
- Object storage (S3/GCS) for resume files instead of local disk.
- Background job queue (e.g. Celery) for higher-volume resume processing.
- Bulk "screen all candidates against this job" endpoint for the ranking dashboard.
- Configurable scoring weights per job role.
- Google Calendar API integration as an alternative to Cal.com for enterprises
  already standardized on Google Workspace.