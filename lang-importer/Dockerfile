# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

# Expose the port Streamlit will run on
EXPOSE 8501

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Run the application
CMD ["streamlit", "run", "app.py"]
