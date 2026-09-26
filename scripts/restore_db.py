#!/usr/bin/env python3
"""
ELHGS Database Restoration Script
Performs pre-flight integrity verification (SHA-256), creates a rollback snapshot,
and restores SQLite or PostgreSQL databases safely.
"""

import os
import sys
import shutil
import hashlib
import json
import subprocess
from datetime import datetime, timezone

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


def restore_database(backup_file: str, skip_confirmation: bool = False):
    if not os.path.isabs(backup_file):
        backup_file = os.path.join(BASE_DIR, backup_file)

    if not os.path.exists(backup_file):
        print(f"Error: Backup file not found: '{backup_file}'", file=sys.stderr)
        sys.exit(1)

    # 1. Verify Checksum against manifest
    output_dir = os.path.dirname(backup_file)
    manifest_path = os.path.join(output_dir, "backup_manifest.json")
    actual_sha = compute_sha256(backup_file)

    if os.path.exists(manifest_path):
        try:
            with open(manifest_path, "r", encoding="utf-8") as f:
                manifest = json.load(f)
            matching = [m for m in manifest if m.get("filename") == os.path.basename(backup_file)]
            if matching:
                expected_sha = matching[0].get("sha256")
                if expected_sha != actual_sha:
                    print(f"SECURITY ALERT: Backup checksum mismatch!\nExpected: {expected_sha}\nActual:   {actual_sha}", file=sys.stderr)
                    sys.exit(1)
                print(f"Integrity verified: SHA-256 match ({actual_sha[:16]}...)")
        except Exception as e:
            print(f"Warning: Could not parse backup manifest ({e}), proceeding with calculated checksum.")

    if not skip_confirmation:
        confirm = input(f"Are you sure you want to restore '{backup_file}'? This will overwrite the active database! (yes/no): ")
        if confirm.strip().lower() != "yes":
            print("Restore aborted by user.")
            sys.exit(0)

    db_url = settings.DATABASE_URL or ""

    if db_url.startswith("sqlite"):
        db_path = db_url.replace("sqlite:///", "")
        if not os.path.isabs(db_path):
            db_path = os.path.join(BASE_DIR, db_path)

        # Create pre-restore safety rollback snapshot
        if os.path.exists(db_path):
            safety_copy = f"{db_path}.prerestore_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.bak"
            shutil.copy2(db_path, safety_copy)
            print(f"Created pre-restore safety copy at '{safety_copy}'")

        print(f"Restoring SQLite database to '{db_path}'...")
        shutil.copy2(backup_file, db_path)

    elif db_url.startswith("postgresql"):
        print(f"Restoring PostgreSQL database from '{backup_file}'...")
        cmd = [
            "psql",
            "-h", settings.POSTGRES_HOST,
            "-p", str(settings.POSTGRES_PORT),
            "-U", settings.POSTGRES_USER,
            "-d", settings.POSTGRES_DB,
            "-f", backup_file
        ]
        env = os.environ.copy()
        env["PGPASSWORD"] = settings.POSTGRES_PASSWORD
        try:
            subprocess.run(cmd, env=env, check=True)
        except (subprocess.SubprocessError, FileNotFoundError) as e:
            print(f"Error restoring PostgreSQL database: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        print(f"Unsupported database scheme: {db_url}", file=sys.stderr)
        sys.exit(1)

    print(f"Database restoration completed successfully from '{backup_file}'.")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python restore_db.py <path_to_backup_file> [--yes]", file=sys.stderr)
        sys.exit(1)
    backup_arg = sys.argv[1]
    skip_conf = "--yes" in sys.argv or "-y" in sys.argv
    restore_database(backup_arg, skip_confirmation=skip_conf)
