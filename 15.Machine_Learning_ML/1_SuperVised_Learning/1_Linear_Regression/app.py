
"""
app.py — Forest Fire FWI Prediction
Algerian Forest Fire Dataset
 
Folder Structure :
    1_SuperVised_Learning/
    ├── app.py                ← this file
    ├── models/
    │   ├── scaler.pkl
    │   ├── linear_model.pkl
    │   ├── lasso_model.pkl
    │   ├── ridge_model.pkl
    │   ├── elasticnet_model.pkl
    │   ├── lasso_cv_model.pkl
    │   ├── ridge_cv_model.pkl
    │   ├── elasticnet_cv_model.pkl
    │   └── feature_columns.pkl
    └── templates/
        ├── index.html
        └── result.html
 
Run : python app.py
"""
import pickle
import numpy as np
from flask import Flask, render_template, request, redirect, url_for
import os

app = Flask(__name__)


# ---------------- Load All Models ----------------
# Load once when app starts — not on every request

with open("models/scaler.pkl", "rb") as f:
    scaler = pickle.load(f)

with open("models/linear_model.pkl", "rb") as f:
    linear_model = pickle.load(f)

with open("models/lasso_model.pkl", "rb") as f:
    lasso_model = pickle.load(f)

with open("models/ridge_model.pkl", "rb") as f:
    ridge_model = pickle.load(f)

with open("models/elasticnet_model.pkl", "rb") as f:
    elasticnet_model = pickle.load(f)

with open("models/lasso_cv_model.pkl",    "rb") as f: 
    lasso_cv_model   = pickle.load(f)

with open("models/ridge_model_cv.pkl",    "rb") as f: 
    ridge_cv_model   = pickle.load(f)

with open("models/elasticnet_cv_model.pkl","rb") as f: 
    elasticnet_cv_model = pickle.load(f)

with open("models/feature_columns.pkl",   "rb") as f: 
    feature_columns  = pickle.load(f)
 
print("✅ All models loaded successfully")
print("Features expected:", feature_columns)
 
# ---------------- Model Registry ----------------
# All models in one place — easy to add or remove
 
MODELS = {
    "Linear Regression"  : linear_model,
    "Lasso"              : lasso_model,
    "Ridge"              : ridge_model,
    "ElasticNet"         : elasticnet_model,
    "LassoCV"            : lasso_cv_model,
    "RidgeCV"            : ridge_cv_model,
    "ElasticNetCV"       : elasticnet_cv_model,
}
 
# Known R² scores from notebook — used to highlight best model
MODEL_R2 = {
    "Linear Regression"  : 0.9847,
    "Lasso"              : 0.9839,
    "Ridge"              : 0.9847,
    "ElasticNet"         : 0.8630,
    "LassoCV"            : 0.9847,
    "RidgeCV"            : 0.9847,
    "ElasticNetCV"       : 0.9847,
}
 
# ---------------- Validation ----------------
def validate_input(data):
    """Check all fields are present and in valid range"""
 
    required_fields = feature_columns
 
    for field in required_fields:
        if field not in data or data[field] == "":
            return False, f"{field} is required"
 
    try:
        temperature = float(data.get("Temperature", 0))
        rh          = float(data.get("RH", 0))
        ws          = float(data.get("Ws", 0))
        rain        = float(data.get("Rain", 0))
 
        if not (0 <= temperature <= 60):
            return False, "Temperature must be between 0 and 60"
 
        if not (0 <= rh <= 100):
            return False, "Relative Humidity must be between 0 and 100"
 
        if not (0 <= ws <= 50):
            return False, "Wind Speed must be between 0 and 50"
 
        if rain < 0:
            return False, "Rain cannot be negative"
 
    except ValueError:
        return False, "All fields must be numeric values"
 
    return True, None
 
 
# ---------------- Predict All Models ----------------
def predict_all(input_array):
    """Run prediction on all 7 models and return results"""
 
    results = []
 
    for model_name, model in MODELS.items():
        prediction   = model.predict(input_array)[0]
        r2           = MODEL_R2.get(model_name, 0)
 
        results.append({
            "model"     : model_name,
            "prediction": round(float(prediction), 2),
            "r2"        : r2,
        })
 
    # Sort by R² score — highest first
    results.sort(key=lambda x: x["r2"], reverse=True)
 
    # Mark best model
    results[0]["is_best"] = True
    for r in results[1:]:
        r["is_best"] = False
 
    return results
 
 
# ---------------- FWI Severity Label ----------------
def get_severity(fwi):
    """Return fire danger level based on FWI value"""
    if fwi < 5:
        return "Low",        "🟢"
    elif fwi < 11:
        return "Moderate",   "🟡"
    elif fwi < 21:
        return "High",       "🟠"
    elif fwi < 33:
        return "Very High",  "🔴"
    else:
        return "Extreme",    "🚨"
 
 
# ---------------- Home Route ----------------
@app.route("/", methods=["GET"])
def index():
    return render_template("index.html", features=feature_columns)
 
 
# ---------------- Predict Route ----------------
@app.route("/predict", methods=["POST"])
def predict():
 
    # Get form data
    data = request.form.to_dict()
 
    # Validate input
    valid, error = validate_input(data)
    if not valid:
        return render_template("index.html", features=feature_columns, error=error)
 
    # Build input array in exact same order as training
    try:
        input_values = [float(data[col]) for col in feature_columns]
        input_array  = np.array(input_values).reshape(1, -1)
 
        # Scale using saved scaler — same scaler fitted on X_train
        input_scaled = scaler.transform(input_array)
 
    except Exception as e:
        return render_template("index.html", features=feature_columns, error=str(e))
 
    # Predict with all models
    results = predict_all(input_scaled)
 
    # Best model prediction for severity label
    best_prediction = results[0]["prediction"]
    severity, icon  = get_severity(best_prediction)
 
    return render_template(
        "result.html",
        results       = results,
        input_data    = data,
        severity      = severity,
        severity_icon = icon,
        best_pred     = best_prediction,
        feature_cols  = feature_columns
    )
 
 
# ---------------- Run ----------------
if __name__ == "__main__":
    app.run(debug=True)
 
