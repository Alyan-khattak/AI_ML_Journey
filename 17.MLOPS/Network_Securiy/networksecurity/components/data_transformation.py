# ═══════════════════════════════════════════════════════════════════
# networksecurity/components/data_transformation.py
# ═══════════════════════════════════════════════════════════════════
# DataValidation ke baad validated CSV data ko transform karta hai.
# KNNImputer se missing values fill karta hai.
# numpy arrays (.npy) save karta hai → ModelTrainer ka INPUT
# preprocessor.pkl save karta hai → PredictPipeline use karega
#
# PEHLE TEEN PROJECTS SE FARQ:
# Student Performance → ColumnTransformer (OHE + StandardScaler)
#                       categorical + numerical features the
# Heart Disease       → ColumnTransformer (OHE + StandardScaler)
#                       IQR outlier removal bhi tha
# SMS Spam            → Word2Vec + StandardScaler (NLP pipeline)
#
# YAHAN (Network Security):
# Sirf KNNImputer — sab features already numerical hain (0,1,-1)
# No OHE needed — no categorical columns
# No StandardScaler — tree-based models ke liye scaling zaroori nahi
# KNNImputer → missing values ko similar rows se fill karta hai
#
# FLOW:
# DataValidationArtifact (valid_train/test_file_path)
#       ↓ read_data()
# train_df, test_df
#       ↓ X/y split + target -1 → 0 convert
# X_train, y_train, X_test, y_test
#       ↓ get_data_transformer_object()
# Pipeline(KNNImputer)
#       ↓ fit_transform(X_train), transform(X_test)
# transformed arrays
#       ↓ np.c_[X, y] → train_arr, test_arr
# train.npy, test.npy → save_numpy_array_data()
# preprocessing.pkl   → save_object()
#       ↓ initiate_data_transformation()
# DataTransformationArtifact → ModelTrainer ko pass hoga
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
   → DataValidationArtifact  ← INPUT (DataValidation ne banaya)
     ├── valid_train_file_path = "Artifacts/.../validated/train.csv"
     └── valid_test_file_path  = "Artifacts/.../validated/test.csv"

   → DataTransformationArtifact ← OUTPUT (yeh return karega)
     ├── transformed_object_file_path = "Artifacts/.../transformed_object/preprocessing.pkl"
     ├── transformed_train_file_path  = "Artifacts/.../transformed/train.npy"
     └── transformed_test_file_path   = "Artifacts/.../transformed/test.npy"

2. networksecurity/entity/config_entity.py
   → DataTransformationConfig ← CONFIG
     ├── transformed_train_file_path
     ├── transformed_test_file_path
     └── transformed_object_file_path

3. networksecurity/constants/training_pipeline/__init__.py
   → TARGET_COLUMN = "Result"
   → DATA_TRANSFORMATION_IMPUTER_PARAMS = {missing_values, n_neighbors, weights}

4. networksecurity/utils/main_utils/utils.py
   → save_numpy_array_data() ← .npy files save karne ke liye
   → save_object()           ← preprocessor.pkl save karne ke liye
