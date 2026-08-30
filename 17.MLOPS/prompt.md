# 🏗️ MLOps Project Architecture — Universal Prompt

## ROLE
You are an expert MLOps engineer. Build a complete, production-grade, modular ML pipeline following the exact architecture, folder structure, coding standards, and conventions described below. Every project must follow this template — no exceptions.

---

## PROJECT OVERVIEW
Build a **[PROJECT_NAME]** pipeline for **[TASK: classification/regression/NLP]**.

Dataset: **[DATASET_SOURCE: local CSV / MongoDB / API]**
Target column: **[TARGET_COLUMN]**
Problem type: **[binary classification / multiclass / regression]**
Deployment: **FastAPI + Docker + HuggingFace model registry**

---

## ABSOLUTE RULES (never break these)

```
1. NO hardcoded values anywhere — everything comes from constants/
2. NO fit_transform on test data — fit on train ONLY
3. NO mutating original dataframes — always df.copy()
4. ALWAYS dill not pickle — handles complex sklearn objects
5. ALWAYS typed artifact dataclasses — never return plain tuples
6. ALWAYS timestamped artifacts — Artifacts/timestamp/ per run
7. ALWAYS log at every step — logging.info() throughout
8. ALWAYS custom exception — raise CustomException(e, sys)
9. ALWAYS separate config from logic — config_entity.py only has paths/values
10. ALWAYS os.path.join() — never hardcode slashes
```

□ Problem type: classification / regression / NLP
  → automatically sahi metric select ho

