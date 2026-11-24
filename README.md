# ecommerce_mcp_v2

A small agent-based data analysis prototype using Groq LLM completion calls, pandas dataframes, and a multi-agent workflow.

## Project structure

- `app.py` - main loop that accepts questions, plans execution, runs code, makes decisions, and generates a report.
- `agents/` - agent modules:
  - `planner_agent.py` - creates a pandas execution plan from user questions.
  - `executor_agent.py` - runs generated code against loaded CSV data.
  - `orchestrator_agent.py` - decides whether to continue or finish.
  - `report_agent.py` - summarizes the final result.
- `services/` - infrastructure:
  - `data_loader.py` - loads CSV files into pandas DataFrames.
  - `groq_client.py` - configures the Groq API client.
- `tools/` - execution helper(s):
  - `python_analysis_tool.py` - evaluates generated Python code with dataset variables.
- `memory/` - simple observation history storage.
- `prompts/` - prompt templates for each agent.
- `data/` - dataset CSV files.

## Setup

1. Create a Python virtual environment:
   ```powershell
   python -m venv .venv
   .venv\Scripts\Activate.ps1
   ```
2. Install dependencies:
   ```powershell
   pip install -r requirements.txt
   ```
3. Provide a Groq API key in a .env file:
   ```text
   GROQ_API_KEY=your_api_key_here
   ```

## Run

```powershell
python app.py
```

Then type a question at the prompt. Enter `quit` or `exit` to stop.

## Notes

- The app expects the CSV files inside `data/` to match the loaded table names.
- Generated code should assign a `result` variable for the executor to return.
- Prompt files are loaded relative to the agent modules to avoid working-directory issues.
