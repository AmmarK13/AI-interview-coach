from __future__ import annotations

import json
import os
import re
from typing import Any

from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

try:
    # pyrefly: ignore [missing-import]
    from groq import Groq
except ImportError:  # pragma: no cover - optional dependency at runtime
    Groq = None


def _extract_json_payload(text: str) -> Any:
    cleaned = text.strip()
    cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\s*```$", "", cleaned)
    return json.loads(cleaned)


def _fallback_evaluation(answer: str) -> dict[str, Any]:
    return {
        "score": 5.0,
        "strengths": ["Answer was submitted successfully."],
        "weaknesses": ["AI evaluation was temporarily unavailable or failed."],
        "feedback": "We were unable to generate detailed AI feedback for this answer at this moment. Please check your connection and configuration.",
        "improved_answer": answer,
    }


def _build_evaluation_prompt(question: str, answer: str) -> str:
    return f"""
You are an expert technical interviewer and computer science coach.
Evaluate the user's answer to the given question.

Question:
{question}

User's Answer:
{answer}

Evaluate the user's answer critically and constructively based on correctness, clarity, completeness, and structure.

Rules:
1. Provide a numeric score from 0.0 to 10.0.
2. Identify 2-4 distinct strengths of the answer.
3. Identify 2-4 distinct weaknesses or areas for improvement.
4. Write detailed, constructive feedback on how they can improve.
5. Provide a perfect, model "improved_answer" that demonstrates how a top-tier candidate would answer this question.
6. Return valid JSON only. No markdown, no code fences, no explanation.

Return the result with this exact JSON structure:
{{
  "score": 8.5,
  "strengths": [
    "strength 1",
    "strength 2"
  ],
  "weaknesses": [
    "weakness 1",
    "weakness 2"
  ],
  "feedback": "Detailed overall feedback text...",
  "improved_answer": "A perfect, high-scoring version of the answer..."
}}
""".strip()


def evaluate_answer(question: str, answer: str) -> dict[str, Any]:
    """Evaluates an interview answer using Groq and returns structured evaluation metrics."""
    
    print("GROQ_API_KEY loaded:", bool(GROQ_API_KEY))
    print("Groq imported:", Groq is not None)

    if not GROQ_API_KEY or Groq is None:
        return _fallback_evaluation(answer)

    try:
        client = Groq(api_key=GROQ_API_KEY)
        prompt = _build_evaluation_prompt(question, answer)
        
        print("Calling GROQ for evaluation...")
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            response_format={"type": "json_object"},
        )
        
        payload = _extract_json_payload(response.choices[0].message.content)
        print("GROQ evaluation response received")

        # Validate and cast fields to match target types
        score = float(payload.get("score", 5.0))
        strengths = list(payload.get("strengths", []))
        weaknesses = list(payload.get("weaknesses", []))
        feedback = str(payload.get("feedback", "")).strip()
        improved_answer = str(payload.get("improved_answer", "")).strip()

        if not feedback or not improved_answer:
            raise ValueError("Missing essential fields in evaluation payload")

        return {
            "score": round(score, 1),
            "strengths": strengths,
            "weaknesses": weaknesses,
            "feedback": feedback,
            "improved_answer": improved_answer,
        }

    except Exception as e:
        print("Groq Evaluation Error:", e)
        return _fallback_evaluation(answer)
