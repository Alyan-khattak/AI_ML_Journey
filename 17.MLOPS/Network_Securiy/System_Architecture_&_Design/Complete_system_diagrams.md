# NetworkSecurity MLOps — Complete Mermaid Diagrams

---

## DIAGRAM 1: High-Level Pipeline Overview

```mermaid
flowchart TD
    MONGO[("🗄️ MongoDB Atlas\nDB: ALYAN\nCollection: NetworkData\n11055 records · 31 cols")]
    ENV["📄 .env\nMONGO_ATLAS_URI\nMLFLOW credentials"]
    CONST["📁 constants/training_pipeline/__init__.py\nTARGET_COLUMN · ARTIFACT_DIR\nSCHEMA_FILE_PATH · IMPUTER_PARAMS\nEXPECTED_SCORE · OVERFIT_THRESHOLD"]
    CE["📁 entity/config_entity.py\nTrainingPipelineConfig\nDataIngestionConfig\nDataValidationConfig\nDataTransformationConfig\nModelTrainerConfig"]
    AE["📁 entity/artifact_entity.py\nDataIngestionArtifact\nDataValidationArtifact\nDataTransformationArtifact\nClassificationMetricArtifact\nModelTrainerArtifact"]
    DI["📁 components/data_ingestion.py\nclass DataIngestion"]
    DV["📁 components/data_validation.py\nclass DataValidation"]
    DT["📁 components/data_transformation.py\nclass DataTransformation"]
    MT["📁 components/model_trainer.py\nclass ModelTrainer"]
    TP["📁 pipeline/training_pipeline.py\nclass TrainingPipeline\nrun_pipeline()"]
    API["📁 app.py — FastAPI\n6 routes · uvicorn:8000"]
    MLFLOW["☁️ MLflow / DagsHub\nexperiment tracking"]
    DISK["💾 Artifacts/timestamp/\nfeature_store · ingested\nvalidated · drift_report\ntransformed · model.pkl"]

    CONST --> CE
    CE --> DI & DV & DT & MT
    AE --> DI & DV & DT & MT
    MONGO --> DI
    ENV --> DI
    DI -->|DataIngestionArtifact| DV
    DV -->|DataValidationArtifact| DT
    DT -->|DataTransformationArtifact| MT
    MT -->|ModelTrainerArtifact| MLFLOW
    MT --> DISK
    TP --> DI & DV & DT & MT
    API -->|GET /train| TP
    API -->|POST /predict| DISK
```

---

## DIAGRAM 2: Data Ingestion — Detailed

```mermaid
flowchart TD
    subgraph CONFIG["DataIngestionConfig (from config_entity.py)"]
        C1["database_name = 'ALYAN'"]
        C2["collection_name = 'NetworkData'"]
        C3["train_test_split_ratio = 0.2"]
        C4["feature_store_file_path\n= Artifacts/timestamp/data_ingestion/feature_store/phishingData.csv"]
        C5["training_file_path\n= Artifacts/timestamp/data_ingestion/ingested/train.csv"]
        C6["testing_file_path\n= Artifacts/timestamp/data_ingestion/ingested/test.csv"]
    end

    subgraph DI["class DataIngestion — data_ingestion.py"]
        INIT["__init__(data_ingestion_config)\n→ self.data_ingestion_config = config"]

        subgraph M1["export_collection_as_dataframe()"]
            M1A["MongoClient(MONGO_DB_URI\n  tlsCAFile=certifi.where()\n  tlsAllowInvalidCertificates=True)"]
            M1B["client['ALYAN']['NetworkData']"]
            M1C["collection.find() → cursor"]
            M1D["pd.DataFrame(list(cursor))\n→ 11055 × 32 DataFrame"]
            M1E["drop '_id' column\n→ 11055 × 31"]
            M1F["replace 'na' → np.nan\n→ 11055 × 31 with NaN"]
            M1A-->M1B-->M1C-->M1D-->M1E-->M1F
        end

        subgraph M2["export_data_into_feature_store(dataframe)"]
            M2A["os.makedirs(feature_store/, exist_ok=True)"]
            M2B["df.to_csv(phishingData.csv, index=False)"]
            M2C["return dataframe (passthrough)"]
            M2A-->M2B-->M2C
        end

        subgraph M3["split_data_as_train_test(dataframe)"]
            M3A["train_test_split(df, test_size=0.2)"]
            M3B["train = 8844 rows · test = 2211 rows"]
            M3C["os.makedirs(ingested/, exist_ok=True)"]
            M3D["train.to_csv(train.csv, index=False)"]
            M3E["test.to_csv(test.csv, index=False)"]
            M3A-->M3B-->M3C-->M3D-->M3E
        end

        subgraph M4["initiate_data_ingestion()"]
            M4A["call export_collection_as_dataframe()"]
            M4B["call export_data_into_feature_store(df)"]
            M4C["call split_data_as_train_test(df)"]
            M4D["return DataIngestionArtifact(\n  train_file_path,\n  test_file_path\n)"]
            M4A-->M4B-->M4C-->M4D
        end

        INIT --> M1 --> M2 --> M3 --> M4
    end

    subgraph OUT["📤 DataIngestionArtifact"]
        O1["train_file_path:\nArtifacts/.../ingested/train.csv"]
        O2["test_file_path:\nArtifacts/.../ingested/test.csv"]
    end

    subgraph STORE["💾 Disk Artifacts"]
        S1["feature_store/phishingData.csv\n11055 × 31 · raw backup"]
        S2["ingested/train.csv · 8844 rows"]
        S3["ingested/test.csv  · 2211 rows"]
    end

    MONGO[("MongoDB Atlas")] --> M1A
    CONFIG --> INIT
    M2B --> S1
    M3D --> S2
    M3E --> S3
    M4D --> OUT
    OUT -->|passed to| DV_NEXT["DataValidation (next step)"]
```

