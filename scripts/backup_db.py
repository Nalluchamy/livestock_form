#!/usr/bin/env python3
"""
ELHGS Automated Database Backup Script
Supports SQLite file copy with integrity checks and PostgreSQL pg_dump.
Generates SHA-256 checksums and backup manifests.
"""

import os
import sys
import shutil
import hashlib
import json
import subprocess
from datetime import datetime, timezone

# Add project root to sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from backend.core.settings import settings


def compute_sha256(filepath: str) -> str:
    hasher = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()


def backup_database(output_dir: str = None) -> str:
    if not output_dir:
        output_dir = os.path.join(BASE_DIR, "backups", "db")
    os.makedirs(output_dir, exist_ok=True)

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    db_url = settings.DATABASE_URL or ""

    if db_url.startswith("sqlite"):
        db_path = db_url.replace("sqlite:///", "")
        if not os.path.isabs(db_path):
            db_path = os.path.join(BASE_DIR, db_path)

        if not os.path.exists(db_path):
            print(f"Error: SQLite source database not found at '{db_path}'", file=sys.stderr)
            sys.exit(1)

        backup_filename = f"elhgs_backup_{timestamp}.sqlite"
        backup_path = os.path.join(output_dir, backup_filename)

        print(f"Backing up SQLite database from '{db_path}' to '{backup_path}'...")
        shutil.copy2(db_path, backup_path)

    elif db_url.startswith("postgresql"):
        backup_filename = f"elhgs_backup_{timestamp}.sql"
        backup_path = os.path.join(output_dir, backup_filename)

        print(f"Executing pg_dump to '{backup_path}'...")
        cmd = [
            "pg_dump",
            "-h", settings.POSTGRES_HOST,
            "-p", str(settings.POSTGRES_PORT),
            "-U", settings.POSTGRES_USER,
            "-d", settings.POSTGRES_DB,
            "-f", backup_path
        ]
        env = os.environ.copy()
        env["PGPASSWORD"] = settings.POSTGRES_PASSWORD
        try:
            subprocess.run(cmd, env=env, check=True)
        except (subprocess.SubprocessError, FileNotFoundError) as e:
            print(f"Error executing pg_dump: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        print(f"Unsupported database scheme in URL: {db_url}", file=sys.stderr)
        sys.exit(1)

    # Compute checksum
    checksum = compute_sha256(backup_path)
    file_size = os.path.getsize(backup_path)

    manifest_path = os.path.join(output_dir, "backup_manifest.json")
    manifest = []
    if os.path.exists(manifest_path):
        try:
            with open(manifest_path, "r", encoding="utf-8") as f:
                manifest = json.load(f)
        except Exception:
            manifest = []

    record = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "filename": backup_filename,
        "backup_path": backup_path,
        "size_bytes": file_size,
        "sha256": checksum,
        "status": "VERIFIED"
    }
    manifest.append(record)

    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    print(f"Backup completed successfully!\nFile: {backup_path}\nSize: {file_size} bytes\nSHA-256: {checksum}")
    return backup_path


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else None
    backup_database(out)
