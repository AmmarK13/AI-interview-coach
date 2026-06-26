# 🎤 AI Interview Coach

An AI-powered mock interview platform that helps users practice and improve their interview skills through realistic, interactive interviews with AI-generated questions, voice responses, transcription, and instant evaluation.

---

## ✨ Features

- **Realistic Mock Interviews**: AI-generated interview questions tailored to different industries, roles, and experience levels.
- **Local Audio Processing**: Automatic transcription of user voice responses using Whisper (`faster-whisper` or `whisper.cpp`).
- **Local Text-to-Speech (TTS)**: Offline voice generation for questions and evaluations using the fast, local **Piper TTS** engine.
- **Real-time Feedback**: AI-powered feedback, score analysis, strengths, weaknesses, and improved answers.
- **User Progress & History**: Track completed interviews, overall average scores, highest achievements, and complete session history over time.
- **RESTful API**: FastAPI-based backend with clean validation schemas and database persistence.
- **Database Migrations**: Fully managed database schema updates via Alembic.

---

## 🛠️ Tech Stack

- **Framework**: FastAPI
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Audio Transcription**: Whisper (Faster-Whisper / Whisper.cpp)
- **Text-to-Speech**: Piper TTS (local ONNX runtime)
- **LLM Integration**: Groq API (LLaMA-3 / Mixtral models)
- **Migrations**: Alembic
- **Web Server**: Uvicorn

---

## 📋 Prerequisites

- **Python 3.10+**
- **PostgreSQL 12+**
- **FFmpeg** (required for audio transcription processing)
- **A Groq API Key** (configured in your environment)

---

## 🚀 Quick Start

### 1. Clone and Setup Virtual Environment
```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
# On macOS/Linux:
source .venv/bin/activate
# On Windows:
.venv\Scripts\activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Download TTS Model Files
Piper runs fully offline and requires a voice model. Download the standard English voice files:
```bash
mkdir -p app/core/tts_models

# Download ONNX model file
curl -L "https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/en/en_US/lessac/medium/en_US-lessac-medium.onnx" -o app/core/tts_models/en_US-lessac-medium.onnx

# Download config json file
curl -L "https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/en/en_US/lessac/medium/en_US-lessac-medium.onnx.json" -o app/core/tts_models/en_US-lessac-medium.onnx.json
```

### 4. Configure Environment Variables
Create a `.env` file in the root of the project:
```env
DATABASE_URL="postgresql://user:password@localhost:5432/interview_coach"
DEBUG=true
PORT=8000
GROQ_API_KEY="your_groq_api_key"
```

### 5. Run Database Migrations
Apply all migration revisions to bring your local database schema up-to-date:
```bash
alembic upgrade head
```

### 6. Run the Application
Start the FastAPI server:
```bash
# To run using standard faster-whisper transcription:
python app/main.py

# To run using Ammar's whisper.cpp configuration:
python app/main_ammar.py
```
The API will be available at `http://127.0.0.1:8000`.

---

## 📚 API Documentation & Endpoints

Once the application is running, visit:
- **Swagger UI**: `http://127.0.0.1:8000/docs`
- **ReDoc**: `http://127.0.0.1:8000/redoc`

### Core Endpoints

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| **POST** | `/sessions` | Create a new mock interview session |
| **GET** | `/sessions` | Fetch all sessions for a user |
| **POST** | `/sessions/{session_id}/questions/generate` | Generate next LLM question |
| **POST** | `/sessions/{session_id}/questions/{question_id}/speak` | Stream TTS audio for the question |
| **POST** | `/sessions/{session_id}/questions/{question_id}/answer/evaluation/speak` | Stream TTS audio for evaluation feedback |
| **POST** | `/session/{session_id}/complete` | Finish session and compile metrics summary |
| **GET** | `/user/{user_id}/sessions/history` | Return all completed session summaries |
| **GET** | `/users/{user_id}/progress` | Get user progress metrics (best score, avg score, total interviews) |

---

## 📁 Project Structure

Please refer to [STRUCTURE.md](file:///Users/umernadeem/Desktop/personal/AI-interview-coach/AI-interview-coach/STRUCTURE.md) for a detailed walkthrough of the architectural directories, service classes, and execution flows.
