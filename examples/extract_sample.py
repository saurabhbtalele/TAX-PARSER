#!/usr/bin/env python3
"""Example: Extract data from a scanned tax form PDF.

Usage:
    python examples/extract_sample.py <pdf_path> [--form-type 1120-S] [--output result.json]

Requires:
    - Azure OpenAI credentials in .env or environment variables
    - Azure Document Intelligence credentials (for supported forms)
    - poppler installed (brew install poppler / apt-get install poppler-utils)
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

# Add src to path for direct execution
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

from tax_parser.engine import TaxParserEngine
from tax_parser.models.result import FormType


def main() -> None:
    parser = argparse.ArgumentParser(description="Extract data from a scanned tax form PDF")
    parser.add_argument("pdf_path", help="Path to the PDF file")
    parser.add_argument(
        "--form-type",
        choices=[ft.value for ft in FormType if ft != FormType.UNKNOWN],
        default=None,
        help="Hint: the form type (skips classification if provided)",
    )
    parser.add_argument(
        "--output", "-o",
        default=None,
        help="Output JSON file path (default: stdout)",
    )
    parser.add_argument(
        "--skip-preprocess",
        action="store_true",
        help="Skip image preprocessing (deskew, watermark removal)",
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose logging",
    )
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

    pdf_path = Path(args.pdf_path)
    if not pdf_path.exists():
        print(f"Error: File not found: {pdf_path}", file=sys.stderr)
        sys.exit(1)

    # Map form type string to enum
    form_type_hint = None
    if args.form_type:
        for ft in FormType:
            if ft.value == args.form_type:
                form_type_hint = ft
                break

    # Run extraction
    engine = TaxParserEngine()
    result = engine.process_document(
        pdf_path,
        form_type_hint=form_type_hint,
        skip_classification=form_type_hint is not None,
        skip_preprocessing=args.skip_preprocess,
    )

    # Output
    result_json = json.dumps(result.model_dump(), indent=2, default=str)

    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(result_json, encoding="utf-8")
        print(f"Result written to: {output_path}")
    else:
        print(result_json)

    # Summary
    print("\n" + "=" * 60, file=sys.stderr)
    print(f"Form Type:          {result.form_type.value}", file=sys.stderr)
    print(f"Pages:              {result.total_pages}", file=sys.stderr)
    print(f"Extraction Method:  {result.extraction_method}", file=sys.stderr)
    print(f"Overall Confidence: {result.overall_confidence:.2%}", file=sys.stderr)
    print(f"Human Review:       {'YES' if result.needs_human_review else 'No'}", file=sys.stderr)
    print(f"Review Flags:       {len(result.review_flags)}", file=sys.stderr)
    print(f"Processing Time:    {result.processing_time_seconds:.1f}s", file=sys.stderr)
    print("=" * 60, file=sys.stderr)

    if result.review_flags:
        print("\nReview Flags:", file=sys.stderr)
        for flag in result.review_flags:
            print(
                f"  [{flag.severity.value.upper()}] {flag.field_name or 'document'}: {flag.message}",
                file=sys.stderr,
            )


if __name__ == "__main__":
    main()
