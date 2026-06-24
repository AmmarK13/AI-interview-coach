

from __future__ import annotations

import json
import os
import re
import random
from enum import Enum
from typing import Any

from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")


class ExperienceLevel(str, Enum):
    intern = "intern"
    junior = "junior"
    mid = "mid"
    senior = "senior"
    lead = "lead"


class QuestionType(str, Enum):
    behavioral = "behavioral"
    technical = "technical"
    situational = "situational"


class Difficulty(str, Enum):
    easy = "easy"
    medium = "medium"
    hard = "hard"


try:
    from google import genai
except ImportError:  # pragma: no cover - optional dependency at runtime
    genai = None


def _normalize_enum_value(value: str | Enum, enum_cls: type[Enum], field_name: str) -> str:
    valid_values = {item.value for item in enum_cls}

    if isinstance(value, Enum):
        normalized = str(getattr(value, "value", value)).strip().lower()
    else:
        normalized = str(value).strip().lower()

    valid_values = {item.value for item in enum_cls}
    if normalized not in valid_values:
        raise ValueError(f"Invalid {field_name}: {value}. Expected one of: {sorted(valid_values)}")
    return normalized


def _canonical_text(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", value.lower()).strip()


def _difficulty_for_level(level: str) -> list[Difficulty]:
    if level in {ExperienceLevel.intern.value, ExperienceLevel.junior.value}:
        return [Difficulty.easy, Difficulty.medium, Difficulty.hard]
    if level == ExperienceLevel.mid.value:
        return [Difficulty.easy, Difficulty.medium, Difficulty.hard]
    return [Difficulty.medium, Difficulty.hard, Difficulty.hard]


def _question_bank(role: str, level: str, question_type: str) -> list[str]:
    question_banks = {
        QuestionType.technical.value: [
            f"Explain how you would design a scalable system for a {level} {role} role.",
            f"What trade-offs would you consider when optimizing a backend service as a {level} {role}?",
            f"How would you debug a production issue in a distributed computer science system as a {level} {role}?",
            f"How would you design an API rate-limiting strategy for a {level} {role}?",
            f"How would you choose between SQL and NoSQL for a product feature as a {level} {role}?",
        ],
        QuestionType.behavioral.value: [
            f"Tell me about a time you solved a difficult technical problem as a {level} {role}.",
            f"How do you approach collaboration when working with engineers, product, and design as a {level} {role}?",
            f"Describe a situation where you had to learn a new technology quickly as a {level} {role}.",
            f"Tell me about a time you disagreed with a technical decision as a {level} {role} and how you handled it.",
            f"Describe a moment when you improved a system or workflow as a {level} {role}.",
        ],
        QuestionType.situational.value: [
            f"How would you handle a critical outage in a system you own as a {level} {role}?",
            f"What would you do if a deadline changed while a major technical task was in progress as a {level} {role}?",
            f"If a teammate disagreed with your approach to a technical design, how would you respond as a {level} {role}?",
            f"How would you respond if a deployment failed just before a demo as a {level} {role}?",
            f"What would you prioritize first if you inherited a messy codebase as a {level} {role}?",
        ],
    }

    return question_banks.get(question_type, question_banks[QuestionType.technical.value])


def _fallback_question(
    role: str,
    level: str,
    question_type: str,
    difficulty: str,
    previous_questions: list[str] | None = None,
) -> dict[str, Any]:
    templates = _question_bank(role, level, question_type)
    seen_questions = {_canonical_text(question) for question in (previous_questions or []) if question}

    available_templates = [
        question for question in templates if _canonical_text(question) not in seen_questions
    ] or templates

    question_text = random.choice(available_templates)

    return {
        "role": role,
        "level": level,
        "question_type": question_type,
        "question": {
            "key": f"{question_type}|{level}|{difficulty}",
            "question_type": question_type,
            "level": level,
            "difficulty": difficulty,
            "question": question_text,
        },
        "source": "fallback",
    }


def _extract_json_payload(text: str) -> Any:
    cleaned = text.strip()
    cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\s*```$", "", cleaned)
    return json.loads(cleaned)


def _build_prompt(
    role: str,
    level: str,
    question_type: str,
    difficulty: str,
    previous_questions: list[str] | None = None,
) -> str:
    previous_questions_block = "\n".join(f"- {question}" for question in (previous_questions or []))
    previous_questions_text = previous_questions_block or "None"

    return f"""
You are an interview question generator for computer science and other technical roles.

Generate exactly 1 question for this profile:
- role: {role}
- level: {level}
- question_type: {question_type}
- difficulty: {difficulty}

Rules:
- Questions must be technical, computer-science related, and suitable for a hiring interview.
- Match the question_type as much as possible.
- Use the requested difficulty exactly.
- Avoid generic, non-technical, or off-topic questions.
- Do not repeat any previous questions listed below.
- Return valid JSON only. No markdown, no code fences, no explanation.

Previous questions already asked for this session:
{previous_questions_text}

Return the result with this exact structure:
{{
  "role": "{role}",
  "level": "{level}",
  "question_type": "{question_type}",
  "question": {{
    "key": "{question_type}|{level}|{difficulty}",
    "question_type": "{question_type}",
    "level": "{level}",
    "difficulty": "{difficulty}",
    "question": "..."
  }}
}}
""".strip()


def genrate_questions(
    role: str,
    level: str,
    question_type: str,
    difficulty: str,
    previous_questions: list[str] | None = None,
) -> dict[str, Any]:
    
    #Improve cost by getting a bunch of questions instead of 1 by 1
    """Generate interview questions using Gemini and return structured JSON.

    The output is designed to be easy to store in a database or return from an API.
    """

    normalized_level = _normalize_enum_value(level, ExperienceLevel, "level")
    normalized_question_type = _normalize_enum_value(question_type, QuestionType, "question_type")
    normalized_difficulty = _normalize_enum_value(difficulty, Difficulty, "difficulty")
    normalized_role = str(role).strip()
    seen_questions = {_canonical_text(question) for question in (previous_questions or []) if question}

    if not normalized_role:
        raise ValueError("role cannot be empty")
    

    print("GEMINI_API_KEY loaded:", bool(GEMINI_API_KEY))
    print("genai imported:", genai is not None)

    if not GEMINI_API_KEY or genai is None:

        return _fallback_question(
            normalized_role,
            normalized_level,
            normalized_question_type,
            normalized_difficulty,
            previous_questions,
        )

    try:
        client = genai.Client(api_key=GEMINI_API_KEY)
        
        prompt = _build_prompt(
            normalized_role,
            normalized_level,
            normalized_question_type,
            normalized_difficulty,
            previous_questions,
        )
        print("Calling Gemini...")
        response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        )
        payload = _extract_json_payload(response.text)
        print("Gemini response received")

        if not isinstance(payload, dict):
            return _fallback_question(

                normalized_role,
                normalized_level,
                normalized_question_type,
                normalized_difficulty,
                previous_questions,
            )

        question = payload.get("question")
        if not isinstance(question, dict):
            return _fallback_question(
                normalized_role,
                normalized_level,
                normalized_question_type,
                normalized_difficulty,
                previous_questions,
            )

        question_text = str(question.get("question", "")).strip()
        difficulty_value = str(question.get("difficulty", "")).strip().lower()
        if not question_text or difficulty_value != normalized_difficulty:
            return _fallback_question(
                normalized_role,
                normalized_level,
                normalized_question_type,
                normalized_difficulty,
                previous_questions,
                previous_questions,
            )

        if _canonical_text(question_text) in seen_questions:
            return _fallback_question(
                normalized_role,
                normalized_level,
                normalized_question_type,
                normalized_difficulty,
                previous_questions,
            )

        return {
            "role": normalized_role,
            "level": normalized_level,
            "question_type": normalized_question_type,
            "question": {
                "key": f"{normalized_question_type}|{normalized_level}|{normalized_difficulty}",
                "question_type": normalized_question_type,
                "level": normalized_level,
                "difficulty": normalized_difficulty,
                "question": question_text,
            },
            "source": "gemini",
        }

    except Exception as e:
        print("Gemini Error:", e)
        return _fallback_question(
            normalized_role,
            normalized_level,
            normalized_question_type,
            normalized_difficulty,
            previous_questions,
        )
