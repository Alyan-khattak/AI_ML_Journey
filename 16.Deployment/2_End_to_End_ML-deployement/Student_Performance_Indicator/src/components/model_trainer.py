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
                "XGBoostRegressor"       : XGBRegressor()
            }

            # evaluate_model sab models train karta hai aur
            # har model ka test R2 score return karta hai dict mein
            # → {"Linear Regression": 0.85, "LassoCV": 0.82, ...}
            models_report: dict = evaluate_model(
                X_train=X_train,
                y_train=y_train,
                X_test=X_test,
                y_test=y_test,
                models=models
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

