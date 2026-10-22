from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Index, String, Text, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Service(Base):
    __tablename__ = "services"
    __table_args__ = (
        CheckConstraint("check_interval > 0", name="ck_services_positive_interval"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    url: Mapped[str] = mapped_column(Text, nullable=False)
    check_interval: Mapped[int] = mapped_column(nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    checks: Mapped[list["ServiceCheck"]] = relationship(
        back_populates="service", passive_deletes=True
    )


class ServiceCheck(Base):
    __tablename__ = "service_checks"
    __table_args__ = (
        Index("ix_service_checks_service_id_checked_at", "service_id", "checked_at"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    service_id: Mapped[int] = mapped_column(
        ForeignKey("services.id", ondelete="CASCADE"), nullable=False
    )
    status: Mapped[str] = mapped_column(String(10), nullable=False)
    status_code: Mapped[int | None]
    response_time_ms: Mapped[float | None]
    checked_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    error: Mapped[str | None] = mapped_column(Text)

    service: Mapped[Service] = relationship(back_populates="checks")
