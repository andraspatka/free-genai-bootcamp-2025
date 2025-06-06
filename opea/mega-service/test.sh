#!/bin/bash

# Test the mega-service
# This script contains all of the commands that need to be executed in order to test the mega-service

export HF_TOKEN=$(aws ssm get-parameter --name "/poc-free-genai-bootcamp/hf-token" --with-decryption --query "Parameter.Value" --output text)
# export LLM_MODEL_ID="meta-llama/Llama-3.2-1B"

export LLM_MODEL_ID="ministral/Ministral-3b-instruct"

docker compose down
docker compose up --build -d

function llm_tts_test() {
  curl http://localhost:3008/v1/audioqna \
      -H "Content-Type: application/json" \
      -d '{
          "messages": "Tell me a joke"
      }' | tr -d '"' | base64 --decode > audio_response_joke.mp3

  aws s3 cp audio_response_joke.mp3 s3://poc-free-genai-bootcamp-data/audio_reponse_joke.mp3
}

function tgi_test() {
  # TGI test only
  curl http://localhost:8008/generate \
      -X POST \
      -d '{"inputs":"What is Deep Learning?","parameters":{"max_new_tokens":20}}' \
      -H 'Content-Type: application/json'

  # doesn't work with meta-llama/Llama-3.2-1B
  curl http://localhost:8008/v1/chat/completions \
      -X POST \
      -d '{
    "messages": [
      {
        "role": "system",
        "content": "You are a helpful assistant."
      },
      {
        "role": "user",
        "content": "What is deep learning?"
      }
    ],
    "stream": true,
    "max_tokens": 20
  }' \
      -H 'Content-Type: application/json'
}

tgi_test

llm_tts_test
