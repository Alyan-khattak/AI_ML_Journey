# ═══════════════════════════════════════════════════════════════════
# networksecurity/components/data_validation.py
# ═══════════════════════════════════════════════════════════════════
# DataIngestion ke baad data quality check karta hai.
# Schema validate karta hai aur data drift detect karta hai.
# Valid data ko aage DataTransformation ke liye save karta hai.
#
# WHY DATA VALIDATION?
# PEHLE TEEN PROJECTS MEIN: Data Validation NAHI THA
#   Student Performance → directly split → transform
#   Heart Disease       → directly split → transform
#   SMS Spam            → directly split → transform
#
# YAHAN (MLOps style):
#   DataValidation = data quality gate
#   Production mein data corrupt ho sakta hai:
#   ├── Missing columns → model crash karega
#   ├── Data drift → model predictions galat honge
#   └── Wrong types → preprocessing fail hoga
#   Isliye validate karo PEHLE aage jaane se
#
# FLOW:
# DataIngestionArtifact (train/test paths)
#       ↓ read_data()
# train_df, test_df
#       ↓ validate_number_cols()
# schema.yaml se expected columns → actual columns se compare
#       ↓ check_numerical_col()
# schema.yaml se expected numeric cols → actual se compare
#       ↓ detect_data_drift()
# KS test → train vs test distribution compare → report.yaml save
#       ↓ initiate_data_validation()
# DataValidationArtifact → DataTransformation ko pass hoga
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
FILES JO YEH USE KARTA HAI:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. networksecurity/entity/artifact_entity.py
   → DataIngestionArtifact  ← INPUT (DataIngestion ne banaya tha)
     ├── train_file_path = "Artifacts/.../ingested/train.csv"
     └── test_file_path  = "Artifacts/.../ingested/test.csv"

   → DataValidationArtifact ← OUTPUT (yeh return karega)
     ├── validation_status
     ├── valid_train_file_path
     ├── valid_test_file_path
     ├── invalid_train_file_path
     ├── invalid_test_file_path
     └── drift_report_file_path

2. networksecurity/entity/config_entity.py
   → DataValidationConfig ← CONFIG (paths milte hain)
     ├── data_validation_dir
     ├── valid_data_dir
     ├── invalid_data_dir
     ├── valid_train_file_path
     ├── valid_test_file_path
     ├── invalid_train_file_path
     ├── invalid_test_file_path
     └── drift_report_file_path

3. networksecurity/constants/training_pipeline/__init__.py
   → SCHEMA_FILE_PATH = "data_schema/schema.yaml"

4. networksecurity/utils/main_utils/utils.py
   → read_yaml_file()   ← schema.yaml padhne ke liye
   → write_yaml_file()  ← drift report likhne ke liye

5. data_schema/schema.yaml ← DataIngestion ne nahi banaya
   → Manually defined — expected columns aur types
   → DataValidation yeh padhta hai aur incoming data se compare karta hai
