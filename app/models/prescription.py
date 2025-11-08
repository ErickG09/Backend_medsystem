from datetime import datetime as dt
from sqlalchemy import String, DateTime, Integer, Float, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ..extensions import db

class Prescription(db.Model):
    __tablename__ = "prescriptions"

    id: Mapped[int] = mapped_column(primary_key=True)

    # Relaciones
    patient_id: Mapped[int] = mapped_column(
        ForeignKey("patients.id", ondelete="CASCADE"), index=True, nullable=False
    )
    consultation_id: Mapped[int | None] = mapped_column(
        ForeignKey("consultations.id", ondelete="SET NULL"), index=True, nullable=True
    )
    professional_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), index=True, nullable=True
    )

    # Fecha/hora
    issued_at: Mapped[dt] = mapped_column(DateTime(timezone=True), nullable=False, index=True)

    # Signos vitales
    temp_c: Mapped[float | None] = mapped_column(Float, nullable=True)
    bp_sys: Mapped[int | None] = mapped_column(Integer, nullable=True)
    bp_dia: Mapped[int | None] = mapped_column(Integer, nullable=True)
    heart_rate: Mapped[int | None] = mapped_column(Integer, nullable=True)
    resp_rate: Mapped[int | None] = mapped_column(Integer, nullable=True)
    bmi: Mapped[float | None] = mapped_column(Float, nullable=True)
    spo2: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Contenido
    diagnosis: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    prescription_text: Mapped[str | None] = mapped_column(String(4000), nullable=True)
    care_instructions: Mapped[str | None] = mapped_column(String(4000), nullable=True)
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
            "prescriptions",
            cascade="all, delete-orphan",
            passive_deletes=True,   # <= consistente con consultas/archivos
        ),
    )
    consultation = relationship("Consultation")
    professional = relationship("User")
