"""
Pydantic schemas for API request/response validation.
"""

from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field, field_validator

from src.models.models import ScoreStatusEnum, StatusEnum

# ==================== Category Schemas ====================


class CategoryBase(BaseModel):
    """Base category schema."""

    title: str = Field(..., min_length=1, max_length=255)
    weight: Optional[float] = Field(None, ge=0.0, le=1.0)
    metadata: Optional[Dict[str, Any]] = None


class CategoryCreate(CategoryBase):
    """Schema for creating a category."""

    sourced_id: str = Field(..., min_length=1, max_length=255, alias="sourcedId")


class CategoryUpdate(BaseModel):
    """Schema for updating a category."""

    title: Optional[str] = Field(None, min_length=1, max_length=255)
    weight: Optional[float] = Field(None, ge=0.0, le=1.0)
    status: Optional[StatusEnum] = None
    metadata: Optional[Dict[str, Any]] = None


class CategoryResponse(BaseModel):
    """Schema for category response (OneRoster format)."""

    sourced_id: str = Field(..., alias="sourcedId")
    status: str
    date_last_modified: str = Field(..., alias="dateLastModified")
    title: str
    weight: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None

    model_config = {"populate_by_name": True}


# ==================== LineItem Schemas ====================


class LineItemBase(BaseModel):
    """Base line item schema."""

    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    assign_date: Optional[datetime] = Field(None, alias="assignDate")
    due_date: Optional[datetime] = Field(None, alias="dueDate")
    class_sourced_id: str = Field(..., min_length=1, max_length=255, alias="classSourcedId")
    category_sourced_id: Optional[str] = Field(
        None, min_length=1, max_length=255, alias="categorySourcedId"
    )
    result_value_min: float = Field(default=0.0, alias="resultValueMin")
    result_value_max: float = Field(default=100.0, alias="resultValueMax")
    metadata: Optional[Dict[str, Any]] = None

    @field_validator("result_value_max")
    @classmethod
    def validate_value_range(cls, v: float, info) -> float:
        """Validate that max > min."""
        if "result_value_min" in info.data and v <= info.data["result_value_min"]:
            raise ValueError("result_value_max must be greater than result_value_min")
        return v


class LineItemCreate(LineItemBase):
    """Schema for creating a line item."""

    sourced_id: str = Field(..., min_length=1, max_length=255, alias="sourcedId")


class LineItemUpdate(BaseModel):
    """Schema for updating a line item."""

    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    assign_date: Optional[datetime] = Field(None, alias="assignDate")
    due_date: Optional[datetime] = Field(None, alias="dueDate")
    category_sourced_id: Optional[str] = Field(None, alias="categorySourcedId")
    result_value_min: Optional[float] = Field(None, alias="resultValueMin")
    result_value_max: Optional[float] = Field(None, alias="resultValueMax")
    status: Optional[StatusEnum] = None
    metadata: Optional[Dict[str, Any]] = None


class LineItemResponse(BaseModel):
    """Schema for line item response (OneRoster format)."""

    sourced_id: str = Field(..., alias="sourcedId")
    status: str
    date_last_modified: str = Field(..., alias="dateLastModified")
    title: str
    description: Optional[str] = None
    assign_date: Optional[str] = Field(None, alias="assignDate")
    due_date: Optional[str] = Field(None, alias="dueDate")
    class_ref: Dict[str, str] = Field(..., alias="class")
    category: Optional[Dict[str, str]] = None
    result_value_min: float = Field(..., alias="resultValueMin")
    result_value_max: float = Field(..., alias="resultValueMax")
    metadata: Optional[Dict[str, Any]] = None

    model_config = {"populate_by_name": True}


# ==================== Result Schemas ====================


class ResultBase(BaseModel):
    """Base result schema."""

    line_item_sourced_id: str = Field(..., min_length=1, max_length=255, alias="lineItemSourcedId")
    student_sourced_id: str = Field(..., min_length=1, max_length=255, alias="studentSourcedId")
    score_status: ScoreStatusEnum = Field(..., alias="scoreStatus")
    score: Optional[float] = None
    score_date: Optional[datetime] = Field(None, alias="scoreDate")
    comment: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

    @field_validator("score")
    @classmethod
    def validate_score_status(cls, v: Optional[float], info) -> Optional[float]:
        """Validate score based on score_status."""
        if "score_status" not in info.data:
            return v

        score_status = info.data["score_status"]
        # Score is required for earned/partial statuses
        if score_status in [ScoreStatusEnum.earnedFull, ScoreStatusEnum.earnedPartial]:
            if v is None:
                raise ValueError(f"score is required for status '{score_status.value}'")
        # Score should not be provided for notEarned or notSubmitted
        elif score_status in [ScoreStatusEnum.notEarned, ScoreStatusEnum.notSubmitted]:
            if v is not None:
                raise ValueError(f"score must not be provided for status '{score_status.value}'")
        return v


class ResultCreate(ResultBase):
    """Schema for creating a result."""

    sourced_id: str = Field(..., min_length=1, max_length=255, alias="sourcedId")


class ResultUpdate(BaseModel):
    """Schema for updating a result."""

    score_status: Optional[ScoreStatusEnum] = Field(None, alias="scoreStatus")
    score: Optional[float] = None
    score_date: Optional[datetime] = Field(None, alias="scoreDate")
    comment: Optional[str] = None
    status: Optional[StatusEnum] = None
    metadata: Optional[Dict[str, Any]] = None


class ResultResponse(BaseModel):
    """Schema for result response (OneRoster format)."""

    sourced_id: str = Field(..., alias="sourcedId")
    status: str
    date_last_modified: str = Field(..., alias="dateLastModified")
    line_item: Dict[str, str] = Field(..., alias="lineItem")
    student: Dict[str, str]
    score_status: str = Field(..., alias="scoreStatus")
    score: Optional[float] = None
    score_date: Optional[str] = Field(None, alias="scoreDate")
    comment: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

    model_config = {"populate_by_name": True}


# ==================== Collection Response ====================


class CollectionResponse(BaseModel):
    """Generic collection response with pagination."""

    data: list
    total: int
    limit: int
    offset: int


# ==================== Error Response ====================


class ErrorResponse(BaseModel):
    """OneRoster error response format."""

    imsx_code_major: str = Field(..., alias="imsx_codeMajor")
    imsx_severity: str = Field(..., alias="imsx_severity")
    imsx_description: str = Field(..., alias="imsx_description")
    imsx_code_minor: Optional[str] = Field(None, alias="imsx_codeMinor")

    model_config = {"populate_by_name": True}
