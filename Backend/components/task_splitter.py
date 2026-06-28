from huggingface_hub import AsyncInferenceClient
from prompts.prompts import TASK_SPLITTER_SYSTEM_INSTRUCTIONS
from pydantic import BaseModel, Field,ValidationError
from typing import List
from fastapi import HTTPException,status
import logging
import os
import json

logger=logging.getLogger(__name__)

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

async def task_splitter(research_plan: str):

    try:
        hf_token=os.environ["HF_TOKEN"]
        model_id=os.environ["TASK_SPLITTER_MODEL_ID"]

    except KeyError as e:
        yield {
                "type":"error",
                "status":500,
                "content":f"Server misconfiguration, missing: {str(e)}"
            }
        return
    
    try:
        splitter_client = AsyncInferenceClient(
            api_key=hf_token,
            provider='novita'
        )

        completion = await splitter_client.chat.completions.create( # type: ignore
            model=model_id,
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
    except Exception as e:
        yield {
                "type":"error",
                "status":502,
                "content":f"Text splitter API error: {str(e)}"
            }
        return
    
    try:
        result = completion.choices[0].message
        logger.debug("Raw model response: %s", result.content)
        subtasks = json.loads(result.content)['subtasks']
        yield {
                "type":"subTaskList",
                "content":SubTaskList(subtasks=subtasks).subtasks
            }
    except (IndexError, AttributeError) as e:
        yield {
                "type":"error",
                "status":502,
                "content":"Model returned unexpected response structure"
            }
    except json.JSONDecodeError as e:
        yield {
                "type":"error",
                "status":502,
                "content":"Model returned invalid JSON"
            }
    except KeyError:
        yield {
                "type":"error",
                "status":502,
                "content":"Model response missing 'subtasks' key"
            }
    except ValidationError as e:
        yield {
                "type":"error",
                "status":502,
                "content":"Model response failed schema validation"
            }