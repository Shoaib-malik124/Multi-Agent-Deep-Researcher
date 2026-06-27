from smolagents import ToolCallingAgent,MCPClient,InferenceClientModel,tool
from prompts.prompts import COORDINATOR_PROMPT_TEMPLATE,SUBAGENT_PROMPT_TEMPLATE
from fastapi import HTTPException,status
import os
import json
import asyncio


async def orchestrator(user_query,research_plan,subtasks):
    try:
        MCP_URL=os.environ["MCP_URL"]
        ORCHESTRATOR_COORDINATOR_MODEL_ID=os.environ["ORCHESTRATOR_COORDINATOR_MODEL_ID"]
        ORCHESTRATOR_SUBAGENT_MODEL_ID=os.environ["ORCHESTRATOR_SUBAGENT_MODEL_ID"]
        hf_token=os.environ["HF_TOKEN"]
    except KeyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Server misconfiguration, missing: {str(e)}"
        )
    
    try:
        orchestrator_model = InferenceClientModel(
            model_id=ORCHESTRATOR_COORDINATOR_MODEL_ID, 
            api_key=hf_token,
            provider="novita",
            bill_to="huggingface"
        )
        subagent_model = InferenceClientModel(
            model_id=ORCHESTRATOR_SUBAGENT_MODEL_ID, 
            api_key=hf_token,
            provider="novita",
            bill_to="huggingface"
        )


        with MCPClient({"url":MCP_URL,"transport":"streamable-http"}) as mcp_tools:
            
            @tool
            async def create_subagent(subtask_id:str,subtask_title:str,subtask_description:str):
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
                subagent=ToolCallingAgent(
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
                
                subtask_report=await asyncio.to_thread(subagent.run,subagent_prompt)
                return subtask_report

            coordinator=ToolCallingAgent(
                tools=[create_subagent],
                model=orchestrator_model,
                add_base_tools=False,
                name=f"coordinator_agent{user_query}",
            )  

            subtasks_json = json.dumps(subtasks, indent=2, ensure_ascii=False)
            coordinator_prompt=COORDINATOR_PROMPT_TEMPLATE.format(
                user_query=user_query,
                research_plan=research_plan,
                subtasks_json=subtasks_json
            )

            final_report=await asyncio.to_thread(coordinator.run,coordinator_prompt)
            return final_report
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f'Orchestrator Model error: {str(e)}'
        )
