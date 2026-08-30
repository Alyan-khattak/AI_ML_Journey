# ═══════════════════════════════════════════════════════════════════
# pushdata.py
# ═══════════════════════════════════════════════════════════════════
# ETL Script — Extract Transform Load
# CSV file se data padhta hai → JSON mein convert karta hai →
# MongoDB Atlas mein push karta hai
#
# YEH SIRF EK BAAR CHALTA HAI — data push karne ke liye
# Production mein data MongoDB mein hota hai
# DataIngestion wahan se pull karega
#
# FLOW:
# phisingData.csv → csv_to_json_converter() → records (list of dicts)
#                                                    ↓
#                              insert_data_to_mongodb() → MongoDB Atlas
###==============================================================

import os
import sys
import json
import pymongo

from dotenv import load_dotenv

# IMP: load_dotenv() → .env file padhta hai aur env variables set karta hai
# bina iske os.getenv() → None return karega
load_dotenv()

MONGO_ATLAS_URI = os.getenv("MONGO_ATLAS_URI")
# .env file mein:
# MONGO_ATLAS_URI="mongodb+srv://alyan:pass@cluster0.xxx.mongodb.net/"

import certifi                  # python package for secure HTTPS connections
ca = certifi.where()            # Certificate Authorities file ka path
                                # SSL handshake ke liye zaroori
# → "/path/to/cacert.pem"
# yeh ek file hai jisme 150+ trusted authorities ki list hai
# Mozilla ne banai hai yeh list
# same jo Chrome/Firefox use karta hai
# certifi = Python ko batata hai kaunsi websites trustworthy hain
# bina iske Python secure connections verify nahi kar sakta                                

import pandas as pd
import numpy as np

from networksecurity.logging.logger import logging
from networksecurity.exception.exception import NetworkSecurityException


# ── CLASS: NetworkDataExtract ─────────────────────────────────────
# Kaam: CSV se data nikalna aur MongoDB mein daalna
# Do methods:
# 1. csv_to_json_converter() → CSV → JSON records
# 2. insert_data_to_mongodb() → records → MongoDB
class NetworkDataExtract():
    def __init__(self):
        pass

    def csv_to_json_converter(self, filepath):
        """
        CSV file ko JSON records ki list mein convert karta hai.
        MongoDB documents ki format mein — har row ek dict ban jaati hai.

        Parameters:
            filepath (str) : CSV file ka path
                             e.g. "Network_Data/phisingData.csv"

        Returns:
            records (list of dict) : har row ek dictionary
                e.g. [{"feature1": 1, "feature2": 0, "Result": 1},
                      {"feature1": 0, "feature2": 1, "Result": -1}, ...]

        WHY JSON?
        MongoDB documents JSON format mein store hote hain
        CSV → DataFrame → JSON → MongoDB
        """
        try:
            # CSV padhna → DataFrame banao
            data = pd.read_csv(filepath)
            logging.info(f"CSV loaded — Shape: {data.shape}")

            # IMP: index reset karo — clean JSON ke liye
            data.reset_index(drop=True, inplace=True)

            # ── CSV → JSON CONVERSION ─────────────────────────────
            # data.T → DataFrame transpose karo (rows ↔ columns)
            # .to_json() → JSON string banao
            # json.loads() → Python dict mein convert
            # .values() → sirf values nikalo (keys = row indices)
            # list() → final list of dicts

            # Example:
            # Original DataFrame:
            #    A   B   C
            #    10  20  25   ← row 0
            #    30  40  50   ← row 1
            #
            # After .T:
            #    0   1
            # A  10  30
            # B  20  40
            # C  25  50
            #
            # After to_json():
            # {"0": {"A": 10, "B": 20, "C": 25},
            #  "1": {"A": 30, "B": 40, "C": 50}}
            #
            # After .values():
            # [{"A": 10, "B": 20, "C": 25},
            #  {"A": 30, "B": 40, "C": 50}]
            records = list(json.loads(data.T.to_json()).values())

            logging.info(f"Converted {len(records)} records to JSON")
            return records

        except Exception as e:
            raise NetworkSecurityException(e, sys)

    def insert_data_to_mongodb(self, records, database, collection):
        """
        JSON records ko MongoDB Atlas mein insert karta hai.

        Parameters:
            records    (list of dict) : csv_to_json_converter() se aaya data
            database   (str)          : MongoDB database naam e.g. "ALYAN"
            collection (str)          : MongoDB collection naam e.g. "NetworkData"

        Returns:
            None — sirf insert karta hai

        MongoDB structure:
        Database → Collections → Documents
        ALYAN    → NetworkData → {feature1: 1, feature2: 0, Result: 1}
                                 {feature1: 0, feature2: 1, Result: -1}
                                 ... (148000+ rows)
        """
        try:
            # IMP: certifi.where() — SSL certificate verify karne ke liye
            self.mongo_client = pymongo.MongoClient(
                MONGO_ATLAS_URI,
                tlsCAFile=certifi.where(),
                tlsAllowInvalidCertificates=True
            )

            # database select karo — agar exist nahi karta → MongoDB khud banayega
            self.database   = self.mongo_client[database]

            # collection select karo — agar exist nahi karta → MongoDB khud banayega
            self.collection = self.database[collection]

            # IMP: insert_many() → ek baar mein sab records insert
            # insert_one() → ek ek karte → slow
            self.collection.insert_many(records)

            logging.info(f"Inserted {len(records)} records into {database}.{collection}")

        except Exception as e:
            raise NetworkSecurityException(e, sys)


