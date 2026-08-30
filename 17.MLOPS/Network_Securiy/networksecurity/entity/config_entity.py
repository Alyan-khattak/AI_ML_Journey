# ═══════════════════════════════════════════════════════════════════
# networksecurity/entity/config_entity.py
# ═══════════════════════════════════════════════════════════════════
# Har pipeline component ka CONFIG yahan define hota hai
#
# WHY ENTITY/CONFIG?
# Pehle teen projects mein:
#   @dataclass directly component file mein tha
#   e.g. data_ingestion.py mein DataIngestionConfig tha
#
# Yahan (MLOps style):
#   Config ALAG FILE mein — entity/config_entity.py
#   Component sirf config object leta hai — paths khud nahi banata
#   Separation of concerns zyada clean hai
#
# PATTERN:
# constants/ → raw values (strings, floats)
#      ↓
# config_entity.py → in values se paths banao (os.path.join)
#      ↓
# component → config object lo, kaam karo
#
# IMP: TrainingPipelineConfig → timestamp generate karta hai
#      sab doosre configs TrainingPipelineConfig se inherit karte hain
#      taaki sab ek hi timestamp folder mein jaayein
###==============================================================

from datetime import datetime
import os
from networksecurity.constants import training_pipeline


# ── DEBUG PRINTS (development ke liye) ───────────────────────────
# IMP: production mein yeh hata dena chahiye
print(training_pipeline.PIPELINE_NAME)   # → "NetworkSecurity"
print(training_pipeline.ARTIFACT_DIR)    # → "Artifacts"


# ══════════════════════════════════════════════════════════════════
# CLASS 1: TrainingPipelineConfig
# ══════════════════════════════════════════════════════════════════
# Master config — timestamp generate karta hai
# Sab doosre configs isko inject karte hain
# Taaki sab ek hi timestamped run folder mein save hon

class TrainingPipelineConfig():
    def __init__(self, timestamp=datetime.now()):
        """
        Pipeline level config — har run pe naya timestamp folder banata hai

        Parameters:
            timestamp (datetime) : default = abhi ka time
                                   test mein alag time pass kar sakte ho

        Creates:
            self.artifact_dir = "Artifacts/08_24_2026_14_32_00"
                                  ^^^^^^^^  ^^^^^^^^^^^^^^^^^^^
                                  ARTIFACT_DIR  timestamp
        """
        # IMP: timestamp string format mein convert karo
        # datetime object → "08_24_2026_14_32_00"
        # %m = month, %d = day, %Y = year, %H = hour, %M = minute, %S = second
        timestamp = timestamp.strftime("%m_%d_%Y_%H_%M_%S")

        self.pipeline_name = training_pipeline.PIPELINE_NAME
        # → "NetworkSecurity"

        self.artifact_name = training_pipeline.ARTIFACT_DIR
        # → "Artifacts"

        self.artifact_dir = os.path.join(self.artifact_name, timestamp)
        # os.path.join("Artifacts", "08_24_2026_14_32_00")
        # → "Artifacts/08_24_2026_14_32_00"
        # IMP: har run pe NAYA folder — history preserve hoti hai
        # PEHLE TEEN PROJECTS MEIN: artifacts/ overwrite hota tha

        self.timestamp: str = timestamp
        # → "08_24_2026_14_32_00"
        # S3 sync mein bhi use hoga baad mein


# ══════════════════════════════════════════════════════════════════
# CLASS 2: DataIngestionConfig
# ══════════════════════════════════════════════════════════════════
# Data Ingestion component ke liye sab paths yahan define hain
# MongoDB se data pull karke kahan save karna hai → sab yahan

