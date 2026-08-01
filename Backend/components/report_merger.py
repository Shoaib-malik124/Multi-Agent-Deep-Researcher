from typing import List
from huggingface_hub import AsyncInferenceClient
from prompts.prompts import MERGER_PROMPT_TEMPLATE
import os
import json
import logging

logger = logging.getLogger(__name__)

async def merger(user_query:str,docs:List[str]):
    hf_token=os.environ["HF_TOKEN"]
    model_id=os.environ["PLANNER_MODEL_ID"]
    
    try: 
        reports_text = "\n\n---\n\n".join(
            [f"Report {i+1}:\n{doc}" for i, doc in enumerate(docs)]
        )
        merger_client=AsyncInferenceClient(
            api_key=hf_token,
            provider="auto"
        )
        
        completion=await merger_client.chat.completions.create(
            model=model_id,
            messages=[
                {"role":"system","content":MERGER_PROMPT_TEMPLATE},
                {"role":"user",
                    "content": f"""
                    User Query:
                    {user_query}

                    The following reports were generated for semantically similar queries.
                    Merge them into one report.

                    {reports_text}
                    """
                }
            ],
        )
    except Exception as e:
        logger.error(f'Merger Agent error: {e}')
        return "" 

    try:
        final_report=completion.choices[0].message.content 
        return final_report 
    except Exception as e:
        logger.error(f'Merger Agent failed to generate the report: {e}')
        return "" 