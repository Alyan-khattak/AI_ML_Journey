# ═══════════════════════════════════════════════════════════════════
# networksecurity/pipeline/training_pipeline.py
# ═══════════════════════════════════════════════════════════════════
# Poori training pipeline ko ek class mein wrap karta hai.
# main.py mein jo manually step by step kiya tha → ab yahan class mein
#
# WHY TRAINING PIPELINE CLASS?
# main.py mein:
#   data_ingestion  = DataIngestion(...)
#   data_validation = DataValidation(...)
#   ... manually chain kiya tha
#
# YAHAN (MLOps style):
#   TrainingPipeline().run_pipeline() → sab kuch ek call mein
#   FastAPI /train route → TrainingPipeline().run_pipeline() call karega
#   Clean orchestration → production ready
#
# FLOW:
# run_pipeline()
#   ↓ start_data_ingestion()   → DataIngestionArtifact
#   ↓ start_data_validation()  → DataValidationArtifact
#   ↓ start_data_transformation() → DataTransformationArtifact
#   ↓ start_model_trainer()    → ModelTrainerArtifact
#   ↓ return ModelTrainerArtifact
###==============================================================

import sys

from networksecurity.components.data_ingestion     import DataIngestion
from networksecurity.components.data_validation    import DataValidation
from networksecurity.components.data_transformation import DataTransformation
from networksecurity.components.model_trainer      import ModelTrainer

from networksecurity.entity.config_entity import (
    TrainingPipelineConfig,
    DataIngestionConfig,
    DataValidationConfig,
    DataTransformationConfig,
    ModelTrainerConfig
)

from networksecurity.entity.artifact_entity import (
    DataIngestionArtifact,
    DataValidationArtifact,
    DataTransformationArtifact,
    ModelTrainerArtifact
)

from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging


