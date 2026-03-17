# Tax Parser — Design Document

**Version:** 0.1.0
**Last Updated:** March 2026

---

## 1. Overview

Tax Parser is a Python-based document processing engine that extracts structured data from scanned US tax form PDFs. It combines Azure Document Intelligence (prebuilt tax models) with Azure OpenAI GPT-4o Vision to classify pages, extract every field, validate the results against IRS arithmetic rules, and flag low-confidence or inconsistent outputs for human review.

The engine is designed as a library-first package — it can be invoked programmatically, from the CLI, or embedded inside a larger application or API service.

---

## 2. Scope

| Capability | Details |
|---|---|
| **PDF ingestion** | Multi-page scanned PDFs converted to images at configurable DPI (default 450). |
| **Image preprocessing** | Deskew, watermark removal, CLAHE enhancement, and per-page quality assessment. |
| **Form classification** | GPT-4o Vision identifies form types with confidence-weighted voting. |
| **Model Comparison** | Side-by-side performance evaluation (Confidence, Cost, Time, Quality) across multiple AI models. |
| **Data extraction** | Dual-strategy: Azure DI prebuilt models for standard forms, GPT-4o Vision for complex business forms. |
| **Modular Extractor Factory** | Plugin-based architecture for easily adding new models (Gemini, Mistral, etc.). |
| **FastAPI Service** | REST API layer for document processing and model orchestration. |
| **Interactive Dashboard** | Modern Web UI with file uploads, analytics charts, and model comparison tables. |
| **Human review flagging** | Intelligent flagging based on confidence, validation errors, and page quality. |

### Out of Scope (Future)

- Asynchronous / parallel batch processing (Celery, etc.).
- Database persistence of extraction results (current results are volatile/JSON-based).
- Multi-tenant access control and audit logging.
- Support for non-US tax forms.

---

## 3. Architecture

### 3.1 High-Level Data Flow

```
┌──────────┐
│  PDF File │
└────┬─────┘
     │
     ▼
┌─────────────────────────────────────────────────────────────────┐
│  1. pdf_to_images()                                             │
│     pdf2image + poppler → list[PIL.Image] at configured DPI     │
└────┬────────────────────────────────────────────────────────────┘
     │
     ▼
┌─────────────────────────────────────────────────────────────────┐
│  2. preprocess_page()  (per page)                               │
│     assess_quality → deskew → remove_watermark → enhance        │
│     Returns: (processed_image, QualityMetrics)                  │
└────┬────────────────────────────────────────────────────────────┘
     │
     ▼
┌─────────────────────────────────────────────────────────────────┐
│  3. FormClassifier.classify_document()                          │
│     GPT-4o Vision (low detail) per page → JSON                  │
│     Confidence-weighted majority vote → primary FormType        │
└────┬────────────────────────────────────────────────────────────┘
     │
     ▼
┌─────────────────────────────────────────────────────────────────┐
│  4. Extraction routing                                          │
│     ┌───────────────────────┬──────────────────────────────┐    │
│     │  Azure DI Forms       │  LLM Extraction Forms        │    │
│     │  (W-2, 1099-*, 1040,  │  (1120-S, 1120, 1065,       │    │
│     │   Schedules B-F)      │   Schedule K-1)              │    │
│     │                       │                              │    │
tax-parser/
├── config/
│   └── settings.py                   # Pydantic-settings configuration
├── docs/
│   ├── ARCHITECTURE_OVERVIEW.md      # High-level design rationale
│   ├── AZURE_OPENAI_SETUP.md         # Azure deployment guide
│   └── DESIGN.md                     # This document
├── src/
│   ├── api/                          # FastAPI REST layer
│   │   ├── main.py                   # API entry point
│   │   ├── routes/                   # Route handlers
│   │   ├── templates/                # Web UI (HTML/JS)
│   │   └── static/                   # CSS/Assets
│   └── tax_parser/                   # Core engine
│       ├── engine.py                 # Orchestration engine
│       ├── classifier.py             # Page classification
│       ├── preprocessor.py           # Image preprocessing
│       ├── extractors/               # modular extractors
│       │   ├── factory.py            # Extractor registry
│       │   ├── azure_di_extractor.py # Azure DI
│       │   └── llm_extractor.py      # GPT-4o
│       ├── models/                   # Pydantic data models
│       ├── schemas/                  # Tax form schemas
│       └── validators/               # Arithmetic validation
├── tests/                            # Automated test suite
├── .env                              # Environment configuration
└── run_server.bat                    # Server start script
�──────────┐
│ ExtractionResult  │
│ (structured JSON) │
└──────────────────┘
```

