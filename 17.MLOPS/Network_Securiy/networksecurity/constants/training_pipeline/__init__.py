# ═══════════════════════════════════════════════════════════════════
# networksecurity/constants/training_pipeline/__init__.py
# ═══════════════════════════════════════════════════════════════════
# Poore project mein use hone wale SAB constants yahan hain
# Koi bhi hardcoded value file mein nahi hogi — sab yahan se aayegi
#
# WHY CONSTANTS FOLDER?
# Pehle teen projects mein:
#   Student Performance → paths data_ingestion.py mein hardcode the
#   Heart Disease       → same — har file mein apni paths
#   SMS Spam            → same — utils.py mein values directly
#
# Yahan (MLOps style):
#   Sab values EK JAGAH — constants/training_pipeline/__init__.py
#   Koi bhi file import karke use kare
#   Path change karna ho → sirf yahan aao — poora project update
#
# IMP: __init__.py isliye — taaki
#      "from networksecurity.constants import training_pipeline"
#      kaam kare — yeh folder ek Python package ban jaata hai
###==============================================================

import os
import sys
import pandas as pd
import numpy as np

# ─────────────────────────────────────────────────────────────────
# COMMON CONSTANTS — poore pipeline mein use honge
# ─────────────────────────────────────────────────────────────────

TARGET_COLUMN = "Result"
# dataset mein yeh column predict karna hai
# phishing = 1, legitimate = -1

PIPELINE_NAME = "NetworkSecurity"
# pipeline ka naam — artifacts folder structure mein use hoga

ARTIFACT_DIR = "Artifacts"
# IMP: root folder — sab pipeline outputs yahan save honge
# timestamped subfolders honge:
# Artifacts/
# └── 08_24_2026_14_32_00/   ← har run ka alag folder
#     ├── data_ingestion/
#     ├── data_validation/
#     ├── data_transformation/
#     └── model_trainer/
#
# PEHLE TEEN PROJECTS MEIN:
# artifacts/ → sab kuch overwrite hota tha har run pe
# YAHAN:
# Artifacts/timestamp/ → har run ka alag folder
# → full run history maintain hoti hai → MLOps best practice

FILE_NAME = "phishingData.csv"
# feature store mein save hone wali raw file ka naam

TRAIN_FILE_NAME = "train.csv"
TEST_FILE_NAME  = "test.csv"
# split ke baad train/test files ke naam

SCHEMA_FILE_PATH = os.path.join("data_schema", "schema.yaml")

SAVED_MODEL_DIR = os.path.join("saved_models")
MODEL_FILE_NAME = "model.pkl"


# ─────────────────────────────────────────────────────────────────
# DATA INGESTION CONSTANTS
# prefix: DATA_INGESTION_ → easily identify karo kahan use hoga
# ─────────────────────────────────────────────────────────────────

DATA_INGESTION_COLLECTION_NAME:  str   = "NetworkData"
# MongoDB collection naam — pushdata.py ne yahan data daala tha
# DataIngestion yahan se pull karega

DATA_INGESTION_DATABASE_NAME:    str   = "ALYAN"
# MongoDB database naam

DATA_INGESTION_DIR_NAME:         str   = "data_ingestion"
# artifact subfolder naam
# path banega: Artifacts/timestamp/data_ingestion/

DATA_INGESTION_FEATURE_STORE_DIR: str  = "feature_store"
# raw data yahan save hoga
# path: Artifacts/timestamp/data_ingestion/feature_store/phishingData.csv
# IMP: feature store = raw data ka backup — split se pehle

DATA_INGESTION_INGESTED_DIR:     str   = "ingested"
# split ke baad train/test yahan save honge
# path: Artifacts/timestamp/data_ingestion/ingested/train.csv
#       Artifacts/timestamp/data_ingestion/ingested/test.csv

DATA_INGESTION_TRAIN_TEST_SPLIT_RATIO: float = 0.2
# 80% train, 20% test






# ─────────────────────────────────────────────────────────────────
# DATA Validation CONSTANTS
# prefix: DATA_VALIDATION_ → easily identify karo kahan use hoga
# ─────────────────────────────────────────────────────────────────

DATA_VALIDATON_DIR_NAME:               str = "data_validation"
# Artifacts/timestamp/data_validation/
# IMP: typo intentional rakha (tumhara code DATA_VALIDATON hai not VALIDATION)
# config_entity.py mein same naam use hota hai

DATA_VALIDATION_VALID_DIR:             str = "validated"
# valid data yahan save hoga
# Artifacts/timestamp/data_validation/validated/train.csv
# Artifacts/timestamp/data_validation/validated/test.csv
# IMP: DataTransformation yahan se padhega

DATA_VALIDATION_INVALID_DIR:           str = "invalid"
# drift ya invalid data yahan
# Artifacts/timestamp/data_validation/invalid/train.csv
# Artifacts/timestamp/data_validation/invalid/test.csv

DATA_VALIDATION_DRIFT_REPORT_DIR:      str = "drift_report"
# KS test report folder
# Artifacts/timestamp/data_validation/drift_report/

