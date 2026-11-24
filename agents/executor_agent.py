from tools.python_analysis_tool import (
    PythonAnalysisTool
)

from memory.observation_memory import (
    ObservationMemory
)


class ExecutorAgent:

    def __init__(self):

        self.tool = (
            PythonAnalysisTool()
        )

        self.memory = (
            ObservationMemory()
        )

    def execute(
        self,
        plan,
        datastore
    ):
        if not isinstance(plan, dict):
            raise ValueError("Plan must be a dict.")

        if "code" not in plan:
            raise ValueError("Plan is missing required key: 'code'.")

        raw = self.tool.run(plan["code"], datastore)

        # Normalize/serialize result for storage in observations
        serialized = raw

        # If the tool returned a DataFrame-JSON string, keep as-is.
        # If it returned Python objects, convert to string safely.
        try:
            import json

            if isinstance(raw, str):
                # try to detect JSON string
                try:
                    json.loads(raw)
                    serialized = raw
                except Exception:
                    serialized = raw
            else:
                serialized = json.dumps(raw)
        except Exception:
            serialized = str(raw)

        observation = {
            "tool": plan.get("tool", "python_analysis"),
            "code": plan["code"],
            "result": serialized,
        }

        self.memory.add(observation)
        return self.memory.get_all()