### 3.2 Project Structure

```
tax-parser/
├── config/
│   └── settings.py                   # Pydantic-settings configuration
├── docs/
│   ├── AZURE_OPENAI_SETUP.md         # Azure deployment guide
│   └── DESIGN.md                     # This document
├── examples/
│   └── extract_sample.py             # CLI entry point
├── scripts/
│   └── check_deployment.py           # Azure deployment verification
├── src/tax_parser/
│   ├── __init__.py                   # Public API (exports TaxParserEngine)
│   ├── engine.py                     # Orchestration engine
│   ├── classifier.py                 # GPT-4o page classification
│   ├── preprocessor.py               # Image preprocessing pipeline
│   ├── extractors/
│   │   ├── base.py                   # BaseExtractor ABC
│   │   ├── azure_di_extractor.py     # Azure Document Intelligence
│   │   └── llm_extractor.py          # GPT-4o Vision extraction
│   ├── models/
│   │   └── result.py                 # ExtractionResult, FormType, FieldValue, etc.
│   ├── prompts/
│   │   └── extraction_prompts.py     # Per-form LLM prompt templates
│   ├── schemas/
│   │   ├── __init__.py               # Schema registry
│   │   ├── base.py                   # BaseTaxForm, Address, TaxpayerInfo
│   │   ├── form_1040.py              # Form 1040 schema
│   │   ├── form_1065.py              # Form 1065 schema
│   │   ├── form_1120.py              # Form 1120 schema
│   │   ├── form_1120s.py             # Form 1120-S schema
│   │   └── schedule_k1.py           # Schedule K-1 (Partnership & S-Corp)
│   └── validators/
│       └── tax_rules.py              # Cross-field validation engine
├── tests/
│   ├── conftest.py
│   ├── test_preprocessor.py
│   ├── test_schemas.py
│   └── test_validator.py
├── .env / .env.example               # Environment configuration
├── pyproject.toml                    # Build metadata + dependencies
└── requirements.txt                  # Pinned dependencies
```

---

## 4. Component Design

### 4.1 TaxParserEngine (`engine.py`)

The central orchestrator that owns the full document processing lifecycle. It is stateless beyond configuration — each `process_document()` call is self-contained.

**Public API:**

| Method | Description |
|---|---|
| `process_document(pdf_path, form_type_hint, skip_classification, skip_preprocessing)` | End-to-end single-document extraction. |
| `process_batch(pdf_paths, form_type_hint)` | Sequential multi-document extraction with per-document error isolation. |

**Convenience function:** `extract_tax_document()` — a one-liner wrapper that creates an engine, processes a document, and optionally writes the result to a JSON file.

**Internal components** (injected at init):

- `FormClassifier` — page-level form type identification
- `AzureDIExtractor` — prebuilt model extraction
- `LLMExtractor` — GPT-4o Vision extraction
- `TaxValidator` — domain-rule validation

**Review flagging logic** (`_should_flag_for_review`):

A document is flagged for human review when any of these conditions are true:
1. Any `ERROR`-severity review flag exists.
2. Overall confidence is below the configured threshold (default 0.85).
3. Any page has `"poor"` quality.
4. More than 3 `WARNING`-severity flags exist.

### 4.2 Preprocessor (`preprocessor.py`)

Handles PDF-to-image conversion and image quality improvement for scanned documents.

| Function | Purpose | Technique |
|---|---|---|
| `pdf_to_images()` | PDF → PIL images | `pdf2image` (poppler backend) at configurable DPI |
| `deskew_image()` | Correct page rotation | Canny edge detection → Hough line detection → median angle → affine rotation |
| `remove_watermark()` | Remove "Client Copy" etc. | HSV color masking (gray + red tones) → connected component filtering (area > 500px) → white fill |
| `enhance_image()` | Improve contrast/sharpness | CLAHE histogram equalization + `fastNlMeansDenoising` |
| `assess_quality()` | Rate page quality | Laplacian variance (blur), estimated DPI, skew detection, watermark pixel ratio → good/acceptable/poor |
| `preprocess_page()` | Full pipeline | assess → conditional deskew → conditional watermark removal → optional enhancement |

