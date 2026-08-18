# ═══════════════════════════════════════════════════════════════════
# data_ingestion.py  — UPDATED VERSION
# ═══════════════════════════════════════════════════════════════════
# Notebook ka kaam (data padhna + train/test split) ko production-ready code mein convert karta hai.
# CI/CD pipeline mein linearly flow karta hai — koi manual step nahi.

###==============================================================

"""

- This File Reads data from some source
- Split it in Train set and Test set 
    - save raw, train, test data in artifact folder 
- return train and test data set path via initiate_data_ingestion function
- these path are given to then :: initiate_data_transformation(self, train_path, test_path):


"""


"""
data_transformation.py

- via --.>initiate_data_transformation(self, train_path, test_path): get train and test dataset paths that are given by data_ingestion.py
- split that data in X_train, y_train, X_test, y_test
- make a preprocessor objject for standarzation
- apply Standard scaler and transfom featurs  via preprocessor obj
- save the preprocessor obj



"""

"""
ENTRY POINT
python data_ingestion.py
        │
        ▼
┌─────────────────────────────────────────────────────┐
│                   DATA INGESTION                     │
│                                                      │
│  DataIngestionConfig (dataclass)                     │
│  ├── train_data_path = "artifacts/train.csv"         │
│  ├── test_data_path  = "artifacts/test.csv"          │
│  └── raw_data_path   = "artifacts/raw.csv"           │
│                                                      │
│  DataIngestion.__init__()                            │
│  └── self.ingestion_config = DataIngestionConfig()   │
│                                                      │
│  DataIngestion.initiate_data_ingestion()             │
│  ├── 1. pd.read_csv(stud.csv)     → df (1000 rows)  │
│  ├── 2. os.makedirs(artifacts/)   → folder banta hai │
│  ├── 3. df.to_csv(raw.csv)        → backup save      │
│  ├── 4. train_test_split(df, 0.2) → 800 / 200 rows  │
│  ├── 5. train_set.to_csv(train.csv)                  │
│  ├── 6. test_set.to_csv(test.csv)                    │
│  └── 7. return ("artifacts/train.csv",               │
│                  "artifacts/test.csv")  ◄── KEY      │
└─────────────────────────────────────────────────────┘
        │
        │  return value
        │  train_data = "artifacts/train.csv"
        │  test_data  = "artifacts/test.csv"
        │
        ▼
┌─────────────────────────────────────────────────────┐
│                DATA TRANSFORMATION                   │
│                                                      │
│  DataTransformationConfig (dataclass)                │
│  └── preprocessor_object_file_path                   │
│      = "artifacts/preprocessor.pkl"                  │
│                                                      │
│  DataTransformation.__init__()                       │
│  └── self.data_transformation_config                 │
│      = DataTransformationConfig()                    │
│                                                      │
│  get_data_transformer_object()  ← called internally  │
│  ├── num_pipeline                                    │
│  │   ├── SimpleImputer(median)                       │
│  │   └── StandardScaler()                            │
│  ├── cat_pipeline                                    │
│  │   ├── SimpleImputer(most_frequent)                │
│  │   ├── OneHotEncoder()                             │
│  │   └── StandardScaler(with_mean=False)             │
│  └── ColumnTransformer(num+cat) → return preprocessor│
│                          ▲ UNFITTED blueprint        │
│                                                      │
│  initiate_data_transformation(train_data, test_data) │
│  ├── 1. pd.read_csv(train.csv)  → train_df 800 rows │
│  ├── 2. pd.read_csv(test.csv)   → test_df  200 rows │
│  ├── 3. get_data_transformer_object() → blueprint    │
│  │                                                   │
│  ├── 4. X_train = train_df.drop("math_score")       │
│  │      y_train = train_df["math_score"]             │
│  │      X_test  = test_df.drop("math_score")         │
│  │      y_test  = test_df["math_score"]              │
│  │                                                   │
│  ├── 5. preprocessor.fit_transform(X_train) ← FIT   │
│  │      preprocessor.transform(X_test)  ← NO FIT    │
│  │                                                   │
│  ├── 6. np.c_[X_train_arr, y_train] → train_arr     │
│  │      np.c_[X_test_arr,  y_test]  → test_arr      │
│  │                                                   │
│  ├── 7. save_object(preprocessor.pkl)                │
│  │                                                   │
│  └── 8. return (train_arr,                           │
│                  test_arr,                           │
│                  "artifacts/preprocessor.pkl")       │
└─────────────────────────────────────────────────────┘
        │
        ▼
   MODEL TRAINER (next step)
   train_arr, test_arr ready
   preprocessor.pkl disk pe saved


DISK PE KYA BANA:
artifacts/
├── raw.csv           ← ingestion  (1000 rows, original)
├── train.csv         ← ingestion  ( 800 rows, raw split)
├── test.csv          ← ingestion  ( 200 rows, raw split)
└── preprocessor.pkl  ← transformation (fitted pipeline)


DONO KA CONNECTION:
ingestion  → CSV files save karta hai disk pe
             paths return karta hai strings ke roop mein
transformation → woh paths leta hai
                 CSVs padhta hai
                 transform karta hai
                 numpy arrays return karta hai
                 pkl save karta hai

STRINGS (paths) IN  →  ingestion
STRINGS (paths) OUT →  transformation IN
NUMPY ARRAYS OUT    →  model trainer IN


"""
##==================================================================

