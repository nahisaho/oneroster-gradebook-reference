"""
Categories API Router
Implements OneRoster Gradebook Categories endpoints.
"""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from src.config.database import get_db
from src.middleware.auth import require_scope
from src.schemas.schemas import (
    CategoryCreate,
    CategoryResponse,
    CategoryUpdate,
    CollectionResponse,
)
from src.services.category_service import CategoryService

router = APIRouter()

# OneRoster scopes
SCOPE_READONLY = "https://purl.imsglobal.org/spec/or/v1p2/scope/roster-core.readonly"
SCOPE_CREATEPUT = "https://purl.imsglobal.org/spec/or/v1p2/scope/results.createput"
SCOPE_DELETE = "https://purl.imsglobal.org/spec/or/v1p2/scope/results.delete"


@router.get("/{sourced_id}", response_model=CategoryResponse)
async def get_category(
    sourced_id: str,
    db: Session = Depends(get_db),
    client: dict = Depends(require_scope(SCOPE_READONLY)),
):
    """
    Get a single category by sourcedId.

    **Required Scope**: `roster-core.readonly`
    """
    service = CategoryService(db)
    category = service.get_by_id(sourced_id)

    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category with sourcedId '{sourced_id}' not found",
        )

    return category.to_oneroster_dict()


@router.get("", response_model=CollectionResponse)
async def get_categories(
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of results"),
    offset: int = Query(0, ge=0, description="Number of results to skip"),
    filter_param: Optional[str] = Query(None, alias="filter", description="Filter expression"),
    sort: Optional[str] = Query(None, description="Sort expression"),
    fields: Optional[str] = Query(None, description="Fields to include"),
    db: Session = Depends(get_db),
    client: dict = Depends(require_scope(SCOPE_READONLY)),
):
    """
    Get collection of categories with pagination and filtering.

    **Required Scope**: `roster-core.readonly`

    **Query Parameters**:
    - `limit`: Maximum number of results (1-1000, default: 100)
    - `offset`: Number of results to skip (default: 0)
    - `filter`: Filter expression (e.g., `title='Math'`)
    - `sort`: Sort expression (e.g., `title`, `-dateLastModified`)
    - `fields`: Comma-separated list of fields to include
    """
    service = CategoryService(db)

    categories, total = service.get_all(
        limit=limit,
        offset=offset,
        filter_expr=filter_param,
        sort_expr=sort,
        fields=fields,
    )

    return {
        "data": [cat.to_oneroster_dict() for cat in categories],
        "total": total,
        "limit": limit,
        "offset": offset,
    }


@router.post("", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_category(
    category: CategoryCreate,
    db: Session = Depends(get_db),
    client: dict = Depends(require_scope(SCOPE_CREATEPUT)),
):
    """
    Create a new category.

    **Required Scope**: `results.createput`
    """
    service = CategoryService(db)

    # Check if category already exists
    existing = service.get_by_id(category.sourced_id)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Category with sourcedId '{category.sourced_id}' already exists",
        )

    # Create category
    new_category = service.create(category.model_dump(by_alias=True))
    return new_category.to_oneroster_dict()


@router.put("/{sourced_id}", response_model=CategoryResponse)
async def update_category(
    sourced_id: str,
    category_update: CategoryUpdate,
    db: Session = Depends(get_db),
    client: dict = Depends(require_scope(SCOPE_CREATEPUT)),
):
    """
    Update an existing category.

    **Required Scope**: `roster-core.readonly`
    """
    service = CategoryService(db)
    category = service.update(sourced_id, category_update.model_dump(exclude_unset=True))

    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category with sourcedId '{sourced_id}' not found",
        )

    return category.to_oneroster_dict()


@router.delete("/{sourced_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(
    sourced_id: str,
    db: Session = Depends(get_db),
    client: dict = Depends(require_scope(SCOPE_DELETE)),
):
    """
    Delete (soft delete) a category by setting status to 'tobedeleted'.

    **Required Scope**: `roster-core.readonly`
    """
    service = CategoryService(db)
    success = service.delete(sourced_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category with sourcedId '{sourced_id}' not found",
        )

    return None