### 4.3 Form Classifier (`classifier.py`)

Uses Azure OpenAI GPT-4o Vision to identify the IRS form type from each scanned page image.

**Classification strategy:**
1. Each page is sent individually to GPT-4o with `detail: "low"` (sufficient for identifying form headers/numbers).
2. The model returns a JSON object: `{ form_type, confidence, page_description }`.
3. The primary document type is determined by confidence-weighted majority vote across all pages, excluding `UNKNOWN` classifications.

**Supported form types (16):** W-2, 1099-NEC, 1099-R, 1099-MISC, 1040, Schedules B/C/D/E/F, Schedule K-1 (Partnership), Schedule K-1 (S-Corp), 1065, 1120-S, 1120, Unknown.

**Edge case handling:** Sub-schedules of a larger form (e.g., Schedule K within Form 1120-S) are classified as the parent form type. Only standalone K-1s distributed to partners/shareholders are classified as Schedule K-1.

### 4.4 Extractors

Both extractors implement the `BaseExtractor` abstract interface:

```python
class BaseExtractor(ABC):
    def extract(self, form_type, page_images, pdf_bytes=None) -> ExtractionResult: ...
    def supported_forms(self) -> set[FormType]: ...
```

#### 4.4.1 AzureDIExtractor (`azure_di_extractor.py`)

Leverages Azure Document Intelligence prebuilt tax models for forms where Microsoft provides dedicated models.

| Form Type | Azure DI Model ID |
|---|---|
| W-2 | `prebuilt-tax.us.w2` |
| 1099-NEC | `prebuilt-tax.us.1099Nec` |
| 1099-R | `prebuilt-tax.us.1099R` |
| 1099-MISC | `prebuilt-tax.us.1099Misc` |
| 1040 | `prebuilt-tax.us.1040` |
| Schedule B | `prebuilt-tax.us.1040.scheduleB` |
| Schedule C | `prebuilt-tax.us.1040.scheduleC` |
| Schedule D | `prebuilt-tax.us.1040.scheduleD` |
| Schedule E | `prebuilt-tax.us.1040.scheduleE` |
| Schedule F | `prebuilt-tax.us.1040.scheduleF` |

**Behavior:**
- Prefers raw PDF bytes (preserves original quality); falls back to re-encoded PNG of the first page.
- Recursively extracts field values across all Azure DI field types (string, number, integer, date, currency, selectionMark, array, object).
- Fields with confidence below the threshold are tagged `needs_review: true` and generate a `WARNING` review flag.

#### 4.4.2 LLMExtractor (`llm_extractor.py`)

Uses GPT-4o Vision for complex multi-page business tax forms that lack Azure DI prebuilt support.

| Form Type | Dedicated Prompt |
|---|---|
| 1120-S | Multi-page extraction (income, deductions, Schedule B/K/L/M) |
| 1120 | Income, deductions, tax computation, Schedule C/J |
| 1065 | Partnership income, deductions, Schedule K/L |
| Schedule K-1 (Partnership) | Parts I–III (partnership info, partner info, current year items) |
| Schedule K-1 (S-Corp) | Parts I–III (corporation info, shareholder info, current year items) |

**Behavior:**
- All pages (up to `max_pages_per_call`, default 10) are sent in a single API call with `detail: "high"` for cross-page context.
- The prompt includes the full JSON schema generated from the Pydantic model, plus instructions for handling null fields, monetary formats, checkboxes, and dates.
- The model returns a structured JSON object plus a `field_confidence` map of dotted field paths to confidence scores.
- Response is recursively flattened into `FieldValue` objects with individual confidence tracking.

### 4.5 Schemas (`schemas/`)

Every supported tax form has a corresponding Pydantic model that defines its complete field structure. These models serve two purposes:

1. **LLM prompt generation** — The JSON schema is injected into the extraction prompt so the model knows exactly what structure to return.
2. **Output typing** — Provides a typed, validatable contract for downstream consumers.

**Hierarchy:**