---

## DIAGRAM 3: Data Validation — Detailed

```mermaid
flowchart TD
    subgraph IN["📥 Inputs"]
        I1["DataIngestionArtifact\n· train_file_path\n· test_file_path"]
        I2["DataValidationConfig\n· valid_train_file_path\n· valid_test_file_path\n· invalid_train_file_path\n· drift_report_file_path"]
        I3["data_schema/schema.yaml\ncolumns: [31 cols]\nnumerical_columns: [31 cols]"]
    end

    subgraph DV["class DataValidation — data_validation.py"]
        INIT["__init__(artifact, config)\n→ self.data_ingestion_artifact\n→ self.data_validation_config\n→ self.schema_config = read_yaml_file(SCHEMA_FILE_PATH)"]

        RD["@staticmethod read_data(file_path)\n→ pd.read_csv()\n→ return DataFrame"]

        subgraph VNC["validate_number_cols(dataframe)"]
            VNC1["expected = len(schema_config['columns']) = 31"]
            VNC2["actual = len(df.columns)"]
            VNC3{{"actual == 31?"}}
            VNC4["return True ✅"]
            VNC5["return False ❌"]
            VNC1-->VNC2-->VNC3
            VNC3-->|Yes|VNC4
            VNC3-->|No|VNC5
        end

        subgraph CNC["check_numerical_col(dataframe)"]
            CNC1["expected_num_cols = schema['numerical_columns']"]
            CNC2["actual_num = df.select_dtypes(['int64','float64']).columns"]
            CNC3{{"all expected in actual?"}}
            CNC4["return True ✅"]
            CNC5["return False ❌"]
            CNC1-->CNC2-->CNC3
            CNC3-->|Yes|CNC4
            CNC3-->|No|CNC5
        end

        subgraph DDR["detect_data_drift(base_df, current_df, threshold=0.05)"]
            DDR1["report = {}; status = True"]
            DDR2["for each column in base_df.columns:"]
            DDR3["ks_2samp(train_col, test_col)\n→ statistic + p_value"]
            DDR4{{"p_value >= 0.05?"}}
            DDR5["is_found = False\nno drift ✅"]
            DDR6["is_found = True\nstatus = False ❌\ndrift detected!"]
            DDR7["report[col] = {p_value, drift_status}"]
            DDR8["write_yaml_file(drift_report_path, report)"]
            DDR9["return status (True=no drift)"]
            DDR1-->DDR2-->DDR3-->DDR4
            DDR4-->|Yes|DDR5-->DDR7
            DDR4-->|No|DDR6-->DDR7
            DDR7-->DDR2
            DDR7-->DDR8-->DDR9
        end

        subgraph IDV["initiate_data_validation()"]
            IDV1["train_df = read_data(train_file_path)\ntest_df  = read_data(test_file_path)"]
            IDV2["validate_number_cols(train_df)\nvalidate_number_cols(test_df)"]
            IDV3["check_numerical_col(train_df)\ncheck_numerical_col(test_df)"]
            IDV4["detect_data_drift(train_df, test_df)"]
            IDV5["os.makedirs(validated/)\ntrain_df.to_csv(valid_train_path)\ntest_df.to_csv(valid_test_path)"]
            IDV6["return DataValidationArtifact(...)"]
            IDV1-->IDV2-->IDV3-->IDV4-->IDV5-->IDV6
        end

        INIT --> RD
        INIT --> VNC
        INIT --> CNC
        INIT --> DDR
        RD & VNC & CNC & DDR --> IDV
    end

    subgraph OUT["📤 DataValidationArtifact"]
        O1["validation_status: bool"]
        O2["valid_train_file_path:\nArtifacts/.../validated/train.csv"]
        O3["valid_test_file_path:\nArtifacts/.../validated/test.csv"]
        O4["invalid_train_file_path:\nArtifacts/.../invalid/train.csv"]
        O5["drift_report_file_path:\nArtifacts/.../drift_report/report.yaml"]
    end

    IN --> INIT
    IDV6 --> OUT
    OUT -->|passed to| DT_NEXT["DataTransformation (next step)"]
```

