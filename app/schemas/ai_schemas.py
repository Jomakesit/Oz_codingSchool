from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel
class AiAnalysisResultResponse(BaseModel):
id: int
record_id: int
is_pneumonia: bool
confidence: Decimal
heatmap_url: str
ai_model: str
created_at: datetime
updated_at: datetime | None
model_config = {"from_attributes": True}
class AiAnalysisResultCreateResponse(BaseModel):
message: str
result: AiAnalysisResultResponse