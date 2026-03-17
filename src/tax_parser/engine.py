"""Main orchestration engine – ties together preprocessing, classification, extraction, and validation."""

from __future__ import annotations

import json
import logging
import time
from pathlib import Path
from typing import Any

from PIL import Image

from config.settings import Settings, get_settings
from tax_parser.classifier import FormClassifier
from tax_parser.extractors.azure_di_extractor import AzureDIExtractor
from tax_parser.extractors.llm_extractor import LLMExtractor
from tax_parser.extractors.factory import ExtractorFactory
from tax_parser.models.result import (
    AZURE_DI_FORMS,
    LLM_EXTRACTION_FORMS,
    ExtractionResult,
    FormType,
    ModelComparisonMetrics,
    ReviewFlag,
    ReviewSeverity,
)
from tax_parser.preprocessor import pdf_to_images, preprocess_page
from tax_parser.validators.tax_rules import TaxValidator

logger = logging.getLogger(__name__)


class TaxParserEngine:
    """End-to-end tax document parsing engine.

    Usage::

        engine = TaxParserEngine()
        result = engine.process_document("path/to/form.pdf")
        print(json.dumps(result.model_dump(), indent=2))
    """

    def __init__(self, settings: Settings | None = None) -> None:
        self._settings = settings or get_settings()
        self._debug_root = (
            Path(self._settings.debug_artifacts_dir).resolve()
            if self._settings.debug_artifacts_dir
            else None
        )

        self._classifier = FormClassifier(self._settings)
        self._azure_extractor = AzureDIExtractor(self._settings)
        self._llm_extractor = LLMExtractor(self._settings)
        self._validator = TaxValidator()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def process_document(
        self,
        pdf_path: str | Path,
        form_type_hint: FormType | None = None,
        skip_classification: bool = False,
        skip_preprocessing: bool = False,
    ) -> ExtractionResult:
        """Process a single tax document PDF end-to-end.

        Args:
            pdf_path: Path to the scanned PDF.
            form_type_hint: If known, skip classification and use this type.
            skip_classification: If True and form_type_hint is set, skip the classifier.
            skip_preprocessing: If True, skip deskew/watermark removal.

        Returns:
            ExtractionResult with structured data, confidence scores, and review flags.
        """
        start_time = time.time()
        pdf_path = Path(pdf_path)

        logger.info("=" * 60)
        logger.info("Processing: %s", pdf_path.name)
        logger.info("=" * 60)

        # Prepare per-run debug folder
        debug_dir: Path | None = None
        if self._debug_root:
            run_id = f"{pdf_path.stem}_{int(start_time)}"
            debug_dir = self._debug_root / run_id
            (debug_dir / "1_raw_images").mkdir(parents=True, exist_ok=True)
            (debug_dir / "2_processed_images").mkdir(parents=True, exist_ok=True)
            logger.info("Debug artifacts will be saved to: %s", debug_dir)

        # 1. Convert PDF to images
        raw_images = pdf_to_images(pdf_path, dpi=self._settings.image_dpi)
        total_pages = len(raw_images)

        if debug_dir:
            for i, img in enumerate(raw_images, start=1):
                out = debug_dir / "1_raw_images" / f"page_{i:03d}.png"
                img.save(out)
            logger.info("Saved %d raw page image(s) → %s", total_pages, debug_dir / "1_raw_images")

        # 2. Preprocess each page
        if skip_preprocessing:
            processed_images = raw_images
            quality_metrics = []
        else:
            processed_images = []
            quality_metrics = []
            for i, img in enumerate(raw_images):
                logger.info("Preprocessing page %d / %d", i + 1, total_pages)
                processed, quality = preprocess_page(img)
                processed_images.append(processed)
                quality_metrics.append(quality)

                if debug_dir:
                    out = debug_dir / "2_processed_images" / f"page_{i + 1:03d}.png"
                    processed.save(out)

            if debug_dir:
                logger.info("Saved %d processed page image(s) → %s", total_pages, debug_dir / "2_processed_images")

        # 3. Classify form type
        if form_type_hint and skip_classification:
            form_type = form_type_hint
            page_classifications = [(form_type, 1.0, "") for _ in processed_images]
        else:
            form_type, page_classifications = self._classifier.classify_document(
                processed_images
            )
            # Override with hint if classification is uncertain
            if form_type == FormType.UNKNOWN and form_type_hint:
                logger.warning(
                    "Classification returned UNKNOWN, using hint: %s",
                    form_type_hint.value,
                )
                form_type = form_type_hint

        logger.info("Form type: %s", form_type.value)

        # 4. Route to appropriate extractor
        pdf_bytes = pdf_path.read_bytes()
        result = self._route_extraction(form_type, processed_images, pdf_bytes, debug_dir=debug_dir)
        
        # Capture primary extraction time for comparison
        result.processing_time_seconds = round(time.time() - start_time, 2)

        # 5. Populate Comparisons
        self._run_comparisons(result, form_type, processed_images, pdf_bytes, debug_dir=debug_dir)

        # 6. Populate metadata
        result.source_file = str(pdf_path)
        result.total_pages = total_pages
        result.form_type = form_type

        # Attach quality metrics to page results
        for i, page_result in enumerate(result.pages):
            if i < len(quality_metrics):
                page_result.quality = quality_metrics[i]
            if i < len(page_classifications):
                page_result.form_type = page_classifications[i][0]

        # 7. Validate extracted data
        validation_flags = self._validator.validate(form_type, result.structured_data)
        result.review_flags.extend(validation_flags)

        # 8. Determine if human review is needed
        result.needs_human_review = self._should_flag_for_review(result)

        # 9. Timing
        result.processing_time_seconds = round(time.time() - start_time, 2)

        logger.info(
            "Extraction complete: confidence=%.2f, review_needed=%s, time=%.1fs",
            result.overall_confidence,
            result.needs_human_review,
            result.processing_time_seconds,
        )

        return result

    def process_batch(
        self,
        pdf_paths: list[str | Path],
        form_type_hint: FormType | None = None,
    ) -> list[ExtractionResult]:
        """Process multiple documents sequentially.

        For production use, consider running this with a task queue (Celery, etc.)
        for parallelism.
        """
        results: list[ExtractionResult] = []
        for i, path in enumerate(pdf_paths):
            logger.info("Batch: processing %d / %d", i + 1, len(pdf_paths))
            try:
                result = self.process_document(path, form_type_hint=form_type_hint)
                results.append(result)
            except Exception:
                logger.exception("Failed to process %s", path)
                results.append(
                    ExtractionResult(
                        source_file=str(path),
                        form_type=form_type_hint or FormType.UNKNOWN,
                        review_flags=[
                            ReviewFlag(
                                severity=ReviewSeverity.ERROR,
                                message=f"Processing failed for {path}",
                            )
                        ],
                        needs_human_review=True,
                    )
                )
        return results

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _route_extraction(
        self,
        form_type: FormType,
        page_images: list[Image.Image],
        pdf_bytes: bytes,
        debug_dir: Path | None = None,
    ) -> ExtractionResult:
        """Route to the correct extractor based on form type."""

        if form_type in AZURE_DI_FORMS:
            logger.info("Routing to Azure Document Intelligence")
            return self._azure_extractor.extract(form_type, page_images, pdf_bytes)

        elif form_type in LLM_EXTRACTION_FORMS:
            logger.info("Routing to LLM (GPT-4o) extractor")
            return self._llm_extractor.extract(form_type, page_images, debug_dir=debug_dir)

        else:
            # Unknown form – attempt LLM extraction as a best-effort fallback
            logger.warning(
                "Form type %s has no dedicated extractor, attempting LLM fallback",
                form_type.value,
            )
            return self._llm_extractor.extract(form_type, page_images, debug_dir=debug_dir)

    def _run_comparisons(
        self,
        primary_result: ExtractionResult,
        form_type: FormType,
        page_images: list[Image.Image],
        pdf_bytes: bytes,
        debug_dir: Path | None = None,
    ) -> None:
        """Run additional models for comparison and populate metrics."""
        
        # 1. Add primary model result as the first comparison
        primary_metrics = ModelComparisonMetrics(
            model_id=getattr(self._llm_extractor if primary_result.extraction_method == "llm" else self._azure_extractor, "model_id", "primary"),
            model_name="Primary (" + primary_result.extraction_method.upper() + ")",
            confidence=primary_result.overall_confidence,
            time=primary_result.processing_time_seconds,
            cost=self._estimate_cost(primary_result.extraction_method, len(page_images)),
            quality_score=self._calculate_quality_score(primary_result),
            is_success=True
        )
        primary_result.comparisons.append(primary_metrics)

        # 2. Identify other comparison models
        active_ids = self._settings.active_comparison_models
        for model_id in active_ids:
            # Skip if it's already the primary
            if model_id == primary_metrics.model_id:
                continue
                
            extractor = ExtractorFactory.get_extractor(model_id, self._settings)
            if not extractor or not extractor.is_available(self._settings):
                logger.info("Model %s not available for comparison (no key or not registered)", model_id)
                continue

            logger.info("Running comparison model: %s", model_id)
            comp_start = time.time()
            try:
                comp_result = extractor.extract(form_type, page_images, pdf_bytes, debug_dir=debug_dir)
                comp_time = round(time.time() - comp_start, 2)
                
                metrics = ModelComparisonMetrics(
                    model_id=model_id,
                    model_name=extractor.display_name,
                    confidence=comp_result.overall_confidence,
                    time=comp_time,
                    cost=self._estimate_cost(model_id, len(page_images)),
                    quality_score=self._calculate_quality_score(comp_result),
                    is_success=True
                )
                primary_result.comparisons.append(metrics)
            except Exception as e:
                logger.error("Comparison model %s failed: %s", model_id, e)
                primary_result.comparisons.append(ModelComparisonMetrics(
                    model_id=model_id,
                    model_name=extractor.display_name,
                    is_success=False,
                    error_message=str(e)
                ))

    def _estimate_cost(self, model_id: str, pages: int) -> float:
        """Rough USD cost estimate based on pages/model."""
        # Simple heuristic mapping
        pricing = {
            "gpt-4o": 0.01 * pages,        # $0.01 per page (vision + extraction)
            "gpt-4o-mini": 0.002 * pages,  # $0.002 per page
            "azure_di": 0.05 * pages,     # $0.05 per page
            "primary": 0.01 * pages
        }
        return round(pricing.get(model_id, 0.01 * pages), 4)

    def _calculate_quality_score(self, result: ExtractionResult) -> float:
        """
        Calculates a 0-100 quality score based on:
        1. Completeness (70%): Percentage of schema fields that returned a non-null value.
        2. Confidence (30%): Average field-level confidence returned by the AI.
        
        Formula: (Completeness * 0.7) + (AvgConfidence * 30)
        """
        if not result.structured_data:
            return 0.0
            
        # Count non-null fields recursively
        def count_fields(data: Any) -> tuple[int, int]:
            total = 0
            extracted = 0
            if isinstance(data, dict):
                for v in data.values():
                    t, e = count_fields(v)
                    total += t
                    extracted += e
            elif isinstance(data, list):
                # For lists, we just count the list as 1 field or sum elements?
                # Simplified: count each non-empty list as a success hit
                total += 1
                if data:
                    extracted += 1
            else:
                total = 1
                extracted = 1 if data is not None and data != "" else 0
            return total, extracted

        total, extracted = count_fields(result.structured_data)
        completeness = (extracted / total * 100) if total > 0 else 0
        
        # Combine completeness and confidence
        score = (completeness * 0.7) + (result.overall_confidence * 100 * 0.3)
        return round(score, 1)

    def _should_flag_for_review(self, result: ExtractionResult) -> bool:
        """Determine if the document needs human review."""

        # Any error-level flags
        if any(f.severity == ReviewSeverity.ERROR for f in result.review_flags):
            return True

        # Low overall confidence
        if result.overall_confidence < self._settings.confidence_threshold:
            return True

        # Poor quality pages
        for page in result.pages:
            if page.quality.overall_quality == "poor":
                return True

        # More than 3 warning-level flags
        warning_count = sum(1 for f in result.review_flags if f.severity == ReviewSeverity.WARNING)
        if warning_count > 3:
            return True

        return False


# ---------------------------------------------------------------------------
# Convenience function
# ---------------------------------------------------------------------------

def extract_tax_document(
    pdf_path: str | Path,
    form_type: FormType | None = None,
    output_json_path: str | Path | None = None,
) -> ExtractionResult:
    """One-liner convenience function.

    Args:
        pdf_path: Path to the PDF.
        form_type: Optional form type hint.
        output_json_path: If set, write the result JSON to this file.

    Returns:
        ExtractionResult
    """
    engine = TaxParserEngine()
    result = engine.process_document(pdf_path, form_type_hint=form_type)

    if output_json_path:
        output_path = Path(output_json_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(
            json.dumps(result.model_dump(), indent=2, default=str),
            encoding="utf-8",
        )
        logger.info("Wrote result JSON to %s", output_path)

    return result
