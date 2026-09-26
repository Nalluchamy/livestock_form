import os
import uuid
import pytest
from sqlalchemy.orm import Session
from sqlalchemy import inspect, select
from fastapi.testclient import TestClient

from backend.models.user import User
from backend.models.refresh_token import RefreshToken
from backend.models.audit_log import AuditLog
from backend.repositories.user_repository import UserRepository
from scripts.backup_db import backup_database, compute_sha256


def test_schema_migration_0004_tables_exist(db_session: Session):
    inspector = inspect(db_session.bind)
    tables = inspector.get_table_names()

    assert "users" in tables
    assert "refresh_tokens" in tables
    assert "audit_logs" in tables

    # Verify column existence
    user_cols = {col["name"] for col in inspector.get_columns("users")}
    assert "id" in user_cols
    assert "username" in user_cols
    assert "email" in user_cols
    assert "hashed_password" in user_cols
    assert "role" in user_cols
    assert "failed_login_attempts" in user_cols
    assert "locked_until" in user_cols


def test_transactional_rollback_on_failed_operation(db_session: Session):
    repo = UserRepository(db_session)
    user = repo.create_user("rollback_test", "rb@test.com", "Password2026!", "FARMER")

    # Attempt to insert an invalid entity or force rollback
    try:
        duplicate_user = User(
            id=uuid.uuid4(),
            username="rollback_test", # Duplicate username
            email="another@test.com",
            hashed_password="hash",
            role="FARMER"
        )
        db_session.add(duplicate_user)
        db_session.commit()
    except Exception:
        db_session.rollback()

    # Verify original user remains intact and database session is healthy
    verified = repo.get_by_username("rollback_test")
    assert verified is not None
    assert verified.id == user.id


def test_cascade_delete_user_revokes_tokens(db_session: Session):
    repo = UserRepository(db_session)
    user = repo.create_user("cascade_user", "casc@test.com", "Password2026!", "EXPERT_GRADER")

    # Create refresh token
    rt = repo.create_refresh_token(user.id, "hash_token_abc_123")
    assert rt is not None

    # Delete user
    db_session.delete(user)
    db_session.commit()

    # Query tokens: should be deleted or nonexistent
    remaining_tokens = db_session.execute(
        select(RefreshToken).where(RefreshToken.user_id == user.id)
    ).scalars().all()
    assert len(remaining_tokens) == 0


def test_backup_script_creates_valid_snapshot(tmp_path):
    output_dir = str(tmp_path / "backups")
    backup_file = backup_database(output_dir)

    assert os.path.exists(backup_file)
    assert os.path.getsize(backup_file) > 0

    manifest_file = os.path.join(output_dir, "backup_manifest.json")
    assert os.path.exists(manifest_file)

    sha = compute_sha256(backup_file)
    assert len(sha) == 64


def test_dataset_collection_progress_endpoint(client: TestClient):
    res = client.get("/api/v1/dataset/collection-progress")
    assert res.status_code == 200
    data = res.json()["data"]

    assert "target" in data
    assert data["target"]["min"] == 100
    assert data["target"]["ideal"] == 200
    assert data["target"]["max"] == 300
    assert "progress_percentage" in data
    assert "readiness_status" in data
    assert "clinical_disclaimer" in data
    assert "not provide automated veterinary diagnoses" in data["clinical_disclaimer"]
