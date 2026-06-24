from huggingface_hub import AsyncInferenceClient
from prompts.prompts import TASK_SPLITTER_SYSTEM_INSTRUCTIONS
from pydantic import BaseModel, Field
from typing import List
import os
import json

class SubTask(BaseModel):
    id: str = Field(..., description='A unique and short text identifier for subtask')
    title: str = Field(..., description='A short and clean title that represents the subtask')
    description: str = Field(..., description='Clean and detailed set of instructions for the agent')

class SubTaskList(BaseModel):
    subtasks: List[SubTask] = Field(..., description='A list of subtasks covering the entire research plan')

TASK_SPLITTER_JSON_SCHEMA = {
    "name": "subtaskList",
    "schema": SubTaskList.model_json_schema(),
    "strict": True,
}

async def task_splitter(research_plan: str) -> List[SubTask]:
    splitter_client = AsyncInferenceClient(
        api_key=os.environ["HF_TOKEN"],
        bill_to="huggingface",
        provider='novita'
    )

    completion = await splitter_client.chat.completions.create( # type: ignore
        model=os.environ["TASK_SPLITTER_MODEL_ID"],
        messages=[
            {"role": "system", "content": TASK_SPLITTER_SYSTEM_INSTRUCTIONS},
            {"role": "user", "content": research_plan}
        ],
        response_format={ # type: ignore
            "type": "json_schema",
            "json_schema": TASK_SPLITTER_JSON_SCHEMA,
        },
        stream=False
    )

    result = completion.choices[0].message
    subtasks = json.loads(result.content)['subtasks']
    return subtasks