```
BaseTaxForm
├── form_type: str
├── tax_year: str | None
├── taxpayer: TaxpayerInfo
│   ├── name, ein, ssn
│   └── address: Address (street, city, state, zip_code, country)
│
├── Form1040
├── Form1065
├── Form1120
├── Form1120S
├── ScheduleK1Partnership
└── ScheduleK1SCorp
```

The `SCHEMA_REGISTRY` in `schemas/__init__.py` maps `FormType` enums to their schema classes and provides `get_json_schema_for_form()` for runtime schema lookup.

### 4.6 Validator (`validators/tax_rules.py`)

Performs post-extraction domain validation to catch OCR/LLM errors through arithmetic consistency checks.

**Universal rules (all forms):**
- **EIN format** — Must match `XX-XXXXXXX` regex pattern.
- **Required header fields** — Taxpayer name must be present (ERROR if missing).

**Form-specific rules:**

| Form | Rule | Check |
|---|---|---|
| 1120-S | Line 1c | 1a − 1b (tolerance ±$1) |
| 1120-S | Line 3 (Gross Profit) | 1c − Line 2 |
| 1120-S | Line 6 (Total Income) | Line 3 + 4 + 5 |
| 1120-S | Line 21 (OBI) | Line 6 − Line 20 |
| 1120-S | Schedule K Line 1 vs Page 1 Line 21 | Must match (ERROR if difference > $1) |
| 1120-S | Schedule L balance sheet | Total assets = Total liabilities + equity (both periods) |
| 1120 | Line 3 (Gross Profit) | 1c − Line 2 |
| 1120 | Line 30 (Taxable Income) | Line 28 − 29a − 29b |
| 1065 | Line 22 (OBI) | Line 8 − Line 21 |

All arithmetic checks use a ±$1.00 tolerance to account for rounding.

### 4.7 Prompt Engineering (`prompts/extraction_prompts.py`)

The LLM extraction prompt is composed of three layers:

1. **Shared preamble** — Universal rules for JSON-only output, null handling, monetary format (no `$` or commas), checkbox conventions, date formats, watermark ignoring, and per-field confidence scoring.
2. **Form-specific instructions** — Describes the expected page layout and sections for each form type (e.g., "Page 1: Header + Income + Deductions" for 1120-S).
3. **JSON schema** — The full Pydantic-generated JSON schema is injected verbatim, plus a `field_confidence` addendum requesting dotted-path confidence maps.

---

## 5. Data Models

### 5.1 ExtractionResult

The top-level output returned by every extraction call.

| Field | Type | Description |
|---|---|---|
| `source_file` | `str` | Input PDF path |
| `total_pages` | `int` | Number of pages in the PDF |
| `form_type` | `FormType` | Primary classified form type |
| `extraction_method` | `str` | `"azure_di"` or `"llm"` |
| `structured_data` | `dict[str, Any]` | Complete parsed form data matching the Pydantic schema |
| `pages` | `list[PageResult]` | Per-page extraction details |
| `comparisons` | `list[ModelComparisonMetrics]` | Multi-model performance data |
| `review_flags` | `list[ReviewFlag]` | Validation issues and low-confidence warnings |
| `needs_human_review` | `bool` | Whether the document requires manual review |
| `overall_confidence` | `float` | Mean confidence across all extracted fields (0.0–1.0) |
| `processing_time_seconds` | `float` | Wall-clock processing time |

### 5.2 ModelComparisonMetrics [NEW]

| Field | Type | Description |
|---|---|---|
| `model_id` | `str` | Unique ID of the model (e.g., `gpt-4o`) |
| `model_name` | `str` | Display name for the UI |
| `confidence` | `float \| None` | Overall confidence score |
| `cost` | `float \| None` | Estimated USD cost of the run |
| `time` | `float \| None` | Processing time in seconds |
| `quality_score` | `float \| None` | 0-100 quality score (completeness + confidence) |
| `is_success` | `bool` | Whether the extraction succeeded |
| `error_message` | `str \| None` | Error details if failed |

### 5.3 PageResult

