from huggingface_hub import AsyncInferenceClient
from prompts.prompts import PLANNER_SYSTEM_INSTRUCTIONS
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
    planner_client=AsyncInferenceClient(
        api_key=os.environ["HF_TOKEN"],
        bill_to="huggingface",
        provider="auto"
    )
    
    model_id=os.environ["PLANNER_MODEL_ID"]

    completion=await planner_client.chat.completions.create(
       model=model_id,
       messages=[
           {"role":"system","content":PLANNER_SYSTEM_INSTRUCTIONS},
           {"role":"user","content":user_query}
       ],
       stream=True
    )

    try:
        async for chunk in completion:
            c=_content(chunk)
            if c:
              yield c
            
    except TypeError:
        try:
            c=_content(completion)
            if c:
              yield c
        except Exception:
            pass
        