"""
"""
ARTIFACTS DIRECTORY — DATA VALIDATION KE BAAD:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Artifacts/
└── 08_24_2026_14_32_00/
    ├── data_ingestion/                    ← DataIngestion ne banaya
    │   ├── feature_store/phishingData.csv
    │   └── ingested/
    │       ├── train.csv                  ← DataValidation ka INPUT
    │       └── test.csv                   ← DataValidation ka INPUT
    │
    └── data_validation/                   ← DataValidation banayega
        ├── validated/                     ← valid data yahan
        │   ├── train.csv                  ← DataTransformation ka INPUT
        │   └── test.csv                   ← DataTransformation ka INPUT
        ├── invalid/                       ← invalid data yahan (agar drift)
        │   ├── train.csv
        │   └── test.csv
        └── drift_report/
            └── report.yaml               ← KS test results
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
"""
ENTRY POINT (main.py se)
        │
        ▼
┌─────────────────────────────────────────────────────┐
│              DATA VALIDATION                         │
│                                                      │
│  INPUT:                                              │
│  DataIngestionArtifact ← DataIngestion ne diya       │
│  ├── train_file_path = ".../ingested/train.csv"      │
│  └── test_file_path  = ".../ingested/test.csv"       │
│                                                      │
│  DataValidationConfig ← config_entity.py se          │
│  ├── valid_train_file_path                           │
│  ├── valid_test_file_path                            │
│  ├── invalid_train_file_path                         │
│  ├── invalid_test_file_path                          │
│  └── drift_report_file_path                          │
│                                                      │
│  DataValidation.__init__()                           │
│  ├── self.data_ingestion_artifact = artifact         │
│  ├── self.data_validation_config  = config           │
│  └── self.schema_config = read_yaml_file(schema.yaml)│
│                                                      │
│  read_data(file_path)  ← @staticmethod              │
│  └── pd.read_csv() → DataFrame                      │
│                                                      │
│  validate_number_cols(df)                            │
│  ├── schema_config se expected cols count nikalo     │
│  ├── df.columns se actual cols count nikalo          │
│  └── equal? → True : False                          │
│                                                      │
│  check_numerical_col(df)                             │
│  ├── schema_config["numerical_columns"] nikalo       │
│  ├── df mein numerical cols dhundho                  │
│  └── match? → True : False                          │
│                                                      │
│  detect_data_drift(train_df, test_df)                │
│  ├── har column pe KS test chalao                    │
│  │   ks_2samp(train_col, test_col)                   │
│  ├── p_value < 0.05 → drift detected                 │
│  ├── report dict banao → write_yaml_file()           │
│  └── return status (True=no drift, False=drift)      │
│                                                      │
│  initiate_data_validation()                          │
│  ├── train/test paths nikalo artifact se             │
│  ├── DataFrames banao read_data() se                 │
│  ├── validate_number_cols() × 2                      │
│  ├── check_numerical_col() × 2                       │
│  ├── detect_data_drift()                             │
│  ├── valid data save karo                            │
│  └── return DataValidationArtifact  ◄── KEY          │
└─────────────────────────────────────────────────────┘
        │
        │  DataValidationArtifact
        │  ├── validation_status = True/False
        │  ├── valid_train_file_path
        │  ├── valid_test_file_path
        │  └── drift_report_file_path
        │
        ▼
   DATA TRANSFORMATION (next step)
"""
##==================================================================

# IMP: DataIngestion ka OUTPUT → DataValidation ka INPUT
# DataIngestion ne banaya tha:
# DataIngestionArtifact(train_file_path=..., test_file_path=...)
from networksecurity.entity.artifact_entity import (
    DataIngestionArtifact,    # ← DataIngestion se aata hai
    DataValidationArtifact    # ← yeh file return karega
)

# config_entity.py → DataValidationConfig → sab paths yahan se
from networksecurity.entity.config_entity import DataValidationConfig

from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging

# SCHEMA_FILE_PATH = "data_schema/schema.yaml"
# constants/training_pipeline/__init__.py mein defined hai
from networksecurity.constants.training_pipeline import SCHEMA_FILE_PATH

# KS test — Kolmogorov-Smirnov test
# train aur test distribution compare karne ke liye
# p_value < 0.05 → distributions alag hain → drift detected
from scipy.stats import ks_2samp

import pandas as pd
import os
import sys

# utils.py se yeh functions import kiye
# read_yaml_file  → schema.yaml padhne ke liye
# write_yaml_file → drift_report.yaml likhne ke liye
from networksecurity.utils.main_utils.utils import read_yaml_file, write_yaml_file


