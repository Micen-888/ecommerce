@echo off
echo Starting Global E-Commerce OLAP Dashboard...
copy .env.example .env >nul 2>nul
python -m venv .venv
call .venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
docker compose up -d
python -m src.etl
streamlit run app.py
