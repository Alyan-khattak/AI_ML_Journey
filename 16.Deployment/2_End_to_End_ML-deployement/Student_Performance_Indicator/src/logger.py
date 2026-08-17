# logger.py — Every event (info, error, warning) gets written to a log FILE.
# Log file auto-named with timestamp so each run makes its own file.
# Helps debug what went wrong and when — without print statements.

import logging
import os
from datetime import datetime

# ── LOG FILE NAME ──────────────────────────────────────────
# datetime.now()              → current date & time object
# .strftime('%m_%d_%Y_%H_%M') → format it as string
#   %m = month (08), %d = day (17), %Y = year (2026)
#   %H = hour (14),  %M = minute (32)
# result → "08_17_2026_14_32.log"
LOG_FILE_NAME = f"{datetime.now().strftime('%m_%d_%Y_%H_%M')}.log"

# ── LOG FOLDER PATH ────────────────────────────────────────
# os.getcwd()                 → current working directory, e.g. /home/aizen/mlproject
# os.path.join(...)           → safely joins paths (handles / for you)
# result → "/home/aizen/mlproject/logs/08_17_2026_14_32.log"  ← folder path
logs_path_folder = os.path.join(os.getcwd(), "logs", LOG_FILE_NAME)

# creates the folder if it doesn't exist — exist_ok=True means no crash if already there
os.makedirs(logs_path_folder, exist_ok=True)

# ── FULL FILE PATH ─────────────────────────────────────────
# logs_path is the FOLDER, LOG_FILE is the FILENAME
# join them → full path to actual .log file inside that folder
# result → "/home/aizen/mlproject/logs/08_17_2026_14_32/08_17_2026_14_32.log"
LOG_FILE_PATH = os.path.join(logs_path_folder, LOG_FILE_NAME)

# ── LOGGING CONFIG ─────────────────────────────────────────
logging.basicConfig(
    filename=LOG_FILE_PATH,     # write logs to this file (not terminal)
    format="[%(asctime)s] %(lineno)d %(name)s - %(levelname)s - %(message)s",
    #        ^^^^^^^^^^^  ^^^^^^^^^^ ^^^^^^^^   ^^^^^^^^^^       ^^^^^^^^^
    #        timestamp    line no    logger     INFO/ERROR        your message
    #        e.g:         e.g: 42    name       level
    #        2026-08-17
    #        14:32:01
    level=logging.INFO,         # capture INFO and above (INFO, WARNING, ERROR, CRITICAL)
)              

                 # DEBUG ignored (below INFO)
                 
# ─────────────────────────────────────────────
# DRY RUN — step by step
#
# Say you run this at 2:32 PM on Aug 17 2026:
#
# 1. LOG_FILE
#       datetime.now()              → 2026-08-17 14:32:00
#       .strftime('%m_%d_%Y_%H_%M') → "08_17_2026_14_32"
#       LOG_FILE                    → "08_17_2026_14_32.log"
#
# 2. logs_path
#       os.getcwd()    → "/home/aizen/mlproject"
#       os.path.join() → "/home/aizen/mlproject/logs/08_17_2026_14_32.log"
#       os.makedirs()  → creates that folder on disk
#
# 3. LOG_FILE_PATH
#       joins logs_path + LOG_FILE
#       → "/home/aizen/mlproject/logs/08_17_2026_14_32.log/08_17_2026_14_32.log"
#                                      ^^^^ folder ^^^^      ^^^^ file ^^^^
#
# 4. logging.basicConfig sets up the logger
#
# 5. somewhere in your code:
#       logging.info("Training started")
#
#    writes this line inside the .log file:
#       [2026-08-17 14:32:05] 42 root - INFO - Training started
#        ^timestamp            ^line  ^logger ^level ^your message
#
# ── BUGS FIXED ────────────────────────────────────────────
# datatime   → datetime        (typo)
# '%H_S'     → '%H_%M'        (%S = seconds, assumed you wanted minutes %M)
# %(acstime) → %(asctime)      (typo)
# ─────────────────────────────────────────────