class DataIngestionConfig():
    def __init__(self, training_pipeline_config: TrainingPipelineConfig):
        """
        DataIngestion ke liye sab paths banata hai.
        TrainingPipelineConfig inject hota hai — timestamp milta hai

        Parameters:
            training_pipeline_config (TrainingPipelineConfig):
                master config — artifact_dir milta hai isse

        PATH STRUCTURE:
        Artifacts/
        └── 08_24_2026_14_32_00/          ← training_pipeline_config.artifact_dir
            └── data_ingestion/            ← DATA_INGESTION_DIR_NAME
                ├── feature_store/         ← DATA_INGESTION_FEATURE_STORE_DIR
                │   └── phishingData.csv   ← FILE_NAME (raw MongoDB data)
                └── ingested/              ← DATA_INGESTION_INGESTED_DIR
                    ├── train.csv          ← TRAIN_FILE_NAME
                    └── test.csv           ← TEST_FILE_NAME
        """

        # ── BASE DIR ──────────────────────────────────────────────
        # "Artifacts/08_24_2026_14_32_00/data_ingestion"
        self.data_ingestion_dir: str = os.path.join(
            training_pipeline_config.artifact_dir,  # "Artifacts/timestamp"
            training_pipeline.DATA_INGESTION_DIR_NAME  # "data_ingestion"
        )
        # → "Artifacts/08_24_2026_14_32_00/data_ingestion"

        # ── FEATURE STORE PATH ────────────────────────────────────
        # Raw MongoDB data yahan save hoga — split se pehle backup
        # "Artifacts/timestamp/data_ingestion/feature_store/phishingData.csv"
        self.feature_store_file_path: str = os.path.join(
            self.data_ingestion_dir,                        # base dir
            training_pipeline.DATA_INGESTION_FEATURE_STORE_DIR,  # "feature_store"
            training_pipeline.FILE_NAME                     # "phishingData.csv"
        )
        # → "Artifacts/08_24_2026_14_32_00/data_ingestion/feature_store/phishingData.csv"

        # ── TRAIN FILE PATH ───────────────────────────────────────
        # 80/20 split ke baad train data yahan
        # "Artifacts/timestamp/data_ingestion/ingested/train.csv"
        self.training_file_path: str = os.path.join(
            self.data_ingestion_dir,                       # base dir
            training_pipeline.DATA_INGESTION_INGESTED_DIR, # "ingested"
            training_pipeline.TRAIN_FILE_NAME              # "train.csv"
        )
        # → "Artifacts/08_24_2026_14_32_00/data_ingestion/ingested/train.csv"

        # ── TEST FILE PATH ────────────────────────────────────────
        # 80/20 split ke baad test data yahan
        self.testing_file_path: str = os.path.join(
            self.data_ingestion_dir,                       # base dir
            training_pipeline.DATA_INGESTION_INGESTED_DIR, # "ingested"
            training_pipeline.TEST_FILE_NAME               # "test.csv"
        )
        # → "Artifacts/08_24_2026_14_32_00/data_ingestion/ingested/test.csv"

        # ── SPLIT RATIO ───────────────────────────────────────────
        self.train_test_split_ratio: float = training_pipeline.DATA_INGESTION_TRAIN_TEST_SPLIT_RATIO
        # → 0.2 → 80% train, 20% test

        # ── MONGODB CONFIG ────────────────────────────────────────
        self.collection_name: str = training_pipeline.DATA_INGESTION_COLLECTION_NAME
        # → "NetworkData" — MongoDB collection jahan phishing data hai

        self.database_name: str = training_pipeline.DATA_INGESTION_DATABASE_NAME
        # → "ALYAN" — MongoDB database naam




# ══════════════════════════════════════════════════════════════════
# CLASS 3: DataValidationConfig
# ══════════════════════════════════════════════════════════════════
# DataValidation ke liye sab paths
# TrainingPipelineConfig inject hota hai → same timestamp folder
class DataValidationConfig:
    def __init__(self, training_pipeline_config: TrainingPipelineConfig):
        """
        PATH STRUCTURE:
        Artifacts/timestamp/
        └── data_validation/
            ├── validated/              ← valid data (DataTransformation ka INPUT)
            │   ├── train.csv
            │   └── test.csv
            ├── invalid/                ← invalid/drifted data
            │   ├── train.csv
            │   └── test.csv
            └── drift_report/
                └── report.yaml         ← KS test results
        """

        self.data_validation_dir: str = os.path.join(
            training_pipeline_config.artifact_dir,       # "Artifacts/timestamp"
            training_pipeline.DATA_VALIDATON_DIR_NAME    # "data_validation"
        )
        # → "Artifacts/08_24_2026_14_32_00/data_validation"

        self.valid_data_dir: str = os.path.join(
            self.data_validation_dir,
            training_pipeline.DATA_VALIDATION_VALID_DIR  # "validated"
        )
        # → "Artifacts/.../data_validation/validated"

        self.invalid_data_dir: str = os.path.join(
            self.data_validation_dir,
            training_pipeline.DATA_VALIDATION_INVALID_DIR  # "invalid"
            # dono valid aur invalid same folder point kar rahe the → galat
        )
        # → "Artifacts/.../data_validation/invalid"

        self.valid_train_file_path: str = os.path.join(
            self.valid_data_dir,
            training_pipeline.TRAIN_FILE_NAME  # "train.csv"
        )
        # → "Artifacts/.../data_validation/validated/train.csv"
        # IMP: DataTransformation yahan se padhega

        self.valid_test_file_path: str = os.path.join(
            self.valid_data_dir,
            training_pipeline.TEST_FILE_NAME  # "test.csv"
        )
        # → "Artifacts/.../data_validation/validated/test.csv"

        self.invalid_train_file_path: str = os.path.join(
            self.invalid_data_dir,
            training_pipeline.TRAIN_FILE_NAME  # "train.csv"
        )
        # → "Artifacts/.../data_validation/invalid/train.csv"
        # agar drift detect hua → yahan save hoga

        self.invalid_test_file_path: str = os.path.join(
            self.invalid_data_dir,
            training_pipeline.TEST_FILE_NAME  # "test.csv"
        )
        # → "Artifacts/.../data_validation/invalid/test.csv"

        self.drift_report_file_path: str = os.path.join(
            self.data_validation_dir,
            training_pipeline.DATA_VALIDATION_DRIFT_REPORT_DIR,      # "drift_report"
            training_pipeline.DATA_VALIDATION_DRIFT_REPORT_FILE_NAME # "report.yaml"
        )
        # → "Artifacts/.../data_validation/drift_report/report.yaml"
        # write_yaml_file() yahan KS test results save karega



