from typing import List
from huggingface_hub import AsyncInferenceClient
from prompts.prompts import MERGER_PROMPT_TEMPLATE
import os
import json
async def merger(user_query:str,docs:List):
    try:
        hf_token=os.environ["HF_TOKEN"]
        model_id=os.environ["PLANNER_MODEL_ID"]
    except KeyError as e:
        raise KeyError()
    
    try: 
        reports_json=json.dumps( # { {text},{text},{text} }
            [s.model_dump() for s in docs],
            indent=2,
            ensure_ascii=False
        )
        planner_client=AsyncInferenceClient(
            api_key=hf_token,
            provider="auto"
        )
        
        completion=await planner_client.chat.completions.create(
            model=model_id,
            messages=[
                {"role":"system","content":MERGER_PROMPT_TEMPLATE},
                {"role":"user",
                    "content": f"""
                    User Query:
                    {user_query}

                    The following reports were generated for semantically similar queries.
                    Merge them into one report.

                    {reports_json}
                    """
                }
            ],
        )
    except Exception:
        return # Because if merger has failed to generate a final response, we have to simply call the research pipeline.

    try:
        final_report=completion.choices[0].message    
        return final_report
    except Exception:
        return # Because if merger has failed to generate a final response, we have to simply call the research pipeline.