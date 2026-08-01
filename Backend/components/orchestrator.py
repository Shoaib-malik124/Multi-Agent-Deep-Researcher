from celery_app import celery_app
from smolagents import ToolCallingAgent, MCPClient, InferenceClientModel
from prompts.prompts import SUBAGENT_PROMPT_TEMPLATE, COORDINATOR_PROMPT_TEMPLATE
import concurrent.futures
import os
import json
import logging

logger = logging.getLogger(__name__)


def run_single_subagent(
    subtask: dict,
    user_query: str,
    research_plan: str,
    mcp_url: str,
    subagent_model: InferenceClientModel
) -> str:
    try:
        with MCPClient({"url": mcp_url, "transport": "streamable-http"}) as mcp_tools:
            agent = ToolCallingAgent(
                tools=mcp_tools,
                model=subagent_model,
                add_base_tools=False,
                name=f"subagent_{subtask['id']}",
            )
            prompt = SUBAGENT_PROMPT_TEMPLATE.format(
                user_query=user_query,
                research_plan=research_plan,
                subtask_id=subtask["id"],
                subtask_title=subtask["title"],
                subtask_description=subtask["description"],
            )
            result = str(agent.run(prompt))
            logger.info(f"Subagent {subtask['id']} completed successfully")
            return result
    except Exception as e:
        logger.error(f"Subagent {subtask['id']} failed: {e}")
        return ""


@celery_app.task(max_retries=1)
def run_orchestrator(user_query: str, research_plan: str, subtasks: list):
    hf_token = os.environ["HF_TOKEN"]
    mcp_url = os.environ["MCP_URL"]
    coordinator_model_id = os.environ["ORCHESTRATOR_COORDINATOR_MODEL_ID"]
    subagent_model_id = os.environ["ORCHESTRATOR_SUBAGENT_MODEL_ID"]

    subagent_model = InferenceClientModel(
        model_id=subagent_model_id,
        api_key=hf_token,
        provider="novita"
    )
    coordinator_model = InferenceClientModel(
        model_id=coordinator_model_id,
        api_key=hf_token,
        provider="novita"
    )

    subagent_reports = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=len(subtasks)) as executor:
        futures = {
            executor.submit(
                run_single_subagent,
                subtask,
                user_query,
                research_plan,
                mcp_url,
                subagent_model
            ): subtask
            for subtask in subtasks
        }
        for future in concurrent.futures.as_completed(futures):
            subtask = futures[future]
            try:
                result = future.result()
                if result:
                    subagent_reports.append({
                        "subtask_id": subtask["id"],
                        "subtask_title": subtask["title"],
                        "report": result
                    })
            except Exception as e:
                logger.error(f"Subagent {subtask['id']} future failed: {e}")

    if not subagent_reports:
        raise RuntimeError("All subagents failed — no reports generated")

    reports_text = "\n\n---\n\n".join([
        f"Report for subtask '{r['subtask_title']}':\n{r['report']}"
        for r in subagent_reports
    ])

    coordinator_prompt = COORDINATOR_PROMPT_TEMPLATE.format(
        user_query=user_query,
        research_plan=research_plan,
        subtasks_json=json.dumps(subtasks, indent=2, ensure_ascii=False),
        sub_agent_reports=reports_text
    ) 

    coordinator = ToolCallingAgent(
        tools=[],
        model=coordinator_model,
        add_base_tools=False,
        name="coordinator_agent",
    )

    final_report = str(coordinator.run(coordinator_prompt))

    if not final_report:
        raise RuntimeError("Coordinator returned empty report")

    logger.info("Orchestrator completed successfully")
    return final_report