# ═══════════════════════════════════════════════════════════════════
# utils.py — UPDATED VERSION
# ═══════════════════════════════════════════════════════════════════
# Common reusable functions — poore project mein import hoti hain.
# save_object  → koi bhi object pkl mein save karo
# evaluate_model → sab models train karo, R2 scores return karo

import os
import sys
import numpy as np
import pandas as pd
import dill                          # pickle ka powerful version — complex objects bhi save karta hai
                                     # sklearn Pipeline, ColumnTransformer etc. bhi handle karta hai
from sklearn.metrics import r2_score

from src.exception import CustomException


def save_object(file_path, obj):
    """
    Kisi bhi Python object ko disk pe .pkl file mein save karta hai.

    Parameters:
        file_path (str) : jahan save karna hai  e.g. "artifacts/preprocessor.pkl"
        obj (any)       : jo object save karna hai e.g. fitted ColumnTransformer

    Returns:
        None — sirf file likhta hai disk pe
    """
    try:
        dir_path = os.path.dirname(file_path)   # "artifacts/preprocessor.pkl" → "artifacts"
        os.makedirs(dir_path, exist_ok=True)     # artifacts/ folder banao agar nahi hai

        with open(file_path, "wb") as f:         # file binary write mode mein kholo
            dill.dump(obj, f)                    # object ko serialize karke file mein daal do

    except Exception as e:
        raise CustomException(e, sys)

# ─────────────────────────────────────────────────────────────────
# DRY RUN — save_object
#
# save_object("artifacts/preprocessor.pkl", fitted_column_transformer)
#
# 1. os.path.dirname("artifacts/preprocessor.pkl") → "artifacts"
# 2. os.makedirs("artifacts", exist_ok=True)       → folder banta hai
# 3. open("artifacts/preprocessor.pkl", "wb")      → binary file khulti hai
# 4. dill.dump(obj, f)                             → object bytes mein convert
#                                                    hokar file mein likha jaata hai
# 5. Disk pe ban gaya: artifacts/preprocessor.pkl
#
# WHY dill NOT pickle?
# pickle complex lambda functions aur sklearn Pipelines kabhi kabhi fail karta hai.
# dill = pickle ka superset — sab kuch handle karta hai.
# ─────────────────────────────────────────────────────────────────


def evaluate_model(X_train, y_train, X_test, y_test, models):
    """
    Sab models ko train karta hai aur har ek ka test R2 score return karta hai.
    ModelTrainer is function ko call karta hai — training loop yahan hai.

    Parameters:
        X_train, y_train : training features aur target (numpy arrays)
        X_test,  y_test  : test features aur target (numpy arrays)
        models (dict)    : {"model name": model_object, ...}

    Returns:
        report (dict)    : {"model name": test_r2_score, ...}
                           ModelTrainer isse best model dhundne ke liye use karta hai
    """
    # BUG FIXED: report[model] tha — model object dict key nahi ban sakta reliably
    # report[name] hona chahiye — string key clean aur readable hai
    try:
        report = {}

        for name, model in models.items():
            model.fit(X_train, y_train)              # train karo

            y_train_pred = model.predict(X_train)    # train predictions
            y_test_pred  = model.predict(X_test)     # test predictions

            train_model_score = r2_score(y_train, y_train_pred)   # train R2
            test_model_score  = r2_score(y_test,  y_test_pred)    # test R2

            # IMP: sirf test score report mein — best model selection test pe hoti hai
            # train score log ke liye print kar sakte ho (overfitting check)
            report[name] = test_model_score   

        return report

    except Exception as e:
        raise CustomException(e, sys)

# ─────────────────────────────────────────────────────────────────
# DRY RUN — evaluate_model
#
# models = {"Linear Regression": LinearRegression(), "LassoCV": LassoCV(), ...}
#
# iteration 1 — name="Linear Regression", model=LinearRegression()
#   model.fit(X_train, y_train)
#   y_train_pred = model.predict(X_train)
#   y_test_pred  = model.predict(X_test)
#   train_score  = r2_score(y_train, y_train_pred) → 0.83
#   test_score   = r2_score(y_test,  y_test_pred)  → 0.85
#   report["Linear Regression"] = 0.85
#
# iteration 2 — name="LassoCV" ...
#   report["LassoCV"] = 0.82
#
# ... repeat for all 8 models
#
# return {
#     "Linear Regression"      : 0.85,
#     "LassoCV"                : 0.82,
#     "RidgeCV"                : 0.84,
#     "K-Neighbors Regressor"  : 0.71,
#     "Decision Tree"          : 0.76,
#     "Random Forest Regressor": 0.88,
#     "CatBoosting Regressor"  : 0.87,
#     "AdaBoost Regressor"     : 0.83
# }
#
# ModelTrainer phir max() se 0.88 nikalta hai → Random Forest best
# ─────────────────────────────────────────────────────────────────


"""


DICT 1 — models  (model_trainer.py mein)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
models = {
    "Linear Regression" : LinearRegression(),   # key=name, value=unfitted object
    "Random Forest"     : RandomForestRegressor(),
    "CatBoosting"       : CatBoostRegressor(),
    ...
}

        │
        │  poora dict pass hota hai
        ▼

evaluate_model(... models=models)   ← utils.py


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
INSIDE evaluate_model()  (utils.py)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

report = {}   ← khali dict, bharta jayega

for name, model in models.items():
#    ^^^^  ^^^^^
#    key   value    dono ek saath milte hain .items() se

    model.fit(X_train, y_train)        # DICT 1 ka model train hota hai
    y_test_pred = model.predict(X_test)
    score = r2_score(y_test, y_test_pred)

    report[name] = score               # DICT 2 mein daal do
    # report["Linear Regression"] = 0.85
    # report["Random Forest"]     = 0.88
    # report["CatBoosting"]       = 0.87

return report   ← DICT 2 return hota hai


        │
        │  report dict wapas aata hai
        ▼

DICT 2 — models_report  (model_trainer.py mein)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
models_report = evaluate_model(...)

# models_report ab yeh hai:
# {
#     "Linear Regression" : 0.85,
#     "Random Forest"     : 0.88,   ← highest
#     "CatBoosting"       : 0.87
# }

best_model_name  = max(models_report, key=models_report.get)
# → "Random Forest"

best_model_score = models_report["Random Forest"]
# → 0.88

best_model = models["Random Forest"]
# DICT 1 se fitted object nikala — string key same hai dono mein
# ↑ IMP: isliye dono dicts mein keys SAME naam hone chahiye

"""