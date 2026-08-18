# ═══════════════════════════════════════════════════════════════════
# model_trainer.py
# ═══════════════════════════════════════════════════════════════════
# Transformation se aaye numpy arrays pe sab models train karta hai.
# Best model dhundhta hai R2 score se.
# Best model ko model.pkl mein save karta hai.
#
# FLOW:
# DataTransformation → (train_arr, test_arr)
#                            ↓
# ModelTrainer → best model train → model.pkl save → r2_score return

import os
import sys
from dataclasses import dataclass

from sklearn.ensemble import (
    AdaBoostRegressor,
    GradientBoostingRegressor,
    RandomForestRegressor
)
from sklearn.linear_model import LinearRegression, LassoCV, RidgeCV
from sklearn.neighbors import KNeighborsRegressor
from sklearn.tree import DecisionTreeRegressor
from sklearn.metrics import r2_score as r2_score_fn   
from catboost import CatBoostRegressor
from xgboost import XGBRegressor

from src.exception import CustomException
from src.logger import logging
from src.utils import save_object, evaluate_model     


# ── CONFIG CLASS ──────────────────────────────────────────────────
# Sirf ek path — trained model kahan save hoga
# BUG FIXED: "articfacts" → "artifacts" (typo)
@dataclass
class ModelTrainerConfig:
    trained_model_file_path: str = os.path.join("artifacts", "model.pkl")


# ── MAIN CLASS ────────────────────────────────────────────────────
class ModelTrainer:
    def __init__(self):                             
        self.model_trainer_config = ModelTrainerConfig()

    def initiate_model_trainer(self, train_array, test_array):
        """
        train_array aur test_array lete hai (numpy).
        Sab models train karta hai evaluate_model() se.
        Best model select karta hai R2 score se.
        Best model pkl mein save karta hai.

        Parameters:
            train_array (np.ndarray) : [X_train cols | y_train col] — transformation se aaya
            test_array  (np.ndarray) : [X_test cols  | y_test col]  — transformation se aaya

        Returns:
            r2 (float) : best model ka test R2 score
        """
        try:
            logging.info("Splitting train and test arrays into X, y")

            # IMP: np.c_ ne features aur target ko ek saath joda tha (last col = target)
            # Ab wapas alag karo
            # [:,:-1] = sab columns EXCEPT last  → features (X)
            # [:, -1] = sirf last column          → target (y)
            X_train, y_train, X_test, y_test = (
                train_array[:, :-1],   # 800 × N  — features
                train_array[:, -1],    # 800       — math_score
                test_array[:, :-1],    # 200 × N  — features
                test_array[:, -1]      # 200       — math_score
            )

            # ---------------- Define Models ----------------
            # Dictionary method — ek loop mein sab train ho jaate hain
            # evaluate_model() utils.py mein hai — wahi training karta hai
            models = {
                "Linear Regression"      : LinearRegression(),
                "LassoCV"                : LassoCV(),          # auto best alpha dhundhta hai CV se
                "RidgeCV"                : RidgeCV(),          # auto best alpha dhundhta hai CV se
                "K-Neighbors Regressor"  : KNeighborsRegressor(),
                "Decision Tree"          : DecisionTreeRegressor(),
                "Random Forest Regressor": RandomForestRegressor(),
                "CatBoosting Regressor"  : CatBoostRegressor(verbose=False),
                "AdaBoost Regressor"     : AdaBoostRegressor(),
                "XGBRegressor"       : XGBRegressor()
            }

            # ---------------- Hyperparameters for Each Model ----------------
            # IMP: keys SAME honi chahiye jaise models dict mein — warna GridSearchCV match nahi karega
            params = {
                "Linear Regression"      : {},
                "LassoCV"                : {},   # LassoCV internally CV karta hai — GridSearch zaruri nahi
                "RidgeCV"                : {},   # same — alphas internally tune hote hain
                "K-Neighbors Regressor"  : {
                    "n_neighbors": [3, 5, 7, 9],
                    "weights"    : ["uniform", "distance"]
                },
                "Decision Tree"          : {
                    "criterion": ["squared_error", "friedman_mse", "absolute_error", "poisson"]
                },
                "Random Forest Regressor": {
                    "n_estimators": [8, 16, 32, 64, 128, 256]
                },
                "Gradient Boosting"      : {
                    "learning_rate": [.1, .01, .05, .001],
                    "subsample"    : [0.6, 0.7, 0.75, 0.8, 0.85, 0.9],
                    "n_estimators" : [8, 16, 32, 64, 128, 256]
                },
                "CatBoosting Regressor"  : {
                    "depth"        : [6, 8, 10],
                    "learning_rate": [0.01, 0.05, 0.1],
                    "iterations"   : [30, 50, 100]
                },
                "AdaBoost Regressor"     : {
                    "learning_rate": [.1, .01, 0.5, .001],
                    "n_estimators" : [8, 16, 32, 64, 128, 256]
                },
                "XGBRegressor"           : {
                    "learning_rate": [.1, .01, .05, .001],
                    "n_estimators" : [8, 16, 32, 64, 128, 256]
                }
            }


            # evaluate_model sab models train karta hai aur
            # har model ka test R2 score return karta hai dict mein
            # → {"Linear Regression": 0.85, "LassoCV": 0.82, ...}
            models_report: dict = evaluate_model(
                X_train=X_train,
                y_train=y_train,
                X_test=X_test,
                y_test=y_test,
                models=models,
                params=params
            )

            

            # ── BEST MODEL SELECT ─────────────────────────────────
            # report mein se highest R2 score nikalo
            best_model_score = max(sorted(models_report.values()))

            # us score se model ka naam nikalo
            # .index() → us value ki position
            # list(keys())[position] → us position ka key (model name)
            best_model_name = list(models_report.keys())[
                list(models_report.values()).index(best_model_score)
            ]

            # naam se actual model object nikalo (fitted hai already)
            best_model = models[best_model_name]

            # IMP: agar best model bhi 0.6 se kam R2 hai → koi kaam ka model nahi mila
            # production mein aisa model deploy karna galat hoga
            if best_model_score < 0.6:
                raise CustomException("No best Model Found", sys)

            logging.info(f"Best Model Found: {best_model_name} with R2: {best_model_score}")

            # best model disk pe save karo — prediction pipeline mein use hoga
            save_object(
                file_path=self.model_trainer_config.trained_model_file_path,
                obj=best_model
            )

            # final R2 score calculate karo test pe
            predicted = best_model.predict(X_test)
            r2 = r2_score_fn(y_test, predicted)   

            logging.info(f"Final Test R2 Score: {r2}")
            return r2

        except Exception as e:
            raise CustomException(e, sys)



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

