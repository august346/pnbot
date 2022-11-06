import os
from typing import Generator, Optional

from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, create_engine, UniqueConstraint, Index, select
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import declarative_base, relationship, Session

DATABASE_URI = os.environ.get(
    "DATABASE_URI",
    "postgresql://postgres:example@localhost:5432/pnbot123"
)

engine = create_engine(DATABASE_URI)
session = Session(engine, future=True)

Base = declarative_base()


class Video(Base):
    __tablename__ = "video"

    id = Column(Integer, primary_key=True)
    md5 = Column(String(128), unique=True, nullable=False)
    meta = Column(postgresql.JSONB, nullable=False)
    extracted = Column(Boolean, nullable=False)

    signatures = relationship("Signature", back_populates="video")

    def save(self) -> "Video":
        session.add(self)
        session.commit()

        return self

    def mark_extracted(self) -> None:
        self.extracted = True

        session.add(self)
        session.commit()

    def is_duplicate(self) -> Optional["Video"]:
        return session.execute(
            select(Video).filter_by(md5=self.md5)
        ).scalar_one_or_none()

    @classmethod
    def ids_to_compare(cls, video_id: int) -> list[int]:
        return session.execute(
            select(Video.id).filter(Video.id!=video_id)
        ).scalars().all()


class Signature(Base):
    __tablename__ = "signature"

    id = Column(Integer, primary_key=True)
    version = Column(Integer, nullable=False)
    range = Column(Integer, nullable=False)
    meta = Column(postgresql.JSONB, nullable=False)

    video_id = Column(Integer, ForeignKey("video.id"), nullable=False)
    video = relationship("Video", back_populates="signatures")

    __table_args__ = (
        UniqueConstraint(
            'video_id',
            'version',
            'range'
        ),
    )

    @staticmethod
    def set_from_video_id(video_id: int) -> Generator["Signature", None, None]:
        return session.execute(
            select(Signature).filter_by(video_id=video_id)
        ).scalars().all()

    def save(self, video_id: int) -> "Signature":
        self.video_id = video_id

        session.add(self)
        session.commit()

        return self

    @classmethod
    def count(cls, video_id: int, version: int) -> int:
        return session.query(Signature).filter_by(
            video_id=video_id,
            version=version
        ).count()


class Compare(Base):
    __tablename__ = "compare"

    id = Column(Integer, primary_key=True)
    version = Column(Integer, nullable=False)
    result = Column(Integer, nullable=False)

    fst_video_id = Column(ForeignKey("video.id"), nullable=False)
    snd_video_id = Column(ForeignKey("video.id"), nullable=False)
    fst_video = relationship("Video", uselist=True, backref="as_fst", foreign_keys=[fst_video_id])
    snd_video = relationship("Video", uselist=True, backref="as_snd", foreign_keys=[snd_video_id])

    __table_args__ = (
        UniqueConstraint(
            'fst_video_id',
            'snd_video_id',
            'version',
        ),
        Index('compare_fsv', 'fst_video_id', 'snd_video_id', 'version')
    )

    def save(self, fst_id: int, snd_id: int) -> "Compare":
        self.fst_video_id = fst_id
        self.snd_video_id = snd_id

        session.add(self)
        session.commit()

        return self

    @classmethod
    def get_result(cls, fst_id: int, snd_id: int, version: int) -> Optional[int]:
        return session.execute(
            select(Compare.result).filter_by(fst_video_id=fst_id, snd_video_id=snd_id, version=version)
        ).scalar_one_or_none()
