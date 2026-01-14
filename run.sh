#!/bin/bash
# Activate virtual environment and run the Streamlit app
cd "$(dirname "$0")"
export GRPC_VERBOSITY=ERROR
export GRPC_LOG_SEVERITY_LEVEL=ERROR
source venv/bin/activate
streamlit run app.py