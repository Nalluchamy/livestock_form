import pytest
import uuid
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from backend.core.settings import settings
from backend.models.user import User
from backend.repositories.user_repository import UserRepository
from backend.repositories.annotation_repository import AnnotationRepository
from backend.repositories.review_repository import ReviewRepository
from backend.core.security import create_access_token


def make_auth_header(user: User) -> dict:
    token = create_access_token({"sub": str(user.id), "username": user.username, "role": user.role})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def auth_users(db_session: Session):
    repo = UserRepository(db_session)
    farmer = repo.create_user("farmer_test", "farmer@test.com", "Password2026!", "FARMER")
    grader = repo.create_user("grader_test", "grader@test.com", "Password2026!", "EXPERT_GRADER")
    senior = repo.create_user("senior_test", "senior@test.com", "Password2026!", "SENIOR_REVIEWER")
    admin = repo.create_user("admin_test", "admin@test.com", "Password2026!", "ADMIN")
    return {
        "farmer": farmer,
        "grader": grader,
        "senior": senior,
        "admin": admin
    }


def test_anonymous_access_rejected_when_not_demo(client: TestClient, db_session: Session):
    settings.DEMO_MODE = False
    res_admin = client.get("/api/v1/admin/users")
    assert res_admin.status_code == 401

    res_grade = client.post("/api/v1/annotations/TEST-01/grade", json={"grade": "B"})
    assert res_grade.status_code == 401

    res_resolve = client.post(f"/api/v1/reviews/{uuid.uuid4()}/resolve", json={
        "reviewer_action": "UPHELD_HUMAN",
        "reviewer_final_decision": "B",
        "reviewer_rationale": "Valid diagnosis"
    })
    assert res_resolve.status_code == 401


def test_farmer_cannot_access_admin_endpoints(client: TestClient, auth_users):
    headers = make_auth_header(auth_users["farmer"])
    res = client.get("/api/v1/admin/users", headers=headers)
    assert res.status_code == 403
    assert "not authorized" in res.json()["detail"].lower()


def test_farmer_cannot_submit_expert_grade(client: TestClient, auth_users, db_session: Session):
    repo = AnnotationRepository(db_session)
    repo.create_or_get_for_image("CATTLE-RBAC-01", "path/to/img.jpg")

    headers = make_auth_header(auth_users["farmer"])
    res = client.post(
        "/api/v1/annotations/CATTLE-RBAC-01/grade",
        json={"grade": "A", "attributes": {"body_condition": 3.0}},
        headers=headers
    )
    assert res.status_code == 403


def test_farmer_cannot_adjudicate_consensus(client: TestClient, auth_users, db_session: Session):
    repo = AnnotationRepository(db_session)
    repo.create_or_get_for_image("CATTLE-RBAC-02", "path/to/img.jpg")

    headers = make_auth_header(auth_users["farmer"])
    res = client.post(
        "/api/v1/annotations/CATTLE-RBAC-02/consensus",
        json={"final_grade": "A", "rationale": "Farmer opinion should not count as senior consensus"},
        headers=headers
    )
    assert res.status_code == 403


def test_expert_grader_cannot_adjudicate_consensus(client: TestClient, auth_users, db_session: Session):
    repo = AnnotationRepository(db_session)
    repo.create_or_get_for_image("CATTLE-RBAC-03", "path/to/img.jpg")

    headers = make_auth_header(auth_users["grader"])
    res = client.post(
        "/api/v1/annotations/CATTLE-RBAC-03/consensus",
        json={"final_grade": "B", "rationale": "Grader attempting unauthorized consensus"},
        headers=headers
    )
    assert res.status_code == 403


def test_expert_grader_cannot_resolve_disagreement_reviews(client: TestClient, auth_users, db_session: Session):
    rev_repo = ReviewRepository(db_session)
    review = rev_repo.create_review("B", "C", reviewer_rationale="Borderline score")

    headers = make_auth_header(auth_users["grader"])
    res = client.post(
        f"/api/v1/reviews/{review.id}/resolve",
        json={
            "reviewer_action": "UPHELD_HUMAN",
            "reviewer_final_decision": "B",
            "reviewer_rationale": "Grader resolution attempt"
        },
        headers=headers
    )
    assert res.status_code == 403


def test_senior_reviewer_can_adjudicate_consensus_and_resolve_reviews(client: TestClient, auth_users, db_session: Session):
    # 1. Adjudicate consensus
    repo = AnnotationRepository(db_session)
    repo.create_or_get_for_image("CATTLE-RBAC-04", "path/to/img.jpg")

    senior_headers = make_auth_header(auth_users["senior"])
    res_cons = client.post(
        "/api/v1/annotations/CATTLE-RBAC-04/consensus",
        json={"final_grade": "A", "rationale": "Authoritative senior veterinary resolution"},
        headers=senior_headers
    )
    assert res_cons.status_code == 200
    assert res_cons.json()["data"]["final_consensus_grade"] == "A"

    # 2. Resolve review
    rev_repo = ReviewRepository(db_session)
    review = rev_repo.create_review("A", "C", reviewer_rationale="Significant disagreement")

    res_rev = client.post(
        f"/api/v1/reviews/{review.id}/resolve",
        json={
            "reviewer_action": "UPHELD_HUMAN",
            "reviewer_final_decision": "A",
            "reviewer_rationale": "Muscle definition and stance confirm Grade A."
        },
        headers=senior_headers
    )
    assert res_rev.status_code == 200
    assert res_rev.json()["data"]["status"] == "RESOLVED"


