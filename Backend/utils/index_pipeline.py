from utils.index_services import search_similar_queries,store_query
def check_pipeline(query:str):
    report_ids=search_similar_queries(query=query)
    return report_ids
        
def insert_pipeline(query:str,report_id:str):
    message=store_query(query=query,report_id=report_id)
    return message