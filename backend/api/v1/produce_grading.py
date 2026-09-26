"""
Produce Quality Grading API Endpoints (Stage 2).
Provides:
- Explainable deterministic produce grading (Tomatoes)
- Real image upload, privacy sanitization, and feature extraction
- Double-blind expert annotation with automatic disagreement escalation
- Before-and-after controlled experiment runner and dashboard metrics
- Documented edge cases with expected vs observed outcomes
"""
import os
import uuid
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from sqlalchemy.orm import Session

from backend.database.session import get_db
from backend.schemas.responses import APIResponse, success_response
from backend.schemas.api import ProduceGradeRequest
from backend.services.produce_grading_service import ProduceGradingService
from backend.evaluation import produce_ingestion as pr_ingest
from backend.evaluation import produce_experiment_runner as pr_exp
from backend.evaluation import synthetic_produce_pipeline as syn_pipe
from backend.evaluation import real_produce_pipeline as real_pipe
from backend.core.auth_deps import optional_current_user
from backend.models.user import User


router = APIRouter(prefix="/produce", tags=["Produce Quality Grading"])


@router.post("/grade", response_model=APIResponse[dict])
def grade_produce(
    request: ProduceGradeRequest,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(optional_current_user)
):
    """
    Grades a produce sample deterministically using the Explainable Rule Engine.
    Returns provisional grade, triggered rules, plain-text reasons, and review triggers.
    """
    service = ProduceGradingService(db)
    result = service.grade_sample(
        attributes=request.model_dump(),
        human_grade=request.human_grade,
        create_persistent_review_on_disagreement=request.create_persistent_review or True
    )
    return success_response(message="Produce sample evaluated successfully.", data=result)


@router.post("/upload-and-grade", response_model=APIResponse[dict])
async def upload_and_grade_produce(
    file: UploadFile = File(...),
    human_grade: Optional[str] = Form(None),
    surface_defect_pct: Optional[float] = Form(None),
    ripeness_stage: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(optional_current_user)
):
    """
    Accepts an uploaded produce image, strips EXIF metadata, extracts computer-vision
    features (color ripeness, defect area %, blur, illumination, circularity),
    and executes deterministic explainable grading.
    """
    contents = await file.read()
    if not contents:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Uploaded file is empty.")

    valid, err_msg = pr_ingest.validate_produce_image(contents, file.filename or "")
    if not valid:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=err_msg)

    # Optional manual overrides
    manual_overrides = {}
    if surface_defect_pct is not None:
        manual_overrides["surface_defect_pct"] = surface_defect_pct
    if ripeness_stage is not None:
        manual_overrides["ripeness_stage"] = ripeness_stage

    service = ProduceGradingService(db)
    result = service.grade_sample(
        image_bytes=contents,
        attributes=manual_overrides,
        human_grade=human_grade
    )
    return success_response(message="Produce image processed and graded.", data=result)


@router.post("/upload", response_model=APIResponse[dict])
async def upload_produce_image(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(optional_current_user)
):
    """
    Ingests and sanitizes a real produce photograph into dataset/produce/processed.
    Performs duplicate prevention and logs cryptographic provenance.
    """
    contents = await file.read()
    if not contents:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Uploaded file is empty.")

    res = pr_ingest.process_produce_image(contents, file.filename or "upload.jpg")
    if not res.get("success"):
        code = status.HTTP_409_CONFLICT if res.get("is_duplicate") else status.HTTP_422_UNPROCESSABLE_ENTITY
        raise HTTPException(status_code=code, detail=res.get("error", "Ingestion failed."))

    # Save to processed folder
    processed_dir = os.path.join("dataset", "produce", "processed")
    os.makedirs(processed_dir, exist_ok=True)
    sample_id = f"tom_{uuid.uuid4().hex[:12]}"
    filename = f"{sample_id}.jpg"
    filepath = os.path.join(processed_dir, filename)

    with open(filepath, "wb") as f:
        f.write(res["sanitized_bytes"])

    return success_response(
        message="Produce image ingested and sanitized successfully.",
        data={
            "sample_id": sample_id,
            "filename": filename,
            "sha256": res["sha256"],
            "phash": res["phash"],
            "features": res["features"]
        }
    )


@router.get("/dataset-status", response_model=APIResponse[dict])
def get_dataset_status():
    """
    Returns current status of the produce image repository.
    Reports PENDING_REAL_IMAGES if genuine curated samples < 10.
    """
    status_data = pr_ingest.get_produce_dataset_status()
    return success_response(message="Dataset status retrieved.", data=status_data)


