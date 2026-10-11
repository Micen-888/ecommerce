#!/usr/bin/env bash
set -e
cp -n .env.example .env || true

if command -v python3.11 >/dev/null 2>&1; then
  PYTHON_BIN="python3.11"
elif [ -x "$(brew --prefix python@3.11 2>/dev/null)/bin/python3.11" ]; then
  PYTHON_BIN="$(brew --prefix python@3.11)/bin/python3.11"
else
  PYTHON_BIN="python3"
fi

echo "Using Python: $($PYTHON_BIN --version)"
$PYTHON_BIN -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip setuptools wheel
pip install -r requirements.txt

echo "Starting PostgreSQL only. MongoDB is expected to run locally or via your own service."
docker compose up -d postgres
python -m src.etl
streamlit run app.py