Classification specific:
  → ClassificationMetricArtifact (f1, precision, recall)
  → predict_proba[:, 1]
  → threshold tuning (Youden's J)
  → class_weight parameter

Regression specific:
  → RegressionMetricArtifact (r2, mae, rmse)
  → model.predict() directly
  → no threshold
  → no class_weight

NLP specific:
  → text cleaning (re.sub, lemmatize, stopwords)
  → Word2Vec/TF-IDF in transformation
  → avg_word2vec function in utils
  → gensim env requirement

---

## FOLDER STRUCTURE

```
ProjectName/
│
├── app.py                          ← FastAPI backend
├── main.py                         ← Pipeline entry point (manual run)
├── pushdata.py                     ← ETL: source → MongoDB (if applicable)
├── setup.py                        ← pip install -e .
├── requirements.txt                ← all dependencies
├── requirements-prod.txt           ← production only (no mlflow/dagshub)
├── Dockerfile
├── .dockerignore
├── .env                            ← secrets (never commit)
├── .gitignore
├── Readme.md
│
├── .github/workflows/
│   └── main.yml                    ← GitHub Actions CI/CD
│
├── projectname/                    ← main package (lowercase, no spaces)
│   │
│   ├── __init__.py
│   │
│   ├── constants/
│   │   └── training_pipeline/
│   │       └── __init__.py         ← ALL constants here
│   │
│   ├── entity/
│   │   ├── config_entity.py        ← dataclass configs (paths only)
│   │   └── artifact_entity.py      ← dataclass artifacts (typed returns)
│   │
│   ├── components/
│   │   ├── __init__.py
│   │   ├── data_ingestion.py
│   │   ├── data_validation.py
│   │   ├── data_transformation.py
│   │   └── model_trainer.py
│   │
│   ├── pipeline/
│   │   ├── __init__.py
│   │   └── training_pipeline.py    ← TrainingPipeline class
│   │
│   ├── utils/
│   │   ├── main_utils/
│   │   │   └── utils.py            ← save/load/yaml/evaluate_models
│   │   └── ml_utils/
│   │       ├── model/
│   │       │   └── estimator.py    ← ModelWrapper class
│   │       └── metric/
│   │           └── classification_metric.py  ← or regression_metric.py
│   │
│   ├── cloud/
│   │   └── hf_syncer.py            ← HuggingFace push/pull
│   │
│   ├── exception/
│   │   └── exception.py            ← CustomException
│   │
│   └── logging/
│       └── logger.py               ← logging setup
│
├── data_schema/
│   └── schema.yaml                 ← expected columns + types
│
├── templates/                      ← Jinja2 HTML
│   ├── index.html
│   ├── predict.html
│   ├── table.html
│   └── predict_manual.html
│
├── System_Architecture_&_Design/   ← diagrams + guides
│
├── data/                           ← raw data (gitignored)
├── Artifacts/                      ← timestamped runs (gitignored)
├── final_model/                    ← latest pkl files (gitignored)
└── prediction_output/              ← batch prediction CSVs (gitignored)
```

---

## FILE 1: constants/training_pipeline/__init__.py

```python
# ALL hardcoded values live here — no exceptions
# Prefix naming: DATA_INGESTION_ / DATA_VALIDATION_ / DATA_TRANSFORMATION_ / MODEL_TRAINER_
# import this module everywhere — never hardcode in components

import os
import numpy as np

# ── COMMON ────────────────────────────────────────────────────────
TARGET_COLUMN  = "[target_col_name]"
PIPELINE_NAME  = "[ProjectName]"
ARTIFACT_DIR   = "Artifacts"
FILE_NAME      = "[raw_data].csv"
TRAIN_FILE_NAME = "train.csv"
TEST_FILE_NAME  = "test.csv"
SCHEMA_FILE_PATH = os.path.join("data_schema", "schema.yaml")

# ── DATA INGESTION ─────────────────────────────────────────────────
DATA_INGESTION_COLLECTION_NAME:        str   = "[collection]"
DATA_INGESTION_DATABASE_NAME:          str   = "[database]"
DATA_INGESTION_DIR_NAME:               str   = "data_ingestion"
DATA_INGESTION_FEATURE_STORE_DIR:      str   = "feature_store"
DATA_INGESTION_INGESTED_DIR:           str   = "ingested"
DATA_INGESTION_TRAIN_TEST_SPLIT_RATIO: float = 0.2

# ── DATA VALIDATION ────────────────────────────────────────────────
DATA_VALIDATON_DIR_NAME:                str = "data_validation"
DATA_VALIDATION_VALID_DIR:              str = "validated"
DATA_VALIDATION_INVALID_DIR:            str = "invalid"
DATA_VALIDATION_DRIFT_REPORT_DIR:       str = "drift_report"
DATA_VALIDATION_DRIFT_REPORT_FILE_NAME: str = "report.yaml"

# ── DATA TRANSFORMATION ────────────────────────────────────────────
DATA_TRANSFORMATION_DIR_NAME:               str  = "data_transformation"
DATA_TRANSFORMATION_TRANSFORMED_DATA_DIR:   str  = "transformed"
DATA_TRANSFORMATION_TRANSFORMED_OBJECT_DIR: str  = "transformed_object"
PREPROCESSING_OBJECT_FILE_NAME:             str  = "preprocessing.pkl"
DATA_TRANSFORMATION_IMPUTER_PARAMS:         dict = {
    "missing_values": np.nan,
    "n_neighbors":    3,
    "weights":        "uniform"
}

# ── MODEL TRAINER ──────────────────────────────────────────────────
MODEL_TRAINER_DIR_NAME:                        str   = "model_trainer"
MODEL_TRAINER_TRAIN_MODEL_DIR:                 str   = "trained_model"
MODEL_TRAINER_TRAINED_MODEL_NAME:              str   = "model.pkl"
MODEL_TRAINER_EXPECTED_SCORE:                  float = 0.6
MODEL_TRAINER_OVERFITTING_UNDER_FITTING_THRESHOLD: float = 0.05

# ── HUGGING FACE ───────────────────────────────────────────────────
HF_REPO_ID:   str = "[hf-username]/[project-name]"
HF_REPO_TYPE: str = "model"
HF_MODEL_DIR: str = "final_model/"
```

---

## FILE 2: entity/config_entity.py

```python
# ONLY paths and primitive values — no logic here
# Every config class takes TrainingPipelineConfig → same timestamp

from datetime import datetime
import os
from [projectname].constants import training_pipeline

@dataclass equivalent using __init__:

class TrainingPipelineConfig:
    # generates timestamp → artifact_dir = Artifacts/timestamp
    # ALL other configs inject this → same run folder

class DataIngestionConfig:
    # takes TrainingPipelineConfig
    # builds all paths using os.path.join + constants
    # data_ingestion_dir / feature_store_file_path
    # training_file_path / testing_file_path
    # train_test_split_ratio / collection_name / database_name

class DataValidationConfig:
    # takes TrainingPipelineConfig
    # data_validation_dir / valid_data_dir / invalid_data_dir
    # valid_train_file_path / valid_test_file_path
    # invalid_train_file_path / invalid_test_file_path
    # drift_report_file_path

class DataTransformationConfig:
    # takes TrainingPipelineConfig
    # data_transformation_dir
    # transformed_train_file_path (.npy)
    # transformed_test_file_path  (.npy)
    # transformed_object_file_path (.pkl)

class ModelTrainerConfig:
    # takes TrainingPipelineConfig
    # model_trainer_dir / trained_model_file_path
    # expected_accuracy / overfitting_underfitting_threshold
```

---

## FILE 3: entity/artifact_entity.py

```python
# TYPED return objects — never return plain tuples from components
# @dataclass for each component output
# Next component always receives previous component's artifact

from dataclasses import dataclass

@dataclass
class DataIngestionArtifact:
    train_file_path: str   # "Artifacts/.../ingested/train.csv"
    test_file_path:  str   # "Artifacts/.../ingested/test.csv"

@dataclass
class DataValidationArtifact:
    validation_status:       bool
    valid_train_file_path:   str
    valid_test_file_path:    str
    invalid_train_file_path: str
    invalid_test_file_path:  str
    drift_report_file_path:  str

@dataclass
class DataTransformationArtifact:
    transformed_object_file_path: str  # preprocessing.pkl
    transformed_train_file_path:  str  # train.npy
    transformed_test_file_path:   str  # test.npy

@dataclass
class ClassificationMetricArtifact:   # or RegressionMetricArtifact
    f1_score:        float
    precision_score: float
    recall_score:    float

@dataclass
class ModelTrainerArtifact:
    trained_model_file_path: str
    train_metric_artifact:   ClassificationMetricArtifact
    test_metric_artifact:    ClassificationMetricArtifact
```

---

## FILE 4: utils/main_utils/utils.py

```python
# Common reusable functions — imported everywhere
# dill not pickle — handles complex sklearn objects

def save_object(file_path: str, obj) -> None:
    # os.makedirs + dill.dump(obj, file_obj)
    # BUG: dill.dump(obj, file_obj) NOT dill.dump(file_path, obj)

def load_object(file_path: str) -> object:
    # dill.load(file_obj) → return object

def save_numpy_array_data(file_path: str, array: np.ndarray) -> None:
    # os.makedirs + np.save(file_obj, array)

def load_numpy_array(file_path: str) -> np.ndarray:
    # np.load(file_obj) → return array

def read_yaml_file(file_path: str) -> dict:
    # yaml.safe_load(file) → return dict

def write_yaml_file(file_path: str, content: object, replace: bool = False) -> None:
    # if replace: os.remove if exists
    # os.makedirs + yaml.dump(content, file)

def evaluate_models(X_train, y_train, X_test, y_test, models: dict, params: dict) -> dict:
    # for each model: GridSearchCV(cv=5, scoring="f1" or "r2")
    # model.set_params(**best_params) → model.fit(X_train)
    # score on test → report[name] = score
    # return report dict
    # IMP: use f1_score for classification, r2_score for regression
```

---

## FILE 5: components/data_ingestion.py

```python
class DataIngestion:
    def __init__(self, data_ingestion_config: DataIngestionConfig):
        # self.data_ingestion_config = data_ingestion_config  ← parameter not self

    def export_collection_as_dataframe(self) -> pd.DataFrame:
        # MongoClient(URI, tlsCAFile=certifi.where(), tlsAllowInvalidCertificates=True)
        # collection.find() → list() → pd.DataFrame()
        # drop _id column
        # replace "na" → np.nan
        # return df

    def export_data_into_feature_store(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        # os.makedirs(feature_store_dir)
        # df.to_csv(feature_store_file_path, index=False, header=True)
        # return dataframe

    def split_data_as_train_test(self, dataframe: pd.DataFrame) -> None:
        # train_test_split(df, test_size=split_ratio)
        # os.makedirs(ingested_dir, exist_ok=True)
        # train.to_csv / test.to_csv

    def initiate_data_ingestion(self) -> DataIngestionArtifact:
        # chain all methods
        # return DataIngestionArtifact(train_file_path, test_file_path)
```

---

## FILE 6: components/data_validation.py

```python
class DataValidation:
    def __init__(self, data_ingestion_artifact: DataIngestionArtifact,
                 data_validation_config: DataValidationConfig):
        # self.schema_config = read_yaml_file(SCHEMA_FILE_PATH)

    @staticmethod
    def read_data(file_path: str) -> pd.DataFrame:
        # pd.read_csv(file_path)

    def validate_number_cols(self, dataframe: pd.DataFrame) -> bool:
        # len(schema_config["columns"]) == len(df.columns)

    def check_numerical_col(self, dataframe: pd.DataFrame) -> bool:
        # schema["numerical_columns"] vs df.select_dtypes(["int64","float64"])

    def detect_data_drift(self, base_df, current_df, threshold=0.05) -> bool:
        # for each column: ks_2samp(train_col, test_col)
        # p_value < threshold → drift → status = False
        # write_yaml_file(drift_report_path, report)
        # return status

    def initiate_data_validation(self) -> DataValidationArtifact:
        # validate columns x2 (train + test)
        # check numerical x2
        # detect drift
        # save valid CSVs
        # return DataValidationArtifact
```

---

## FILE 7: components/data_transformation.py

```python
class DataTransformation:
    def __init__(self, data_validation_artifact: DataValidationArtifact,
                 data_transformation_config: DataTransformationConfig):
        pass

    @staticmethod
    def read_data(file_path: str) -> pd.DataFrame:
        # pd.read_csv()

    def get_data_transformer_object(self) -> Pipeline:
        # KNNImputer(**DATA_TRANSFORMATION_IMPUTER_PARAMS)
        # Pipeline(steps=[("imputer", imputer)])
        # Add ColumnTransformer if categorical columns exist
        # Add StandardScaler if SVM/KNN models will be used
        # return pipeline

    def initiate_data_transformation(self) -> DataTransformationArtifact:
        # read valid train + test CSVs
        # X/y split → target separate
        # convert target if needed (-1→0 for binary)
        # preprocessor = get_data_transformer_object()
        # X_train_t = preprocessor.fit_transform(X_train)  ← FIT ON TRAIN ONLY
        # X_test_t  = preprocessor.transform(X_test)       ← TRANSFORM ONLY
        # train_arr = np.c_[X_train_t, y_train]
        # test_arr  = np.c_[X_test_t,  y_test]
        # save_numpy_array_data (train.npy + test.npy)
        # save_object (preprocessing.pkl)
        # return DataTransformationArtifact
```

---

## FILE 8: components/model_trainer.py

```python
class ModelTrainer:
    def __init__(self, model_trainer_config: ModelTrainerConfig,
                 data_transformation_artifact: DataTransformationArtifact):
        pass

    def track_mlflow(self, best_model, metric_artifact):
        # dagshub.init() INSIDE this function — not module level
        # mlflow.start_run()
        # mlflow.log_metric("f1_score", ...)
        # mlflow.sklearn.log_model(best_model, "model")

    def train_model(self, X_train, y_train, X_test, y_test) -> ModelTrainerArtifact:
        # define models dict
        # define params dict (GridSearchCV grids)
        # evaluate_models() → report dict
        # best_model = max(report, key=score)
        # if best_score < expected_accuracy → raise Exception
        # get_classification_score(y_train, y_train_pred) → train_metric
        # get_classification_score(y_test,  y_test_pred)  → test_metric
        # track_mlflow(best_model, train_metric)
        # track_mlflow(best_model, test_metric)
        # overfit check: |train - test| > threshold → log warning
        # preprocessor = load_object(preprocessing.pkl)
        # ModelWrapper(preprocessor, best_model) → save_object(model.pkl)
        # save to final_model/ too
        # push_model_to_huggingface()  ← from cloud/hf_syncer.py
        # return ModelTrainerArtifact

    def initiate_model_trainer(self) -> ModelTrainerArtifact:
        # load_numpy_array(train.npy) + load_numpy_array(test.npy)
        # X_train = arr[:,:-1]  y_train = arr[:,-1]
        # return train_model(X_train, y_train, X_test, y_test)
```

---

## FILE 9: utils/ml_utils/model/estimator.py

```python
class ModelWrapper:
    # wraps preprocessor + model into one object
    # predict(x):
    #   x_t = self.preprocessor.transform(x)
    #   return self.model.predict(x_t)
    # single pkl → one load → predict
    # use in FastAPI routes
```

---

## FILE 10: pipeline/training_pipeline.py

```python
class TrainingPipeline:
    def __init__(self):
        self.training_pipeline_config = TrainingPipelineConfig()

    def start_data_ingestion(self) -> DataIngestionArtifact:
    def start_data_validation(self, artifact) -> DataValidationArtifact:
    def start_data_transformation(self, artifact) -> DataTransformationArtifact:
    def start_model_trainer(self, artifact) -> ModelTrainerArtifact:

    def run_pipeline(self) -> ModelTrainerArtifact:
        # chain all start_* methods
        # each passes previous artifact to next
        # return ModelTrainerArtifact
```

---

## FILE 11: app.py

```python
# FastAPI — always these routes:
# GET  /                  → index.html
# GET  /train             → TrainingPipeline().run_pipeline()
# GET  /predict           → predict.html (CSV form)
# POST /predict           → CSV upload → ModelWrapper.predict() → table.html
# GET  /predict/manual    → predict_manual.html (field form)
# POST /predict/manual    → Pydantic model → DataFrame(1×N) → predict → JSON
# GET  /diagrams          → diagrams.html

# STARTUP EVENT:
# @app.on_event("startup")
# if not os.path.exists("final_model/model.pkl"):
#     pull_model_from_huggingface()

# Pydantic input model:
# class ModelInput(BaseModel):
#     feature1: int/float
#     feature2: int/float
#     ... all features typed

# CORSMiddleware(allow_origins=["*"])
# Jinja2Templates("./templates")
# load from final_model/ — never from Artifacts/
```

---

## FILE 12: cloud/hf_syncer.py

```python
def push_model_to_huggingface(
    folder_path = HF_MODEL_DIR,
    repo_id     = HF_REPO_ID,
    repo_type   = HF_REPO_TYPE,
    private     = False
) -> str:
    # HfApi().create_repo(exist_ok=True)
    # HfApi().upload_folder(folder_path, repo_id)
    # return url

def pull_model_from_huggingface(
    repo_id  = HF_REPO_ID,
    save_dir = HF_MODEL_DIR
) -> str:
    # snapshot_download(repo_id, local_dir=save_dir)
    # return local_path
```

---

## CODING STANDARDS

### Comments style (always follow this):
```python
# ═══════════════════════════════════════════════════════════════════
# filename.py
# ═══════════════════════════════════════════════════════════════════
# One line: what this file does
# How it fits in the pipeline
###==============================================================
"""
Docstring: input → process → output
ASCII flow diagram showing connections to other files
"""
##==================================================================

# ── SECTION NAME ──────────────────────────────────────────────────
# IMP: critical decision explanation
# BUG FIXED: what was wrong → what is correct

# DRY RUN below every major function:
# input → step1 → step2 → output with actual values
```

### Every function must have:
- Docstring with Parameters + Returns
- `logging.info()` at start and end
- `try/except` → `raise CustomException(e, sys)`
- Type hints on parameters and return

### Naming conventions:
```
Constants     → ALL_CAPS_SNAKE_CASE
Classes       → PascalCase
Functions     → snake_case
Variables     → snake_case
Config fields → snake_case with type hints
```

---

## DATA SCHEMA (data_schema/schema.yaml)

```yaml
columns:
  - feature1: int64
  - feature2: float64
  - target:   int64

numerical_columns:
  - feature1
  - feature2

# add categorical_columns if applicable
# add target_column
```

---

## ENVIRONMENT VARIABLES (.env)

```env
MONGO_ATLAS_URI="mongodb+srv://..."
MLFLOW_TRACKING_USERNAME="dagshub_username"
MLFLOW_TRACKING_PASSWORD="dagshub_token"
```

---

## GITIGNORE (always include)

```
Artifacts/
final_model/
prediction_output/
*.pkl
*.npy
mlflow.db
mlruns/
.env
__pycache__/
*.egg-info/
logs/
```

---

## DOCKERFILE

```dockerfile
FROM python:3.10-slim-bullseye
WORKDIR /app
RUN apt-get update && apt-get install -y gcc && rm -rf /var/lib/apt/lists/*
COPY requirements-prod.txt .
RUN pip install --no-cache-dir -r requirements-prod.txt
COPY . .
EXPOSE 8000
CMD ["python", "app.py"]
```

---

## GITHUB ACTIONS (.github/workflows/main.yml)

```yaml
name: CI Pipeline
on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  integration:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with: {python-version: "3.10"}
      - run: pip install -r requirements.txt
      - run: |
          pip install flake8
          flake8 [projectname]/ --count --select=E9,F63,F7,F82 --show-source --statistics
```

---

## ARTIFACTS DIRECTORY (generated — never commit)

```
Artifacts/
└── MM_DD_YYYY_HH_MM_SS/
    ├── data_ingestion/
    │   ├── feature_store/[raw].csv
    │   └── ingested/train.csv + test.csv
    ├── data_validation/
    │   ├── validated/train.csv + test.csv
    │   ├── invalid/train.csv + test.csv
    │   └── drift_report/report.yaml
    ├── data_transformation/
    │   ├── transformed/train.npy + test.npy
    │   └── transformed_object/preprocessing.pkl
    └── model_trainer/
        └── trained_model/model.pkl

final_model/           ← for FastAPI (pulled from HF on deploy)
├── model.pkl
└── preprocessor.pkl
```

---

## COMMON BUGS TO AVOID

```python
# 1. dill argument order
dill.dump(obj, file_obj)          # ✅ correct
dill.dump(file_obj, obj)          # ❌ wrong

# 2. fit_transform on test
X_test = preprocessor.fit_transform(X_test)   # ❌ leakage
X_test = preprocessor.transform(X_test)       # ✅ correct

# 3. dagshub.init() at module level
dagshub.init(...)                  # ❌ runs on every import
def track_mlflow():
    dagshub.init(...)              # ✅ only when training

# 4. MongoClient wrong syntax
database = client(DB_NAME)         # ❌ not callable
database = client[DB_NAME]         # ✅ correct

# 5. __init__ typo
def __int__(self):                 # ❌ integer dunder
def __init__(self):                # ✅ initializer

# 6. self assignment
self.config = self.config          # ❌ assigns nothing
self.config = config               # ✅ assigns parameter

# 7. predict_proba index
y_prob = model.predict_proba(X)[:, 0]   # ❌ if 0=negative class
y_prob = model.predict_proba(X)[:, 1]   # ✅ positive class probability

# 8. makedirs without exist_ok
os.makedirs(path)                  # ❌ crashes if exists
os.makedirs(path, exist_ok=True)   # ✅ safe

# 9. if __name__ check
if __name__ == "__name__":         # ❌ always False
if __name__ == "__main__":         # ✅ correct
```

---

## DELIVERABLES CHECKLIST

```
□ constants/training_pipeline/__init__.py   — all values
□ entity/config_entity.py                  — 5 config classes
□ entity/artifact_entity.py                — 5 artifact dataclasses
□ exception/exception.py                   — CustomException
□ logging/logger.py                        — logging setup
□ utils/main_utils/utils.py                — 7 utility functions
□ utils/ml_utils/model/estimator.py        — ModelWrapper
□ utils/ml_utils/metric/[metric].py        — get_[metric]_score()
□ components/data_ingestion.py             — DataIngestion class
□ components/data_validation.py            — DataValidation class
□ components/data_transformation.py        — DataTransformation class
□ components/model_trainer.py              — ModelTrainer class
□ pipeline/training_pipeline.py            — TrainingPipeline class
□ cloud/hf_syncer.py                       — HF push/pull
□ data_schema/schema.yaml                  — column schema
□ app.py                                   — FastAPI 7 routes
□ main.py                                  — entry point
□ setup.py                                 — package install
□ requirements.txt                         — all deps
□ requirements-prod.txt                    — prod deps only
□ Dockerfile                               — production container
□ .dockerignore
□ .gitignore
□ .env (template only — never commit values)
□ .github/workflows/main.yml               — CI pipeline
□ templates/ (index, predict, table, predict_manual, diagrams)
□ Readme.md                                — full documentation
```

---

## DEEP LEARNING EXTENSION
> Only apply this section if: `Framework: PyTorch / TensorFlow / HuggingFace Transformers`
> Replace corresponding sklearn sections with these

---

### NEW CONSTANTS (add to constants/training_pipeline/__init__.py)

```python
# ── DEEP LEARNING ──────────────────────────────────────────────────
# Add these BELOW existing constants — do not remove sklearn constants

DL_NUM_EPOCHS:              int   = 50
DL_BATCH_SIZE:              int   = 32
DL_LEARNING_RATE:           float = 0.001
DL_HIDDEN_LAYERS:           list  = [128, 64, 32]
DL_DROPOUT_RATE:            float = 0.3
DL_EARLY_STOPPING_PATIENCE: int   = 5
DL_MODEL_FILE_NAME:         str   = "model.pth"      # PyTorch
# DL_MODEL_FILE_NAME:       str   = "model.h5"       # TensorFlow
DL_OPTIMIZER:               str   = "adam"
DL_LOSS_FUNCTION:           str   = "cross_entropy"  # classification
# DL_LOSS_FUNCTION:         str   = "mse"            # regression
```

---

### NEW FOLDER: models/ (add to project root package)

```
projectname/
└── models/
    ├── __init__.py
    └── neural_net.py    ← model architecture ONLY — no training logic here
```

```python
# projectname/models/neural_net.py
# ═══════════════════════════════════════════════════════════════════
# models/neural_net.py
# ═══════════════════════════════════════════════════════════════════
# Neural network architecture define karta hai — ONLY architecture
# No training logic here — ModelTrainer mein hoga
# Config se hyperparams inject hote hain — no hardcoding
###==============================================================

import torch
import torch.nn as nn
from [projectname].constants.training_pipeline import (
    DL_HIDDEN_LAYERS,
    DL_DROPOUT_RATE
)

class NeuralNet(nn.Module):
    """
    Configurable feedforward neural network.
    Hidden layers + dropout config se aate hain — hardcoded nahi.

    Parameters:
        input_dim  (int) : number of features
        output_dim (int) : number of classes (1 for regression/binary)
        hidden_layers (list) : neurons per layer e.g. [128, 64, 32]
        dropout_rate  (float): dropout probability

    FLOW:
    input → Linear → ReLU → Dropout → ... → output layer
    """
    def __init__(self,
                 input_dim:     int,
                 output_dim:    int,
                 hidden_layers: list  = DL_HIDDEN_LAYERS,
                 dropout_rate:  float = DL_DROPOUT_RATE):
        super(NeuralNet, self).__init__()

        layers = []
        prev_dim = input_dim

        # IMP: dynamically build layers from config
        # change DL_HIDDEN_LAYERS in constants → architecture changes
        for hidden_dim in hidden_layers:
            layers.append(nn.Linear(prev_dim, hidden_dim))
            layers.append(nn.ReLU())
            layers.append(nn.Dropout(dropout_rate))
            prev_dim = hidden_dim

        # output layer — no activation (handled by loss function)
        layers.append(nn.Linear(prev_dim, output_dim))

        self.network = nn.Sequential(*layers)

    def forward(self, x):
        return self.network(x)
```

---

### REPLACE: DataTransformation (DL version)

```python
# components/data_transformation.py — DL VERSION
# Difference from sklearn version:
# sklearn → KNNImputer Pipeline → .npy arrays
# DL      → StandardScaler → torch.FloatTensor → DataLoader

import torch
from torch.utils.data import TensorDataset, DataLoader
from sklearn.preprocessing import StandardScaler

class DataTransformation:
    def get_data_transformer_object(self) -> StandardScaler:
        # IMP: StandardScaler for DL — features same scale pe
        # KNNImputer bhi rakh sakte ho Pipeline mein pehle
        return StandardScaler()

    def create_dataloaders(self, X_train, y_train, X_test, y_test):
        """
        numpy arrays → PyTorch DataLoaders

        FLOW:
        numpy → torch.FloatTensor → TensorDataset → DataLoader
        DataLoader → batched training → GPU compatible
        """
        # numpy → torch tensors
        X_train_t = torch.FloatTensor(X_train)
        y_train_t = torch.LongTensor(y_train)    # classification
        # y_train_t = torch.FloatTensor(y_train) # regression

        X_test_t  = torch.FloatTensor(X_test)
        y_test_t  = torch.LongTensor(y_test)

        # TensorDataset → pairs X with y
        train_dataset = TensorDataset(X_train_t, y_train_t)
        test_dataset  = TensorDataset(X_test_t,  y_test_t)

        # DataLoader → batching + shuffling
        train_loader = DataLoader(
            train_dataset,
            batch_size=DL_BATCH_SIZE,
            shuffle=True    # IMP: shuffle train only — not test
        )
        test_loader = DataLoader(
            test_dataset,
            batch_size=DL_BATCH_SIZE,
            shuffle=False   # IMP: never shuffle test
        )

        return train_loader, test_loader

    def initiate_data_transformation(self) -> DataTransformationArtifact:
        # read valid CSVs
        # X/y split
        # preprocessor = get_data_transformer_object()
        # X_train_t = preprocessor.fit_transform(X_train) ← FIT ONLY ON TRAIN
        # X_test_t  = preprocessor.transform(X_test)
        # train_loader, test_loader = create_dataloaders(...)
        # save_object(preprocessing.pkl, preprocessor)
        # save_numpy_array_data(train.npy, np.c_[X_train_t, y_train])
        # save_numpy_array_data(test.npy,  np.c_[X_test_t, y_test])
        # return DataTransformationArtifact
```

---

### REPLACE: ModelTrainer (DL version)

```python
# components/model_trainer.py — DL VERSION
# Difference from sklearn version:
# sklearn → GridSearchCV → model.fit() → done
# DL      → manual training loop → epochs → early stopping → lr scheduler

import torch
import torch.nn as nn
import torch.optim as optim
from [projectname].models.neural_net import NeuralNet

class ModelTrainer:

    def get_optimizer(self, model):
        # IMP: optimizer config se aata hai — not hardcoded
        if DL_OPTIMIZER == "adam":
            return optim.Adam(model.parameters(), lr=DL_LEARNING_RATE)
        elif DL_OPTIMIZER == "sgd":
            return optim.SGD(model.parameters(), lr=DL_LEARNING_RATE)

    def get_criterion(self):
        if DL_LOSS_FUNCTION == "cross_entropy":
            return nn.CrossEntropyLoss()   # classification
        elif DL_LOSS_FUNCTION == "mse":
            return nn.MSELoss()            # regression

    def train_one_epoch(self, model, loader, optimizer, criterion, device):
        """One epoch training loop"""
        model.train()
        total_loss = 0

        for X_batch, y_batch in loader:
            X_batch = X_batch.to(device)
            y_batch = y_batch.to(device)

            optimizer.zero_grad()          # gradients reset
            output = model(X_batch)        # forward pass
            loss   = criterion(output, y_batch)  # loss calculate
            loss.backward()                # backward pass
            optimizer.step()               # weights update

            total_loss += loss.item()

        return total_loss / len(loader)

    def evaluate(self, model, loader, criterion, device):
        """Validation loop — no gradient computation"""
        model.eval()
        total_loss = 0
        correct    = 0
        total      = 0

        with torch.no_grad():              # IMP: no grad on eval
            for X_batch, y_batch in loader:
                X_batch = X_batch.to(device)
                y_batch = y_batch.to(device)

                output  = model(X_batch)
                loss    = criterion(output, y_batch)
                total_loss += loss.item()

                # accuracy
                predicted = torch.argmax(output, dim=1)
                correct  += (predicted == y_batch).sum().item()
                total    += y_batch.size(0)

        return total_loss / len(loader), correct / total

    def train_model(self, X_train, y_train, X_test, y_test):
        # device setup
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        logging.info(f"Training on: {device}")

        # model banao
        input_dim  = X_train.shape[1]
        output_dim = len(np.unique(y_train))  # classes
        model      = NeuralNet(input_dim, output_dim).to(device)

        optimizer  = self.get_optimizer(model)
        criterion  = self.get_criterion()

        # learning rate scheduler — reduce on plateau
        scheduler  = optim.lr_scheduler.ReduceLROnPlateau(
            optimizer, patience=3, factor=0.5
        )

        # DataLoaders
        train_loader, test_loader = create_dataloaders(
            X_train, y_train, X_test, y_test
        )

        # ── TRAINING LOOP ──────────────────────────────────────
        best_val_loss  = float("inf")
        patience_count = 0
        best_model_state = None

        for epoch in range(DL_NUM_EPOCHS):
            train_loss = self.train_one_epoch(
                model, train_loader, optimizer, criterion, device
            )
            val_loss, val_acc = self.evaluate(
                model, test_loader, criterion, device
            )

            scheduler.step(val_loss)

            logging.info(
                f"Epoch {epoch+1}/{DL_NUM_EPOCHS} | "
                f"Train Loss: {train_loss:.4f} | "
                f"Val Loss: {val_loss:.4f} | "
                f"Val Acc: {val_acc:.4f}"
            )

            # MLflow log per epoch
            mlflow.log_metric("train_loss", train_loss, step=epoch)
            mlflow.log_metric("val_loss",   val_loss,   step=epoch)
            mlflow.log_metric("val_acc",    val_acc,    step=epoch)

            # ── EARLY STOPPING ──────────────────────────────────
            # IMP: save best model — not last epoch
            # val_loss improve nahi → patience_count++
            # patience_count > threshold → stop training
            if val_loss < best_val_loss:
                best_val_loss    = val_loss
                patience_count   = 0
                best_model_state = model.state_dict().copy()
                logging.info(f"Best model saved at epoch {epoch+1}")
            else:
                patience_count += 1
                if patience_count >= DL_EARLY_STOPPING_PATIENCE:
                    logging.info(f"Early stopping at epoch {epoch+1}")
                    break

        # best weights restore karo
        model.load_state_dict(best_model_state)

        # save model
        os.makedirs(os.path.dirname(
            self.model_trainer_config.trained_model_file_path
        ), exist_ok=True)

        torch.save(
            model.state_dict(),
            self.model_trainer_config.trained_model_file_path
        )
        logging.info("Model saved as .pth")

        # HuggingFace push
        push_model_to_huggingface()

        return ModelTrainerArtifact(...)
```

---

### REPLACE: ModelWrapper (DL version)

```python
# utils/ml_utils/model/estimator.py — DL VERSION

class DLModelWrapper:
    """
    Preprocessor + PyTorch model wrap karta hai.
    FastAPI predict route yahan se call karega.
    sklearn ModelWrapper jaisi API — same .predict(x) interface
    """
    def __init__(self, preprocessor, model, input_dim, output_dim,
                 hidden_layers=DL_HIDDEN_LAYERS, dropout_rate=DL_DROPOUT_RATE):
        self.preprocessor  = preprocessor
        self.input_dim     = input_dim
        self.output_dim    = output_dim
        self.hidden_layers = hidden_layers
        self.dropout_rate  = dropout_rate
        # model weights alag load honge — model object nahi store karo
        # dill pytorch models theek se serialize nahi karta

    def load_model(self, model_path: str):
        """model.pth se weights load karo"""
        model = NeuralNet(
            self.input_dim,
            self.output_dim,
            self.hidden_layers,
            self.dropout_rate
        )
        model.load_state_dict(torch.load(model_path, map_location="cpu"))
        model.eval()
        return model

    def predict(self, x, model_path: str):
        """
        Raw features → prediction

        Parameters:
            x          : pd.DataFrame ya numpy array
            model_path : path to .pth file

        Returns:
            numpy array of predictions
        """
        # preprocess
        x_scaled = self.preprocessor.transform(x)
        x_tensor = torch.FloatTensor(x_scaled)

        # load model + predict
        model = self.load_model(model_path)
        with torch.no_grad():
            output     = model(x_tensor)
            prediction = torch.argmax(output, dim=1)

        return prediction.numpy()
```

---

### NEW ARTIFACT (add to artifact_entity.py)

```python
@dataclass
class DLModelTrainerArtifact:
    trained_model_file_path: str    # model.pth path
    preprocessor_file_path:  str    # preprocessing.pkl path
    train_loss:   float
    val_loss:     float
    val_accuracy: float
    epochs_trained: int             # early stopping se kam ho sakta hai
    best_epoch:     int
```

---

### requirements.txt additions (DL)

```
# PyTorch (CPU — GPU ke liye alag install command)
torch
torchvision

# OR TensorFlow
tensorflow

# Common DL utils
tensorboard    ← optional (MLflow use kar rahe ho toh skip)
```

---


---

### DL SPECIFIC BUGS TO ADD IN COMMON BUGS SECTION

```python
# 10. optimizer.zero_grad() missing
output = model(x)
loss.backward()
optimizer.step()              # ❌ gradients accumulate

optimizer.zero_grad()         # ✅ reset before each batch
output = model(x)
loss.backward()
optimizer.step()

# 11. model.eval() missing on validation
for X, y in val_loader:
    output = model(X)         # ❌ dropout still active

model.eval()                  # ✅ dropout disabled
with torch.no_grad():
    output = model(X)

# 12. torch.no_grad() missing
output = model(x)             # ❌ gradient graph builds → memory waste
with torch.no_grad():
    output = model(x)         # ✅ no gradient computation

# 13. saving last epoch not best
torch.save(model.state_dict(), path)  # ❌ at end of loop
# inside loop:
if val_loss < best_val_loss:
    torch.save(model.state_dict(), path)  # ✅ save best

# 14. shuffle test loader
DataLoader(test_dataset, shuffle=True)   # ❌ evaluation order changes
DataLoader(test_dataset, shuffle=False)  # ✅ consistent evaluation

# 15. tensor device mismatch
x = x.to("cuda")
model = NeuralNet()           # ❌ model still on CPU
model = NeuralNet().to(device)  # ✅ same device
```