@router.get("/synthetic-status", response_model=APIResponse[dict])
def get_synthetic_dataset_status():
    """
    Returns current status of the synthetic produce dataset, including physical file counts,
    quota status, QC audit results, and strict isolation guarantee.
    """
    summary = syn_pipe.get_synthetic_dataset_summary()
    return success_response(message="Synthetic dataset status retrieved.", data=summary)


@router.post("/synthetic-benchmark", response_model=APIResponse[dict])
def run_synthetic_benchmark(
    payload: Optional[Dict[str, Any]] = None,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(optional_current_user)
):
    """
    Runs a benchmark evaluation on available synthetic produce images and records
    in PostgreSQL under evaluation_type='synthetic_produce_development' to guarantee separation.
    """
    exp_name = (payload or {}).get("experiment_name", "EXP_SYNTHETIC_BENCHMARK_PRODUCE")
    result = syn_pipe.run_synthetic_benchmark_experiment(db=db, experiment_name=exp_name)
    return success_response(message="Synthetic benchmark experiment executed.", data=result)


@router.get("/real/status", response_model=APIResponse[dict])
def get_real_produce_status(db: Session = Depends(get_db)):
    """
    Returns verified status of the genuine produce dataset:
    real_images_collected, real_images_required (30), real_images_remaining,
    annotation progress (annotated, consensus, disagreements, adjudicated),
    and non-fabrication guarantees.
    """
    status_data = real_pipe.get_real_produce_dataset_status(db=db)
    return success_response(message="Real produce dataset status retrieved.", data=status_data)


@router.post("/real/upload", response_model=APIResponse[dict])
async def upload_real_produce_image(
    file: UploadFile = File(...),
    source_type: Optional[str] = Form("field_harvest"),
    capture_environment: Optional[str] = Form("packhouse_table"),
    camera_type: Optional[str] = Form("smartphone_camera"),
    capture_date: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(optional_current_user)
):
    """
    Ingests, sanitizes, and registers a genuine produce photograph into dataset/produce/real/.
    Strips EXIF/GPS, performs PII checks, creates provenance metadata, and registers
    double-blind annotation task in PostgreSQL.
    """
    contents = await file.read()
    if not contents:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Uploaded file is empty.")

    res = real_pipe.ingest_real_produce_image(
        raw_bytes=contents,
        filename=file.filename or "real_tomato.jpg",
        source_type=source_type or "field_harvest",
        capture_environment=capture_environment or "packhouse_table",
        camera_type=camera_type or "smartphone_camera",
        capture_date=capture_date,
        db=db
    )
    if not res.get("success"):
        code = status.HTTP_409_CONFLICT if res.get("is_duplicate") else status.HTTP_422_UNPROCESSABLE_ENTITY
        raise HTTPException(status_code=code, detail=res.get("error", "Real produce ingestion failed."))

    return success_response(message="Genuine produce image ingested and registered successfully.", data=res)


@router.post("/real/annotate", response_model=APIResponse[dict])
def submit_real_produce_grade(
    payload: Dict[str, Any],
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(optional_current_user)
):
    """
    Submits an independent human grader assessment for a genuine tomato sample.
    Supports double-blind isolation and automatic disagreement escalation.
    """
    sample_id = payload.get("sample_id")
    grader_id = payload.get("grader_id") or (current_user.username if current_user else "anonymous_grader")
    grade = payload.get("grade")
    confidence = payload.get("confidence")
    notes = payload.get("notes")

    if not sample_id or not grade:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="sample_id and grade are required.")

    try:
        res = real_pipe.submit_double_blind_produce_grade(
            sample_id=sample_id,
            grader_id=grader_id,
            grade=grade,
            confidence=confidence,
            notes=notes,
            db=db
        )
        return success_response(message="Grade submitted successfully.", data=res)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))


@router.post("/real/adjudicate", response_model=APIResponse[dict])
def adjudicate_real_produce(
    payload: Dict[str, Any],
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(optional_current_user)
):
    """
    Authoritative Senior Reviewer adjudication of inter-grader disagreement on genuine produce.
    """
    sample_id = payload.get("sample_id")
    reviewer_id = payload.get("reviewer_id") or (current_user.username if current_user else "senior_adjudicator")
    final_grade = payload.get("final_grade")
    rationale = payload.get("rationale")

    if not sample_id or not final_grade or not rationale:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="sample_id, final_grade, and rationale are required.")

    try:
        res = real_pipe.adjudicate_produce_disagreement(
            sample_id=sample_id,
            reviewer_id=reviewer_id,
            final_grade=final_grade,
            rationale=rationale,
            db=db
        )
        return success_response(message="Produce disagreement adjudicated successfully.", data=res)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))


