"""
Line Item Service
Business logic for line items operations.
"""

from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy.orm import Session

from src.models.models import LineItem, StatusEnum
from src.utils.query_parser import parse_filter, parse_sort


class LineItemService:
    """Service class for LineItem operations."""

    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, sourced_id: str) -> Optional[LineItem]:
        """Get a line item by sourcedId."""
        return (
            self.db.query(LineItem)
            .filter(LineItem.sourced_id == sourced_id, LineItem.status == StatusEnum.active)
            .first()
        )

    def get_all(
        self,
        limit: int = 100,
        offset: int = 0,
        filter_expr: Optional[str] = None,
        sort_expr: Optional[str] = None,
        fields: Optional[str] = None,
    ) -> Tuple[List[LineItem], int]:
        """
        Get all line items with pagination, filtering, and sorting.

        Args:
            limit: Maximum number of results to return
            offset: Number of results to skip
            filter_expr: OneRoster filter expression
            sort_expr: OneRoster sort expression
            fields: Comma-separated list of fields to return

        Returns:
            Tuple of (list of line items, total count)
        """
        query = self.db.query(LineItem).filter(LineItem.status == StatusEnum.active)

        # Apply filters
        if filter_expr:
            conditions = parse_filter(filter_expr, LineItem)
            for condition in conditions:
                query = query.filter(condition)

        # Get total count before pagination
        total = query.count()

        # Apply sorting
        if sort_expr:
            order_by_clauses = parse_sort(sort_expr, LineItem)
            for clause in order_by_clauses:
                query = query.order_by(clause)
        else:
            # Default sorting by sourcedId
            query = query.order_by(LineItem.sourced_id)

        # Apply pagination
        line_items = query.limit(limit).offset(offset).all()

        return line_items, total

    def create(self, data: Dict[str, Any]) -> LineItem:
        """Create a new line item."""
        # Convert camelCase to snake_case for database
        line_item_data = {
            "sourced_id": data.get("sourcedId"),
            "status": StatusEnum.active,
            "title": data.get("title"),
            "description": data.get("description"),
            "assign_date": data.get("assignDate"),
            "due_date": data.get("dueDate"),
            "class_sourced_id": data.get("classSourcedId"),
            "category_sourced_id": data.get("categorySourcedId"),
            "result_value_min": data.get("resultValueMin", 0),
            "result_value_max": data.get("resultValueMax", 100),
            "metadata_": data.get("metadata"),
        }

        line_item = LineItem(**line_item_data)
        self.db.add(line_item)
        self.db.commit()
        self.db.refresh(line_item)
        return line_item

    def update(self, sourced_id: str, data: Dict[str, Any]) -> Optional[LineItem]:
        """Update an existing line item."""
        line_item = self.get_by_id(sourced_id)
        if not line_item:
            return None

        # Update allowed fields
        if "title" in data:
            line_item.title = data["title"]
        if "description" in data:
            line_item.description = data["description"]
        if "assignDate" in data:
            line_item.assign_date = data["assignDate"]
        if "dueDate" in data:
            line_item.due_date = data["dueDate"]
        if "categorySourcedId" in data:
            line_item.category_sourced_id = data["categorySourcedId"]
        if "resultValueMin" in data:
            line_item.result_value_min = data["resultValueMin"]
        if "resultValueMax" in data:
            line_item.result_value_max = data["resultValueMax"]
        if "metadata" in data:
            line_item.metadata_ = data["metadata"]

        self.db.commit()
        self.db.refresh(line_item)
        return line_item

    def delete(self, sourced_id: str) -> bool:
        """
        Soft delete a line item.
        Sets status to 'tobedeleted' instead of physically deleting.
        """
        line_item = self.get_by_id(sourced_id)
        if not line_item:
            return False

        line_item.status = StatusEnum.tobedeleted
        self.db.commit()
        return True
