# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# # Install system dependencies
# RUN apt-get update && apt-get install -y \
#     build-essential \
#     curl \
#     software-properties-common \
#     git \
#     && rm -rf /var/lib/apt/lists/*

# Copy the current directory contents into the container at /app
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

# Expose the port Streamlit will run on
EXPOSE 8501

# Create a directory for exports
RUN mkdir -p /app/exports

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Run the application
CMD ["streamlit", "run", "app.py"]