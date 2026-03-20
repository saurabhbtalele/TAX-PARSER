"""LLM-based extractor using Azure OpenAI GPT-4o Vision for custom forms."""

from __future__ import annotations

import json
import logging
import time
from pathlib import Path
from typing import Any, TYPE_CHECKING

from openai import AzureOpenAI
from PIL import Image

from tax_parser.extractors.base import BaseExtractor
from tax_parser.models.result import (
    LLM_EXTRACTION_FORMS,
    ExtractionResult,
    FieldValue,
    FormType,
    PageResult,
    ReviewFlag,
    ReviewSeverity,
)
from tax_parser.preprocessor import image_to_base64
from tax_parser.prompts.extraction_prompts import build_extraction_prompt
from tax_parser.schemas import get_json_schema_for_form

from tax_parser.extractors.factory import ExtractorFactory

if TYPE_CHECKING:
    from config.settings import Settings

logger = logging.getLogger(__name__)


class LLMExtractor(BaseExtractor):
    """Extract tax data from scanned forms using GPT-4o Vision."""

    def __init__(self, settings: Settings, deployment_override: str | None = None) -> None:
        self._client = AzureOpenAI(
            azure_endpoint=settings.azure_openai_endpoint,
            api_key=settings.azure_openai_key,
            api_version=settings.azure_openai_api_version,
        )
        self._deployment = deployment_override or settings.azure_openai_deployment
        self._confidence_threshold = settings.confidence_threshold
        self._max_pages = settings.max_pages_per_call

    @property
    def model_id(self) -> str:
        return "gpt-4o"

    @property
    def display_name(self) -> str:
        return "GPT-4o Vision"

    def is_available(self, settings: Settings) -> bool:
        return bool(settings.azure_openai_key and settings.azure_openai_endpoint)

    @property
    def supported_forms(self) -> set[FormType]:
        return LLM_EXTRACTION_FORMS

    def extract(
        self,
        form_type: FormType,
        page_images: list[Image.Image],
        pdf_bytes: bytes | None = None,
        debug_dir: Path | None = None,
    ) -> ExtractionResult:
        """Send page images to GPT-4o and parse the structured JSON response."""

        json_schema = get_json_schema_for_form(form_type)
        if json_schema is None:
            raise ValueError(f"No JSON schema defined for form type: {form_type.value}")

        prompt = build_extraction_prompt(form_type, json_schema)

        # Build the multi-image message content
        content: list[dict[str, Any]] = [{"type": "text", "text": prompt}]

        # Send all pages (up to max) in a single call for cross-page context
        pages_to_send = page_images[: self._max_pages]
        for i, img in enumerate(pages_to_send):
            b64 = image_to_base64(img, fmt="PNG")
            content.append(
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/png;base64,{b64}",
                        "detail": "high",
                    },
                }
            )

        # Save debug artifacts: prompt text, redacted request, and images sent to GPT
        if debug_dir:
            llm_debug = debug_dir / "3_llm_request"
            llm_debug.mkdir(parents=True, exist_ok=True)

            (llm_debug / "prompt.txt").write_text(prompt, encoding="utf-8")

            redacted_content = []
            for item in content:
                if item.get("type") == "image_url":
                    redacted_content.append({
                        "type": "image_url",
                        "image_url": {"detail": item["image_url"]["detail"], "url": "<base64 omitted>"},
                    })
                else:
                    redacted_content.append(item)
            (llm_debug / "request_payload.json").write_text(
                json.dumps({"model": self._deployment, "content": redacted_content}, indent=2),
                encoding="utf-8",
            )

            for i, img in enumerate(pages_to_send, start=1):
                img.save(llm_debug / f"page_sent_{i:03d}.png")

            logger.info(
                "Saved LLM debug artifacts → %s  (prompt.txt, request_payload.json, %d image(s))",
                llm_debug,
                len(pages_to_send),
            )

        logger.info(
            "Calling GPT-4o for %s extraction (%d pages)",
            form_type.value,
            len(pages_to_send),
        )

        response = self._client.chat.completions.create(
            model=self._deployment,
            messages=[{"role": "user", "content": content}],
            max_tokens=16384,
            temperature=0.0,
        )

        raw_response = response.choices[0].message.content or "{}"
        raw_response = raw_response.strip()

        if debug_dir:
            llm_debug = debug_dir / "3_llm_request"
            (llm_debug / "response_raw.txt").write_text(raw_response, encoding="utf-8")
            logger.info("Saved raw GPT response → %s", llm_debug / "response_raw.txt")

        # Strip markdown fences if present
        if raw_response.startswith("```"):
            raw_response = raw_response.split("\n", 1)[-1]
            if raw_response.endswith("```"):
                raw_response = raw_response[: raw_response.rfind("```")]
            raw_response = raw_response.strip()

        try:
            parsed = json.loads(raw_response)
        except json.JSONDecodeError:
            logger.error("Failed to parse LLM response as JSON:\n%s", raw_response[:500])
            return ExtractionResult(
                source_file="",
                total_pages=len(page_images),
                form_type=form_type,
                extraction_method="llm",
                review_flags=[
                    ReviewFlag(
                        severity=ReviewSeverity.ERROR,
                        message="LLM returned invalid JSON – manual extraction required",
                    )
                ],
                needs_human_review=True,
            )

        # Separate confidence map from structured data
        field_confidence: dict[str, float] = parsed.pop("field_confidence", {})
        structured_data = parsed

        # Build field-level results with confidence
        field_values: dict[str, FieldValue] = {}
        review_flags: list[ReviewFlag] = []

        self._flatten_fields(
            structured_data,
            prefix="",
            field_confidence=field_confidence,
            field_values=field_values,
            review_flags=review_flags,
        )

        # Build page results
        pages = [
            PageResult(
                page_number=i + 1,
                form_type=form_type,
                fields=field_values if i == 0 else {},
            )
            for i in range(len(page_images))
        ]

        # Overall confidence
        confidences = [fv.confidence for fv in field_values.values() if fv.value is not None]
        overall_confidence = sum(confidences) / len(confidences) if confidences else 0.0

        return ExtractionResult(
            source_file="",
            total_pages=len(page_images),
            form_type=form_type,
            extraction_method="llm",
            model_id=self.model_id,
            structured_data=structured_data,
            pages=pages,
            review_flags=review_flags,
            needs_human_review=len(review_flags) > 0,
            overall_confidence=round(overall_confidence, 3),
            metadata={
                "prompt": prompt,
                "raw_response": raw_response,
                "input_tokens": getattr(response.usage, "prompt_tokens", None),
                "output_tokens": getattr(response.usage, "completion_tokens", None),
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

            # Look up confidence for this field path
            conf = field_confidence.get(path, 0.8)  # Default to 0.8 if not specified
            needs_review = conf < self._confidence_threshold

            field_values[path] = FieldValue(
                value=value,
                confidence=conf,
                source="llm",
                needs_review=needs_review,
                review_reason=f"Low confidence ({conf:.2f})" if needs_review else None,
            )
            if needs_review and value is not None:
                review_flags.append(
                    ReviewFlag(
                        field_name=path,
                        severity=ReviewSeverity.WARNING,
                        message=f"LLM confidence {conf:.2f} below threshold {self._confidence_threshold}",
                    )
                )


class GPT4oMiniExtractor(LLMExtractor):
    """Lighter version of the LLM extractor using gpt-4o-mini."""

    def __init__(self, settings: Settings) -> None:
        super().__init__(settings, deployment_override=settings.openai_mini_deployment)

    @property
    def model_id(self) -> str:
        return "gpt-4o-mini"

    @property
    def display_name(self) -> str:
        return "GPT-4o Mini"


# Register extractors
ExtractorFactory.register("gpt-4o", LLMExtractor)
ExtractorFactory.register("gpt-4o-mini", GPT4oMiniExtractor)