class TrainingPipeline:
    def __init__(self):
        # IMP: ek hi TrainingPipelineConfig — sab steps same timestamp use karenge
        # taaki sab artifacts ek hi Artifacts/timestamp/ folder mein jaayein
        self.training_pipeline_config = TrainingPipelineConfig()
        logging.info(f"TrainingPipeline initialized — artifact_dir: {self.training_pipeline_config.artifact_dir}")

    def start_data_ingestion(self) -> DataIngestionArtifact:
        """
        MongoDB se data pull karta hai → feature store → train/test split

        Returns:
            DataIngestionArtifact:
                ├── train_file_path = "Artifacts/.../ingested/train.csv"
                └── test_file_path  = "Artifacts/.../ingested/test.csv"
        """
        try:
            self.data_ingestion_config = DataIngestionConfig(
                training_pipeline_config=self.training_pipeline_config
            )
            logging.info("Start Data Ingestion")

            data_ingestion = DataIngestion(
                data_ingestion_config=self.data_ingestion_config
            )
            data_ingestion_artifact = data_ingestion.initiate_data_ingestion()

            logging.info(f"Data Ingestion Completed: {data_ingestion_artifact}\n")
            
            return data_ingestion_artifact

        except Exception as e:
            raise NetworkSecurityException(e, sys)
            # BUG FIXED: raise NetworkSecurityException → (e, sys) pass karo

    def start_data_validation(self, data_ingestion_artifact: DataIngestionArtifact) -> DataValidationArtifact:
        """
        Schema validate karta hai → drift detect karta hai → valid data save

        Parameters:
            data_ingestion_artifact : start_data_ingestion() ka output
                train/test CSV paths yahan se milte hain

        Returns:
            DataValidationArtifact:
                ├── validation_status
                ├── valid_train_file_path
                ├── valid_test_file_path
                └── drift_report_file_path
        """
        try:
            self.data_validation_config = DataValidationConfig(
                training_pipeline_config=self.training_pipeline_config
            )
            logging.info("Start Data Validation")

            data_validation = DataValidation(
                data_ingestion_artifact=data_ingestion_artifact,
                # ↑ DataIngestion ka OUTPUT → DataValidation ka INPUT
                data_validation_config=self.data_validation_config
            )
            data_validation_artifact = data_validation.initiate_data_validation()

            logging.info(f"Data Validation Completed: {data_validation_artifact}\n")
            return data_validation_artifact

        except Exception as e:
            raise NetworkSecurityException(e, sys)

    def start_data_transformation(self, data_validation_artifact: DataValidationArtifact) -> DataTransformationArtifact:
        """
        Validated CSV → KNNImputer → numpy arrays (.npy) → preprocessor.pkl

        Parameters:
            data_validation_artifact : start_data_validation() ka output
                valid_train/test_file_path yahan se milte hain

        Returns:
            DataTransformationArtifact:
                ├── transformed_train_file_path → train.npy
                ├── transformed_test_file_path  → test.npy
                └── transformed_object_file_path → preprocessing.pkl
        """
        try:
            self.data_transformation_config = DataTransformationConfig(
                training_pipeline_config=self.training_pipeline_config
            )
            logging.info("Start Data Transformation")

            data_transformation = DataTransformation(
                data_validation_artifact=data_validation_artifact,
                # ↑ DataValidation ka OUTPUT → DataTransformation ka INPUT
                data_transformation_config=self.data_transformation_config
            )
            data_transformation_artifact = data_transformation.initiate_data_transformation()

            # BUG FIXED: "Data Validation Completed" → "Data Transformation Completed"
            logging.info(f"Data Transformation Completed: {data_transformation_artifact}\n")
            return data_transformation_artifact

        except Exception as e:
            raise NetworkSecurityException(e, sys)

    def start_model_trainer(self, data_transformation_artifact: DataTransformationArtifact) -> ModelTrainerArtifact:
        """
        numpy arrays → GridSearchCV → best model → MLflow → NetworkModel.pkl

        Parameters:
            data_transformation_artifact : start_data_transformation() ka output
                train.npy, test.npy, preprocessing.pkl paths yahan se milte hain

        Returns:
            ModelTrainerArtifact:
                ├── trained_model_file_path
                ├── train_metric_artifact (f1, precision, recall)
                └── test_metric_artifact  (f1, precision, recall)
        """
        try:
            self.model_trainer_config = ModelTrainerConfig(
                training_pipeline_config=self.training_pipeline_config
            )
            logging.info("Start Model Trainer")

            model_trainer = ModelTrainer(
                model_trainer_config=self.model_trainer_config,
                data_transformation_artifact=data_transformation_artifact
                # ↑ DataTransformation ka OUTPUT → ModelTrainer ka INPUT
            )
            model_trainer_artifact = model_trainer.initiate_model_trainer()

            logging.info(f"Model Training Completed: {model_trainer_artifact}\n")
            return model_trainer_artifact

        except Exception as e:
            raise NetworkSecurityException(e, sys)

    def run_pipeline(self) -> ModelTrainerArtifact:
        """
        Poori pipeline ek call mein run karta hai.
        FastAPI /train route yahan se call karega.

        Returns:
            ModelTrainerArtifact → final trained model ka artifact
        """
        try:
            logging.info("=" * 60)
            logging.info("Training Pipeline Started")
            logging.info("=" * 60)

            # ── STEP 1: DATA INGESTION ─────────────────────────────
            data_ingestion_artifact = self.start_data_ingestion()

            # ── STEP 2: DATA VALIDATION ────────────────────────────
            # data_ingestion_artifact → DataValidation ko pass
            data_validation_artifact = self.start_data_validation(
                data_ingestion_artifact=data_ingestion_artifact
            )

            # ── STEP 3: DATA TRANSFORMATION ────────────────────────
            # data_validation_artifact → DataTransformation ko pass
            data_transformation_artifact = self.start_data_transformation(
                data_validation_artifact=data_validation_artifact
            )

            # ── STEP 4: MODEL TRAINER ──────────────────────────────
            # data_transformation_artifact → ModelTrainer ko pass
            model_trainer_artifact = self.start_model_trainer(
                data_transformation_artifact=data_transformation_artifact
            )

            logging.info("=" * 60)
            logging.info("Training Pipeline Completed")
            logging.info("=" * 60)

            return model_trainer_artifact

        except Exception as e:
            raise NetworkSecurityException(e, sys)


# ─────────────────────────────────────────────────────────────────
# DRY RUN — run_pipeline()
#
# pipeline = TrainingPipeline()
# artifact = pipeline.run_pipeline()
#
# 1. start_data_ingestion()
#    → MongoDB → feature_store/phishingData.csv
#    → ingested/train.csv + test.csv
#    → DataIngestionArtifact
#
# 2. start_data_validation(data_ingestion_artifact)
#    → schema check → drift detection
#    → validated/train.csv + test.csv
#    → drift_report/report.yaml
#    → DataValidationArtifact
#
# 3. start_data_transformation(data_validation_artifact)
#    → KNNImputer → train.npy + test.npy
#    → preprocessing.pkl
#    → DataTransformationArtifact
#
# 4. start_model_trainer(data_transformation_artifact)
#    → GridSearchCV → best model
#    → MLflow metrics log
#    → NetworkModel.pkl save
#    → ModelTrainerArtifact
#
# FastAPI mein:
# @app.get("/train")
# def train():
#     pipeline = TrainingPipeline()
#     pipeline.run_pipeline()
#     return {"message": "Training completed"}
# ─────────────────────────────────────────────────────────────────

