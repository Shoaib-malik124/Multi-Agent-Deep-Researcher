import math
async def get_documents(db_connection,user_id:str,page_num:int,page_content:int=10):
    try:
        total_documents=await db_connection.reports.count_documents({"owner":user_id})
        cursor=db_connection.reports.find({"owner":user_id}).sort("created_at",-1).skip((page_num-1)*page_content).limit(page_content)

        documents=[]
        async for doc in cursor:
            doc["_id"]=str(doc["_id"])
            documents.append(doc)

        total_pages=math.ceil(total_documents/page_content)
        return {
            "total_pages":total_pages,
            "documents":documents
        }
    except Exception:
        return {
            "total_pages":0,
            "documents":[]
        }