| Field | Type | Description |
|---|---|---|
| `page_number` | `int` | 1-indexed page number |
| `form_type` | `FormType` | Classified type for this specific page |
| `quality` | `QualityMetrics` | Image quality assessment |
| `fields` | `dict[str, FieldValue]` | Field-level extraction results |
| `raw_text` | `str \| None` | Raw OCR text (if available) |

### 5.3 FieldValue

| Field | Type | Description |
|---|---|---|
| `value` | `Any` | Extracted value |
| `confidence` | `float` | 0.0–1.0 confidence score |
| `source` | `str` | `"azure_di"`, `"llm"`, or `"manual"` |
| `bounding_box` | `list[float] \| None` | Normalized coordinates `[x0, y0, x1, y1]` |
| `needs_review` | `bool` | Whether this field was flagged |
| `review_reason` | `str \| None` | Reason for the flag |

### 5.4 ReviewFlag

| Field | Type | Description |
|---|---|---|
| `field_name` | `str \| None` | Dotted path of the flagged field |
| `page` | `int \| None` | Page number |
| `severity` | `ReviewSeverity` | `info`, `warning`, or `error` |
| `message` | `str` | Human-readable description |
| `auto_resolved` | `bool` | Whether the issue was auto-corrected |

---

## 6. Technology Stack

| Layer | Technology | Purpose |
|---|---|---|
| **Language** | Python 3.10+ | Core runtime |
| **Data modeling** | Pydantic v2 | Schema definitions, validation, JSON serialization |
| **Configuration** | pydantic-settings + python-dotenv | Type-safe settings from environment variables |
| **PDF handling** | pdf2image + poppler | PDF → image conversion |
| **Image processing** | OpenCV (headless) + NumPy + Pillow | Deskew, watermark removal, quality assessment |
| **AI — Document extraction** | Azure Document Intelligence SDK | Prebuilt tax form models (W-2, 1099, 1040, Schedules) |
| **AI — Vision classification & extraction** | Azure OpenAI SDK (GPT-4o Vision) | Page classification, complex form extraction |
| **Testing** | pytest + pytest-asyncio | Unit and integration tests |
| **Build** | setuptools + pyproject.toml | Package build and distribution |

### External Service Dependencies

| Service | Usage | Required Credentials |
|---|---|---|
| **Azure Document Intelligence** | Prebuilt tax document models | `AZURE_DI_ENDPOINT`, `AZURE_DI_KEY` |
| **Azure OpenAI** | GPT-4o Vision for classification + LLM extraction | `AZURE_OPENAI_ENDPOINT`, `AZURE_OPENAI_KEY`, `AZURE_OPENAI_DEPLOYMENT` |

### System Dependencies

- **poppler** — Required by `pdf2image` for PDF rendering (`brew install poppler` on macOS, `apt-get install poppler-utils` on Linux).

---

## 7. Configuration

All configuration is managed through environment variables (loaded from `.env` via `pydantic-settings`).

| Variable | Default | Description |
|---|---|---|
| `AZURE_DI_ENDPOINT` | — | Azure Document Intelligence endpoint URL |
| `AZURE_DI_KEY` | — | Azure Document Intelligence API key |
| `AZURE_OPENAI_ENDPOINT` | — | Azure OpenAI endpoint URL |
| `AZURE_OPENAI_KEY` | — | Azure OpenAI API key |
| `AZURE_OPENAI_DEPLOYMENT` | `gpt-4o` | Azure OpenAI model deployment name |
| `AZURE_OPENAI_API_VERSION` | `2024-12-01-preview` | Azure OpenAI API version |
| `CONFIDENCE_THRESHOLD` | `0.85` | Minimum confidence before flagging for review |
| `IMAGE_DPI` | `300` | DPI for PDF-to-image conversion |
| `MAX_PAGES_PER_CALL` | `10` | Max pages sent in a single LLM API call |
| `LOG_LEVEL` | `INFO` | Python logging level |

---

## 8. Extraction Routing

The engine routes each document to the optimal extractor based on its classified form type:

```
FormType ──► AZURE_DI_FORMS?  ──yes──► AzureDIExtractor (prebuilt model)
             │
             no
             │
             ▼
             LLM_EXTRACTION_FORMS?  ──yes──► LLMExtractor (GPT-4o Vision)
             │
             no
             │
             ▼
             LLMExtractor (fallback for UNKNOWN types)
```

