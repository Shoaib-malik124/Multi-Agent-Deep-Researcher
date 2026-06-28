from huggingface_hub import AsyncInferenceClient
from prompts.prompts import PLANNER_SYSTEM_INSTRUCTIONS
from fastapi import HTTPException,status
import os

def _content(obj):
    try:
        return obj.choices[0].delta.content
    except Exception:
        try:
            return obj.choices[0].message.content
        except Exception:
            return None
        
async def research_planner(user_query:str):
    try:
        hf_token=os.environ["HF_TOKEN"]
        model_id=os.environ["PLANNER_MODEL_ID"]
    except KeyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Server misconfiguration: missing {str(e)}"
        )
    
    try:
        planner_client=AsyncInferenceClient(
            api_key=hf_token,
            provider="auto"
        )
        
        completion=await planner_client.chat.completions.create(
            model=model_id,
            messages=[
                {"role":"system","content":PLANNER_SYSTEM_INSTRUCTIONS},
                {"role":"user","content":user_query}
            ],
            stream=True
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Planner, API error: {str(e)}"
        )

    research_plan=""

    try:
        async for chunk in completion:
            c=_content(chunk)
            if c:
               research_plan+=c
               yield {"type":"chunk","content":c}
        if research_plan:
            yield {"type":"plan","content":research_plan}
        else:
            yield {"type":"error","status":502,"content":"Planner Model failed to generate research plan"}
            
    except TypeError:
        try:
            c=_content(completion)
            if c:
                research_plan=c
                yield {"type":"plan","content":research_plan}
            else:
                yield {"type":"error","status":502,"content":"Planner Model failed to generate research plan"}
        except Exception as e:
            yield {"type":"error","status":502,"content":"Planner Model failed to generate research plan"}
    except Exception as e:
        yield {"type":"error","status":502,"content":"Planner Model failed to generate research plan"}