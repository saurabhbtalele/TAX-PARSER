"""Google Gemini Vision extractor for tax forms."""

from __future__ import annotations

import json
import logging
import io
from pathlib import Path
from typing import Any, TYPE_CHECKING

from PIL import Image
import google.genai as genai
from google.genai import types

import google.genai as genai
from google.genai import types

from tax_parser.extractors.base import BaseExtractor
from tax_parser.extractors.factory import ExtractorFactory
from tax_parser.models.result import (
    LLM_EXTRACTION_FORMS,
    AZURE_DI_FORMS,
    ExtractionResult,
    FieldValue,
    FormType,
    PageResult,
    ReviewFlag,
    ReviewSeverity,
)
from tax_parser.prompts.extraction_prompts import build_extraction_prompt
from tax_parser.schemas import get_json_schema_for_form

if TYPE_CHECKING:
    from config.settings import Settings

logger = logging.getLogger(__name__)


class GeminiExtractor(BaseExtractor):
    """Extract tax data using Google Gemini Vision (New SDK)."""

    def __init__(self, settings: Settings) -> None:
        self._api_key = settings.gemini_api_key or ""
        self._client = None
        if self._api_key:
            self._client = genai.Client(api_key=self._api_key)
        
        self._model_name = settings.gemini_model_name
        self._confidence_threshold = settings.confidence_threshold
        self._max_pages = settings.max_pages_per_call

    @property
    def model_id(self) -> str:
        return "gemini-2.0-flash"

    @property
    def display_name(self) -> str:
        return "Google Gemini 2.0 Flash"

    def is_available(self, settings: Settings) -> bool:
        return bool(settings.gemini_api_key)

    @property
    def supported_forms(self) -> set[FormType]:
        return LLM_EXTRACTION_FORMS | AZURE_DI_FORMS

    def extract(
        self,
        form_type: FormType,
        page_images: list[Image.Image],
        pdf_bytes: bytes | None = None,
        debug_dir: Path | None = None,
    ) -> ExtractionResult:
        """Send page images to Gemini and parse the structured JSON response."""

        json_schema = get_json_schema_for_form(form_type)
        if json_schema is None:
            raise ValueError(f"No JSON schema defined for form type: {form_type.value}")

        prompt = build_extraction_prompt(form_type, json_schema)

        # Build image parts for Gemini
        pages_to_send = page_images[: self._max_pages]
        contents = [prompt]
        
        for img in pages_to_send:
            buf = io.BytesIO()
            img.save(buf, format="PNG")
            buf.seek(0)
            contents.append(
                types.Part.from_bytes(
                    data=buf.getvalue(), 
                    mime_type="image/png"
                )
            )

        # Save debug artifacts
        if debug_dir:
            gemini_debug = debug_dir / "3_gemini_request"
            gemini_debug.mkdir(parents=True, exist_ok=True)
            (gemini_debug / "prompt.txt").write_text(prompt, encoding="utf-8")
            for i, img in enumerate(pages_to_send, start=1):
                img.save(gemini_debug / f"page_sent_{i:03d}.png")

        logger.info(
            "Calling Gemini (New SDK) for %s extraction (%d pages)",
            form_type.value,
            len(pages_to_send),
        )

        if not self._client:
            raise ValueError("Gemini API Client not initialized. Check API key.")

        response = self._client.models.generate_content(
            model=self._model_name,
            contents=contents
        )

        raw_response = response.text or "{}"
        raw_response = raw_response.strip()

        if debug_dir:
            gemini_debug = debug_dir / "3_gemini_request"
            (gemini_debug / "response_raw.txt").write_text(raw_response, encoding="utf-8")

        # Strip markdown fences if present
        if raw_response.startswith("```"):
            raw_response = raw_response.split("\n", 1)[-1]
            if raw_response.endswith("```"):
                raw_response = raw_response[: raw_response.rfind("```")]
            raw_response = raw_response.strip()

        try:
            parsed = json.loads(raw_response)
        except json.JSONDecodeError:
            logger.error("Failed to parse Gemini response as JSON:\n%s", raw_response[:500])
            return ExtractionResult(
                source_file="",
                total_pages=len(page_images),
                form_type=form_type,
                extraction_method="gemini",
                review_flags=[
                    ReviewFlag(
                        severity=ReviewSeverity.ERROR,
                        message="Gemini returned invalid JSON - manual extraction required",
                    )
                ],
                needs_human_review=True,
            )

        # Separate confidence map
        field_confidence: dict[str, float] = parsed.pop("field_confidence", {})
        structured_data = parsed

        # Build field-level results
        field_values: dict[str, FieldValue] = {}
        review_flags: list[ReviewFlag] = []

        self._flatten_fields(
            structured_data, "", field_confidence, field_values, review_flags
        )

        pages = [
            PageResult(
                page_number=i + 1,
                form_type=form_type,
                fields=field_values if i == 0 else {},
            )
            for i in range(len(page_images))
        ]

        confidences = [fv.confidence for fv in field_values.values() if fv.value is not None]
        overall_confidence = sum(confidences) / len(confidences) if confidences else 0.0

        # Extract token usage
        input_tokens = None
        output_tokens = None
        if hasattr(response, 'usage_metadata') and response.usage_metadata:
            input_tokens = getattr(response.usage_metadata, 'prompt_token_count', None)
            output_tokens = getattr(response.usage_metadata, 'candidates_token_count', None)

        return ExtractionResult(
            source_file="",
            total_pages=len(page_images),
            form_type=form_type,
            extraction_method="gemini",
            structured_data=structured_data,
            pages=pages,
            review_flags=review_flags,
            needs_human_review=len(review_flags) > 0,
            overall_confidence=round(overall_confidence, 3),
            metadata={
                "prompt": prompt,
                "raw_response": raw_response,
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
            }
        )

    def _flatten_fields(
        self,
        data: dict[str, Any],
        prefix: str,
        field_confidence: dict[str, float],
        field_values: dict[str, FieldValue],
        review_flags: list[ReviewFlag],
    ) -> None:
        """Recursively flatten nested data into field_values with confidence."""
        for key, value in data.items():
            path = f"{prefix}.{key}" if prefix else key

            if isinstance(value, dict):
                self._flatten_fields(value, path, field_confidence, field_values, review_flags)
                continue

            conf = field_confidence.get(path, 0.75)
            needs_review = conf < self._confidence_threshold

            field_values[path] = FieldValue(
                value=value,
                confidence=conf,
                source="gemini",
                needs_review=needs_review,
                review_reason=f"Low confidence ({conf:.2f})" if needs_review else None,
            )

            if needs_review and value is not None:
                review_flags.append(
                    ReviewFlag(
                        field_name=path,
                        severity=ReviewSeverity.WARNING,
                        message=f"Gemini confidence {conf:.2f} below threshold {self._confidence_threshold}",
                    )
                )


# Register extractor
ExtractorFactory.register("gemini-2.0-flash", GeminiExtractor)
