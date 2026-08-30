# ═══════════════════════════════════════════════════════════════════
# networksecurity/utils/main_utils/utils.py
# ═══════════════════════════════════════════════════════════════════
# Common reusable utility functions — poore project mein import hoti hain
#
# PEHLE TEEN PROJECTS MEIN:
#   utils.py → save_object, load_object, evaluate_models
#
# YAHAN (MLOps style):
#   utils/main_utils/utils.py → YAML read/write bhi hai
#   YAML kyun? drift_report.yaml, schema.yaml → structured config files
#   utils/ml_utils/ → model specific utilities (alag folder)
#
# FUNCTIONS:
# read_yaml_file()  → schema.yaml padhta hai → dict return karta hai
# write_yaml_file() → drift report.yaml likhta hai
###==============================================================

import os
import sys
import yaml                          # YAML files parse karne ke liye
                                     # pip install pyaml

from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging
import numpy as np
import dill
from sklearn.model_selection import GridSearchCV
from sklearn.metrics import r2_score

# ══════════════════════════════════════════════════════════════════
# FUNCTION 1: read_yaml_file
# ══════════════════════════════════════════════════════════════════
def read_yaml_file(file_path: str) -> dict:
    """
    YAML file padhta hai aur Python dict mein convert karta hai.

    KAHAN USE HOTA HAI:
    DataValidation.__init__() mein:
        self.schema_config = read_yaml_file(SCHEMA_FILE_PATH)
        # data_schema/schema.yaml padhta hai
        # expected columns aur types milte hain
        # validate_number_cols() aur check_numerical_col() mein use hoga

    Parameters:
        file_path (str) : YAML file ka path
                          e.g. "data_schema/schema.yaml"

    Returns:
        dict : YAML content Python dict mein
               e.g. {"columns": [...], "numerical_columns": [...]}
    """
    try:
        with open(file_path, "rb") as yaml_file:
            # "rb" = read binary mode
            # yaml.safe_load → YAML string → Python dict
            return yaml.safe_load(yaml_file)
    except Exception as e:
        raise NetworkSecurityException(e, sys)


# ══════════════════════════════════════════════════════════════════
# FUNCTION 2: write_yaml_file
# ══════════════════════════════════════════════════════════════════
def write_yaml_file(file_path: str, content: object, replace: bool = False) -> None:
    """
    Python dict ko YAML file mein likhta hai.

    KAHAN USE HOTA HAI:
    DataValidation.detect_data_drift() mein:
        write_yaml_file(drift_report_file_path, report)
        # KS test results YAML mein save hote hain
        # "Artifacts/timestamp/data_validation/drift_report/report.yaml"

    Parameters:
        file_path (str)    : jahan save karna hai
        content   (object) : jo likhna hai (dict → YAML)
        replace   (bool)   : True → existing file delete karke naya banao
                             False → existing file pe append (default)

    Returns:
        None — sirf file likhta hai
    """
    try:
        if replace:
            # IMP: replace=True → purani file delete karo
            # warna YAML mein duplicate entries aa sakte hain
            if os.path.exists(file_path):
                os.remove(file_path)

        # folder banao agar exist nahi karta
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        with open(file_path, "w") as file:
            # yaml.dump → Python dict → YAML string → file mein likho
            yaml.dump(content, file)

    except Exception as e:
        raise NetworkSecurityException(e, sys)




# ══════════════════════════════════════════════════════════════════
# FUNCTION 3: save_numpy_array_data
# ══════════════════════════════════════════════════════════════════
def save_numpy_array_data(file_path:str, array: np.array):
    """
    Numpy array ko .npy file mein save karta hai.
    ModelTrainer is file ko load karke X_train, y_train nikaalega.

    Parameters:
        file_path (str)        : jahan save karna hai e.g. "Artifacts/.../train.npy"
        array     (np.ndarray) : numpy array jo save karna hai
    """
      
    try:
        logging.info("Entered The Save numpy array  method of util.py to save ")
        dir_path = os.path.dirname(file_path)
        os.makedirs(dir_path, exist_ok=True)
        with open(file_path, "wb") as file_obj:
            np.save(file_obj, array)
    except Exception as e:
        raise NetworkSecurityException(e, sys)