# ══════════════════════════════════════════════════════════════════
# CLASS 4: Data TransformationConfig
# ══════════════════════════════════════════════════════════════════

class DataTransformationConfig:
    def __init__(self, training_pipeline_config: TrainingPipelineConfig):
        """
        DataTransformation ke liye sab paths banata hai.
        TrainingPipelineConfig inject hota hai → timestamp milta hai

        Parameters:
            training_pipeline_config (TrainingPipelineConfig):
                master config — artifact_dir milta hai isse
                → "Artifacts/08_24_2026_14_32_00"


        # IMP: .csv → .npy (numpy binary format)
        # DataTransformation numpy arrays save karta hai
        # .npy = numpy ka native format → fast load → sklearn direct use karta hai
        # .csv se zyada efficient — float64 arrays ke liye
        #
        # PATH STRUCTURE:
        # Artifacts/timestamp/
        # └── data_transformation/                    ← data_transformation_dir
        #     ├── transformed/                        ← TRANSFORMED_DATA_DIR
        #     │   ├── train.npy                       ← transformed_train_file_path
        #     │   └── test.npy                        ← transformed_test_file_path
        #     └── transformed_object/                 ← TRANSFORMED_OBJECT_DIR
        #         └── preprocessing.pkl              ← transformed_object_file_path
        #      
        """

        self.data_transformation_dir: str = os.path.join(
            training_pipeline_config.artifact_dir,           # "Artifacts/timestamp"
            training_pipeline.DATA_TRANSFORMATION_DIR_NAME   # "data_transformation"
        )
        # → "Artifacts/08_24_2026_14_32_00/data_transformation"

        self.transformed_train_file_path: str = os.path.join(
            self.data_transformation_dir,
            training_pipeline.DATA_TRANSFORMATION_TRANSFORMED_DATA_DIR,  # "transformed"
            training_pipeline.TRAIN_FILE_NAME.replace("csv", "npy")
            # "train.csv" → "train.npy"
            # IMP: .npy = numpy binary format
            # DataTransformation np.save() se save karega
            # DataValidation ne validated/train.csv save kiya tha
            # DataTransformation usse padhega → numpy array → .npy save karega
        )
        # → "Artifacts/.../data_transformation/transformed/train.npy"

        self.transformed_test_file_path: str = os.path.join(
            self.data_transformation_dir,
            training_pipeline.DATA_TRANSFORMATION_TRANSFORMED_DATA_DIR,  # "transformed"
            training_pipeline.TEST_FILE_NAME.replace("csv", "npy")
            # "test.csv" → "test.npy"
        )
        # → "Artifacts/.../data_transformation/transformed/test.npy"

        self.transformed_object_file_path: str = os.path.join(
            self.data_transformation_dir,
            training_pipeline.DATA_TRANSFORMATION_TRANSFORMED_OBJECT_DIR,  # "transformed_object"
            training_pipeline.PREPROCESSING_OBJECT_FILE_NAME               # "preprocessing.pkl"
            # IMP: KNNImputer fitted preprocessor yahan save hoga
            # predict_pipeline mein load karke naye data pe transform karega
            # same as pehle teen projects mein preprocessor.pkl tha
        )
        # → "Artifacts/.../data_transformation/transformed_object/preprocessing.pkl"



