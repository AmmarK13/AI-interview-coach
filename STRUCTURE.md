# AI Interview Coach - Project File Structure

This document explains the organization and architectural layers of the project.

## Directory Layout

```text
.
├── app/
│   ├── audio/               # Audio file storage directories
│   │   ├── answers/         # Saved user response recordings (answers) & evaluation speech
│   │   └── question/        # TTS generated question & evaluation speech files
│   │
│   ├── core/                # Core configurations and global settings
│   │   ├── config.py        # Environmental settings
│   │   ├── database.py      # Database setup and session handlers
│   │   ├── security.py      # Password hashing/security configuration
│   │   └── tts_models/      # Offline Piper TTS voice model files (.onnx & .json)
│   │
│   ├── models/              # SQLAlchemy database tables and mappings
│   │   ├── answer_evaluation.py
│   │   ├── answers.py
│   │   ├── audio_response.py
│   │   ├── interviews.py
│   │   ├── questions.py
│   │   ├── session_summary.py
│   │   ├── user.py
│   │   ├── user_progress.py
│   │   └── voice_output.py  # Tracks all TTS speech assets
│   │
│   ├── schemas/             # Pydantic models for request/response serialization
│   │   ├── auth.py          # Registration and Login body definitions
│   │   └── sessions.py      # Session and Question parameters
│   │
│   ├── services/            # Core business logic and database access layer
│   │   ├── auth_service.py      # Registration and Login execution
│   │   ├── session_service.py   # CRUD for mock sessions
│   │   ├── question_service.py  # LLM question handling and TTS speak generation
│   │   ├── answer_service.py    # Transcription, evaluation, and retries
│   │   └── user_service.py      # User progress calculation and sync
│   │
│   ├── routers/             # API routes matching endpoints to service actions
│   │   ├── root.py          # `/` and `/health` check endpoints
│   │   ├── auth.py          # `/auth/*` routes
│   │   ├── sessions.py      # `/sessions/*` routes
│   │   ├── answers.py       # `/sessions/.../answer/*` routes
│   │   ├── responses.py     # `/sessions/.../responses/*` routes
│   │   ├── users.py         # `/users/{user_id}/progress` endpoint
│   │   └── questions.py     # `/sessions/.../questions/.../speak` endpoints
│   │
│   ├── utils/               # Internal utility and helper modules
│   │   ├── evaluateAnswers.py   # Groq evaluation client logic
│   │   ├── genrateQuestions.py  # Groq question generation client logic
│   │   ├── transcribe.py        # Faster‑Whisper transcription (default)
│   │   ├── transcribe_ammar.py  # Whisper.cpp CLI wrapper (partner's version)
│   │   ├── tts.py               # Piper TTS voice generation helper
│   │   └── util.py              # General helper functions (file saving)
│   │
│   ├── test/                # Unit and integration test files
│   │   ├── test_modellist.py
│   │   ├── test_whisper.py
│   │   └── test_tts.py      # Tests Piper TTS audio generation
│   │
│   ├── main.py              # Main API entrypoint (using standard transcribe)
│   └── main_ammar.py        # Partner's entrypoint (using Whisper.cpp transcription)
│
├── requirements.txt         # Consolidated Python dependencies list
└── alembic.ini              # Database migration tool configuration
```

## Key Architecture Layers

1. **Routing Layer (`app/routers/`)** – Defines fastapi routes, validates request parameters, and delegates all business logic to the Services.

2. **Service Layer (`app/services/`)** – Implements core business logic. 
   - `session_service.py` manages interview sessions.
   - `question_service.py` generates new questions and implements TTS generation using the local Piper engine.
   - `user_service.py` computes running progress records for users.
   - `answer_service.py` handles audio transcription and LLM-based evaluation.

3. **Database Layer (`app/models/` & `app/core/database.py`)** – Defines SQLAlchemy models and provides session handling.

4. **Validation Layer (`app/schemas/`)** – Houses Pydantic schemas for request payloads and response models.

5. **Core Configuration (`app/core/`)** – Includes the database engine, session factory, shared security context, and holds downloaded TTS voice models.

---

## Differences between `main.py` and `main_ammar.py`
- **`main.py`**: Uses the Python‑native `faster‑whisper` package for transcription.
- **`main_ammar.py`**: Uses the Whisper.cpp CLI wrapper (`transcribe_audio_ammar`) and preloads extra models.
- Both entrypoints load the same routes and expose the same public API.
