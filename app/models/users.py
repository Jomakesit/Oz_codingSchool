from sqlalchemy import Boolean, Column, DateTime, Enum, Integer, String, func

from app.core.db.databases import Base
from app.models.enums import Department, Gender, Role


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(255), unique=True)
    hashed_password = Column(
        String(255),
        comment="평문 저장 x -> 해쉬화 된 비밀번호 저장"
    )
    name = Column(String(20))
    phone_number = Column(
        String(20),
        unique=True,
        comment="유저 휴대폰 번호"
    )
    gender = Column(
        Enum(Gender),
        nullable=False,
        comment="성별 선택"
    )
    department = Column(
        Enum(Department),
        nullable=False,
        comment="부서 선택"
    )
    role = Column(
        Enum(Role),
        nullable=False,
        comment="부여된 역할 권한"
    )
    is_active = Column(
        Boolean,
        nullable=False,
        default=True,
        comment="계정 활성화 여부"
    )
    created_at = Column(
        DateTime,
        nullable=False,
        server_default=func.now(),
        comment="유저 생성 일시"
    )
    updated_at = Column(
        DateTime,
        nullable=True,
        onupdate=func.now(),
        comment="유저 정보 수정 일시"
    )