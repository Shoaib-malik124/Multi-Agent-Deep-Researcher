from fastapi import APIRouter, Depends, Request
from authentication.auth import verify_jwt
from db.db import get_db
from schemas.query import ResearchRequest
from components.orchestrator import run_orchestrator
from components.task_splitter import task_splitter
from components.research_planner import research_planner
from schemas.document import Reports
from datetime import datetime, timezone
from fastapi.responses import StreamingResponse
from pymongo.errors import PyMongoError
from utils.limiter import limiter
from utils.index_pipeline import check_pipeline, insert_pipeline
from components.report_merger import merger
from db.redis import get_redis
from db.get_documents import get_documents
from bson import ObjectId
import asyncio
import json
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/api/documents")
async def returnDocuments(
    page_num: int = 1,
    user=Depends(verify_jwt),
    db=Depends(get_db),
    redis_cache=Depends(get_redis)
):
    user_id = user["sub"]

    try:
        cached = redis_cache.get(f'{user_id}:{page_num}')
        if cached:
            return json.loads(cached)
    except Exception as e:
        logger.error(f'Redis fetch error: {e}')

    try:
        response = await get_documents(db_connection=db, user_id=user_id, page_num=page_num)
        try:
            redis_cache.set(f'{user_id}:{page_num}', json.dumps(response), ex=3600)
        except Exception as e:
            logger.error(f'Redis set error: {e}')
        return response
    except Exception as e:
        logger.error(f'Database fetch error: {e}')
        return {"total_pages": 0, "documents": []}


@router.post('/api/research')
@limiter.limit("1/hour")
async def deepResearch(
    request: Request,
    body: ResearchRequest,
    user=Depends(verify_jwt),
    db=Depends(get_db),
    redis_cache=Depends(get_redis)
):
    user_id = user["sub"]
    query = body.query

    async def streamChunks():

        report_ids = await asyncio.to_thread(check_pipeline, query, user_id)  # type: ignore

        if report_ids:
            docs = []
            for id in report_ids:
                try:
                    result = await db.reports.find_one({"_id": ObjectId(id)})
                    if result:
                        docs.append(result["content"])
                except Exception as e:
                    logger.error(f"Failed to fetch report {id}: {e}")

            if docs:
                try:
                    resultant_report = await merger(query, docs)
                    if resultant_report:
                        yield json.dumps({
                            "type": "final_report",
                            "content": resultant_report
                        })
                        return
                except Exception as e:
                    logger.error(f'Merger agent error: {e}')

        research_plan = ""
        async for event in research_planner(query):
            if event["type"] == "chunk":
                research_plan += event["content"]
                yield json.dumps({
                    "type": "chunk",
                    "content": event["content"]
                })
            elif event["type"] == "plan":
                research_plan = event["content"]
            elif event["type"] == "error":
                yield json.dumps({
                    "type": "error",
                    "status": event["status"],
                    "content": event["content"]
                })
                return

        if not research_plan:
            yield json.dumps({
                "type": "error",
                "status": 502,
                "content": "Internal Server Error"
            })
            return

        subTaskList: list = []
        async for event in task_splitter(research_plan=research_plan):
            if event["type"] == "subTaskList":
                subTaskList = event["content"]
            else:
                yield json.dumps({
                    "type": event["type"],
                    "status": event["status"],
                    "content": event["content"]
                })
                return

        if not subTaskList:
            yield json.dumps({
                "type": "error",
                "status": 502,
                "content": "Internal Server Error"
            })
            return

        task = run_orchestrator.delay(  # type: ignore
            user_query=query,
            research_plan=research_plan,
            subtasks=[s.model_dump() for s in subTaskList]
        )

        logger.info(f"Orchestrator task dispatched: {task.id}")

        final_report = ""
        while True:
            if await request.is_disconnected():
                logger.info(f"Client disconnected — task {task.id} still running in background")
                return

            if task.ready():
                if task.successful():
                    final_report = task.result
                    break
                else:
                    logger.error(f"Orchestrator task failed: {task.result}")
                    yield json.dumps({
                        "type": "error",
                        "status": 502,
                        "content": "Internal Server Error"
                    })
                    return

            await asyncio.sleep(5)

        if not final_report:
            yield json.dumps({
                "type": "error",
                "status": 502,
                "content": "Internal Server Error"
            })
            return

        yield json.dumps({
            "type": "final_report",
            "content": final_report
        })

        report = Reports(
            query=query,
            content=final_report,
            owner=user_id,
            created_at=datetime.now(timezone.utc)
        )

        document_id = ""
        try:
            response = await db.reports.insert_one(report.model_dump())
            document_id = str(response.inserted_id)
            logger.info(f"Report saved to MongoDB: {document_id}")

            try:
                keys = redis_cache.keys(f"{user_id}:*")
                if keys:
                    redis_cache.delete(*keys)
            except Exception as e:
                logger.error(f"Redis cache invalidation failed: {e}")

        except PyMongoError as e:
            logger.error(f"Report insertion to MongoDB failed: {e}")
        except Exception as e:
            logger.error(f"Database error: {e}")

        if document_id:
            message = await asyncio.to_thread(insert_pipeline, query, document_id, user_id)
            logger.info(f"Vector store: {message}")

    return StreamingResponse(
        streamChunks(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no"
        }
    )