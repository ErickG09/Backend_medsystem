from datetime import datetime as dt
from sqlalchemy import String, DateTime, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ..extensions import db

class Consultation(db.Model):
    __tablename__ = "consultations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    patient_id: Mapped[int] = mapped_column(
        ForeignKey("patients.id", ondelete="CASCADE"), index=True, nullable=False
    )
    professional_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), index=True, nullable=True
    )

    # Título / nombre de la consulta
    title: Mapped[str] = mapped_column(String(200), nullable=False)

    # Fecha y hora (UTC)
    datetime: Mapped[dt] = mapped_column(DateTime(timezone=True), nullable=False, index=True)

    # Notas
    notes: Mapped[str | None] = mapped_column(String(4000), nullable=True)

    # Productos usados (texto simple)
    products: Mapped[str | None] = mapped_column(String(2000), nullable=True)

    created_at: Mapped[dt] = mapped_column(
        DateTime(timezone=True), server_default=db.func.now(), nullable=False
    )
    updated_at: Mapped[dt] = mapped_column(
        DateTime(timezone=True), server_default=db.func.now(), onupdate=db.func.now(), nullable=False
    )

    patient = relationship(
        "Patient",
        backref=db.backref(
            "consultations",
            cascade="all, delete-orphan",
            passive_deletes=True,   # <= importante con ON DELETE CASCADE
        ),
    )
    professional = relationship("User")
