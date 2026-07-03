async def get_documents(db_connection,user_id:str,page_num:int,page_content:int=10):
    try:
        cursor=db_connection.reports.find({"owner":user_id}).sort("created_at",-1).skip((page_num-1)*page_content).limit(page_content)
        documents=[]
        async for doc in cursor:
            doc["_id"]=str(doc["_id"])
            documents.append(doc)
        return documents
    except Exception:
        return []