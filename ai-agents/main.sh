#!/bin/bash

# Start the Docker container if it's not already running
docker-compose up -d

# Run the main.py script in the container
docker-compose exec ai-agents python /app/main.py
