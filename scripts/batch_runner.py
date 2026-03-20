"""CLI Batch Runner — Process a folder of PDFs and output comparison CSV.

Usage:
    python -m scripts.batch_runner D:\\path\\to\\pdf_folder
    python -m scripts.batch_runner D:\\path\\to\\pdf_folder --output results.csv
    python -m scripts.batch_runner D:\\path\\to\\pdf_folder --form-type "1120-S"

The CSV will contain one row per (PDF × Model) with all comparison metrics.
"""

from __future__ import annotations

import argparse
import csv
import json
import logging
import sys
import time
from datetime import datetime
from pathlib import Path

# Ensure project root is on sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))
sys.path.insert(0, str(PROJECT_ROOT))

from config.settings import get_settings
from tax_parser.engine import TaxParserEngine
from tax_parser.models.result import ExtractionResult, FormType, ModelComparisonMetrics


# ── CSV column definitions ──────────────────────────────────────────
CSV_COLUMNS = [
    "file",
    "form_type",
    "total_pages",
    "model_id",
    "model_name",
    "is_primary",
    "confidence",
    "est_cost_usd",
    "cost_per_page",
    "time_seconds",
    "quality_score",
    "fields_extracted",
    "fields_total",
    "field_coverage_pct",
    "input_tokens",
    "output_tokens",
    "total_tokens",
    "review_flags",
    "is_success",
    "error_message",
    "extraction_method",
    "case_folder",
    "timestamp",
]


def _build_rows(
    pdf_name: str, result: ExtractionResult, case_folder: str
) -> list[dict]:
    """Convert ExtractionResult + comparisons into flat CSV rows."""
    rows = []
    ts = datetime.now().isoformat(timespec="seconds")

    for comp in result.comparisons:
        coverage = (
            round(comp.fields_extracted / comp.fields_total * 100, 1)
            if comp.fields_total > 0
            else 0.0
        )
        rows.append(
            {
                "file": pdf_name,
                "form_type": result.form_type.value,
                "total_pages": result.total_pages,
                "model_id": comp.model_id,
                "model_name": comp.model_name,
                "is_primary": comp.model_id == result.extraction_method,
                "confidence": round(comp.confidence * 100, 1),
                "est_cost_usd": comp.cost,
                "cost_per_page": comp.cost_per_page,
                "time_seconds": comp.time,
                "quality_score": comp.quality_score,
                "fields_extracted": comp.fields_extracted,
                "fields_total": comp.fields_total,
                "field_coverage_pct": coverage,
                "input_tokens": comp.input_tokens or 0,
                "output_tokens": comp.output_tokens or 0,
                "total_tokens": (comp.input_tokens or 0) + (comp.output_tokens or 0),
                "review_flags": comp.review_flags_count,
                "is_success": comp.is_success,
                "error_message": comp.error_message or "",
                "extraction_method": result.extraction_method,
                "case_folder": case_folder,
                "timestamp": ts,
            }
        )

    # If no comparisons at all, still log the primary result
    if not rows:
        rows.append(
            {
                "file": pdf_name,
                "form_type": result.form_type.value,
                "total_pages": result.total_pages,
                "model_id": result.extraction_method,
                "model_name": result.extraction_method,
                "is_primary": True,
                "confidence": round(result.overall_confidence * 100, 1),
                "est_cost_usd": 0.0,
                "cost_per_page": 0.0,
                "time_seconds": result.processing_time_seconds,
                "quality_score": 0.0,
                "fields_extracted": 0,
                "fields_total": 0,
                "field_coverage_pct": 0.0,
                "input_tokens": 0,
                "output_tokens": 0,
                "total_tokens": 0,
                "review_flags": len(result.review_flags),
                "is_success": True,
                "error_message": "",
                "extraction_method": result.extraction_method,
                "case_folder": "",
                "timestamp": datetime.now().isoformat(timespec="seconds"),
            }
        )

    return rows


def _find_case_folder(result: ExtractionResult) -> str:
    """Try to get the case folder path from the result metadata."""
    # The engine stores the case_folder_path if available
    settings = get_settings()
    case_dir = Path(settings.case_output_dir)
    if case_dir.exists():
        # Get the most recent subfolder
        subdirs = sorted(case_dir.iterdir(), key=lambda p: p.stat().st_mtime, reverse=True)
        if subdirs:
            return str(subdirs[0])
    return ""


