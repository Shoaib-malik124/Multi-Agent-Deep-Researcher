from components.research_planner import research_planner
from components.task_splitter import task_splitter
from smolagents import ToolCallingAgent,MCPClient,InferenceClientModel,tool
from prompts.prompts import COORDINATOR_PROMPT_TEMPLATE,SUBAGENT_PROMPT_TEMPLATE
import os
import json
import asyncio


async def research_caller(user_query:str):
    research_plan=""
    async for event in research_planner(user_query):
        if event["type"]=="chunk":
           research_plan+=event["content"]
           # pass to frontend
        elif event["type"]=="plan":
           research_plan=event["content"]
           
async def orchestrator(user_query:str):
    research_plan=await research_caller(user_query)
    subtasks=await task_splitter(research_plan) # type:ignore
    
    FIRECRAWL_API_KEY=os.environ["FIRECRAWL_API_KEY"]
    MCP_URL=os.environ["MCP_URL"]

    orchestrator_model=InferenceClientModel(
        model_id=os.environ["ORCHESTRATOR_MODEL_ID"],
        api_key=FIRECRAWL_API_KEY,
        provider='novita',
        bill_to="huggingface"
    )
    subagent_model=InferenceClientModel(
        model_id=os.environ["ORCHESTRATOR_SUBAGENT_MODEL_ID"],
        api_key=FIRECRAWL_API_KEY,
        provider='novita',
        bill_to="huggingface"
    )

    with MCPClient({"url":MCP_URL,"transport":"streamable-http"}) as mcp_tools:

        @tool
        async def create_subagent(subtask_id:str,subtask_title:str,subtask_description:str):
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