---

## DIAGRAM 4: Data Transformation — Detailed

```mermaid
flowchart TD
    subgraph IN["📥 Inputs"]
        I1["DataValidationArtifact\n· valid_train_file_path\n· valid_test_file_path"]
        I2["DataTransformationConfig\n· transformed_train_file_path (.npy)\n· transformed_test_file_path  (.npy)\n· transformed_object_file_path (.pkl)"]
        I3["CONSTANTS\nDATA_TRANSFORMATION_IMPUTER_PARAMS:\n  missing_values=NaN\n  n_neighbors=3\n  weights='uniform'\nTARGET_COLUMN='Result'"]
    end

    subgraph DT["class DataTransformation — data_transformation.py"]
        INIT["__init__(data_validation_artifact, data_transformation_config)\n→ self.data_validation_artifact\n→ self.data_transformation_config"]

        RD["@staticmethod read_data(file_path)\n→ pd.read_csv() → DataFrame"]

        subgraph GTO["get_data_transformer_object()"]
            GTO1["KNNImputer(**DATA_TRANSFORMATION_IMPUTER_PARAMS)\n  missing_values=NaN\n  n_neighbors=3\n  weights='uniform'"]
            GTO2["Pipeline(steps=[('imputer', imputer)])\nWHY PIPELINE?\n→ steps chain karta hai\n→ baad mein steps add easy\n→ fit/transform sequentially"]
            GTO3["return Pipeline object"]
            GTO1-->GTO2-->GTO3
        end

        subgraph IDT["initiate_data_transformation()"]
            IDT1["read_data(valid_train.csv) → train_df (8844×31)\nread_data(valid_test.csv)  → test_df  (2211×31)"]

            subgraph XY["X/y Split + Target Convert"]
                XY1["X_train = train_df.drop('Result') → (8844×30)"]
                XY2["y_train = train_df['Result']"]
                XY3["y_train.replace(-1, 0)\nWHY? sklearn → 0/1 expect karta hai\n-1 = legitimate → 0 convert"]
                XY4["X_test = test_df.drop('Result') → (2211×30)"]
                XY5["y_test  = test_df['Result'].replace(-1, 0)"]
                XY1-->XY2-->XY3
                XY4-->XY5
            end

            IDT2["preprocessor = get_data_transformer_object()\n→ KNNImputer Pipeline"]

            subgraph FT["Fit + Transform"]
                FT1["X_train_t = preprocessor.fit_transform(X_train)\nFIT on train ONLY — no leakage!\nKNN neighbors calculated from train data\nNaN filled with avg of 3 nearest neighbors"]
                FT2["X_test_t = preprocessor.transform(X_test)\nTRANSFORM ONLY — no fit!\nTrain's neighbors used for test NaN fill"]
                FT1-->FT2
            end

            subgraph STACK["np.c_ Stack"]
                ST1["train_arr = np.c_[X_train_t, y_train]\n→ shape: (8844, 31)\nlast col = label (0/1)"]
                ST2["test_arr = np.c_[X_test_t, y_test]\n→ shape: (2211, 31)\nlast col = label (0/1)"]
            end

            subgraph SAVE["Save Artifacts"]
                SV1["save_numpy_array_data(\n  transformed_train_file_path,\n  train_arr\n) → train.npy"]
                SV2["save_numpy_array_data(\n  transformed_test_file_path,\n  test_arr\n) → test.npy"]
                SV3["save_object(\n  transformed_object_file_path,\n  preprocessor\n) → preprocessing.pkl"]
            end

            IDT6["return DataTransformationArtifact(...)"]

            IDT1-->XY-->IDT2-->FT-->STACK-->SAVE-->IDT6
        end

        INIT --> RD & GTO
        GTO & RD --> IDT
    end

    subgraph OUT["📤 DataTransformationArtifact"]
        O1["transformed_object_file_path:\nArtifacts/.../transformed_object/preprocessing.pkl"]
        O2["transformed_train_file_path:\nArtifacts/.../transformed/train.npy\nshape: (8844, 31)"]
        O3["transformed_test_file_path:\nArtifacts/.../transformed/test.npy\nshape: (2211, 31)"]
    end

    IN --> INIT
    IDT6 --> OUT
    OUT -->|passed to| MT_NEXT["ModelTrainer (next step)"]
```

---

## DIAGRAM 5: Model Trainer — Detailed

