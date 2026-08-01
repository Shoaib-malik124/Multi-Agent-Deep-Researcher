from huggingface_hub import AsyncInferenceClient
from prompts.prompts import PLANNER_SYSTEM_INSTRUCTIONS
import os
import logging

logger = logging.getLogger(__name__)

def _content(obj):
    try:
        return obj.choices[0].delta.content
    except Exception as e:
        try:
            return obj.choices[0].message.content
        except Exception:
            return None
        
async def research_planner(user_query:str):
    hf_token=os.environ["HF_TOKEN"]
    model_id=os.environ["PLANNER_MODEL_ID"]
    
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
        yield {
              "type":"error",
              "status":502,
              "content":f"Internal Server Error"
            }
        logger.error(f"Research planner HF connection error: {e}")
        return

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
            logger.error("Planner Model failed to generate research plan")
            yield {"type":"error","status":502,"content":"Internal Server Error"}
            
    except TypeError:
        c=_content(completion)
        if c:
            research_plan=c
            yield {"type":"plan","content":research_plan}
        else:
            logger.error("Planner Model failed to generate research plan")
            yield {"type":"error","status":502,"content":"Internal Server Error"}