| Routing Group | Form Types | Extractor |
|---|---|---|
| **Azure DI** | W-2, 1099-NEC, 1099-R, 1099-MISC, 1040, Schedules B/C/D/E/F | `AzureDIExtractor` |
| **LLM** | 1120-S, 1120, 1065, Schedule K-1 (Partnership), Schedule K-1 (S-Corp) | `LLMExtractor` |
| **Fallback** | Unknown / unrecognized | `LLMExtractor` |

---

## 9. Usage

### CLI

```bash
python examples/extract_sample.py <pdf_path> \
    [--form-type 1120-S] \
    [--output result.json] \
    [--skip-preprocess] \
    [--verbose]
```

### Programmatic — Single Document

```python
from tax_parser import TaxParserEngine

engine = TaxParserEngine()
result = engine.process_document("path/to/form.pdf")
print(result.structured_data)
```

### Programmatic — With Hints

```python
from tax_parser.engine import TaxParserEngine
from tax_parser.models.result import FormType

engine = TaxParserEngine()
result = engine.process_document(
    "path/to/1120s.pdf",
    form_type_hint=FormType.FORM_1120S,
    skip_classification=True,
)
```

### Programmatic — Batch

```python
from tax_parser import TaxParserEngine

engine = TaxParserEngine()
results = engine.process_batch(["doc1.pdf", "doc2.pdf", "doc3.pdf"])
```

### Convenience One-Liner

```python
from tax_parser.engine import extract_tax_document

result = extract_tax_document("form.pdf", output_json_path="result.json")
```

---

## 10. Testing

Tests are located in the `tests/` directory and use `pytest`.

| Test File | Coverage |
|---|---|
| `test_preprocessor.py` | PDF-to-image conversion, deskew, watermark removal, quality assessment |
| `test_schemas.py` | Pydantic schema validation, JSON schema generation, schema registry |
| `test_validator.py` | Arithmetic checks, EIN validation, balance sheet reconciliation |

Run tests:

```bash
pytest tests/ -v
```

---

## 11. Design Decisions

| Decision | Rationale |
|---|---|
| **Dual-extractor architecture** | Azure DI prebuilt models provide higher accuracy and field-level bounding boxes for supported forms; GPT-4o Vision covers the long tail of complex business forms. |
| **Per-page classification** | Multi-page PDFs often contain different form types (e.g., 1120-S + K-1s); per-page classification enables correct routing and future multi-form splitting. |
| **Pydantic schemas as prompt contracts** | Generating JSON schemas from Pydantic models ensures the LLM output structure matches the application's type system without manual synchronization. |
| **Confidence at two levels** | Field-level confidence (from Azure DI or LLM self-assessment) and document-level confidence (mean of fields) support both granular and aggregate quality decisions. |
| **$1.00 tolerance in arithmetic validation** | Scanned forms and OCR/LLM extraction may introduce minor rounding differences; a $1 tolerance avoids false positives while still catching real errors. |
| **Watermark removal before extraction** | "Client Copy" and similar watermarks can interfere with OCR and LLM interpretation; preprocessing removes them using color-space filtering. |
| **Low-detail images for classification, high-detail for extraction** | Classification only needs to read the form title/number (low tokens, fast); extraction needs to read every field value (high detail, more tokens). |
| **Sequential page classification** | Pages are classified one at a time to avoid token limits and allow per-page confidence tracking. A future optimization could batch classify with a single multi-image call. |

---

## 12. Limitations and Known Constraints

- **No async execution** — All Azure and OpenAI API calls are synchronous. Batch processing is sequential.
- **No PDF text layer extraction** — The engine always converts to images, even for PDFs with embedded text. This trades speed for consistency with truly scanned documents.
- **LLM confidence is self-reported** — GPT-4o's confidence estimates are heuristic, not calibrated probabilities. They should be treated as relative indicators, not absolute measures.
- **poppler dependency** — The `pdf2image` library requires poppler to be installed at the system level, which adds a deployment prerequisite.
- **Single-document classification** — If a PDF contains multiple distinct tax forms (e.g., a W-2 followed by a 1040), the engine classifies the entire document as a single form type via majority vote. Multi-form splitting is not yet implemented.

## 13. AI Model Comparison Table

The system provides a real-time comparison table...
