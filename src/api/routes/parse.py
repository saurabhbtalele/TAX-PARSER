import os
import tempfile
import logging
from pathlib import Path
from typing import Optional, List

from fastapi import APIRouter, File, UploadFile, Form, HTTPException
from fastapi.responses import JSONResponse

from tax_parser.engine import TaxParserEngine
from tax_parser.models.result import FormType

logger = logging.getLogger(__name__)

router = APIRouter()
engine = TaxParserEngine()

@router.post("/parse")
async def parse_document(
    file: UploadFile = File(...),
    form_type: Optional[str] = Form(None),
    extraction_strategy: Optional[List[str]] = Form(None),
    skip_preprocessing: Optional[str] = Form("false")
):
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    tmp_path = None
    try:
        # Save to temporary file
        fd, tmp_filename = tempfile.mkstemp(suffix=".pdf")
        tmp_path = Path(tmp_filename)
        with os.fdopen(fd, 'wb') as f:
            f.write(await file.read())
        
        # Determine FormType — resilient: wrong type falls back to auto-detect
        form_type_hint = None
        skip_classification = False
        if form_type and form_type.strip():
            form_type_val = form_type.strip()
            for ft in FormType:
                if ft.value == form_type_val:
                    form_type_hint = ft
                    break
            if form_type_hint is None:
                logger.warning(
                    "User provided form type '%s' does not match any known FormType. "
                    "Falling back to auto-detect.",
                    form_type_val,
                )
            else:
                skip_classification = True

        # Process document
        result = engine.process_document(
            tmp_path,
            form_type_hint=form_type_hint,
            skip_classification=skip_classification,
            extraction_strategy=extraction_strategy,
            skip_preprocessing=skip_preprocessing.lower() == "true",
        )
        
        return JSONResponse(content=result.model_dump(mode='json'))
        
    except Exception as e:
        logger.error(f"Error processing document: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if tmp_path and tmp_path.exists():
            try:
                os.remove(tmp_path)
            except Exception as cleanup_err:
                logger.warning(f"Failed to cleanup temp file {tmp_path}: {cleanup_err}")
