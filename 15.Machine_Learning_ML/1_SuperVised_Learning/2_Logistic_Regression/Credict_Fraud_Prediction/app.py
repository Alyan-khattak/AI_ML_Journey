"""
Credit Card Fraud Detection — Flask App

Folder Structure :
    fraud_app/
    ├── app.py                ← this file
    ├── models/
    │   ├── balanced_model.pkl
    │   ├── scaler.pkl
    │   ├── feature_columns.pkl
    │   └── threshold.pkl
    └── templates/
        ├── index.html
        └── result.html

Run : python app.py
"""

from flask import Flask, render_template, request, redirect, url_for
import pickle
import numpy as np
import os

# always load models relative to where app.py is located
# not relative to where you run the command from
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def model_path(filename):
    return os.path.join(BASE_DIR, "models", filename)
app = Flask(__name__)


# ---------------- Load Models ----------------
# load once when app starts — not on every request

with open(model_path("balanced_model.pkl"),   "rb") as f: model           = pickle.load(f)
with open(model_path("scaler.pkl"),           "rb") as f: scaler          = pickle.load(f)
with open(model_path("features_columns.pkl"), "rb") as f: feature_columns = pickle.load(f)
with open(model_path("threshold.pkl"),        "rb") as f: threshold       = pickle.load(f)


print("✅ All models loaded")
print("Features expected :", feature_columns)
print("Threshold         :", threshold)


# ---------------- Validation ----------------
def validate_input(data):

    required = ["amount", "time"]

    for field in required:
        if not data.get(field):
            return False, f"{field} is required"

    try:
        amount = float(data["amount"])
        time   = float(data["time"])

        if amount < 0:
            return False, "Amount cannot be negative"

        if time < 0:
            return False, "Time cannot be negative"

    except ValueError:
        return False, "Amount and Time must be numeric"

    return True, None


# ---------------- Risk Level ----------------
def get_risk_level(probability):
    if probability < 0.1:
        return "Very Low",  "🟢"
    elif probability < 0.3:
        return "Low",       "🟡"
    elif probability < 0.5:
        return "Medium",    "🟠"
    elif probability < 0.7:
        return "High",      "🔴"
    else:
        return "Very High", "🚨"


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
        # get amount and time from form
        amount = float(data["amount"])
        time   = float(data["time"])

        # get V1-V28 from form — default to 0 if not provided
        v_features = []
        for i in range(1, 29):
            val = data.get(f"v{i}", 0)
            v_features.append(float(val) if val != "" else 0.0)

        # scale Amount and Time — same scaler fitted on training data
        scaled = scaler.transform([[amount, time]])
        amount_scaled = scaled[0][0]
        time_scaled   = scaled[0][1]

        # build feature array in same order as training
        # order : Time, V1-V28, Amount
        input_array = np.array([[time_scaled] + v_features + [amount_scaled]])

        # predict probability of fraud (class 1)
        fraud_prob  = model.predict_proba(input_array)[0][1]

        # apply threshold — not default 0.5
        prediction  = int(fraud_prob >= threshold)

        # risk level
        risk_level, risk_icon = get_risk_level(fraud_prob)

        # result dict
        result = {
            "prediction"  : prediction,
            "label"       : "FRAUD"      if prediction == 1 else "LEGITIMATE",
            "probability" : round(float(fraud_prob) * 100, 2),
            "threshold"   : round(threshold * 100, 1),
            "risk_level"  : risk_level,
            "risk_icon"   : risk_icon,
            "amount"      : amount,
            "time"        : time,
        }

        return render_template("result.html", result=result)

    except Exception as e:
        return render_template("index.html", error=str(e))


# ---------------- Run ----------------
if __name__ == "__main__":
    app.run(debug=True)