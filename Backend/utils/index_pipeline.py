from utils.index_services import search_similar_queries,store_query
def check_pipeline(query:str,user_id:str):
    report_ids=search_similar_queries(query=query,user_id=user_id)
    return report_ids
        
def insert_pipeline(query:str,report_id:str,user_id:str):
    message=store_query(query=query,report_id=report_id,user_id=user_id)
    return message