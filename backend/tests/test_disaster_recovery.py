import os
import sys
import uuid
import time
import shutil
import tempfile
import pytest
from datetime import datetime, timezone
from sqlalchemy import create_engine, select, func
from sqlalchemy.orm import sessionmaker

from backend.database.base import Base
from backend.models.user import User
from backend.models.expert_annotation import ExpertAnnotation
from backend.models.disagreement_review import DisagreementReview
from backend.models.audit_log import AuditLog
from backend.models.fact_grading_event import FactGradingEvent
from backend.models.dim_sample import DimSample
from backend.models.dim_grader import DimGrader
from backend.models.experiment_result import ExperimentResult
from backend.core.settings import settings
from scripts.backup_db import backup_database, compute_sha256
from scripts.restore_db import restore_database


@pytest.fixture
def disaster_recovery_env(tmp_path):
    """
    Creates an isolated temporary database and backup directory
    to execute a realistic disaster recovery lifecycle.
    """
    db_file = tmp_path / "test_dr_source.db"
    backup_dir = tmp_path / "dr_backups"
    backup_dir.mkdir(parents=True, exist_ok=True)

    db_url = f"sqlite:///{db_file}"
    engine = create_engine(db_url, connect_args={"check_same_thread": False})
    Session = sessionmaker(bind=engine)
    Base.metadata.create_all(bind=engine)

    # Seed representative records across all critical tables
    session = Session()
    try:
        # 1. User
        user = User(
            id=uuid.uuid4(),
            username="dr_vet_lead",
            email="dr_vet@farm.internal",
            hashed_password="hashed_pw_test",
            role="SENIOR_REVIEWER",
            is_active=True,
            is_verified=True
        )
        session.add(user)

        # 2. Expert Annotation
        annotation = ExpertAnnotation(
            sample_id="DR-CATTLE-99",
            image_path="dataset/real/processed/images/dr_cattle_99.jpg",
            expert_grade_1="B",
            expert_grader_1_id="grader_alpha",
            expert_grade_2="C",
            expert_grader_2_id="grader_beta",
            annotation_status="DISAGREEMENT",
            body_condition=2.5,
            coat_quality="Dull",
            eye_condition="Clear",
            wound_presence="None",
            mobility="Normal",
            appetite="Good"
        )
        session.add(annotation)

        # 3. Disagreement Review
        review = DisagreementReview(
            id=uuid.uuid4(),
            original_human_grade="B",
            original_system_grade="C",
            status="PENDING",
            reviewer_rationale="Borderline body condition score requires veterinarian review"
        )
        session.add(review)

        # 4. Audit Log
        audit = AuditLog(
            user_id=user.id,
            username=user.username,
            action="DISASTER_RECOVERY_BASELINE",
            resource_type="system",
            status="SUCCESS",
            details={"env": "dr_test"}
        )
        session.add(audit)

        # 5. Experiment Result
        exp = ExperimentResult(
            experiment_name="dr_eval_test",
            dataset_version="v1.0.0-real",
            model_version="dt-v1.0",
            evaluation_type="retrospective_real",
            status="completed",
            dataset_sample_count=50,
            test_sample_count=15,
            performance_metrics={"accuracy": 86.7},
            expert_agreement_metrics={"cohen_kappa": 0.74}
        )
        session.add(exp)

        session.commit()
    finally:
        session.close()

    # Preserve original settings
    orig_url = settings.DATABASE_URL
    settings.DATABASE_URL = db_url

    yield {
        "db_file": str(db_file),
        "db_url": db_url,
        "backup_dir": str(backup_dir),
        "engine": engine,
        "Session": Session
    }

    # Teardown
    settings.DATABASE_URL = orig_url
    engine.dispose()


