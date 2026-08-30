# ═══════════════════════════════════════════════════════════════════
# app.py — FastAPI Backend
# ═══════════════════════════════════════════════════════════════════
# Network Security MLOps project ka production API
# Teen routes:
# GET /          → /docs pe redirect (Swagger UI)
# GET /train     → poori training pipeline trigger karta hai
# GET /predict   → CSV upload → batch prediction → HTML table
# POST /predict/manual → manual input → single prediction
#
# PEHLE TEEN PROJECTS MEIN: Flask use kiya tha
# YAHAN: FastAPI — async, automatic docs, type validation built-in
###==============================================================

import sys
import os

# ── MONGODB ───────────────────────────────────────────────────────
import pymongo
# pymongo = MongoDB Python driver
# MongoClient → Atlas se connect karta hai

import certifi
# certifi = trusted SSL certificates ki list
# MongoDB Atlas HTTPS connection verify karne ke liye
ca = certifi.where()
# ca = certificate file ka path → MongoClient ko pass hoga

from dotenv import load_dotenv
# python-dotenv → .env file se environment variables load karta hai
# MONGO_DB_URL, credentials etc. .env mein hain

# ── NETWORKSECURITY IMPORTS ───────────────────────────────────────
from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging
from networksecurity.pipeline.training_pipeline import TrainingPipeline
# TrainingPipeline → run_pipeline() → poori training ek call mein

from networksecurity.utils.ML_utils.model.estimator import NetworkModel
# NetworkModel → preprocessor + model wrapper
# predict() → transform → predict internally

# ── FASTAPI IMPORTS ───────────────────────────────────────────────
from fastapi import FastAPI, File, UploadFile, Request
# FastAPI   → web framework (Flask ka async alternative)
# File      → file parameter define karne ke liye
# UploadFile → CSV file upload handle karta hai
# Request   → HTTP request object → templates mein chahiye

from fastapi.middleware.cors import CORSMiddleware
# CORSMiddleware → Cross Origin Resource Sharing
# Browser security rule: ek domain dusre domain ko request nahi kar sakta
# e.g. frontend (localhost:3000) → backend (localhost:8000) → blocked by browser
# CORSMiddleware → yeh restriction relax karta hai

from fastapi.responses import Response
# Response → plain text/HTML response return karne ke liye

from fastapi.templating import Jinja2Templates
# Jinja2Templates → HTML templates render karne ke liye
# Flask ka render_template() jaisa

from starlette.responses import RedirectResponse
# RedirectResponse → ek URL se dusre pe redirect karta hai
# / → /docs redirect ke liye use hoga

from uvicorn import run as app_run
# uvicorn → ASGI server — FastAPI run karne ke liye
# Flask ke liye Werkzeug tha → FastAPI ke liye uvicorn

import pandas as pd
from networksecurity.utils.main_utils.utils import load_object
from networksecurity.constants.training_pipeline import (
    DATA_INGESTION_COLLECTION_NAME,
    DATA_INGESTION_DATABASE_NAME
)

# ── ENV VARIABLES ─────────────────────────────────────────────────
load_dotenv()
MONGO_DB_URL = os.getenv("MONGO_ATLAS_URI")


# ── MONGODB CONNECTION ────────────────────────────────────────────
client = pymongo.MongoClient(MONGO_DB_URL, tlsCAFile=ca)

database   = client[DATA_INGESTION_DATABASE_NAME]
# sahi: collection = database[COLLECTION_NAME]
collection = database[DATA_INGESTION_COLLECTION_NAME]

# ── TEMPLATES ─────────────────────────────────────────────────────
templates = Jinja2Templates(directory="./templates")


# ── FASTAPI APP ───────────────────────────────────────────────────
app = FastAPI(
    title="Network Security MLOps",
    description="Phishing URL detection pipeline",
    version="0.0.1"
)

# ── CORS MIDDLEWARE ───────────────────────────────────────────────
# origins = ["*"] → sab domains allow karo
# "*" = wildcard — koi bhi frontend is API ko call kar sakta hai
# Production mein specific domains do:
# origins = ["https://yourfrontend.com"]
#
# allow_methods=["*"] → GET, POST, PUT, DELETE sab allowed
# allow_headers=["*"] → koi bhi HTTP header allowed
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,    # kaunse domains se requests allow karein
    allow_credentials=True,   # cookies/auth headers allow
    allow_methods=["*"],      # sab HTTP methods
    allow_headers=["*"]       # sab headers
)

# ── WHAT IS MIDDLEWARE? ───────────────────────────────────────────
# Middleware = request aur response ke beech mein chalta hai
# Har request → middleware → route handler → middleware → response
#
# CORSMiddleware kya karta hai:
# Browser: "Main localhost:3000 hun, main localhost:8000 ko request kar sakta hun?"
# CORSMiddleware: "Haan, origins=['*'] hai → allowed"
# Browser: request bhejta hai
# ─────────────────────────────────────────────────────────────────







