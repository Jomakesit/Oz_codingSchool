from sqlalchemy import BigInteger, Boolean, Column, DateTime, DECIMAL, ForeignKey, String, func

from app.core.db.databases import Base


class AiAnalysisResult(Base):
    __tablename__ = "ai_analysis_results"

    id = Column(BigInteger, primary_key=True, autoincrement=True)

    record_id = Column(
        BigInteger,
        ForeignKey("medical_records.id", ondelete="CASCADE"),
        nullable=False,
        comment="진료 기록 id"
    )

    is_pneumonia = Column(
        Boolean,
        nullable=False,
        comment="폐렴 진단 여부"
    )

    confidence = Column(
        DECIMAL(5, 2),
        nullable=False,
        comment="AI 예측 신뢰도"
    )

    heatmap_url = Column(
        String(255),
        nullable=False,
        comment="AI가 판별한 병변 표시 이미지 url"
    )

    ai_model = Column(
        String(50),
        nullable=False,
        comment="AI 예측에 사용된 모델명 혹은 모델파일"
    )

    created_at = Column(
        DateTime,
        nullable=False,
        server_default=func.now(),
        comment="AI 폐렴 예측 결과 생성일시"
    )

    updated_at = Column(
        DateTime,
        nullable=True,
        onupdate=func.now(),
        comment="수정 일시"
    )