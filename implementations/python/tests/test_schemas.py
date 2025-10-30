"""Tests for schema validation."""
import pytest
from pydantic import ValidationError

from src.models.models import ScoreStatusEnum, StatusEnum
from src.schemas.schemas import (
    CategoryCreate,
    LineItemCreate,
    ResultCreate,
)


def test_category_weight_validation():
    """Test category weight must be between 0 and 1."""
    # Valid weight
    category = CategoryCreate(
        sourcedId="test-cat-001",
        status=StatusEnum.active,
        title="Test Category",
        weight=0.5,
    )
    assert category.weight == 0.5

    # Invalid weight > 1
    with pytest.raises(ValidationError) as exc_info:
        CategoryCreate(
            sourcedId="test-cat-002",
            status=StatusEnum.active,
            title="Test Category",
            weight=1.5,
        )
    assert "less_than_equal" in str(exc_info.value)

    # Invalid weight < 0
    with pytest.raises(ValidationError) as exc_info:
        CategoryCreate(
            sourcedId="test-cat-003",
            status=StatusEnum.active,
            title="Test Category",
            weight=-0.1,
        )
    assert "greater_than_equal" in str(exc_info.value)


def test_line_item_value_range_validation():
    """Test line item max must be greater than min."""
    # Valid range
    line_item = LineItemCreate(
        sourcedId="test-li-001",
        status=StatusEnum.active,
        title="Test Assignment",
        classSourcedId="class-001",
        resultValueMin=0.0,
        resultValueMax=100.0,
    )
    assert line_item.result_value_max > line_item.result_value_min

    # Invalid: max <= min
    with pytest.raises(ValidationError) as exc_info:
        LineItemCreate(
            sourcedId="test-li-002",
            status=StatusEnum.active,
            title="Test Assignment",
            classSourcedId="class-001",
            resultValueMin=100.0,
            resultValueMax=50.0,
        )
    assert "greater than" in str(exc_info.value)


def test_result_score_validation_for_earned_status():
    """Test result score is required for earned statuses."""
    # Valid: score provided for earnedFull
    result = ResultCreate(
        sourcedId="test-res-001",
        lineItemSourcedId="li-001",
        studentSourcedId="student-001",
        scoreStatus=ScoreStatusEnum.earnedFull,
        score=85.0,
    )
    assert result.score == 85.0

    # Invalid: missing score for earnedFull
    with pytest.raises(ValidationError) as exc_info:
        ResultCreate(
            sourcedId="test-res-002",
            lineItemSourcedId="li-001",
            studentSourcedId="student-001",
            scoreStatus=ScoreStatusEnum.earnedFull,
            score=None,
        )
    assert "required" in str(exc_info.value)

    # Invalid: missing score for earnedPartial
    with pytest.raises(ValidationError) as exc_info:
        ResultCreate(
            sourcedId="test-res-003",
            lineItemSourcedId="li-001",
            studentSourcedId="student-001",
            scoreStatus=ScoreStatusEnum.earnedPartial,
            score=None,
        )
    assert "required" in str(exc_info.value)


def test_result_score_validation_for_not_earned_status():
    """Test result score must not be provided for notEarned/notSubmitted."""
    # Valid: no score for notSubmitted
    result = ResultCreate(
        sourcedId="test-res-004",
        lineItemSourcedId="li-001",
        studentSourcedId="student-001",
        scoreStatus=ScoreStatusEnum.notSubmitted,
        score=None,
    )
    assert result.score is None

    # Invalid: score provided for notSubmitted
    with pytest.raises(ValidationError) as exc_info:
        ResultCreate(
            sourcedId="test-res-005",
            lineItemSourcedId="li-001",
            studentSourcedId="student-001",
            scoreStatus=ScoreStatusEnum.notSubmitted,
            score=50.0,
        )
    assert "must not be provided" in str(exc_info.value)

    # Invalid: score provided for notEarned
    with pytest.raises(ValidationError) as exc_info:
        ResultCreate(
            sourcedId="test-res-006",
            lineItemSourcedId="li-001",
            studentSourcedId="student-001",
            scoreStatus=ScoreStatusEnum.notEarned,
            score=0.0,
        )
    assert "must not be provided" in str(exc_info.value)