# ── STARTUP EVENT ─────────────────────────────────────────────────
# WHY THIS IS NEEDED:
# final_model/ gitignore mein hai → Railway/Render pe nahi hoti
# bina model ke /predict → FileNotFoundError crash karega
#
# DO OPTIONS THE:
#
# Option 1 (yeh wala) → HuggingFace se download karo on startup
#   Pros: automatic, no manual step, model registry best practice
#   Cons: first startup slow hoga (download time)
#
# Option 2 → /train route call karo deployment ke baad
#   Browser mein: https://your-app.railway.app/train
#   Pipeline run hogi → final_model/ ban jayegi
#   Pros: latest model ban jayega
#   Cons: manual step, MongoDB connection chahiye, time lagta hai
#
# IMP: agar HuggingFace pe model push nahi kiya tha →
#      pehle locally run karo: PYTHONPATH=. python main.py
#      phir model automatically HF pe push ho jayega
#      phir deploy karo
# ─────────────────────────────────────────────────────────────────

from networksecurity.cloud.hf_syncer import pull_model_from_huggingface

@app.on_event("startup")
async def startup_event():
    """
    App start hone pe automatically model download karta hai.
    final_model/ exist kare toh skip karo — warna HF se pull karo.

    FLOW:
    Railway/Render deploy
        ↓ uvicorn starts
        ↓ startup_event() trigger
        ↓ final_model/model.pkl exist?
            YES → skip (local dev mein already hai)
            NO  → pull_model_from_huggingface()
                  → HF se model.pkl + preprocessor.pkl download
                  → final_model/ mein save
        ↓ /predict routes ready 
    """
    if not os.path.exists("final_model/model.pkl"):
        # IMP: file check karo — agar already hai toh download mat karo
        # local development mein final_model/ hoti hai → skip
        # Railway/Render pe nahi hoti → download
        logging.info("final_model/model.pkl not found")
        logging.info("Downloading models from HuggingFace Hub...")
        pull_model_from_huggingface()
        # pull_model_from_huggingface() → hf_syncer.py mein defined
        # snapshot_download(repo_id, local_dir="final_model/")
        # → model.pkl + preprocessor.pkl download hote hain
        logging.info("Models downloaded successfully → final_model/ ready")
    else:
        # local machine pe already final_model/ hai → skip download
        logging.info("final_model/ already exists → skipping HF download")




# ══════════════════════════════════════════════════════════════════
# ROUTE 1: / → Swagger UI Redirect
# ══════════════════════════════════════════════════════════════════
@app.get("/", tags=["authentication"])
async def index(request:Request):
    # FastAPI automatically /docs pe Swagger UI banata hai
    # wahan sab routes test kar sakte ho browser mein
    return templates.TemplateResponse(request=request, name="index.html")




# ══════════════════════════════════════════════════════════════════
# ROUTE alpha: / → Get System Diagrams
# ══════════════════════════════════════════════════════════════════
@app.get("/diagrams")
async def diagrams_page(request: Request):
    return templates.TemplateResponse(request=request, name="diagrams.html")


@app.get("/pipeline")
async def pipeline_page(request:Request):
    return templates.TemplateResponse(request=request, name="pipeline_explain.html")


# ══════════════════════════════════════════════════════════════════
# ROUTE 2: /train → Training Pipeline Trigger
# ══════════════════════════════════════════════════════════════════

## I am Commenting this out so that Run API don't run the system
## in UI homepage the run pipline button always run the system 
## if you want tht functionality then un comment it 

# @app.get("/train")
# async def train_route():
#     """
#     Poori training pipeline trigger karta hai.
#     MongoDB → Ingestion → Validation → Transformation → ModelTrainer
#     """
#     try:
#         logging.info("Training route called")
#         train_pipeline = TrainingPipeline()
#         train_pipeline.run_pipeline()
#         logging.info("Training pipeline completed via API")
#         return Response("Training is Successful")
#     except Exception as e:
#         raise NetworkSecurityException(e, sys)


# ══════════════════════════════════════════════════════════════════
# ROUTE 3: /predict → Batch CSV Prediction
# ══════════════════════════════════════════════════════════════════

# ── ROUTE 3: predict page (GET) ──────────────────────────────────
@app.get("/predict")
async def predict_page(request: Request):
    # IMP: GET /predict → form page dikhao
    # POST /predict → actual prediction karo
    return templates.TemplateResponse(request=request, name="predict.html")