```mermaid
flowchart TD
    subgraph IN["📥 Inputs"]
        I1["DataTransformationArtifact\n· transformed_train_file_path (train.npy)\n· transformed_test_file_path  (test.npy)\n· transformed_object_file_path (preprocessing.pkl)"]
        I2["ModelTrainerConfig\n· trained_model_file_path\n· expected_accuracy = 0.6\n· overfitting_threshold = 0.05"]
    end

    subgraph MT["class ModelTrainer — model_trainer.py"]
        INIT["__init__(model_trainer_config, data_transformation_artifact)"]

        subgraph TM["track_mlflow(best_model, classificationmetric)"]
            TM1["mlflow.start_run()"]
            TM2["mlflow.log_metric('f1_score', ...)"]
            TM3["mlflow.log_metric('precision_score', ...)"]
            TM4["mlflow.log_metric('recall_score', ...)"]
            TM5["mlflow.sklearn.log_model(best_model, 'model')\n→ DagsHub remote sync"]
            TM1-->TM2-->TM3-->TM4-->TM5
        end

        subgraph TRAINM["train_model(X_train, y_train, X_test, y_test)"]
            subgraph MODELS["Define Models + Params"]
                M1["RandomForestClassifier(verbose=0)\nparams: n_estimators=[8,16,32,128,256]"]
                M2["DecisionTreeClassifier()\nparams: criterion=[gini,entropy,log_loss]"]
                M3["GradientBoostingClassifier(verbose=0)\nparams: learning_rate,subsample,n_estimators"]
                M4["LogisticRegression(verbose=0)\nparams: {} (no grid)"]
                M5["AdaBoostClassifier()\nparams: learning_rate,n_estimators"]
            end

            EVAL["evaluate_models(X_train,y_train,X_test,y_test,models,params)\n→ GridSearchCV(cv=5, scoring='f1', n_jobs=-1) per model\n→ model.set_params(**best_params)\n→ model.fit(X_train)\n→ f1_score(y_test, y_pred)\n→ return {model_name: test_f1}"]

            SEL{{"best_f1 >= 0.6?"}}
            SEL_NO["raise Exception\n'No best model found'"]
            SEL_YES["best_model = max(report, key=f1)\nbest_model_name = RandomForest\nbest_f1 = 0.9716"]

            TRAIN_M["y_train_pred = best_model.predict(X_train)\ntrain_metric = get_classification_score(y_train, y_train_pred)\n→ ClassificationMetricArtifact\n  f1=0.9916 · precision=0.9887 · recall=0.9945\ntrack_mlflow(best_model, train_metric)"]

            TEST_M["y_test_pred = best_model.predict(X_test)\ntest_metric = get_classification_score(y_test, y_test_pred)\n→ ClassificationMetricArtifact\n  f1=0.9716 · precision=0.9589 · recall=0.9846\ntrack_mlflow(best_model, test_metric)"]

            OFC{{"abs(train_f1 - test_f1) > 0.05?"}}
            OFC_YES["log WARNING: Overfitting/Underfitting\n|0.9916 - 0.9716| = 0.02 < 0.05 ✅"]
            OFC_NO["pass — no overfit"]

            NWRAP["preprocessor = load_object(preprocessing.pkl)\nnetwork_model = NetworkModel(preprocessor, best_model)\nsave_object(trained_model_file_path, network_model)\nsave_object('final_model/model.pkl', best_model)\nsave_object('final_model/preprocessor.pkl', preprocessor)"]

            RET["return ModelTrainerArtifact(\n  trained_model_file_path,\n  train_metric_artifact,\n  test_metric_artifact\n)"]

            MODELS --> EVAL --> SEL
            SEL -->|No| SEL_NO
            SEL -->|Yes| SEL_YES --> TRAIN_M --> TEST_M --> OFC
            OFC -->|Yes| OFC_YES --> NWRAP
            OFC -->|No| OFC_NO --> NWRAP
            NWRAP --> RET
        end

        subgraph IMT["initiate_model_trainer()"]
            IMT1["train_arr = load_numpy_array(train.npy) → (8844,31)"]
            IMT2["test_arr  = load_numpy_array(test.npy)  → (2211,31)"]
            IMT3["X_train = train_arr[:, :-1] → (8844,30)\ny_train = train_arr[:, -1]  → (8844,)"]
            IMT4["X_test  = test_arr[:, :-1]  → (2211,30)\ny_test  = test_arr[:, -1]   → (2211,)"]
            IMT5["return train_model(X_train, y_train, X_test, y_test)"]
            IMT1-->IMT2-->IMT3-->IMT4-->IMT5
        end

        INIT --> TM & TRAINM & IMT
        IMT --> TRAINM
    end

    subgraph OUT["📤 ModelTrainerArtifact"]
        O1["trained_model_file_path:\nArtifacts/.../model_trainer/trained_model/model.pkl"]
        O2["train_metric_artifact:\nClassificationMetricArtifact\n  f1=0.9916 · precision=0.9887 · recall=0.9945"]
        O3["test_metric_artifact:\nClassificationMetricArtifact\n  f1=0.9716 · precision=0.9589 · recall=0.9846"]
    end

    subgraph DISK["💾 Saved to Disk"]
        D1["Artifacts/.../model_trainer/trained_model/model.pkl\n(NetworkModel: preprocessor + RandomForest)"]
        D2["final_model/model.pkl\n(RandomForest only)"]
        D3["final_model/preprocessor.pkl\n(fitted KNNImputer Pipeline)"]
    end

    IN --> INIT
    RET --> OUT
    NWRAP --> DISK
    OUT -->|passed to| API_NEXT["FastAPI (serving)"]
    DISK -->|loaded by| API_NEXT
```