# ══════════════════════════════════════════════════════════════════
# FUNCTION 4: save_object
# ══════════════════════════════════════════════════════════════════
def save_object(file_path:str, obj: object):
    """
    .npy file se numpy array load karta hai.
    ModelTrainer use karega.
    """
    try:
        logging.info(f"Entered The Save object method of util.py to save {obj} ")
        dir_path = os.path.dirname(file_path)
        os.makedirs(dir_path, exist_ok=True)
        with open(file_path, "wb") as file_obj:
            dill.dump(obj, file_obj)

        logging.info(f"Existed the mehod and saved : {obj} ")
    except Exception as e:
        raise NetworkSecurityException(e, sys)

    

# ══════════════════════════════════════════════════════════════════
# FUNCTION 5: load_object
# ══════════════════════════════════════════════════════════════════
def load_object(file_path:str) -> object:
    """
     load saved object 
    """
    try:
        logging.info(f"Entered The Load object method of util.py to load object from {file_path}  ")
        with open(file_path, "rb") as file_obj:
            return dill.load(file_obj)
    except Exception as e:
        raise NetworkSecurityException(e, sys)



# ══════════════════════════════════════════════════════════════════
# FUNCTION 6: load_numpy_array
# ══════════════════════════════════════════════════════════════════
def load_numpy_array(file_path:str) -> np.array:
    """
     load saved object 
    """
    try:
        logging.info(f"Entered The Load object method of util.py to save")
        with open(file_path, "rb") as file_obj:
            return np.load(file_obj)
    except Exception as e:
        raise NetworkSecurityException(e, sys)



# ══════════════════════════════════════════════════════════════════
# FUNCTION 7: evaluate_models
# ══════════════════════════════════════════════════════════════════
def evaluate_models(X_train, y_train, X_test, y_test, models, params) -> dict:
    """
    Sab models ko GridSearchCV se tune karta hai.
    Har model ka test F1 score return karta hai.

    ModelTrainer.train_model() is function ko call karta hai.

    PEHLE TEEN PROJECTS MEIN:
        r2_score use kiya tha — regression tha
    YAHAN:
        f1_score use karo — classification hai
        network security → false positives bhi costly hain

    Parameters:
        X_train, y_train : training data (numpy arrays)
        X_test,  y_test  : test data (numpy arrays)
        models  (dict)   : {"model name": model_object}
        params  (dict)   : {"model name": {param_grid}}

    Returns:
        report (dict) : {"model name": test_f1_score}
                        ModelTrainer isse best model dhundne ke liye use karta hai
    """
    try:
        from sklearn.model_selection import GridSearchCV
        from sklearn.metrics import f1_score
        # BUG FIXED: r2_score → f1_score
        # r2_score regression ke liye hai — classification mein galat metric

        logging.info("Entered evaluate_models — starting GridSearchCV for all models")

        report = {}

        for name, model in models.items():
            param_grid = params[name]
            # us model ke params nikalo
            # e.g. "Random Forest" → {"n_estimators": [8,16,32,128,256]}

            # GridSearchCV — best params dhundho 5-fold CV se
            grid_cv = GridSearchCV(
                estimator=model,
                param_grid=param_grid,
                cv=5,
                scoring="f1",     
                n_jobs=-1          # sab cores use karo → fast
            )

            grid_cv.fit(X_train, y_train)
            logging.info(f"{name} — best params: {grid_cv.best_params_} | best CV F1: {grid_cv.best_score_:.4f}")

            # best params model pe set karo
            model.set_params(**grid_cv.best_params_)
            # ** = dict unpack → model.set_params(n_estimators=256) etc.

            # best params se final train karo
            model.fit(X_train, y_train)

            y_train_pred = model.predict(X_train)
            y_test_pred  = model.predict(X_test)


            # test pred ko test true se compare karo
            train_model_score = f1_score(y_train, y_train_pred)
            test_model_score  = f1_score(y_test,  y_test_pred)
        
            report[name] = test_model_score
            logging.info(f"{name} → Train F1: {train_model_score:.4f} | Test F1: {test_model_score:.4f}")

        return report

    except Exception as e:
        raise NetworkSecurityException(e, sys)


# ─────────────────────────────────────────────────────────────────
# DRY RUN
#
# read_yaml_file("data_schema/schema.yaml")
# → {"columns": [{"having_IP_Address": "int64"}, ...],
#    "numerical_columns": ["having_IP_Address", ...]}
#
# write_yaml_file("Artifacts/.../drift_report/report.yaml",
#                 {"having_IP_Address": {"p_value": 0.23, "drift_status": False}, ...})
# → YAML file ban gayi:
#   having_IP_Address:
#     drift_status: false
#     p_value: 0.23
# ─────────────────────────────────────────────────────────────────