# ── MAIN CLASS ────────────────────────────────────────────────────
class DataValidation:
    def __init__(self,
                 data_ingestion_artifact: DataIngestionArtifact,
                 data_validation_config: DataValidationConfig):
        """
        DataValidation initialize karta hai.

        Parameters:
            data_ingestion_artifact (DataIngestionArtifact):
                DataIngestion.initiate_data_ingestion() ka output
                ├── train_file_path = ".../ingested/train.csv"
                └── test_file_path  = ".../ingested/test.csv"

            data_validation_config (DataValidationConfig):
                config_entity.py se — sab validation paths yahan
        """
        try:
            # DataIngestion ka output store karo
            # export_collection_as_dataframe ne banaya tha → feature store → split
            self.data_ingestion_artifact = data_ingestion_artifact

            # config_entity.py ka DataValidationConfig
            # valid/invalid paths aur drift report path yahan hain
            self.data_validation_config  = data_validation_config

            # IMP: schema.yaml padhna — expected columns aur types
            # SCHEMA_FILE_PATH = "data_schema/schema.yaml" (constants se)
            # read_yaml_file() utils.py mein defined hai
            self.schema_config = read_yaml_file(SCHEMA_FILE_PATH)
            # schema_config → {"columns": [...], "numerical_columns": [...]}
            logging.info(f"Schema loaded from: {SCHEMA_FILE_PATH}")

        except Exception as e:
            raise NetworkSecurityException(e, sys)

    @staticmethod
    def read_data(file_path) -> pd.DataFrame:
        """
        CSV file padhta hai aur DataFrame return karta hai.

        @staticmethod kyun?
        Class ka koi instance variable use nahi karta (self nahi)
        Pure utility function hai — sirf CSV padhna hai
        DataValidation.read_data() directly call kar sakte hain

        Parameters:
            file_path (str) : CSV file ka path
                e.g. "Artifacts/.../ingested/train.csv"
                DataIngestionArtifact se milega yeh path

        Returns:
            pd.DataFrame : CSV ka DataFrame
        """
        try:
            return pd.read_csv(file_path)
        except Exception as e:
            raise NetworkSecurityException(e, sys)

    def validate_number_cols(self, dataframe: pd.DataFrame) -> bool:
        """
        DataFrame mein utne columns hain ya nahi jitne schema mein expected hain.

        schema.yaml mein 31 columns defined hain (30 features + 1 target)
        Agar MongoDB se aaya data mein columns kam/zyada hain → False return

        Parameters:
            dataframe (pd.DataFrame) : train ya test DataFrame

        Returns:
            bool : True = columns match, False = mismatch
        """
        try:
            # schema_config["columns"] → list of dicts
            # len() → kitne columns expected hain → 31
            number_of_cols = len(self.schema_config["columns"])
            logging.info(f"Expected columns (schema): {number_of_cols}")
            logging.info(f"Actual columns (dataframe): {len(dataframe.columns)}")

            if len(dataframe.columns) == number_of_cols:
                return True
            return False

        except Exception as e:
            raise NetworkSecurityException(e, sys)

    def check_numerical_col(self, dataframe: pd.DataFrame) -> bool:
        """
        DataFrame mein sab expected numerical columns hain ya nahi.

        schema.yaml mein numerical_columns list hai
        Agar koi numerical column missing → False return

        Parameters:
            dataframe (pd.DataFrame) : train ya test DataFrame

        Returns:
            bool : True = sab numerical cols hain, False = missing cols
        """
        try:
            # schema se expected numerical columns
            numerical_cols = self.schema_config["numerical_columns"]
            logging.info(f"Expected numerical cols: {numerical_cols}")

            dataframe_num_cols = dataframe.select_dtypes(
                include=["int64", "float64"]
            ).columns.tolist()
            logging.info(f"Actual numerical cols: {dataframe_num_cols}")

            for col in numerical_cols:
                if col not in dataframe_num_cols:
                    logging.info(f"Missing numerical column: {col}")
                    return False
            return True

        except Exception as e:
            raise NetworkSecurityException(e, sys)

    def detect_data_drift(self, base_df, current_df, threshold=0.05) -> bool:
        """
        Train aur Test data mein statistical drift detect karta hai.

        WHY DRIFT DETECTION?
        Train pe model train hota hai — test pe evaluate hota hai
        Agar dono ka distribution bahut alag hai → model test pe kaam nahi karega
        KS Test (Kolmogorov-Smirnov) = do distributions compare karta hai

        KS TEST:
        p_value >= 0.05 → distributions same hain → NO drift 
        p_value <  0.05 → distributions alag hain → DRIFT DETECTED 

        Parameters:
            base_df    (pd.DataFrame) : train data (reference)
            current_df (pd.DataFrame) : test data (compare karna hai)
            threshold  (float)        : p_value threshold (default 0.05)

        Returns:
            bool : True = no drift, False = drift detected
        """
        try:
            status = True    # assume karo no drift — agar drift mile toh False
            report = {}      

            for column in base_df.columns:
                d1 = base_df[column]
                d2 = current_df[column]

                # IMP: KS test — do distributions compare karta hai
                # ks_2samp(train_col, test_col) → statistic + p_value
                is_same_dist = ks_2samp(d1, d2)

                if threshold <= is_same_dist.pvalue:
                    # p_value >= threshold → same distribution → no drift
                    is_found = False
                else:
                    # p_value < threshold → different distribution → drift!
                    is_found = True
                    status = False  # pipeline mein flag karo

                # report mein column ka result add karo
                report.update({
                    column: {
                        "p_value": float(is_same_dist.pvalue),
                        "drift_status": is_found
                        
                    }
                })

            # drift report YAML mein save karo
            # "Artifacts/timestamp/data_validation/drift_report/report.yaml"
            drift_report_file_path = self.data_validation_config.drift_report_file_path
            dir_path = os.path.dirname(drift_report_file_path)
            os.makedirs(dir_path, exist_ok=True)

            # write_yaml_file() → utils.py mein defined
            write_yaml_file(file_path=drift_report_file_path, content=report)
            logging.info(f"Drift report saved: {drift_report_file_path}")

            return status

        except Exception as e:
            raise NetworkSecurityException(e, sys)

    def initiate_data_validation(self) -> DataValidationArtifact:
        """
        DataValidation ka main entry point.
        Sab validation checks chain karta hai aur artifact return karta hai.

        Returns:
            DataValidationArtifact:
                ├── validation_status       → True/False
                ├── valid_train_file_path   → ".../validated/train.csv"
                ├── valid_test_file_path    → ".../validated/test.csv"
                ├── invalid_train_file_path → ".../invalid/train.csv"
                ├── invalid_test_file_path  → ".../invalid/test.csv"
                └── drift_report_file_path  → ".../drift_report/report.yaml"
        """
        try:
            logging.info("Entered Data Validation Method")

            #-------------------------------------------------
            # for all the steps its function is defined Above 
            #-------------------------------------------------

            # ── STEP 1: Paths nikalo ──────────────────────────────
            # DataIngestionArtifact se train/test paths milte hain
            # DataIngestion ne yahan CSVs save kiye the
            train_file_path = self.data_ingestion_artifact.train_file_path
            test_file_path  = self.data_ingestion_artifact.test_file_path
            # → "Artifacts/.../ingested/train.csv"
            # → "Artifacts/.../ingested/test.csv"

            # ── STEP 2: DataFrames banao ──────────────────────────
            # @staticmethod read_data() → pd.read_csv()
            train_dataframe = DataValidation.read_data(train_file_path)
            test_dataframe  = DataValidation.read_data(test_file_path)
            logging.info(f"Train: {train_dataframe.shape} | Test: {test_dataframe.shape}")

            # ── STEP 3: Column count validate karo ───────────────
            error_message = ""   # error messages collect karo

            status = self.validate_number_cols(dataframe=train_dataframe)
            if not status:
                error_message += "Train DataFrame Doesn't have all the Columns \n"
                logging.warning("Train column validation failed")

            status = self.validate_number_cols(dataframe=test_dataframe)
            if not status:
                error_message += "Test DataFrame Doesn't have all the Columns\n"
                logging.warning("Test column validation failed")

            # ── STEP 4: Numerical columns check karo ─────────────
            status = self.check_numerical_col(dataframe=train_dataframe)
            if not status:
                error_message += "Train DataFrame has Missing numerical columns\n"
                logging.warning("Train numerical column check failed")

            status = self.check_numerical_col(dataframe=test_dataframe)
            if not status:
                error_message += "Test DataFrame has numerical columns\n"
                logging.warning("Test numerical column check failed")

            # ── STEP 5: Data Drift detect karo ───────────────────
            # train = base (reference), test = current (compare)
            status = self.detect_data_drift(
                base_df=train_dataframe,
                current_df=test_dataframe
            )
            logging.info(f"Data drift status: {'No Drift' if status else 'Drift Detected'}")

            # ── STEP 6: Valid data save karo ──────────────────────
            # IMP: valid data save karo → DataTransformation yahan se padhega
            dir_path = os.path.dirname(
                self.data_validation_config.valid_train_file_path
            )
            os.makedirs(dir_path, exist_ok=True)

            train_dataframe.to_csv(
                self.data_validation_config.valid_train_file_path,
                index=False, header=True
            )
            logging.info(f"Valid train saved: {self.data_validation_config.valid_train_file_path}")

            test_dataframe.to_csv(
                self.data_validation_config.valid_test_file_path,
                index=False, header=True
            )
            logging.info(f"Valid test saved: {self.data_validation_config.valid_test_file_path}")

            # ── STEP 7: Artifact banao ────────────────────────────
            data_validation_artifact = DataValidationArtifact(
                validation_status=status,
                valid_train_file_path=self.data_validation_config.valid_train_file_path,
                valid_test_file_path=self.data_validation_config.valid_test_file_path,
                invalid_train_file_path=self.data_validation_config.invalid_train_file_path,
                invalid_test_file_path=self.data_validation_config.invalid_test_file_path,
                drift_report_file_path=self.data_validation_config.drift_report_file_path
            )

            logging.info(f"Data Validation completed: {data_validation_artifact}")
            return data_validation_artifact

        except Exception as e:
            raise NetworkSecurityException(e, sys)


