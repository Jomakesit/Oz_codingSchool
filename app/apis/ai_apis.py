from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.db.databases import async_get_db
from app.schemas.ai_schemas import AiAnalysisResultResponse, AiAnalysisResultCreateResponse
from app.services.ai_service import AiService
router = APIRouter(prefix="/api/v1/ai", tags=["ai"])
@router.post("/predict/{record_id}", response_model=AiAnalysisResultCreateResponse, status_code=200)
async def predict_pneumonia(
record_id: int,
xray_image: UploadFile = File(...),
db: AsyncSession = Depends(async_get_db),
):
image_bytes = await xray_image.read()
if not image_bytes:
raise HTTPException(status_code=400, detail="이미지 파일이 없거나 올바르지 않습니다.")
service = AiService(db)
result = await service.predict_pneumonia(record_id, image_bytes)

return AiAnalysisResultCreateResponse(
    message="폐렴 예측이 완료되었습니다.",
    result=result,
)
@router.get("/predict/{record_id}", response_model=AiAnalysisResultResponse, status_code=200)
async def get_prediction_result(
record_id: int,
db: AsyncSession = Depends(async_get_db),
):
service = AiService(db)
result = await service.get_result_by_record_id(record_id)
if result is None:
    raise HTTPException(status_code=404, detail="해당 진료기록의 예측 결과가 존재하지 않습니다.")

return result