---

## DIAGRAM 6: FastAPI — Routes & Prediction Flow

```mermaid
flowchart TD
    subgraph SETUP["app.py Setup"]
        A0["app = FastAPI(title='Network Security MLOps')"]
        A1["CORSMiddleware(allow_origins=['*']\n  allow_methods=['*']\n  allow_headers=['*']\n  allow_credentials=True)"]
        A2["templates = Jinja2Templates('./templates')"]
        A3["client = MongoClient(MONGO_ATLAS_URI, tlsCAFile=ca)\ndatabase   = client['ALYAN']\ncollection = database['NetworkData']"]
        A4["uvicorn.run(app, host='0.0.0.0', port=8000)"]
    end

    subgraph ROUTES["FastAPI Routes"]
        R1["GET /\n→ TemplateResponse(index.html)\n→ landing page"]

        subgraph R2["GET /train"]
            R2A["TrainingPipeline()"]
            R2B["run_pipeline()\n→ DataIngestion\n→ DataValidation\n→ DataTransformation\n→ ModelTrainer"]
            R2C["Response('Training Successful')"]
            R2A-->R2B-->R2C
        end

        R3["GET /predict\n→ TemplateResponse(predict.html)\n→ CSV upload form"]

        subgraph R4["POST /predict (CSV batch)"]
            R4A["UploadFile(file, accept='.csv')"]
            R4B["pd.read_csv(file.file) → DataFrame (N×30)"]
            R4C["load_object('final_model/preprocessor.pkl')"]
            R4D["load_object('final_model/model.pkl')"]
            R4E["NetworkModel(preprocessor, model)"]
            R4F["network_model.predict(df)\n→ preprocessor.transform(df)\n→ model.predict(X_transformed)\n→ y_pred = [0,1,0,1,...]"]
            R4G["df['predicted_column'] = y_pred"]
            R4H["df.to_csv('prediction_output/output.csv')"]
            R4I["df.to_html(classes='table table-striped')"]
            R4J["TemplateResponse('table.html'\n  context={table: html})"]
            R4A-->R4B-->R4C-->R4D-->R4E-->R4F-->R4G-->R4H-->R4I-->R4J
        end

        R5["GET /predict/manual\n→ TemplateResponse(predict_manual.html)\n→ 30-field input form"]

        subgraph R6["POST /predict/manual"]
            R6A["NetworkDataInput (Pydantic BaseModel)\n30 int fields:\nhaving_IP_Address, URL_Length,\nShortining_Service, ... Statistical_report\nAuto validates types · 422 if missing"]
            R6B["data.model_dump() → dict"]
            R6C["pd.DataFrame([dict]) → (1×30)"]
            R6D["load_object('final_model/preprocessor.pkl')\nload_object('final_model/model.pkl')"]
            R6E["NetworkModel(preprocessor, model)"]
            R6F["network_model.predict(df)[0]\n→ single prediction"]
            R6G{{"prediction == 1?"}}
            R6H["label = 'Phishing'"]
            R6I["label = 'Legitimate'"]
            R6J["return JSON:\n{prediction: 0/1\n label: str\n message: str}"]
            R6A-->R6B-->R6C-->R6D-->R6E-->R6F-->R6G
            R6G-->|Yes|R6H-->R6J
            R6G-->|No|R6I-->R6J
        end
    end

    subgraph TEMPLATES["templates/"]
        T1["index.html\nStats bento · pipeline steps\nQuick action buttons"]
        T2["predict.html\nCSV drag-drop · file confirm\nValue legend: 1/-1/0"]
        T3["table.html\nBatch results · phish/legit badges\nSummary strip (count + threat rate)"]
        T4["predict_manual.html\n30 inputs (4 groups)\nFetch POST → inline result\nNo page reload"]
    end

    SETUP --> ROUTES
    R1 --> T1
    R3 --> T2
    R4J --> T3
    R5 --> T4
```

