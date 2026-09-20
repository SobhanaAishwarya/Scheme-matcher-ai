#!/usr/bin/env bash
# One-click launcher for macOS / Linux: creates a virtual env, installs packages, starts the app.
set -e
cd "$(dirname "$0")"
if [ ! -d ".venv" ]; then
  echo "Creating virtual environment..."
  python3 -m venv .venv
fi
source .venv/bin/activate
echo "Installing requirements..."
pip install -r requirements.txt
echo "Starting Scheme Matcher AI..."
streamlit run app.py
