"""
Batch Runner for Tax Parser — Excel Workbook Output.
Processes all PDFs in a directory and saves structured results to a multi-sheet Excel file.
"""

import os
import json
import logging
import time
from pathlib import Path
from typing import Any, Dict, List

import pandas as pd
from PIL import Image

# Ensure the project root and src are in the path
import sys
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))
sys.path.append(str(project_root / "src"))

from tax_parser.engine import TaxParserEngine
from tax_parser.models.result import FormType, ExtractionResult

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("BatchRunnerExcel")

def flatten_dict(d: Dict[str, Any], prefix: str = "") -> Dict[str, Any]:
    """Recursively flatten a nested dictionary into dotted paths."""
    items = {}
    for k, v in d.items():
        new_key = f"{prefix}.{k}" if prefix else k
        if isinstance(v, dict):
            items.update(flatten_dict(v, new_key))
        elif isinstance(v, list):
            # For simplicity in Excel, join lists with commas
            items[new_key] = ", ".join(map(str, v)) if v else ""
        else:
            items[new_key] = v
    return items

def process_directory(
    input_dir: str, 
    output_excel: str, 
    strategies: List[str] = ["gemini", "azure", "openai4o"],
    form_type_hint: str = None
):
    """Process all PDFs and save to Excel."""
    input_path = Path(input_dir)
    if not input_path.exists():
        logger.error(f"Input directory does not exist: {input_dir}")
        return

    # Find all PDFs
    pdf_files = list(input_path.glob("**/*.pdf"))
    if not pdf_files:
        logger.warning(f"No PDF files found in {input_dir}")
        return

    logger.info(f"Found {len(pdf_files)} PDF files. Starting extraction...")
    
    engine = TaxParserEngine()
    
    # Store results grouped by FormType
    # { "1040": [row1, row2, ...], "W-2": [...] }
    all_results: Dict[str, List[Dict[str, Any]]] = {}

    for i, pdf_file in enumerate(pdf_files, start=1):
        logger.info(f"[{i}/{len(pdf_files)}] Processing: {pdf_file.name}")
        
        try:
            # Process the document
            # Note: We pass strategies as a list of strings
            result = engine.process_document(
                pdf_file, 
                form_type_hint=form_type_hint,
                extraction_strategy=strategies
            )
            
            form_str = result.form_type.value if hasattr(result.form_type, "value") else str(result.form_type)
            if form_str not in all_results:
                all_results[form_str] = []
            
            # Generate a row for EACH model comparison (Primary + Comparators)
            for comp in result.comparisons:
                row = {
                    "File Name": pdf_file.name,
                    "Model ID": comp.model_id,
                    "Model Name": comp.model_name,
                    "Is Primary": comp.model_id == result.model_id,
                    "Quality Score (0-100)": comp.quality_score,
                    "Fields Extracted": comp.fields_extracted,
                    "Fields Total": comp.fields_total,
                    "Input Tokens": comp.input_tokens,
                    "Output Tokens": comp.output_tokens,
                    "Cost (USD)": comp.cost,
                    "Cost Per Page": comp.cost_per_page,
                    "Time (s)": comp.time,
                    "Confidence Avg": comp.confidence,
                    "Is Success": comp.is_success,
                    "Error/Reason": comp.error_message if not comp.is_success else "",
                }
                
                # Detailed Field Data (flattened for this specific model)
                if comp.structured_data:
                    field_data = flatten_dict(comp.structured_data)
                    row.update(field_data)
                
                all_results[form_str].append(row)
            
        except Exception as e:
            logger.error(f"Failed to process {pdf_file.name}: {e}", exc_info=True)

    # Save to Excel
    logger.info(f"Generating Excel: {output_excel}")
    from openpyxl.utils import get_column_letter
    
    with pd.ExcelWriter(output_excel, engine="openpyxl") as writer:
        for form_type, rows in all_results.items():
            df = pd.DataFrame(rows)
            
            # Clean up sheet name (Excel limit 31 chars, no special chars)
            sheet_name = "".join(c for c in form_type if c.isalnum() or c in " -")[:31]
            if not sheet_name:
                sheet_name = "Unknown"
                
            df.to_excel(writer, sheet_name=sheet_name, index=False)
            
            # Auto-adjust column widths (with fallback to avoid crashes)
            try:
                worksheet = writer.sheets[sheet_name]
                for idx, col in enumerate(df.columns):
                    # Calculate max length of values in this column
                    # Convert all to string first to avoid len(float) errors
                    vals = [str(v) for v in df[col].values]
                    max_val_len = max([len(v) for v in vals]) if vals else 0
                    
                    # Compare with header length
                    max_len = max(float(max_val_len), len(str(col))) + 2
                    
                    # Get correct Excel column letter
                    col_letter = get_column_letter(idx + 1)
                    worksheet.column_dimensions[col_letter].width = min(max_len, 60)
            except Exception as style_err:
                logger.warning(f"Could not adjust column widths for {sheet_name}: {style_err}")

    logger.info("Batch processing complete! Workbook saved.")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Batch process PDFs into an Excel workbook.")
    parser.add_argument("--input", required=True, help="Directory containing PDFs")
    parser.add_argument("--output", default="batch_results.xlsx", help="Output Excel filename")
    parser.add_argument("--strategies", default="gemini,azure,openai4o", help="Comma-separated model IDs")
    parser.add_argument("--hint", help="Optional FormType hint (e.g., '1040', 'W-2')")
    
    args = parser.parse_args()
    
    strat_list = [s.strip() for s in args.strategies.split(",")]
    
    process_directory(args.input, args.output, strategies=strat_list, form_type_hint=args.hint)
