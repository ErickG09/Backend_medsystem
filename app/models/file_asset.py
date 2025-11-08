from datetime import datetime
from enum import Enum
from sqlalchemy import String, Integer, DateTime, ForeignKey, Enum as PgEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ..extensions import db

class FileKind(str, Enum):
    DOCUMENT = "document"    # PDFs, identificaciones, consentimientos escaneados
    PHOTO = "photo"          # fotos clínicas (antes/después)

class PhotoPhase(str, Enum):
    BEFORE = "before"
    AFTER = "after"

class FileAsset(db.Model):
    __tablename__ = "file_assets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    patient_id: Mapped[int] = mapped_column(
        ForeignKey("patients.id", ondelete="CASCADE"), index=True, nullable=False
    )
    kind: Mapped[FileKind] = mapped_column(PgEnum(FileKind, name="file_kind"), nullable=False, index=True)

    # Solo si es PHOTO
    photo_phase: Mapped[PhotoPhase | None] = mapped_column(PgEnum(PhotoPhase, name="photo_phase"), nullable=True, index=True)
    photo_order: Mapped[int | None] = mapped_column(Integer, nullable=True)

    url: Mapped[str] = mapped_column(String(1000), nullable=False)
    mime_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    title: Mapped[str | None] = mapped_column(String(255), nullable=True)
    note: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    size_bytes: Mapped[int | None] = mapped_column(Integer, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=db.func.now(), nullable=False)

    patient = relationship(
        "Patient",
        backref=db.backref(
            "files",
            cascade="all, delete-orphan",
            passive_deletes=True,   # <= consistente
        ),
    )
