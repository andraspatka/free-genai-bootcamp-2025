# Use an official Python runtime as a parent image
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /app

# Prevent Python from writing pyc files to disc
ENV PYTHONDONTWRITEBYTECODE 1
# Ensure Python output is sent straight to terminal without buffering
ENV PYTHONUNBUFFERED 1

# Install system dependencies if needed (e.g., for psycopg2)
# RUN apt-get update && apt-get install -y --no-install-recommends \
#     build-essential libpq-dev \
#     && rm -rf /var/lib/apt/lists/*
# Note: Using psycopg2-binary avoids needing libpq-dev usually

# Install pip requirements
# Copy only requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY language_agent language_agent

WORKDIR /app/language_agent

# Make port 8501 available for Streamlit
EXPOSE 8501

# Set default command to run Streamlit
# It will run the frontend app, which imports the backend
# Healthcheck for Streamlit app
# HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health || exit 1

# Run the Streamlit app
ENTRYPOINT ["streamlit", "run", "frontend/app.py", "--server.port=8501", "--server.address=0.0.0.0"]
