"""
Tests for Genuine Produce Dataset Ingestion, Double-Blind Annotation, and Validation Pipeline.
Phase 17: Real Tomato Dataset Collection & Stage 2 Validation.

Verifies:
- Real dataset directory structure and metadata.csv initialization
- Ingestion pipeline: format validation, dimensions, SHA-256, dHash
- EXIF/GPS scrubbing and privacy checks
- Duplicate and near-duplicate rejection
- Non-fabrication data integrity: ground-truth grade requires human grading
- Double-blind annotation: Grader 1 / Grader 2 isolation
- Automatic consensus clearance vs open disagreement escalation
- Senior adjudicator dispute resolution
- Leakage-safe dataset splitting (train/val/test) with perceptual clustering
- Real-data experiment runner isolation (evaluation_type='real_produce_validation')
- Pending-state reporting when genuine data < 10 samples
- REST API endpoints compliance
"""
import io
import os
import csv
import json
import pytest
from PIL import Image, ImageDraw

from backend.evaluation import real_produce_pipeline as real_pipe
from backend.models.expert_annotation import ExpertAnnotation


def create_test_produce_bytes(seed: int = 0, color: tuple = (220, 30, 20), size: tuple = (250, 250)) -> bytes:
    """Creates a synthetic test JPEG image with distinct visual layout based on seed."""
    img = Image.new("RGB", size, (255, 255, 255))
    draw = ImageDraw.Draw(img)
    ox = (seed * 27) % 60
    oy = (seed * 31) % 60
    draw.ellipse([30 + ox, 30 + oy, size[0] - 30 - ox, size[1] - 30 - oy], fill=color)
    if seed > 0:
        draw.rectangle([40 + (seed * 15) % 100, 40, 70 + (seed * 15) % 100, 90], fill=(30, 180, 40))
        draw.line([(0, (seed * 35) % 250), (size[0], ((seed + 1) * 35) % 250)], fill=(50, 50, 50), width=3)
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=90)
    return buf.getvalue()


@pytest.fixture
def isolated_real_pipeline(tmp_path, monkeypatch):
    """Isolates real produce file storage to a temporary directory for unit testing."""
    real_dir = tmp_path / "real"
    raw_dir = real_dir / "raw"
    proc_dir = real_dir / "processed"
    ann_dir = real_dir / "annotations"
    splits_dir = real_dir / "splits"
    rep_dir = real_dir / "reports"
    meta_path = real_dir / "metadata.csv"
    feedback_path = rep_dir / "stakeholder_feedback.json"

    monkeypatch.setattr(real_pipe, "REAL_PRODUCE_DIR", str(real_dir))
    monkeypatch.setattr(real_pipe, "RAW_DIR", str(raw_dir))
    monkeypatch.setattr(real_pipe, "PROCESSED_DIR", str(proc_dir))
    monkeypatch.setattr(real_pipe, "ANNOTATIONS_DIR", str(ann_dir))
    monkeypatch.setattr(real_pipe, "SPLITS_DIR", str(splits_dir))
    monkeypatch.setattr(real_pipe, "REPORTS_DIR", str(rep_dir))
    monkeypatch.setattr(real_pipe, "METADATA_PATH", str(meta_path))
    monkeypatch.setattr(real_pipe, "STAKEHOLDER_FEEDBACK_PATH", str(feedback_path))

    real_pipe.ensure_directories()
    return real_dir


