# To see the System Architecture Read the Pdf "NetworkSecurity_System_Architecture" in the root folder
# to see Data Ingestion Strucure -->> 2_data_ingestion.png located in this folder


# ═══════════════════════════════════════════════════════════════════
# networksecurity/components/data_ingestion.py
# ═══════════════════════════════════════════════════════════════════
# MongoDB se data pull karta hai → feature store mein save karta hai
# → train/test split karta hai → DataIngestionArtifact return karta hai
#
# PEHLE TEEN PROJECTS SE FARQ:
# Student Performance → pd.read_csv(local file)
# Heart Disease       → pd.read_csv(local file)
# SMS Spam            → pd.read_csv(local file)
# Network Security    → MongoDB Atlas se data pull ← YEH NAYI CHEEZ
#
# FLOW:
# MongoDB Atlas
#       ↓ export_collection_as_dataframe()
#   DataFrame (raw data)
#       ↓ export_data_into_feature_store()
#   feature_store/phishingData.csv  ← raw backup
#       ↓ split_data_as_train_test_split()
#   ingested/train.csv + test.csv
#       ↓ initiate_data_ingestion()
#   DataIngestionArtifact → DataValidation ko pass hoga
#
###==============================================================

"""
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
=================================================================
### IMP:: FILE STRUCTURE
==================================================================
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

1:Constants/taraining_pipeline/__init__.py ::: Is file mai Saary COMMON Variables k naam likhy h 

2:entity/config_entity.py :: is file mai directory structure k hisab sy Saary Paths defined h

3:entity/artifact_entity :: is me artifacts ( RETURN VALUES ) aik file/class kon kon si cheezein return karega woh defined h -->> We can say Outputs of a file
                            pipeline mai aik file ka Output usky next file ka input Hota h
                            e.g data_ingestion file k artifacts ( Outputs ) data_validation k inputs h
                            same data_validation k artifacts ( Outputs ) data_transformation k inputs honge

4: utils/main_utils/utils.py :: is file mai saary wo methods defined h jo multiple files mai use honge

5:loggin/logger.py :: logging defined h 
6: exception/exception.py :: exception defined h 
 
"""

"""
config_entity.py
- DataIngestionConfig → sab paths yahan se aate hain
  ├── feature_store_file_path → "Artifacts/timestamp/data_ingestion/feature_store/phishingData.csv"
  ├── training_file_path      → "Artifacts/timestamp/data_ingestion/ingested/train.csv"
  ├── testing_file_path       → "Artifacts/timestamp/data_ingestion/ingested/test.csv"
  ├── train_test_split_ratio  → 0.2
  ├── collection_name         → "NetworkData"
  └── database_name           → "ALYAN"
"""
"""
artifact_entity.py
- DataIngestionArtifact → yeh file return karti hai
  ├── train_file_path → "Artifacts/timestamp/data_ingestion/ingested/train.csv"
  └── test_file_path  → "Artifacts/timestamp/data_ingestion/ingested/test.csv"
"""
"""
constants/training_pipeline/__init__.py
- sab raw values yahan se aate hain
  TARGET_COLUMN, FILE_NAME, TRAIN_FILE_NAME etc.
"""
"""
ARTIFACTS DIRECTORY STRUCTURE:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Artifacts/                              ← ARTIFACT_DIR
└── 08_24_2026_14_32_00/               ← timestamp (har run alag)
    └── data_ingestion/                ← DATA_INGESTION_DIR_NAME
        ├── feature_store/             ← DATA_INGESTION_FEATURE_STORE_DIR
        │   └── phishingData.csv       ← FILE_NAME
        │       raw MongoDB data       ← split se pehle backup
        │       (148000+ rows)
        └── ingested/                  ← DATA_INGESTION_INGESTED_DIR
            ├── train.csv              ← TRAIN_FILE_NAME (80%)
            └── test.csv               ← TEST_FILE_NAME  (20%)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
"""
ENTRY POINT (main.py se)
        │
        ▼
