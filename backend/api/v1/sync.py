from typing import List, Dict, Any
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel

from backend.database.session import get_db
from backend.schemas.responses import APIResponse, success_response
from backend.services.api_grading_service import APIGradingService

router = APIRouter(prefix="/sync", tags=["Offline Sync"])

class SyncBatchItem(BaseModel):
    id: str
    attributes: Dict[str, Any]
    human_grade: str | None = None

class SyncBatchRequest(BaseModel):
    items: List[SyncBatchItem]

@router.post("", response_model=APIResponse[dict])
def sync_offline_batch(payload: SyncBatchRequest, db: Session = Depends(get_db)):
    """
    Batch endpoint processing offline queued grading events.
    """
    service = APIGradingService(db)
    processed = 0
    errors = []

    for item in payload.items:
        try:
            service.execute_grading(
                attributes=item.attributes,
                human_grade=item.human_grade
            )
            processed += 1
        except Exception as e:
            errors.append({"id": item.id, "error": str(e)})

    return success_response(
        message=f"Batch sync complete. Processed {processed} item(s).",
        data={
            "processed_count": processed,
            "failed_count": len(errors),
            "errors": errors
        }
    )
