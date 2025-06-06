# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt && pip install watchfiles

# Copy the entire project
COPY backend backend
COPY frontend frontend

# Set PYTHONPATH to include the current directory
ENV PYTHONPATH=/app:$PYTHONPATH

# Expose the port Streamlit will run on
EXPOSE 8501

# Set environment variables for AWS credentials (will be overridden by docker-compose)
ENV AWS_ACCESS_KEY_ID=""
ENV AWS_SECRET_ACCESS_KEY=""
ENV AWS_REGION=""

# Run the Streamlit application
# Make sure to not watch the entire /app directory as it contains the transcripts folder
# The transcripts folder gets changed after transcript download which causes the server to restart and lose the
# session state
CMD ["watchfiles", "streamlit run frontend/main.py --server.port=8501 --server.address=0.0.0.0", "/app/backend", "/app/frontend"]
