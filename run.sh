#!/bin/bash
source .venv/bin/activate

streamlit run multi_app.py --server.port 8081

## streamlit run bedrock_app.py --server.port 8082
## streamlit run ollama_app.py --server.port 8083