┌─────────────────────────────────────────────────────┐
│                 DATA INGESTION                       │
│                                                      │
│  DataIngestionConfig (config_entity.py se)           │
│  ├── feature_store_file_path                         │
│  ├── training_file_path                              │
│  ├── testing_file_path                               │
│  ├── train_test_split_ratio = 0.2                    │
│  ├── collection_name = "NetworkData"                 │
│  └── database_name = "ALYAN"                         │
│                                                      │
│  DataIngestion.__init__(data_ingestion_config)       │
│  └── self.data_ingestion_config = config             │
│                                                      │
│  export_collection_as_dataframe()                    │
│  ├── MongoDB connect karo                            │
│  ├── collection.find() → list of dicts               │
│  ├── pd.DataFrame(list) → DataFrame                 │
│  ├── _id column drop karo                            │
│  ├── "na" → np.nan replace karo                      │
│  └── return df (148000+ rows)                        │
│                                                      │
│  export_data_into_feature_store(df)                  │
│  ├── feature_store_file_path nikalo config se        │
│  ├── os.makedirs() → folder banao                    │
│  ├── df.to_csv(feature_store_path)                   │
│  └── return df                                       │
│                                                      │
│  split_data_as_train_test_split(df)                  │
│  ├── train_test_split(df, 0.2)                       │
│  ├── os.makedirs(ingested/) → folder banao           │
│  ├── train_set.to_csv(training_file_path)            │
│  └── test_set.to_csv(testing_file_path)              │
│                                                      │
│  initiate_data_ingestion()                           │
│  ├── export_collection_as_dataframe()                │
│  ├── export_data_into_feature_store()                │
│  ├── split_data_as_train_test_split()                │
│  └── return DataIngestionArtifact(                   │
│            train_file_path,                          │
│            test_file_path)          ◄── KEY          │
└─────────────────────────────────────────────────────┘
        │
        │  DataIngestionArtifact
        │  ├── train_file_path = "Artifacts/.../ingested/train.csv"
        │  └── test_file_path  = "Artifacts/.../ingested/test.csv"
        │
        ▼
   DATA VALIDATION (next step)
