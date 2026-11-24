import json
from pathlib import Path

from services.groq_client import client
from services.mcp_schema import (
    OrchestratorContext,
    OrchestratorDecision,
    create_mcp_message,
    context_to_json,
)


class OrchestratorAgent:

    def __init__(self):
        prompt_path = Path(__file__).resolve().parent.parent / "prompts" / "orchestrator_prompt.txt"
        with prompt_path.open("r", encoding="utf-8") as f:
            self.system_prompt = f.read()

    def decide(
        self,
        question,
        observations
    ):
        context = OrchestratorContext(
            question=question,
            observations=observations,
        )

        prompt = context_to_json(context)

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                create_mcp_message("system", self.system_prompt),
                create_mcp_message("user", prompt),
            ],
            temperature=0,
        )

        content = response.choices[0].message.content
        decision = self._parse_json_response(content)
        return OrchestratorDecision.parse_obj(decision).model_dump()

    def _parse_json_response(self, content):
        if not content:
            raise ValueError("Orchestrator returned an empty response.")

        cleaned = content.replace("```json", "").replace("```", "").strip()
        if not cleaned:
            raise ValueError("Orchestrator response contained only markdown fences.")

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
                f"Unable to parse JSON from orchestrator response:\n{cleaned}"
            )