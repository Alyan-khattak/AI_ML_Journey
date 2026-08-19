## This file is copy of app.py created for ElasticBeanStalk Deployment 


# ═══════════════════════════════════════════════════════════════════
# application.py — Flask Web Application Entry Point
# ═══════════════════════════════════════════════════════════════════
# User browser se form submit karta hai → Flask receive karta hai →
# CustomData object banta hai → PredictPipeline predict karta hai →
# result wapas HTML mein dikhta hai
#
# FLOW:
# Browser → GET  /              → index.html  (landing page)
# Browser → GET  /predictdata   → home.html   (form page)
# Browser → POST /predictdata   → prediction  → home.html (result)

from flask import Flask, render_template, request
import numpy as np
import pandas as pd
from src.pipeline.predict_pipeline import CustomData, PredictPipeline

# IMP: application naam isliye — AWS Elastic Beanstalk "application" variable dhundhta hai
# app = application → locally bhi same object use hota hai
application = Flask(__name__)
app = application


# ── ROUTE 1: Landing Page ─────────────────────────────────────────
# Method  : GET only
# Trigger : user visits "/"
# Returns : index.html render karta hai — simple landing/home page
@app.route("/")
def index():
    return render_template("index.html")


# ── ROUTE 2: Prediction ───────────────────────────────────────────
# Method  : GET + POST
# Trigger : user visits "/predictdata" ya form submit karta hai
# GET  → sirf form dikhao (home.html)
# POST → form data lo → predict karo → result ke saath home.html
@app.route("/predictdata", methods=["POST", "GET"])
def predict_datapoint():

    if request.method == "GET":
        # sirf form page dikhao — koi prediction nahi
        return render_template("home.html")

    else:
        # ── STEP 1: Form Data → CustomData Object ─────────────────
        # request.form.get("field_name") → HTML form se value nikalta hai
        # CustomData class in data ko validate karke structured object mein store karta hai
        # BUG FIXED: missing comma after parental_level_of_education
        data = CustomData(
            gender                      = request.form.get("gender"),
            race_ethnicity              = request.form.get("race_ethnicity"),
            parental_level_of_education = request.form.get("parental_level_of_education"),
            lunch                       = request.form.get("lunch"),
            test_preparation_course     = request.form.get("test_preparation_course"),
            reading_score               = request.form.get("reading_score"),
            writing_score               = request.form.get("writing_score")
        )

        # ── STEP 2: CustomData → DataFrame ────────────────────────
        # get_data_as_frame() CustomData ka method hai
        # Returns: 1 row DataFrame — preprocessor isi format mein expect karta hai
        pred_df = data.get_data_as_frame()
        print(pred_df)   # debug ke liye — terminal mein dikhega

        # ── STEP 3: DataFrame → Prediction ────────────────────────
        # PredictPipeline.predict() :
        #   1. model.pkl load karta hai
        #   2. preprocessor.pkl load karta hai
        #   3. preprocessor.transform(pred_df) → scale/encode karta hai
        #   4. model.predict() → math_score predict karta hai
        # Returns: numpy array e.g. [72.4]
        predict_pipeline = PredictPipeline()
        results = predict_pipeline.predict(pred_df)

        # results[0] → pehla (aur sirf) prediction value nikalo
        # home.html mein "results" variable se access hota hai {{ results }}
        return render_template("home.html", results=results[0])


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
    # host="0.0.0.0" → sab network interfaces pe suno (AWS deploy ke liye zaroori)
    # debug=True → code change pe auto-reload, error details browser mein


# ─────────────────────────────────────────────────────────────────
# DRY RUN — POST request
#
# User form fill karta hai:
#   gender="female", reading_score=72, writing_score=68 ...
#
# 1. request.form.get("gender") → "female"
#    CustomData object banta hai sab values ke saath
#
# 2. data.get_data_as_frame() →
#    pd.DataFrame:
#    | gender | race_ethnicity | ... | reading_score | writing_score |
#    | female | group B        | ... | 72            | 68            |
#
# 3. PredictPipeline().predict(pred_df)
#    → preprocessor.transform() → scaled/encoded array
#    → model.predict()          → [74.3]
#
# 4. results[0] = 74.3
#    render_template("home.html", results=74.3)
#    → HTML mein {{ results }} → "74.3" dikhta hai
# ─────────────────────────────────────────────────────────────────