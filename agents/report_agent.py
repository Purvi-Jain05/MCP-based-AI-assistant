from pathlib import Path

from services.groq_client import client
from services.mcp_schema import (
    ReportContext,
    create_mcp_message,
    context_to_json,
)


class ReportAgent:

    def __init__(self):
        prompt_path = Path(__file__).resolve().parent.parent / "prompts" / "report_prompt.txt"
        with prompt_path.open("r", encoding="utf-8") as f:
            self.system_prompt = f.read()

    def generate(
        self,
        question,
        observations
    ):
        report_context = ReportContext(
            question=question,
            observations=observations,
        )

        prompt = context_to_json(report_context)

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                create_mcp_message("system", self.system_prompt),
                create_mcp_message("user", prompt),
            ],
            temperature=0.2,
        )

        return response.choices[0].message.content