"""
Line Items API Router
Implements OneRoster Gradebook Line Items endpoints.
"""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from src.config.database import get_db
from src.middleware.auth import require_scope
from src.schemas.schemas import (
    CollectionResponse,
    LineItemCreate,
    LineItemResponse,
    LineItemUpdate,
)
from src.services.line_item_service import LineItemService

router = APIRouter()

# OneRoster scopes
SCOPE_READONLY = "https://purl.imsglobal.org/spec/or/v1p2/scope/roster-core.readonly"
SCOPE_CREATEPUT = "https://purl.imsglobal.org/spec/or/v1p2/scope/results.createput"
SCOPE_DELETE = "https://purl.imsglobal.org/spec/or/v1p2/scope/results.delete"


@router.get("/{sourced_id}", response_model=LineItemResponse)
async def get_line_item(
    sourced_id: str,
    db: Session = Depends(get_db),
    client: dict = Depends(require_scope(SCOPE_READONLY)),
):
    """Get a single line item by sourcedId."""
    service = LineItemService(db)
    line_item = service.get_by_id(sourced_id)

    if not line_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"LineItem with sourcedId '{sourced_id}' not found",
        )

    return line_item.to_oneroster_dict()


@router.get("", response_model=CollectionResponse)
async def get_line_items(
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    filter_param: Optional[str] = Query(None, alias="filter"),
    sort: Optional[str] = Query(None),
    fields: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    client: dict = Depends(require_scope(SCOPE_READONLY)),
):
    """Get collection of line items with pagination and filtering."""
    service = LineItemService(db)

    line_items, total = service.get_all(
        limit=limit,
        offset=offset,
        filter_expr=filter_param,
        sort_expr=sort,
        fields=fields,
    )

    return {
        "data": [item.to_oneroster_dict() for item in line_items],
        "total": total,
        "limit": limit,
        "offset": offset,
    }


@router.post("", response_model=LineItemResponse, status_code=status.HTTP_201_CREATED)
async def create_line_item(
    line_item_create: LineItemCreate,
    db: Session = Depends(get_db),
    client: dict = Depends(require_scope(SCOPE_CREATEPUT)),
):
    """Create a new line item."""
    service = LineItemService(db)
    line_item = service.create(line_item_create.model_dump(by_alias=True))
    return line_item.to_oneroster_dict()


@router.put("/{sourced_id}", response_model=LineItemResponse)
async def update_line_item(
    sourced_id: str,
    line_item_update: LineItemUpdate,
    db: Session = Depends(get_db),
    client: dict = Depends(require_scope(SCOPE_CREATEPUT)),
):
    """Update an existing line item."""
    service = LineItemService(db)
    line_item = service.update(sourced_id, line_item_update.model_dump(exclude_unset=True))

    if not line_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"LineItem with sourcedId '{sourced_id}' not found",
        )

    return line_item.to_oneroster_dict()


@router.delete("/{sourced_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_line_item(
    sourced_id: str,
    db: Session = Depends(get_db),
    client: dict = Depends(require_scope(SCOPE_DELETE)),
):
    """Delete (soft delete) a line item."""
    service = LineItemService(db)
    success = service.delete(sourced_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"LineItem with sourcedId '{sourced_id}' not found",
        )

    return None
