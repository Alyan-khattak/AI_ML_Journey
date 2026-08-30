# MLflow — Beginner Guide

MLflow = ML experiment tracking tool. Har model run ka metrics, params, aur model save karta hai. Baad mein compare kar sako.

---

## Why MLflow?

```
Without MLflow:
  Run 1: RF, F1=0.85  ← terminal mein dikh ke gaya
  Run 2: LR, F1=0.91  ← kahan gaya pata nahi
  Run 3: GB, F1=0.88  ← best kaunsa tha?

With MLflow:
  Sab runs database mein saved → compare karo → best deploy karo
```

---

## Core Concepts

```
Experiment → project ya task ka naam  (e.g. "NetworkSecurity")
Run        → ek model training attempt
Metric     → jo measure kiya (F1, Accuracy etc.)
Param      → jo use kiya (n_estimators=256 etc.)
Artifact   → jo save kiya (model.pkl, plots etc.)
```

---

## Most Used Code

```python
import mlflow

# ── 1. Experiment set karo ────────────────────────────────────────
mlflow.set_experiment("NetworkSecurity")
# sab runs is experiment ke under jaayenge

# ── 2. Run start karo ─────────────────────────────────────────────
with mlflow.start_run():

    # ── 3. Metrics log karo ───────────────────────────────────────
    mlflow.log_metric("f1_score",       0.95)
    mlflow.log_metric("precision",      0.94)
    mlflow.log_metric("recall",         0.96)

    # ── 4. Params log karo ────────────────────────────────────────
    mlflow.log_param("n_estimators",    256)
    mlflow.log_param("model_type",      "RandomForest")

    # ── 5. Model save karo ────────────────────────────────────────
    mlflow.sklearn.log_model(model, "model")
    # model MLflow ke artifacts mein save hoga

# with block khatam → run automatically end
```

---

## MLflow UI

```bash
# project folder mein chalaao
mlflow ui

# browser mein jaao:
# http://127.0.0.1:5000
```

UI mein dikh raha hoga:
```
Experiments → Runs → Metrics + Params table
                   → Compare runs (graphs)
                   → Download model
```

---

## Is Project Mein Kaise Use Ho Raha Hai

```python
# model_trainer.py → track_mlflow()
def track_mlflow(self, best_model, metric):
    with mlflow.start_run():
        mlflow.log_metric("f1_score",       metric.f1_score)
        mlflow.log_metric("precision_score", metric.precision_score)
        mlflow.log_metric("recall_score",    metric.recall_score)
        mlflow.sklearn.log_model(best_model, "model")
```

Har training run pe:
- Train metrics log hote hain
- Test metrics log hote hain
- Best model MLflow mein save hota hai

---

## Local Storage

```
project/
├── mlflow.db        ← SQLite — experiments + metrics yahan
└── mlruns/          ← artifacts (models, plots) yahan
    └── 0/
        └── run_id/
            └── artifacts/model/
```

---

## DagsHub (Remote MLflow)

```python
import dagshub
dagshub.init(repo_owner="username", repo_name="repo", mlflow=True)
mlflow.set_tracking_uri("https://dagshub.com/username/repo.mlflow")
```

Team ke saath share karna ho → DagsHub pe push karo — sab runs wahan dikhenge.

---

## Quick Reference

| Action | Code |
|---|---|
| Experiment set | `mlflow.set_experiment("name")` |
| Run start | `with mlflow.start_run():` |
| Metric log | `mlflow.log_metric("key", value)` |
| Param log | `mlflow.log_param("key", value)` |
| Model save | `mlflow.sklearn.log_model(model, "name")` |
| Model load | `mlflow.sklearn.load_model("runs:/run_id/name")` |
| UI open | `mlflow ui` → localhost:5000 |
