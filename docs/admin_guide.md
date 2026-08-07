# 🛠️ Administrator & Operations Guide

This guide details operational administration, database maintenance, logging, and model updates for ELHGS.

---

## 1. Database Backup & Restore

### Backup PostgreSQL Database
```bash
docker exec -t elhgs_postgres pg_dump -U elhgs_user elhgs_db > backup_$(date +%Y%m%d).sql
```

### Restore PostgreSQL Database
```bash
cat backup.sql | docker exec -i elhgs_postgres psql -U elhgs_user -d elhgs_db
```

---

## 2. Model Updates & Retraining
To retrain ML models on new empirical observations:
1. Place new training data in `dataset/`.
2. Run retraining pipeline:
   ```bash
   python -m backend.ml.train
   ```
3. Joblib artifacts (`decision_tree.joblib` & `logistic_regression.joblib`) will be updated automatically in `backend/models/`.

---

## 3. Structured Logging & Monitoring
Logs are output in structured format to stdout and persisted to `elhgs.log`. To inspect container logs live:
```bash
docker logs -f elhgs_backend
```
Optional Sentry integration can be enabled by specifying `SENTRY_DSN` in `.env`.
