FROM python:3.11-slim

WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Create empty database directory
RUN mkdir -p /app/data

# Expose port 8000
EXPOSE 8000

RUN invoke init-db

# Run the application
CMD ["python", "app.py"]