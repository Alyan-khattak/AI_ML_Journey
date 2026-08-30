# ═══════════════════════════════════════════════════════════════════
# networksecurity/utils/ml_utils/metric/classification_metric.py
# ═══════════════════════════════════════════════════════════════════
# Classification metrics calculate karta hai aur
# ClassificationMetricArtifact return karta hai.
#
# WHY ALAG FILE?
# PEHLE TEEN PROJECTS MEIN:
#   metrics directly model_trainer.py mein calculate karte the
#   r2_score ya roc_auc_score ek line mein
#
# YAHAN (MLOps style):
#   get_classification_score() → alag utility function
#   ModelTrainer do baar call karega:
#   1. train data pe → train_metric_artifact
#   2. test data pe  → test_metric_artifact
#   dono ClassificationMetricArtifact objects → ModelTrainerArtifact mein store
#   MLflow bhi yahi metrics log karega
###==============================================================

from networksecurity.entity.artifact_entity import ClassificationMetricArtifact
# ClassificationMetricArtifact → f1_score, precision_score, recall_score store karta hai

from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging
import sys

from sklearn.metrics import f1_score, precision_score, recall_score


def get_classification_score(y_true, y_pred) -> ClassificationMetricArtifact:
    """
    Classification metrics calculate karta hai aur structured artifact return karta hai.

    ModelTrainer do baar call karega:
    1. train_metric = get_classification_score(y_train, y_train_pred)
    2. test_metric  = get_classification_score(y_test,  y_test_pred)

    Phir overfitting check:
    |train_metric.f1_score - test_metric.f1_score| > threshold → reject

    Parameters:
        y_true (array) : actual labels    (0=legitimate, 1=phishing)
        y_pred (array) : predicted labels (0=legitimate, 1=phishing)

    Returns:
        ClassificationMetricArtifact:
            ├── f1_score        → F1 = 2 * (precision * recall) / (precision + recall)
            ├── precision_score → TP / (TP + FP) — flagged mein kitne real threats
            └── recall_score    → TP / (TP + FN) — actual threats mein kitne pakde
    """
    try:
        logging.info("Entered get_classification_score — calculating metrics")

        # ── F1 SCORE ──────────────────────────────────────────────
        # F1 = precision aur recall ka balance
        # network security mein important:
        # FP costly → legitimate traffic block hoga
        # FN costly → actual attack miss hoga
        model_f1_score = f1_score(y_true, y_pred)

        # ── PRECISION SCORE ───────────────────────────────────────
        # precision = TP / (TP + FP)
        # flagged threats mein se kitne real threats the
        # low precision → legitimate traffic pe bhi alert → annoying
        # BUG FIXED: precession → precision (typo)
        model_precision_score = precision_score(y_true, y_pred)

        # ── RECALL SCORE ──────────────────────────────────────────
        # recall = TP / (TP + FN)
        # actual threats mein se kitne pakde
        # low recall → real attacks miss → dangerous
        model_recall_score = recall_score(y_true, y_pred)

        logging.info(
            f"Metrics calculated — "
            f"F1: {model_f1_score:.4f} | "
            f"Precision: {model_precision_score:.4f} | "
            f"Recall: {model_recall_score:.4f}"
        )

        # ── ARTIFACT BANAO ────────────────────────────────────────
        # teen metrics ek structured object mein
        # ModelTrainerArtifact mein train_metric aur test_metric store honge
        classification_metric = ClassificationMetricArtifact(
            f1_score=model_f1_score,
            precision_score=model_precision_score,
            # BUG FIXED: precession_score → precision_score (typo in artifact field)
            recall_score=model_recall_score
        )

        logging.info(f"ClassificationMetricArtifact created: {classification_metric}")
        return classification_metric

    except Exception as e:
        raise NetworkSecurityException(e, sys)


# ─────────────────────────────────────────────────────────────────
# DRY RUN
#
# y_true = [1, 0, 1, 1, 0, 1]   ← actual labels
# y_pred = [1, 0, 0, 1, 0, 1]   ← predicted labels
#
# TP = 3 (1→1 correct)
# FP = 0 (0→1 wrong)
# FN = 1 (1→0 wrong)
# TN = 2 (0→0 correct)
#
# precision = 3 / (3+0) = 1.00
# recall    = 3 / (3+1) = 0.75
# f1        = 2 * (1.00 * 0.75) / (1.00 + 0.75) = 0.857
#
# ClassificationMetricArtifact(
#     f1_score        = 0.857,
#     precision_score = 1.000,
#     recall_score    = 0.750
# )
# ─────────────────────────────────────────────────────────────────