# ─────────────────────────────────────────────────────────────────
# DRY RUN — initiate_model_trainer()
#
# train_array shape: 800 × 8   (7 features + 1 target)
# test_array  shape: 200 × 8
#
# 1. X_train = train_array[:, :-1]  → 800 × 7
#    y_train = train_array[:, -1]   → 800 values (math_score)
#    X_test  = test_array[:, :-1]   → 200 × 7
#    y_test  = test_array[:, -1]    → 200 values
#
# 2. evaluate_model() sab 8 models pe loop karta hai:
#       LinearRegression.fit(X_train, y_train)
#       predict(X_test) → r2_score → report["Linear Regression"] = 0.85
#       ... repeat for all models
#
# 3. models_report =
#       {
#           "Linear Regression"      : 0.85,
#           "LassoCV"                : 0.82,
#           "RidgeCV"                : 0.84,
#           "K-Neighbors Regressor"  : 0.71,
#           "Decision Tree"          : 0.76,
#           "Random Forest Regressor": 0.88,
#           "CatBoosting Regressor"  : 0.87,
#           "AdaBoost Regressor"     : 0.83
#       }
#
# 4. best_model_score = max(...) → 0.88
#    best_model_name  = "Random Forest Regressor"
#    best_model       = models["Random Forest Regressor"]  (fitted object)
#
# 5. 0.88 > 0.6 → threshold pass ✅
#
# 6. save_object("artifacts/model.pkl", best_model)
#       → Random Forest disk pe save
#
# 7. predicted = best_model.predict(X_test) → 200 predictions
#    r2 = r2_score_fn(y_test, predicted)    → 0.88
#    return 0.88
#
# Disk pe ban gaya:
#   artifacts/
#   ├── raw.csv
#   ├── train.csv
#   ├── test.csv
#   ├── preprocessor.pkl
#   └── model.pkl          ← best model (Random Forest)
# ─────────────────────────────────────────────────────────────────

