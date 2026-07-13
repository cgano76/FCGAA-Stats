import enum
import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class ValidationStatus(str, enum.Enum):
    draft = "brouillon"
    to_check = "a_verifier"
    validated = "valide"
    rejected = "rejete"


class ProductionSpaceCode(str, enum.Enum):
    conventional = "CONVENTIONNEL"
    organic = "BIO"


class ImportStatus(str, enum.Enum):
    draft = "brouillon"
    extracting = "extraction_en_cours"
    extracted = "extrait"
    to_check = "a_verifier"
    to_validate = "a_valider"
    validated = "valide"
    rejected = "rejete"
    archived = "archive"


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    first_name: Mapped[str | None] = mapped_column(String(120))
    last_name: Mapped[str | None] = mapped_column(String(120))
    password_hash: Mapped[str] = mapped_column(String(255))
    role_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("roles.id"))
    oga_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("ogas.id"))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime)
    identity_provider: Mapped[str | None] = mapped_column(String(80))
    external_subject_id: Mapped[str | None] = mapped_column(String(255))


class Role(Base, TimestampMixin):
    __tablename__ = "roles"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(80), unique=True)
    label: Mapped[str] = mapped_column(String(120))


class Oga(Base, TimestampMixin):
    __tablename__ = "ogas"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255))
    code_oga: Mapped[str] = mapped_column(String(20), unique=True, index=True)
    email: Mapped[str | None] = mapped_column(String(255))
    phone: Mapped[str | None] = mapped_column(String(50))
    address: Mapped[str | None] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


class Subscription(Base, TimestampMixin):
    __tablename__ = "subscriptions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    oga_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("ogas.id"), index=True)
    starts_at: Mapped[datetime] = mapped_column(DateTime)
    ends_at: Mapped[datetime] = mapped_column(DateTime)
    status: Mapped[str] = mapped_column(String(40), default="active")


class AccessException(Base, TimestampMixin):
    __tablename__ = "access_exceptions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    oga_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("ogas.id"), index=True)
    reason: Mapped[str] = mapped_column(Text)
    starts_at: Mapped[datetime] = mapped_column(DateTime)
    ends_at: Mapped[datetime | None] = mapped_column(DateTime)
    granted_by: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id"))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


class SourceFile(Base, TimestampMixin):
    __tablename__ = "source_files"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    original_name: Mapped[str] = mapped_column(String(500))
    file_type: Mapped[str] = mapped_column(String(80))
    storage_path: Mapped[str] = mapped_column(String(1000))
    sha256: Mapped[str | None] = mapped_column(String(64), unique=True)
    detected_year: Mapped[int | None] = mapped_column(Integer)
    uploaded_by: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id"))
    status: Mapped[ImportStatus] = mapped_column(Enum(ImportStatus), default=ImportStatus.draft)


class ImportBatch(Base, TimestampMixin):
    __tablename__ = "import_batches"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source_file_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("source_files.id"), index=True)
    status: Mapped[ImportStatus] = mapped_column(Enum(ImportStatus), default=ImportStatus.draft)
    report: Mapped[dict | None] = mapped_column(JSONB)
    extracted_rows_count: Mapped[int] = mapped_column(Integer, default=0)
    anomalies_count: Mapped[int] = mapped_column(Integer, default=0)


