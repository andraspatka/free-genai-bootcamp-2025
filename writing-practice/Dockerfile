# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

RUN apt-get update && apt-get upgrade -y && \
    apt-get install -y \
        tesseract-ocr \
        tesseract-ocr-ita \
        libgl1-mesa-glx \
        && \
    apt-get clean autoclean && \
    apt-get autoremove -y && \
    rm -rf /var/lib/apt/lists/*

# Copy the requirements file first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt && pip install watchfiles

# Copy the entire project
COPY frontend frontend
COPY backend backend

# Set PYTHONPATH to include the current directory
ENV PYTHONPATH=/app:$PYTHONPATH

# Expose the port Streamlit will run on
EXPOSE 8501

# Set environment variables for AWS credentials (will be overridden by docker-compose)
ENV AWS_ACCESS_KEY_ID=""
ENV AWS_SECRET_ACCESS_KEY=""
ENV AWS_REGION=""
ENV GRADIO_SERVER_NAME="0.0.0.0"
ENV PYTHONUNBUFFERED=1

# Run the Streamlit application
# Make sure to not watch the entire /app directory as it contains the transcripts folder
# The transcripts folder gets changed after transcript download which causes the server to restart and lose the
# session state
CMD ["watchfiles", "python frontend/main.py", "/app/backend", "/app/frontend"]
