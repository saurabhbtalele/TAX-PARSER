@echo off
setlocal EnableDelayedExpansion

:: ---------------------------------------------------------
:: TAX PARSER - INTERACTIVE CLI
:: ---------------------------------------------------------

:: Set Colors
color 0B
echo.
echo ========================================================
echo                 T A X   P A R S E R
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
:: 2. Determine Input Mode
set "INPUT_FILE=%~1"
set "SECOND_ARG=%~2"

:: If multiple arguments are provided (e.g. -o, --form-type), pass them all through directly
if not "!SECOND_ARG!"=="" (
    echo [INFO] Running with manual arguments: %*
    goto :EXECUTE_FULL
)

:: If only one file was passed, skip the file prompt but allow form hint
if not "!INPUT_FILE!"=="" goto :PROMPT_FORM

:: Interactive Prompt for File
:PROMPT_FILE
color 0f
echo Please enter the path to the PDF tax form you want to process.
echo (Or drag and drop the file into this window and press Enter)
echo.
set /p INPUT_FILE="PDF Path: "

:: Remove extra quotes if dragged in
set "INPUT_FILE=!INPUT_FILE:"=!"
if "!INPUT_FILE!"=="" (
    color 0E
    echo [WARNING] No file path provided.
    echo.
    goto :PROMPT_FILE
)
if not exist "!INPUT_FILE!" (
    color 0C
    echo [ERROR] File not found: "!INPUT_FILE!"
    echo.
    goto :PROMPT_FILE
)

:: 3. Optional Parameters (Form Type)
:PROMPT_FORM
color 0f
echo.
echo [Optional] Enter the Form Type if known. Supported types:
echo   - 1120-S, 1065, 1120, W-2, 1040
echo   - Schedule K-1 (Partnership)
echo   - Schedule K-1 (S-Corp)
echo.
echo Leave blank to let the AI automatically classify the document.
set "FORM_TYPE="
set /p FORM_TYPE="Form Type [Blank for Auto]: "

:: 4. Execution
:EXECUTE_INTERACTIVE
color 0A
echo.
echo ========================================================
echo Starting Extraction Engine...
echo ========================================================
echo.

set "PYTHON_EXE=.\.venv\Scripts\python.exe"
set "EXTRACT_SCRIPT=examples/extract_sample.py"
set "OUTPUT_ARGS=-o result.json -v"

if "!FORM_TYPE!"=="" (
    set "FINAL_CMD="!PYTHON_EXE!" "!EXTRACT_SCRIPT!" "!INPUT_FILE!" !OUTPUT_ARGS!"
) else (
    set "FINAL_CMD="!PYTHON_EXE!" "!EXTRACT_SCRIPT!" "!INPUT_FILE!" --form-type "!FORM_TYPE!" !OUTPUT_ARGS!"
)
goto :RUN_COMMAND

:EXECUTE_FULL
set "PYTHON_EXE=.\.venv\Scripts\python.exe"
set "EXTRACT_SCRIPT=examples/extract_sample.py"
set "FINAL_CMD="!PYTHON_EXE!" "!EXTRACT_SCRIPT!" %*"

:RUN_COMMAND
:: Run it
echo Running: !FINAL_CMD!
echo.
color 0f
!FINAL_CMD!

:: Done
echo.
if %errorlevel% equ 0 goto :SUCCESS
color 0C
echo ========================================================
echo ERROR! Extraction failed. Please check the logs above.
echo ========================================================
goto :END

:SUCCESS
color 0A
echo ========================================================
echo SUCCESS! Extraction complete. Results saved to result.json
echo ========================================================

:END
echo.
pause
color 07
exit /b %errorlevel%
