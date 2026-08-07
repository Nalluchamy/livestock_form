import uuid
import json
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session

from backend.core.settings import settings
from backend.repositories.grading_repository import GradingRepository
from backend.services import grading_service
from backend.services.validators import ValidationError
from backend.models.fact_grading_event import FactGradingEvent
from backend.services.exceptions import APIException


class APIGradingService:
    """
    Bridge service connecting the REST API to the pure Grading Service and Database Repositories.
    Handles DEMO_MODE logic, entity creation, and transactional boundaries.
    """
    def __init__(self, db: Session):
        self.db = db
        self.repo = GradingRepository(db)

    def execute_grading(
        self, 
        attributes: Dict[str, Any], 
        sample_id: Optional[uuid.UUID] = None,
        grader_id: Optional[uuid.UUID] = None,
        image_id: Optional[uuid.UUID] = None,
        human_grade: Optional[str] = None
    ) -> dict:
        
        generated_demo = False
        
        # 1. Handle missing IDs vs DEMO_MODE
        if not sample_id or not grader_id:
            if settings.DEMO_MODE:
                demo_sample = self.repo.create_demo_sample()
                demo_grader = self.repo.create_demo_grader()
                sample_id = demo_sample.id
                grader_id = demo_grader.id
                generated_demo = True
                
                if not image_id:
                    # For demo mode, pretend we had an image if missing to keep 100% confidence realistic
                    image_id = uuid.uuid4()
            else:
                raise APIException(
                    message="Missing required sample_id or grader_id in production mode.",
                    status_code=400
                )

        has_image = bool(image_id)

        # 2. Call the pure Rule Engine (Business Logic)
        try:
            grading_result = grading_service.generate_grade(attributes, has_image=has_image)
        except (ValueError, ValidationError) as e:
            raise APIException(message=str(e), status_code=400)

        # 3. Detect Disagreement
        disagreement_reason = None
        review_status = "completed"
        if human_grade:
            disagreement = grading_service.detect_disagreement(human_grade, grading_result)
            if disagreement:
                disagreement_reason = disagreement.reason
                review_status = "pending"

        # Inherit review_required from low confidence
        if grading_result.review_required:
            review_status = "pending"

        # 4. Save to Database
        fact_event = FactGradingEvent(
            sample_id=sample_id,
            grader_id=grader_id,
            image_id=image_id,
            human_grade=human_grade,
            ai_grade=grading_result.grade,
            confidence_score=grading_result.confidence,
            explanation=json.dumps(grading_result.reasons),
            review_status=review_status,
            is_synced=True
        )

        saved_event = self.repo.save_grading_event(fact_event)

        # 5. Build standard response
        response_data = {
            "grading_event_id": str(saved_event.id),
            "grade": grading_result.grade,
            "confidence": grading_result.confidence,
            "reasons": grading_result.reasons,
            "missing_attributes": grading_result.missing_attributes,
            "review_required": grading_result.review_required or (review_status == "pending"),
            "sample_id": str(sample_id),
            "grader_id": str(grader_id),
            "generated_demo_entities": generated_demo
        }
        
        return response_data