class StatisticalYear(Base, TimestampMixin):
    __tablename__ = "statistical_years"
    __table_args__ = (
        UniqueConstraint("annee_recueil", "annee_cloture", "annee_recolte", "annee_exercice"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    annee_recueil: Mapped[int | None] = mapped_column(Integer)
    annee_cloture: Mapped[int] = mapped_column(Integer, index=True)
    annee_recolte: Mapped[int | None] = mapped_column(Integer)
    annee_exercice: Mapped[int | None] = mapped_column(Integer)
    label: Mapped[str] = mapped_column(String(160))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


class ProductionSpace(Base, TimestampMixin):
    __tablename__ = "production_spaces"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    code: Mapped[ProductionSpaceCode] = mapped_column(Enum(ProductionSpaceCode), unique=True)
    label: Mapped[str] = mapped_column(String(120))


class Profession(Base, TimestampMixin):
    __tablename__ = "professions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    code_nomenclature: Mapped[str] = mapped_column(String(20), unique=True, index=True)
    label: Mapped[str] = mapped_column(String(255))
    family: Mapped[str | None] = mapped_column(String(160))
    production_type: Mapped[str | None] = mapped_column(String(160))
    bio_possible: Mapped[bool] = mapped_column(Boolean, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


class Zone(Base, TimestampMixin):
    __tablename__ = "zones"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    code: Mapped[str] = mapped_column(String(20), unique=True)
    label: Mapped[str] = mapped_column(String(120))
    description: Mapped[str | None] = mapped_column(Text)


class Quartile(Base, TimestampMixin):
    __tablename__ = "quartiles"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    code: Mapped[str] = mapped_column(String(40), unique=True)
    label: Mapped[str] = mapped_column(String(120))
    sort_order: Mapped[int] = mapped_column(Integer)


class Indicator(Base, TimestampMixin):
    __tablename__ = "indicators"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    code: Mapped[str] = mapped_column(String(40), unique=True, index=True)
    label: Mapped[str] = mapped_column(String(255))
    category: Mapped[str | None] = mapped_column(String(120))
    unit: Mapped[str | None] = mapped_column(String(40))
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    is_public_allowed: Mapped[bool] = mapped_column(Boolean, default=False)


class Formula(Base, TimestampMixin):
    __tablename__ = "formulas"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    code: Mapped[str] = mapped_column(String(40), index=True)
    label: Mapped[str] = mapped_column(String(255))
    expression: Mapped[str] = mapped_column(Text)
    source: Mapped[str] = mapped_column(String(255))
    version: Mapped[str] = mapped_column(String(40), default="1")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


class StatisticsValue(Base, TimestampMixin):
    __tablename__ = "statistics_values"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    statistical_year_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("statistical_years.id"), index=True)
    production_space_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("production_spaces.id"), index=True)
    profession_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("professions.id"), index=True)
    indicator_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("indicators.id"), index=True)
    zone_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("zones.id"), index=True)
    quartile_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("quartiles.id"), index=True)
    value_numeric: Mapped[float | None] = mapped_column(Numeric(18, 4))
    value_text: Mapped[str | None] = mapped_column(String(255))
    unit: Mapped[str | None] = mapped_column(String(40))
    value_kind: Mapped[str] = mapped_column(String(80), default="moyenne")
    validation_status: Mapped[ValidationStatus] = mapped_column(
        Enum(ValidationStatus), default=ValidationStatus.draft, index=True
    )
    confidence_score: Mapped[float | None] = mapped_column(Float)
    source_file_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("source_files.id"))
    source_page: Mapped[int | None] = mapped_column(Integer)
    source_table_label: Mapped[str | None] = mapped_column(String(255))
    source_row_label: Mapped[str | None] = mapped_column(String(255))
    source_column_label: Mapped[str | None] = mapped_column(String(255))
    validated_at: Mapped[datetime | None] = mapped_column(DateTime)
    validated_by: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id"))

    indicator: Mapped[Indicator] = relationship()


class AiAnalysis(Base, TimestampMixin):
    __tablename__ = "ai_analyses"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    profession_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("professions.id"))
    statistical_year_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("statistical_years.id"))
    production_space_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("production_spaces.id"))
    analysis_type: Mapped[str] = mapped_column(String(80))
    prompt_version: Mapped[str] = mapped_column(String(40), default="1")
    model_provider: Mapped[str] = mapped_column(String(80), default="mistral")
    model_name: Mapped[str] = mapped_column(String(120))
    content: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(40), default="generee")
    generated_by: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id"))
    source_snapshot: Mapped[dict | None] = mapped_column(JSONB)


class Export(Base, TimestampMixin):
    __tablename__ = "exports"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    export_type: Mapped[str] = mapped_column(String(40))
    title: Mapped[str] = mapped_column(String(255))
    storage_path: Mapped[str | None] = mapped_column(String(1000))
    generated_by: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id"))
    parameters: Mapped[dict | None] = mapped_column(JSONB)


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    user_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id"))
    oga_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("ogas.id"))
    action: Mapped[str] = mapped_column(String(120), index=True)
    resource_type: Mapped[str | None] = mapped_column(String(120))
    resource_id: Mapped[str | None] = mapped_column(String(120))
    details: Mapped[dict | None] = mapped_column(JSONB)

