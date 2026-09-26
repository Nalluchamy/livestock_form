"""
CLI Utility for Ingesting Genuine Produce Photographs into EQGS.
Phase 17: Real Produce Dataset Collection & Ingestion Workflow.

Usage:
    python scripts/ingest_real_produce_dataset.py --input-dir /path/to/photos
    python scripts/ingest_real_produce_dataset.py --file /path/to/photo.jpg --source farm_harvest
    python scripts/ingest_real_produce_dataset.py --status
"""
import os
import sys
import argparse
from typing import List

# Setup path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from backend.evaluation.real_produce_pipeline import (
    ingest_real_produce_image,
    get_real_produce_dataset_status,
    split_real_produce_dataset,
    TARGET_IMAGES_REQUIRED
)
from backend.database.session import SessionLocal


def ingest_file(file_path: str, source: str, environment: str, camera: str, category: str = "apparent_high_quality", db=None) -> dict:
    if not os.path.exists(file_path):
        return {"success": False, "error": f"File not found: {file_path}"}
    with open(file_path, "rb") as f:
        content = f.read()
    filename = os.path.basename(file_path)
    return ingest_real_produce_image(
        raw_bytes=content,
        filename=filename,
        source_type=source,
        capture_environment=environment,
        camera_type=camera,
        collection_category=category,
        db=db
    )


def main():
    parser = argparse.ArgumentParser(description="Ingest genuine produce images into EQGS validation repository.")
    parser.add_argument("--input-dir", type=str, help="Directory containing genuine produce photographs")
    parser.add_argument("--file", type=str, help="Single image file to ingest")
    parser.add_argument("--source", type=str, default="field_harvest", help="Source type (field_harvest, packhouse, market)")
    parser.add_argument("--environment", type=str, default="packhouse_table", help="Capture environment (packhouse_table, sorting_crate, greenhouse)")
    parser.add_argument("--camera", type=str, default="smartphone_camera", help="Camera type / device used")
    parser.add_argument("--category", type=str, default="apparent_high_quality", choices=["apparent_high_quality", "apparent_minor_defects", "apparent_substantial_defects"], help="Collection category (target: 10 high-quality, 10 minor defects, 10 substantial defects)")
    parser.add_argument("--split", action="store_true", help="Re-generate leakage-safe splits after ingestion")
    parser.add_argument("--status", action="store_true", help="Print current status of real produce repository")
    args = parser.parse_args()

    db = SessionLocal()

    if args.status or (not args.input_dir and not args.file):
        status_info = get_real_produce_dataset_status(db=db)
        cats = status_info.get("collection_categories", {})
        print("\n================ REAL PRODUCE DATASET STATUS ================")
        print(f"Status:                 {status_info['status']}")
        print(f"Real Images Collected:  {status_info['real_images_collected']}")
        print(f"Target Required:        {status_info['real_images_required']}")
        print(f"Remaining Required:     {status_info['real_images_remaining']}")
        print(f"Recommended Target:     {status_info['recommended_target']}")
        print("--- Collection Categories (Targets: 10/10/10) ---")
        print(f"  Apparently High-Quality:      {cats.get('apparent_high_quality', 0)} / 10 target")
        print(f"  Minor Visible Defects:        {cats.get('apparent_minor_defects', 0)} / 10 target")
        print(f"  Substantial Visible Defects:  {cats.get('apparent_substantial_defects', 0)} / 10 target")
        print("--- Double-Blind Human Annotation ---")
        print(f"Annotation Workflow:    {status_info.get('expert_annotation_status', 'PENDING_EXPERT_ANNOTATION')}")
        print(f"Annotated Samples:      {status_info['images_annotated']}")
        print(f"Consensus Samples:      {status_info['consensus_samples']}")
        print(f"Disagreements:          {status_info['disagreements']}")
        print(f"Adjudicated Samples:    {status_info['adjudicated_samples']}")
        print("=============================================================\n")
        db.close()
        return

    files_to_process: List[str] = []
    if args.file:
        files_to_process.append(args.file)
    elif args.input_dir:
        if not os.path.exists(args.input_dir):
            print(f"Error: Directory '{args.input_dir}' does not exist.")
            db.close()
            sys.exit(1)
        for fname in os.listdir(args.input_dir):
            if fname.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')):
                files_to_process.append(os.path.join(args.input_dir, fname))

    print(f"\nProcessing {len(files_to_process)} produce image(s)...")
    ingested_count = 0
    duplicate_count = 0
    error_count = 0

    for fpath in files_to_process:
        res = ingest_file(fpath, args.source, args.environment, args.camera, category=args.category, db=db)
        if res.get("success"):
            ingested_count += 1
            print(f"[OK] Ingested {os.path.basename(fpath)} -> {res['sample_id']}")
        elif res.get("is_duplicate"):
            duplicate_count += 1
            print(f"[SKIP] Duplicate: {os.path.basename(fpath)} - {res.get('error')}")
        else:
            error_count += 1
            print(f"[FAIL] Error on {os.path.basename(fpath)}: {res.get('error')}")

    print("\n--- Ingestion Run Summary ---")
    print(f"Successfully Ingested:  {ingested_count}")
    print(f"Duplicates Skipped:     {duplicate_count}")
    print(f"Errors Encountered:     {error_count}")

    if args.split:
        splits = split_real_produce_dataset()
        print(f"Regenerated Splits: Train={splits['train_samples']}, Val={splits['val_samples']}, Test={splits['test_samples']}")

    status_info = get_real_produce_dataset_status(db=db)
    print(f"Updated Status: {status_info['status']} ({status_info['real_images_collected']}/{TARGET_IMAGES_REQUIRED} collected, {status_info['real_images_remaining']} remaining)")
    db.close()


if __name__ == "__main__":
    main()
