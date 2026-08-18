# ═══════════════════════════════════════════════════════════════════
# utils.py
# ═══════════════════════════════════════════════════════════════════
# Common reusable functions — poore project mein import hoti hain.
# Abhi sirf ek function hai: save_object (pickle/dill se object save karna)
# Baad mein load_object, evaluate_models etc. bhi yahan aayenge.

import os
import sys
import numpy as np
import pandas as pd
import dill                          # pickle ka powerful version — complex objects bhi save karta hai
                                     # sklearn Pipeline, ColumnTransformer etc. bhi handle karta hai

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