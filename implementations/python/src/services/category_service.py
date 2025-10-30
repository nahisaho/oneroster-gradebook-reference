"""
Category Service
Business logic for categories operations.
"""

from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy.orm import Session

from src.models.models import Category, StatusEnum
from src.utils.query_parser import parse_filter, parse_sort


class CategoryService:
    """Service class for Category operations."""

    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, sourced_id: str) -> Optional[Category]:
        """Get a category by sourcedId."""
        return (
            self.db.query(Category)
            .filter(Category.sourced_id == sourced_id, Category.status == StatusEnum.active)
            .first()
        )

    def get_all(
        self,
        limit: int = 100,
        offset: int = 0,
        filter_expr: Optional[str] = None,
        sort_expr: Optional[str] = None,
        fields: Optional[str] = None,
    ) -> Tuple[List[Category], int]:
        """
        Get all categories with pagination, filtering, and sorting.

        Args:
            limit: Maximum number of results to return
            offset: Number of results to skip
            filter_expr: OneRoster filter expression
            sort_expr: OneRoster sort expression
            fields: Comma-separated list of fields to return

        Returns:
            Tuple of (list of categories, total count)
        """
        query = self.db.query(Category).filter(Category.status == StatusEnum.active)

        # Apply filters
        if filter_expr:
            conditions = parse_filter(filter_expr, Category)
            for condition in conditions:
                query = query.filter(condition)

        # Get total count before pagination
        total = query.count()

        # Apply sorting
        if sort_expr:
            order_by_clauses = parse_sort(sort_expr, Category)
            for clause in order_by_clauses:
                query = query.order_by(clause)
        else:
            # Default sorting by sourcedId
            query = query.order_by(Category.sourced_id)

        # Apply pagination
        categories = query.limit(limit).offset(offset).all()

        return categories, total

    def create(self, data: Dict[str, Any]) -> Category:
        """Create a new category."""
        # Convert camelCase to snake_case for database
        category_data = {
            "sourced_id": data.get("sourcedId"),
            "status": StatusEnum.active,
            "title": data.get("title"),
            "weight": data.get("weight"),
            "metadata_": data.get("metadata"),
        }

        category = Category(**category_data)
        self.db.add(category)
        self.db.commit()
        self.db.refresh(category)
        return category

    def update(self, sourced_id: str, data: Dict[str, Any]) -> Optional[Category]:
        """Update an existing category."""
        category = self.get_by_id(sourced_id)
        if not category:
            return None

        # Update allowed fields
        if "title" in data:
            category.title = data["title"]
        if "weight" in data:
            category.weight = data["weight"]
        if "metadata" in data:
            category.metadata_ = data["metadata"]

        self.db.commit()
        self.db.refresh(category)
        return category

    def delete(self, sourced_id: str) -> bool:
        """
        Soft delete a category.
        Sets status to 'tobedeleted' instead of physically deleting.
        """
        category = self.get_by_id(sourced_id)
        if not category:
            return False

        category.status = StatusEnum.tobedeleted
        self.db.commit()
        return True
