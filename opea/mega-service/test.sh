#!/bin/bash

curl http://localhost:3008/v1/audioqna \
    -H "Content-Type: application/json" \
    -d '{
        "messages": "Tell me a short story about a robot learning to be human"
    }'
