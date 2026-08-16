# Use Python 3.7 with Alpine Linux as the base image.
# Alpine is a very small Linux distribution, so the resulting
# Docker image is usually much smaller than a full Python image.
FROM python:3.7-alpine


# Set the working directory inside the container to /code.
#
# If /code does not already exist, Docker creates it.
#
# All commands after this point will be executed relative to /code.
# For example:
#   COPY . .
#   RUN pip install ...
#
# will operate inside /code.
WORKDIR /code


# Set the Flask application file.
#
# Flask needs to know which Python file contains the Flask
# application object.
#
# Our application is assumed to be:
#     app.py
#
# So Flask will look for the application inside app.py.
ENV FLASK_APP=app.py


# Tell Flask to listen on all network interfaces.
#
# 0.0.0.0 is important inside a Docker container.
#
# If Flask only listens on 127.0.0.1 (localhost), it would only
# be accessible from inside the container.
#
# 0.0.0.0 means:
#     "Listen for connections on all available interfaces."
ENV FLASK_RUN_HOST=0.0.0.0


# Copy everything from the current directory on our computer
# into the /code directory inside the Docker image.
#
# The first "." means:
#     Current directory on the HOST
#
# The second "." means:
#     Current WORKDIR inside the CONTAINER (/code)
#
# So:
#
#     COPY . .
#
# essentially means:
#
#     Host project files
#            ↓
#     /code inside container
COPY . .


# Install all Python dependencies listed in requirements.txt.
#
# pip is Python's package manager.
#
# The -r option tells pip:
#     "Read the packages from this requirements file."
#
# For example, if requirements.txt contains:
#
#     Flask
#     redis
#
# pip will install both packages into the Docker image.
#
# --no-cache-dir prevents pip from keeping its package cache,
# which helps keep the Docker image smaller.
RUN pip install --no-cache-dir -r requirements.txt


# Document that the Flask application listens on port 5000.
#
# IMPORTANT:
# EXPOSE does NOT actually publish the port to your host machine.
#
# It simply tells Docker:
#     "This container is expected to use port 5000."
#
# To actually access it from your computer, you would use
# a port mapping when running the container, for example:
#
#     docker run -p 5000:5000 <image-name>
EXPOSE 5000


# Start the Flask development server when the container starts.
#
# Because we already defined:
#
#     FLASK_APP=app.py
#     FLASK_RUN_HOST=0.0.0.0
#
# Flask knows:
#     - which application to run
#     - which interface to listen on
#
# The command is written in exec/JSON form:
#
#     ["flask", "run"]
#
# This is preferable to:
#
#     CMD ["flask ", "run"]
#
# because "flask " contains an unnecessary space.
CMD ["flask", "run"]