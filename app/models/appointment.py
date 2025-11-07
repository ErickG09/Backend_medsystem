from datetime import datetime as dt
from enum import Enum
from sqlalchemy import (
    String, DateTime, Integer, ForeignKey, Enum as PgEnum
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ..extensions import db

class AppointmentStatus(str, Enum):
    PENDING   = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    NO_SHOW   = "no_show"
    COMPLETED = "completed"

class AppointmentType(str, Enum):
    CONSULTA       = "consulta"
    CONTROL        = "control"
    PROCEDIMIENTO  = "procedimiento"
    OTRO           = "otro"

class Appointment(db.Model):
    __tablename__ = "appointments"

    id: Mapped[int] = mapped_column(primary_key=True)

    # Relaciones
    patient_id: Mapped[int] = mapped_column(
        ForeignKey("patients.id", ondelete="CASCADE"), index=True, nullable=False
    )
    professional_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), index=True, nullable=True
    )

    # Core de agenda
    title: Mapped[str] = mapped_column(String(200), nullable=False)  # Nombre visible del evento
    start_at: Mapped[dt] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    end_at: Mapped[dt]   = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    duration_min: Mapped[int] = mapped_column(Integer, nullable=False)  # redundante para rapidez de UI

    status: Mapped[AppointmentStatus] = mapped_column(
        PgEnum(AppointmentStatus, name="appointment_status"), nullable=False, default=AppointmentStatus.PENDING, index=True
    )
    appt_type: Mapped[AppointmentType] = mapped_column(
        PgEnum(AppointmentType, name="appointment_type"), nullable=False, default=AppointmentType.CONSULTA, index=True
    )

    # Extras
    treatment: Mapped[str | None] = mapped_column(String(300), nullable=True)  # opcional
    notes: Mapped[str | None] = mapped_column(String(4000), nullable=True)

    created_at: Mapped[dt] = mapped_column(
        DateTime(timezone=True), server_default=db.func.now(), nullable=False
    )
    updated_at: Mapped[dt] = mapped_column(
        DateTime(timezone=True), server_default=db.func.now(),
        onupdate=db.func.now(), nullable=False
    )

    patient = relationship("Patient")
    professional = relationship("User")
