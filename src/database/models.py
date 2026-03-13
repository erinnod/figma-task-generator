import uuid
from datetime import datetime
from sqlalchemy import (
    String, Text, Integer, Boolean, DateTime, ForeignKey, JSON
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from src.database.base import Base

def generate_uuid():
    return str(uuid.uuid4())

class Screen(Base):
    __tablename__ = "figma_screens"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=generate_uuid
    )
    # text type to match OnTarget's project table
    project_id: Mapped[str] = mapped_column(String, nullable=False)
    figma_node_id: Mapped[str] = mapped_column(String(255), nullable=False)

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    page_name: Mapped[str] = mapped_column(String(255), nullable=True)
    blob_path: Mapped[str] = mapped_column(String(500), nullable=True)
    order_index: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[str] = mapped_column(String(50), default="pending")
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )

    ai_review: Mapped["AIReview"] = relationship(
        back_populates="screen",
        cascade="all, delete-orphan",
        uselist=False
    )
    client_responses: Mapped[list["ClientResponse"]] = relationship(
        back_populates="screen", cascade="all, delete-orphan"
    )
    designer_notes: Mapped[list["DesignerNote"]] = relationship(
        back_populates="screen", cascade="all, delete-orphan"
    )
    tasks: Mapped[list["Task"]] = relationship(
        back_populates="screen"
    )

class AIReview(Base):
    __tablename__ = "figma_ai_reviews"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), primary_key=True, default=generate_uuid
    )
    screen_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("figma_screens.id", ondelete="CASCADE"),
        nullable=False
    )
    assumptions: Mapped[dict] = mapped_column(JSON, nullable=True)
    questions: Mapped[dict] = mapped_column(JSON, nullable=True)
    confidence_scores: Mapped[dict] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )

    screen: Mapped["Screen"] = relationship(back_populates="ai_review")


class ClientResponse(Base):
    __tablename__ = "figma_client_responses"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), primary_key=True, default=generate_uuid
    )
    screen_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("figma_screens.id", ondelete="CASCADE"),
        nullable=False
    )
    question_index: Mapped[int] = mapped_column(Integer, nullable=False)
    question_text: Mapped[str] = mapped_column(String, nullable=False)
    response_text: Mapped[str] = mapped_column(Text, nullable=True)
    submitted_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )

    screen: Mapped["Screen"] = relationship(
        back_populates="client_responses"
    )


class ReviewToken(Base):
    __tablename__ = "figma_review_tokens"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), primary_key=True, default=generate_uuid
    )
    # text to match OnTarget project table
    project_id: Mapped[str] = mapped_column(String, nullable=False)
    client_email: Mapped[str] = mapped_column(
        String(255), nullable=False
    )
    token: Mapped[str] = mapped_column(
        String(500), unique=True, nullable=False
    )
    expires_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False
    )
    used_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )


class DesignerNote(Base):
    __tablename__ = "figma_designer_notes"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), primary_key=True, default=generate_uuid
    )
    screen_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("figma_screens.id", ondelete="CASCADE"),
        nullable=False
    )
    note: Mapped[str] = mapped_column(Text, nullable=False)
    resolved: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )

    screen: Mapped["Screen"] = relationship(
        back_populates="designer_notes"
    )


class Task(Base):
    __tablename__ = "figma_tasks"

    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), primary_key=True, default=generate_uuid
    )
    # text to match OnTarget project table
    project_id: Mapped[str] = mapped_column(String, nullable=False)
    screen_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("figma_screens.id", ondelete="SET NULL"),
        nullable=True
    )
    category: Mapped[str] = mapped_column(String(50), nullable=False)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    complexity: Mapped[str] = mapped_column(String(20), nullable=True)
    acceptance_criteria: Mapped[dict] = mapped_column(
        JSON, nullable=True
    )
    ontarget_task_id: Mapped[str] = mapped_column(
        String, nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )

    screen: Mapped["Screen"] = relationship(back_populates="tasks")