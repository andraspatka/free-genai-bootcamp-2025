FROM node:22-slim

WORKDIR /app

# Copy package files first to leverage Docker cache
COPY package*.json ./
RUN npm install

# Copy the rest of the application
COPY . .

# Build the application
RUN npm run build && \
    node generate-serve-config.js && \
    cp /app/serve.json /app/dist/serve.json

# Install serve to run the built application
RUN npm install -g serve

# Expose port 8080
EXPOSE 8080

# Run the application with the serve configuration
CMD ["serve", "-s", "dist", "-l", "8080", "--config", "serve.json"]
