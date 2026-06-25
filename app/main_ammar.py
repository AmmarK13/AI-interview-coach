from fastapi import FastAPI
import uvicorn
from app.routers import root, auth, sessions, answers, responses, users
from app.utils.transcribe_ammar import transcribe_audio_ammar

app = FastAPI(
    title="AI Interview Coach",
    description="AI-powered mock interview platform",
    version="1.0.0"
)

app.state.transcribe_fn = transcribe_audio_ammar

# Register routers
app.include_router(root.router)
app.include_router(auth.router)
app.include_router(sessions.router)
app.include_router(answers.router)
app.include_router(responses.router)
app.include_router(users.router)


if __name__ == "__main__":
    print("🚀 Starting AI Interview Coach API (Ammar Edition)...")
    
    uvicorn.run(
        "app.main_ammar:app",
        host="127.0.0.1",
        port=8000,
        reload=True
    )
