# 📑 Tax Parser Engine & Comparison Suite

A high-performance processing pipeline for extracting structured data from scanned US tax forms. Built for the **Mortgage Industry** with native support for multi-model comparison (Azure DI vs OpenAI vs Gemini) and pipeline audit trails.

---

## 🚀 Key Features

### 1. Multi-Model Comparison
Compare performance across multiple AI models for every document:
- **Azure Document Intelligence** (Fast, precise for standard forms)
- **OpenAI GPT-4o / Mini** (High reasoning, great for complex schedules)
- **Google Gemini 2.0 Flash** (Vision-native, extremely cost-effective)

### 2. CLI Batch Runner
Process entire directories of PDFs and generate a comprehensive comparison CSV:
```powershell
# Run on a folder and save results to CSV
python -m scripts.batch_runner tax_returns_business/ -o output/results.csv
```

### 3. Required-Fields Quality Scoring
A 0–100 quality metric based on business-critical fields:
- **K-1 Partnership**: 39 mandatory fields (Part II ownership, Section L capital account, Part III income).
- **K-1 S-Corp**: 21 mandatory fields.
- **Form 1120-S**: 23 mandatory fields.
- *Quality = (Extracted Required Fields / Total Required Fields) × 100*

### 4. Case Folder Pipeline (Audit Trail)
Every run creates a structured audit folder under `output/cases/`:
- `01_input/`: Original PDF.
- `02_preprocessed/`: Cleaned page images + quality metadata.
- `03_classification/`: Auto-detection results.
- `04_extraction/`: Full JSON outputs for **every model** (GPT, Gemini, Azure).
- `05_validation/`: Review flags and rule violations.

---

## 🛠️ Setup

