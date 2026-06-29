from utils.index_services import search_similar_queries,store_query
def check_pipeline(query:str):
    for event in search_similar_queries(query=query):
        if event["type"]=="report_ids":
            return event["type"],event["content"]
        else:
            return event["type"],event["status"]
        
def insert_pipeline(query:str,report_id:str):
    for event in store_query(query=query,report_id=report_id):
        if event["type"]=="success":
            return event["type"],event["content"]
        else:
            return event["type"],event["status"]