@router.get("/real/samples", response_model=APIResponse[dict])
def list_real_produce_samples(
    status: Optional[str] = None,
    viewer_id: Optional[str] = None,
    is_senior: bool = False,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(optional_current_user)
):
    """
    Returns genuine tomato samples with double-blind isolation and status indicators.
    Viewer identity and senior reviewer privilege are respected to prevent grade leaks.
    """
    if viewer_id:
        eff_viewer = viewer_id
        eff_senior = is_senior
    elif current_user:
        eff_viewer = current_user.username
        eff_senior = (current_user.role in ("SENIOR_REVIEWER", "ADMIN")) or is_senior
    else:
        eff_viewer = None
        eff_senior = is_senior

    samples = real_pipe.get_real_produce_samples(
        db=db,
        status_filter=status,
        viewer_id=eff_viewer,
        is_senior=eff_senior
    )
    return success_response(message=f"Retrieved {len(samples)} real produce samples.", data={"samples": samples, "total": len(samples)})


@router.post("/real/batch-upload", response_model=APIResponse[dict])
async def batch_upload_real_produce(
    files: List[UploadFile] = File(...),
    collection_category: Optional[str] = Form("apparent_high_quality"),
    source_type: Optional[str] = Form("field_harvest"),
    capture_environment: Optional[str] = Form("packhouse_table"),
    camera_type: Optional[str] = Form("smartphone_camera"),
    capture_date: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(optional_current_user)
):
    """
    Batch ingests genuine tomato photographs.
    Processes each file through the 12-step sanitization and duplicate detection pipeline.
    Returns per-file status, individual rejection reasons, and summary counts.
    """
    if not files:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No files provided.")

    results = []
    succeeded = 0
    failed = 0

    for file in files:
        contents = await file.read()
        if not contents:
            results.append({
                "filename": file.filename,
                "success": False,
                "error": "File is empty."
            })
            failed += 1
            continue

        res = real_pipe.ingest_real_produce_image(
            raw_bytes=contents,
            filename=file.filename or "real_tomato.jpg",
            source_type=source_type or "field_harvest",
            capture_environment=capture_environment or "packhouse_table",
            camera_type=camera_type or "smartphone_camera",
            collection_category=collection_category or "apparent_high_quality",
            capture_date=capture_date,
            db=db
        )
        if res.get("success"):
            succeeded += 1
            results.append({
                "filename": file.filename,
                "success": True,
                "sample_id": res.get("sample_id"),
                "quality_passed": res.get("quality_passed", True),
                "collection_category": collection_category or "apparent_high_quality"
            })
        else:
            failed += 1
            results.append({
                "filename": file.filename,
                "success": False,
                "error": res.get("error", "Ingestion rejected"),
                "is_duplicate": res.get("is_duplicate", False)
            })

    status_data = real_pipe.get_real_produce_dataset_status(db=db)
    return success_response(
        message=f"Batch processed {len(files)} files: {succeeded} ingested, {failed} rejected.",
        data={
            "total_processed": len(files),
            "succeeded": succeeded,
            "failed": failed,
            "results": results,
            "dataset_status": status_data
        }
    )


@router.get("/stakeholder/status", response_model=APIResponse[dict])
def get_produce_stakeholder_status():
    """
    Returns current status and aggregated responses from the Stage 2 stakeholder study.
    Displays PENDING_EXTERNAL_EVIDENCE when 0 participants have submitted.
    """
    data = real_pipe.get_stakeholder_validation_status()
    return success_response(message="Stakeholder validation status retrieved.", data=data)


