# 🐍 PythonAnywhere — Complete Flask Deployment Guide

> A production-tested guide based on real deployment experience. Includes every error encountered and how it was resolved.

---

## 📌 What is PythonAnywhere?

PythonAnywhere is a cloud platform specifically designed for Python applications. Unlike AWS or Heroku, it requires **zero infrastructure knowledge** — no EC2, no Docker, no load balancers. You just upload your code and configure a web app.

### Key Features

| Feature | Details |
|---|---|
| Platform | Python-native (built for Python apps) |
| Hosting | Shared hosting (free) or dedicated (paid) |
| Flask support | Native — no extra config needed |
| SSH/Console | Browser-based Bash console |
| Always-on | Free tier stays up (no sleep like Render) |
| HTTPS | Automatically provided |
| Jupyter | Not on free tier |

### Plans

| Plan | Cost | Web Apps | CPU/day | Storage |
|---|---|---|---|---|
| **Beginner (Free)** | $0 | 1 | 100s | 512MB |
| Developer | $10/mo | 1 | 5000s | 5GB |
| Custom | $10-500/mo | Up to 20 | Up to 100k | Custom |

> **Free tier restriction:** Outbound internet access is restricted. Your app cannot make external API calls. For local ML apps (loading pkl files), this is not an issue.

---

## 🗂️ How PythonAnywhere Works

```
Your Code (GitHub)
        │
        ▼
PythonAnywhere Server
├── Bash Console     ← you run commands here (like your local terminal)
├── Files tab        ← browse/edit files
├── Web tab          ← configure your Flask web app
│   ├── WSGI file    ← tells server HOW to run your Flask app
│   └── Reload btn   ← restart server after changes
└── your-username.pythonanywhere.com  ← public URL
```

### What is WSGI?

WSGI (Web Server Gateway Interface) = the bridge between the web server and your Python app.

```
Browser Request
      ↓
PythonAnywhere Web Server (nginx)
      ↓
WSGI file (/var/www/username_pythonanywhere_com_wsgi.py)
      ↓
Your Flask app (app.py)
      ↓
Response back to browser
```

The WSGI file is what you configure to tell the server:
- Where your project is
- Which Python object is your Flask app

---

## 🚀 Step-by-Step Deployment Guide

### Prerequisites
- GitHub account with your Flask project
- PythonAnywhere account (free Beginner account)
- Your project must have `requirements.txt`

---

### STEP 1 — Create PythonAnywhere Account

```
1. Go to pythonanywhere.com
2. Click "Create a Beginner account"
3. Choose username carefully — becomes your URL:
   username.pythonanywhere.com
4. Verify email
```

---

### STEP 2 — Open Bash Console

```
Dashboard → New console → $ Bash
```

This is your terminal — same as your local machine's terminal.

---

### STEP 3 — Clone Your GitHub Repository

```bash
git clone https://github.com/your-username/your-repo.git
cd your-repo
```

> **IMP:** Make sure your repo has `requirements.txt` with all dependencies.

---

### STEP 4 — Install Dependencies

```bash
# IMP: use --user flag on PythonAnywhere free tier
pip install -r requirements.txt --user
pip install -e . --user   # if you have setup.py
```

> **Best Practice:** Always use `--user` flag on free tier. Without it, you may get permission errors.

---

### STEP 5 — Run Your Pipeline (if needed)

If your app requires trained model files (pkl files), run your training pipeline:

```bash
# IMP: use the SAME Python version that WSGI uses (Python 3.10)
# Check what Python version is set in Web tab first
PYTHONPATH=. python3.10 src/components/data_ingestion.py
```

> **CRITICAL:** Always match the Python version between your pipeline and WSGI. See Error #4 below.

---

### STEP 6 — Create Web App

```
1. Dashboard → Web tab → "Add a new web app"
2. Click Next
3. Select Flask
4. Select Python 3.10 (recommended — most compatible)
5. Path: /home/your-username/your-repo/app.py
6. Click Next → web app created
```

---

### STEP 7 — Configure WSGI File

After creating the web app, PythonAnywhere creates a WSGI file automatically. You must edit it.

```
Web tab → WSGI configuration file → click the link
```

**Delete everything** and replace with:

```python
import sys
import os

# IMP: set working directory FIRST
# this ensures relative paths (like "artifacts/model.pkl") work correctly
os.chdir('/home/your-username/your-repo')

# add project to Python path so imports work
sys.path.insert(0, '/home/your-username/your-repo')

# import your Flask app
# 'app' = filename (app.py), 'app' = Flask object name inside that file
from app import app as application
```

> **Save** (Ctrl+S) after editing.

**Why `os.chdir()`?**
Without it, the working directory is `/home/your-username/` — so relative paths like `artifacts/model.pkl` resolve to `/home/your-username/artifacts/model.pkl` which doesn't exist. `os.chdir()` fixes this.

---

### STEP 8 — Reload Web App

```
Web tab → Green "Reload" button → click it
```

Every time you make changes (code, WSGI file, new pkl files), you must reload.

---

### STEP 9 — Visit Your App

```
https://your-username.pythonanywhere.com
```

---

### STEP 10 — Debugging Errors

If something goes wrong:

```
Web tab → Log files section
├── Error log   ← most useful — shows Python tracebacks
├── Access log  ← shows HTTP requests (200, 500 etc.)
└── Server log  ← server-level issues
```