DATA_VALIDATION_DRIFT_REPORT_FILE_NAME: str = "report.yaml"
# KS test results yahan save honge
# Artifacts/timestamp/data_validation/drift_report/report.yaml




# ─────────────────────────────────────────────────────────────────
# DATA Validation Transformation 
# prefix: DATA_Transformation_ → easily identify karo kahan use hoga
# ─────────────────────────────────────────────────────────────────
DATA_TRANSFORMATION_DIR_NAME:              str = "data_transformation"
# Artifacts/timestamp/data_transformation/

DATA_TRANSFORMATION_TRANSFORMED_DATA_DIR:  str = "transformed"
# numpy arrays yahan:
# Artifacts/timestamp/data_transformation/transformed/train.npy
# Artifacts/timestamp/data_transformation/transformed/test.npy

DATA_TRANSFORMATION_TRANSFORMED_OBJECT_DIR: str = "transformed_object"
# preprocessor pkl yahan:
# Artifacts/timestamp/data_transformation/transformed_object/preprocessing.pkl

PREPROCESSING_OBJECT_FILE_NAME: str = "preprocessing.pkl"
# fitted KNNImputer — DataTransformationConfig mein use hota hai
# predict_pipeline mein load hoga naye data transform karne ke liye

#Knn Imputer to replace nan Values
DATA_TRANSFORMATION_IMPUTER_PARAMS: dict = {
    "missing_values": np.nan,
    # IMP: kaunsi values ko missing maana jaaye
    # np.nan = NaN values → yahi replace karenge
    # DataIngestion mein humne "na" strings → np.nan kiya tha
    # ab KNNImputer in NaN values ko fill karega

    "n_neighbors": 3,
    # KNN Imputer — KNN (K-Nearest Neighbors) use karta hai missing values fill karne ke liye
    # n_neighbors=3 → 3 nearest neighbors dhundho
    # missing value = in 3 neighbors ka average
    #
    # Example:
    # Row mein "port" column NaN hai
    # Similar 3 rows dhundho (baaki features ke basis pe)
    # Un 3 rows ka "port" value average karo → NaN fill karo
    #
    # WHY KNN IMPUTER (not SimpleImputer)?
    # SimpleImputer → sirf median/mean use karta hai (global)
    # KNNImputer    → similar rows dekh ke fill karta hai (local)
    # Network security data mein features correlated hain
    # similar network patterns similar values rakhte hain
    # → KNN zyada accurate fill karta hai

    "weights": "uniform"
    # IMP: "weights" (plural) → "weight" galat hai → bug fix karo
    # 3 neighbors mein se har ek ko kitna importance do
    #
    # "uniform"  → sab neighbors ko equal weight
    #              avg(neighbor1, neighbor2, neighbor3)
    #
    # "distance" → paas wale neighbor ko zyada weight
    #              closer neighbor → more influence
    #
    # "uniform" kyun choose kiya?
    # is dataset mein binary/categorical features hain (0, 1, -1)
    # distance-based weighting zyada farak nahi karta
    # simple aur fast → uniform better choice
}

# IMP: DataTransformation mein use hoga:
# from networksecurity.constants.training_pipeline import DATA_TRANSFORMATION_IMPUTER_PARAMS
#
# imputer = KNNImputer(**DATA_TRANSFORMATION_IMPUTER_PARAMS)
# → KNNImputer(missing_values=np.nan, n_neighbors=3, weights="uniform")
#
# ** = dict unpack → key-value pairs → function arguments ban jaate hain





# ─────────────────────────────────────────────────────────────────
# MODEL TRAINER CONSTANTS
# prefix: MODEL_TRAINER_ → easily identify karo kahan use hoga
# ─────────────────────────────────────────────────────────────────

MODEL_TRAINER_DIR_NAME: str = "model_trainer"
# Artifacts/timestamp/model_trainer/

MODEL_TRAINER_TRAIN_MODEL_DIR: str = "trained_model"
# Artifacts/timestamp/model_trainer/trained_model/

MODEL_TRAINER_TRAINED_MODEL_NAME: str = "model.pkl"
# Artifacts/timestamp/model_trainer/trained_model/model.pkl
# PredictPipeline load karega yahan se

MODEL_TRAINER_EXPECTED_SCORE: float = 0.6
# IMP: minimum acceptable accuracy
# agar best model bhi 0.6 se kam → pipeline rok do

MODEL_TRAINER_OVERFITTING_UNDER_FITTING_THRESHOLD: float = 0.05
# IMP: train score - test score > 0.05 → overfitting
#      test score  - train score > 0.05 → underfitting
# dono cases mein model reject karo
# Example:
#   train accuracy = 0.95, test accuracy = 0.70
#   difference = 0.25 > 0.05 → OVERFITTING → reject






# ─────────────────────────────────────────────────────────────────
# MODEL PUSHER CONSTANT
# Pushing Models to HuggingFace
# ─────────────────────────────────────────────────────────────────
# constants/training_pipeline/__init__.py mein add karo
HF_REPO_ID:   str = "alyan-ktk/networksecurity-mlops"
HF_REPO_TYPE: str = "model"
HF_MODEL_DIR: str = "final_model/"