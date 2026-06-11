from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db.databases import async_get_db
from app.schemas.patient_schemas import PatientCreateRequest, PatientResponse
from app.services.patient_service import PatientService

router = APIRouter(prefix="/api/v1/patients", tags=["patients"])


@router.post("/", response_model=PatientResponse, status_code=201)
async def create_patient(
    data: PatientCreateRequest,
    db: AsyncSession = Depends(async_get_db),
):
    return await PatientService(db).create_patient(data)
