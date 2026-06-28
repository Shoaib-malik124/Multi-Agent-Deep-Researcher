from smolagents import ToolCallingAgent, MCPClient, InferenceClientModel, tool
from prompts.prompts import COORDINATOR_PROMPT_TEMPLATE, SUBAGENT_PROMPT_TEMPLATE
from fastapi import HTTPException, status
import os
import json
import asyncio
import logging

logger = logging.getLogger(__name__)

async def orchestrator(user_query: str, research_plan: str, subtasks: list):

    try:
        hf_token = os.environ["HF_TOKEN"]
        mcp_url = os.environ["MCP_URL"]
        coordinator_model_id = os.environ["ORCHESTRATOR_COORDINATOR_MODEL_ID"]
        subagent_model_id = os.environ["ORCHESTRATOR_SUBAGENT_MODEL_ID"]
    except KeyError as e:
        logger.error(f"Missing environment variable: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Server misconfiguration, missing: {str(e)}"
        )

    coordinator_model = InferenceClientModel(
        model_id=coordinator_model_id,
        api_key=hf_token,
        provider="novita",
    )
    subagent_model = InferenceClientModel(
        model_id=subagent_model_id,
        api_key=hf_token,
        provider="novita",
    )

    subtasks_json = json.dumps(
        [s.model_dump() for s in subtasks],
        indent=2,
        ensure_ascii=False
    )

    coordinator_prompt = COORDINATOR_PROMPT_TEMPLATE.format(
        user_query=user_query,
        research_plan=research_plan,
        subtasks_json=subtasks_json
    )

    def run_sync():
        with MCPClient({"url": mcp_url, "transport": "streamable-http"}) as mcp_tools:

            @tool
            def create_subagent(subtask_id: str, subtask_title: str, subtask_description: str) -> str:
                """
                Spawn a dedicated research sub-agent for a single subtask.

                Args:
                    subtask_id (str): The unique identifier for the subtask.
                    subtask_title (str): The descriptive title of the subtask.
                    subtask_description (str): Detailed instructions for the sub-agent to perform the subtask.

                The sub-agent:
                - Has access to the Firecrawl MCP tools.
                - Must perform deep research ONLY on this subtask.
                - Returns a structured markdown report with:
                - a clear heading identifying the subtask,
                - a narrative explanation,
                - bullet-point key findings,
                - explicit citations / links to sources.
                """
                subagent = ToolCallingAgent(
                    tools=mcp_tools,
                    model=subagent_model,
                    add_base_tools=False,
                    name=f"subagent_{subtask_id}",
                )
                subagent_prompt = SUBAGENT_PROMPT_TEMPLATE.format(
                    user_query=user_query,
                    research_plan=research_plan,
                    subtask_id=subtask_id,
                    subtask_title=subtask_title,
                    subtask_description=subtask_description,
                )
                return str(subagent.run(subagent_prompt))

            coordinator = ToolCallingAgent(
                tools=[create_subagent],
                model=coordinator_model,
                add_base_tools=False,
                name="coordinator_agent",
            )

            return str(coordinator.run(coordinator_prompt))

    try:
        final_report = await asyncio.to_thread(run_sync)

        if not final_report:
            logger.error("Orchestrator returned empty report")
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Orchestrator returned empty report"
            )

        return final_report

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Orchestrator failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Orchestrator error: {str(e)}"
        )