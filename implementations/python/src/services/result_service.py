"""
Result Service
Business logic for results operations.
"""

from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy.orm import Session

from src.models.models import Result, StatusEnum
from src.utils.query_parser import parse_filter, parse_sort


class ResultService:
    """Service class for Result operations."""

    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, sourced_id: str) -> Optional[Result]:
        """Get a result by sourcedId."""
        return (
            self.db.query(Result)
            .filter(Result.sourced_id == sourced_id, Result.status == StatusEnum.active)
            .first()
        )

    def get_all(
        self,
        limit: int = 100,
        offset: int = 0,
        filter_expr: Optional[str] = None,
        sort_expr: Optional[str] = None,
        fields: Optional[str] = None,
    ) -> Tuple[List[Result], int]:
        """
        Get all results with pagination, filtering, and sorting.

        Args:
            limit: Maximum number of results to return
            offset: Number of results to skip
            filter_expr: OneRoster filter expression
            sort_expr: OneRoster sort expression
            fields: Comma-separated list of fields to return

        Returns:
            Tuple of (list of results, total count)
        """
        query = self.db.query(Result).filter(Result.status == StatusEnum.active)

        # Apply filters
        if filter_expr:
            conditions = parse_filter(filter_expr, Result)
            for condition in conditions:
                query = query.filter(condition)

        # Get total count before pagination
        total = query.count()

        # Apply sorting
        if sort_expr:
            order_by_clauses = parse_sort(sort_expr, Result)
            for clause in order_by_clauses:
                query = query.order_by(clause)
        else:
            # Default sorting by sourcedId
            query = query.order_by(Result.sourced_id)

        # Apply pagination
        results = query.limit(limit).offset(offset).all()

        return results, total

    def create(self, data: Dict[str, Any]) -> Result:
        """Create a new result."""
        # Convert camelCase to snake_case for database
        result_data = {
            "sourced_id": data.get("sourcedId"),
            "status": StatusEnum.active,
            "line_item_sourced_id": data.get("lineItemSourcedId"),
            "student_sourced_id": data.get("studentSourcedId"),
            "score_status": data.get("scoreStatus"),
            "score": data.get("score"),
            "score_date": data.get("scoreDate"),
            "comment": data.get("comment"),
            "metadata_": data.get("metadata"),
        }

        result = Result(**result_data)
        self.db.add(result)
        self.db.commit()
        self.db.refresh(result)
        return result

    def update(self, sourced_id: str, data: Dict[str, Any]) -> Optional[Result]:
        """Update an existing result."""
        result = self.get_by_id(sourced_id)
        if not result:
            return None

        # Update allowed fields
        if "scoreStatus" in data:
            result.score_status = data["scoreStatus"]
        if "score" in data:
            result.score = data["score"]
        if "scoreDate" in data:
            result.score_date = data["scoreDate"]
        if "comment" in data:
            result.comment = data["comment"]
        if "metadata" in data:
            result.metadata_ = data["metadata"]

        self.db.commit()
        self.db.refresh(result)
        return result

    def delete(self, sourced_id: str) -> bool:
        """
        Soft delete a result.
        Sets status to 'tobedeleted' instead of physically deleting.
        """
        result = self.get_by_id(sourced_id)
        if not result:
            return False

        result.status = StatusEnum.tobedeleted
        self.db.commit()
        return True
