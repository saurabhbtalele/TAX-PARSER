#!/bin/bash

# ---------------------------------------------------------
# TAX PARSER - FASTAPI SERVER (macOS/Linux)
# ---------------------------------------------------------

# Colors for terminal
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================================${NC}"
echo -e "${BLUE}                T A X   S E R V E R             ${NC}"
echo -e "${BLUE}========================================================${NC}"
echo ""

# 1. Check Virtual Environment
if [ -f ".venv/bin/python" ]; then
    PYTHON_EXE=".venv/bin/python"
elif [ -f "venv/bin/python" ]; then
    PYTHON_EXE="venv/bin/python"
else
    echo -e "${RED}[ERROR] Virtual environment not found.${NC}"
    echo "Please run the following setup steps first:"
    echo "  python3 -m venv .venv"
    echo "  source .venv/bin/activate"
    echo "  pip install -r requirements.txt"
    echo ""
    read -p "Press enter to exit..."
    exit 1
fi

echo -e "${GREEN}Starting FastAPI web server...${NC}"
echo -e "Access the UI at: ${BLUE}http://localhost:8000${NC}"
echo ""

# 2. Add src to PYTHONPATH so uvicorn can find tax_parser
export PYTHONPATH=$PYTHONPATH:$(pwd):$(pwd)/src

# 3. Run uvicorn
$PYTHON_EXE -m uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload

echo ""
read -p "Press enter to exit..."
