# AI Interview Coach - Project File Structure

This document explains the organization and architectural layers of the project.

## Directory Layout

```text
.
├── app/
│   ├── core/                # Core configurations and global settings
│   │   ├── config.py        # Environmental settings
│   │   ├── database.py      # Database setup and session handlers
│   │   └── security.py      # Password hashing/security configuration (pwd_context)
│   │
│   ├── models/              # SQLAlchemy database tables and mappings
│   │   ├── answer_evaluation.py
│   │   ├── answers.py
│   │   ├── audio_response.py
│   │   ├── interviews.py
│   │   ├── questions.py
│   │   └── user.py
│   │
│   ├── schemas/             # Pydantic models for request/response serialization
│   │   ├── auth.py          # Registration and Login body definitions
│   │   └── sessions.py      # Session and Question parameters
│   │
│   ├── services/            # Core business logic and database access layer
│   │   ├── auth_service.py      # Registration and Login execution
│   │   ├── session_service.py   # CRUD for mock sessions
│   │   ├── question_service.py  # LLM generation and retrieval of questions
│   │   └── answer_service.py    # Transcription, evaluation, and retries (accepts a custom transcribe function)
│   │
│   ├── routers/             # API routes matching endpoints to service actions
│   │   ├── root.py          # `/` and `/health` check endpoints
│   │   ├── auth.py          # `/auth/*` routes
│   │   ├── sessions.py      # `/sessions/*` routes
│   │   ├── answers.py       # `/sessions/.../answer/*` routes (uses dynamic transcription function)
│   │   └── responses.py     # `/sessions/.../responses/*` routes
│   │
│   ├── utils/               # Internal utility functions (unchanged legacy helpers)
│   │   ├── evaluateAnswers.py   # Groq evaluation client logic
│   │   ├── genrateQuestions.py  # Groq question generation client logic
│   │   ├── transcribe.py        # Faster‑Whisper transcription (default)
│   │   ├── transcribe_ammar.py  # Whisper.cpp CLI wrapper (partner's version)
│   │   └── util.py              # General helper functions (such as save upload)
│   │
│   ├── test/                # Unit and integration test files
│   │   ├── test_modellist.py
│   │   └── test_whisper.py  # Moved from utils to tests
│   │
│   ├── main.py              # Main API entrypoint – registers routers and sets `app.state.transcribe_fn = transcribe_audio`
│   └── main_ammar.py        # Partner's entrypoint – registers the same routers but sets `app.state.transcribe_fn = transcribe_audio_ammar`
│
├── requirements.txt         # Consolidated Python dependencies list
└── alembic.ini              # Database migration tool configuration
```

## Key Architecture Layers

1. **Routing Layer (`app/routers/`)** – Defines fastapi routes, validates request parameters, and delegates all business logic to the Services. The **answers router** now extracts the transcription function from `request.app.state` so the same service can be used with either transcription backend.

2. **Service Layer (`app/services/`)** – Implements core operations. `save_and_transcribe_answer` now accepts an optional `transcribe_fn` argument, defaulting to the standard `transcribe_audio`. This enables the `main_ammar.py` entrypoint to inject the Whisper‑CPP based `transcribe_audio_ammar` without altering service code.

3. **Database Layer (`app/models/` & `app/core/database.py`)** – Defines SQLAlchemy models and provides session handling.

4. **Validation Layer (`app/schemas/`)** – Houses Pydantic schemas for request payloads and response models.

5. **Core Configuration (`app/core/`)** – Includes the database engine, session factory, and the shared password‑hashing context in `security.py`.

## Differences between `main.py` and `main_ammar.py`
- **`main.py`**: Uses the Python‑native `faster‑whisper` package for transcription and registers it via:
  ```python
  app.state.transcribe_fn = transcribe_audio
  ```
- **`main_ammar.py`**: Uses the Whisper.cpp CLI wrapper (`transcribe_audio_ammar`) and registers it with:
  ```python
  app.state.transcribe_fn = transcribe_audio_ammar
  ```
- Both entrypoints load **exactly the same set of routers** and therefore expose an identical public API; only the underlying transcription engine differs.

---

## How the Dynamic Transcription Works
1. The **answers router** receives the incoming request and reads `transcribe_fn` from `request.app.state`.
2. It forwards this callable to `save_and_transcribe_answer`.
3. The service function calls the provided `transcribe_fn` (or falls back to the default `transcribe_audio`).
4. This design keeps the service layer pure and testable while allowing each entrypoint to swap the transcription backend with a single line of configuration.

---

## Cleanup & Refactoring Summary
- Removed all duplicate/backup files (`* 2.py`).
- Moved the lone test script from `app/utils/` to `app/test/`.
- Consolidated route definitions into dedicated router modules.
- Centralised business logic into service modules.
- Added `app.state.transcribe_fn` handling for both main entrypoints.
- Updated documentation (this file) to reflect the new layout and dynamic transcription mechanism.

---

*This structure provides a clean, maintainable codebase that can easily switch between transcription back‑ends, supports future extensions, and follows modern FastAPI best practices.*
