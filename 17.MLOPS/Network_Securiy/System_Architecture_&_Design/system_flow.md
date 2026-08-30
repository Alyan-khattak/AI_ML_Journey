```mermaid
flowchart TD

%% ═══════════════════════════════════════════════════
%% STYLES
%% ═══════════════════════════════════════════════════
classDef fileNode    fill:#0f1520,stroke:#00FF41,stroke-width:1px,color:#00FF41,font-family:monospace
classDef classNode   fill:#0a1a0a,stroke:#00FF41,stroke-width:2px,color:#e2e8f0,font-family:monospace
classDef funcNode    fill:#111,stroke:#00AA30,stroke-width:1px,color:#aaa,font-family:monospace,font-size:11px
classDef storageNode fill:#1a1a0a,stroke:#FFB800,stroke-width:1px,color:#FFB800,font-family:monospace
classDef artifactNode fill:#0a0a1a,stroke:#4488FF,stroke-width:1px,color:#4488FF,font-family:monospace
classDef dbNode      fill:#1a0a0a,stroke:#FF6644,stroke-width:2px,color:#FF6644,font-family:monospace
classDef configNode  fill:#0f0f1a,stroke:#AA44FF,stroke-width:1px,color:#AA44FF,font-family:monospace
classDef apiNode     fill:#0a1520,stroke:#00CCFF,stroke-width:2px,color:#00CCFF,font-family:monospace

%% ═══════════════════════════════════════════════════
%% 0. EXTERNAL SOURCES
%% ═══════════════════════════════════════════════════
subgraph EXT["⬛ EXTERNAL SOURCES"]
    MONGO[("MongoDB Atlas\nDB: ALYAN\nCollection: NetworkData\n148k+ phishing records")]:::dbNode
    ENV["📄 .env file\nMONGO_ATLAS_URI\nMLFLOW credentials"]:::storageNode
end

%% ═══════════════════════════════════════════════════
%% 1. PUSH DATA — ETL Script
%% ═══════════════════════════════════════════════════
subgraph PUSH["📁 pushdata.py — ETL (Run Once)"]
    PD1["class NetworkDataExtract"]:::classNode
    PD2["csv_to_json_converter(filepath)\n→ pd.read_csv(phishingData.csv)\n→ data.T.to_json()\n→ list of dicts"]:::funcNode
    PD3["insert_data_to_mongodb(records, db, collection)\n→ MongoClient(URI, tlsCAFile)\n→ client[ALYAN][NetworkData]\n→ collection.insert_many(records)"]:::funcNode
    PD1 --> PD2 --> PD3
end

CSV_SRC["📄 Network_Data/phishingData.csv\n11055 rows × 31 cols"]:::storageNode
CSV_SRC --> PD2
PD3 --> MONGO

%% ═══════════════════════════════════════════════════
%% 2. CONSTANTS & CONFIG
%% ═══════════════════════════════════════════════════
subgraph CONST["📁 constants/training_pipeline/__init__.py"]
    C1["TARGET_COLUMN = 'Result'\nPIPELINE_NAME = 'NetworkSecurity'\nARTIFACT_DIR = 'Artifacts'\nFILE_NAME = 'phishingData.csv'\nTRAIN_FILE_NAME = 'train.csv'\nTEST_FILE_NAME = 'test.csv'\nSCHEMA_FILE_PATH = 'data_schema/schema.yaml'"]:::configNode
    C2["DATA_INGESTION_DATABASE_NAME = 'ALYAN'\nDATA_INGESTION_COLLECTION_NAME = 'NetworkData'\nDATA_INGESTION_DIR_NAME = 'data_ingestion'\nDATA_INGESTION_FEATURE_STORE_DIR = 'feature_store'\nDATA_INGESTION_INGESTED_DIR = 'ingested'\nDATA_INGESTION_TRAIN_TEST_SPLIT_RATIO = 0.2"]:::configNode
    C3["DATA_VALIDATON_DIR_NAME = 'data_validation'\nDATA_VALIDATION_VALID_DIR = 'validated'\nDATA_VALIDATION_INVALID_DIR = 'invalid'\nDATA_VALIDATION_DRIFT_REPORT_DIR = 'drift_report'\nDATA_VALIDATION_DRIFT_REPORT_FILE_NAME = 'report.yaml'"]:::configNode
    C4["DATA_TRANSFORMATION_DIR_NAME = 'data_transformation'\nDATA_TRANSFORMATION_TRANSFORMED_DATA_DIR = 'transformed'\nDATA_TRANSFORMATION_TRANSFORMED_OBJECT_DIR = 'transformed_object'\nPREPROCESSING_OBJECT_FILE_NAME = 'preprocessing.pkl'\nDATA_TRANSFORMATION_IMPUTER_PARAMS = {\n  missing_values: NaN,\n  n_neighbors: 3,\n  weights: uniform\n}"]:::configNode
    C5["MODEL_TRAINER_DIR_NAME = 'model_trainer'\nMODEL_TRAINER_TRAIN_MODEL_DIR = 'trained_model'\nMODEL_TRAINER_TRAINED_MODEL_NAME = 'model.pkl'\nMODEL_TRAINER_EXPECTED_SCORE = 0.6\nMODEL_TRAINER_OVERFITTING_THRESHOLD = 0.05"]:::configNode
end

subgraph CE["📁 entity/config_entity.py"]
    CE0["class TrainingPipelineConfig\n__init__(timestamp=datetime.now())\n→ artifact_dir = Artifacts/timestamp"]:::classNode
    CE1["class DataIngestionConfig\n__init__(training_pipeline_config)\n→ data_ingestion_dir\n→ feature_store_file_path\n→ training_file_path\n→ testing_file_path\n→ train_test_split_ratio\n→ collection_name\n→ database_name"]:::classNode
    CE2["class DataValidationConfig\n__init__(training_pipeline_config)\n→ data_validation_dir\n→ valid_data_dir / invalid_data_dir\n→ valid_train_file_path\n→ valid_test_file_path\n→ invalid_train_file_path\n→ invalid_test_file_path\n→ drift_report_file_path"]:::classNode
    CE3["class DataTransformationConfig\n__init__(training_pipeline_config)\n→ data_transformation_dir\n→ transformed_train_file_path (.npy)\n→ transformed_test_file_path (.npy)\n→ transformed_object_file_path (.pkl)"]:::classNode
    CE4["class ModelTrainerConfig\n__init__(training_pipeline_config)\n→ model_trainer_dir\n→ trained_model_file_path\n→ expected_accuracy = 0.6\n→ overfitting_threshold = 0.05"]:::classNode
    CE0 --> CE1
    CE0 --> CE2
    CE0 --> CE3
    CE0 --> CE4
end

CONST --> CE

subgraph AE["📁 entity/artifact_entity.py"]
    AE1["@dataclass DataIngestionArtifact\n→ train_file_path: str\n→ test_file_path: str"]:::artifactNode
    AE2["@dataclass DataValidationArtifact\n→ validation_status: bool\n→ valid_train_file_path: str\n→ valid_test_file_path: str\n→ invalid_train_file_path: str\n→ invalid_test_file_path: str\n→ drift_report_file_path: str"]:::artifactNode
    AE3["@dataclass DataTransformationArtifact\n→ transformed_object_file_path: str\n→ transformed_train_file_path: str\n→ transformed_test_file_path: str"]:::artifactNode
    AE4["@dataclass ClassificationMetricArtifact\n→ f1_score: float\n→ precision_score: float\n→ recall_score: float"]:::artifactNode
    AE5["@dataclass ModelTrainerArtifact\n→ trained_model_file_path: str\n→ train_metric_artifact: ClassificationMetricArtifact\n→ test_metric_artifact: ClassificationMetricArtifact"]:::artifactNode
end

subgraph UTILS["📁 utils/main_utils/utils.py"]
    U1["save_object(file_path, obj)\n→ os.makedirs()\n→ dill.dump(obj, file_obj)"]:::funcNode
    U2["load_object(file_path)\n→ dill.load(file_obj)\n→ return object"]:::funcNode
    U3["save_numpy_array_data(file_path, array)\n→ os.makedirs()\n→ np.save(file_obj, array)"]:::funcNode
    U4["load_numpy_array(file_path)\n→ np.load(file_obj)\n→ return ndarray"]:::funcNode
    U5["read_yaml_file(file_path)\n→ yaml.safe_load()\n→ return dict"]:::funcNode
    U6["write_yaml_file(file_path, content)\n→ yaml.dump(content, file)"]:::funcNode
    U7["evaluate_models(X_train, y_train, X_test, y_test, models, params)\n→ for each model: GridSearchCV(cv=5, scoring=f1)\n→ model.set_params(**best_params)\n→ model.fit(X_train)\n→ f1_score(y_test, y_pred)\n→ return report: dict"]:::funcNode
end

subgraph MLUTILS["📁 utils/ml_utils/"]
    ML1["model/estimator.py\nclass NetworkModel\n__init__(preprocessor, model)\npredict(x)\n→ x_transform = preprocessor.transform(x)\n→ y_hat = model.predict(x_transform)\n→ return y_hat"]:::classNode
    ML2["metric/classification_metric.py\nget_classification_score(y_true, y_pred)\n→ f1_score(y_true, y_pred)\n→ precision_score(y_true, y_pred)\n→ recall_score(y_true, y_pred)\n→ return ClassificationMetricArtifact"]:::funcNode
end

subgraph SCHEMA["📁 data_schema/schema.yaml"]
    SCH["columns: [31 columns]\n  having_IP_Address: int64\n  URL_Length: int64\n  ... (29 more)\n  Result: int64\nnumerical_columns: [31 names]"]:::storageNode
end

%% ═══════════════════════════════════════════════════
%% 3. DATA INGESTION
%% ═══════════════════════════════════════════════════
subgraph DI["📁 components/data_ingestion.py"]
    DI0["class DataIngestion\n__init__(data_ingestion_config: DataIngestionConfig)"]:::classNode
    DI1["export_collection_as_dataframe()\nINPUT: config.database_name, config.collection_name\n→ MongoClient(MONGO_DB_URI, tlsCAFile, tlsAllowInvalidCertificates)\n→ client[ALYAN][NetworkData]\n→ collection.find() → list of dicts\n→ pd.DataFrame(list) → 11055 × 32 df\n→ drop _id column → 11055 × 31\n→ replace 'na' → NaN\nOUTPUT: DataFrame (11055 × 31)"]:::funcNode
    DI2["export_data_into_feature_store(dataframe)\nINPUT: DataFrame (11055 × 31)\n→ feature_store_file_path from config\n→ os.makedirs(feature_store/)\n→ df.to_csv(phishingData.csv)\nOUTPUT: same DataFrame (passthrough)\nSTORES: Artifacts/timestamp/data_ingestion/feature_store/phishingData.csv"]:::funcNode
    DI3["split_data_as_train_test(dataframe)\nINPUT: DataFrame (11055 × 31)\n→ train_test_split(df, test_size=0.2, stratify=None)\n→ train = 8844 rows, test = 2211 rows\n→ os.makedirs(ingested/)\n→ train.to_csv(train.csv)\n→ test.to_csv(test.csv)\nSTORES: Artifacts/.../ingested/train.csv\n         Artifacts/.../ingested/test.csv"]:::funcNode
    DI4["initiate_data_ingestion()\n→ export_collection_as_dataframe()\n→ export_data_into_feature_store()\n→ split_data_as_train_test()\n→ return DataIngestionArtifact(\n    train_file_path,\n    test_file_path\n  )"]:::funcNode
    DI0 --> DI1 --> DI2 --> DI3 --> DI4
end

MONGO --> DI1
CE1 --> DI0
AE1 --> DI4

DIA["🔵 DataIngestionArtifact\ntrain_file_path = Artifacts/.../ingested/train.csv\ntest_file_path  = Artifacts/.../ingested/test.csv"]:::artifactNode
DI4 --> DIA

%% ═══════════════════════════════════════════════════
%% 4. DATA VALIDATION
%% ═══════════════════════════════════════════════════
subgraph DV["📁 components/data_validation.py"]
    DV0["class DataValidation\n__init__(data_ingestion_artifact, data_validation_config)\n→ self.data_ingestion_artifact\n→ self.data_validation_config\n→ self.schema_config = read_yaml_file(SCHEMA_FILE_PATH)"]:::classNode
    DV1["@staticmethod read_data(file_path)\n→ pd.read_csv(file_path)\n→ return DataFrame"]:::funcNode
    DV2["validate_number_cols(dataframe)\nINPUT: DataFrame\n→ schema_config['columns'] → expected count = 31\n→ len(df.columns) == 31?\nOUTPUT: bool (True/False)"]:::funcNode
    DV3["check_numerical_col(dataframe)\nINPUT: DataFrame\n→ schema_config['numerical_columns']\n→ df.select_dtypes(['int64','float64'])\n→ all expected cols present?\nOUTPUT: bool"]:::funcNode
    DV4["detect_data_drift(base_df, current_df, threshold=0.05)\nINPUT: train_df, test_df\n→ for each column:\n   ks_2samp(train_col, test_col)\n   p_value >= 0.05 → no drift\n   p_value < 0.05  → drift!\n→ report = {col: {p_value, drift_status}}\n→ write_yaml_file(drift_report_file_path, report)\nOUTPUT: bool (True=no drift)"]:::funcNode
    DV5["initiate_data_validation()\n→ read_data(train_path) → train_df (8844 × 31)\n→ read_data(test_path)  → test_df  (2211 × 31)\n→ validate_number_cols(train_df)\n→ validate_number_cols(test_df)\n→ check_numerical_col(train_df)\n→ check_numerical_col(test_df)\n→ detect_data_drift(train_df, test_df)\n→ save valid train.csv + test.csv\n→ return DataValidationArtifact"]:::funcNode
    DV0 --> DV1
    DV0 --> DV2
    DV0 --> DV3
    DV0 --> DV4
    DV1 & DV2 & DV3 & DV4 --> DV5
end

DIA --> DV0
CE2 --> DV0
SCHEMA --> DV0
U5 --> DV0
U6 --> DV4

DVA["🔵 DataValidationArtifact\nvalidation_status = True\nvalid_train_file_path = Artifacts/.../validated/train.csv\nvalid_test_file_path  = Artifacts/.../validated/test.csv\ninvalid_train_file_path = Artifacts/.../invalid/train.csv\ninvalid_test_file_path  = Artifacts/.../invalid/test.csv\ndrift_report_file_path  = Artifacts/.../drift_report/report.yaml"]:::artifactNode
DV5 --> DVA

DRIFT_STORE["💛 Artifacts/.../data_validation/\n├── validated/train.csv (8844 rows)\n├── validated/test.csv  (2211 rows)\n├── invalid/train.csv\n├── invalid/test.csv\n└── drift_report/report.yaml\n    {col: {p_value: 0.43, drift_status: false}}"]:::storageNode
DV5 --> DRIFT_STORE

%% ═══════════════════════════════════════════════════
%% 5. DATA TRANSFORMATION
%% ═══════════════════════════════════════════════════
subgraph DT["📁 components/data_transformation.py"]
    DT0["class DataTransformation\n__init__(data_validation_artifact, data_transformation_config)\n→ self.data_validation_artifact\n→ self.data_transformation_config"]:::classNode
    DT1["@staticmethod read_data(file_path)\n→ pd.read_csv()\n→ return DataFrame"]:::funcNode
    DT2["get_data_transformer_object()\n→ KNNImputer(**DATA_TRANSFORMATION_IMPUTER_PARAMS)\n   missing_values=NaN, n_neighbors=3, weights='uniform'\n→ Pipeline(steps=[('imputer', imputer)])\nOUTPUT: fitted Pipeline object"]:::funcNode
    DT3["initiate_data_transformation()\nINPUT: valid_train.csv (8844 × 31)\n        valid_test.csv  (2211 × 31)\n\nSTEP 1: read_data(valid_train_path) → train_df\n         read_data(valid_test_path)  → test_df\n\nSTEP 2: X/y split\n  X_train = train_df.drop('Result') → (8844 × 30)\n  y_train = train_df['Result']\n  y_train.replace(-1, 0)  ← -1→0 binary conversion\n  X_test  = test_df.drop('Result')  → (2211 × 30)\n  y_test  = test_df['Result'].replace(-1, 0)\n\nSTEP 3: preprocessor = get_data_transformer_object()\n\nSTEP 4: X_train_t = preprocessor.fit_transform(X_train)\n         X_test_t  = preprocessor.transform(X_test)\n         (fit only on train — no leakage)\n\nSTEP 5: train_arr = np.c_[X_train_t, y_train] → (8844 × 31)\n         test_arr  = np.c_[X_test_t,  y_test]  → (2211 × 31)\n\nSTEP 6: save_numpy_array_data(train_file_path, train_arr)\n         save_numpy_array_data(test_file_path,  test_arr)\n         save_object(object_file_path, preprocessor)\n\nOUTPUT: DataTransformationArtifact"]:::funcNode
    DT0 --> DT1
    DT0 --> DT2
    DT1 & DT2 --> DT3
end

DVA --> DT0
CE3 --> DT0
U1 --> DT3
U3 --> DT3

DTA["🔵 DataTransformationArtifact\ntransformed_object_file_path = Artifacts/.../transformed_object/preprocessing.pkl\ntransformed_train_file_path  = Artifacts/.../transformed/train.npy\ntransformed_test_file_path   = Artifacts/.../transformed/test.npy"]:::artifactNode
DT3 --> DTA

TRANS_STORE["💛 Artifacts/.../data_transformation/\n├── transformed/\n│   ├── train.npy (8844 × 31 numpy array)\n│   └── test.npy  (2211 × 31 numpy array)\n└── transformed_object/\n    └── preprocessing.pkl (fitted KNNImputer Pipeline)"]:::storageNode
DT3 --> TRANS_STORE

%% ═══════════════════════════════════════════════════
%% 6. MODEL TRAINER
%% ═══════════════════════════════════════════════════
subgraph MT["📁 components/model_trainer.py"]
    MT0["class ModelTrainer\n__init__(model_trainer_config, data_transformation_artifact)\n→ self.model_trainer_config\n→ self.data_transformation_artifact"]:::classNode
    MT1["track_mlflow(best_model, classificationmetric)\n→ mlflow.start_run()\n→ mlflow.log_metric('f1_score', ...)\n→ mlflow.log_metric('precision_score', ...)\n→ mlflow.log_metric('recall_score', ...)\n→ mlflow.sklearn.log_model(best_model, 'model')\n→ DagsHub remote tracking"]:::funcNode
    MT2["train_model(X_train, y_train, X_test, y_test)\n\nMODELS:\n  RandomForestClassifier(verbose=0)\n  DecisionTreeClassifier()\n  GradientBoostingClassifier(verbose=0)\n  LogisticRegression(verbose=0)\n  AdaBoostClassifier()\n\nPARAMS (GridSearchCV grids):\n  RF: n_estimators=[8,16,32,128,256]\n  DT: criterion=[gini,entropy,log_loss]\n  GB: learning_rate,subsample,n_estimators\n  LR: {} (no params)\n  AB: learning_rate,n_estimators\n\n→ evaluate_models() → report dict\n→ best_model = max(report, key=f1)\n→ if best_f1 < 0.6 → raise Exception\n\n→ y_train_pred = best_model.predict(X_train)\n→ train_metric  = get_classification_score(y_train, y_train_pred)\n→ track_mlflow(best_model, train_metric)\n\n→ y_test_pred  = best_model.predict(X_test)\n→ test_metric   = get_classification_score(y_test, y_test_pred)\n→ track_mlflow(best_model, test_metric)\n\n→ |train_f1 - test_f1| > 0.05? → log WARNING\n\n→ preprocessor = load_object(preprocessing.pkl)\n→ network_model = NetworkModel(preprocessor, best_model)\n→ save_object(trained_model_file_path, network_model)\n→ save_object('final_model/model.pkl', best_model)\n→ save_object('final_model/preprocessor.pkl', preprocessor)\n\n→ return ModelTrainerArtifact"]:::funcNode
    MT3["initiate_model_trainer()\n→ train_arr = load_numpy_array(train.npy)\n→ test_arr  = load_numpy_array(test.npy)\n→ X_train = train_arr[:, :-1] (8844 × 30)\n→ y_train = train_arr[:, -1]  (8844,)\n→ X_test  = test_arr[:, :-1]  (2211 × 30)\n→ y_test  = test_arr[:, -1]   (2211,)\n→ return train_model(X_train, y_train, X_test, y_test)"]:::funcNode
    MT0 --> MT1
    MT0 --> MT2
    MT0 --> MT3
    MT3 --> MT2
    MT2 --> MT1
end

DTA --> MT0
CE4 --> MT0
U2 --> MT3
U4 --> MT3
U7 --> MT2
ML1 --> MT2
ML2 --> MT2
U1 --> MT2

MLFLOW["☁️ MLflow / DagsHub\nExperiment: NetworkSecurity\nRuns: train_metric + test_metric\nMetrics: f1, precision, recall\nModel artifacts logged"]:::dbNode
MT1 --> MLFLOW

MTA["🔵 ModelTrainerArtifact\ntrained_model_file_path = Artifacts/.../model_trainer/trained_model/model.pkl\ntrain_metric = ClassificationMetricArtifact(f1=0.9916, precision=0.9887, recall=0.9945)\ntest_metric  = ClassificationMetricArtifact(f1=0.9716, precision=0.9589, recall=0.9846)"]:::artifactNode
MT2 --> MTA

MODEL_STORE["💛 Artifacts/.../model_trainer/trained_model/model.pkl\n  (NetworkModel: preprocessor + RandomForest)\n\nfinal_model/\n  ├── model.pkl        (best_model only)\n  └── preprocessor.pkl (fitted KNNImputer)"]:::storageNode
MT2 --> MODEL_STORE

%% ═══════════════════════════════════════════════════
%% 7. TRAINING PIPELINE ORCHESTRATOR
%% ═══════════════════════════════════════════════════
subgraph TP["📁 pipeline/training_pipeline.py"]
    TP0["class TrainingPipeline\n__init__()\n→ self.training_pipeline_config = TrainingPipelineConfig()"]:::classNode
    TP1["start_data_ingestion()\n→ DataIngestionConfig(training_pipeline_config)\n→ DataIngestion(config)\n→ .initiate_data_ingestion()\n→ return DataIngestionArtifact"]:::funcNode
    TP2["start_data_validation(data_ingestion_artifact)\n→ DataValidationConfig(training_pipeline_config)\n→ DataValidation(artifact, config)\n→ .initiate_data_validation()\n→ return DataValidationArtifact"]:::funcNode
    TP3["start_data_transformation(data_validation_artifact)\n→ DataTransformationConfig(training_pipeline_config)\n→ DataTransformation(artifact, config)\n→ .initiate_data_transformation()\n→ return DataTransformationArtifact"]:::funcNode
    TP4["start_model_trainer(data_transformation_artifact)\n→ ModelTrainerConfig(training_pipeline_config)\n→ ModelTrainer(config, artifact)\n→ .initiate_model_trainer()\n→ return ModelTrainerArtifact"]:::funcNode
    TP5["run_pipeline()\n→ start_data_ingestion()\n→ start_data_validation()\n→ start_data_transformation()\n→ start_model_trainer()\n→ return ModelTrainerArtifact"]:::funcNode
    TP0 --> TP5
    TP5 --> TP1 --> TP2 --> TP3 --> TP4
end

MTA --> TP4

%% ═══════════════════════════════════════════════════
%% 8. FASTAPI APP
%% ═══════════════════════════════════════════════════
subgraph API["📁 app.py — FastAPI Backend"]
    API0["app = FastAPI(title='Network Security MLOps')\nCORSMiddleware(allow_origins=['*'])\ntemplates = Jinja2Templates('./templates')"]:::apiNode
    API1["GET /\n→ TemplateResponse('index.html')\n→ Landing page"]:::funcNode
    API2["GET /train\n→ TrainingPipeline()\n→ .run_pipeline()\n→ Response('Training Successful')"]:::funcNode
    API3["GET /predict\n→ TemplateResponse('predict.html')\n→ CSV upload form"]:::funcNode
    API4["POST /predict\n→ UploadFile (CSV)\n→ pd.read_csv(file)\n→ load_object('final_model/preprocessor.pkl')\n→ load_object('final_model/model.pkl')\n→ NetworkModel(preprocessor, model)\n→ .predict(df) → y_pred\n→ df['predicted_column'] = y_pred\n→ df.to_csv('prediction_output/output.csv')\n→ df.to_html()\n→ TemplateResponse('table.html', table)"]:::funcNode
    API5["GET /predict/manual\n→ TemplateResponse('predict_manual.html')\n→ Manual input form"]:::funcNode
    API6["POST /predict/manual\nNetworkDataInput (Pydantic, 30 fields)\n→ data.model_dump() → dict\n→ pd.DataFrame([dict])\n→ load_object('final_model/preprocessor.pkl')\n→ load_object('final_model/model.pkl')\n→ NetworkModel.predict(df)[0]\n→ label = 'Phishing' if 1 else 'Legitimate'\n→ return {prediction, label, message}"]:::funcNode
    API0 --> API1 & API2 & API3 & API4 & API5 & API6
end

MODEL_STORE --> API4
MODEL_STORE --> API6
TP5 --> API2

subgraph TEMPLATES["📁 templates/"]
    T1["index.html — landing page\nStats bento, pipeline steps\nQuick action buttons"]:::fileNode
    T2["predict.html — CSV upload form\nDragdrop zone, file confirmation\nValue legend: 1/-1/0"]:::fileNode
    T3["table.html — results\nSummary strip (phish/legit count)\nStyled prediction badges"]:::fileNode
    T4["predict_manual.html — manual form\n30 feature inputs (4 groups)\nFetch POST → inline result"]:::fileNode
end

API1 --> T1
API3 --> T2
API4 --> T3
API5 --> T4

%% ═══════════════════════════════════════════════════
%% 9. ARTIFACTS DIRECTORY FINAL STATE
%% ═══════════════════════════════════════════════════
subgraph ARTS["💛 Artifacts/timestamp/ — Final State"]
    ART1["data_ingestion/\n├── feature_store/phishingData.csv\n└── ingested/\n    ├── train.csv (8844 rows)\n    └── test.csv  (2211 rows)"]:::storageNode
    ART2["data_validation/\n├── validated/\n│   ├── train.csv\n│   └── test.csv\n├── invalid/\n│   ├── train.csv\n│   └── test.csv\n└── drift_report/report.yaml"]:::storageNode
    ART3["data_transformation/\n├── transformed/\n│   ├── train.npy (8844 × 31)\n│   └── test.npy  (2211 × 31)\n└── transformed_object/\n    └── preprocessing.pkl"]:::storageNode
    ART4["model_trainer/\n└── trained_model/\n    └── model.pkl (NetworkModel)"]:::storageNode
end

ENV --> DI1
```
