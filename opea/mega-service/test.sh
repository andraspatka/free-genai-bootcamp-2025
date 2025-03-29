#!/bin/bash

export HF_TOKEN=$(aws ssm get-parameter --name "/poc-free-genai-bootcamp/hf-token" --with-decryption --query "Parameter.Value" --output text)
export LLM_MODEL_ID="meta-llama/Llama-3.2-1B"

export LLM_MODEL_ID="ministral/Ministral-3b-instruct"

docker compose down
docker compose up --build -d



curl http://localhost:3008/v1/audioqna \
    -H "Content-Type: application/json" \
    -d '{
        "messages": "Tell me a short story about a robot learning to be human"
    }'

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
