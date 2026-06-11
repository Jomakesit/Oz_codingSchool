from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.ai_analysis_results import AiAnalysisResult
from app.models.xray_images import XrayImage
from worker.model import predict
class AiService:
def init(self, db: AsyncSession):
self.db = db
async def get_result_by_record_id(self, record_id: int) -> AiAnalysisResult | None:
    result = await self.db.execute(
        select(AiAnalysisResult).where(AiAnalysisResult.record_id == record_id)
    )
    return result.scalar_one_or_none()

async def predict_pneumonia(self, record_id: int, image_bytes: bytes) -> AiAnalysisResult:
    prediction = predict(image_bytes)

    ai_result = AiAnalysisResult(
        record_id=record_id,
        is_pneumonia=prediction["is_pneumonia"],
        confidence=prediction["confidence"],
        heatmap_url="",
        ai_model=prediction["ai_model"],
    )

    self.db.add(ai_result)
    await self.db.commit()
    await self.db.refresh(ai_result)
    return ai_result