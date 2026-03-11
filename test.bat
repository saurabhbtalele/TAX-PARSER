@echo off
:: Simplified test script to avoid CMD parser issues

if exist ".venv\Scripts\pytest.exe" goto :RUN_TESTS
echo [ERROR] pytest not found in .venv.
echo Please run the setup steps first.
exit /b 1

:RUN_TESTS
echo Starting test suite...
".venv\Scripts\pytest.exe" %*
goto :EOF