def run_batch(
    pdf_input: Path,
    output_csv: Path,
    form_type_hint: FormType | None = None,
) -> None:
    """Process PDF(s) from a directory or a single file and write comparison CSV."""

    if pdf_input.is_file():
        if pdf_input.suffix.lower() == ".pdf":
            pdfs = [pdf_input]
        else:
            print(f"❌ File is not a PDF: {pdf_input}")
            sys.exit(1)
    else:
        pdfs = sorted(pdf_input.glob("*.pdf"))

    if not pdfs:
        print(f"❌ No PDF files found for: {pdf_input}")
        sys.exit(1)

    print(f"\n{'='*60}")
    print(f"  TAX-PARSER Batch Runner")
    print(f"{'='*60}")
    print(f"  📁 Input folder : {pdf_input}")
    print(f"  📄 PDFs found   : {len(pdfs)}")
    print(f"  💾 Output CSV   : {output_csv}")
    if form_type_hint:
        print(f"  📋 Form type    : {form_type_hint.value}")
    else:
        print(f"  📋 Form type    : Auto-detect")
    print(f"{'='*60}\n")

    engine = TaxParserEngine()
    all_rows: list[dict] = []
    total_start = time.time()

    for i, pdf_path in enumerate(pdfs, 1):
        print(f"[{i}/{len(pdfs)}] Processing: {pdf_path.name} ... ", end="", flush=True)
        file_start = time.time()

        try:
            result = engine.process_document(
                pdf_path=pdf_path,
                form_type_hint=form_type_hint,
                skip_classification=bool(form_type_hint),
            )

            case_folder = _find_case_folder(result)
            rows = _build_rows(pdf_path.name, result, case_folder)
            all_rows.extend(rows)

            elapsed = round(time.time() - file_start, 1)
            models_ok = sum(1 for r in rows if r["is_success"])
            models_fail = sum(1 for r in rows if not r["is_success"])
            print(
                f"✅ {result.form_type.value} | "
                f"{models_ok} models OK, {models_fail} failed | "
                f"{elapsed}s"
            )

        except Exception as e:
            elapsed = round(time.time() - file_start, 1)
            print(f"❌ Error: {e} ({elapsed}s)")
            all_rows.append(
                {
                    "file": pdf_path.name,
                    "form_type": "ERROR",
                    "total_pages": 0,
                    "model_id": "N/A",
                    "model_name": "N/A",
                    "is_primary": False,
                    "confidence": 0,
                    "est_cost_usd": 0,
                    "cost_per_page": 0,
                    "time_seconds": elapsed,
                    "quality_score": 0,
                    "fields_extracted": 0,
                    "fields_total": 0,
                    "field_coverage_pct": 0,
                    "input_tokens": 0,
                    "output_tokens": 0,
                    "total_tokens": 0,
                    "review_flags": 0,
                    "is_success": False,
                    "error_message": str(e),
                    "extraction_method": "N/A",
                    "case_folder": "",
                    "timestamp": datetime.now().isoformat(timespec="seconds"),
                }
            )

    # ── Write CSV ──────────────────────────────────────────────────
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    with open(output_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_COLUMNS)
        writer.writeheader()
        writer.writerows(all_rows)

    total_elapsed = round(time.time() - total_start, 1)
    total_models = len(all_rows)
    successes = sum(1 for r in all_rows if r["is_success"])

    print(f"\n{'='*60}")
    print(f"  ✅ BATCH COMPLETE")
    print(f"{'='*60}")
    print(f"  📄 Files processed : {len(pdfs)}")
    print(f"  🤖 Model runs      : {total_models} ({successes} OK)")
    print(f"  ⏱️  Total time      : {total_elapsed}s")
    print(f"  💾 CSV saved to    : {output_csv}")
    print(f"{'='*60}\n")


def _parse_form_type(value: str) -> FormType | None:
    """Safely parse a form type string to FormType enum."""
    if not value or value.lower() == "auto":
        return None
    for ft in FormType:
        if ft.value.lower() == value.lower():
            return ft
    print(f"⚠️  Unknown form type '{value}', using auto-detect")
    return None


def main():
    parser = argparse.ArgumentParser(
        description="Batch process PDFs and output comparison CSV",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m scripts.batch_runner D:\\TAX\\tax_returns_business
  python -m scripts.batch_runner D:\\TAX\\pdfs --output my_results.csv
  python -m scripts.batch_runner D:\\TAX\\pdfs --form-type "1120-S"
        """,
    )
    parser.add_argument(
        "pdf_dir",
        type=Path,
        help="Directory containing PDF files to process",
    )
    parser.add_argument(
        "--output", "-o",
        type=Path,
        default=None,
        help="Output CSV path (default: output/batch_results_{timestamp}.csv)",
    )
    parser.add_argument(
        "--form-type", "-f",
        type=str,
        default="auto",
        help="Form type hint (e.g., '1120-S', '1065', 'auto')",
    )
    parser.add_argument(
        "--log-level",
        type=str,
        default="WARNING",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Logging level (default: WARNING for clean output)",
    )

    args = parser.parse_args()

    # Configure logging
    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format="%(levelname)s - %(name)s - %(message)s",
    )

    # Validate input dir
    if not args.pdf_dir.exists():
        print(f"❌ Directory not found: {args.pdf_dir}")
        sys.exit(1)

    # Set output path
    if args.output is None:
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        args.output = Path("output") / f"batch_results_{ts}.csv"

    form_type = _parse_form_type(args.form_type)

    run_batch(
        pdf_input=args.pdf_dir,
        output_csv=args.output,
        form_type_hint=form_type,
    )


if __name__ == "__main__":
    main()
