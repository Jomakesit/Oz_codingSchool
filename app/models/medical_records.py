from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, String, Text, func

from app.core.db.databases import Base


class MedicalRecord(Base):
    __tablename__ = "medical_records"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    patient_id = Column(
        BigInteger,
        ForeignKey("patients.id", ondelete="CASCADE"),
        nullable=False,
        comment="환자 정보 테이블 FK"
    )
    chart_number = Column(
        String(50),
        nullable=False,
        unique=True,
        comment="환자 진료 차트 번호"
    )
    symptoms = Column(
        Text,
        nullable=False,
        comment="환자 증상 기록"
    )
    created_at = Column(
        DateTime,
        nullable=False,
        server_default=func.now(),
        comment="진료 정보 등록 일시"
    )
    updated_at = Column(
        DateTime,
        nullable=True,
        onupdate=func.now(),
        comment="진료 정보 수정 일시"
    )