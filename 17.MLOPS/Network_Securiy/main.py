# ═══════════════════════════════════════════════════════════════════
# main.py
# ═══════════════════════════════════════════════════════════════════
# Entry point — pipeline manually test karne ke liye
# Production mein TrainingPipeline.run_pipeline() use hoga
# Abhi DataIngestion + DataValidation + DataTransformation test
###==============================================================

import sys

from networksecurity.components.data_ingestion import DataIngestion
from networksecurity.components.data_validation import DataValidation
from networksecurity.components.data_transformation import DataTransformation
# ↑ NEW — DataTransformation component import kiya

from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging

from networksecurity.entity.config_entity import (
    TrainingPipelineConfig,
    DataIngestionConfig,
    DataValidationConfig,
    DataTransformationConfig    # ← NEW
)

from networksecurity.components.model_trainer import ModelTrainer
from networksecurity.entity.config_entity import ModelTrainerConfig

if __name__ == "__main__":
    try:
        logging.info("Training Pipeline started")

        # ── STEP 1: Master Config ──────────────────────────────────
        # TrainingPipelineConfig → timestamp generate hoga
        # sab doosre configs isko inject karte hain
        # taaki sab ek hi Artifacts/timestamp/ folder mein jaayein
        training_pipeline_config = TrainingPipelineConfig()
        logging.info(f"Artifact dir: {training_pipeline_config.artifact_dir}")

        # ── STEP 2: Data Ingestion ─────────────────────────────────
        # MongoDB → feature_store CSV → 80/20 split → artifact
        # DataIngestionArtifact → train/test paths return karta hai
        data_ingestion_config = DataIngestionConfig(
            training_pipeline_config=training_pipeline_config
        )
        data_ingestion = DataIngestion(
            data_ingestion_config=data_ingestion_config
        )
        logging.info("DataIngestion initialized")

        data_ingestion_artifact = data_ingestion.initiate_data_ingestion()
        logging.info(f"DataIngestion completed: {data_ingestion_artifact}")
        # data_ingestion_artifact:
        # ├── train_file_path = "Artifacts/.../ingested/train.csv"
        # └── test_file_path  = "Artifacts/.../ingested/test.csv"

        # ── STEP 3: Data Validation ────────────────────────────────
        # schema check → numerical cols check → KS drift detection
        # valid data save → DataValidationArtifact return
        data_validation_config = DataValidationConfig(
            training_pipeline_config=training_pipeline_config
        )
        # IMP: same training_pipeline_config inject karo
        # taaki same Artifacts/timestamp/ folder use ho

        data_validation = DataValidation(
            data_ingestion_artifact=data_ingestion_artifact,
            # ↑ DataIngestion ka OUTPUT → DataValidation ka INPUT
            # train/test paths yahan se milenge
            data_validation_config=data_validation_config
        )
        logging.info("DataValidation initialized")

        data_validation_artifact = data_validation.initiate_data_validation()
        logging.info(f"DataValidation completed: {data_validation_artifact}")
        # data_validation_artifact:
        # ├── validation_status       = True/False
        # ├── valid_train_file_path   = "Artifacts/.../validated/train.csv"
        # ├── valid_test_file_path    = "Artifacts/.../validated/test.csv"
        # ├── invalid_train_file_path = "Artifacts/.../invalid/train.csv"
        # ├── invalid_test_file_path  = "Artifacts/.../invalid/test.csv"
        # └── drift_report_file_path  = "Artifacts/.../drift_report/report.yaml"

        # ── STEP 4: Data Transformation ───────────────────────────
        # validated CSV → KNNImputer → numpy arrays (.npy) → preprocessor.pkl
        # DataTransformationArtifact → ModelTrainer ko pass hoga
        data_transformation_config = DataTransformationConfig(
            training_pipeline_config=training_pipeline_config
        )
        # IMP: same training_pipeline_config inject karo → same timestamp

        data_transformation = DataTransformation(
            data_validation_artifact=data_validation_artifact,
            # ↑ DataValidation ka OUTPUT → DataTransformation ka INPUT
            # valid_train_file_path aur valid_test_file_path yahan se milenge
            # "Artifacts/.../validated/train.csv" → DataTransformation padhega
            data_transformation_config=data_transformation_config
        )
        logging.info("DataTransformation initialized")

        data_transformation_artifact = data_transformation.initiate_data_transformation()
        logging.info(f"DataTransformation completed: {data_transformation_artifact}")
        # data_transformation_artifact:
        # ├── transformed_train_file_path    = "Artifacts/.../transformed/train.npy"
        # ├── transformed_test_file_path     = "Artifacts/.../transformed/test.npy"
        # └── transformed_object_file_path   = "Artifacts/.../transformed_object/preprocessing.pkl"

        # ── STEP 5: Model Trainer ──────────────────────────────────
        # numpy arrays → GridSearchCV → best model → MLflow → artifact
        model_trainer_config = ModelTrainerConfig(
            training_pipeline_config=training_pipeline_config
        )
        # IMP: same training_pipeline_config → same timestamp folder

        model_trainer = ModelTrainer(
            model_trainer_config=model_trainer_config,
            data_transformation_artifact=data_transformation_artifact
            # ↑ DataTransformation ka OUTPUT → ModelTrainer ka INPUT
            # train.npy, test.npy, preprocessing.pkl paths yahan se milenge
        )
        logging.info("ModelTrainer initialized")

        model_trainer_artifact = model_trainer.initiate_model_trainer()
        logging.info(f"ModelTrainer completed: {model_trainer_artifact}")
        # model_trainer_artifact:
        # ├── trained_model_file_path = "Artifacts/.../model_trainer/trained_model/model.pkl"
        # ├── train_metric_artifact   = ClassificationMetricArtifact(f1, precision, recall)
        # └── test_metric_artifact    = ClassificationMetricArtifact(f1, precision, recall)

        print(model_trainer_artifact)

    except Exception as e:
        raise NetworkSecurityException(e, sys)