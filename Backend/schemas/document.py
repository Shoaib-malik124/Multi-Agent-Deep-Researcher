from pydantic import BaseModel,Field
from datetime import datetime

class reports(BaseModel):
    query:str=Field(
        ...,
        description="The user query for which the report is generated"
    )
    content:str=Field(
        ...,
        description="Deep Research report in Markdown format"
    )
    owner:str=Field(
        ...,
        description="ID of the report owner"
    )
    created_at:datetime=Field(
        ...,
        description='The timestamp when this report is generated'
    )