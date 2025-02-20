# Language Vocabulary Importer

## Overview
This Streamlit application generates vocabulary words for language learning using a local LLM.

## Setup
1. Start with Docker:
```bash
make start
```

Wait until the model gets pulled as well. After that you can start the lang importer: `http://localhost:8501/`

## Features
- Generate vocabulary words for different word groups
- Export generated vocabulary to JSON
- Uses local LLM via OPEA's Ollama server

## Technical Details
- Framework: Streamlit
- LLM Endpoint: `ollama-server:8008`

## Generated with AI (Windsurf Cascade Base)

This project was mostly generated with AI. The input prompt was the `TechnicalSpec.md` file.
Minor adjustments were made to the generated code.

