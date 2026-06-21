# 🎤 AI Interview Coach

An AI-powered mock interview platform that helps users practice and improve their interview skills through realistic, interactive interviews with AI-generated questions, responses, and feedback.

## ✨ Features

- **Realistic Mock Interviews**: AI-generated interview questions tailored to different industries and roles
- **Audio Processing**: Automatic transcription of user responses using Whisper
- **Real-time Feedback**: AI-powered feedback and analysis of interview performance
- **Interview Sessions**: Track multiple interview sessions with detailed metrics
- **Audio Storage**: Secure storage and retrieval of interview recordings
- **RESTful API**: FastAPI-based REST API for seamless integration
- **Database Persistence**: PostgreSQL integration for reliable data storage

## 🛠️ Tech Stack

- **Framework**: FastAPI
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Audio Processing**: FFmpeg, Whisper, librosa
- **LLM Integration**: OpenAI API with instructor validation
- **Async**: AsyncPG for async database operations
- **Web Server**: Uvicorn

## 📋 Prerequisites

- Python 3.11+
- PostgreSQL 12+
- FFmpeg (for audio processing)
- pip (Python package manager)

## 🚀 Quick Start

### 1. Clone and Setup Virtual Environment

```bash
# Create virtual environment
python -m venv myvenv

# Activate virtual environment
# On Windows:
myvenv\Scripts\activate
# On macOS/Linux:
source myvenv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Create a `.env` file in the project root:

```env
DATABASE_URL=postgresql://user:password@localhost:5432/interview_coach
OPENAI_API_KEY=your_openai_api_key_here
```

### 4. Run the Application

```bash
python app/main.py
```

The API will start at `http://127.0.0.1:8000`

## 📚 API Documentation

Once the application is running, visit:

- **Interactive Docs**: `http://127.0.0.1:8000/docs`
- **ReDoc**: `http://127.0.0.1:8000/redoc`
- **Health Check**: `http://127.0.0.1:8000/health`

## 📁 Project Structure

```
AI-interview-coach/
├── app/
│   ├── core/
│   │   ├── config.py          # Configuration management
│   │   └── database.py        # Database setup and session
│   ├── main.py                # FastAPI application entry point
│   └── __init__.py
├── models/
│   ├── user.py                # User model
│   ├── interviews.py          # InterviewSession model
│   ├── audio_response.py      # AudioResponse model
│   └── __init__.py
├── myvenv/                    # Virtual environment
├── requirements.txt           # Python dependencies
├── .gitignore                 # Git ignore rules
├── .env                       # Environment variables (not in git)
└── README.md                  # This file
```

## 📊 Data Models

### User
- `id`: UUID primary key
- `email`: Unique email address
- `created_at`: Timestamp of account creation
- **Relations**: One-to-many with InterviewSession

### InterviewSession
- `id`: UUID primary key
- `user_id`: Foreign key to User
- `title`: Interview title/description
- `created_at`: Timestamp of session creation
- **Relations**: Many-to-one with User, One-to-many with AudioResponse

### AudioResponse
- `id`: UUID primary key
- `session_id`: Foreign key to InterviewSession
- `audio_path`: Path to stored audio file
- `transcript`: Transcribed text from audio
- `duration_seconds`: Duration of audio
- `created_at`: Timestamp of response creation
- **Relations**: Many-to-one with InterviewSession

## 🔧 Configuration

### Database Connection
Update the `DATABASE_URL` in your `.env` file:

```
DATABASE_URL=postgresql://[user]:[password]@[host]:[port]/[database]
```

### API Keys
Add your OpenAI API key to `.env`:

```
OPENAI_API_KEY=sk-your-key-here
```

## 🚦 Health Check

Test if the API is running:

```bash
curl http://127.0.0.1:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "message": "API is running successfully",
  "service": "AI Interview Coach"
}
```

## 📝 Development

### Running in Development Mode

The application runs with `reload=True` by default, which automatically restarts the server when code changes are detected.

### Database Migrations

Tables are automatically created on application startup via `Base.metadata.create_all()`. For schema changes, consider using Alembic for database migrations:

```bash
pip install alembic
alembic init alembic
```

## 🤝 Contributing

1. Create a feature branch (`git checkout -b feature/amazing-feature`)
2. Commit your changes (`git commit -m 'Add amazing feature'`)
3. Push to the branch (`git push origin feature/amazing-feature`)
4. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For issues and questions, please open an issue on GitHub or contact the development team.

## 🎯 Roadmap

- [ ] Advanced analytics and performance metrics
- [ ] Interview question templates
- [ ] Multi-language support
- [ ] Video interview capability
- [ ] Integration with LinkedIn
- [ ] Export interview reports as PDF

---

**Made with ❤️ for aspiring job seekers**
