#!/bin/bash

curl -X POST "http://localhost:3008/v1/audioqna" \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {
        "role": "user",
        "content": "Tell me a short story about a robot learning to be human"
      }
    ],
    "max_tokens": 128,
    "top_k": 10,
    "top_p": 0.95,
    "temperature": 0.7,
    "frequency_penalty": 0.0,
    "presence_penalty": 0.0,
    "repetition_penalty": 1.03,
    "voice": "default"
  }'