"""
"""
ARTIFACTS DIRECTORY — DATA TRANSFORMATION KE BAAD:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Artifacts/
└── 08_24_2026_14_32_00/
    ├── data_ingestion/
    │   └── ...
    ├── data_validation/
    │   ├── validated/
    │   │   ├── train.csv   ← DataTransformation ka INPUT
    │   │   └── test.csv    ← DataTransformation ka INPUT
    │   └── drift_report/report.yaml
    └── data_transformation/              ← DataTransformation banayega
        ├── transformed/                  ← numpy arrays
        │   ├── train.npy                 ← ModelTrainer ka INPUT
        │   └── test.npy                  ← ModelTrainer ka INPUT
        └── transformed_object/
            └── preprocessing.pkl        ← PredictPipeline load karega
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
"""
ENTRY POINT (main.py se)
        │
        ▼
┌─────────────────────────────────────────────────────┐
│              DATA TRANSFORMATION                     │
│                                                      │
│  INPUT:                                              │
│  DataValidationArtifact ← DataValidation ne diya     │
│  ├── valid_train_file_path = ".../validated/train.csv│
│  └── valid_test_file_path  = ".../validated/test.csv │
│                                                      │
│  DataTransformationConfig ← config_entity.py se      │
│  ├── transformed_train_file_path  (.npy)             │
│  ├── transformed_test_file_path   (.npy)             │
│  └── transformed_object_file_path (.pkl)             │
│                                                      │
│  DataTransformation.__init__()                       │
│  ├── self.data_validation_artifact = artifact        │
│  └── self.data_transformation_config = config        │
│                                                      │
│  read_data(file_path) ← @staticmethod               │
│  └── pd.read_csv() → DataFrame                      │
│                                                      │
│  get_data_transformer_object()                       │
│  ├── KNNImputer(**DATA_TRANSFORMATION_IMPUTER_PARAMS)│
│  │   missing_values=NaN, n_neighbors=3, uniform      │
│  └── Pipeline([("imputer", imputer)]) → return       │
│                                                      │
│  initiate_data_transformation()                      │
│  ├── 1. read valid_train.csv → train_df              │
│  │      read valid_test.csv  → test_df               │
│  ├── 2. X/y split                                    │
│  │      target -1 → 0 convert (binary classification)│
│  ├── 3. get_data_transformer_object()                │
│  ├── 4. fit_transform(X_train) ← SIRF TRAIN PE      │
│  │      transform(X_test)     ← NO FIT               │
│  ├── 5. np.c_[X, y] → train_arr, test_arr           │
│  ├── 6. save train.npy + test.npy                    │
│  │      save preprocessing.pkl                       │
│  └── 7. return DataTransformationArtifact  ◄── KEY  │
└─────────────────────────────────────────────────────┘
        │
        │  DataTransformationArtifact
        │  ├── transformed_train_file_path = ".../transformed/train.npy"
        │  ├── transformed_test_file_path  = ".../transformed/test.npy"
        │  └── transformed_object_file_path = ".../preprocessing.pkl"
        │
        ▼
   MODEL TRAINER (next step)
"""
##==================================================================

import sys
import os
import numpy as np
import pandas as pd
from sklearn.impute import KNNImputer
from sklearn.pipeline import Pipeline

# TARGET_COLUMN = "Result" — constants se
# DataTransformation X/y split mein use karega
from networksecurity.constants.training_pipeline import TARGET_COLUMN

# DATA_TRANSFORMATION_IMPUTER_PARAMS = {missing_values, n_neighbors, weights}
# KNNImputer ko yahi params pass honge
from networksecurity.constants.training_pipeline import DATA_TRANSFORMATION_IMPUTER_PARAMS

from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging

from networksecurity.entity.artifact_entity import (
    DataTransformationArtifact,  # ← yeh file return karega
    DataValidationArtifact        # ← DataValidation ka output → yahan ka input
)
from networksecurity.entity.config_entity import DataTransformationConfig

# save_numpy_array_data → .npy files save karne ke liye (utils.py mein add karo)
# save_object           → preprocessor.pkl save karne ke liye
from networksecurity.utils.main_utils.utils import save_numpy_array_data, save_object


