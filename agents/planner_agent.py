import json
from pathlib import Path

from services.groq_client import client
from services.mcp_schema import (
    QuestionContext,
    PlanSchema,
    build_data_schema,
    context_to_json,
    create_mcp_message,
)


class PlannerAgent:

    def __init__(self):
        prompt_path = Path(__file__).resolve().parent.parent / "prompts" / "planner_prompt.txt"
        with prompt_path.open("r", encoding="utf-8") as f:
            self.system_prompt = f.read()

    def plan(
        self,
        question,
        schema,
        metadata
    ):
        prompt = f"""
Question:
{question}

Schema:
{json.dumps(schema, indent=2)}

Metadata:
{json.dumps(metadata, indent=2,default=str)}

Return ONLY JSON.

Format:

{{
  "tool":"python_analysis",
  "code":"valid pandas code"
}}
"""
        #data_schema = build_data_schema(schema)
        #context = QuestionContext(question=question, data_schema=data_schema, metadata=metadata)

        #prompt = context_to_json(context)

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                create_mcp_message("system", self.system_prompt),
                create_mcp_message("user", prompt),
            ],
            temperature=0,
        )

        content = response.choices[0].message.content

        print("\nPLANNER OUTPUT:")
        print(content)

        plan = self._parse_json_response(content)
        return PlanSchema.parse_obj(plan).model_dump()

    def _parse_json_response(self, content):
        if not content:
            raise ValueError("Planner returned an empty response.")

        cleaned = content.replace("```json", "").replace("```", "").strip()
        if not cleaned:
            raise ValueError("Planner response contained only markdown fences.")

        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            start = cleaned.find("{")
            end = cleaned.rfind("}")
            if start != -1 and end != -1 and start < end:
                trimmed = cleaned[start:end + 1]
                try:
                    return json.loads(trimmed)
                except json.JSONDecodeError:
                    pass
            raise ValueError(
                f"Unable to parse JSON from planner response:\n{cleaned}"
            )