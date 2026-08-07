# System Architecture

This document describes the high-level architecture of the Explainable Livestock Health Grading System (ELHGS).

## System Context Diagram

```mermaid
graph TD
    FG[Field Grader] -->|Inputs attributes & images| Frontend[Frontend App]
    SR[Senior Reviewer] -->|Reviews disputes| Frontend
    FM[Farm Manager] -->|Views dashboard| Frontend
    Buyer[Buyer] -->|Views final grades| Frontend
    
    Frontend -->|API Requests| Backend[FastAPI Backend]
    Backend -->|Reads/Writes| DB[(PostgreSQL)]
    Backend -->|Requests Prediction| ML[Future ML Layer]
```

## Component Diagram

```mermaid
graph TD
    subgraph Frontend [React / Vite App]
        UI[UI Components]
        State[State Management]
        Offline[Offline Cache]
    end

    subgraph Backend [FastAPI Application]
        API[API Routers]
        Auth[Auth Middleware]
        Services[Business Logic Services]
        RuleEngine[Rule Engine]
    end

    subgraph Data [Data Layer]
        ORM[SQLAlchemy ORM]
        DB[(PostgreSQL Star Schema)]
    end

    UI --> State
    State --> Offline
    Offline -->|Sync| API
    API --> Auth
    Auth --> Services
    Services --> RuleEngine
    Services --> ORM
    ORM --> DB
```

## Deployment Diagram

```mermaid
graph TD
    User((User Devices)) -->|HTTPS| CDN[Vercel CDN - Frontend]
    User -->|HTTPS| API_Gateway[Render/Railway - Backend]
    API_Gateway --> Backend_Container[FastAPI Docker Container]
    Backend_Container --> DB_Container[(PostgreSQL Docker Container)]
```

## Data Flow Diagram

```mermaid
sequenceDiagram
    participant Grader as Field Grader
    participant App as Frontend App
    participant API as Backend API
    participant DB as PostgreSQL Database
    participant ML as Future ML Layer

    Grader->>App: Submits Attributes & Image
    App->>API: POST /api/v1/grade/predict
    API->>ML: Forward Data
    ML-->>API: Return Grade, Confidence, Explanation
    API-->>App: Display Result
    
    alt Grader Accepts
        Grader->>App: Accept Grade
        App->>API: POST /api/v1/grade/save
        API->>DB: Persist Final Grade
    else Grader Disagrees
        Grader->>App: Submit Disagreement + Reason
        App->>API: POST /api/v1/grade/dispute
        API->>DB: Persist to Review Queue
    end
```

## Technology Stack
- **Frontend:** React, Vite, TypeScript, TailwindCSS
- **Backend:** Python 3.13, FastAPI, SQLAlchemy, Alembic
- **Database:** PostgreSQL (Star Schema)
- **Deployment:** Docker Compose, Vercel, Render/Railway

## Architecture Decisions
- **Local-First Frontend:** Implemented to satisfy the strong offline mode requirement.
- **FastAPI:** Chosen for high performance and native async support in Python 3.13.
- **Star Schema Database:** Optimized for dashboard aggregations and analytics.

## Future ML Layer
The future ML Layer will sit behind the backend API and act as an isolated microservice. It will utilize interpretable machine learning techniques (like SHAP or LIME) to guarantee that an explanation string is returned alongside the grade prediction.
