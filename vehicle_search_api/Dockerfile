# Use an official Python runtime as a parent image
FROM python:3.9-slim-buster

# Set environment variables for Python
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory in the container
WORKDIR /app_code

# Install system dependencies if any were needed (none for this basic app yet)
# RUN apt-get update && apt-get install -y --no-install-recommends some-package

# Install Python dependencies
# Copy only requirements.txt first to leverage Docker cache
COPY ./requirements.txt /app_code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /app_code/requirements.txt

# Copy the application code into the container
COPY ./app /app_code/app

# Copy the .env file into the container
# IMPORTANT: For production, it's generally recommended to pass environment variables
# directly to the container at runtime (e.g., via docker run -e, docker-compose environment, or Kubernetes secrets)
# rather than copying the .env file into the image.
# This .env file is expected by app/main.py at ../.env relative to its own path,
# which means it should be at /app_code/.env if main.py is at /app_code/app/main.py
COPY ./.env /app_code/.env

# Expose the port the app runs on
EXPOSE 8000

# Define the command to run the application
# The command assumes that uvicorn will find app.main:app
# Uvicorn needs to be run from a directory where 'app' is a discoverable package/module.
# Running from /app_code, 'app.main' should be correct.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
