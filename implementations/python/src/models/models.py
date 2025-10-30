"""
SQLAlchemy models for OneRoster Gradebook Service.
"""

import enum
from datetime import datetime

from sqlalchemy import (
    CheckConstraint,
    Column,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Index,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from src.config.database import Base


class StatusEnum(str, enum.Enum):
    """Status enum for all entities."""

    active = "active"
    tobedeleted = "tobedeleted"


class ScoreStatusEnum(str, enum.Enum):
    """Score status enum for Result model."""

    earnedPartial = "earnedPartial"
    earnedFull = "earnedFull"
    notEarned = "notEarned"
    notSubmitted = "notSubmitted"
    submitted = "submitted"
    late = "late"
    incomplete = "incomplete"
    missing = "missing"
    inProgress = "inProgress"
    withdrawn = "withdrawn"


class Category(Base):
    """
    Category model - OneRoster Gradebook Category.
    Represents a grading category for line items.
    """

    __tablename__ = "categories"

    sourced_id = Column(String(255), primary_key=True)
    status = Column(
        Enum(StatusEnum, name="status_enum"),
        nullable=False,
        default=StatusEnum.active,
    )
    date_last_modified = Column(DateTime, nullable=False, default=datetime.utcnow)
    title = Column(String(255), nullable=False)
    weight = Column(Float, CheckConstraint("weight >= 0 AND weight <= 1"))
    metadata_ = Column("metadata", JSONB)  # Use metadata_ as attribute name

    # Relationships
    line_items = relationship("LineItem", back_populates="category")

    # Indexes
    __table_args__ = (
        Index("idx_categories_status", "status"),
        Index("idx_categories_date_last_modified", "date_last_modified"),
    )

    def to_oneroster_dict(self) -> dict:
        """Convert to OneRoster format."""
        result = {
            "sourcedId": self.sourced_id,
            "status": self.status.value,
            "dateLastModified": self.date_last_modified.isoformat() + "Z",
            "title": self.title,
        }
        if self.weight is not None:
            result["weight"] = self.weight
        if self.metadata_:
            result["metadata"] = self.metadata_
        return result


class LineItem(Base):
    """
    LineItem model - OneRoster Gradebook Line Item.
    Represents a gradable assignment or assessment.
    """

    __tablename__ = "line_items"

    sourced_id = Column(String(255), primary_key=True)
    status = Column(
        Enum(StatusEnum, name="status_enum"),
        nullable=False,
        default=StatusEnum.active,
    )
    date_last_modified = Column(DateTime, nullable=False, default=datetime.utcnow)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    assign_date = Column(DateTime)
    due_date = Column(DateTime)
    class_sourced_id = Column(String(255), nullable=False)
    category_sourced_id = Column(String(255), ForeignKey("categories.sourced_id"))
    result_value_min = Column(Float, nullable=False, default=0.0)
    result_value_max = Column(Float, nullable=False, default=100.0)
    metadata_ = Column("metadata", JSONB)  # Use metadata_ as attribute name

    # Relationships
    category = relationship("Category", back_populates="line_items")
    results = relationship("Result", back_populates="line_item")

    # Indexes
    __table_args__ = (
        Index("idx_line_items_class", "class_sourced_id"),
        Index("idx_line_items_category", "category_sourced_id"),
        Index("idx_line_items_status", "status"),
        Index("idx_line_items_date_last_modified", "date_last_modified"),
        Index("idx_line_items_due_date", "due_date"),
        Index("idx_line_items_class_status", "class_sourced_id", "status"),
        Index("idx_line_items_category_status", "category_sourced_id", "status"),
        CheckConstraint("result_value_max > result_value_min", name="check_value_range"),
    )

    def to_oneroster_dict(self) -> dict:
        """Convert to OneRoster format."""
        from src.config.settings import settings

        result = {
            "sourcedId": self.sourced_id,
            "status": self.status.value,
            "dateLastModified": self.date_last_modified.isoformat() + "Z",
            "title": self.title,
            "class": {
                "href": f"{settings.rostering_service_base_url}/classes/{self.class_sourced_id}",
                "sourcedId": self.class_sourced_id,
                "type": "class",
            },
            "resultValueMin": self.result_value_min,
            "resultValueMax": self.result_value_max,
        }

        if self.description:
            result["description"] = self.description
        if self.assign_date:
            result["assignDate"] = self.assign_date.isoformat() + "Z"
        if self.due_date:
            result["dueDate"] = self.due_date.isoformat() + "Z"
        if self.category_sourced_id:
            result["category"] = {
                "href": f"{settings.api_base_url}/ims/oneroster/v1p2/categories/{self.category_sourced_id}",
                "sourcedId": self.category_sourced_id,
                "type": "category",
            }
        if self.metadata_:
            result["metadata"] = self.metadata_
        return result


class Result(Base):
    """
    Result model - OneRoster Gradebook Result.
    Represents a student's score/grade for a line item.
    """

    __tablename__ = "results"

    sourced_id = Column(String(255), primary_key=True)
    status = Column(
        Enum(StatusEnum, name="status_enum"),
        nullable=False,
        default=StatusEnum.active,
    )
    date_last_modified = Column(DateTime, nullable=False, default=datetime.utcnow)
    line_item_sourced_id = Column(String(255), ForeignKey("line_items.sourced_id"), nullable=False)
    student_sourced_id = Column(String(255), nullable=False)
    score_status = Column(
        Enum(ScoreStatusEnum, name="score_status_enum"),
        nullable=False,
    )
    score = Column(Float)
    score_date = Column(DateTime)
    comment = Column(Text)
    metadata_ = Column("metadata", JSONB)  # Use metadata_ as attribute name

    # Relationships
    line_item = relationship("LineItem", back_populates="results")

    # Indexes
    __table_args__ = (
        Index(
            "idx_results_lineitem_student",
            "line_item_sourced_id",
            "student_sourced_id",
            unique=True,
        ),
        Index("idx_results_student", "student_sourced_id"),
        Index("idx_results_score_status", "score_status"),
        Index("idx_results_date_last_modified", "date_last_modified"),
    )

    def to_oneroster_dict(self) -> dict:
        """Convert to OneRoster format."""
        from src.config.settings import settings

        result = {
            "sourcedId": self.sourced_id,
            "status": self.status.value,
            "dateLastModified": self.date_last_modified.isoformat() + "Z",
            "lineItem": {
                "href": f"{settings.api_base_url}/ims/oneroster/v1p2/lineItems/{self.line_item_sourced_id}",
                "sourcedId": self.line_item_sourced_id,
                "type": "lineItem",
            },
            "student": {
                "href": f"{settings.rostering_service_base_url}/users/{self.student_sourced_id}",
                "sourcedId": self.student_sourced_id,
                "type": "user",
            },
            "scoreStatus": self.score_status.value,
        }

        if self.score is not None:
            result["score"] = float(self.score)
        if self.score_date:
            result["scoreDate"] = self.score_date.isoformat() + "Z"
        if self.comment:
            result["comment"] = self.comment
        if self.metadata_:
            result["metadata"] = self.metadata_

        return result
