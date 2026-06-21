from fastapi import FastAPI
from fastapi.responses import JSONResponse
from app.core.database import Base, engine
from app.models.user import User
from app.models.interviews import InterviewSession
from app.models.audio_response import AudioResponse
import uvicorn




app = FastAPI(
    title="AI Interview Coach",
    description="AI-powered mock interview platform",
    version="1.0.0"
)

@app.get("/health")
def health_check():
    """Health check endpoint to verify API is running."""
    return JSONResponse(
        status_code=200,
        content={
            "status": "healthy",
            "message": "API is running successfully",
            "service": "AI Interview Coach"
        }
    )

if __name__ == "__main__":

    
    print("🚀 Starting AI Interview Coach API...")
    print("📊 Database tables initialized")
    
    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True
    )
