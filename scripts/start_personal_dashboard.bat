@echo off
echo Starting Personal Role Profile Dashboard...
cd /d "%~dp0.."
python -m streamlit run src/personal_dashboard.py
pause
