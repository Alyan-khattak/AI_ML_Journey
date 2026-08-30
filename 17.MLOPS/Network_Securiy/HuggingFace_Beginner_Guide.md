# 🤗 Hugging Face — Beginner Guide

Hugging Face = ML community platform. Models, datasets, aur spaces free mein host kar sakte ho.

---

## Why Hugging Face?

```
Problem: model.pkl local machine pe hai — server pe nahi
Solution: HF pe push karo → koi bhi download kar sakta hai
          deployment pe hf_hub_download() se load karo
```

---

## Account + Token Setup

```
1. huggingface.co → Sign Up (free)

2. Settings → Access Tokens → New Token
   Name: anything (e.g. "write-token")
   Type: WRITE ← zaroori (Read se repo create nahi hoga)
   → Generate → Copy token (hf_xxxx...)

3. Terminal mein login:
   hf auth login --force
   → token paste karo → Enter

4. Verify:
   hf auth whoami
   → tumhara username dikhega
```

IMP: Username exactly match karna chahiye — case sensitive hai.
```
HF profile pe username dekho: alyan-ktk (not Alyan-khattak)
repo_id = "alyan-ktk/repo-naam"  ← exact username
```

---

## Install

```bash
pip install huggingface_hub
```

---

## Repo Banao + Files Upload Karo

```python
from huggingface_hub import HfApi

api = HfApi()

# Repo banao
api.create_repo(
    repo_id="alyan-ktk/networksecurity-mlops",
    repo_type="model",   # "model" / "dataset" / "space"
    private=False,       # free mein public rehta hai
    exist_ok=True        # already exist → error nahi
)

# Folder upload karo
api.upload_folder(
    folder_path="final_model/",
    repo_id="alyan-ktk/networksecurity-mlops",
    repo_type="model"
)
```

Result:
```
huggingface.co/alyan-ktk/networksecurity-mlops
├── model.pkl
└── preprocessor.pkl
```

---

## Model Download Karo (Deployment pe)

```python
from huggingface_hub import hf_hub_download

# single file download
model_path = hf_hub_download(
    repo_id="alyan-ktk/networksecurity-mlops",
    filename="model.pkl"
)

# ya poora folder download karo
from huggingface_hub import snapshot_download

local_path = snapshot_download(
    repo_id="alyan-ktk/networksecurity-mlops",
    repo_type="model",
    local_dir="final_model/"
)
```

---

## Is Project Mein Kaise Use Kiya

```python
# networksecurity/cloud/hf_syncer.py
from huggingface_hub import HfApi

def push_model_to_huggingface(folder_path, repo_id):
    api = HfApi()
    api.create_repo(repo_id=repo_id, exist_ok=True)
    api.upload_folder(folder_path=folder_path, repo_id=repo_id)

# model_trainer.py ke end mein:
push_model_to_huggingface(
    folder_path="final_model/",
    repo_id="alyan-ktk/networksecurity-mlops"
)
```

Constants mein configure kiya:
```python
# constants/training_pipeline/__init__.py
HF_REPO_ID   = "alyan-ktk/networksecurity-mlops"
HF_REPO_TYPE = "model"
HF_MODEL_DIR = "final_model/"
```

---

## Quick Reference

| Action | Code |
|---|---|
| Login | `hf auth login --force` |
| Whoami | `hf auth whoami` |
| Repo create | `api.create_repo(repo_id, exist_ok=True)` |
| Upload folder | `api.upload_folder(folder_path, repo_id)` |
| Download file | `hf_hub_download(repo_id, filename)` |
| Download all | `snapshot_download(repo_id, local_dir)` |

---

## Common Errors

```
403 Forbidden   → token Type "Read" hai → "Write" token banao

403 Namespace   → repo_id mein username galat hai
                  huggingface.co pe profile check karo
                  exact username use karo (case sensitive)

Already logged  → hf auth login --force se force re-login karo
```

---

*Used in: NetworkSecurity MLOps Pipeline — M. Alyan Khattak*