def test_backup_and_full_restoration_parity(disaster_recovery_env):
    """
    Full end-to-end disaster recovery test:
    1. Back up populated database.
    2. Verify SHA-256 checksum and manifest.
    3. Simulate catastrophic data loss (table truncation).
    4. Restore from backup.
    5. Verify 100% record parity and application readability.
    6. Measure Recovery Time Objective (RTO).
    """
    env = disaster_recovery_env
    Session = env["Session"]

    # Step 1: Backup database
    backup_file = backup_database(output_dir=env["backup_dir"])
    assert os.path.exists(backup_file)
    assert os.path.getsize(backup_file) > 0

    # Step 2: Verify SHA-256 matches computed
    actual_hash = compute_sha256(backup_file)
    manifest_path = os.path.join(env["backup_dir"], "backup_manifest.json")
    assert os.path.exists(manifest_path)
    with open(manifest_path, "r", encoding="utf-8") as f:
        import json
        manifest = json.load(f)
    matching = [m for m in manifest if m["filename"] == os.path.basename(backup_file)]
    assert len(matching) == 1
    assert matching[0]["sha256"] == actual_hash
    assert matching[0]["status"] == "VERIFIED"

    # Step 3: Simulate catastrophic data loss (delete all users, reviews, annotations)
    session = Session()
    try:
        session.query(User).delete()
        session.query(ExpertAnnotation).delete()
        session.query(DisagreementReview).delete()
        session.query(AuditLog).delete()
        session.query(ExperimentResult).delete()
        session.commit()

        # Confirm data loss
        assert session.query(User).count() == 0
        assert session.query(ExpertAnnotation).count() == 0
        assert session.query(DisagreementReview).count() == 0
    finally:
        session.close()

    # Step 4: Execute Database Restoration & Measure Recovery Time Objective (RTO)
    start_time = time.perf_counter()
    restore_database(backup_file, skip_confirmation=True)
    rto_seconds = time.perf_counter() - start_time

    # Record RTO: Must be under 5.0 seconds for disaster recovery compliance
    assert rto_seconds < 5.0, f"Recovery time exceeded threshold: {rto_seconds:.2f}s"

    # Step 5: Verify Complete Data Parity
    verify_session = Session()
    try:
        # Check User restored
        restored_user = verify_session.query(User).filter_by(username="dr_vet_lead").first()
        assert restored_user is not None
        assert restored_user.email == "dr_vet@farm.internal"
        assert restored_user.role == "SENIOR_REVIEWER"

        # Check Expert Annotation restored
        restored_annot = verify_session.query(ExpertAnnotation).filter_by(sample_id="DR-CATTLE-99").first()
        assert restored_annot is not None
        assert restored_annot.expert_grade_1 == "B"
        assert restored_annot.expert_grade_2 == "C"
        assert restored_annot.annotation_status == "DISAGREEMENT"
        assert restored_annot.body_condition == 2.5

        # Check Disagreement Review restored
        restored_rev = verify_session.query(DisagreementReview).first()
        assert restored_rev is not None
        assert restored_rev.original_human_grade == "B"
        assert restored_rev.original_system_grade == "C"

        # Check Audit Log restored
        restored_audit = verify_session.query(AuditLog).filter_by(action="DISASTER_RECOVERY_BASELINE").first()
        assert restored_audit is not None
        assert restored_audit.username == "dr_vet_lead"

        # Check Experiment Result restored
        restored_exp = verify_session.query(ExperimentResult).filter_by(experiment_name="dr_eval_test").first()
        assert restored_exp is not None
        assert restored_exp.dataset_version == "v1.0.0-real"
        assert restored_exp.performance_metrics["accuracy"] == 86.7
    finally:
        verify_session.close()


def test_restoration_creates_safety_rollback_snapshot(disaster_recovery_env):
    """
    Verifies that restore_db.py creates a pre-restoration rollback snapshot
    before overwriting the active database.
    """
    env = disaster_recovery_env
    backup_file = backup_database(output_dir=env["backup_dir"])

    # Perform restoration
    restore_database(backup_file, skip_confirmation=True)

    # Check for safety snapshot in database directory
    parent_dir = os.path.dirname(env["db_file"])
    bak_files = [f for f in os.listdir(parent_dir) if ".prerestore_" in f and f.endswith(".bak")]
    assert len(bak_files) >= 1, "Pre-restoration rollback snapshot was not created!"


def test_restoration_aborts_on_corrupted_checksum(disaster_recovery_env, capsys):
    """
    Verifies security defense: if a backup file has been altered or tampered with
    so its SHA-256 does not match the signed manifest, restore_database aborts with error code 1.
    """
    env = disaster_recovery_env
    backup_file = backup_database(output_dir=env["backup_dir"])

    # Tamper with backup file
    with open(backup_file, "ab") as f:
        f.write(b"CORRUPTED_BYTES_INJECTED")

    with pytest.raises(SystemExit) as exc_info:
        restore_database(backup_file, skip_confirmation=True)

    assert exc_info.value.code == 1
    captured = capsys.readouterr()
    assert "checksum mismatch" in captured.err.lower()
