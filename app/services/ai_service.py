import json
import uuid
from decimal import Decimal
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.redis_client import get_redis
from app.models.ai_analysis_results import AiAnalysisResult


class AiService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_result_by_record_id(self, record_id: int) -> AiAnalysisResult | None:
        result = await self.db.execute(
            select(AiAnalysisResult).where(AiAnalysisResult.record_id == record_id)
        )
        return result.scalar_one_or_none()

    async def predict_pneumonia(self, record_id: int, image_bytes: bytes) -> AiAnalysisResult:
        # 같은 record_id에 대한 기존 결과가 있으면 반환
        existing = await self.get_result_by_record_id(record_id)
        if existing:
            return existing

        redis = await get_redis()
        task_id = str(uuid.uuid4())
        result_channel = f"result:{task_id}"

        # 작업을 Redis 큐에 등록
        task = {
            "task_id": task_id,
            "record_id": record_id,
            "image_bytes": image_bytes.hex(),
        }
        await redis.rpush("pneumonia_queue", json.dumps(task))

        # 결과 Subscribe
        pubsub = redis.pubsub()
        await pubsub.subscribe(result_channel)

        prediction = None
        async for message in pubsub.listen():
            if message["type"] == "message":
                prediction = json.loads(message["data"])
                break

        await pubsub.unsubscribe(result_channel)

        # DB에 결과 저장
        ai_result = AiAnalysisResult(
            record_id=record_id,
            is_pneumonia=prediction["is_pneumonia"],
            confidence=Decimal(str(prediction["confidence"])),
            heatmap_url="",
            ai_model=prediction["ai_model"],
        )
        self.db.add(ai_result)
        await self.db.commit()
        await self.db.refresh(ai_result)
        return ai_result