# ─────────────────────────────────────────────────────────────────
# DRY RUN — initiate_data_validation()
#
# INPUT:
# data_ingestion_artifact.train_file_path = "Artifacts/.../ingested/train.csv"
# data_ingestion_artifact.test_file_path  = "Artifacts/.../ingested/test.csv"
#
# 1. read_data() → train_df (8844 × 31), test_df (2211 × 31)
#
# 2. validate_number_cols(train_df)
#    schema mein 31 cols → train_df mein 31 cols → True 
#
# 3. validate_number_cols(test_df)
#    schema mein 31 cols → test_df mein 31 cols → True 
#
# 4. check_numerical_col(train_df)
#    schema numerical_cols = [having_IP_Address, URL_Length, ...]
#    train_df numerical cols = same → True 
#
# 5. detect_data_drift(train_df, test_df)
#    har column pe KS test:
#    having_IP_Address: p_value=0.43 >= 0.05 → no drift
#    URL_Length:        p_value=0.67 >= 0.05 → no drift
#    ... sab columns pe
#    report.yaml mein save
#    status = True (no drift)
#
# 6. valid data save:
#    "Artifacts/.../validated/train.csv"
#    "Artifacts/.../validated/test.csv"
#
# 7. DataValidationArtifact(
#       validation_status=True,
#       valid_train_file_path="Artifacts/.../validated/train.csv",
#       ...
#    )
#
# Disk pe ban gaya:
# Artifacts/
# └── timestamp/
#     └── data_validation/
#         ├── validated/
#         │   ├── train.csv  ← DataTransformation ka INPUT
#         │   └── test.csv
#         ├── invalid/       ← empty (no drift tha)
#         └── drift_report/
#             └── report.yaml
# ─────────────────────────────────────────────────────────────────