---

## DIAGRAM 7: Training Pipeline Orchestrator

```mermaid
flowchart TD
    subgraph TP["class TrainingPipeline — pipeline/training_pipeline.py"]
        INIT["__init__()\n→ self.training_pipeline_config = TrainingPipelineConfig()\n→ timestamp = datetime.now().strftime('%m_%d_%Y_%H_%M_%S')\n→ artifact_dir = Artifacts/timestamp"]

        subgraph RUN["run_pipeline()"]
            S1["start_data_ingestion()"]
            S2["start_data_validation(data_ingestion_artifact)"]
            S3["start_data_transformation(data_validation_artifact)"]
            S4["start_model_trainer(data_transformation_artifact)"]
            RET["return ModelTrainerArtifact"]
            S1-->|DataIngestionArtifact|S2
            S2-->|DataValidationArtifact|S3
            S3-->|DataTransformationArtifact|S4
            S4-->RET
        end

        subgraph SD1["start_data_ingestion()"]
            SD1A["DataIngestionConfig(training_pipeline_config)\n→ paths inherit same timestamp"]
            SD1B["DataIngestion(config)\n.initiate_data_ingestion()"]
            SD1C["return DataIngestionArtifact"]
            SD1A-->SD1B-->SD1C
        end

        subgraph SD2["start_data_validation(data_ingestion_artifact)"]
            SD2A["DataValidationConfig(training_pipeline_config)"]
            SD2B["DataValidation(artifact, config)\n.initiate_data_validation()"]
            SD2C["return DataValidationArtifact"]
            SD2A-->SD2B-->SD2C
        end

        subgraph SD3["start_data_transformation(data_validation_artifact)"]
            SD3A["DataTransformationConfig(training_pipeline_config)"]
            SD3B["DataTransformation(artifact, config)\n.initiate_data_transformation()"]
            SD3C["return DataTransformationArtifact"]
            SD3A-->SD3B-->SD3C
        end

        subgraph SD4["start_model_trainer(data_transformation_artifact)"]
            SD4A["ModelTrainerConfig(training_pipeline_config)"]
            SD4B["ModelTrainer(config, artifact)\n.initiate_model_trainer()"]
            SD4C["return ModelTrainerArtifact"]
            SD4A-->SD4B-->SD4C
        end

        INIT --> RUN
        S1 --> SD1 --> S2
        S2 --> SD2 --> S3
        S3 --> SD3 --> S4
        S4 --> SD4 --> RET
    end

    API["FastAPI GET /train"] -->|triggers| INIT
    MAIN["main.py __main__"] -->|triggers| INIT
```

---

## DIAGRAM 8: NetworkModel + Prediction Chain

```mermaid
flowchart TD
    subgraph ESTIMATOR["utils/ml_utils/model/estimator.py"]
        subgraph NM["class NetworkModel"]
            NM_INIT["__init__(preprocessor, model)\n→ self.preprocessor = KNNImputer Pipeline\n→ self.model = RandomForest"]
            NM_PRED["predict(x)\n→ x_transform = self.preprocessor.transform(x)\n→ y_hat = self.model.predict(x_transform)\n→ return y_hat"]
            NM_INIT --> NM_PRED
        end
    end

    subgraph METRIC["utils/ml_utils/metric/classification_metric.py"]
        GCS["get_classification_score(y_true, y_pred)\n→ f1_score(y_true, y_pred)\n→ precision_score(y_true, y_pred)\n→ recall_score(y_true, y_pred)\n→ return ClassificationMetricArtifact(\n    f1_score, precision_score, recall_score\n  )"]
    end

    subgraph UTILS["utils/main_utils/utils.py"]
        SO["save_object(file_path, obj)\n→ os.makedirs()\n→ dill.dump(obj, file_obj)"]
        LO["load_object(file_path)\n→ dill.load(file_obj)\n→ return object"]
        SNA["save_numpy_array_data(file_path, array)\n→ np.save(file_obj, array)"]
        LNA["load_numpy_array(file_path)\n→ np.load(file_obj)\n→ return ndarray"]
        RY["read_yaml_file(file_path)\n→ yaml.safe_load()\n→ return dict"]
        WY["write_yaml_file(file_path, content)\n→ yaml.dump(content, file)"]
        EM["evaluate_models(X_train, y_train, X_test, y_test, models, params)\n→ GridSearchCV(cv=5, scoring='f1') per model\n→ f1_score(y_test, y_pred)\n→ return {name: f1}"]
    end

    subgraph PRED_FLOW["Prediction Flow (POST /predict/manual)"]
        PF1["Input: 30 feature values (int)\nhaving_IP_Address=-1, URL_Length=1 ..."]
        PF2["Pydantic NetworkDataInput validates types"]
        PF3["data.model_dump() → Python dict"]
        PF4["pd.DataFrame([dict]) → (1×30) DataFrame"]
        PF5["load_object('final_model/preprocessor.pkl')\n→ fitted KNNImputer Pipeline"]
        PF6["load_object('final_model/model.pkl')\n→ trained RandomForest"]
        PF7["NetworkModel(preprocessor, model)"]
        PF8["network_model.predict(df)\n→ preprocessor.transform(df) → (1×30) scaled\n→ model.predict(scaled) → [0] or [1]"]
        PF9["prediction = result[0]"]
        PF10{{"prediction == 1?"}}
        PF11["label = 'Phishing'\nmessage = 'URL is Phishing'"]
        PF12["label = 'Legitimate'\nmessage = 'URL is Legitimate'"]
        PF13["return {prediction: int\n  label: str\n  message: str}"]
        PF1-->PF2-->PF3-->PF4-->PF5-->PF6-->PF7-->PF8-->PF9-->PF10
        PF10-->|Yes|PF11-->PF13
        PF10-->|No|PF12-->PF13
    end

    NM_PRED --> PRED_FLOW
    LO --> PF5 & PF6
    GCS --> METRIC
```