@app.post("/predict")
async def predict_route(request: Request, file: UploadFile = File(...)):
    """
    CSV file upload karo → batch prediction → HTML table return

    Parameters:
        file (UploadFile) : CSV file with same columns as training data
                            (30 features — Result column optional)

    Returns:
        HTML table with predictions appended
    """
    try:
        logging.info(f"Predict route called — file: {file.filename}")

        df = pd.read_csv(file.file)
        logging.info(f"Uploaded CSV shape: {df.shape}")

        # final_model/ mein preprocessor aur model save kiya tha
        # ModelTrainer ke save_object() calls se
        preprocessor = load_object("final_model/preprocessor.pkl")
        model        = load_object("final_model/model.pkl")

        # NetworkModel → preprocessor + model wrapper
        # predict() internally: transform → predict
        network_model = NetworkModel(preprocessor=preprocessor, model=model)

        y_pred = network_model.predict(df)
        # y_pred = [1, 0, 1, 0, ...] → 1=phishing, 0=legitimate

        df["predicted_column"] = y_pred
        # CSV mein prediction column add karo

        os.makedirs("prediction_output", exist_ok=True)
        df.to_csv("prediction_output/output.csv", index=False)
        logging.info("Predictions saved to prediction_output/output.csv")

        # HTML table banao → browser mein dikhao
        table_html = df.to_html(classes="table table-striped")

        return templates.TemplateResponse(
            request=request,
            name="table.html",
            context={"table": table_html}
        )

    except Exception as e:
        raise NetworkSecurityException(e, sys)


# ══════════════════════════════════════════════════════════════════
# ROUTE 4: /predict/manual → Single Manual Prediction
# ══════════════════════════════════════════════════════════════════
from pydantic import BaseModel
# pydantic → FastAPI ka validation library
# BaseModel → request body ke fields define karo
# automatic type validation + error messages

class NetworkDataInput(BaseModel):
    """
    Manual prediction ke liye input schema.
    Pydantic automatically validate karega:
    - type check (int/float)
    - missing fields → 422 error
    - swagger UI mein form ban jaayega
    """
    having_IP_Address:             int
    URL_Length:                    int
    Shortining_Service:            int
    having_At_Symbol:              int
    double_slash_redirecting:      int
    Prefix_Suffix:                 int
    having_Sub_Domain:             int
    SSLfinal_State:                int
    Domain_registeration_length:   int
    Favicon:                       int
    port:                          int
    HTTPS_token:                   int
    Request_URL:                   int
    URL_of_Anchor:                 int
    Links_in_tags:                 int
    SFH:                           int
    Submitting_to_email:           int
    Abnormal_URL:                  int
    Redirect:                      int
    on_mouseover:                  int
    RightClick:                    int
    popUpWidnow:                   int
    Iframe:                        int
    age_of_domain:                 int
    DNSRecord:                     int
    web_traffic:                   int
    Page_Rank:                     int
    Google_Index:                  int
    Links_pointing_to_page:        int
    Statistical_report:            int


# ── ROUTE 4: manual predict page (GET) ───────────────────────────
@app.get("/predict/manual")
async def predict_manual_page(request: Request):
    # IMP: GET /predict/manual → form page dikhao
    return templates.TemplateResponse(request=request, name="predict_manual.html")

# ── ROUTE 4b: manual predict POST ────────────────────────────────
@app.post("/predict/manual")
async def predict_manual(data: NetworkDataInput):
    """
    Manual input se ek URL ka prediction karta hai.
    Swagger UI (/docs) mein form fill karo → predict.

    Parameters:
        data (NetworkDataInput) : pydantic model — sab 30 features

    Returns:
        JSON: prediction (0/1) + label (Legitimate/Phishing) + probability
    """
    try:
        logging.info("Manual predict route called")

        # pydantic model → dict → DataFrame
        # model_dump() → {"having_IP_Address": 1, "URL_Length": 0, ...}
        input_dict = data.model_dump()
        input_df   = pd.DataFrame([input_dict])
        # [input_dict] → list of one dict → 1 row DataFrame
        logging.info(f"Manual input shape: {input_df.shape}")

        # artifacts load karo
        preprocessor = load_object("final_model/preprocessor.pkl")
        model        = load_object("final_model/model.pkl")

        network_model = NetworkModel(preprocessor=preprocessor, model=model)

        prediction = network_model.predict(input_df)[0]
        # [0] → sirf pehla (aur ek) prediction nikalo

        label = "Phishing" if prediction == 1 else "Legitimate"
        logging.info(f"Manual prediction: {prediction} → {label}")

        return {
            "prediction": int(prediction),
            "label":      label,
            "message":    f"URL is classified as {label}"
        }
    
    except Exception as e:
        raise NetworkSecurityException(e, sys)


# ── ENTRY POINT ───────────────────────────────────────────────────
if __name__ == "__main__":
   
    app_run(app, host="0.0.0.0", port=8000)
    # host="0.0.0.0" → sab interfaces pe suno (Docker + Railway ke liye zaroori)
    # port=8000 → FastAPI standard port


# ─────────────────────────────────────────────────────────────────
