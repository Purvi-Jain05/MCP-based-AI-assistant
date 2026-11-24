from __future__ import annotations

from typing import Any, Dict, List, Literal

from pydantic import BaseModel, Field, model_validator


class DataTableSchema(BaseModel):
    name: str
    columns: List[str]


class DataSchema(BaseModel):
    tables: List[DataTableSchema]


class QuestionContext(BaseModel):
    question: str
    data_schema: DataSchema
    metadata: Dict[str, Any] | None = None


class PlanSchema(BaseModel):
    tool: str = Field(default="python_analysis")
    code: str


class Observation(BaseModel):
    tool: str
    code: str
    result: str


class OrchestratorContext(BaseModel):
    question: str
    observations: List[Observation]


class ReportContext(BaseModel):
    question: str
    observations: List[Observation]


class OrchestratorDecision(BaseModel):
    action: Literal["continue", "finish"]
    reason: str | None = None
    next_question: str | None = None

    @model_validator(mode="after")
    def validate_continue(cls, model):
        if model.action == "continue" and not model.next_question:
            raise ValueError("next_question is required when action is continue")
        return model


PYTHON_ANALYSIS_TOOL: Dict[str, Any] = {
    "type": "function",
    "function": {
        "name": "python_analysis",
        "description": "Executes pandas code on the ecommerce dataset and returns the result in `result`.",
        "parameters": {
            "type": "object",
            "properties": {
                "code": {
                    "type": "string",
                    "description": "Pandas code to execute using available DataFrames. Must assign the final answer to variable result."
                }
            },
            "required": ["code"],
            "additionalProperties": False,
        },
    },
}


def build_data_schema(schema: Dict[str, List[str]]) -> DataSchema:
    return DataSchema(
        tables=[DataTableSchema(name=name, columns=columns) for name, columns in schema.items()]
    )


def context_to_json(context: BaseModel) -> str:
    return context.model_dump_json(indent=2)


def create_mcp_message(role: str, text: str) -> Dict[str, Any]:
    return {
        "role": role,
        "content": text,
    }
