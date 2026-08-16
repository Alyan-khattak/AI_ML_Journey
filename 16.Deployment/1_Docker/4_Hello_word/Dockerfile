# ============================================================
# 1. BASE IMAGE
# ============================================================

# FROM specifies the base image that our Docker image will use.
#
# python:3.8-alpine means:
#
#   python  → Python Docker image
#   3.8     → Python version
#   alpine  → Alpine Linux, a very small Linux distribution
#
# Docker will first download/use this image as the foundation
# of our own image.
#
# So conceptually:
#
#       Python 3.8 + Alpine Linux
#               ↓
#          Base Image
#               ↓
#        Our application
#
FROM python:3.8-alpine


# ============================================================
# 2. COPY APPLICATION FILES
# ============================================================

# COPY copies files/directories from our LOCAL machine
# into the Docker image.
#
# Syntax:
#
# COPY <source> <destination>
#
# "." means:
# "Take the contents of the current directory"
#
# "/app" means:
# "Put those files inside the /app directory
#  inside the Docker image/container."
#
# Docker will create /app if necessary.
#
# For example, if our local project looks like:
#
# project/
# ├── Dockerfile
# ├── app.py
# └── requirements.txt
#
# after COPY:
#
# Docker Image
# └── /app
#     ├── Dockerfile
#     ├── app.py
#     └── requirements.txt
#
COPY . /app


# ============================================================
# 3. WORKING DIRECTORY
# ============================================================

# WORKDIR sets the current working directory inside
# the image/container.
#
# After this instruction:
#
#     /app
#
# becomes the current directory.
#
# So commands that come after WORKDIR will be executed
# relative to /app.
#
# For example:
#
#     RUN pip install -r requirements.txt
#
# is effectively working with:
#
#     /app/requirements.txt
#
# Instead of having to write:
#
#     /app/requirements.txt
#
# every time.
#
WORKDIR /app


# ============================================================
# 4. INSTALL PYTHON DEPENDENCIES
# ============================================================

# RUN executes a command while Docker is BUILDING the image.
#
# requirements.txt contains the Python packages our application
# needs.
#
# For example:
#
# requirements.txt
# ─────────────────
# Flask
#
# When Docker executes:
#
#     pip install -r requirements.txt
#
# pip reads requirements.txt and installs everything listed there
# into the Docker image.
#
# IMPORTANT:
#
# This happens during IMAGE BUILDING.
#
# It is NOT executed every time the container starts.
#
RUN pip install -r requirement.txt


# ============================================================
# 5. START THE APPLICATION
# ============================================================

# CMD specifies the default command that Docker should execute
# when a container is started from this image.
#
# Here we are telling Docker:
#
#     Run app.py using Python
#
# So when we execute:
#
#     docker run myflaskapp
#
# Docker will effectively execute:
#
#     python app.py
#
# IMPORTANT:
#
# RUN  → executes while BUILDING the image
#
# CMD  → executes when RUNNING the container
#
CMD ["python", "app.py"]