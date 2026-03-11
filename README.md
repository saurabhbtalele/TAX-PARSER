# Tax Parser Engine

Core parsing engine for extracting structured data from scanned US tax form PDFs using Azure Document Intelligence and OpenAI.

## Project Overview

This project provides a robust pipeline for:
1. **Preprocessing**: Deskewing and watermark removal for scanned documents.
2. **Classification**: Automatically identifying the type of tax form (e.g., 1120, 1120-S, 1065, K-1).
3. **Extraction**: Using Azure Document Intelligence and LLMs (OpenAI) to extract structured data into Pydantic models.
4. **Validation**: Ensuring extracted data meets business rules and consistency checks.

## Quick Start

### 1. Prerequisites
- Python 3.10 or higher.
- Azure OpenAI credentials.
- Azure Document Intelligence credentials.
- Poppler installed (for PDF to image conversion).

### 2. Setup
Run the following commands to set up the environment and install dependencies:

```powershell
python -m venv .venv
.\.venv\Scripts\pip install -r requirements.txt
```

### 3. Configuration
Copy `.env.example` to `.env` and fill in your credentials:
```bash
cp .env.example .env
```

## Usage

### Process a Tax Form
Use the provided `run.bat` script for easy execution:

```powershell
.\run.bat path/to/your/tax_form.pdf
```

Available options:
- `--form-type`: Hint the form type (e.g., `1120-S`, `1065`) to skip classification.
- `--output`: Save results to a specified JSON file.
- `--verbose`: Enable detailed logging.

### Common Examples

**Automatic Classification**:
```powershell
.\run.bat "tax_returns_business\tax_returns_business_001.pdf"
```

**Partnership K-1**:
```powershell
.\run.bat "tax_returns_business\K1 (2).pdf" --form-type "Schedule K-1 (Partnership)" -o result_k1.json -v
```

**S-Corp K-1**:
```powershell
.\run.bat "tax_returns_business\1120s_K1_1.pdf" --form-type "Schedule K-1 (S-Corp)" -o result_k1_1.json -v
```

**Form 1120-S**:
```powershell
.\run.bat "tax_returns_business/tax_returns_business_002.pdf" --form-type "1120-S" -o result.json -v
```

### Running Tests
Use the `test.bat` script to run the test suite:

```powershell
.\test.bat
```

## Project Structure

- `src/tax_parser/`: Core engine logic.
  - `engine.py`: Main entry point for the parsing pipeline.
  - `classifier.py`: Document type identification.
  - `preprocessor.py`: Image cleaning and enhancement.
  - `models/`: Pydantic schemas for extracted data.
- `examples/`: Usage samples and demonstration scripts.
- `tests/`: Comprehensive test suite.
- `tax_returns_business/`: Directory containing sample PDFs for testing.

## License
MIT
