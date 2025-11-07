from datetime import date, datetime
from enum import Enum
from sqlalchemy import String, Date, Boolean, Integer, DateTime, Float
from sqlalchemy.orm import Mapped, mapped_column
from ..extensions import db

class Sex(str, Enum):
    FEMALE = "F"
    MALE = "M"
    OTHER = "O"

class Patient(db.Model):
    __tablename__ = "patients"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    # Identificación básica (OBLIGATORIOS en creación)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    last_name: Mapped[str] = mapped_column(String(150), nullable=False, index=True)
    date_of_birth: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    sex: Mapped[Sex] = mapped_column(db.Enum(Sex, name="sex_enum"), nullable=False, index=True)

    # Contacto principal (OBLIGATORIOS en creación)
    phone: Mapped[str] = mapped_column(String(30), nullable=False, index=True)
    email: Mapped[str] = mapped_column(String(255), nullable=False, index=True)

    # Otros datos
    photo_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    address: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # Datos clínicos
    weight_kg: Mapped[float | None] = mapped_column(Float, nullable=True)   # OBLIG en sección 2
    height_m: Mapped[float | None] = mapped_column(Float, nullable=True)    # OBLIG en sección 2
    bmi: Mapped[float | None] = mapped_column(Float, nullable=True)         # calculado y guardado
    age_years: Mapped[int | None] = mapped_column(Integer, nullable=True)   # calculado y guardado

    past_history: Mapped[str | None] = mapped_column(String(2000), nullable=True)     # antecedentes patológicos
    allergies: Mapped[str | None] = mapped_column(String(2000), nullable=True)
    treatments_of_interest: Mapped[str | None] = mapped_column(String(2000), nullable=True)  # OBLIG en sección 2

    # Documentos/consentimientos (sección 3)
    privacy_notice_accepted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)   # OBLIG en sección 3
    informed_consent_accepted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False) # OBLIG en sección 3

    # Contacto de emergencia
    emergency_full_name: Mapped[str | None] = mapped_column(String(200), nullable=True)
    emergency_phone: Mapped[str | None] = mapped_column(String(30), nullable=True)
    emergency_relation: Mapped[str | None] = mapped_column(String(100), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=db.func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=db.func.now(),
                                                 onupdate=db.func.now(), nullable=False)

    # Helpers -----------------------------------------------------------------
    @property
    def display_id(self) -> str:
        """ID legible para UI (no se persiste)."""
        return f"P-{self.id:04d}" if self.id else "P-????"

    def recalc_age_and_bmi(self):
        # edad
        if self.date_of_birth:
            today = date.today()
            years = today.year - self.date_of_birth.year - (
                (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
            )
            self.age_years = max(0, years)
        else:
            self.age_years = None

        # IMC
        if self.weight_kg and self.height_m and self.height_m > 0:
            self.bmi = round(self.weight_kg / (self.height_m ** 2), 1)
        else:
            self.bmi = None
