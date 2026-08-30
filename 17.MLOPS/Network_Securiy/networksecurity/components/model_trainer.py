# ═══════════════════════════════════════════════════════════════════
# networksecurity/components/model_trainer.py
# ═══════════════════════════════════════════════════════════════════
# DataTransformation ke baad numpy arrays pe models train karta hai.
# GridSearchCV se best model select karta hai.
# MLflow mein metrics track karta hai.
# NetworkModel (preprocessor + model) save karta hai.
# ModelTrainerArtifact return karta hai.
#
# PEHLE TEEN PROJECTS SE FARQ:
# Student Performance → R2 score, regression models
# Heart Disease       → AUC score, Youden's J threshold
# SMS Spam            → F1 score, Word2Vec features
# Network Security    → F1 score + MLflow tracking + NetworkModel wrapper
#                       overfitting/underfitting check bhi hai
#
# FLOW:
# DataTransformationArtifact (train.npy, test.npy, preprocessing.pkl)
#       ↓ load_numpy_array()
# train_arr, test_arr
#       ↓ X/y split
# X_train, y_train, X_test, y_test
#       ↓ train_model() → evaluate_models() → GridSearchCV
# best_model
#       ↓ get_classification_score() × 2 (train + test)
# train_metric, test_metric
#       ↓ track_mlflow() × 2
# MLflow experiment logged
#       ↓ NetworkModel(preprocessor, best_model)
#       ↓ save_object(model.pkl)
# ModelTrainerArtifact → return
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

5: utils/ML_utils/metric/classification_metric.py :: is file me metric calculation k liye funcion defined h
6: utils/ML_utils/model/estimator.py              :: is file mai model k prediction ka code likha hwa h, input data py precessor Apply krky predict krta h 

7: cloud/hf_sync.py :: is file final_model to Hugging face pr push krny ka code likha Hwa h 

7:loggin/logger.py :: logging defined h 
8: exception/exception.py :: exception defined h 
 
"""




"""
FILES JO YEH USE KARTA HAI:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. artifact_entity.py
   → DataTransformationArtifact ← INPUT
     ├── transformed_train_file_path = ".../transformed/train.npy"
     ├── transformed_test_file_path  = ".../transformed/test.npy"
     └── transformed_object_file_path = ".../preprocessing.pkl"

   → ModelTrainerArtifact ← OUTPUT
     ├── trained_model_file_path    = ".../model_trainer/trained_model/model.pkl"
     ├── train_metric_artifact      = ClassificationMetricArtifact
     └── test_metric_artifact       = ClassificationMetricArtifact

   → ClassificationMetricArtifact (nested in ModelTrainerArtifact)
     ├── f1_score
     ├── precision_score
     └── recall_score

2. config_entity.py
   → ModelTrainerConfig ← CONFIG
     ├── trained_model_file_path
     ├── expected_accuracy = 0.6
     └── overfitting_underfitting_threshold = 0.05

3. utils/ml_utils/model/estimator.py
   → NetworkModel(preprocessor, model)
     predict() → transform → predict

4. utils/ml_utils/metric/classification_metric.py
   → get_classification_score() → ClassificationMetricArtifact

5. utils/main_utils/utils.py
   → evaluate_models() → GridSearchCV → best F1 dict
   → load_numpy_array() → .npy → numpy array
   → save_object()      → NetworkModel.pkl save
   → load_object()      → preprocessor.pkl load
"""
"""
ENTRY POINT (main.py se)
        │
        ▼