---

## DIAGRAM 9: Data Shape Transformation Through Pipeline

```mermaid
flowchart LR
    subgraph MONGO["MongoDB"]
        D0["11055 documents\neach: {feature1: 1, feature2: -1, ...\n_id: ObjectId, Result: 1}"]
    end

    subgraph DI_SHAPE["After DataIngestion"]
        D1["DataFrame\n(11055, 32) ← with _id\n(11055, 31) ← after drop\nCSV: train (8844×31)\n     test  (2211×31)"]
    end

    subgraph DV_SHAPE["After DataValidation"]
        D2["Same shape — validated\ntrain (8844, 31)\ntest  (2211, 31)\nAll 31 cols confirmed\nNo drift detected"]
    end

    subgraph DT_SHAPE["After DataTransformation"]
        D3["X_train: (8844, 30) features\ny_train: (8844,)   labels 0/1\nKNNImputer fills NaN\nnp.c_ → train_arr (8844, 31)\n         test_arr  (2211, 31)\nSaved as .npy binary"]
    end

    subgraph MT_SHAPE["ModelTrainer Input"]
        D4["train_arr[:, :-1] → X_train (8844, 30)\ntrain_arr[:, -1]  → y_train (8844,)\ntest_arr[:, :-1]  → X_test  (2211, 30)\ntest_arr[:, -1]   → y_test  (2211,)"]
    end

    subgraph PRED_SHAPE["Prediction Input"]
        D5["batch:  N × 30 DataFrame\nmanual: 1 × 30 DataFrame\n→ preprocessor.transform() → scaled\n→ model.predict() → [0,1,0...]"]
    end

    MONGO -->|collection.find() + pd.DataFrame| DI_SHAPE
    DI_SHAPE -->|validated/ CSVs| DV_SHAPE
    DV_SHAPE -->|fit_transform + np.c_| DT_SHAPE
    DT_SHAPE -->|load_numpy_array| MT_SHAPE
    MT_SHAPE -->|NetworkModel.predict| PRED_SHAPE
```

---

## DIAGRAM 10: Config Entity Dependency Tree

```mermaid
flowchart TD
    TP["TrainingPipelineConfig\n__init__(timestamp=datetime.now())\n→ artifact_dir = Artifacts/timestamp\n→ pipeline_name = 'NetworkSecurity'"]

    DIC["DataIngestionConfig(TrainingPipelineConfig)\n→ data_ingestion_dir\n→ feature_store_file_path\n→ training_file_path\n→ testing_file_path\n→ train_test_split_ratio = 0.2\n→ collection_name = 'NetworkData'\n→ database_name = 'ALYAN'"]

    DVC["DataValidationConfig(TrainingPipelineConfig)\n→ data_validation_dir\n→ valid_data_dir / invalid_data_dir\n→ valid_train_file_path\n→ valid_test_file_path\n→ invalid_train_file_path\n→ invalid_test_file_path\n→ drift_report_file_path"]

    DTC["DataTransformationConfig(TrainingPipelineConfig)\n→ data_transformation_dir\n→ transformed_train_file_path (.npy)\n→ transformed_test_file_path  (.npy)\n→ transformed_object_file_path (.pkl)"]

    MTC["ModelTrainerConfig(TrainingPipelineConfig)\n→ model_trainer_dir\n→ trained_model_file_path\n→ expected_accuracy = 0.6\n→ overfitting_underfitting_threshold = 0.05"]

    CONST["constants/training_pipeline/__init__.py\nAll raw string/float values"]

    CONST --> TP
    TP -->|inject| DIC
    TP -->|inject| DVC
    TP -->|inject| DTC
    TP -->|inject| MTC

    DIC -->|used by| DI_CLASS["class DataIngestion"]
    DVC -->|used by| DV_CLASS["class DataValidation"]
    DTC -->|used by| DT_CLASS["class DataTransformation"]
    MTC -->|used by| MT_CLASS["class ModelTrainer"]
```

