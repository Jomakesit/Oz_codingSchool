from sqlalchemy.ext.asyncio import AsyncSession

from app.models.patients import Patient
from app.repositories.patient_repository import PatientRepository
from app.schemas.patient_schemas import PatientCreateRequest


class PatientService:
    def __init__(self, db: AsyncSession):
        self.repo = PatientRepository(db)

    async def create_patient(self, data: PatientCreateRequest) -> Patient:
        patient = Patient(
            name=data.name,
            age=data.age,
            gender=data.gender,
            phone=data.phone,
        )
        return await self.repo.create(patient)
