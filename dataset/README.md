# Datasets

This directory contains datasets used for training and evaluating the Explainable Livestock Health Grading System (ELHGS).

## Folder Layout

- `raw/`: Original, unmodified image data collected from partner farms. **(DO NOT edit files in this directory)**.
- `processed/`: Images that have been normalized, resized, and guaranteed to have all EXIF data stripped.
- `labels/`: Annotations and corresponding baseline human grades in JSON/CSV formats.
- `metadata/`: Safely abstracted categorical information about the samples (e.g., species, location category), stripped of any PII.

## Ethical Image Collection & Metadata Stripping

To adhere to our strict ethical guidelines:
1. **No identifying backgrounds:** Images must be framed to focus solely on the animal. No faces of farm workers or identifiable farm signage should be visible.
2. **Mandatory Metadata Stripping:** All raw images are processed through a stripping script before entering the `processed/` directory. EXIF tags (GPS coordinates, timestamps, device serial numbers) are completely eradicated to prevent any geospatial or temporal tracking of workers.

## Naming Convention

Processed images should use randomized UUIDs to prevent sequential guessing or temporal clustering. 
Example: `e4b5294a-8d19-4a9f-a2e1-7c9b83b6f2d5.jpg`

## Attribute Collection & Grading Workflow

Expert graders provide labels through a double-blind process. Disagreements between expert graders in the raw dataset are preserved to train the ML models on confidence uncertainty, ensuring the final rule engine outputs realistic confidence scores reflecting real-world ambiguity.
