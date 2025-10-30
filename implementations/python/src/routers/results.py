"""
Results API Router
Implements OneRoster Gradebook Results endpoints.
"""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from src.config.database import get_db
from src.middleware.auth import require_scope
from src.schemas.schemas import CollectionResponse, ResultCreate, ResultResponse, ResultUpdate
from src.services.result_service import ResultService

router = APIRouter()

# OneRoster scopes
SCOPE_READONLY = "https://purl.imsglobal.org/spec/or/v1p2/scope/results.readonly"
SCOPE_CREATEPUT = "https://purl.imsglobal.org/spec/or/v1p2/scope/results.createput"
SCOPE_DELETE = "https://purl.imsglobal.org/spec/or/v1p2/scope/results.delete"


@router.get("/{sourced_id}", response_model=ResultResponse)
async def get_result(
    sourced_id: str,
    db: Session = Depends(get_db),
    client: dict = Depends(require_scope(SCOPE_READONLY)),
):
    """Get a single result by sourcedId."""
    service = ResultService(db)
    result = service.get_by_id(sourced_id)

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Result with sourcedId '{sourced_id}' not found",
        )

    return result.to_oneroster_dict()


@router.get("", response_model=CollectionResponse)
async def get_results(
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    filter_param: Optional[str] = Query(None, alias="filter"),
    sort: Optional[str] = Query(None),
    fields: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    client: dict = Depends(require_scope(SCOPE_READONLY)),
):
    """Get collection of results with pagination and filtering."""
    service = ResultService(db)

    results, total = service.get_all(
        limit=limit,
        offset=offset,
        filter_expr=filter_param,
        sort_expr=sort,
        fields=fields,
    )

    return {
        "data": [res.to_oneroster_dict() for res in results],
        "total": total,
        "limit": limit,
        "offset": offset,
    }


@router.post("", response_model=ResultResponse, status_code=status.HTTP_201_CREATED)
async def create_result(
    result_create: ResultCreate,
    db: Session = Depends(get_db),
    client: dict = Depends(require_scope(SCOPE_CREATEPUT)),
):
    """Create a new result."""
    service = ResultService(db)
    result = service.create(result_create.model_dump(by_alias=True))
    return result.to_oneroster_dict()


@router.put("/{sourced_id}", response_model=ResultResponse)
async def update_result(
    sourced_id: str,
    result_update: ResultUpdate,
    db: Session = Depends(get_db),
    client: dict = Depends(require_scope(SCOPE_CREATEPUT)),
):
    """Update an existing result."""
    service = ResultService(db)
    result = service.update(sourced_id, result_update.model_dump(exclude_unset=True))

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Result with sourcedId '{sourced_id}' not found",
        )

    return result.to_oneroster_dict()


@router.delete("/{sourced_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_result(
    sourced_id: str,
    db: Session = Depends(get_db),
    client: dict = Depends(require_scope(SCOPE_DELETE)),
):
    """Delete (soft delete) a result."""
    service = ResultService(db)
    success = service.delete(sourced_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Result with sourcedId '{sourced_id}' not found",
        )

    return None
