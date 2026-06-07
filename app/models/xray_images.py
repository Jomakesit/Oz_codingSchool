from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, Integer, String, func
from app.core.db.databases import Base


class XrayImage(Base):
    __tablename__ = "xray_images"

    id = Column(BigInteger, primary_key=True, autoincrement=True)

    record_id = Column(
        BigInteger,
        ForeignKey("medical_records.id", ondelete="CASCADE"),
        nullable=False,
        comment="진료 기록 id"
    )

    # 제공 ERD 기준:
    # - uploader_id: not null
    # - FK 삭제 정책: users.id 삭제 시 SET NULL
    #
    # 주의:
    # SET NULL은 참조 대상 사용자가 삭제될 때 uploader_id를 NULL로 바꾸는 정책입니다.
    # 그러나 uploader_id가 nullable=False이면 NULL 저장이 불가능하므로
    # 두 조건은 실제 DB 제약에서 충돌할 수 있습니다.
    # 본 과제에서는 제공 ERD 기준을 유지하고, 해당 내용은 문서에 확인 필요 사항으로 남깁니다.
    # uploader_id = Column(
    #     BigInteger,
    #     ForeignKey("users.id", ondelete="SET NULL"),
    #     nullable=True,
    #     comment="X-ray 이미지를 업로드한 유저의 id"
    # )

    uploader_id = Column(
    Integer,
    ForeignKey("users.id", ondelete="SET NULL"),
    nullable=True,
    comment="X-ray 이미지를 업로드한 유저의 id"
)

    image_url = Column(
        String(2048),
        nullable=False,
        comment="이미지 url"
    )

    shooting_datetime = Column(
        DateTime,
        nullable=False,
        comment="X-ray 촬영일시"
    )

    created_at = Column(
        DateTime,
        nullable=False,
        server_default=func.now(),
        comment="X-ray 이미지 등록 일시"
    )