# ── MAIN CLASS ────────────────────────────────────────────────────
class DataTransformation:
    def __init__(self,
                 data_validation_artifact: DataValidationArtifact,
                 data_transformation_config: DataTransformationConfig):
        """
        DataTransformation initialize karta hai.

        Parameters:
            data_validation_artifact (DataValidationArtifact):
                DataValidation.initiate_data_validation() ka output
                ├── valid_train_file_path = ".../validated/train.csv"
                └── valid_test_file_path  = ".../validated/test.csv"

            data_transformation_config (DataTransformationConfig):
                config_entity.py se — transformed paths yahan
        """
        try:
            self.data_validation_artifact   = data_validation_artifact
            # BUG FIXED: self.data_transformation_config = self.data_transformation_config
            # self se self assign kar raha tha → NameError
            self.data_transformation_config = data_transformation_config
        except Exception as e:
            raise NetworkSecurityException(e, sys)

    @staticmethod
    def read_data(file_path: str) -> pd.DataFrame:
        """
        CSV file padhta hai aur DataFrame return karta hai.

        @staticmethod kyun?
        self use nahi karta — pure utility function
        DataTransformation.read_data() directly call kar sakte hain

        Parameters:
            file_path (str) : validated CSV ka path
                e.g. "Artifacts/.../validated/train.csv"
                DataValidationArtifact.valid_train_file_path se milega

        Returns:
            pd.DataFrame
        """
        try:
            return pd.read_csv(file_path)
        except Exception as e:
            raise NetworkSecurityException(e, sys)
            # BUG FIXED: raise Exception(e, sys) → NetworkSecurityException

    def get_data_transformer_object(self) -> Pipeline:
        """
        KNNImputer Pipeline banata hai aur return karta hai.

        PEHLE TEEN PROJECTS MEIN:
            ColumnTransformer(num_pipeline, cat_pipeline)
            StandardScaler, OHE sab the
        YAHAN:
            Sirf KNNImputer — sab features already numerical hain
            No OHE, No StandardScaler needed

        WHY PIPELINE?
        Pipeline = steps ko chain karta hai
        Abhi sirf ek step hai (imputer)
        Baad mein aur steps add karna ho toh easy hai
        fit() → sab steps sequentially fit hote hain
        transform() → sab steps sequentially transform karte hain

        Returns:
            Pipeline : fitted hone ke baad missing values fill karega
        """
        logging.info("Entered get_data_transformer_object method")
        try:
            # KNNImputer banao — constants se params lo
            # **DATA_TRANSFORMATION_IMPUTER_PARAMS = dict unpack
            # → KNNImputer(missing_values=np.nan, n_neighbors=3, weights="uniform")
            imputer: KNNImputer = KNNImputer(**DATA_TRANSFORMATION_IMPUTER_PARAMS)
            logging.info(f"KNNImputer initialized with params: {DATA_TRANSFORMATION_IMPUTER_PARAMS}")

            
            processor: Pipeline = Pipeline(steps=[
                ("imputer", imputer)
                # step naam "imputer" → Pipeline.named_steps["imputer"] se access
            ])

            return processor

        except Exception as e:
            raise NetworkSecurityException(e, sys)

    def initiate_data_transformation(self) -> DataTransformationArtifact:
        """
        DataTransformation ka main entry point.
        Validated CSV → KNNImputer → numpy arrays → save → artifact

        Returns:
            DataTransformationArtifact:
                ├── transformed_object_file_path → preprocessing.pkl
                ├── transformed_train_file_path  → train.npy
                └── transformed_test_file_path   → test.npy
        """
        logging.info("Entered initiate_data_transformation method")
        try:
            logging.info("Data Transformation started")

            ##-----------------------------------------##
            ##     STEP 1: DATA PADHNA
            ##-----------------------------------------##
            # DataValidationArtifact se valid paths milte hain
            # DataValidation ne yahan validated data save kiya tha
            train_df = DataTransformation.read_data(
                self.data_validation_artifact.valid_train_file_path
            )
           
            test_df = DataTransformation.read_data(
                self.data_validation_artifact.valid_test_file_path
            )
            logging.info(f"Train: {train_df.shape} | Test: {test_df.shape}")

            ##-----------------------------------------##
            ##     STEP 2: X/y SPLIT + TARGET CONVERT
            ##-----------------------------------------##
            logging.info("Splitting into X/y and converting target")

            # X = features (sab columns except target)
            # y = target (Result column)
            # TARGET_COLUMN = "Result" — constants se
            input_feature_train_df  = train_df.drop(TARGET_COLUMN, axis=1)
            target_feature_train_df = train_df[TARGET_COLUMN]

            # IMP: target -1 → 0 convert karo
            # Dataset mein: phishing=1, legitimate=-1
            # Binary classification ke liye: phishing=1, legitimate=0
            # sklearn models 0/1 expect karte hain — -1 nahi
            target_feature_train_df = target_feature_train_df.replace(-1, 0)

            input_feature_test_df  = test_df.drop(TARGET_COLUMN, axis=1)
            target_feature_test_df = test_df[TARGET_COLUMN]
            target_feature_test_df = target_feature_test_df.replace(-1, 0)

            logging.info("X/y split completed | -1 → 0 conversion done")

            ##-----------------------------------------##
            ##     STEP 3: PREPROCESSOR BANAO
            ##-----------------------------------------##
            # get_data_transformer_object() → Pipeline(KNNImputer) milta hai
            preprocessor_obj = self.get_data_transformer_object()

            ##-----------------------------------------##
            ##     STANDARDIZATION / IMPUTATION
            ##-----------------------------------------##
            # IMP: fit_transform SIRF train pe
            # test pe sirf transform — no leakage
            # KNNImputer train data ki statistics se NaN fill karega
            transformed_input_train_df = preprocessor_obj.fit_transform(input_feature_train_df)
            # fit → KNN neighbors train data se calculate hote hain
            # transform → NaN values fill hoti hain

            transformed_input_test_df = preprocessor_obj.transform(input_feature_test_df)
            # sirf transform — train ki neighbors use hoti hain
            logging.info("KNNImputer applied — train fit_transform, test transform only")

            ##-----------------------------------------##
            ##     STEP 4: FEATURES + TARGET COMBINE
            ##-----------------------------------------##
            # np.c_ = horizontally stack — last col = target
            # same pattern as pehle teen projects mein
            train_arr = np.c_[
                transformed_input_train_df,
                np.array(target_feature_train_df)
            ]
            test_arr = np.c_[
                transformed_input_test_df,
                np.array(target_feature_test_df)
            ]
            logging.info(f"train_arr: {train_arr.shape} | test_arr: {test_arr.shape}")

            ##-----------------------------------------##
            ##     STEP 5: SAVE ARTIFACTS
            ##-----------------------------------------##
            # .npy format mein save karo — numpy binary format
            # utils.py mein save_numpy_array_data() add karo
            save_numpy_array_data(
                self.data_transformation_config.transformed_train_file_path,
                train_arr
            )
            logging.info(f"train.npy saved: {self.data_transformation_config.transformed_train_file_path}")

            save_numpy_array_data(
                self.data_transformation_config.transformed_test_file_path,
                test_arr
            )
            logging.info(f"test.npy saved: {self.data_transformation_config.transformed_test_file_path}")

            # IMP: preprocessor save karo — predict_pipeline mein load hoga
            # BUG FIXED: save_transformed_object_file_path → transformed_object_file_path
            save_object(
                self.data_transformation_config.transformed_object_file_path,
                preprocessor_obj
            )
            logging.info(f"preprocessing.pkl saved: {self.data_transformation_config.transformed_object_file_path}")

            ##-----------------------------------------##
            ##     STEP 6: ARTIFACT BANAO
            ##-----------------------------------------##
           
            data_transformation_artifact = DataTransformationArtifact(
                transformed_object_file_path=self.data_transformation_config.transformed_object_file_path,
                transformed_train_file_path=self.data_transformation_config.transformed_train_file_path,
                transformed_test_file_path=self.data_transformation_config.transformed_test_file_path,
            )

            logging.info(f"Data Transformation completed: {data_transformation_artifact}")
            return data_transformation_artifact

        except Exception as e:
            raise NetworkSecurityException(e, sys)


