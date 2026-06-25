from pydantic import BaseModel
from app.utils.genrateQuestions import ExperienceLevel, QuestionType, Difficulty

class CreateSession(BaseModel):
    userid: str
    title: str
    role: str
    level: ExperienceLevel

class GenerateQuestionRequest(BaseModel):
    question_type: QuestionType
    difficulty: Difficulty