---

## DIAGRAM 11: Artifact Entity Chain

```mermaid
flowchart LR
    subgraph AE["entity/artifact_entity.py — @dataclass"]
        ART1["DataIngestionArtifact\n· train_file_path: str\n· test_file_path: str"]
        ART2["DataValidationArtifact\n· validation_status: bool\n· valid_train_file_path: str\n· valid_test_file_path: str\n· invalid_train_file_path: str\n· invalid_test_file_path: str\n· drift_report_file_path: str"]
        ART3["DataTransformationArtifact\n· transformed_object_file_path: str\n· transformed_train_file_path: str\n· transformed_test_file_path: str"]
        ART4["ClassificationMetricArtifact\n· f1_score: float\n· precision_score: float\n· recall_score: float"]
        ART5["ModelTrainerArtifact\n· trained_model_file_path: str\n· train_metric_artifact: ClassificationMetricArtifact\n· test_metric_artifact: ClassificationMetricArtifact"]
    end

    DI["DataIngestion\n.initiate_data_ingestion()"] -->|returns| ART1
    ART1 -->|input to| DV["DataValidation\n.initiate_data_validation()"]
    DV -->|returns| ART2
    ART2 -->|input to| DT["DataTransformation\n.initiate_data_transformation()"]
    DT -->|returns| ART3
    ART3 -->|input to| MT["ModelTrainer\n.initiate_model_trainer()"]
    ART4 -->|nested in| ART5
    MT -->|returns| ART5
    ART5 -->|logged to| MLFLOW["MLflow / DagsHub"]
```

---

## DIAGRAM 12: MLflow Tracking Flow

```mermaid
sequenceDiagram
    participant MT as ModelTrainer
    participant DAGSHUB as dagshub.init()
    participant MLFLOW as mlflow
    participant DAGSHUBREPO as DagsHub Repo

    MT->>DAGSHUB: dagshub.init(repo_owner, repo_name, mlflow=True)
    DAGSHUB-->>MT: MLflow tracking URI set

    Note over MT: Train metric (on train data)
    MT->>MLFLOW: mlflow.start_run()
    MT->>MLFLOW: log_metric("f1_score", 0.9916)
    MT->>MLFLOW: log_metric("precision_score", 0.9887)
    MT->>MLFLOW: log_metric("recall_score", 0.9945)
    MT->>MLFLOW: sklearn.log_model(best_model, "model")
    MLFLOW->>DAGSHUBREPO: sync run data
    MT->>MLFLOW: end run

    Note over MT: Test metric (on test data)
    MT->>MLFLOW: mlflow.start_run()
    MT->>MLFLOW: log_metric("f1_score", 0.9716)
    MT->>MLFLOW: log_metric("precision_score", 0.9589)
    MT->>MLFLOW: log_metric("recall_score", 0.9846)
    MT->>MLFLOW: sklearn.log_model(best_model, "model")
    MLFLOW->>DAGSHUBREPO: sync run data
    MT->>MLFLOW: end run

    DAGSHUBREPO-->>MT: Experiments tab: 3 runs visible
```

---

## DIAGRAM 13: KS Drift Detection Logic

```mermaid
flowchart TD
    START["detect_data_drift(base_df=train, current_df=test, threshold=0.05)"]
    INIT["report = {}\nstatus = True\ncols = base_df.columns (31 cols)"]
    LOOP["for column in cols:"]
    KS["ks_2samp(train_col, test_col)\nKolmogorov-Smirnov 2-sample test\n→ statistic + p_value"]
    CHECK{{"p_value >= threshold (0.05)?"}}
    NO_DRIFT["is_found = False\nSame distribution ✅\nno drift"]
    DRIFT["is_found = True\nstatus = False\nDifferent distributions ⚠️"]
    REPORT["report[column] = {\n  'p_value': float(p_value),\n  'drift_status': is_found\n}"]
    MORE{{"more columns?"}}
    SAVE["write_yaml_file(drift_report_file_path, report)\n→ Artifacts/.../drift_report/report.yaml"]
    RETURN["return status\nTrue  = no drift (pipeline continues)\nFalse = drift detected (logged, pipeline continues with warning)"]

    START-->INIT-->LOOP-->KS-->CHECK
    CHECK-->|Yes|NO_DRIFT-->REPORT
    CHECK-->|No|DRIFT-->REPORT
    REPORT-->MORE
    MORE-->|Yes|LOOP
    MORE-->|No|SAVE-->RETURN
```