# ─────────────────────────────────────────────────────────────────
# DRY RUN — initiate_data_transformation()
#
# INPUT:
# valid_train_file_path = "Artifacts/.../validated/train.csv"
# valid_test_file_path  = "Artifacts/.../validated/test.csv"
#
# 1. read_data() → train_df (8844 × 31), test_df (2211 × 31)
#
# 2. X/y split:
#    X_train = train_df.drop("Result") → (8844 × 30)
#    y_train = train_df["Result"]       → (8844,) values: 1, -1
#    y_train.replace(-1, 0)             → (8844,) values: 1, 0
#
# 3. KNNImputer Pipeline banao
#    missing_values=NaN, n_neighbors=3, weights="uniform"
#
# 4. fit_transform(X_train):
#    har NaN value → 3 nearest neighbors ka average se fill
#    output: (8844 × 30) numpy array — no NaN
#
#    transform(X_test):
#    train ki neighbors use karo → (2211 × 30) numpy array
#
# 5. np.c_:
#    train_arr = (8844 × 31)  last col = y_train (0/1)
#    test_arr  = (2211 × 31)  last col = y_test  (0/1)
#
# 6. save:
#    train.npy → "Artifacts/.../transformed/train.npy"
#    test.npy  → "Artifacts/.../transformed/test.npy"
#    preprocessing.pkl → "Artifacts/.../transformed_object/preprocessing.pkl"
#
# 7. DataTransformationArtifact(
#       transformed_object_file_path = "Artifacts/.../preprocessing.pkl",
#       transformed_train_file_path  = "Artifacts/.../train.npy",
#       transformed_test_file_path   = "Artifacts/.../test.npy"
#    )
# ─────────────────────────────────────────────────────────────────