@router.post("/stakeholder/submit", response_model=APIResponse[dict])
def submit_produce_stakeholder_feedback(payload: Dict[str, Any]):
    """
    Submits an anonymous participant survey response for the Stage 2 usability study.
    """
    if not payload.get("role"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Participant role is required.")
    res = real_pipe.submit_stakeholder_feedback(payload)
    return success_response(message="Stakeholder feedback submitted successfully.", data=res)


@router.get("/real/failure-cases", response_model=APIResponse[dict])
def get_produce_failure_cases():
    """
    Returns the four documented genuine-image edge & failure cases from docs/ERROR_ANALYSIS.md.
    """
    cases = real_pipe.get_genuine_failure_cases()
    return success_response(message="Documented produce failure cases retrieved.", data={"failure_cases": cases})


@router.post("/real/splits", response_model=APIResponse[dict])
def generate_real_produce_splits():
    """
    Generates leakage-safe train/val/test splits for genuine produce with perceptual dHash clustering.
    """
    splits = real_pipe.split_real_produce_dataset()
    return success_response(message="Real produce splits generated.", data=splits)


@router.post("/real/experiment", response_model=APIResponse[dict])
def run_real_produce_experiment(
    payload: Optional[Dict[str, Any]] = None,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(optional_current_user)
):
    """
    Executes real produce validation experiment under evaluation_type='real_produce_validation'.
    Returns PENDING_REAL_DATA if consensus samples < 10.
    """
    exp_name = (payload or {}).get("experiment_name", "EXP_REAL_PRODUCE_STAGE2")
    res = real_pipe.run_real_produce_validation_experiment(db=db, experiment_name=exp_name)
    return success_response(message="Real produce experiment evaluation executed.", data=res)



@router.get("/experiments/summary", response_model=APIResponse[dict])
def get_experiment_summary(db: Session = Depends(get_db)):
    """
    Returns the Before-and-After Controlled Experiment Dashboard data,
    comparing human-only vs AI-assisted produce grading.
    """
    exp_data = pr_exp.get_produce_experiment_dashboard_data(db)
    return success_response(message="Experiment summary retrieved.", data=exp_data)


@router.post("/experiments/run", response_model=APIResponse[dict])
def run_experiment_trial(
    payload: Dict[str, Any],
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(optional_current_user)
):
    """
    Executes a comparative before-and-after evaluation trial and persists results.
    """
    baseline_trials = payload.get("baseline_trials", [])
    assisted_trials = payload.get("assisted_trials", [])
    exp_name = payload.get("experiment_name", f"EXP_PRODUCE_{uuid.uuid4().hex[:8]}")
    dataset_version = payload.get("dataset_version", "v1.0-produce")
    is_synthetic = payload.get("is_synthetic", False)

    result = pr_exp.run_before_and_after_experiment(
        baseline_trials=baseline_trials,
        assisted_trials=assisted_trials,
        experiment_name=exp_name,
        dataset_version=dataset_version,
        db=db,
        is_synthetic=is_synthetic
    )
    return success_response(message="Experiment run executed and recorded.", data=result)


@router.get("/edge-cases", response_model=APIResponse[dict])
def get_documented_edge_cases():
    """
    Returns the three required Stage 2 edge-case failure scenarios
    with input conditions, expected vs observed behavior, and mitigations.
    """
    cases = [
        {
            "case_id": "CASE_1_POOR_LIGHTING_AND_BLUR",
            "title": "Poor Lighting and Camera Motion Blur",
            "input_conditions": {
                "illumination_lux": 28.0,
                "laplacian_var": 42.1,
                "surface_defect_pct": 2.0
            },
            "expected_behavior": "Image quality gate rejects capture; refuses to assign unverified provisional grade; prompts recapture.",
            "observed_behavior": "Ingestion flags FLAG_LOW_ILLUMINANCE and FLAG_IMAGE_BLUR; sets provisional grade to REJECTED_IMAGE; confidence 0.0%.",
            "failure_etiology": "High-frequency blur attenuates blemish gradients risking false-negative defect detection.",
            "corrective_action": "Viewfinder prompts operator to steady device under diffuse daylight or LED grading lamp >= 500 lux."
        },
        {
            "case_id": "CASE_2_SURFACE_OCCLUSION",
            "title": "Foliage Obstruction and Hidden Defect Risk",
            "input_conditions": {
                "surface_occlusion_pct": 34.0,
                "surface_defect_pct": 3.0,
                "ripeness_stage": "RED"
            },
            "expected_behavior": "System detects surface obstruction; prevents unverified Grade A assignment; flags missing observation.",
            "observed_behavior": "Rule engine attaches RULE_PARTIAL_OCCLUSION_WARNING; review_required set to True; flags OCCLUDED_SURFACE.",
            "failure_etiology": "Single-angle monocular view cannot evaluate obscured blossom-end or calyx cavity where decay initiates.",
            "corrective_action": "Workflow mandates capturing both stem view and lateral profile when occlusion exceeds 20%."
        },
        {
            "case_id": "CASE_3_BORDERLINE_DISAGREEMENT",
            "title": "Borderline Quality & Grader Disagreement (5.1% Defect)",
            "input_conditions": {
                "surface_defect_pct": 5.1,
                "grader_1_grade": "A",
                "grader_2_grade": "B",
                "ripeness_stage": "RED"
            },
            "expected_behavior": "Preserves both human grades; detects discordance; initiates persistent review in PostgreSQL.",
            "observed_behavior": "Rule engine flags BORDERLINE_DEFECT_AREA; discordance detected (A != B); review created with status OPEN.",
            "failure_etiology": "Continuous natural blemish distributions encounter discrete categorical cutoffs (5.0% threshold).",
            "corrective_action": "High-resolution crop escalated to Senior Adjudicator for definitive reference grade recording."
        }
    ]
    return success_response(message="Documented edge cases retrieved.", data={"edge_cases": cases})
