# Database Architecture

The data layer of the Explainable Livestock Health Grading System (ELHGS) is designed around a **Star Schema** to optimize for analytical queries, dashboard aggregations, and resilient offline synchronization.

## Entity-Relationship Diagram

```mermaid
erDiagram
    FACT_GRADING_EVENTS {
        uuid id PK
        uuid sample_id FK
        uuid grader_id FK
        uuid image_id FK
        uuid criterion_id FK
        string human_grade
        string ai_grade
        float confidence_score
        text explanation
        string review_status
        string client_offline_id
        boolean is_synced
        datetime created_at
    }

    DIM_SAMPLE {
        uuid id PK
        string farm_location
        string species
        datetime created_at
    }

    DIM_GRADER {
        uuid id PK
        string username
        string role
        boolean is_active
        datetime created_at
    }

    DIM_IMAGE {
        uuid id PK
        string file_path
        boolean exif_stripped
        int file_size_bytes
        string resolution
        datetime created_at
    }

    DIM_CRITERION {
        uuid id PK
        string attribute_name
        string rule_condition
        string measured_value
        json metadata_json
        datetime created_at
    }

    FACT_GRADING_EVENTS }|--|| DIM_SAMPLE : "grades"
    FACT_GRADING_EVENTS }o--o| DIM_GRADER : "graded by"
    FACT_GRADING_EVENTS }o--o| DIM_IMAGE : "based on"
    FACT_GRADING_EVENTS }o--o| DIM_CRITERION : "evaluated against"
```

## Star Schema Explanation
- **Fact Table (`fact_grading_events`)**: The core transactional table. Every time a grader submits a grade, accepts an AI prediction, or disputes a result, a record is created here.
- **Dimensions**: Represent the actors (`dim_grader`), the subjects (`dim_sample`), the evidence (`dim_image`), and the logical criteria (`dim_criterion`) that give context to the fact.

## Naming Conventions
- All tables are strictly lower_case_with_underscores.
- Fact tables are prefixed with `fact_`.
- Dimension tables are prefixed with `dim_`.
- Primary keys are UUIDs named `id`.

## Indexing Strategy
- **Foreign Keys**: All foreign keys in the fact table are indexed for fast joins.
- **Offline Sync**: The `client_offline_id` and `is_synced` columns are indexed to optimize the synchronization routines for mobile clients reconnecting to the server.
- **Review Status**: Indexed to allow Senior Reviewers to instantly query the dispute queue.

## Alembic Migration Workflow
Migrations are stored in `backend/alembic/versions/`.

To apply migrations locally:
```bash
alembic upgrade head
```

To autogenerate a new schema revision after altering SQLAlchemy models:
```bash
alembic revision --autogenerate -m "description of changes"
```
