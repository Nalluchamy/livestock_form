# 🚀 Deployment Guide

This document provides step-by-step instructions for deploying the Explainable Livestock Health Grading System (ELHGS) across local Docker Compose environments and cloud platforms (Render, Railway, Vercel).

---

## 1. Local Deployment via Docker Compose

### Prerequisites
- Docker Engine 24+
- Docker Compose v2+

### Running the Stack
1. Clone the repository and copy the environment template:
   ```bash
   cp .env.development.example .env
   ```
2. Build and launch all services (PostgreSQL, FastAPI Backend, React Frontend):
   ```bash
   docker compose up --build -d
   ```
3. Access services:
   - **React PWA Frontend:** `http://localhost`
   - **FastAPI OpenAPI Docs:** `http://localhost:8000/docs`
   - **Health Check Endpoint:** `http://localhost:8000/api/v1/health`

---

## 2. Cloud Deployment Target: Render / Railway (Backend API & PostgreSQL)

### Step-by-Step Render Setup
1. **Database:** Create a Managed PostgreSQL Instance on Render. Copy the Internal Database URL.
2. **Web Service:** Create a new Web Service pointing to the repository.
   - **Environment:** Python 3.13
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`
   - **Environment Variables:**
     - `POSTGRES_HOST`, `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`
     - `DEMO_MODE=true` (for hackathon testing)

---

## 3. Cloud Deployment Target: Vercel (React Frontend PWA)

1. Connect repository to Vercel.
2. Set **Root Directory** to `frontend`.
3. Set **Framework Preset** to `Vite`.
4. Configure environment variable:
   - `VITE_API_BASE_URL=https://your-render-backend.onrender.com/api/v1`
5. Click **Deploy**.
