"""
Heart Disease Prediction — Flask App

Folder Structure :
    heart_disease_prediction/
    ├── app.py                ← this file
    ├── models/
    │   ├── lr_tuned.pkl
    │   ├── scaler.pkl
    │   ├── column_transformer.pkl
    │   ├── feature_columns.pkl
    │   └── threshold.pkl
    └── templates/
        ├── index.html
        └── result.html

Run : python app.py
"""

import os
import pickle
import numpy as np
import pandas as pd
from flask import Flask, render_template, request

app = Flask(__name__)


# ---------------- Load Models ----------------
# load once when app starts — not on every request

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def model_path(filename):
    return os.path.join(BASE_DIR, "models", filename)

with open(model_path("lr_tuned.pkl"),            "rb") as f: model     = pickle.load(f)
with open(model_path("scaler.pkl"),              "rb") as f: scaler    = pickle.load(f)
with open(model_path("column_transformer.pkl"),  "rb") as f: ct        = pickle.load(f)
with open(model_path("feature_columns.pkl"),     "rb") as f: feat_cols = pickle.load(f)
with open(model_path("threshold.pkl"),           "rb") as f: threshold = pickle.load(f)

print("✅ All models loaded")
print("Threshold :", threshold)
print("Features  :", feat_cols)


# ---------------- Validation ----------------
def validate_input(data):

    required = ["age", "sex", "cp", "trestbps", "chol", "fbs",
                "restecg", "thalach", "exang", "oldpeak", "slope", "ca", "thal"]

    for field in required:
        if not data.get(field) and data.get(field) != "0":
            return False, f"{field} is required"

    try:
        age      = int(data["age"])
        trestbps = int(data["trestbps"])
        chol     = int(data["chol"])
        thalach  = int(data["thalach"])
        oldpeak  = float(data["oldpeak"])

        if not (18 <= age <= 100):
            return False, "Age must be between 18 and 100"

        if not (80 <= trestbps <= 220):
            return False, "Blood Pressure must be between 80 and 220"

        if not (100 <= chol <= 600):
            return False, "Cholesterol must be between 100 and 600"

        if not (60 <= thalach <= 220):
            return False, "Max Heart Rate must be between 60 and 220"

        if not (0 <= oldpeak <= 7):
            return False, "ST Depression must be between 0 and 7"

    except ValueError:
        return False, "All fields must be numeric values"

    return True, None


# ---------------- Risk Level ----------------
def get_risk_level(probability):
    if probability < 0.20:
        return "Low Risk",      "🟢", "low"
    elif probability < 0.40:
        return "Moderate Risk",  "🟡", "moderate"
    elif probability < 0.55:
        return "Elevated Risk", "🟠", "elevated"
    elif probability < 0.75:
        return "High Risk",     "🔴", "high"
    else:
        return "Very High Risk", "🚨", "very-high"


# ---------------- Home — Form ----------------
@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")


# ---------------- Predict ----------------
@app.route("/predict", methods=["POST"])
def predict():

    # get form data
    data = request.form.to_dict()

    # validate
    valid, error = validate_input(data)
    if not valid:
        return render_template("index.html", error=error)

    try:
        # build raw input as DataFrame — same column order as training
        raw_input = pd.DataFrame({
            "age":      [int(data["age"])],
            "sex":      [int(data["sex"])],
            "cp":       [int(data["cp"])],
            "trestbps": [int(data["trestbps"])],
            "chol":     [int(data["chol"])],
            "fbs":      [int(data["fbs"])],
            "restecg":  [int(data["restecg"])],
            "thalach":  [int(data["thalach"])],
            "exang":    [int(data["exang"])],
            "oldpeak":  [float(data["oldpeak"])],
            "slope":    [int(data["slope"])],
            "ca":       [int(data["ca"])],
            "thal":     [int(data["thal"])],
        })

        # Step 1 : One Hot Encode using saved ColumnTransformer
        # fit was done on training data — only transform here
        encoded = ct.transform(raw_input)

        # Step 2 : Scale using saved StandardScaler
        scaled = scaler.transform(encoded)

        # Step 3 : Predict probability
        disease_prob = model.predict_proba(scaled)[0][1]

        # Step 4 : Apply custom threshold (not default 0.5)
        prediction = int(disease_prob >= threshold)

        # risk level
        risk_level, risk_icon, risk_class = get_risk_level(disease_prob)

        # readable labels for display
        sex_label      = "Male" if int(data["sex"]) == 1 else "Female"
        cp_labels      = {0: "Typical Angina", 1: "Atypical Angina", 2: "Non-Anginal Pain", 3: "Asymptomatic"}
        restecg_labels = {0: "Normal", 1: "ST-T Abnormality", 2: "Left Ventricular Hypertrophy"}
        slope_labels   = {0: "Upsloping", 1: "Flat", 2: "Downsloping"}
        thal_labels    = {0: "Normal", 1: "Fixed Defect", 2: "Reversible Defect"}

        result = {
            "prediction"     : prediction,
            "label"          : "HEART DISEASE DETECTED" if prediction == 1 else "NO HEART DISEASE",
            "probability"    : round(float(disease_prob) * 100, 1),
            "threshold"      : round(threshold * 100, 1),
            "risk_level"     : risk_level,
            "risk_icon"      : risk_icon,
            "risk_class"     : risk_class,
            "age"            : data["age"],
            "sex"            : sex_label,
            "cp"             : cp_labels.get(int(data["cp"]), data["cp"]),
            "trestbps"       : data["trestbps"],
            "chol"           : data["chol"],
            "fbs"            : "Yes" if int(data["fbs"]) == 1 else "No",
            "restecg"        : restecg_labels.get(int(data["restecg"]), data["restecg"]),
            "thalach"        : data["thalach"],
            "exang"          : "Yes" if int(data["exang"]) == 1 else "No",
            "oldpeak"        : data["oldpeak"],
            "slope"          : slope_labels.get(int(data["slope"]), data["slope"]),
            "ca"             : data["ca"],
            "thal"           : thal_labels.get(int(data["thal"]), data["thal"]),
        }

        return render_template("result.html", result=result)

    except Exception as e:
        return render_template("index.html", error=str(e))


# ---------------- Run ----------------
if __name__ == "__main__":
    app.run(debug=True)