┌─────────────────────────────────────────────────────┐
│                 MODEL TRAINER                        │
│                                                      │
│  INPUT:                                              │
│  DataTransformationArtifact                          │
│  ├── transformed_train_file_path → train.npy         │
│  ├── transformed_test_file_path  → test.npy          │
│  └── transformed_object_file_path → preprocessing.pkl│
│                                                      │
│  ModelTrainerConfig                                  │
│  ├── trained_model_file_path                         │
│  ├── expected_accuracy = 0.6                         │
│  └── overfitting_underfitting_threshold = 0.05       │
│                                                      │
│  initiate_model_trainer()                            │
│  ├── 1. load train.npy → train_arr                   │
│  │      load test.npy  → test_arr                    │
│  ├── 2. X/y split (last col = target)               │
│  ├── 3. train_model(X_train, y_train, X_test, y_test)│
│  │      ├── 5 models + params define                 │
│  │      ├── evaluate_models() → GridSearchCV → F1   │
│  │      ├── best model select                        │
│  │      ├── get_classification_score() train         │
│  │      ├── track_mlflow() train metrics             │
│  │      ├── get_classification_score() test          │
│  │      ├── track_mlflow() test metrics              │
│  │      ├── NetworkModel(preprocessor, best_model)   │
│  │      ├── save_object(model.pkl)                   │
│  │      └── return ModelTrainerArtifact              │
│  └── return ModelTrainerArtifact  ◄── KEY            │
└─────────────────────────────────────────────────────┘
        │
        │  ModelTrainerArtifact
        │  ├── trained_model_file_path
        │  ├── train_metric_artifact (f1, precision, recall)
        │  └── test_metric_artifact  (f1, precision, recall)
        │
        ▼
   PREDICT PIPELINE / FastAPI (next step)
