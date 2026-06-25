from pydantic import BaseModel
from app.utils.genrateQuestions import ExperienceLevel, QuestionType, Difficulty
from enum import Enum

class CreateSession(BaseModel):
    userid: str
    title: str
    role: str
    level: ExperienceLevel

class Status(str,Enum):
    complete ="complete"
    inprogress="inprogress"


class GenerateQuestionRequest(BaseModel):
    question_type: QuestionType
    difficulty: Difficulty


class SessionComplete(BaseModel):
    userid: str
    sessionid:str