# ══════════════════════════════════════════════════════════════════
# CLASS ModelTrainerConfig
# ══════════════════════════════════════════════════════════════════
class ModelTrainerConfig:
    def __init__(self, training_pipeline_config: TrainingPipelineConfig):
        """
        ModelTrainer ke liye sab paths banata hai.

        Parameters:
            training_pipeline_config (TrainingPipelineConfig):
                master config — artifact_dir milta hai isse
                → "Artifacts/08_24_2026_14_32_00"

        PATH STRUCTURE:
        Artifacts/timestamp/
        └── model_trainer/                    ← model_trainer_dir
            └── trained_model/                ← MODEL_TRAINER_TRAIN_MODEL_DIR
                └── model.pkl                 ← trained_model_file_path
        """

        self.model_trainer_dir: str = os.path.join(
            training_pipeline_config.artifact_dir,      # "Artifacts/timestamp"
            training_pipeline.MODEL_TRAINER_DIR_NAME    # "model_trainer"
        )
        # → "Artifacts/08_24_2026_14_32_00/model_trainer"

        self.trained_model_file_path: str = os.path.join(
            self.model_trainer_dir,
            training_pipeline.MODEL_TRAINER_TRAIN_MODEL_DIR,    # "trained_model"
            training_pipeline.MODEL_TRAINER_TRAINED_MODEL_NAME  # "model.pkl"
        )
        # → "Artifacts/08_24_2026_14_32_00/model_trainer/trained_model/model.pkl"
        # IMP: PredictPipeline yahan se model load karega

        self.expected_accuracy: float = training_pipeline.MODEL_TRAINER_EXPECTED_SCORE
        # → 0.6
        # ModelTrainer check karega → agar best model 0.6 se kam → exception

        self.overfitting_underfitting_threshold: float = training_pipeline.MODEL_TRAINER_OVERFITTING_UNDER_FITTING_THRESHOLD




# ─────────────────────────────────────────────────────────────────
# FULL ARTIFACTS STRUCTURE — DATA INGESTION + VALIDATION + TRANSFORMATION + MODEL TRAINER
#
# Artifacts/
# └── 08_24_2026_14_32_00/              ← TrainingPipelineConfig timestamp
#     │
#     ├── data_ingestion/               ← DataIngestionConfig.data_ingestion_dir
#     │   ├── feature_store/            ← DATA_INGESTION_FEATURE_STORE_DIR
#     │   │   └── phishingData.csv      ← raw MongoDB data backup
#     │   └── ingested/                 ← DATA_INGESTION_INGESTED_DIR
#     │       ├── train.csv             ← DataIngestionArtifact.train_file_path
#     │       └── test.csv              ← DataIngestionArtifact.test_file_path
#     │
#     ├── data_validation/              ← DataValidationConfig.data_validation_dir
#     │   ├── validated/                ← DATA_VALIDATION_VALID_DIR
#     │   │   ├── train.csv             ← DataValidationArtifact.valid_train_file_path
#     │   │   └── test.csv              ← DataValidationArtifact.valid_test_file_path
#     │   ├── invalid/                  ← DATA_VALIDATION_INVALID_DIR
#     │   │   ├── train.csv             ← DataValidationArtifact.invalid_train_file_path
#     │   │   └── test.csv              ← DataValidationArtifact.invalid_test_file_path
#     │   └── drift_report/             ← DATA_VALIDATION_DRIFT_REPORT_DIR
#     │       └── report.yaml           ← DataValidationArtifact.drift_report_file_path
#     │
#     ├── data_transformation/          ← DataTransformationConfig.data_transformation_dir
#     │   ├── transformed/              ← DATA_TRANSFORMATION_TRANSFORMED_DATA_DIR
#     │   │   ├── train.npy             ← DataTransformationArtifact.transformed_train_file_path
#     │   │   └── test.npy              ← DataTransformationArtifact.transformed_test_file_path
#     │   └── transformed_object/       ← DATA_TRANSFORMATION_TRANSFORMED_OBJECT_DIR
#     │       └── preprocessing.pkl     ← DataTransformationArtifact.transformed_object_file_path
#     │           (fitted KNNImputer)   ← PredictPipeline load karega
#     │
#     └── model_trainer/                ← ModelTrainerConfig.model_trainer_dir
#         └── trained_model/            ← MODEL_TRAINER_TRAIN_MODEL_DIR
#             └── model.pkl             ← ModelTrainerArtifact.trained_model_file_path
#                 (best fitted model)   ← PredictPipeline load karega
#
# ─────────────────────────────────────────────────────────────────
# CHAIN — har step ka output agla step ka input hai:
#
# MongoDB Atlas
#   ↓ DataIngestion
# ingested/train.csv + test.csv        ← DataIngestionArtifact
#   ↓ DataValidation
# validated/train.csv + test.csv       ← DataValidationArtifact
# drift_report/report.yaml
#   ↓ DataTransformation
# transformed/train.npy + test.npy     ← DataTransformationArtifact
# transformed_object/preprocessing.pkl
#   ↓ ModelTrainer
# trained_model/model.pkl              ← ModelTrainerArtifact
#   ↓ PredictPipeline
# preprocessing.pkl + model.pkl → naye data pe prediction
# ─────────────────────────────────────────────────────────────────


