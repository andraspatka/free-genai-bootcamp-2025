#!/bin/bash

export HF_TOKEN=$(aws ssm get-parameter --name "/poc-free-genai-bootcamp/hf-token" --with-decryption --query "Parameter.Value" --output text)

docker compose down
docker compose up --build -d

LLM_MODEL_ID="meta-llama/Llama-3.2-1B"

curl http://localhost:3008/v1/audioqna \
    -H "Content-Type: application/json" \
    -d '{
        "messages": "Tell me a short story about a robot learning to be human"
    }'

# TGI test only
curl localhost:8008/v1/chat/completions \
    -X POST \
    -d '{
  "model": "'${LLM_MODEL_ID}'",
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