def test_admin_has_superuser_privileges(client: TestClient, auth_users):
    admin_headers = make_auth_header(auth_users["admin"])

    # List users
    res_users = client.get("/api/v1/admin/users", headers=admin_headers)
    assert res_users.status_code == 200
    users = res_users.json()
    assert len(users) >= 4

    # Update role
    target_farmer = auth_users["farmer"]
    patch_role_res = client.patch(
        f"/api/v1/admin/users/{target_farmer.id}/role",
        json={"role": "EXPERT_GRADER"},
        headers=admin_headers
    )
    assert patch_role_res.status_code == 200
    assert patch_role_res.json()["role"] == "EXPERT_GRADER"

    # Query audit logs
    logs_res = client.get("/api/v1/admin/audit-logs", headers=admin_headers)
    assert logs_res.status_code == 200
    assert logs_res.json()["total"] >= 1


def test_expert_grader_cannot_impersonate_another_grader(client: TestClient, auth_users, db_session: Session):
    repo = AnnotationRepository(db_session)
    repo.create_or_get_for_image("CATTLE-RBAC-05", "path/to/img.jpg")

    headers = make_auth_header(auth_users["grader"])
    # Attempting to grade under another grader ID
    res = client.post(
        "/api/v1/annotations/CATTLE-RBAC-05/grade",
        json={
            "grader_id": "impersonated_grader_alice",
            "grade": "C"
        },
        headers=headers
    )
    assert res.status_code == 403
    assert "different user's identity" in res.json()["detail"]


def test_single_grader_cannot_fill_both_grader1_and_grader2_slots(client: TestClient, auth_users, db_session: Session):
    repo = AnnotationRepository(db_session)
    repo.create_or_get_for_image("CATTLE-RBAC-06", "path/to/img.jpg")

    headers = make_auth_header(auth_users["grader"])

    # Grader submits first grade (slot 1)
    res1 = client.post(
        "/api/v1/annotations/CATTLE-RBAC-06/grade",
        json={"grade": "B"},
        headers=headers
    )
    assert res1.status_code == 200
    assert res1.json()["data"]["annotation_status"] == "PARTIALLY_ANNOTATED"

    # Same grader submits again: updates slot 1, does NOT fill slot 2
    res2 = client.post(
        "/api/v1/annotations/CATTLE-RBAC-06/grade",
        json={"grade": "A"},
        headers=headers
    )
    assert res2.status_code == 200
    # Crucially: status remains PARTIALLY_ANNOTATED (cannot self-grade consensus)
    assert res2.json()["data"]["annotation_status"] == "PARTIALLY_ANNOTATED"
    assert res2.json()["data"]["expert_grade_1"] == "A"
    assert res2.json()["data"]["expert_grade_2"] is None


def test_farmer_cannot_list_expert_annotations(client: TestClient, auth_users):
    farmer_headers = make_auth_header(auth_users["farmer"])
    res = client.get("/api/v1/annotations", headers=farmer_headers)
    assert res.status_code == 403
    assert "not authorized" in res.json()["detail"].lower()

    # Grader, Senior, Admin CAN list annotations
    for role_key in ["grader", "senior", "admin"]:
        role_headers = make_auth_header(auth_users[role_key])
        ok_res = client.get("/api/v1/annotations", headers=role_headers)
        assert ok_res.status_code == 200


def test_farmer_cannot_access_disagreement_reviews_queue(client: TestClient, auth_users):
    farmer_headers = make_auth_header(auth_users["farmer"])
    res = client.get("/api/v1/reviews", headers=farmer_headers)
    assert res.status_code == 403
    assert "not authorized" in res.json()["detail"].lower()

    # Grader, Senior, Admin CAN access reviews queue
    for role_key in ["grader", "senior", "admin"]:
        role_headers = make_auth_header(auth_users[role_key])
        ok_res = client.get("/api/v1/reviews", headers=role_headers)
        assert ok_res.status_code == 200


def test_farmer_can_submit_grade_and_sync(client: TestClient, auth_users):
    farmer_headers = make_auth_header(auth_users["farmer"])

    # Grade submission
    grade_res = client.post(
        "/api/v1/grade",
        json={
            "attributes": {
                "body_condition": 3.0,
                "coat_quality": "Smooth",
                "eye_condition": "Clear",
                "wound_presence": "None",
                "mobility": "Normal",
                "appetite": "Good"
            }
        },
        headers=farmer_headers
    )
    assert grade_res.status_code == 200
    assert grade_res.json()["data"]["grade"] == "A"

    # Grading history
    hist_res = client.get("/api/v1/grading-events", headers=farmer_headers)
    assert hist_res.status_code == 200

    # Sync
    sync_res = client.post(
        "/api/v1/sync",
        json={
            "items": [
                {
                    "id": "item_farmer_01",
                    "attributes": {
                        "body_condition": 3.0,
                        "coat_quality": "Smooth",
                        "eye_condition": "Clear",
                        "wound_presence": "None",
                        "mobility": "Normal",
                        "appetite": "Good"
                    }
                }
            ]
        },
        headers=farmer_headers
    )
    assert sync_res.status_code == 200
    assert sync_res.json()["data"]["processed_count"] == 1


def test_anonymous_access_to_sync_and_grading_rejected_when_not_demo(client: TestClient):
    settings.ENVIRONMENT = "production"
    settings.DEMO_MODE = False
    try:
        sync_res = client.post("/api/v1/sync", json={"items": []})
        assert sync_res.status_code == 401

        grade_res = client.post("/api/v1/grade", json={"attributes": {}})
        assert grade_res.status_code == 401

        hist_res = client.get("/api/v1/grading-events")
        assert hist_res.status_code == 401
    finally:
        settings.ENVIRONMENT = "development"
