from fastapi import FastAPI
import uvicorn
from app.routers import root, auth, sessions, answers, responses
from app.utils.transcribe import transcribe_audio

app = FastAPI(
    title="AI Interview Coach",
    description="AI-powered mock interview platform",
    version="1.0.0"
)

app.state.transcribe_fn = transcribe_audio

# Register routers
app.include_router(root.router)
app.include_router(auth.router)
app.include_router(sessions.router)
app.include_router(answers.router)
app.include_router(responses.router)


if __name__ == "__main__":
    print("🚀 Starting AI Interview Coach API...")
    
    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True
    )
