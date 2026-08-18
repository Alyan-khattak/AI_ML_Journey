# ═══════════════════════════════════════════════════════════════════
# data_transformation.py
# ═══════════════════════════════════════════════════════════════════
# Notebook mein jo manually kiya tha (imputation, encoding, scaling)
# woh yahan automated pipeline mein convert hota hai.
#
# DO KAAM:
# 1. get_data_transformer_object() → sklearn Pipeline banao, return karo
# 2. initiate_data_transformation() → wo pipeline use karke train/test transform karo
#                                     aur preprocessor.pkl save karo
#
# FLOW:
# DataIngestion → (train_path, test_path)
#                        ↓
# DataTransformation → (train_arr, test_arr, preprocessor.pkl path)
#                        ↓
# ModelTrainer → model train karo



###==============================================================

"""
data_ingestion.py
- This File Reads data from some source
- Split it in Train set and Test set 
    - save raw, train, test data in artifact folder 
- return train and test data set path  via initiate_data_ingestion function
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

import sys
import os
from dataclasses import dataclass

import numpy as np
import pandas as pd

from sklearn.compose import ColumnTransformer   # alag alag columns pe alag pipelines lagao
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.impute import SimpleImputer        # missing values handle karo
from sklearn.pipeline import Pipeline           # steps ko sequence mein chain karo

from src.exception import CustomException
from src.logger import logging
from src.utils import save_object               # preprocessor.pkl disk pe save karne ke liye


# ── CONFIG CLASS ──────────────────────────────────────────────────
# Sirf ek path store karta hai — preprocessor pickle kahan save hoga
# @dataclass = __init__ auto ban jaata hai
@dataclass
class DataTransformationConfig:
    preprocessor_object_file_path: str = os.path.join("artifacts", "preprocessor.pkl")


# ── MAIN CLASS ────────────────────────────────────────────────────
class DataTransformation:
    def __init__(self):   
        self.data_transformation_config = DataTransformationConfig()
        # ab self.data_transformation_config.preprocessor_object_file_path available hai


    def get_data_transformer_object(self):
        """
        Sklearn ColumnTransformer banata hai jo:
        - Numerical cols pe: imputation (median) + StandardScaler lagata hai
        - Categorical cols pe: imputation (mode) + OneHotEncoder + StandardScaler lagata hai

        Returns:
            preprocessor (ColumnTransformer) — abhi FITTED nahi, sirf defined
            Fitting initiate_data_transformation() mein hogi train data pe
        """
        try:
            # EDA notebook se pata tha ye cols numerical hain
            numerical_features   = ["writing_score", "reading_score"]

            # EDA notebook se pata tha ye cols categorical hain
            categorical_features = [
                'gender',
                'race_ethnicity',
                'parental_level_of_education',
                'lunch',
                'test_preparation_course'
            ]

            # ── NUMERICAL PIPELINE ────────────────────────────────
            # Step 1: SimpleImputer(median) — missing values ko median se bharo
            #         median isliye kyunki outliers se affect nahi hota (mean hota)
            # Step 2: StandardScaler — mean=0, std=1 pe scale karo
            #         distance-based models ke liye zaroori
            num_pipeline = Pipeline(steps=[
                ("imputer", SimpleImputer(strategy="median")),
                ("scaler",  StandardScaler())
            ])

            # ── CATEGORICAL PIPELINE ──────────────────────────────
            # Step 1: SimpleImputer(most_frequent) — missing values ko mode se bharo
            # Step 2: OneHotEncoder — categories ko 0/1 columns mein convert karo
            # Step 3: StandardScaler — encoded columns bhi scale karo
            #         with_mean=False hona chahiye OHE ke baad — sparse matrix issue
            #         (yahan bug hai — fix neeche bataya)
            cat_pipeline = Pipeline(steps=[
                ("imputer", SimpleImputer(strategy="most_frequent")),
                ("onehot",  OneHotEncoder(handle_unknown="ignore")),   # IMP: handle_unknown
                                                                        # production mein naye
                                                                        # categories aayein toh crash na ho
                ("scaler",  StandardScaler(with_mean=False))           # IMP: sparse matrix ke liye
                                                                        # with_mean=False zaroori hai
            ])

            logging.info(f"Numerical Cols   : {numerical_features}")
            logging.info(f"Categorical Cols : {categorical_features}") 

            # ── COLUMN TRANSFORMER ────────────────────────────────
            # num_pipeline  → sirf numerical_features pe lagao
            # cat_pipeline  → sirf categorical_features pe lagao
            # Dono ka output horizontally stack hota hai (numpy array)
            preprocessor = ColumnTransformer(transformers=[
                ("num_pipeline", num_pipeline,   numerical_features),
                ("cat_pipeline", cat_pipeline,   categorical_features)
            ])

            return preprocessor   # UNFITTED — sirf blueprint return ho raha hai

        except Exception as e:
            raise CustomException(e, sys)



    def initiate_data_transformation(self, train_path, test_path):
        """
        train_path aur test_path se data padhta hai.
        preprocessor fit karta hai SIRF train pe.
        dono ko transform karta hai.
        preprocessor.pkl save karta hai.

        Parameters:
            train_path (str) : "artifacts/train.csv"
            test_path  (str) : "artifacts/test.csv"

        Returns:
            tuple: (train_arr, test_arr, preprocessor_pkl_path)
                train_arr  — numpy array: [transformed features | target]
                test_arr   — numpy array: [transformed features | target]
                path       — str: preprocessor.pkl ka path (ModelTrainer ko chahiye)
        """
        try:
            train_df = pd.read_csv(train_path)
            test_df  = pd.read_csv(test_path)
            logging.info("Read Train and Test Data completed")

            logging.info("Obtaining preprocessing object")
            preprocessor_obj = self.get_data_transformer_object()   # blueprint milta hai 
                                                                    # as get_data_transfomer_object() method doesnt take any inputs and returns preprocessor which we stored in preprocessor_obj

            target_col_name  = "math_score"

            ##-----------------------------------------##
            ##     TRAIN TEST SPLIT
            ##-----------------------------------------##

            # ── TRAIN DATA SPLIT ──────────────────────────────────
            # X (features) aur y (target) alag karo
            input_feature_train_df  = train_df.drop(target_col_name, axis=1)  # X_train
            target_feature_train_df = train_df[target_col_name]               # y_train

            # ── TEST DATA SPLIT ───────────────────────────────────
            input_feature_test_df  = test_df.drop(target_col_name, axis=1)  # X_test
            target_feature_test_df = test_df[target_col_name]               # y_test

            logging.info("Applying preprocessor on Training and Test Data")


            ##-----------------------------------------##
            ##     Standardzation 
            ##-----------------------------------------##

            # IMP: fit_transform SIRF train pe — test ka koi bhi information
            # preprocessor mein nahi jaana chahiye (no leakage)
            input_feature_train_array = preprocessor_obj.fit_transform(input_feature_train_df)

            # IMP: test pe sirf transform — fit nahi (train ki statistics use hoti hain)
            input_feature_test_array  = preprocessor_obj.transform(input_feature_test_df)

            # ── COMBINE FEATURES + TARGET ─────────────────────────
            # np.c_ = horizontally stack karo (column wise)
            # [transformed features cols | target col]
            # e.g. train: 800 rows × 7 features  +  800 rows × 1 target
            #      → 800 rows × 8
            train_arr = np.c_[input_feature_train_array, np.array(target_feature_train_df)]
            test_arr  = np.c_[input_feature_test_array,  np.array(target_feature_test_df)]

            # ── SAVE PREPROCESSOR ─────────────────────────────────
            # fitted preprocessor ko pkl mein save karo
            # prediction time pe same transformations apply karni hongi naye data pe
            # The Function is defined in utils.py
            save_object(
                file_path=self.data_transformation_config.preprocessor_object_file_path,
                obj=preprocessor_obj
            )
            logging.info("Preprocessor pickle saved")

            return (
                train_arr,
                test_arr,
                self.data_transformation_config.preprocessor_object_file_path
            )

        except Exception as e:
            raise CustomException(e, sys)


# ─────────────────────────────────────────────────────────────────
# FULL DRY RUN — get_data_transformer_object()
#
# preprocessor = get_data_transformer_object()
#
# 1. numerical_features   = ["writing_score", "reading_score"]
# 2. categorical_features = ["gender", "race_ethnicity", ...]
#
# 3. num_pipeline banata hai:
#       SimpleImputer(median) → StandardScaler()
#
# 4. cat_pipeline banata hai:
#       SimpleImputer(most_frequent) → OneHotEncoder() → StandardScaler(with_mean=False)
#
# 5. ColumnTransformer:
#       num_pipeline  → writing_score, reading_score columns pe
#       cat_pipeline  → gender, race_ethnicity ... pe
#
# 6. return preprocessor   ← abhi kuch fit nahi hua, sirf plan ready hai
# ─────────────────────────────────────────────────────────────────

# ─────────────────────────────────────────────────────────────────
# FULL DRY RUN — initiate_data_transformation()
#
# train_path = "artifacts/train.csv"  (800 rows)
# test_path  = "artifacts/test.csv"   (200 rows)
#
# 1. train_df = pd.read_csv(...)  → 800 × 8 DataFrame
#    test_df  = pd.read_csv(...)  → 200 × 8 DataFrame
#
# 2. preprocessor_obj = get_data_transformer_object()
#       → ColumnTransformer blueprint milta hai (unfitted)
#
# 3. input_feature_train_df  = train_df.drop("math_score")  → 800 × 7
#    target_feature_train_df = train_df["math_score"]        → 800 values
#
#    input_feature_test_df   = test_df.drop("math_score")   → 200 × 7
#    target_feature_test_df  = test_df["math_score"]         → 200 values
#
# 4. fit_transform on train:
#       num_pipeline:
#           writing_score, reading_score → median impute → scale
#       cat_pipeline:
#           gender         → [male, female]           → [0,1] → scale
#           race_ethnicity → [A,B,C,D,E]              → [0,0,0,1,0] → scale
#           ...
#       output: 800 × N numpy array  (N = 2 num + OHE expanded cat cols)
#
# 5. transform on test (NO fit — train ki mean/std use hoti hai):
#       output: 200 × N numpy array
#
# 6. np.c_ se target chipkao:
#       train_arr → 800 × (N+1)   last col = math_score
#       test_arr  → 200 × (N+1)   last col = math_score
#
# 7. save_object("artifacts/preprocessor.pkl", preprocessor_obj)
#       → fitted preprocessor disk pe save
#
# 8. return (train_arr, test_arr, "artifacts/preprocessor.pkl")
#       → ModelTrainer ko yahi milega
#
# Disk pe ban gaya:
#   artifacts/
#   ├── raw.csv           (1000 rows — ingestion se)
#   ├── train.csv         ( 800 rows — ingestion se)
#   ├── test.csv          ( 200 rows — ingestion se)
#   └── preprocessor.pkl  (fitted ColumnTransformer — prediction mein use hoga)
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