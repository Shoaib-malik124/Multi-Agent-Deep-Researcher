from pinecone import Pinecone
import os

def get_index(): 
    try:
        key = os.environ["PINECONE_API_KEY"]
        host = os.environ["PINECONE_INDEX_HOST"]
    except KeyError as e:
        raise KeyError()
    
    try:
        pc = Pinecone(api_key=key)
        return pc.Index(host=host)
    except Exception as e:
        raise ConnectionError()

def search_similar_queries(query:str,threshold:float=0.85):
    try:
        index=get_index()
        results = index.search_records( 
            namespace="queries", 
            query={
                "inputs": {"text": query},
                "top_k": 5
            },
            fields=["report_id"] 
        )
        report_ids = []
        for hit in results["result"]["hits"]:
            if hit["_score"] >= threshold:
                report_ids.append(hit["fields"]["report_id"])
        yield {
            "type":"report_ids",
            "content":report_ids
        }
    except KeyError as e:
        yield {
            "type":"error",
            "status":500,
            "content":f"Server misconfiguration, missing: {str(e)}"
        }
    except ConnectionError as e:
        yield {
            "type":"error",
            "status":502,
            "content":f"BAD GATEWAY,Pinecone connection failed: {e}"
        }
    except Exception as e:
        yield {
            "type":"error",
            "status":502,
            "content":f"BAD GATEWAY, {e}"
        }
    
def store_query(query:str,report_id:str):
    try:
        index=get_index()
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
        yield {
            "type":"success",
            "content":"query stored"
        }
    except KeyError as e:
        yield {
            "type":"error",
            "status":500,
            "content":f"Server misconfiguration, missing: {str(e)}"
        }
    except ConnectionError as e:
        yield {
            "type":"error",
            "status":502,
            "content":f"BAD GATEWAY,Pinecone connection failed: {e}"
        }
    except Exception as e:
        yield {
            "type":"error",
            "status":502,
            "content":f"BAD GATEWAY, {e}"
        }
