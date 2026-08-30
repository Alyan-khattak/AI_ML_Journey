# ═══════════════════════════════════════════════════════════════════
# networksecurity/cloud/hf_syncer.py
# ═══════════════════════════════════════════════════════════════════
# Hugging Face Hub se model push/pull karta hai
# ModelTrainer yahan se import karta hai — cloud logic alag file mein
#
# WHY ALAG FILE?
# model_trainer.py → training logic
# hf_syncer.py     → cloud sync logic
# Separation of concerns — ek file ek kaam
###==============================================================

import sys
import os
from huggingface_hub import HfApi

from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging
from networksecurity.constants.training_pipeline import (
    HF_REPO_ID,
    HF_REPO_TYPE,
    HF_MODEL_DIR
)


def push_model_to_huggingface(
    folder_path: str = HF_MODEL_DIR,
    repo_id:     str = HF_REPO_ID,
    repo_type:   str = HF_REPO_TYPE,
    private:     bool = False
) -> str:
    """
    final_model/ folder ko Hugging Face Hub pe push karta hai.

    Parameters:
        folder_path (str)  : local folder jo upload karna hai
                             default: HF_MODEL_DIR (constants se)
        repo_id     (str)  : HF repo naam
                             default: HF_REPO_ID (constants se)
        repo_type   (str)  : "model" ya "dataset"
        private     (bool) : True = private repo

    Returns:
        str : HF repo URL

    WHY DEFAULT PARAMS?
    Constants se default milta hai — koi bhi override kar sakta hai:
        push_model_to_huggingface(repo_id="other/repo")
    """
    try:
        logging.info(f"Pushing to HuggingFace: {repo_id}")

        api = HfApi()

        # repo banao — already exist → exist_ok=True se error nahi
        api.create_repo(
            repo_id=repo_id,
            repo_type=repo_type,
            private=private,
            exist_ok=True
        )
        logging.info(f"Repo ready: huggingface.co/{repo_id}")

        # folder upload karo
        api.upload_folder(
            folder_path=folder_path,
            repo_id=repo_id,
            repo_type=repo_type
        )

        url = f"https://huggingface.co/{repo_id}"
        logging.info(f"Model pushed successfully: {url}")
        return url

    except Exception as e:
        raise NetworkSecurityException(e, sys)


def pull_model_from_huggingface(
    repo_id:   str = HF_REPO_ID,
    repo_type: str = HF_REPO_TYPE,
    save_dir:  str = HF_MODEL_DIR
) -> str:
    """
    HuggingFace se model download karta hai local mein.
    Deployment pe use hoga — final_model/ nahi hogi server pe.

    Parameters:
        repo_id  (str) : HF repo naam
        repo_type(str) : "model"
        save_dir (str) : local folder jahan save karna hai

    Returns:
        str : local folder path
    """
    try:
        from huggingface_hub import snapshot_download

        logging.info(f"Pulling model from HuggingFace: {repo_id}")

        os.makedirs(save_dir, exist_ok=True)

        local_path = snapshot_download(
            repo_id=repo_id,
            repo_type=repo_type,
            local_dir=save_dir
        )

        logging.info(f"Model downloaded to: {local_path}")
        return local_path

    except Exception as e:
        raise NetworkSecurityException(e, sys)