import os
import sys
from src.exception import CustomException
from src.logger import logging

import pandas as pd
import numpy as np

from sklearn.model_selection import train_test_split
from dataclasses import dataclass

# ── NEW IMPORT ────────────────────────────────────────────────────
# DataTransformation aur DataTransformationConfig import kiye
# Taaki __main__ block mein ingestion ke baad transformation directly chain ho sake.
# Yeh poori pipeline ek hi script se trigger ho jaaye:
#   python data_ingestion.py → ingestion → transformation (→ aage model training)
from src.components.data_transformation import DataTransformation, DataTransformationConfig
# ──────────────────────────────────────────────────────────────────

# ── WHY @dataclass? ───────────────────────────────────────
# @dataclass decorator automatically banata hai __init__, __repr__ etc.
# Sirf variables define karo with types — baaki sab auto.
# Bina @dataclass ke yeh likhna padta:
#   class DataIngestionConfig:
#       def __init__(self):
#           self.train_data_path = os.path.join("artifacts","train.csv")
#           ...
# @dataclass ke saath sirf yeh:
#   train_data_path: str = os.path.join("artifacts","train.csv")
# ──────────────────────────────────────────────────────────

from src.components.model_trainer import ModelTrainer

@dataclass
class DataIngestionConfig:
    # Yeh class sirf PATHS store karti hai — koi logic nahi
    # artifacts/ folder mein teen files save hongi
    # os.path.join = OS-safe path banata hai (Windows/Linux dono pe kaam karta hai)

    # IMP: paths relative hain — jahan se script run hogi wahan artifacts/ banega
    train_data_path: str = os.path.join("artifacts", "train.csv")   # split ke baad train data
    test_data_path:  str = os.path.join("artifacts", "test.csv")    # split ke baad test data
    raw_data_path:   str = os.path.join("artifacts", "raw.csv")     # original data ka backup


# ── WHY TWO CLASSES? ──────────────────────────────────────
# DataIngestionConfig = sirf CONFIG (paths/settings) — data class, no logic
# DataIngestion       = sirf LOGIC (padhna, split karna, save karna)
# Separation of concerns — agar path change karna ho sirf Config chhuo,
# agar logic change karna ho sirf DataIngestion chhuo.
# ──────────────────────────────────────────────────────────

class DataIngestion:
    def __init__(self):
        # Config object banao — teen paths mil gayi
        self.ingestion_config = DataIngestionConfig()

    def initiate_data_ingestion(self):
        logging.info("Entered Data Ingestion Method")
        try:
            df = pd.read_csv("/home/aizen/AI_ML/16.Deployment/2_End_to_End_ML-deployement/Student_Performance_Indicator/Notebook/Data/stud.csv")
            logging.info("Read the Dataset as DataFrame")

            # IMP: artifacts/ folder banao agar exist nahi karta
            # os.path.dirname = path se sirf folder part nikalta hai
            #   e.g. "artifacts/train.csv" → "artifacts"
            # exist_ok=True = crash mat karo agar folder already hai
            os.makedirs(os.path.dirname(self.ingestion_config.train_data_path), exist_ok=True)
            # os.makedirs(directory_name)
            # self.ingestion_config.train_data_path = "artifacts/train.csv"
            # os.path.dirname("artifacts/train.csv") = "artifacts"
            # Bas path se file name hata ke sirf folder part nikalta hai.
            # Phir os.makedirs("artifacts") us folder ko disk pe banata hai.

            # raw data save karo — original ka backup artifacts mein
            df.to_csv(self.ingestion_config.raw_data_path, index=False, header=True)

            logging.info("Train Test Split Initiated")

            # 80/20 split
            train_set, test_set = train_test_split(df, test_size=0.2, random_state=42)

            # save train and test data
            train_set.to_csv(self.ingestion_config.train_data_path, index=False, header=True)
            test_set.to_csv(self.ingestion_config.test_data_path,   index=False, header=True)

            logging.info("Ingestion of the Data is completed")

            # IMP: train aur test paths return karo
            # Data Transformation component ko yahi paths chahiye honge next step mein
            return (
                self.ingestion_config.train_data_path,
                self.ingestion_config.test_data_path,
            )

        except Exception as e:
            raise CustomException(e, sys)