"""
##==================================================================

import sys
import os
import numpy as np
import pandas as pd
import mlflow
# IMP: mlflow → experiment tracking
# har run ka metrics, params, model version store karta hai
# DagsHub ya local MLflow server pe log hoga

from networksecurity.constants.training_pipeline import TARGET_COLUMN
from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging

from networksecurity.entity.artifact_entity import (
    ModelTrainerArtifact,          # ← yeh file return karega
    ClassificationMetricArtifact,  # ← train + test metrics
    DataTransformationArtifact     # ← DataTransformation ka output → input
)
from networksecurity.entity.config_entity import ModelTrainerConfig

from networksecurity.utils.main_utils.utils import (
    save_object,        # NetworkModel.pkl save karne ke liye
    load_object,        # preprocessor.pkl load karne ke liye
    load_numpy_array,   # train.npy, test.npy load karne ke liye
    evaluate_models     # GridSearchCV → F1 dict
)
from networksecurity.utils.ML_utils.metric.classification_metric import get_classification_score
# get_classification_score() → f1, precision, recall calculate karta hai

from networksecurity.utils.ML_utils.model.estimator import NetworkModel
# NetworkModel → preprocessor + model ek object mein wrap karta hai

from networksecurity.cloud.hf_syncer import push_model_to_huggingface
#To Push Model to Hugging face 

from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import (
    AdaBoostClassifier,
    GradientBoostingClassifier,
    RandomForestClassifier
)

'''
I commented this part and put this code in Track_flow function
why ? -> b/c i am depolying on Rainway and its giving errors 
Kyunki training_pipeline.py → model_trainer.py import karta hai → dagshub.init() module load hote hi run hota hai — chahe /train call ho ya na ho.
and I dont wanna add my credentionals there -> So if you are running locally uncomment this and comment these lines ml_flow track function 


# Initailization DagsHub
# To see what is DagsHub and Mlflow see the file :: MLflow_Beginner_Guide.md
import dagshub
dagshub.init(repo_owner='Alyan-khattak', repo_name='Network-Security-MLops', mlflow=True)
#MLflow tracks your ML Experiments 
#DagsHUb is like gthub , You connect ur github repo with DagsHUb
#then when you run the MLFlow Experiments are track over there, you can see it in dagshub experiments Sections

'''

# ── MAIN CLASS ────────────────────────────────────────────────────
class ModelTrainer:
    def __init__(self,
                 model_trainer_config: ModelTrainerConfig,
                 data_transformation_artifact: DataTransformationArtifact):
        """
        ModelTrainer initialize karta hai.

        Parameters:
            model_trainer_config (ModelTrainerConfig):
                config_entity.py se — paths aur thresholds
                ├── trained_model_file_path
                ├── expected_accuracy = 0.6
                └── overfitting_underfitting_threshold = 0.05

            data_transformation_artifact (DataTransformationArtifact):
                DataTransformation ka output → yahan ka input
                ├── transformed_train_file_path → train.npy
                ├── transformed_test_file_path  → test.npy
                └── transformed_object_file_path → preprocessing.pkl
        """
        try:
            self.model_trainer_config         = model_trainer_config
            self.data_transformation_artifact = data_transformation_artifact
            logging.info("ModelTrainer initialized")
        except Exception as e:
            raise NetworkSecurityException(e, sys)

    def track_mlflow(self, best_model, classificationmetric: ClassificationMetricArtifact):
        """
        MLflow mein model metrics log karta hai.
        DagsHub ya local server pe experiment track hota hai.

        Parameters:
            best_model              : fitted sklearn model
            classificationmetric   : ClassificationMetricArtifact (f1, precision, recall)
        """
        with mlflow.start_run():

            # Initailization DagsHub
            # To see what is DagsHub and Mlflow see the file :: MLflow_Beginner_Guide.md
            import dagshub
            dagshub.init(repo_owner='Alyan-khattak', repo_name='Network-Security-MLops', mlflow=True)
            #MLflow tracks your ML Experiments 
            #DagsHUb is like gthub , You connect ur github repo with DagsHUb
            #then when you run the MLFlow Experiments are track over there, you can see it in dagshub experiments Sections

            f1_score        = classificationmetric.f1_score
            precision_score = classificationmetric.precision_score
            recall_score    = classificationmetric.recall_score

            mlflow.log_metric("f1_score",        f1_score)
            mlflow.log_metric("precision_score",  precision_score)
            mlflow.log_metric("recall_score",     recall_score)

    
            # load_model loads a model — log_model saves it to MLflow
            mlflow.sklearn.log_model(best_model, name="model")
            logging.info(
                f"MLflow logged — F1: {f1_score:.4f} | "
                f"Precision: {precision_score:.4f} | "
                f"Recall: {recall_score:.4f}"
            )

    def train_model(self, X_train, y_train, X_test, y_test) -> ModelTrainerArtifact:
        """
        Sab models train karta hai, best select karta hai,
        overfitting check karta hai, NetworkModel save karta hai.

        Parameters:
            X_train, y_train : training features aur target (numpy arrays)
            X_test,  y_test  : test features aur target (numpy arrays)

        Returns:
            ModelTrainerArtifact
        """

        # ---------------- Define Models ----------------
        # IMP: verbose=0 set karo — verbose=1 bahut output karta hai
        models = {
            "Random Forest"      : RandomForestClassifier(verbose=1),
            "Decision Tree"      : DecisionTreeClassifier(),
            "Gradient Boosting"  : GradientBoostingClassifier(verbose=1),
            "Logistic Regression": LogisticRegression(verbose=1),
            "AdaBoost"           : AdaBoostClassifier(),
        }

        # ---------------- Hyperparameter Grids ----------------
        # IMP: keys models dict ke saath EXACTLY match hone chahiye
        params = {
            "Decision Tree": {
                "criterion": ["gini", "entropy", "log_loss"],
            },
            "Random Forest": {
                "n_estimators": [8, 16, 32, 128, 256]
            },
            "Gradient Boosting": {
                "learning_rate": [.1, .01, .05, .001],
                "subsample"    : [0.6, 0.7, 0.75, 0.85, 0.9],
                "n_estimators" : [8, 16, 32, 64, 128, 256]
            },
            "Logistic Regression": {},
            # {} = koi param nahi → GridSearchCV ek fit karega
            "AdaBoost": {
                "learning_rate": [.1, .01, .001],
                "n_estimators" : [8, 16, 32, 64, 128, 256]
            }
        }

        # ── EVALUATE ALL MODELS ───────────────────────────────────

        model_report: dict = evaluate_models(
            X_train=X_train,
            y_train=y_train,
            X_test=X_test,
            y_test=y_test,
            models=models,
            params=params
        )
        logging.info(f"Model evaluation complete: {model_report}")

        # ── BEST MODEL SELECT ─────────────────────────────────────
        best_model_score = max(sorted(model_report.values()))


        best_model_name = list(model_report.keys())[
            list(model_report.values()).index(best_model_score)
        ]
        best_model = models[best_model_name]
        logging.info(f"Best Model: {best_model_name} | F1: {best_model_score:.4f}")

        # IMP: expected_accuracy check karo
        if best_model_score < self.model_trainer_config.expected_accuracy:
            raise NetworkSecurityException(
                f"No best model found — F1 {best_model_score:.4f} < expected {self.model_trainer_config.expected_accuracy}",
                sys
            )

        # ── TRAIN METRICS ─────────────────────────────────────────
        y_train_pred = best_model.predict(X_train)


        # This Function is defined in utils/ML_utils/metrics/classification_metric.py
        classification_train_metric = get_classification_score(
            y_true=y_train,
            y_pred=y_train_pred
        )

        # track_ml_flow function is defined Above 
        self.track_mlflow(best_model, classification_train_metric)
        logging.info(f"Train metrics: {classification_train_metric}")

        # ── TEST METRICS ──────────────────────────────────────────
        y_test_pred = best_model.predict(X_test)
        # y_pred=y_test galat tha — y_test_pred hona chahiye

         # This Function is defined in utils/ML_utils/metrics/classification_metric.py
        classification_test_metric = get_classification_score(
            y_true=y_test,
            y_pred=y_test_pred
        )
        self.track_mlflow(best_model, classification_test_metric)
        logging.info(f"Test metrics: {classification_test_metric}")

        # ── OVERFITTING / UNDERFITTING CHECK ─────────────────────
        # IMP: train - test > threshold → overfitting
        #      test - train > threshold → underfitting
        diff = abs(
            classification_train_metric.f1_score -
            classification_test_metric.f1_score
        )
        if diff > self.model_trainer_config.overfitting_underfitting_threshold:
            logging.warning(
                f"Overfitting/Underfitting detected — "
                f"Train F1: {classification_train_metric.f1_score:.4f} | "
                f"Test F1: {classification_test_metric.f1_score:.4f} | "
                f"Diff: {diff:.4f} > threshold: {self.model_trainer_config.overfitting_underfitting_threshold}"
            )

        # ── LOAD PREPROCESSOR ─────────────────────────────────────
        # DataTransformation ne save kiya tha → yahan load karo
        # NetworkModel mein wrap karne ke liye
        preprocessor = load_object(
            self.data_transformation_artifact.transformed_object_file_path
        )
        logging.info("Preprocessor loaded from transformation artifact")

        # ── SAVE NetworkModel ─────────────────────────────────────
        # IMP: preprocessor + model ek saath pkl mein save karo
        # PredictPipeline ek load se dono mil jaayenge
        
        model_dir_path = os.path.dirname(
            self.model_trainer_config.trained_model_file_path
        )
        os.makedirs(model_dir_path, exist_ok=True)


        # NetWorkModel is defined in utils/ML_utils/model/estimator.py
        network_model = NetworkModel(preprocessor=preprocessor, model=best_model)
        save_object(
            file_path=self.model_trainer_config.trained_model_file_path,
            obj=network_model
        )
        logging.info(f"NetworkModel saved: {self.model_trainer_config.trained_model_file_path}")

        #########################
        # Model Pusher -> save Model and preprocessor in final_model folder too
        ###########################
        FINAL_MODEL_DIR = "/home/aizen/ML_Projects/Network_Securiy/final_model"
        # save  model 
        save_object(
            file_path=os.path.join(FINAL_MODEL_DIR, "model.pkl"),
            obj=best_model
        )
        # save preprocessor
        save_object(
            file_path=os.path.join(FINAL_MODEL_DIR, "preprocessor.pkl"),
            obj=preprocessor
        )

        ### ==>> Pushing Model Too Hugging Face 
        push_model_to_huggingface() # code for this is written in cloud/hf_sync.py


        # ── ARTIFACT BANAO ────────────────────────────────────────
        model_trainer_artifact = ModelTrainerArtifact(
            trained_model_file_path=self.model_trainer_config.trained_model_file_path,
            train_metric_artifact=classification_train_metric,
            test_metric_artifact=classification_test_metric
        )

        logging.info(f"ModelTrainer Artifact: {model_trainer_artifact}")
        return model_trainer_artifact


    

    def initiate_model_trainer(self) -> ModelTrainerArtifact:
        """
        ModelTrainer ka main entry point.
        .npy files load karta hai → X/y split → train_model() → artifact return

        Returns:
            ModelTrainerArtifact:
                ├── trained_model_file_path  → model.pkl
                ├── train_metric_artifact    → ClassificationMetricArtifact
                └── test_metric_artifact     → ClassificationMetricArtifact
        """
        try:
            logging.info("Entered initiate_model_trainer")

            ##-----------------------------------------##
            ##     STEP 1: .npy FILES LOAD KARO
            ##-----------------------------------------##
            # DataTransformationArtifact se paths milte hain
            train_file_path = self.data_transformation_artifact.transformed_train_file_path
            test_file_path  = self.data_transformation_artifact.transformed_test_file_path
            # → "Artifacts/.../transformed/train.npy"
            # → "Artifacts/.../transformed/test.npy"

            # load_numpy_array → np.load() → numpy array
            train_arr = load_numpy_array(train_file_path)
            test_arr  = load_numpy_array(test_file_path)
            logging.info(f"Loaded — train_arr: {train_arr.shape} | test_arr: {test_arr.shape}")

            ##-----------------------------------------##
            ##     STEP 2: X/y SPLIT
            ##-----------------------------------------##
            # IMP: last col = target — np.c_ ne yahan chipkaya tha DataTransformation mein
            # [:,:-1] = sab columns EXCEPT last → features (X)
            # [:, -1] = sirf last column         → target (y)
            X_train, y_train, X_test, y_test = (
                train_arr[:, :-1],
                train_arr[:, -1],
                test_arr[:, :-1],
                test_arr[:, -1]
            )
            logging.info(
                f"X_train: {X_train.shape} | y_train: {y_train.shape} | "
                f"X_test: {X_test.shape}  | y_test: {y_test.shape}"
            )

            ##-----------------------------------------##
            ##     STEP 3: MODEL TRAIN KARO
            ##-----------------------------------------##
            model_trainer_artifact = self.train_model(X_train, y_train, X_test, y_test)

            return model_trainer_artifact

        except Exception as e:
            raise NetworkSecurityException(e, sys)


# ─────────────────────────────────────────────────────────────────
# DRY RUN — initiate_model_trainer()
#
# 1. train.npy load → train_arr (8844 × 31)
#    test.npy  load → test_arr  (2211 × 31)
#
# 2. X_train = (8844 × 30), y_train = (8844,)
#    X_test  = (2211 × 30), y_test  = (2211,)
#
# 3. evaluate_models() → 5 models GridSearchCV:
#    {"Random Forest": 0.95, "Decision Tree": 0.91, ...}
#    best = "Random Forest" → F1: 0.95
#
# 4. F1 0.95 > 0.6 (expected_accuracy) → pass 
#
# 5. classification_train_metric = get_classification_score(y_train, y_train_pred)
#    → ClassificationMetricArtifact(f1=0.97, precision=0.96, recall=0.98)
#    track_mlflow(best_model, train_metric) → MLflow log
#
# 6. classification_test_metric = get_classification_score(y_test, y_test_pred)
#    → ClassificationMetricArtifact(f1=0.95, precision=0.94, recall=0.96)
#    track_mlflow(best_model, test_metric) → MLflow log
#
# 7. |0.97 - 0.95| = 0.02 < 0.05 (threshold) → no overfitting 
#
# 8. preprocessor = load_object(preprocessing.pkl)
#    network_model = NetworkModel(preprocessor, RandomForest)
#    save_object("Artifacts/.../model_trainer/trained_model/model.pkl", network_model)
#
# 9. ModelTrainerArtifact(
#       trained_model_file_path = "Artifacts/.../model.pkl",
#       train_metric_artifact   = ClassificationMetricArtifact(0.97, 0.96, 0.98),
#       test_metric_artifact    = ClassificationMetricArtifact(0.95, 0.94, 0.96)
#    )
# ─────────────────────────────────────────────────────────────────

# ─────────────────────────────────────────────────────────────────
# BUGS FIXED SUMMARY:
# 1. evaluate_model(y_train=y) → y variable nahi tha → y_train
# 2. X_test, y_test, models, params missing the evaluate_models() mein
# 3. model_report.key() → model_report.keys()
# 4. get_classification_score(y_pred=y_train) → y_train_pred
# 5. get_classification_score(y_pred=y_test) → y_test_pred
# 6. mlflow.sklearn.load_model → log_model
# 7. precession_score → precision_score
# 8. commas missing X_train, y_train, X_test, y_test tuple mein
# 9. verbose=1 → verbose=0 (less noise)
# 10. initaite_model_trainer → initiate_model_trainer
# ─────────────────────────────────────────────────────────────────