```bash
# Or from Bash console:
tail -50 /var/log/your-username.pythonanywhere.com.error.log
```

> **IMP:** Always check the **timestamp** on the error log. Old errors from before your last reload should be ignored — only look at errors after your last reload time.

---

## ⚠️ Errors Encountered & How We Fixed Them

### Error 1 — `ImportError: cannot import name 'application' from 'app'`

```
ImportError: cannot import name 'application' from 'app'
```

**Cause:** WSGI file was trying to import `application` but Flask object in `app.py` was named `app`.

**Fix:** Change WSGI import line:
```python
# Wrong
from app import application

# Correct
from app import app as application
```

---

### Error 2 — PythonAnywhere Overwrote `app.py`

**What happened:** When creating the web app, PythonAnywhere replaced our `app.py` with a default Hello World Flask template.

**Symptoms:** App showed "Hello from Flask!" instead of our actual app.

**Fix:**
```bash
# restore from git
git checkout -- app.py

# or pull from GitHub
git pull origin master
```

**Best Practice:** Always run `git status` after creating a web app to check if any files were modified.

---

### Error 3 — `FileNotFoundError: artifacts/model.pkl`

```
FileNotFoundError: No such file or directory: 'artifacts/model.pkl'
```

**Cause:** Two possible causes:
1. Relative path resolving to wrong directory (working directory was `/home/alyanktk/` not project root)
2. Pipeline was never run on PythonAnywhere — pkl files didn't exist

**Fix 1 — Set working directory in WSGI:**
```python
import os
os.chdir('/home/your-username/your-repo')
```

**Fix 2 — Run pipeline on PythonAnywhere:**
```bash
PYTHONPATH=. python3.10 src/components/data_ingestion.py
```

---

### Error 4 — `ModuleNotFoundError: No module named 'numpy._core'`

```
ModuleNotFoundError: No module named 'numpy._core'
```

**Cause:** pkl files were created on local machine with **numpy 2.5.0** but PythonAnywhere had **numpy 2.1.0**. The pkl file referenced `numpy._core` which doesn't exist in older numpy.

**Root cause:** Different Python versions + numpy versions between local machine and server.

```
Local machine    → Python 3.14 + numpy 2.5.0 → pkl created here
PythonAnywhere   → Python 3.10 + numpy 2.1.0 → pkl loaded here
Result           → CRASH — incompatible
```

**Fix — Run pipeline on PythonAnywhere using same Python as WSGI:**
```bash
# Check which Python WSGI uses (Web tab → Python version)
# Then run pipeline with THAT version:
PYTHONPATH=. python3.10 src/components/data_ingestion.py
```

This generates fresh pkl files using Python 3.10 + numpy 2.1.0 — same as what WSGI uses.

**Key Learning:** Always generate pkl files on the **same environment** that will load them. Never copy pkl files from a different Python/numpy version.

---

### Error 5 — `ModuleNotFoundError: No module named 'src'`

```
ModuleNotFoundError: No module named 'src'
```

**Cause:** Running Python script without setting PYTHONPATH — Python couldn't find the `src` package.

**Fix:**
```bash
# Wrong
python3.10 src/components/data_ingestion.py

# Correct
PYTHONPATH=. python3.10 src/components/data_ingestion.py
```

---

## ✅ Best Practices Summary

```
1. ALWAYS use --user flag when pip installing on free tier

2. ALWAYS match Python version between WSGI and pipeline run
   Check: Web tab → Python version
   Then:  python3.X (same X) to run scripts

3. ALWAYS use os.chdir() in WSGI file for projects with relative paths

4. ALWAYS run pipeline ON PythonAnywhere — never copy pkl from local

5. ALWAYS check error log timestamp — ignore old errors before last reload

6. ALWAYS use PYTHONPATH=. when running scripts that import src package

7. AFTER every change: reload Web app before testing

8. git pull to update code, then Reload — two separate steps
```

---

## 🔄 Update Workflow (After Initial Deploy)

```bash
# 1. Pull latest code
cd /home/your-username/your-repo
git pull origin master

# 2. If model changed, retrain
PYTHONPATH=. python3.10 src/components/data_ingestion.py

# 3. Go to Web tab → Reload
```

---

## 📁 Project Structure Requirements

```
your-repo/
├── app.py              ← Flask app — must have Flask object named 'app'
├── requirements.txt    ← all dependencies
├── setup.py            ← if using src/ package structure
├── src/
│   ├── __init__.py
│   ├── components/
│   ├── pipeline/
│   ├── exception.py
│   ├── logger.py
│   └── utils.py
├── templates/          ← HTML files
│   ├── index.html
│   └── home.html
└── artifacts/          ← generated on server by running pipeline
    ├── model.pkl
    ├── preprocessor.pkl
    └── threshold.pkl   ← (if using custom threshold)
```

> **IMP:** `artifacts/` should be in `.gitignore` — generate on server by running pipeline. Never push pkl files from local machine (version mismatch issues).

---

## 🔗 Useful Links

- PythonAnywhere Dashboard: pythonanywhere.com/dashboard
- Error Log: `/var/log/username.pythonanywhere.com.error.log`
- WSGI File: `/var/www/username_pythonanywhere_com_wsgi.py`
- Help Docs: help.pythonanywhere.com

---

*Guide written based on real deployment of Heart Disease Predictor — End-to-End ML Flask App*
*M. Alyan Khattak — github.com/Alyan-khattak*