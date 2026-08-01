from pinecone import Pinecone
import os
import logging

logger = logging.getLogger(__name__)

key = os.environ["PINECONE_API_KEY"]
host = os.environ["PINECONE_INDEX_HOST"]

index=None
try:
    pc = Pinecone(api_key=key)
    index=pc.Index(host=host)
except Exception as e:
    logger.error(f'Pinecone connection error: {e}')
    

def search_similar_queries(query:str,user_id:str,threshold:float=0.85):
    report_ids = []
    try:
        if(index):
            results = index.search_records( 
                namespace="queries", 
                query={
                    "inputs": {"text": query},
                    "top_k": 5,
                    "filter": {"user_id": {"$eq": user_id}}
                }
            )
            
            for hit in results["result"]["hits"]:
                if hit["_score"] >= threshold:
                    report_ids.append(hit["_id"])
    except Exception as e:
        logger.error(f'Vector search error: {e}')
    finally:
        return report_ids
    
def store_query(query:str,report_id:str,user_id:str):
    message="success"
    try:
        if(index):
            index.upsert_records(
                namespace="queries",
                records=[
                    {
                        "_id":report_id,
                        "text":query,
                        "user_id":user_id
                    }
                ]
            ) 
    except Exception as e:
        message="failure"
        logger.error(f'Vector Index store error: {e}')
    finally:
        return message