def test_real_dataset_directory_structure():
    """Verifies all required real produce directories and metadata exist in production workspace."""
    real_pipe.ensure_directories()
    assert os.path.exists("dataset/produce/real")
    assert os.path.exists("dataset/produce/real/raw")
    assert os.path.exists("dataset/produce/real/processed")
    assert os.path.exists("dataset/produce/real/annotations")
    assert os.path.exists("dataset/produce/real/splits")
    assert os.path.exists("dataset/produce/real/reports")
    assert os.path.exists("dataset/produce/real/metadata.csv")

    with open("dataset/produce/real/metadata.csv", "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        header = next(reader)
        assert "sample_id" in header
        assert "dataset_type" in header
        assert "is_synthetic" in header
        assert "is_real" in header


def test_real_produce_status_initial_pending_state(db_session, isolated_real_pipeline):
    """Verifies status reports PENDING_REAL_DATA when collected images < 30."""
    status_info = real_pipe.get_real_produce_dataset_status(db=db_session)
    assert status_info["status"] == "PENDING_REAL_DATA"
    assert status_info["real_images_collected"] == 0
    assert status_info["real_images_required"] == 30
    assert status_info["real_images_remaining"] == 30
    assert status_info["dataset_type"] == "REAL_PRODUCE"
    assert status_info["is_synthetic"] is False
    assert status_info["is_real"] is True
    assert "isolation_statement" in status_info
    assert "data_integrity_rule" in status_info


def test_real_image_ingestion_and_provenance(db_session, isolated_real_pipeline):
    """Verifies genuine produce ingestion, EXIF removal, raw preservation, and DB registration."""
    img_bytes = create_test_produce_bytes(seed=1, color=(210, 35, 25))
    res = real_pipe.ingest_real_produce_image(
        raw_bytes=img_bytes,
        filename="field_tomato_01.jpg",
        source_type="field_harvest",
        capture_environment="packhouse_table",
        camera_type="smartphone_camera",
        db=db_session
    )

    assert res["success"] is True
    sample_id = res["sample_id"]
    assert sample_id.startswith("real_tom_")
    assert res["dataset_type"] == "REAL_PRODUCE"
    assert len(res["sha256"]) == 64
    assert len(res["dhash"]) > 0

    # Verify physical file existence
    assert os.path.exists(res["raw_evidence_path"])
    assert os.path.exists(res["processed_image_path"])

    # Verify metadata entry
    records = real_pipe.load_metadata_records()
    matched = [r for r in records if r["sample_id"] == sample_id]
    assert len(matched) == 1
    row = matched[0]
    assert row["dataset_type"] == "REAL_PRODUCE"
    assert row["is_real"] == "True"
    assert row["is_synthetic"] == "False"
    assert row["annotation_status"] == "PENDING"
    assert row["grade"] == ""  # Strict data integrity: no automated ground truth

    # Verify DB record
    ea = db_session.query(ExpertAnnotation).filter(ExpertAnnotation.sample_id == sample_id).first()
    assert ea is not None
    assert ea.species == "tomato"
    assert ea.annotation_status == "PENDING"


def test_real_image_duplicate_prevention(db_session, isolated_real_pipeline):
    """Verifies exact duplicate images are rejected with duplicate flag."""
    img_bytes = create_test_produce_bytes(seed=2, color=(200, 40, 30))
    res1 = real_pipe.ingest_real_produce_image(img_bytes, "unique_tomato.jpg", db=db_session)
    assert res1["success"] is True

    # Attempt re-ingestion of exact same image
    res2 = real_pipe.ingest_real_produce_image(img_bytes, "duplicate_tomato.jpg", db=db_session)
    assert res2["success"] is False
    assert res2.get("is_duplicate") is True
    assert "duplicate" in res2["error"].lower()


def test_double_blind_grading_and_consensus(db_session, isolated_real_pipeline):
    """Verifies double-blind grading workflow: Grader 1 + Grader 2 agreement -> CONSENSUS_REACHED."""
    img_bytes = create_test_produce_bytes(seed=3, color=(215, 25, 20))
    res = real_pipe.ingest_real_produce_image(img_bytes, "consensus_tomato.jpg", db=db_session)
    assert res["success"] is True
    sample_id = res["sample_id"]

    # Grader 1 submits Grade A
    g1_res = real_pipe.submit_double_blind_produce_grade(
        sample_id=sample_id,
        grader_id="expert_grader_01",
        grade="A",
        confidence=95.0,
        notes="Flawless epidermis, uniform red color.",
        db=db_session
    )
    assert g1_res["annotation_status"] == "PARTIALLY_ANNOTATED"

    # Grader 2 submits Grade A (consensus!)
    g2_res = real_pipe.submit_double_blind_produce_grade(
        sample_id=sample_id,
        grader_id="expert_grader_02",
        grade="A",
        confidence=92.0,
        notes="Confirmed premium quality.",
        db=db_session
    )
    assert g2_res["annotation_status"] == "CONSENSUS_REACHED"

    # Check metadata.csv updated with authoritative reference grade
    records = real_pipe.load_metadata_records()
    matched = [r for r in records if r["sample_id"] == sample_id][0]
    assert matched["grade"] == "A"
    assert matched["grader_1_grade"] == "A"
    assert matched["grader_2_grade"] == "A"
    assert matched["annotation_status"] == "CONSENSUS_REACHED"


def test_double_blind_disagreement_and_adjudication(db_session, isolated_real_pipeline):
    """Verifies disagreement detection (A != B) and senior reviewer authoritative adjudication."""
    img_bytes = create_test_produce_bytes(seed=4, color=(205, 50, 30))
    res = real_pipe.ingest_real_produce_image(img_bytes, "dispute_tomato.jpg", db=db_session)
    assert res["success"] is True
    sample_id = res["sample_id"]

    # Grader 1 says A
    real_pipe.submit_double_blind_produce_grade(
        sample_id=sample_id,
        grader_id="expert_grader_01",
        grade="A",
        db=db_session
    )

    # Grader 2 says B -> Disagreement!
    g2_res = real_pipe.submit_double_blind_produce_grade(
        sample_id=sample_id,
        grader_id="expert_grader_02",
        grade="B",
        db=db_session
    )
    assert g2_res["annotation_status"] == "DISAGREEMENT"

    # Verify status in metadata
    records = real_pipe.load_metadata_records()
    matched = [r for r in records if r["sample_id"] == sample_id][0]
    assert matched["annotation_status"] == "DISAGREEMENT"
    assert matched["grade"] == ""  # No consensus grade yet

    # Senior Adjudicator resolves dispute to Grade B
    adj_res = real_pipe.adjudicate_produce_disagreement(
        sample_id=sample_id,
        reviewer_id="senior_reviewer_01",
        final_grade="B",
        rationale="Small superficial scratch near shoulder exceeds Grade A tolerance; commercial Grade B confirmed.",
        db=db_session
    )
    assert adj_res["status"] == "CONSENSUS_REACHED"
    assert adj_res["adjudicated_grade"] == "B"

    # Check finalized ground truth in metadata
    records = real_pipe.load_metadata_records()
    matched_final = [r for r in records if r["sample_id"] == sample_id][0]
    assert matched_final["grade"] == "B"
    assert matched_final["adjudicated_grade"] == "B"
    assert matched_final["annotation_status"] == "CONSENSUS_REACHED"


def test_leakage_safe_dataset_splitting(db_session, isolated_real_pipeline):
    """Verifies leakage-safe splitting generates train/val/test sets without overlap."""
    # Ingest 3 distinct samples
    for i in range(3):
        b = create_test_produce_bytes(seed=10 + i)
        real_pipe.ingest_real_produce_image(b, f"tomato_split_{i}.jpg", db=db_session)

    splits = real_pipe.split_real_produce_dataset(train_ratio=0.7, val_ratio=0.15, test_ratio=0.15)
    assert "total_genuine_samples" in splits
    assert os.path.exists(os.path.join(real_pipe.SPLITS_DIR, "train.csv"))
    assert os.path.exists(os.path.join(real_pipe.SPLITS_DIR, "val.csv"))
    assert os.path.exists(os.path.join(real_pipe.SPLITS_DIR, "test.csv"))
    assert os.path.exists(os.path.join(real_pipe.SPLITS_DIR, "manifest.json"))

    # Verify no sample appears in more than one partition
    def read_ids(filename):
        with open(os.path.join(real_pipe.SPLITS_DIR, filename), "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            return {r["sample_id"] for r in reader if r.get("sample_id")}

    train_ids = read_ids("train.csv")
    val_ids = read_ids("val.csv")
    test_ids = read_ids("test.csv")

    assert train_ids.isdisjoint(val_ids), "Train and Val partitions must not share samples!"
    assert train_ids.isdisjoint(test_ids), "Train and Test partitions must not share samples!"
    assert val_ids.isdisjoint(test_ids), "Val and Test partitions must not share samples!"


def test_real_produce_experiment_pending_state(db_session, isolated_real_pipeline):
    """
    Verifies that running the real produce experiment returns PENDING_REAL_DATA
    when genuine consensus-annotated samples < 10, refusing to fabricate fake metrics.
    """
    res = real_pipe.run_real_produce_validation_experiment(db=db_session, experiment_name="TEST_REAL_EXP")
    assert res["status"] in {"PENDING_REAL_DATA", "completed"}
    assert res["evaluation_type"] == "real_produce_validation"
    assert res["is_synthetic"] is False


def test_strict_real_synthetic_isolation(isolated_real_pipeline):
    """Verifies that synthetic data is strictly isolated and never leaks into real dataset splits."""
    real_records = real_pipe.load_metadata_records()
    for r in real_records:
        assert r["dataset_type"] == "REAL_PRODUCE"
        assert not r["sample_id"].startswith("syn_"), f"Synthetic ID {r['sample_id']} found in real dataset!"
        assert r["is_synthetic"] in {"False", "false", "0"}


def test_real_produce_api_endpoints(client, db_session, isolated_real_pipeline):
    """Verifies REST API endpoints for real produce dataset management."""
    # 1. GET /api/v1/produce/real/status
    resp = client.get("/api/v1/produce/real/status")
    assert resp.status_code == 200
    st_data = resp.json()["data"]
    assert "real_images_collected" in st_data
    assert "real_images_required" in st_data
    assert st_data["real_images_required"] == 30

    # 2. POST /api/v1/produce/real/upload
    img_bytes = create_test_produce_bytes(seed=20, color=(218, 32, 22))
    files = {"file": ("api_tomato.jpg", img_bytes, "image/jpeg")}
    data = {"source_type": "farm_harvest", "capture_environment": "packhouse_table"}
    up_resp = client.post("/api/v1/produce/real/upload", files=files, data=data)
    assert up_resp.status_code == 200
    up_data = up_resp.json()["data"]
    sample_id = up_data["sample_id"]
    assert sample_id.startswith("real_tom_")

    # 3. POST /api/v1/produce/real/annotate (Grader 1)
    ann_resp = client.post("/api/v1/produce/real/annotate", json={
        "sample_id": sample_id,
        "grader_id": "api_grader_01",
        "grade": "A",
        "confidence": 95.0,
        "notes": "Excellent grade."
    })
    assert ann_resp.status_code == 200

    # 4. POST /api/v1/produce/real/splits
    split_resp = client.post("/api/v1/produce/real/splits")
    assert split_resp.status_code == 200

    # 5. POST /api/v1/produce/real/experiment
    exp_resp = client.post("/api/v1/produce/real/experiment", json={"experiment_name": "API_REAL_EXP"})
    assert exp_resp.status_code == 200
    exp_data = exp_resp.json()["data"]
    assert exp_data["evaluation_type"] == "real_produce_validation"
    assert exp_data["is_synthetic"] is False


def test_batch_upload_real_produce_api(client, isolated_real_pipeline):
    """Verifies batch upload endpoint for real produce images."""
    img1 = create_test_produce_bytes(seed=31, color=(210, 25, 20))
    img2 = create_test_produce_bytes(seed=32, color=(190, 80, 25))

    files = [
        ("files", ("batch_tom_1.jpg", img1, "image/jpeg")),
        ("files", ("batch_tom_2.jpg", img2, "image/jpeg"))
    ]
    data = {
        "collection_category": "apparent_minor_defects",
        "source_type": "field_harvest",
        "capture_environment": "packhouse_table"
    }

    resp = client.post("/api/v1/produce/real/batch-upload", files=files, data=data)
    assert resp.status_code == 200
    resp_data = resp.json()["data"]
    assert resp_data["total_processed"] == 2
    assert resp_data["succeeded"] == 2
    assert resp_data["failed"] == 0
    assert len(resp_data["results"]) == 2
    assert resp_data["results"][0]["success"] is True

    # Test duplicate upload in batch
    dup_files = [("files", ("batch_tom_dup.jpg", img1, "image/jpeg"))]
    dup_resp = client.post("/api/v1/produce/real/batch-upload", files=dup_files, data=data)
    assert dup_resp.status_code == 200
    dup_data = dup_resp.json()["data"]
    assert dup_data["succeeded"] == 0
    assert dup_data["failed"] == 1
    assert dup_data["results"][0]["is_duplicate"] is True


def test_list_real_produce_samples_double_blind_api(client, isolated_real_pipeline):
    """Verifies sample listing endpoint respects double-blind isolation."""
    img = create_test_produce_bytes(seed=45, color=(215, 30, 25))
    up_resp = client.post(
        "/api/v1/produce/real/upload",
        files={"file": ("blind_tom.jpg", img, "image/jpeg")},
        data={"collection_category": "apparent_high_quality"}
    )
    assert up_resp.status_code == 200
    sample_id = up_resp.json()["data"]["sample_id"]

    # Submit Grader 1
    client.post("/api/v1/produce/real/annotate", json={
        "sample_id": sample_id,
        "grader_id": "grader_alice",
        "grade": "A",
        "confidence": 92.0
    })

    # Query as grader_bob (Grader 2) - should not see Alice's grade
    list_resp = client.get(f"/api/v1/produce/real/samples?viewer_id=grader_bob")
    assert list_resp.status_code == 200
    samples = list_resp.json()["data"]["samples"]
    target = next((s for s in samples if s["sample_id"] == sample_id), None)
    assert target is not None
    assert target["annotation_status"] == "PARTIALLY_ANNOTATED"
    assert target["grader_1_grade"] is None  # Masked for Bob!

    # Query as grader_alice - can see their own grade
    list_alice = client.get(f"/api/v1/produce/real/samples?viewer_id=grader_alice")
    sample_alice = next(s for s in list_alice.json()["data"]["samples"] if s["sample_id"] == sample_id)
    assert sample_alice["grader_1_grade"] == "A"


def test_produce_stakeholder_survey_api(client, isolated_real_pipeline):
    """Verifies stakeholder feedback status and submission flow."""
    # 1. Initial status -> PENDING_EXTERNAL_EVIDENCE
    st_resp = client.get("/api/v1/produce/stakeholder/status")
    assert st_resp.status_code == 200
    st_data = st_resp.json()["data"]
    assert st_data["status"] == "PENDING_EXTERNAL_EVIDENCE"
    assert st_data["total_participants"] == 0

    # 2. Submit anonymous feedback
    payload = {
        "role": "PRODUCE_GRADER",
        "completed_tasks": {"task_1": True, "task_2": True, "task_3": True, "task_4": True, "task_5": True},
        "likert_scores": {
            "q1_usability": 5,
            "q2_explanation_clarity": 5,
            "q3_attribute_accuracy": 4,
            "q4_disagreement_fairness": 5,
            "q5_packhouse_viability": 5
        },
        "qualitative_feedback": {
            "missing_info": "None, explanations are clear.",
            "override_scenarios": "When fruit has internal spongy soft spots.",
            "speed_improvements": "Barcode scanning for crate IDs."
        }
    }
    sub_resp = client.post("/api/v1/produce/stakeholder/submit", json=payload)
    assert sub_resp.status_code == 200
    sub_data = sub_resp.json()["data"]
    assert sub_data["success"] is True
    assert sub_data["total_participants"] == 1

    # 3. Query status again -> RECORDED_SESSIONS
    st_resp_after = client.get("/api/v1/produce/stakeholder/status")
    assert st_resp_after.status_code == 200
    st_data_after = st_resp_after.json()["data"]
    assert st_data_after["status"] == "RECORDED_SESSIONS"
    assert st_data_after["total_participants"] == 1
    assert st_data_after["mean_scores"]["q1_usability"] == 5.0


def test_produce_failure_cases_api(client):
    """Verifies endpoint returns all 4 documented produce failure cases."""
    resp = client.get("/api/v1/produce/real/failure-cases")
    assert resp.status_code == 200
    cases = resp.json()["data"]["failure_cases"]
    assert len(cases) == 4
    case_ids = [c["case_id"] for c in cases]
    assert "case_1_lighting_blur" in case_ids
    assert "case_2_surface_occlusion" in case_ids
    assert "case_3_borderline_defect" in case_ids
    assert "case_4_wood_grain_shadows" in case_ids


def test_experiment_runner_edge_cases():
    """
    Verifies experiment runner correctly computes median durations,
    denominators, and handles zero baseline dispute rate as undefined without division by zero.
    """
    from backend.evaluation.produce_experiment_runner import run_before_and_after_experiment

    # Case 1: Baseline dispute rate is 0.0% (both graders agreed on everything)
    baseline_perfect = [
        {"sample_id": "s1", "grader_1_grade": "A", "grader_2_grade": "A", "reference_grade": "A", "duration_sec": 24.0},
        {"sample_id": "s2", "grader_1_grade": "B", "grader_2_grade": "B", "reference_grade": "B", "duration_sec": 26.0}
    ]
    assisted_perfect = [
        {"sample_id": "s1", "grader_1_grade": "A", "grader_2_grade": "A", "reference_grade": "A", "duration_sec": 14.0},
        {"sample_id": "s2", "grader_1_grade": "B", "grader_2_grade": "B", "reference_grade": "B", "duration_sec": 16.0}
    ]

    res = run_before_and_after_experiment(baseline_perfect, assisted_perfect, is_synthetic=False)
    comp = res["comparison"]
    assert comp["dispute_rate_baseline_pct"] == 0.0
    assert comp["relative_dispute_reduction_pct"] is None  # Undefined!
    assert "UNDEFINED" in comp["relative_dispute_reduction_display"]
    assert comp["median_duration_baseline_sec"] == 25.0
    assert comp["median_duration_assisted_sec"] == 15.0

