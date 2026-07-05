from pinecone import Pinecone
import os
import logging

logger = logging.getLogger(__name__)

def get_index(): 
    try:
        key = os.environ["PINECONE_API_KEY"]
        host = os.environ["PINECONE_INDEX_HOST"]
    except KeyError as e:
        logger.error(f'Pinecone key error: {e}')
        return None
    
    try:
        pc = Pinecone(api_key=key)
        return pc.Index(host=host)
    except Exception as e:
        logger.error(f'Pinecone connection error: {e}')
        return None

def search_similar_queries(query:str,threshold:float=0.85):
    index=get_index()
    report_ids = []
    try:
        if(index):
            results = index.search_records( 
                namespace="queries", 
                query={
                    "inputs": {"text": query},
                    "top_k": 5
                },
                fields=["report_id"] 
            )
            
            for hit in results["result"]["hits"]:
                if hit["_score"] >= threshold:
                    report_ids.append(hit["fields"]["report_id"])
    except Exception as e:
        logger.error(f'Vector search error: {e}')
    finally:
        return report_ids
    
def store_query(query:str,report_id:str):
    index=get_index()
    message="failure"
    try:
        if(index):
            index.upsert_records(
                namespace="queries",
                records=[
                    {
                        "_id":report_id,
                        "text":query,
                        "report_id":report_id
                    }
                ]
            ) 
            message="success"
    except Exception as e:
        logger.error(f'Index store error: {e}')
    finally:
        return message

