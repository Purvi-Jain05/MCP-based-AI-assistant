import logging

from services.data_loader import DataStore
from agents.planner_agent import PlannerAgent
from agents.executor_agent import ExecutorAgent
from agents.report_agent import ReportAgent
from agents.orchestrator_agent import OrchestratorAgent

logging.basicConfig(
    level=logging.WARNING,
    format="%(asctime)s %(levelname)s %(message)s"
)
logger = logging.getLogger(__name__)


def main():
    datastore = DataStore()
    planner = PlannerAgent()
    executor = ExecutorAgent()
    reporter = ReportAgent()
    orchestrator = OrchestratorAgent()

    logger.info("Starting ecommerce_mcp_v2 agent loop")
    print("Type 'quit' or 'exit' to stop.")

    while True:
        try:
            question = input("\nAsk: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nGoodbye.")
            break

        if not question:
            continue

        if question.lower() in {"quit", "exit"}:
            print("Exiting.")
            break

        executor.memory.reset()
        current_question = question
        observations = []

        for _ in range(3):
            try:
                schema = datastore.get_schema()

                metadata = datastore.get_metadata()
                plan = planner.plan(current_question, schema, metadata)
                logger.info("Planner returned plan: %s", plan)
            except Exception as exc:
                logger.exception("Planner error")
                print("\nPlanner error:", exc)
                break

            try:
                observations = executor.execute(plan, datastore)
                logger.info("Execution observations: %s", observations)
            except Exception as exc:
                logger.exception("Execution error")
                print("\nExecution error:", exc)
                break

            try:
                decision = orchestrator.decide(question, observations)
                logger.info("Orchestrator decision: %s", decision)
            except Exception as exc:
                logger.exception("Orchestrator error")
                print("\nOrchestrator error:", exc)
                break

            print("\nDECISION:")
            print(decision)

            if isinstance(decision, dict) and decision.get("action") == "finish":
                break

            if not isinstance(decision, dict) or "next_question" not in decision:
                logger.warning("Invalid decision response: %s", decision)
                print("\nInvalid decision response, stopping.")
                break

            current_question = decision["next_question"]

        try:
            report = reporter.generate(question, observations)
            logger.info("Report generated successfully")
        except Exception as exc:
            logger.exception("Report generation failed")
            report = f"Report generation failed: {exc}"

        print("\nREPORT:\n")
        print(report)


if __name__ == "__main__":
    main()
