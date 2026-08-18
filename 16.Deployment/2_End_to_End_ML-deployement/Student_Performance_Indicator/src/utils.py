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
from sklearn.model_selection import GridSearchCV

from src.exception import CustomException
from src.logger import logging


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



#############
# Method to load Pikle Files
##################

def load_object(file_path):
    try:
        with open(file_path, "rb") as f:
            return dill.load(f)
    except Exception as e:
        raise CustomException(e,sys)
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


def evaluate_model(X_train, y_train, X_test, y_test, models, params):
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
            # model.fit(X_train, y_train)              # train karo # as we are doing Hyper-permeter Tuning we dont need the simple fit 

            param_grid = params[name]

            grid_cv = GridSearchCV(
                estimator=model,
                param_grid=param_grid,
                cv=3,
                scoring="r2",
                n_jobs=-1
            )
            # grid serach CV will gve us the best Prameters
            grid_cv.fit(X_train,y_train) #  # CV pe best params dhundho

            logging.info(f"{name} — best params: {grid_cv.best_params_}") 
            # best params model pe set karo
            model.set_params(**grid_cv.best_params_) # for every model use the best params 
            # ** = dict unpack
            # {"n_estimators": 100, "max_depth": 5}
            # → model.set_params(n_estimators=100, max_depth=5)

            # ab best params se final train
            model.fit(X_train, y_train)


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
╔══════════════════════════════════════════════════════════════════╗
║                    model_trainer.py                             ║
╠══════════════════════════════════════════════════════════════════╣
║                                                                  ║
║  DICT 1 — models                                                 ║
║  ┌─────────────────────────────────────────────┐                 ║
║  │ "Linear Regression"       : LinearRegression()   │            ║
║  │ "LassoCV"                 : LassoCV()            │            ║
║  │ "RidgeCV"                 : RidgeCV()            │            ║
║  │ "K-Neighbors Regressor"   : KNeighborsRegressor()│            ║
║  │ "Decision Tree"           : DecisionTreeRegressor│            ║
║  │ "Random Forest Regressor" : RandomForestRegressor│            ║
║  │ "Gradient Boosting"       : GradientBoosting()   │            ║
║  │ "CatBoosting Regressor"   : CatBoostRegressor()  │            ║
║  │ "AdaBoost Regressor"      : AdaBoostRegressor()  │            ║
║  │ "XGBRegressor"            : XGBRegressor()       │            ║
║  └─────────────────────────────────────────────┘                 ║
║  key = model name (string)                                       ║
║  value = unfitted model object                                   ║
║                                                                  ║
║  DICT 2 — params                                                 ║
║  ┌─────────────────────────────────────────────┐                 ║
║  │ "Linear Regression"       : {}              │                 ║
║  │ "LassoCV"                 : {}              │                 ║
║  │ "RidgeCV"                 : {}              │                 ║
║  │ "K-Neighbors Regressor"   : {n_neighbors,   │                 ║
║  │                              weights}       │                 ║
║  │ "Decision Tree"           : {criterion}     │                 ║
║  │ "Random Forest Regressor" : {n_estimators}  │                 ║
║  │ "Gradient Boosting"       : {learning_rate, │                 ║
║  │                              subsample,     │                 ║
║  │                              n_estimators}  │                 ║
║  │ "CatBoosting Regressor"   : {depth,         │                 ║
║  │                              learning_rate, │                 ║
║  │                              iterations}    │                 ║
║  │ "AdaBoost Regressor"      : {learning_rate, │                 ║
║  │                              n_estimators}  │                 ║
║  │ "XGBRegressor"            : {learning_rate, │                 ║
║  │                              n_estimators}  │                 ║
║  └─────────────────────────────────────────────┘                 ║
║  key = model name (SAME as DICT 1 — must match)                  ║
║  value = dict of hyperparameters to tune                         ║
║                                                                  ║
╠══════════════════════════════════════════════════════════════════╣
║  dono dicts evaluate_model() mein pass hote hain                 ║
║                                                                  ║
║  evaluate_model(X_train, y_train, X_test, y_test,               ║
║                 models=DICT1, params=DICT2)                      ║
╚══════════════════════════════════════════════════════════════════╝
                          │
                          ▼