# ─────────────────────────────────────────────────────────────────
# DRY RUN
#
# trainingpipelineconfig = TrainingPipelineConfig()
# → timestamp = "08_24_2026_14_32_00"
# → artifact_dir = "Artifacts/08_24_2026_14_32_00"
#
# dataingestionconfig = DataIngestionConfig(trainingpipelineconfig)
# → data_ingestion_dir    = "Artifacts/08_24_2026_14_32_00/data_ingestion"
# → feature_store_path    = "Artifacts/.../data_ingestion/feature_store/phishingData.csv"
# → training_file_path    = "Artifacts/.../data_ingestion/ingested/train.csv"
# → testing_file_path     = "Artifacts/.../data_ingestion/ingested/test.csv"
# → train_test_split_ratio = 0.2
# → collection_name        = "NetworkData"
# → database_name          = "ALYAN"
# ─────────────────────────────────────────────────────────────────


# ─────────────────────────────────────────────────────────────────
# COMPARISON — TEEN PEHLE PROJECTS vs IS PROJECT
# ─────────────────────────────────────────────────────────────────
#
# ┌──────────────────────┬────────────────────┬───────────────────┐
# │ Feature              │ Teen Projects      │ Network Security  │
# ├──────────────────────┼────────────────────┼───────────────────┤
# │ Config location      │ Same file mein     │ config_entity.py  │
# │                      │ @dataclass tha     │ alag file         │
# │                      │ data_ingestion.py  │                   │
# ├──────────────────────┼────────────────────┼───────────────────┤
# │ Constants            │ Hardcoded          │ constants/        │
# │                      │ "artifacts/train"  │ training_pipeline │
# │                      │ directly           │ /__init__.py      │
# ├──────────────────────┼────────────────────┼───────────────────┤
# │ Artifacts            │ artifacts/         │ Artifacts/        │
# │                      │ overwrite hoti     │ timestamp/        │
# │                      │ har run pe         │ har run alag      │
# ├──────────────────────┼────────────────────┼───────────────────┤
# │ Data source          │ CSV file           │ MongoDB Atlas     │
# │                      │ local path         │ cloud database    │
# ├──────────────────────┼────────────────────┼───────────────────┤
# │ Config injection     │ Nahi               │ Haan              │
# │                      │ @dataclass         │ DataIngestionConfig│
# │                      │ standalone tha     │ (TrainingPipeline │
# │                      │                    │ Config) inject    │
# ├──────────────────────┼────────────────────┼───────────────────┤
# │ Return type          │ tuple              │ DataIngestion     │
# │                      │ (train_path,       │ Artifact object   │
# │                      │  test_path)        │ (typed)           │
# ├──────────────────────┼────────────────────┼───────────────────┤
# │ Web framework        │ Flask              │ FastAPI           │
# │ ML tracking          │ Nahi               │ MLflow + DagsHub  │
# │ Cloud storage        │ Nahi               │ AWS S3            │
# │ CI/CD                │ Railway auto       │ GitHub Actions    │
# │                      │ deploy             │ → ECR → EC2       │
# └──────────────────────┴────────────────────┴───────────────────┘
#
# STUDENT PERFORMANCE:
#   @dataclass DataIngestionConfig in data_ingestion.py
#   artifacts/train.csv → overwrite
#   CSV se data
#   return (train_path, test_path) → simple tuple
#
# HEART DISEASE:
#   Same as Student Performance
#   Extra: threshold.pkl save kiya
#   Youden's J optimization
#
# SMS SPAM:
#   Same structure
#   Extra: Word2Vec model save kiya
#   NLP pipeline — text cleaning
#
# NETWORK SECURITY (YEH PROJECT):
#   Config ALAG FILE mein (config_entity.py)
#   Constants ALAG FILE mein (constants/)
#   Timestamped artifacts → history preserve
#   MongoDB se data (not CSV)
#   DataIngestionArtifact object return (not tuple)
#   MLflow experiment tracking
#   AWS S3 artifact sync
#   Full CI/CD pipeline
# ─────────────────────────────────────────────────────────────────