import uuid
import pytest
from backend.repositories.review_repository import ReviewRepository
from backend.services.exceptions import APIException


def test_create_persistent_review(db_session):
    repo = ReviewRepository(db_session)
    review = repo.create_review(
        original_human_grade="B",
        original_system_grade="C",
        reviewer_rationale="Borderline BCS observed."
    )
    assert review.id is not None
    assert review.original_human_grade == "B"
    assert review.original_system_grade == "C"
    assert review.status == "PENDING"
    assert review.resolved_at is None


def test_immutability_of_original_grades_on_resolve(db_session):
    repo = ReviewRepository(db_session)
    review = repo.create_review(
        original_human_grade="B",
        original_system_grade="C",
    )
    
    # Resolve with authoritative decision
    resolved = repo.resolve_review(
        review_id=review.id,
        reviewer_id="SR-VET-001",
        reviewer_action="UPHELD_HUMAN",
        reviewer_final_decision="B",
        reviewer_rationale="Gait examination confirms animal condition is stable Grade B."
    )

    assert resolved.status == "RESOLVED"
    assert resolved.reviewer_final_decision == "B"
    assert resolved.resolved_at is not None
    
    # Original grades MUST remain completely unchanged
    assert resolved.original_human_grade == "B"
    assert resolved.original_system_grade == "C"


def test_safe_status_transitions(db_session):
    repo = ReviewRepository(db_session)
    review = repo.create_review(original_human_grade="A", original_system_grade="B")
    
    # PENDING -> IN_REVIEW (allowed)
    r1 = repo.update_status(review.id, "IN_REVIEW", reviewer_id="SR-01")
    assert r1.status == "IN_REVIEW"

    # IN_REVIEW -> ESCALATED (allowed)
    r2 = repo.update_status(review.id, "ESCALATED")
    assert r2.status == "ESCALATED"

    # Resolve from ESCALATED
    r3 = repo.resolve_review(
        review_id=review.id,
        reviewer_id="SENIOR-AUDITOR",
        reviewer_action="EXPERT_OVERRIDE",
        reviewer_final_decision="A",
        reviewer_rationale="Consensus panel determination."
    )
    assert r3.status == "RESOLVED"

    # Cannot transition out of terminal RESOLVED status
    with pytest.raises(APIException) as excinfo:
        repo.update_status(review.id, "PENDING")
    assert "Cannot transition" in str(excinfo.value.message)


def test_review_stats(db_session):
    repo = ReviewRepository(db_session)
    r1 = repo.create_review(original_human_grade="A", original_system_grade="B")
    r2 = repo.create_review(original_human_grade="C", original_system_grade="D")
    
    repo.resolve_review(
        review_id=r1.id,
        reviewer_id="SR-01",
        reviewer_action="UPHELD_HUMAN",
        reviewer_final_decision="A",
        reviewer_rationale="Upheld"
    )

    stats = repo.get_review_stats()
    assert stats["total_reviews"] == 2
    assert stats["resolved_count"] == 1
    assert stats["pending_count"] == 1
    assert stats["upheld_human_count"] == 1
