# ═══════════════════════════════════════════════════════════════════
# predict_pipeline.py
# ═══════════════════════════════════════════════════════════════════
# Production prediction ka kaam yahan hota hai.
# Training pipeline ne jo artifacts banaye (model.pkl, preprocessor.pkl)
# woh yahan load hokar naye data pe prediction karte hain.
#
# DO CLASSES:
# PredictPipeline → pkl load karo, transform karo, predict karo
# CustomData      → HTML form ka raw data leke DataFrame banao

import sys
import pandas as pd
from src.exception import CustomException
from src.logger import logging
from src.utils import load_object   # dill se pkl file load karta hai


# ── CLASS 1: PredictPipeline ──────────────────────────────────────
# Kaam: artifacts/ se trained model aur preprocessor load karo
#       naye input data pe prediction karo
class PredictPipeline:
    def __init__(self):
        pass   # koi initialization nahi chahiye — predict() mein sab hota hai

    def predict(self, features):
        """
        Naye input data pe math_score predict karta hai.

        Parameters:
            features (pd.DataFrame) : 1 row DataFrame — CustomData.get_data_as_frame() se aata hai

        Returns:
            predictions (np.ndarray) : e.g. array([74.3])
            app.py mein results[0] se pehla value nikala jaata hai
        """

        try:
            model_path       = "artifacts/model.pkl"
            preprocessor_path = "artifacts/preprocessor.pkl"

            # load_object → dill.load() karta hai pkl file ko
            # model       → fitted best model (e.g. LassoCV)
            # preprocessor → fitted ColumnTransformer (scaler + encoder)
            model        = load_object(file_path=model_path)
            preprocessor = load_object(file_path=preprocessor_path)

            # IMP: sirf transform — fit nahi
            # training ki statistics (mean, std, categories) use hoti hain
            data_scaled  = preprocessor.transform(features)

            # model predict karta hai scaled data pe
            predictions  = model.predict(data_scaled)

            
            return predictions

        except Exception as e:
            raise CustomException(e, sys)


# ── CLASS 2: CustomData ───────────────────────────────────────────
# Kaam: HTML form se aaya raw data leke
#       ek structured 1-row DataFrame banao
#       jo preprocessor samajh sake
class CustomData:
    def __init__(self,
                 gender: str,                        
                 race_ethnicity: str,
                 parental_level_of_education: str,
                 lunch: str,
                 test_preparation_course: str,
                 reading_score: int,
                 writing_score: int):

   
        self.gender                      = gender
        self.race_ethnicity              = race_ethnicity   # BUG FIXED: race_enthnicity → race_ethnicity
        self.parental_level_of_education = parental_level_of_education
        self.lunch                       = lunch
        self.test_preparation_course     = test_preparation_course
        self.reading_score               = reading_score
        self.writing_score               = writing_score

    def get_data_as_frame(self):
        """
        self mein stored sab values ko 1-row DataFrame mein convert karta hai.
        Column names EXACTLY wahi hone chahiye jo training data mein the —
        preprocessor inhi names se features dhundhta hai.

        Returns:
            pd.DataFrame : 1 row × 7 columns
        """
        try:
            custom_data_input_dict = {
                # IMP: key names training data ke column names se exactly match hone chahiye
                "gender"                      : [self.gender],
                "race_ethnicity"              : [self.race_ethnicity],  # BUG FIXED: race_ehtnicity typo
                "parental_level_of_education" : [self.parental_level_of_education],
                "lunch"                       : [self.lunch],
                "test_preparation_course"     : [self.test_preparation_course],
                "reading_score"               : [self.reading_score],
                "writing_score"               : [self.writing_score]    # BUG FIXED: "wrting_score " typo + space
            }
            # list mein wrap kiya e.g. [self.gender] → DataFrame ko
            # 1 row banana hota hai, isliye values list mein honi chahiye

            return pd.DataFrame(custom_data_input_dict)
            # →
            # | gender | race_ethnicity | ... | reading_score | writing_score |
            # | female | group B        | ... | 72            | 68            |

        except Exception as e:
            raise CustomException(e, sys)


# ─────────────────────────────────────────────────────────────────
# FULL DRY RUN
#
# app.py se aata hai:
#   data = CustomData(gender="female", reading_score=72, ...)
#
# 1. CustomData.__init__()
#       self.gender        = "female"
#       self.reading_score = 72
#       ... sab store ho gaya
#
# 2. data.get_data_as_frame()
#       dict banta hai → pd.DataFrame
#       →  1 row × 7 cols DataFrame return
#
# 3. predict_pipeline.predict(pred_df)
#       load_object("artifacts/model.pkl")        → LassoCV object
#       load_object("artifacts/preprocessor.pkl") → ColumnTransformer
#
#       preprocessor.transform(pred_df)
#       → "female" → [0,1] (OHE)
#       → reading_score=72 → scaled value
#       → 1 row numpy array
#
#       model.predict(data_scaled) → array([74.3])
#       return array([74.3])
#
# 4. app.py mein:
#       results    = array([74.3])
#       results[0] = 74.3
#       render_template("home.html", results=74.3)
# ─────────────────────────────────────────────────────────────────
