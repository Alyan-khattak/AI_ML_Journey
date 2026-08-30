# ═══════════════════════════════════════════════════════════════════
# networksecurity/entity/artifact_entity.py
# ═══════════════════════════════════════════════════════════════════
# Har pipeline component ka RETURN TYPE yahan define hota hai.
#
# WHY ARTIFACT ENTITY?
# PEHLE TEEN PROJECTS MEIN:
#   return (train_path, test_path)  ← simple tuple
#   koi bhi order mein unpack kar sakta tha → bugs
#   type information nahi thi
#
# YAHAN (MLOps style):
#   return DataIngestionArtifact(train_file_path=..., test_file_path=...)
#   typed object → IDE autocomplete → type checking → professional
#   DataValidation ko exactly pata hai kya expect karna hai
###==============================================================

from dataclasses import dataclass

# @dataclass → __init__ auto ban jaata hai
# sirf fields define karo → class ready

@dataclass
class DataIngestionArtifact:
    train_file_path: str
    # "Artifacts/timestamp/data_ingestion/ingested/train.csv"

    test_file_path: str
    # "Artifacts/timestamp/data_ingestion/ingested/test.csv"

# IMP: DataValidation in paths se data padhega
# koi bhi component jo DataIngestion ke baad aaye
# use DataIngestionArtifact milega → type-safe




# ── ARTIFACT 2: DataValidationArtifact ───────────────────────────
# DataValidation.initiate_data_validation() yeh return karega
# DataTransformation ko yeh milega → valid paths se data padhega
@dataclass
class DataValidationArtifact:
    validation_status: bool
    # True = data valid hai → pipeline aage chale
    # False = data invalid hai → pipeline rok do

    valid_train_file_path: str
    # validated/train.csv → DataTransformation yahan se padhega
    # "Artifacts/timestamp/data_validation/validated/train.csv"

    valid_test_file_path: str
    # validated/test.csv → DataTransformation yahan se padhega
    # "Artifacts/timestamp/data_validation/validated/test.csv"

    invalid_train_file_path: str
    # invalid/train.csv → agar drift detect hua → yahan save hoga
    # "Artifacts/timestamp/data_validation/invalid/train.csv"

    invalid_test_file_path: str
    # invalid/test.csv
    # "Artifacts/timestamp/data_validation/invalid/test.csv"

    drift_report_file_path: str
    # drift_report/report.yaml → KS test results yahan save honge
    # "Artifacts/timestamp/data_validation/drift_report/report.yaml"





# ── ARTIFACT 3: DataTransformationArtifact ───────────────────────────
# DataTransformation.initiate_data_transformation() yeh return karega
# Model Trainer ko yeh milega  as input→ valid paths se data padhega    
@dataclass
class DataTransformationArtifact:
    transformed_object_file_path: str
    # "Artifacts/.../data_transformation/transformed_object/preprocessing.pkl"
    # IMP: ModelTrainer + PredictPipeline dono use karenge

    transformed_train_file_path: str
    # "Artifacts/.../data_transformation/transformed/train.npy"
    # ModelTrainer ka INPUT

    transformed_test_file_path: str
    # "Artifacts/.../data_transformation/transformed/test.npy"
    # ModelTrainer ka INPUT



# ── ARTIFACT 4: ClassificationMetricArtifact ─────────────────────
# ModelTrainer train aur test dono pe metrics calculate karta hai
# F1, Precision, Recall → ek structured object mein store karo
# ModelTrainerArtifact mein yeh nested hoga
#
# WHY ALAG ARTIFACT?
# PEHLE TEEN PROJECTS MEIN:
#   sirf r2_score ya AUC return karte the — single float
# YAHAN:
#   teen metrics ek object mein → clean aur type-safe
#   train_metric aur test_metric → dono alag alag store honge
#   → overfitting check karna easy: train_metric.f1 vs test_metric.f1
@dataclass
class ClassificationMetricArtifact:
    f1_score: float
    # F1 = precision aur recall ka harmonic mean
    # network security mein important → false positives bhi costly hain

    precision_score: float
    # BUG FIXED: precession_score → precision_score (typo)
    # precision = TP / (TP + FP)
    # flagged threats mein se kitne real threats the

    recall_score: float
    # recall = TP / (TP + FN)
    # actual threats mein se kitne pakde


# ── ARTIFACT 5: ModelTrainerArtifact ─────────────────────────────
# ModelTrainer.initiate_model_training() yeh return karega
# PredictPipeline ko model_file_path chahiye → load karke predict karega
# MLflow bhi in metrics ko log karega experiment tracking ke liye
#
# IMP: train_metric aur test_metric DONO store hain
# DataValidation artifact ke baad validation_status tha (True/False)
# ModelTrainer artifact mein actual performance numbers hain
# → overfitting check: train_metric.f1_score vs test_metric.f1_score
@dataclass
class ModelTrainerArtifact:
    trained_model_file_path: str
    # "Artifacts/timestamp/model_trainer/trained_model/model.pkl"
    # PredictPipeline yahan se model load karega

    train_metric_artifact: ClassificationMetricArtifact
    # training data pe metrics
    # ├── f1_score
    # ├── precision_score
    # └── recall_score
    # overfitting check: train_metric.f1 - test_metric.f1 > 0.05?

    test_metric_artifact: ClassificationMetricArtifact
    # test data pe metrics
    # ├── f1_score
    # ├── precision_score
    # └── recall_score
    # yeh wala production performance estimate karta hai
