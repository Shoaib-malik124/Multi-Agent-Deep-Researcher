from huggingface_hub import AsyncInferenceClient
from prompts.prompts import TASK_SPLITTER_SYSTEM_INSTRUCTIONS
from pydantic import BaseModel, Field,ValidationError
from typing import List
from fastapi import HTTPException,status
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

    try:
        hf_token=os.environ["HF_TOKEN"]
        model_id=os.environ["TASK_SPLITTER_MODEL_ID"]

    except KeyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Server misconfiguration, missing: {str(e)}"
        )
    
    try:
        splitter_client = AsyncInferenceClient(
            api_key=hf_token,
            bill_to="huggingface",
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
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Text splitter API error: {str(e)}"
        )
    
    try:
        result = completion.choices[0].message
        subtasks = json.loads(result.content)['subtasks']
        return SubTaskList(subtasks=subtasks).subtasks
    except (IndexError, AttributeError) as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Model returned unexpected response structure"
        )
    except json.JSONDecodeError as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Model returned invalid JSON"
        )
    except KeyError:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Model response missing 'subtasks' key"
        )
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Model response failed schema validation"
        )