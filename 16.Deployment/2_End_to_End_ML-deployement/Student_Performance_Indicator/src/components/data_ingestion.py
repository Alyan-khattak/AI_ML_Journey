# data_ingestion.py
# Notebook ka kaam (data padhna + train/test split) ko production-ready code mein convert karta hai.
# CI/CD pipeline mein linearly flow karta hai — koi manual step nahi.

import os
import sys
from src.exception import CustomException
from src.logger import logging

import pandas as pd
import numpy as np

from sklearn.model_selection import train_test_split
from dataclasses import dataclass


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
            #Phir os.makedirs("artifacts") us folder ko disk pe banata hai.
           
            # raw data save karo — original ka backup artifacts mein
            df.to_csv(self.ingestion_config.raw_data_path, index=False, header=True)

            logging.info("Train Test Split Initiated")

            # 80/20 split
            train_set, test_set = train_test_split(df, test_size=0.2, random_state=42)

            # save train and test da
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
    obj = DataIngestion()
    obj.initiate_data_ingestion()  


# ─────────────────────────────────────────────────────────────────────
# WHY SPLIT HERE BEFORE EDA/FE?
#
# Notebook mein:  EDA → FE → Clean → Split  (exploration ke liye theek hai)
# Production mein: Split PEHLE → phir FE/Scaling sirf train pe fit karo
#
# IMP: agar split baad mein karo toh test data ka information train mein
# leak ho sakta hai (StandardScaler, Imputer etc. poore data pe fit ho jaate)
# Yahan split pehle = test set bilkul unseen rehta hai. No leakage.
# ─────────────────────────────────────────────────────────────────────

# ─────────────────────────────────────────────────────────────────────
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
# 3. Disk pe ban gaya:
#       Student_Performance_Indicator/
#       └── artifacts/
#           ├── raw.csv    (1000 rows)
#           ├── train.csv  ( 800 rows)
#           └── test.csv   ( 200 rows)
# ─────────────────────────────────────────────────────────────────────

# ─────────────────────────────────────────────────────────────────────
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
# ─────────────────────────────────────────────────────────────────────