"""
##==================================================================

import os
import sys
import numpy as np
import pandas as pd
import pymongo
import certifi
from typing import List
from sklearn.model_selection import train_test_split
from dotenv import load_dotenv

from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging
from networksecurity.entity.config_entity import DataIngestionConfig
from networksecurity.entity.artifact_entity import DataIngestionArtifact

# IMP: .env file load karo — MONGO_DB_URI wahan defined hai
# bina iske os.getenv() → None return karega
load_dotenv()

MONGO_DB_URI = os.getenv("MONGO_ATLAS_URI")
# .env mein:
# MONGO_DB_URI="mongodb+srv://alyan:pass@cluster0.xxx.mongodb.net/"


# ── MAIN CLASS ────────────────────────────────────────────────────
class DataIngestion():
    def __init__(self, data_ingestion_config: DataIngestionConfig):
        """
        DataIngestion class initialize karta hai.
        Config inject hota hai — paths aur settings config se milti hain

        Parameters:
            data_ingestion_config (DataIngestionConfig):
                config_entity.py se aata hai
                paths, split ratio, MongoDB info sab yahan

        IMP: PEHLE TEEN PROJECTS MEIN:
            self.ingestion_config = DataIngestionConfig()  ← khud banata tha
            YAHAN:
            config BAHAR se inject hota hai → testing easy → MLOps pattern
        """
        try:
            self.data_ingestion_config = data_ingestion_config
            logging.info("DataIngestion initialized with config")
        except Exception as e:
            raise NetworkSecurityException(e, sys)

    def export_collection_as_dataframe(self):
        """
        MongoDB Atlas se poora collection padhta hai aur DataFrame banata hai.

        MONGODB → DATAFRAME CONVERSION:
        ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        MongoDB mein data documents ke roop mein hota hai:
        [
            {"feature1": 1, "feature2": 0, "Result": 1,  "_id": ObjectId("...")},
            {"feature1": 0, "feature2": 1, "Result": -1, "_id": ObjectId("...")},
            ...
        ]

        collection.find() → sab documents nikalo (cursor)
        list(collection.find()) → Python list of dicts
        pd.DataFrame(list(...)) → DataFrame

        | feature1 | feature2 | Result | _id        |
        | 1        | 0        | 1      | ObjectId.. |
        | 0        | 1        | -1     | ObjectId.. |

        Phir _id drop karo → clean DataFrame:
        | feature1 | feature2 | Result |
        | 1        | 0        | 1      |
        | 0        | 1        | -1     |

        Returns:
            df (pd.DataFrame) : clean DataFrame — NaN values replace ki hain
        """
        try:
            database_name   = self.data_ingestion_config.database_name
            collection_name = self.data_ingestion_config.collection_name
            logging.info(f"Connecting to MongoDB: {database_name}.{collection_name}")

            # IMP: certifi.where() → SSL certificate verify karne ke liye
            # Arch Linux + OpenSSL issue fix
            self.mongo_client = pymongo.MongoClient(
                    MONGO_DB_URI,
                    tlsCAFile=certifi.where(),
                    tlsAllowInvalidCertificates=True,
                    serverSelectionTimeoutMS=60000,
                    connectTimeoutMS=60000,
                    socketTimeoutMS=60000
                )

            # database → collection select karo
            collection = self.mongo_client[database_name][collection_name]
            # self.mongo_client["ALYAN"]["NetworkData"]

            # ── MONGODB → DATAFRAME ───────────────────────────────
            # collection.find() → sab documents ka cursor
            # list()            → cursor → Python list of dicts
            # pd.DataFrame()    → list of dicts → DataFrame
            df = pd.DataFrame(list(collection.find()))
            logging.info(f"Data fetched from MongoDB — Shape: {df.shape}")

            # IMP: MongoDB har document mein "_id" field add karta hai
            # yeh ObjectId hota hai — ML mein useless
            # drop karo warna scaler/model crash karega
            if "_id" in df.columns.to_list():
                df = df.drop("_id", axis=1)
                logging.info("Dropped _id column")

            # IMP: MongoDB mein missing values "na" string ke roop mein hain
            # np.nan mein convert karo → sklearn imputer samjhega
            df.replace({"na": np.nan}, inplace=True)
            logging.info(f"Replaced 'na' strings with NaN — Shape: {df.shape}")

            return df

        except Exception as e:
            raise NetworkSecurityException(e, sys)

    def export_data_into_feature_store(self, dataframe: pd.DataFrame):
        """
        Raw DataFrame ko feature store mein CSV ke roop mein save karta hai.
        Yeh split se PEHLE raw data ka backup hai.

        WHY FEATURE STORE?
        MongoDB data → feature store CSV → split → train/test
        Agar baad mein phir split karni ho → MongoDB se dubara pull nahi karna
        Feature store se directly karo → fast + offline possible

        Parameters:
            dataframe (pd.DataFrame) : export_collection_as_dataframe() se aaya

        Returns:
            dataframe (pd.DataFrame) : same DataFrame — chain ke liye
        """
        try:
            feature_store_file_path = self.data_ingestion_config.feature_store_file_path
            # → "Artifacts/08_24_2026_14_32_00/data_ingestion/feature_store/phishingData.csv"

            # IMP: os.path.dirname → sirf folder path nikalo
            # "Artifacts/.../feature_store/phishingData.csv"
            # → "Artifacts/.../feature_store"
            dir_path = os.path.dirname(feature_store_file_path)
            os.makedirs(dir_path, exist_ok=True)
            logging.info(f"Feature store directory created: {dir_path}")

            dataframe.to_csv(feature_store_file_path, index=False, header=True)
            logging.info(f"Raw data saved to feature store: {feature_store_file_path}")

            return dataframe

        except Exception as e:
            raise NetworkSecurityException(e, sys)

    def split_data_as_train_test(self, dataframe: pd.DataFrame):
        """
        DataFrame ko 80/20 split karta hai aur save karta hai.

        Parameters:
            dataframe (pd.DataFrame) : feature store wala clean data

        Returns:
            None — directly files save karta hai
                   paths config mein already hain
        """
        try:
            logging.info("Train/Test split started")

            # IMP: test_size parameter format sahi karo
            train_set, test_set = train_test_split(
                dataframe,
                test_size=self.data_ingestion_config.train_test_split_ratio
            )
            logging.info(f"Split done — Train: {train_set.shape} | Test: {test_set.shape}")

            # ingested/ folder banao
            dir_path = os.path.dirname(self.data_ingestion_config.training_file_path)
            os.makedirs(dir_path, exist_ok=True)
            logging.info(f"Ingested directory created: {dir_path}")

            # train save karo
            train_set.to_csv(
                self.data_ingestion_config.training_file_path,
                index=False, header=True
            )
            logging.info(f"Train saved: {self.data_ingestion_config.training_file_path}")

            # test save karo
            test_set.to_csv(
                self.data_ingestion_config.testing_file_path,
                index=False, header=True
            )
            logging.info(f"Test saved: {self.data_ingestion_config.testing_file_path}")

        except Exception as e:
            raise NetworkSecurityException(e, sys)

    def initiate_data_ingestion(self):
        """
        DataIngestion ka main entry point.
        Sab teen functions chain karta hai aur artifact return karta hai.

        Returns:
            DataIngestionArtifact:
                ├── train_file_path → "Artifacts/.../ingested/train.csv"
                └── test_file_path  → "Artifacts/.../ingested/test.csv"

        IMP: PEHLE TEEN PROJECTS MEIN:
            return (train_path, test_path)  ← simple tuple
            YAHAN:
            return DataIngestionArtifact(...)  ← typed object
            → DataValidation ko type-safe pass hoga
        """
        try:
            logging.info("Entered Data Ingestion Method")

            # Step 1: MongoDB → DataFrame
            dataframe = self.export_collection_as_dataframe()

            # Step 2: DataFrame → feature store CSV (raw backup)
            dataframe = self.export_data_into_feature_store(dataframe)

            # Step 3: DataFrame → train/test split → save
            self.split_data_as_train_test(dataframe)

            # Step 4: Artifact banao — typed return object
            data_ingestion_artifact = DataIngestionArtifact(
                train_file_path=self.data_ingestion_config.training_file_path,
                test_file_path=self.data_ingestion_config.testing_file_path
            )

            logging.info(f"Data Ingestion completed — Artifact: {data_ingestion_artifact}")
            return data_ingestion_artifact

        except Exception as e:
            raise NetworkSecurityException(e, sys)


# ─────────────────────────────────────────────────────────────────
# DRY RUN — initiate_data_ingestion()
#
# config = DataIngestionConfig(TrainingPipelineConfig())
# obj = DataIngestion(config)
# artifact = obj.initiate_data_ingestion()
#
# 1. export_collection_as_dataframe()
#       MongoClient("ALYAN")["NetworkData"].find()
#       → list of 148000+ dicts
#       → pd.DataFrame → 148000 × 31 cols
#       → drop _id → 148000 × 30
#       → "na" → NaN
#       → return df
#
# 2. export_data_into_feature_store(df)
#       mkdir "Artifacts/timestamp/data_ingestion/feature_store/"
#       df.to_csv("...feature_store/phishingData.csv")
#       → return df
#
# 3. split_data_as_train_test(df)
#       train_test_split(df, test_size=0.2)
#       → train = 118400 rows
#       → test  =  29600 rows
#       mkdir "Artifacts/timestamp/data_ingestion/ingested/"
#       train.to_csv("...ingested/train.csv")
#       test.to_csv("...ingested/test.csv")
#
# 4. DataIngestionArtifact(
#       train_file_path = "Artifacts/.../ingested/train.csv",
#       test_file_path  = "Artifacts/.../ingested/test.csv"
#    )
#
# Disk pe ban gaya:
# Artifacts/
# └── 08_24_2026_14_32_00/
#     └── data_ingestion/
#         ├── feature_store/
#         │   └── phishingData.csv  (148000 rows — raw backup)
#         └── ingested/
#             ├── train.csv         (118400 rows)
#             └── test.csv          ( 29600 rows)
# ─────────────────────────────────────────────────────────────────
