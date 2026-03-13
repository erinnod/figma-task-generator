from src.figma.models import DesignContext


SYSTEM_PROMPT = """You are a senior software architect and engineering lead.

Your role is to analyse UI design specifications and generate comprehensive, 
structured development task breakdowns for engineering teams.

When given a design context, you must:
1. Reason about what functionality each screen and component implies
2. Identify frontend, backend, and database work required
3. Generate specific, actionable development tasks
4. Estimate complexity for each task (low / medium / high)
5. Identify dependencies between tasks where relevant

Your output must be valid JSON matching the exact schema provided.
Do not include any text outside the JSON structure.
Do not add markdown code fences.
Return only the raw JSON object."""


def build_task_generation_prompt(context: DesignContext, llm_context: str) -> str:
    return f"""Analyse the following Figma design and generate a complete 
development task breakdown.

{llm_context}

Generate development tasks for this design. Return a JSON object with 
this exact structure:

{{
  "project_name": "string",
  "summary": "string — one paragraph describing what this product is",
  "total_tasks": number,
  "tasks": {{
    "frontend": [
      {{
        "id": "FE-001",
        "title": "string",
        "description": "string",
        "complexity": "low | medium | high",
        "screens_referenced": ["screen name"],
        "acceptance_criteria": ["criterion 1", "criterion 2"]
      }}
    ],
    "backend": [
      {{
        "id": "BE-001", 
        "title": "string",
        "description": "string",
        "complexity": "low | medium | high",
        "acceptance_criteria": ["criterion 1", "criterion 2"]
      }}
    ],
    "database": [
      {{
        "id": "DB-001",
        "title": "string", 
        "description": "string",
        "complexity": "low | medium | high",
        "acceptance_criteria": ["criterion 1", "criterion 2"]
      }}
    ],
    "testing": [
      {{
        "id": "TEST-001",
        "title": "string",
        "description": "string",
        "complexity": "low | medium | high"
      }}
    ]
  }}
}}

Generate thorough, specific tasks. A senior engineer reading these tasks 
should have everything they need to begin implementation immediately."""