if __name__ == "__main__":
    # ── STEP 1: INGESTION ─────────────────────────────────────────
    obj = DataIngestion()
    train_data, test_data = obj.initiate_data_ingestion()
    # train_data = "artifacts/train.csv"
    # test_data  = "artifacts/test.csv"

    # ── STEP 2: TRANSFORMATION ────────────────────────────────────
    # NEW: ingestion ke turant baad transformation chain ho jaata hai
    # DataTransformation object banao
    data_transformation = DataTransformation()

    # train_data aur test_data paths pass karo — wahi jo ingestion ne return kiye
    train_array, test_array, _ = data_transformation.initiate_data_transformation(train_data, test_data)

    # IMP: yeh line chalane se poori pipeline ek saath chalti hai:
    # 1. CSV padha jaata hai
    # 2. artifacts/ mein raw/train/test save hote hain
    # 3. ColumnTransformer fit hota hai train pe
    # 4. train_arr, test_arr numpy arrays ban jaate hain
    # 5. preprocessor.pkl artifacts/ mein save ho jaata hai

    modeltrainer = ModelTrainer()
    print(modeltrainer.initiate_model_trainer(train_array, test_array))


# ─────────────────────────────────────────────────────────────────
# WHY SPLIT HERE BEFORE EDA/FE?
#
# Notebook mein:  EDA → FE → Clean → Split  (exploration ke liye theek hai)
# Production mein: Split PEHLE → phir FE/Scaling sirf train pe fit karo
#
# IMP: agar split baad mein karo toh test data ka information train mein
# leak ho sakta hai (StandardScaler, Imputer etc. poore data pe fit ho jaate)
# Yahan split pehle = test set bilkul unseen rehta hai. No leakage.
# ─────────────────────────────────────────────────────────────────

# ─────────────────────────────────────────────────────────────────
# DRY RUN — step by step
#
# 1. obj = DataIngestion()
#       __init__ chalta hai
#       self.ingestion_config = DataIngestionConfig()
#       ingestion_config.train_data_path = "artifacts/train.csv"
#       ingestion_config.test_data_path  = "artifacts/test.csv"
#       ingestion_config.raw_data_path   = "artifacts/raw.csv"
#
# 2. obj.initiate_data_ingestion()
#
#       logging.info("Entered Data Ingestion Method")
#       → log file mein likhta hai: [timestamp] - INFO - Entered Data Ingestion Method
#
#       df = pd.read_csv("stud.csv")
#       → 1000 rows, 8 columns load hoti hain
#
#       os.path.dirname("artifacts/train.csv") → "artifacts"
#       os.makedirs("artifacts", exist_ok=True) → folder banta hai disk pe
#
#       df.to_csv("artifacts/raw.csv")
#       → poora 1000 row data raw.csv mein save
#
#       train_test_split(df, test_size=0.2)
#       → train_set = 800 rows
#       → test_set  = 200 rows
#
#       train_set.to_csv("artifacts/train.csv") → 800 rows save
#       test_set.to_csv("artifacts/test.csv")   → 200 rows save
#
#       return ("artifacts/train.csv", "artifacts/test.csv")
#       → ye paths Data Transformation ko pass honge
#
# 3. data_transformation.initiate_data_transformation(train_data, test_data)
#       → ColumnTransformer fit hota hai train pe
#       → test sirf transform hota hai
#       → preprocessor.pkl save hota hai
#
# 4. Disk pe ban gaya:
#       Student_Performance_Indicator/
#       └── artifacts/
#           ├── raw.csv           (1000 rows)
#           ├── train.csv         ( 800 rows)
#           ├── test.csv          ( 200 rows)
#           └── preprocessor.pkl  (fitted ColumnTransformer)
# ─────────────────────────────────────────────────────────────────

# ─────────────────────────────────────────────────────────────────
# LOG FOLDER FIX:
# Log AI_ML/ root mein ban raha tha kyunki logger.py mein os.getcwd() use kiya tha
# aur tum AI_ML/ se script run kar rahe the.
#
# logger.py mein yeh fix karo:
#
# logs_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
#                          "..", "..", "logs", LOG_FILE)
#
# Ya simple fix — script hamesha Student_Performance_Indicator/ se run karo:
#   cd /home/aizen/AI_ML/16.Deployment/2_End_to_End_ML-deployement/Student_Performance_Indicator
#   python -u src/components/data_ingestion.py
# ─────────────────────────────────────────────────────────────────


