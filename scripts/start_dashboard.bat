@echo off
cd /d "%~dp0.."
echo Starting Time Analytics Dashboard...
echo.
echo The dashboard will open in your browser at http://localhost:8501
echo.
echo Press Ctrl+C to stop the server
echo.
python -m streamlit run src/interactive_dashboard.py
