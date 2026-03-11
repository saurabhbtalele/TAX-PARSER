@echo off
setlocal EnableDelayedExpansion

:: ---------------------------------------------------------
:: TAX PARSER - FASTAPI SERVER
:: ---------------------------------------------------------

color 0B
echo.
echo ========================================================
echo                 T A X   S E R V E R
echo ========================================================
echo.

:: Add poppler to PATH for pdf2image (if installed locally)
set "PATH=%PATH%;C:\poppler\poppler-24.08.0\Library\bin"

:: 1. Check Virtual Environment
if exist ".venv\Scripts\python.exe" goto :ENV_OK
color 0C
echo [ERROR] Virtual environment (.venv) not found.
echo Please run the following setup steps first:
echo   python -m venv .venv
echo   .\.venv\Scripts\pip install -r requirements.txt
echo.
pause
exit /b 1

:ENV_OK
color 0A
echo Starting FastAPI web server...
echo Access the UI at: http://localhost:8000
echo.

:: Add src to PYTHONPATH so uvicorn can find tax_parser
set "PYTHONPATH=%CD%;%CD%\src"

.\.venv\Scripts\python.exe -m uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload

echo.
pause
exit /b %errorlevel%
