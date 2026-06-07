from sqlalchemy import BigInteger, Column, DateTime, Enum, SmallInteger, String, func

from app.core.db.databases import Base
from app.models.enums import Gender


class Patient(Base):
    __tablename__ = "patients"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    name = Column(
        String(30),
        nullable=False,
        comment="환자 성명"
    )
    age = Column(
        SmallInteger,
        nullable=False,
        comment="smallint"
    )
    gender = Column(
        Enum(Gender),
        nullable=True,
        comment="환자 성별"
    )
    phone = Column(
        String(11),
        nullable=False,
        comment="환자 연락처, 국내 전화번호로 한정"
    )
    created_at = Column(
        DateTime,
        nullable=False,
        server_default=func.now(),
        comment="환자 정보 등록 일시"
    )
    updated_at = Column(
        DateTime,
        nullable=True,
        onupdate=func.now(),
        comment="환자 정보 수정 일시"
    )