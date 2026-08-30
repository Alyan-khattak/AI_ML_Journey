# ═══════════════════════════════════════════════════════════════════
# networksecurity/utils/ml_utils/model/estimator.py
# ═══════════════════════════════════════════════════════════════════
# Production prediction ka wrapper class hai
# preprocessor + model dono ek object mein combine karta hai
#
# WHY NetworkModel CLASS?
# PEHLE TEEN PROJECTS MEIN:
#   predict_pipeline.py mein alag alag load karte the:
#   preprocessor = load_object("preprocessor.pkl")
#   model        = load_object("model.pkl")
#   scaled       = preprocessor.transform(X)
#   pred         = model.predict(scaled)
#
# YAHAN (MLOps style):
#   NetworkModel(preprocessor, model) → ek object
#   model_estimator.predict(X) → internally transform + predict
#   save_object(path, NetworkModel) → dono ek saath pkl mein
#   load_object(path) → ek load se dono mil jaate hain
#   cleaner aur error-proof approach
#
# FLOW:
# ModelTrainer → NetworkModel(preprocessor, model) banata hai
#             → save_object(SAVED_MODEL_DIR/model.pkl, network_model)
# PredictPipeline → load_object → network_model.predict(X)
###==============================================================

from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging
import sys

from networksecurity.constants.training_pipeline import SAVED_MODEL_DIR, MODEL_FILE_NAME
# SAVED_MODEL_DIR = "saved_models"   ← versioned models ke liye alag folder
# MODEL_FILE_NAME = "model.pkl"
# IMP: Artifacts/timestamp/model_trainer/ se ALAG hai yeh
# saved_models/ = production mein deploy hone wala final model
# Artifacts/ = experiment history


class NetworkModel:
    """
    Preprocessor aur Model ko ek object mein wrap karta hai.
    predict() call karo → internally transform + predict hota hai.

    PEHLE TEEN PROJECTS MEIN:
        PredictPipeline mein manually karte the:
        data_scaled = preprocessor.transform(features)
        predictions = model.predict(data_scaled)

    YAHAN:
        network_model = NetworkModel(preprocessor, model)
        predictions   = network_model.predict(features)
        Ek call mein dono steps — cleaner API
    """

    def __init__(self, preprocessor, model):
        """
        Parameters:
            preprocessor : fitted KNNImputer Pipeline
                           DataTransformation ne train kiya tha
                           → missing values fill karega new data pe

            model        : fitted best classification model
                           ModelTrainer ne select kiya tha
                           → predict karega preprocessed data pe
        """
        try:
            self.preprocessor = preprocessor
            self.model         = model
            logging.info(f"NetworkModel initialized — Model: {type(model).__name__}")
        except Exception as e:
            raise NetworkSecurityException(e, sys)

    def predict(self, x):
        """
        Raw features leke prediction return karta hai.
        Internally: transform → predict

        Parameters:
            x : raw features
                pd.DataFrame ya numpy array
                PredictPipeline yahan se call karega

        Returns:
            y_hat : numpy array of predictions (0=legitimate, 1=phishing)
        """
        try:
            logging.info(f"Entered predict method — input shape: {x.shape}")

            # IMP: pehle preprocessor se transform karo
            # KNNImputer missing values fill karega
            # same fitted preprocessor jo training mein use hua tha
            x_transform = self.preprocessor.transform(x)
            logging.info(f"Preprocessing done — transformed shape: {x_transform.shape}")

            # model pe predict karo
            y_hat = self.model.predict(x_transform)
            logging.info(f"Prediction complete — model: {type(self.model).__name__} | predictions: {y_hat}")

            return y_hat

        except Exception as e:
            raise NetworkSecurityException(e, sys)


# ─────────────────────────────────────────────────────────────────
# DRY RUN
#
# ModelTrainer mein:
#   network_model = NetworkModel(preprocessor_obj, best_model)
#   save_object("saved_models/model.pkl", network_model)
#
# PredictPipeline mein:
#   network_model = load_object("saved_models/model.pkl")
#   predictions   = network_model.predict(new_data_df)
#
# predict() internally:
#   x_transform = knn_imputer.transform(new_data_df)
#               → NaN fill → scaled
#   y_hat       = best_model.predict(x_transform)
#               → [1, 0, 1, 1, 0] (1=phishing, 0=legitimate)
#   return y_hat
# ─────────────────────────────────────────────────────────────────