# ── ENTRY POINT ───────────────────────────────────────────────────
if __name__ == "__main__":

    FILE_PATH  = "/home/aizen/ML_Projects/Network_Securiy/Network_Data/phisingData.csv"
    DATABASE   = "ALYAN"
    COLLECTION = "NetworkData"

    # Step 1: object banao
    networkobj = NetworkDataExtract()

    # Step 2: CSV → JSON records
    records = networkobj.csv_to_json_converter(filepath=FILE_PATH)
    print(f"Total records converted: {len(records)}")

    # Step 3: MongoDB mein push karo
    networkobj.insert_data_to_mongodb(
        records=records,
        database=DATABASE,
        collection=COLLECTION
    )
    print("Data pushed to MongoDB successfully!")


## TO see this Data in the MongoDB ATLAS
## On Left Side Bar in DataBase Section Click ON DataExplorer 
## THen Cluster0 -> Ur database name ( mine ALYAN ) -> expand to ur collection

# ─────────────────────────────────────────────────────────────────
# ETL PIPELINE — EXPLANATION
# ─────────────────────────────────────────────────────────────────
#
# ETL = Extract → Transform → Load
#
# ── E: EXTRACT ────────────────────────────────────────────────────
# Source se raw data nikalna
# Yahan: phisingData.csv → pd.read_csv()
# Production mein: database, API, S3, data warehouse etc.
# Kaam: raw data as-is lena — koi changes nahi
#
# ── T: TRANSFORM ──────────────────────────────────────────────────
# Raw data ko usable format mein convert karna
# Yahan: DataFrame → JSON records (list of dicts)
# data.T.to_json() → transpose → JSON string
# json.loads().values() → Python list of dicts
# Kaam: CSV rows → MongoDB documents format
#
# ── L: LOAD ───────────────────────────────────────────────────────
# Transformed data ko destination mein daalna
# Yahan: records → MongoDB Atlas (cloud database)
# insert_many() → ek saath sab records
# Kaam: data production database mein jaata hai
#
# ── WHY ETL? ──────────────────────────────────────────────────────
# CSV file directly production mein use nahi karte:
#
# CSV problems:
# ├── Local file — server pe nahi hoti
# ├── Version control mein large files → slow
# ├── Multiple users access nahi kar sakte
# └── No query support
#
# MongoDB advantages:
# ├── Cloud pe — koi bhi access kar sakta hai
# ├── DataIngestion.py wahan se pull karega
# ├── Scale hota hai — crores of records
# ├── Real-time updates possible
# └── MLOps pipeline ke liye standard approach
#
# ── FLOW IN THIS PROJECT ──────────────────────────────────────────
#
# pushdata.py (EK BAAR):
# phisingData.csv → JSON → MongoDB Atlas
#
# Training Pipeline (har baar train karo):
# MongoDB Atlas → DataIngestion → CSV artifacts/
#              → DataValidation → validate
#              → DataTransformation → numpy arrays
#              → ModelTrainer → model.pkl
#              → MLflow → metrics track
#
# ─────────────────────────────────────────────────────────────────