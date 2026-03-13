import json
from src.llm.client import LLMClient, LLMClientError

REVIEW_SYSTEM_PROMPT = """You are a senior product analyst and UX consultant.

Your job is to analyse individual screens from a UI design and:
1. State clear assumptions about what each screen does and how it behaves
2. Generate clarification questions for the client to confirm or correct your assumptions

Focus on:
- User interactions and flows (what happens when they click, submit, etc.)
- Business logic (validation rules, error states, edge cases)
- Data requirements (what information is needed, stored, or displayed)
- Navigation and transitions (where does this screen lead)

Do NOT ask about:
- Visual design preferences (colours, fonts, spacing)
- Things that are obvious from the design

Your output must be valid JSON only. No markdown, no explanation outside the JSON."""


REVIEW_USER_PROMPT = """Analyse this screen and generate assumptions and clarification questions.

{screen_context}

Return a JSON object with this exact structure:
{{
  "assumptions": [
    {{
      "id": "A1",
      "text": "Clear statement of what you assume this screen does",
      "confidence": "high | medium | low",
      "reasoning": "Why you believe this"
    }}
  ],
  "questions": [
    {{
      "id": "Q1",
      "assumption_id": "A1",
      "question": "Specific question for the client",
      "context": "Why this matters for development"
    }}
  ],
  "confidence_scores": {{
    "overall": "high | medium | low",
    "reasoning": "Overall confidence in the assumptions"
  }}
}}

Generate as many assumptions and questions as needed to fully clarify this screen.
Focus on anything that would affect how a developer builds this."""

class ReviewGenerator:
    """
    Generates AI assumptions and clarification questions
    for a single Figma screen.
    """

    def __init__(self, llm_client: LLMClient):
        self.llm = llm_client

    async def generate(
        self,
        screen_name: str,
        page_name: str,
        screen_context: str
    ) -> dict:
        """
        Generate assumptions and questions for a single screen.

        Returns a dict with assumptions, questions, confidence_scores.
        """
        prompt = REVIEW_USER_PROMPT.format(
            screen_context=screen_context
        )

        try:
            raw_response = self.llm.complete(prompt, REVIEW_SYSTEM_PROMPT)
            return self._parse_response(raw_response, screen_name)
        except LLMClientError as e:
            raise Exception(f"LLM review generation failed: {e}")
    
    def _parse_response(self, raw: str, screen_name: str) -> dict:
        """
        Parse and validate the LLM JSON response.
        Falls back gracefully if parsing fails.
        """
        try:
            # Strip any accidental markdown fences
            cleaned = raw.strip()
            if cleaned.startswith("```"):
                lines = cleaned.split("\n")
                cleaned = "\n".join(lines[1:-1])

            data = json.loads(cleaned)

            # Validate expected keys exist
            if "assumptions" not in data or "questions" not in data:
                raise ValueError("Missing required keys in response")

            return data

        except (json.JSONDecodeError, ValueError) as e:
            # Return a safe fallback so one bad screen
            # doesn't break the whole pipeline
            print(f"Could not parse LLM response for "
                  f"{screen_name}: {e}")
            return {
                "assumptions": [],
                "questions": [],
                "confidence_scores": {
                    "overall": "low",
                    "reasoning": "Could not parse AI response"
                }
            }