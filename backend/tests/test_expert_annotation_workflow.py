from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from backend.repositories.annotation_repository import AnnotationRepository


def test_double_blind_grading_and_isolation(client: TestClient, db_session: Session):
    repo = AnnotationRepository(db_session)
    repo.create_or_get_for_image("CATTLE-BLIND-01", "dataset/real/processed/images/CATTLE-BLIND-01.jpg")

    # 1. Grader 1 submits grade
    g1_payload = {
        "grader_id": "EXP-CATTLE-01",
        "grade": "B",
        "attributes": {
            "body_condition": 3.0,
            "coat_quality": "Smooth",
            "eye_condition": "Clear",
            "wound_presence": "None",
            "mobility": "Normal",
            "appetite": "Good"
        },
        "notes": "Good muscle structure and active temperament."
    }
    res1 = client.post("/api/v1/annotations/CATTLE-BLIND-01/grade", json=g1_payload)
    assert res1.status_code == 200
    d1 = res1.json()["data"]
    assert d1["annotation_status"] == "PARTIALLY_ANNOTATED"
    assert d1["expert_grade_1"] == "B"

    # 2. Verify Double-Blind Isolation: Grader 2 querying the sample CANNOT see Grader 1's grade
    res_blind = client.get("/api/v1/annotations/CATTLE-BLIND-01?viewer_id=EXP-CATTLE-02&is_senior=false")
    assert res_blind.status_code == 200
    blind_data = res_blind.json()["data"]
    assert blind_data["expert_grade_1"] is None
    assert blind_data["expert_grade_1_notes"] is None

    # 3. Grader 2 submits identical grade -> Automatic Consensus
    g2_payload = {
        "grader_id": "EXP-CATTLE-02",
        "grade": "B",
        "attributes": {"body_condition": 3.0},
        "notes": "Agree with healthy condition."
    }
    res2 = client.post("/api/v1/annotations/CATTLE-BLIND-01/grade", json=g2_payload)
    assert res2.status_code == 200
    d2 = res2.json()["data"]
    assert d2["annotation_status"] == "CONSENSUS_REACHED"
    assert d2["final_consensus_grade"] == "B"


def test_disagreement_preservation_and_senior_adjudication(client: TestClient, db_session: Session):
    repo = AnnotationRepository(db_session)
    repo.create_or_get_for_image("CATTLE-DISAGREE-01", "dataset/real/processed/images/sample.jpg")

    # Grader 1 assigns A
    client.post("/api/v1/annotations/CATTLE-DISAGREE-01/grade", json={
        "grader_id": "EXP-01",
        "grade": "A",
        "attributes": {"body_condition": 3.2}
    })

    # Grader 2 assigns C (Disagreement!)
    res_disagree = client.post("/api/v1/annotations/CATTLE-DISAGREE-01/grade", json={
        "grader_id": "EXP-02",
        "grade": "C",
        "attributes": {"body_condition": 2.2, "coat_quality": "Rough"}
    })
    data_disagree = res_disagree.json()["data"]
    assert data_disagree["annotation_status"] == "DISAGREEMENT"
    assert data_disagree["final_consensus_grade"] is None  # Never imputed or averaged

    # Senior reviewer inspects and adjudicates
    adj_payload = {
        "reviewer_id": "SR-VET-01",
        "final_grade": "B",
        "rationale": "Slight rough coat due to winter shed; body condition is moderate 2.5 confirming Grade B."
    }
    res_adj = client.post("/api/v1/annotations/CATTLE-DISAGREE-01/consensus", json=adj_payload)
    assert res_adj.status_code == 200
    data_adj = res_adj.json()["data"]
    assert data_adj["annotation_status"] == "CONSENSUS_REACHED"
    assert data_adj["final_consensus_grade"] == "B"
    assert data_adj["consensus_reviewer_id"] == "SR-VET-01"


def test_quality_flagging_rejects_sample(client: TestClient, db_session: Session):
    repo = AnnotationRepository(db_session)
    repo.create_or_get_for_image("CATTLE-POOR-IMG", "dataset/real/processed/images/poor.jpg")

    flag_payload = {
        "grader_id": "EXP-01",
        "reason": "Severe lens blur and sun glare completely obscuring thoracic ribs."
    }
    res = client.post("/api/v1/annotations/CATTLE-POOR-IMG/flag-quality", json=flag_payload)
    assert res.status_code == 200
    data = res.json()["data"]
    assert data["annotation_status"] == "REJECTED"
    assert data["quality_flagged"] is True
    assert "sun glare" in data["quality_issue_reason"]


def test_annotation_stats_summary(client: TestClient, db_session: Session):
    res = client.get("/api/v1/annotations/stats/summary")
    assert res.status_code == 200
    stats = res.json()["data"]
    assert "total_samples" in stats
    assert "consensus_reached_samples" in stats
    assert "disagreement_samples" in stats
    assert "exact_agreement_percentage" in stats