╔══════════════════════════════════════════════════════════════════╗
║                       utils.py                                  ║
║                  evaluate_model()                                ║
╠══════════════════════════════════════════════════════════════════╣
║                                                                  ║
║  DICT 3 — report = {}   ← khali, loop mein bharta hai           ║
║                                                                  ║
║  for name, model in models.items():                              ║
║  ─────────────────────────────────                               ║
║                                                                  ║
║  iteration 1:                                                    ║
║    name  = "Linear Regression"                                   ║
║    model = LinearRegression()                                    ║
║    param_grid = params["Linear Regression"] = {}                 ║
║                                                                  ║
║    GridSearchCV(model, param_grid={}, cv=3)                      ║
║    gs.fit(X_train)    ← best params dhundho                     ║
║    model.set_params(**gs.best_params_)                           ║
║    model.fit(X_train) ← final train best params se              ║
║    score = r2_score(y_test, model.predict(X_test))               ║
║                                                                  ║
║    report["Linear Regression"] = 0.85                           ║
║                                                                  ║
║  iteration 2:                                                    ║
║    name  = "Random Forest Regressor"                             ║
║    model = RandomForestRegressor()                               ║
║    param_grid = {"n_estimators": [8,16,32,64,128,256]}          ║
║                                                                  ║
║    GridSearchCV tries all 6 values of n_estimators              ║
║    best → n_estimators=128  (example)                           ║
║    model.set_params(n_estimators=128)                            ║
║    model.fit(X_train)                                            ║
║    score = r2_score(...)                                         ║
║                                                                  ║
║    report["Random Forest Regressor"] = 0.88                     ║
║                                                                  ║
║  ... repeat for all 10 models                                    ║
║                                                                  ║
║  return report                                                   ║
╚══════════════════════════════════════════════════════════════════╝
                          │
                          ▼
╔══════════════════════════════════════════════════════════════════╗
║                    model_trainer.py                             ║
╠══════════════════════════════════════════════════════════════════╣
║                                                                  ║
║  DICT 3 — models_report (returned from evaluate_model)          ║
║  ┌──────────────────────────────────────┐                        ║
║  │ "Linear Regression"       : 0.85    │                        ║
║  │ "LassoCV"                 : 0.82    │                        ║
║  │ "RidgeCV"                 : 0.84    │                        ║
║  │ "K-Neighbors Regressor"   : 0.71    │                        ║
║  │ "Decision Tree"           : 0.76    │                        ║
║  │ "Random Forest Regressor" : 0.88  ←│─ highest               ║
║  │ "Gradient Boosting"       : 0.87    │                        ║
║  │ "CatBoosting Regressor"   : 0.86    │                        ║
║  │ "AdaBoost Regressor"      : 0.83    │                        ║
║  │ "XGBRegressor"            : 0.85    │                        ║
║  └──────────────────────────────────────┘                        ║
║                                                                  ║
║  best_model_name  = max(models_report, key=models_report.get)   ║
║                  = "Random Forest Regressor"                     ║
║                                                                  ║
║  best_model_score = models_report["Random Forest Regressor"]    ║
║                   = 0.88                                         ║
║                                                                  ║
║  best_model = models["Random Forest Regressor"]                 ║
║             = fitted RandomForestRegressor object               ║
║             ↑ DICT 1 se — isliye keys same honi chahiye         ║
║                                                                  ║
║  save_object("artifacts/model.pkl", best_model)                 ║
╚══════════════════════════════════════════════════════════════════╝

IMP RULE:
DICT 1 keys == DICT 2 keys == DICT 3 keys
sab mein "Random Forest Regressor" — ek bhi alag hua toh crash

"""