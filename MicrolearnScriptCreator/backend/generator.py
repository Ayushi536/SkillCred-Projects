"""
backend/generator.py
Core LLM integration: build prompt, call Gemini (google-genai), return parsed JSON.

Notes:
- The generator returns a dict with keys:
  - title (str)
  - total_seconds (int)
  - scenes (list of dicts with keys: scene (int), heading, narration, visuals (list), est_seconds)
"""

import os
import json
import re
from typing import Dict, Any
from dotenv import load_dotenv

load_dotenv()  # Load variables from .env if present

from google import genai
from google.genai import types
import google.genai as genai

CLIENT = genai.Client(api_key=os.environ["GEMINI_API_KEY"])




DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "gemini-2.5-flash")


SYSTEM_INSTRUCTION = (
    "You are an expert microlearning script writer. "
    "Given structured inputs, return ONLY valid JSON (no extra commentary) following this schema:\n"
    "{\n"
    '  "title": "string",\n'
    '  "total_seconds": integer,   # between 60 and 120\n'
    '  "scenes": [\n'
    '    { "scene": integer, "heading": "string", "narration": "string", "visuals": ["string", ...], "est_seconds": integer }\n'
    '  ]\n'
    "}\n"
    "Constraints:\n"
    "- 3 to 6 scenes\n"
    "- Total seconds must be 60-120\n"
    "- Each scene: short narration, ideally 8-30 seconds\n"
    "- Visual suggestions should be 1-4 concise items per scene\n    "
)

def _build_user_prompt(topic: str, audience: str, difficulty: str, tone: str, language: str, target_seconds: int) -> str:
    return (
        f"Topic: {topic}\n"
        f"Target audience: {audience}\n"
        f"Difficulty: {difficulty}\n"
        f"Tone/style: {tone}\n"
        f"Language: {language}\n"
        f"Target total seconds: {target_seconds}\n\n"
        "Create a short explainer video script. Output strictly JSON using the schema provided in the system instruction."
    )

# def _extract_first_json(text: str) -> str:
#     # Basic extraction of first { ... } block — tolerant helper
#     match = re.search(r"\{(?:[^{}]|(?R))*\}", text, flags=re.DOTALL)
#     if match:
#         return match.group(0)
#     # fallback: try to find lines starting with '{' to last '}' pair
#     try:
#         start = text.index("{")
#         end = text.rindex("}") + 1
#         return text[start:end]
#     except ValueError:
#         return text  # will fail later

def _extract_first_json(text: str) -> str:
    start = text.find("{")
    if start == -1:
        return text  # No JSON found

    brace_count = 0
    for i, char in enumerate(text[start:], start):
        if char == "{":
            brace_count += 1
        elif char == "}":
            brace_count -= 1
            if brace_count == 0:
                return text[start:i+1]
    return text  # Fallback if unbalanced



def generate_script(
    topic: str,
    audience: str = "general public",
    difficulty: str = "beginner",
    tone: str = "informal",
    language: str = "English",
    target_seconds: int = 90,
) -> Dict[str, Any]:
    """
    Main entrypoint: returns parsed script dict.
    May raise ValueError if model doesn't return JSON parseable text.
    """
    prompt = _build_user_prompt(topic, audience, difficulty, tone, language, target_seconds)

    # Use system instruction via config to increase reliability of structured output
    config = types.GenerateContentConfig(system_instruction=SYSTEM_INSTRUCTION)

    response = CLIENT.models.generate_content(
        model=DEFAULT_MODEL,
        contents=prompt,
        config=config,
    )

    # response.text is the textual content returned (docs show this property)
    raw = getattr(response, "text", None)
    if raw is None:
        # Some SDKs return a different structure; fall back to str()
        raw = str(response)

    # attempt to parse JSON strictly; if fail, try to extract first JSON block
    try:
        parsed = json.loads(raw)
        return parsed
    except json.JSONDecodeError:
        candidate = _extract_first_json(raw)
        try:
            parsed = json.loads(candidate)
            return parsed
        except Exception as e:
            raise ValueError(f"Unable to parse JSON from model response. Raw response:\n{raw}") from e
