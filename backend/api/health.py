import os
import time
import shutil
from datetime import datetime, timezone
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text

from backend.schemas.responses import APIResponse, success_response
from backend.core.settings import settings
from backend.database.session import get_db

router = APIRouter(tags=["Health"])

START_TIME = time.time()


@router.get("/health", response_model=APIResponse[dict])
def health_check(db: Session = Depends(get_db)):
    """
    Comprehensive operational health check endpoint.
    Reports database connectivity, disk storage capacity, model artifact availability, and uptime.
    """
    # 1. Database Connectivity Check
    db_status = {"connected": False, "latency_ms": 0.0, "dialect": "unknown"}
    t0 = time.time()
    try:
        db.execute(text("SELECT 1"))
        db_status["latency_ms"] = round((time.time() - t0) * 1000, 2)
        db_status["connected"] = True
        db_status["dialect"] = db.bind.dialect.name if db.bind else "sqlite"
    except Exception as e:
        db_status["error"] = str(e)

    # 2. Disk Storage Check
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    processed_dir = os.path.join(base_dir, "dataset", "real", "processed", "images")
    os.makedirs(processed_dir, exist_ok=True)

    disk_status = {"writable": False, "free_space_mb": 0.0}
    try:
        test_file = os.path.join(processed_dir, ".health_check_probe")
        with open(test_file, "w") as f:
            f.write("ok")
        os.remove(test_file)
        disk_status["writable"] = True

        total, used, free = shutil.disk_usage(processed_dir)
        disk_status["free_space_mb"] = round(free / (1024 * 1024), 2)
        disk_status["total_space_mb"] = round(total / (1024 * 1024), 2)
    except Exception as e:
        disk_status["error"] = str(e)

    # 3. Model Artifact Availability
    models_dir = os.path.join(base_dir, "backend", "evaluation", "models")
    artifacts = {
        "models_directory_exists": os.path.isdir(models_dir),
        "synthetic_dataset_available": os.path.isdir(os.path.join(base_dir, "dataset", "synthetic")),
        "real_dataset_directory_ready": os.path.isdir(processed_dir),
    }

    # 4. Overall Service Status
    is_healthy = db_status["connected"] and disk_status["writable"]
    overall_status = "healthy" if is_healthy else "degraded"

    uptime_seconds = round(time.time() - START_TIME, 1)

    return success_response(
        message="Service is healthy" if is_healthy else "Service is experiencing degraded performance",
        data={
            "status": overall_status,
            "version": settings.VERSION,
            "environment": settings.ENVIRONMENT,
            "uptime_seconds": uptime_seconds,
            "database": db_status,
            "storage": disk_status,
            "artifacts": artifacts,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    )


@router.get("/health/detailed", response_model=APIResponse[dict])
def detailed_health_check(db: Session = Depends(get_db)):
    """
    Detailed operational health and observability endpoint.
    Aggregates database connectivity, storage metrics, audit incident statistics,
    and backup verification records.
    """
    import json
    from sqlalchemy import select, func
    from backend.models.audit_log import AuditLog

    # 1. Base health check
    base_health = health_check(db)
    base_data = dict(base_health.get("data", {}))

    # 2. Audit incident monitoring
    auth_failures = db.execute(
        select(func.count(AuditLog.id)).where(AuditLog.action == "AUTH_LOGIN_FAILURE")
    ).scalar() or 0
    token_reuse_alerts = db.execute(
        select(func.count(AuditLog.id)).where(AuditLog.action == "AUTH_TOKEN_REUSE_DETECTED")
    ).scalar() or 0
    authz_denials = db.execute(
        select(func.count(AuditLog.id)).where(AuditLog.action == "AUTHZ_ACCESS_DENIED")
    ).scalar() or 0

    # 3. Backup Status from manifest
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    manifest_path = os.path.join(base_dir, "backups", "db", "backup_manifest.json")
    backup_summary = {"manifest_found": False, "latest_backup": None, "total_backups": 0}
    if os.path.exists(manifest_path):
        try:
            with open(manifest_path, "r", encoding="utf-8") as f:
                manifest_data = json.load(f)
                if manifest_data:
                    backup_summary["manifest_found"] = True
                    backup_summary["total_backups"] = len(manifest_data)
                    backup_summary["latest_backup"] = manifest_data[-1]
        except Exception:
            pass

    operational_metrics = {
        "authentication_failures_count": auth_failures,
        "token_reuse_security_alerts": token_reuse_alerts,
        "authorization_access_denials": authz_denials,
        "backup_verification": backup_summary,
        "max_upload_size_mb": settings.MAX_UPLOAD_SIZE_BYTES // (1024 * 1024),
        "demo_mode": settings.DEMO_MODE,
    }

    base_data["operational_monitoring"] = operational_metrics

    return success_response(
        message="Detailed operational health metrics retrieved.",
        data=base_data
    )
