@echo off
REM One-click launcher for Windows: creates a virtual env, installs packages, starts the app.
cd /d "%~dp0"
if not exist .venv (
    echo Creating virtual environment...
    python -m venv .venv
)
call .venv\Scripts\activate.bat
echo Installing requirements...
pip install -r requirements.txt
echo Starting Scheme Matcher AI...
streamlit run app.py
pause