"""
ENTRY POINT
python data_ingestion.py
        │
        ▼
┌─────────────────────────────────────────────────────┐
│                   DATA INGESTION                     │
│                                                      │
│  DataIngestionConfig (dataclass)                     │
│  ├── train_data_path = "artifacts/train.csv"         │
│  ├── test_data_path  = "artifacts/test.csv"          │
│  └── raw_data_path   = "artifacts/raw.csv"           │
│                                                      │
│  DataIngestion.__init__()                            │
│  └── self.ingestion_config = DataIngestionConfig()   │
│                                                      │
│  DataIngestion.initiate_data_ingestion()             │
│  ├── 1. pd.read_csv(stud.csv)     → df (1000 rows)  │
│  ├── 2. os.makedirs(artifacts/)   → folder banta hai │
│  ├── 3. df.to_csv(raw.csv)        → backup save      │
│  ├── 4. train_test_split(df, 0.2) → 800 / 200 rows  │
│  ├── 5. train_set.to_csv(train.csv)                  │
│  ├── 6. test_set.to_csv(test.csv)                    │
│  └── 7. return ("artifacts/train.csv",               │
│                  "artifacts/test.csv")  ◄── KEY      │
└─────────────────────────────────────────────────────┘
        │
        │  return value
        │  train_data = "artifacts/train.csv"
        │  test_data  = "artifacts/test.csv"
        │
        ▼
┌─────────────────────────────────────────────────────┐
│                DATA TRANSFORMATION                   │
│                                                      │
│  DataTransformationConfig (dataclass)                │
│  └── preprocessor_object_file_path                   │
│      = "artifacts/preprocessor.pkl"                  │
│                                                      │
│  DataTransformation.__init__()                       │
│  └── self.data_transformation_config                 │
│      = DataTransformationConfig()                    │
│                                                      │
│  get_data_transformer_object()  ← called internally  │
│  ├── num_pipeline                                    │
│  │   ├── SimpleImputer(median)                       │
│  │   └── StandardScaler()                            │
│  ├── cat_pipeline                                    │
│  │   ├── SimpleImputer(most_frequent)                │
│  │   ├── OneHotEncoder()                             │
│  │   └── StandardScaler(with_mean=False)             │
│  └── ColumnTransformer(num+cat) → return preprocessor│
│                          ▲ UNFITTED blueprint        │
│                                                      │
│  initiate_data_transformation(train_data, test_data) │
│  ├── 1. pd.read_csv(train.csv)  → train_df 800 rows │
│  ├── 2. pd.read_csv(test.csv)   → test_df  200 rows │
│  ├── 3. get_data_transformer_object() → blueprint    │
│  │                                                   │
│  ├── 4. X_train = train_df.drop("math_score")       │
│  │      y_train = train_df["math_score"]             │
│  │      X_test  = test_df.drop("math_score")         │
│  │      y_test  = test_df["math_score"]              │
│  │                                                   │
│  ├── 5. preprocessor.fit_transform(X_train) ← FIT   │
│  │      preprocessor.transform(X_test)  ← NO FIT    │
│  │                                                   │
│  ├── 6. np.c_[X_train_arr, y_train] → train_arr     │
│  │      np.c_[X_test_arr,  y_test]  → test_arr      │
│  │                                                   │
│  ├── 7. save_object(preprocessor.pkl)                │
│  │                                                   │
│  └── 8. return (train_arr,                           │
│                  test_arr,                           │
│                  "artifacts/preprocessor.pkl")       │
└─────────────────────────────────────────────────────┘
        │
        ▼
   MODEL TRAINER (next step)
   train_arr, test_arr ready
   preprocessor.pkl disk pe saved


DISK PE KYA BANA:
artifacts/
├── raw.csv           ← ingestion  (1000 rows, original)
├── train.csv         ← ingestion  ( 800 rows, raw split)
├── test.csv          ← ingestion  ( 200 rows, raw split)
└── preprocessor.pkl  ← transformation (fitted pipeline)


DONO KA CONNECTION:
ingestion  → CSV files save karta hai disk pe
             paths return karta hai strings ke roop mein
transformation → woh paths leta hai
                 CSVs padhta hai
                 transform karta hai
                 numpy arrays return karta hai
                 pkl save karta hai

STRINGS (paths) IN  →  ingestion
STRINGS (paths) OUT →  transformation IN
NUMPY ARRAYS OUT    →  model trainer IN


"""