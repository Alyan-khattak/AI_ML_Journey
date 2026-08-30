# 🔐 Network Security MLOps Pipeline

> End-to-end MLOps system for phishing URL detection — from raw data in MongoDB Atlas to a live FastAPI prediction service. Built with production-grade modularity: timestamped artifact versioning, typed component contracts, schema validation with statistical drift detection, and full experiment tracking via MLflow + DagsHub.


[![Python](https://img.shields.io/badge/Python-3.10-blue?style=flat-square)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green?style=flat-square)](https://fastapi.tiangolo.com)
[![MLflow](https://img.shields.io/badge/MLflow-Tracked-orange?style=flat-square)](https://dagshub.com/Alyan-khattak/Network-Security-MLops)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue?style=flat-square)](https://hub.docker.com/r/alyanktk/networksecurity-mlops)
[![HuggingFace](https://img.shields.io/badge/HuggingFace-Model-yellow?style=flat-square)](https://huggingface.co/alyan-ktk/networksecurity-mlops)


---

## 🚀 Links

| Resource | URL |
|---|---|
| **Live Demo** |[live-app](https://network-security-mlops-production.up.railway.app/) |
| **DockerHub** | [hub.docker.com/r/alyanktk/networksecurity-mlops](https://hub.docker.com/r/alyanktk/networksecurity-mlops) |
| **MLflow / DagsHub** | [dagshub.com/Alyan-khattak/Network-Security-MLops](https://dagshub.com/Alyan-khattak/Network-Security-MLops) |
| **Hugging Face** | [huggingface.co/alyan-ktk/networksecurity-mlops](https://huggingface.co/alyan-ktk/networksecurity-mlops) |
| **GitHub** | [github.com/Alyan-khattak/Network-Security-MLops](https://github.com/Alyan-khattak/Network-Security-MLops) |

---

## 📌 What This Project Does

Phishing attacks disguise malicious URLs as legitimate websites to steal credentials and financial data. This pipeline takes a set of 30 URL-based features — derived from the URL structure, domain properties, SSL state, and page behavior — and classifies each URL as **Phishing (1)** or **Legitimate (-1)**.

What makes this different from a simple notebook classifier is the **MLOps infrastructure** around it:

- **MongoDB Atlas** serves as the data source — data is ingested via API, not local files
- **DataValidation** acts as a quality gate — it checks schema compliance and runs a Kolmogorov-Smirnov drift test across all 30 features before any model sees the data
- **Timestamped artifact versioning** — every pipeline run produces its own `Artifacts/timestamp/` folder, preserving the full history of ingested data, validation reports, transformed arrays, and trained models
- **MLflow + DagsHub** track every experiment — F1, Precision, and Recall are logged for both train and test sets, with overfitting detection built in
- **Hugging Face Hub** stores the trained model and preprocessor — decoupling the trained artifacts from the deployment environment
- **FastAPI** serves the model with two prediction modes: batch CSV upload and single manual input via a 30-field form

---

## 📈 Model Results

| Metric | Train | Test |
|---|---|---|
| **F1 Score** | 0.9916 | 0.9716 |
| **Precision** | 0.9887 | 0.9589 |
| **Recall** | 0.9945 | 0.9846 |
| **Overfitting Gap** | — | 0.02 ✅ < 0.05 threshold |

**Best Model:** RandomForest (GridSearchCV, cv=5, scoring=f1)
**Dataset:** 11,055 phishing URL records · 30 features · MongoDB Atlas
**Threshold:** 0.5 (default, F1-optimal on this dataset)

---

## 🏗️ System Architecture & Design

All architecture diagrams, system flows, and technical guides are in the **`System_Architecture_&_Design/`** directory:

```
System_Architecture_&_Design/
├── ns_system_diagram.html        ← Interactive HTML — 4 tabs:
│                                   Pipeline Flow (collapsible components)
│                                   Architecture SVG · Data Shapes · Artifacts Tree
├── Complete_system_diagrams.md   ← 13 Mermaid diagrams:
│                                   Per-component detail · Config chain
│                                   Artifact chain · MLflow sequence
│                                   KS drift logic · Data shape flow
├── NetworkSecurity_System_Architecture.pdf  ← PDF export
├── system_design.html            ← Standalone design reference
└── system_flow.md                ← Pipeline flow in markdown
```

> Open `ns_system_diagram.html` in browser for the full interactive diagram with sidebar navigation.

---

## 📦 Pipeline Stages

```
MongoDB Atlas (11,055 records)
    │
    ▼ DataIngestion
    ├── collection.find() → pd.DataFrame
    ├── drop _id · replace "na" → NaN
    ├── stratified 80/20 split
    └── → Artifacts/.../data_ingestion/feature_store/ + ingested/
    │
    ▼ DataValidation
    ├── schema check: 31 columns expected
    ├── numerical column check
    ├── KS drift test (threshold=0.05) per column
    ├── drift_report/report.yaml written
    └── → Artifacts/.../data_validation/validated/ + drift_report/
    │
    ▼ DataTransformation
    ├── X/y split · target -1→0 (binary)
    ├── KNNImputer(n_neighbors=3) fit on train ONLY
    ├── np.c_[X_transformed, y] → .npy arrays
    └── → Artifacts/.../data_transformation/transformed/ + preprocessing.pkl
    │
    ▼ ModelTrainer
    ├── 5 models · GridSearchCV(cv=5, scoring=f1)
    ├── overfit check: |train_f1 - test_f1| > 0.05 → flag
    ├── MLflow: log metrics + model → DagsHub
    ├── NetworkModel(preprocessor, model) → model.pkl
    └── → Artifacts/.../model_trainer/ + final_model/ + HuggingFace
    │
    ▼ FastAPI (app.py)
    ├── GET  /train          → triggers run_pipeline()
    ├── POST /predict        → CSV batch → table.html
    ├── POST /predict/manual → 30-field JSON → prediction
    └── GET  /diagrams       → interactive architecture diagrams
```

---

## 🛠️ Setup & Run

### Prerequisites
- Python 3.10
- MongoDB Atlas free account
- conda or virtualenv

### 1. Clone

```bash
git clone https://github.com/Alyan-khattak/Network-Security-MLops.git
cd Network-Security-MLops
```

### 2. Environment

```bash
conda create -n mlops-env python=3.10 -y
conda activate mlops-env

pip install -r requirements.txt
pip install -e .
```

### 3. Configure Environment Variables

Create `.env` in project root:

```env
MONGO_ATLAS_URI="mongodb+srv://username:password@cluster0.xxx.mongodb.net/?appName=Cluster0"
MLFLOW_TRACKING_USERNAME="your_dagshub_username"
MLFLOW_TRACKING_PASSWORD="your_dagshub_token"
```

> See `MLflow_Beginner_Guide.md` for DagsHub token setup.

### 4. Push Data to MongoDB (run once)

```bash
PYTHONPATH=. python pushdata.py
```

### 5. Run Training Pipeline

```bash
PYTHONPATH=. python main.py
```

Artifacts will be generated in `Artifacts/timestamp/` and model pushed to `final_model/` and HuggingFace.

### 6. Start API Server

```bash
python app.py
# → http://localhost:8000
```

---

## 🐳 Docker

```bash
# Pull and run
docker pull alyanktk/networksecurity-mlops
docker run -p 8000:8000 \
  -e MONGO_ATLAS_URI="your_mongo_uri" \
  alyanktk/networksecurity-mlops

# Or build locally
docker build -t networksecurity-mlops .
docker run -p 8000:8000 networksecurity-mlops
```

---

## 📡 API Routes

| Method | Route | Description |
|---|---|---|
| `GET` | `/` | Landing page with pipeline stats |
| `GET` | `/train` | Trigger full training pipeline |
| `GET` | `/predict` | CSV upload form (batch) |
| `POST` | `/predict` | Batch prediction → HTML results table |
| `GET` | `/predict/manual` | 30-field manual input form |
| `POST` | `/predict/manual` | Single URL prediction (JSON response) |
| `GET` | `/diagrams` | Interactive system architecture diagrams |
| `GET` | `/docs` | Auto-generated Swagger UI |

### Manual Prediction — Example Request

```bash
curl -X POST http://localhost:8000/predict/manual \
  -H "Content-Type: application/json" \
  -d '{"having_IP_Address":-1,"URL_Length":1,"Shortining_Service":1,
       "having_At_Symbol":-1,"double_slash_redirecting":-1,"Prefix_Suffix":-1,
       "having_Sub_Domain":1,"SSLfinal_State":1,"Domain_registeration_length":-1,
       "Favicon":1,"port":1,"HTTPS_token":-1,"Request_URL":1,"URL_of_Anchor":-1,
       "Links_in_tags":1,"SFH":-1,"Submitting_to_email":-1,"Abnormal_URL":-1,
       "Redirect":0,"on_mouseover":-1,"RightClick":1,"popUpWidnow":1,"Iframe":1,
       "age_of_domain":-1,"DNSRecord":-1,"web_traffic":-1,"Page_Rank":-1,
       "Google_Index":1,"Links_pointing_to_page":1,"Statistical_report":-1}'
```

```json
{
  "prediction": 1,
  "label": "Phishing",
  "message": "URL is classified as Phishing"
}
```

**Feature encoding:** `1` = phishing indicator · `-1` = legitimate indicator · `0` = neutral

---

## 📁 Project Structure

```
Network-Security-MLops/
│
├── app.py                              ← FastAPI backend
├── main.py                             ← Pipeline entry point
├── pushdata.py                         ← ETL: CSV → MongoDB
├── setup.py
├── requirements.txt
├── Dockerfile
├── .dockerignore
├── .env                                ← (not committed — add your own)
│
├── .github/workflows/
│   └── main.yml                        ← GitHub Actions CI/CD
│
├── networksecurity/
│   ├── components/
│   │   ├── data_ingestion.py
│   │   ├── data_validation.py
│   │   ├── data_transformation.py
│   │   └── model_trainer.py
│   ├── pipeline/
│   │   └── training_pipeline.py        ← TrainingPipeline.run_pipeline()
│   ├── entity/
│   │   ├── config_entity.py            ← 5 @dataclass config classes
│   │   └── artifact_entity.py          ← 5 @dataclass artifact classes
│   ├── constants/
│   │   └── training_pipeline/__init__.py  ← all constants in one place
│   ├── utils/
│   │   ├── main_utils/utils.py         ← save/load/yaml/evaluate_models
│   │   └── ml_utils/
│   │       ├── model/estimator.py      ← NetworkModel(preprocessor, model)
│   │       └── metric/classification_metric.py
│   ├── cloud/
│   │   └── hf_syncer.py               ← HuggingFace push/pull
│   ├── exception/exception.py
│   └── logging/logger.py
│
├── data_schema/
│   └── schema.yaml                     ← 31 expected columns + types
│
├── templates/
│   ├── index.html
│   ├── predict.html
│   ├── table.html
│   ├── predict_manual.html
│   └── diagrams.html
│
├── System_Architecture_&_Design/       ← diagrams + guides
│   ├── ns_system_diagram.html
│   ├── Complete_system_diagrams.md
│   ├── NetworkSecurity_System_Architecture.pdf
│   ├── system_design.html
│   └── system_flow.md
│
├── MLflow_Beginner_Guide.md            ← MLflow + DagsHub setup guide
├── HuggingFace_Beginner_Guide.md       ← HF Hub setup + usage guide
│
├── Network_Data/
│   └── phishingData.csv
├── Artifacts/                          ← timestamped pipeline runs (gitignored)
└── final_model/                        ← latest model + preprocessor (gitignored)
```

---

## 📖 Guides

Two beginner guides are included in the project root:

| Guide | Contents |
|---|---|
| `MLflow_Beginner_Guide.md` | MLflow concepts, DagsHub connection, logging metrics/models, UI navigation |
| `HuggingFace_Beginner_Guide.md` | Account setup, token creation (Write vs Read), push/pull model, common 403 errors |

---

## ⚙️ Key Engineering Decisions

| Decision | Reason |
|---|---|
| Timestamped artifacts | Full run history — no overwriting |
| Typed artifact dataclasses | Type-safe pipeline contracts |
| Constants folder | No hardcoded values in components |
| KNNImputer fit on train only | Strict no-leakage policy |
| NetworkModel wrapper | One pkl load for preprocessor + model |
| Separate cloud/ module | Cloud sync decoupled from training logic |
| F1 scoring in GridSearchCV | Imbalanced-aware metric (87% ham, 13% spam analog) |

---

## 🧰 Tech Stack

| Category | Tools |
|---|---|
| **Language** | Python 3.10 |
| **ML** | scikit-learn · pandas · numpy · dill |
| **NLP / Imputation** | KNNImputer · Pipeline |
| **Tracking** | MLflow · DagsHub |
| **Model Registry** | Hugging Face Hub |
| **Data Source** | MongoDB Atlas · pymongo · certifi |
| **API** | FastAPI · uvicorn · Jinja2 · pydantic |
| **Containerization** | Docker |
| **CI/CD** | GitHub Actions |

---

## 👤 Author

**M. Alyan Khattak**
[github.com/Alyan-khattak](https://github.com/Alyan-khattak) · [portfolio-alyan.vercel.app](https://portfolio-alyan.vercel.app)