### 1. Prerequisites
- Python 3.10+
- [Poppler](https://github.com/oschwartz10612/poppler-windows/releases) (add to PATH)

### 2. Installation
```powershell
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Configuration
Copy `.env.example` to `.env` and configure your keys:
```env
AZURE_OPENAI_KEY=...
AZURE_DI_KEY=...
GEMINI_API_KEY=...
```

---

## 📂 Usage

### 🖥️ Web UI (Comparison Dashboard)
Start the server and access the interactive dashboard to see "Winner" badges and expandable model details.
```powershell
.\run_server.bat
# Visit: http://localhost:8000
```

### ⌨️ CLI Batch Runner
Process a folder of tax returns and get an Excel-ready CSV:
```powershell
# Basic usage
python -m scripts.batch_runner path/to/pdfs

# Force specific form type (e.g. for mortgage underwriting)
python -m scripts.batch_runner path/to/pdfs -f "Schedule K-1 (Partnership)"

# Custom output file
python -m scripts.batch_runner path/to/pdfs -o comparison_report.csv
```

### ⌨️ Single File Processing
```powershell
.\run.bat path/to/file.pdf --form-type "1120-S"
```

---

## 🏗️ Project Structure
- `src/tax_parser/`
  - `engine.py`: Pipeline orchestrator.
  - `quality/`: Required-fields registry and scoring logic.
  - `extractors/`: Multi-model implementations (Azure, OpenAI, Gemini).
  - `schemas/`: Pydantic models for IRS forms.
- `scripts/batch_runner.py`: CLI for folder processing.
- `output/cases/`: Per-extraction pipeline artifacts.

---

## 📊 Understanding Metrics

### 1. Confidence (AI Self-Reported)
- **Definition**: The average probability assigned by the AI model across all extracted fields.
- **Scale**: 0% to 100%.
- **Use Case**: Used to flag low-confidence extractions for manual review. High confidence does not always guarantee accuracy, which is why we use **Quality** as a secondary check.

### 2. Quality (Business Accuracy)
- **Definition**: A weighted balance between **Model Recognition** (finding the key) and **Extraction Coverage** (pulling the value).
- **Formula**: `Quality = (Recognition % * 0.5) + (Coverage % * 0.5)`
- **Why**: In tax parsing, just "finding" where a box should be is a huge success for an AI. If the AI finds the key but the value is empty on the form, we give full credit for **Recognition** but 0 for **Coverage**.

**Scoring Breakdown for Mortgage Underwriting:**
1. **Model Recognition (50%)**: Did the AI emit all required keys? (Verifies AI understands the form layout).
2. **Extraction Coverage (50%)**: Are those fields populated with non-zero data? (Verifies document completeness).

**Step-by-step example for Schedule K-1 (Partnership):**

> Suppose GPT-4o processes a K-1 PDF. The engine checks every field in the 39-field checklist:

| # | IRS Label | Field Path | Found? |
|---|---|---|---|
| 1 | Box A – Partnership EIN | `entity.ein` | ✅ |
| 2 | Box B – Partnership Name | `entity.name` | ✅ |
| 3 | Box B – Street Address | `entity.address.street` | ✅ |
| 4 | Box B – City | `entity.address.city` | ✅ |
| 5 | Box B – State | `entity.address.state` | ✅ |
| 6 | Box B – ZIP | `entity.address.zip` | ✅ |
| 7 | Box C – IRS Service Center | `entity.irs_center` | ❌ (missing) |
| 8 | Box D – PTP Flag | `entity.publicly_traded_partnership` | ✅ |
| 9 | Box E – Partner SSN/ITIN | `partner.ssn_or_ein` | ✅ |
| 10 | Box F – Partner Name | `partner.name` | ✅ |
| 11 | Box F – Street | `partner.address.street` | ✅ |
| 12 | Box F – City | `partner.address.city` | ✅ |
| 13 | Box F – State | `partner.address.state` | ✅ |
| 14 | Box F – ZIP | `partner.address.zip` | ❌ (missing) |
| 15 | Box G – General Partner? | `partner.is_general_partner` | ✅ |
| 16 | Box H – Domestic? | `partner.is_domestic_partner` | ✅ |
| 17 | Box I1 – Entity Type | `partner.partner_type` | ✅ |
| 18 | Box J – Profit % Beginning | `partner.profit_sharing_beginning` | ✅ |
| 19 | Box J – Profit % Ending | `partner.profit_sharing_ending` | ✅ |
| 20 | Box J – Loss % Beginning | `partner.loss_sharing_beginning` | ✅ |
| 21 | Box J – Loss % Ending | `partner.loss_sharing_ending` | ✅ |
| 22 | Box J – Capital % Beginning | `partner.capital_sharing_beginning` | ✅ |
| 23 | Box J – Capital % Ending | `partner.capital_sharing_ending` | ✅ |
| 24 | Box K – Nonrecourse Liability | `partner.nonrecourse_liability_ending` | ✅ |
| 25 | Box K – Qualified Nonrecourse | `partner.qualified_nonrecourse_liability_ending` | ❌ (missing) |
| 26 | Box K – Recourse Liability | `partner.recourse_liability_ending` | ✅ |
| 27 | Section L – Beginning Capital | `capital_account.beginning_capital_account` | ✅ |
| 28 | Section L – Capital Contributed | `capital_account.capital_contributed` | ✅ |
| 29 | Section L – Net Income/Loss | `capital_account.current_year_net_income_loss` | ✅ |
| 30 | Section L – Other Changes | `capital_account.other_increase_decrease` | ✅ |
| 31 | Section L – Withdrawals | `capital_account.withdrawals_distributions` | ✅ |
| 32 | Section L – Ending Capital | `capital_account.ending_capital_account` | ✅ |
| 33 | Line 1 – Ordinary Income | `income_deductions.line_1_ordinary_business_income` | ✅ |
| 34 | Line 2 – Net Rental RE | `income_deductions.line_2_net_rental_real_estate` | ✅ |
| 35 | Line 4c – Guaranteed Payments | `income_deductions.line_4c_total_guaranteed_payments` | ✅ |
| 36 | Line 5 – Interest Income | `income_deductions.line_5_interest_income` | ✅ |
| 37 | Line 6a – Ordinary Dividends | `income_deductions.line_6a_ordinary_dividends` | ✅ |
| 38 | Line 19 – Distributions | `income_deductions.line_19_distributions` | ✅ |
| 39 | Line 15 – SE Earnings | `self_employment.line_15_net_earnings` | ✅ |

> **Result**: 36 found / 39 required → **Quality = (36/39) × 100 = 92.3%**

The three missing fields (IRS Center, ZIP code, Qualified Nonrecourse) would flag this extraction for review.

> 💡 **To customise**: Edit [`src/tax_parser/quality/required_fields/schedule_k1_partnership.py`](src/tax_parser/quality/required_fields/schedule_k1_partnership.py) and add or remove field paths. The score recalculates automatically.



### 3. Estimated Cost (USD)
Costs are estimated based on **page count** and the current pricing tier for each model API.
| Model | Cost per Page | Notes |
|---|---|---|
| **Azure DI** | **$0.05** | Standard Azure Document Intelligence rate. |
| **GPT-4o** | **$0.01** | High reasoning, vision-enabled. |
| **GPT-4o Mini** | **$0.002** | Optimized for speed and cost. |
| **Gemini 2.0 Flash** | **$0.005** | Vision-native, high-performance bargain. |

---

## ⚖️ License
MIT
