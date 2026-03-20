"""Azure Document Intelligence extractor for forms with prebuilt models."""

from __future__ import annotations

import logging
from typing import Any, TYPE_CHECKING

from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.ai.documentintelligence.models import AnalyzeDocumentRequest
from azure.core.credentials import AzureKeyCredential
from PIL import Image

from tax_parser.extractors.base import BaseExtractor
from tax_parser.extractors.factory import ExtractorFactory
from tax_parser.models.result import (
    AZURE_DI_FORMS,
    ExtractionResult,
    FieldValue,
    FormType,
    PageResult,
    ReviewFlag,
    ReviewSeverity,
)
from tax_parser.preprocessor import image_to_bytes
import io

if TYPE_CHECKING:
    from config.settings import Settings

logger = logging.getLogger(__name__)

# Maps our FormType enum to the Azure DI prebuilt model ID.
# See: https://learn.microsoft.com/en-us/azure/ai-services/document-intelligence/concept-tax-document
AZURE_MODEL_MAP: dict[FormType, str] = {
    FormType.W2: "prebuilt-tax.us.w2",
    FormType.FORM_1099_NEC: "prebuilt-tax.us.1099Nec",
    FormType.FORM_1099_R: "prebuilt-tax.us.1099R",
    FormType.FORM_1099_MISC: "prebuilt-tax.us.1099Misc",
    FormType.FORM_1040: "prebuilt-tax.us.1040",
    FormType.SCHEDULE_B: "prebuilt-tax.us.1040.scheduleB",
    FormType.SCHEDULE_C: "prebuilt-tax.us.1040.scheduleC",
    FormType.SCHEDULE_D: "prebuilt-tax.us.1040.scheduleD",
    FormType.SCHEDULE_E: "prebuilt-tax.us.1040.scheduleE",
    FormType.SCHEDULE_F: "prebuilt-tax.us.1040.scheduleF",
}


class AzureDIExtractor(BaseExtractor):
    """Extract tax data using Azure Document Intelligence prebuilt models."""

    def __init__(self, settings: Settings) -> None:
        self._client = DocumentIntelligenceClient(
            endpoint=settings.azure_di_endpoint,
            credential=AzureKeyCredential(settings.azure_di_key),
        )
        self._confidence_threshold = settings.confidence_threshold

    @property
    def model_id(self) -> str:
        return "azure_di"

    @property
    def display_name(self) -> str:
        return "Azure Document Intelligence"

    def is_available(self, settings: Settings) -> bool:
        return bool(settings.azure_di_key and settings.azure_di_endpoint)

    @property
    def supported_forms(self) -> set[FormType]:
        return AZURE_DI_FORMS

    def extract(
        self,
        form_type: FormType,
        page_images: list[Image.Image],
        pdf_bytes: bytes | None = None,
    ) -> ExtractionResult:
        """Send the document to Azure DI and normalize the response."""

        model_id = AZURE_MODEL_MAP.get(form_type)
        if model_id is None:
            raise ValueError(f"No Azure DI model for form type: {form_type.value}")

        # We always prefer to send the PREPROCESSED images to Azure, as they have 
        # been denoised, sharpened, and deskewed. This significantly improves 
        # Azure's extraction quality compared to sending the raw (noisy) scan.
        # It also avoids 'InvalidContent' errors if the original PDF was corrupt.
        
        pdf_buffer = io.BytesIO()
        try:
            # Convert all processed pages into a single high-quality PDF
            # We use the first image as the base and append the rest
            rgb_images = [img.convert("RGB") for img in page_images]
            rgb_images[0].save(
                pdf_buffer,
                format="PDF",
                save_all=True,
                append_images=rgb_images[1:],
                resolution=300.0,
            )
            document_content = pdf_buffer.getvalue()
            content_type = "application/pdf"
            logger.info("Sending %d preprocessed pages as a clean PDF to Azure", len(page_images))
        except Exception as e:
            logger.warning("Failed to rebuild PDF from images: %s. Falling back to first page image.", e)
            document_content = image_to_bytes(page_images[0], fmt="PNG")
            content_type = "image/png"

        logger.info(
            "Calling Azure DI model '%s' for %s (%d pages)",
            model_id,
            form_type.value,
            len(page_images),
        )

        poller = self._client.begin_analyze_document(
            model_id=model_id,
            body=AnalyzeDocumentRequest(bytes_source=document_content),
            content_type="application/octet-stream",
        )
        result = poller.result()

        # ---- Normalize Azure DI output to our unified structure ----
        structured_data: dict[str, Any] = {}
        field_values: dict[str, FieldValue] = {}
        review_flags: list[ReviewFlag] = []

        for doc in (result.documents or []):
            for field_name, field in (doc.fields or {}).items():
                value = self._extract_field_value(field)
                confidence = field.confidence if field.confidence is not None else 0.0

                field_values[field_name] = FieldValue(
                    value=value,
                    confidence=confidence,
                    source="azure_di",
                    needs_review=confidence < self._confidence_threshold,
                    review_reason=(
                        f"Low confidence ({confidence:.2f})"
                        if confidence < self._confidence_threshold
                        else None
                    ),
                )

                structured_data[field_name] = value

                if confidence < self._confidence_threshold:
                    review_flags.append(
                        ReviewFlag(
                            field_name=field_name,
                            severity=ReviewSeverity.WARNING,
                            message=f"Azure DI confidence {confidence:.2f} below threshold {self._confidence_threshold}",
                        )
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

        overall_confidence = (
            sum(fv.confidence for fv in field_values.values()) / len(field_values)
            if field_values
            else 0.0
        )

        return ExtractionResult(
            source_file="",
            total_pages=len(page_images),
            form_type=form_type,
            extraction_method="azure_di",
            model_id=self.model_id,
            structured_data=structured_data,
            pages=pages,
            review_flags=review_flags,
            needs_human_review=len(review_flags) > 0,
            overall_confidence=round(overall_confidence, 3),
        )

    @staticmethod
    def _extract_field_value(field: Any) -> Any:
        """Recursively extract the value from an Azure DI field object."""
        if field is None:
            return None

        field_type = getattr(field, "type", None) or getattr(field, "value_type", None)

        if field_type == "string":
            return field.value_string if hasattr(field, "value_string") else field.content
        elif field_type == "number":
            return field.value_number if hasattr(field, "value_number") else field.content
        elif field_type == "integer":
            return field.value_integer if hasattr(field, "value_integer") else field.content
        elif field_type == "date":
            return str(field.value_date) if hasattr(field, "value_date") and field.value_date else field.content
        elif field_type == "currency":
            currency = field.value_currency if hasattr(field, "value_currency") else None
            if currency:
                return currency.amount
            return field.content
        elif field_type == "selectionMark":
            return field.value_selection_mark if hasattr(field, "value_selection_mark") else field.content
        elif field_type == "array":
            items = field.value_array if hasattr(field, "value_array") else []
            return [AzureDIExtractor._extract_field_value(item) for item in (items or [])]
        elif field_type == "object":
            obj = field.value_object if hasattr(field, "value_object") else {}
            return {
                k: AzureDIExtractor._extract_field_value(v)
                for k, v in (obj or {}).items()
            }
        else:
            # Fallback: use content string
            return getattr(field, "content", None) or getattr(field, "value", None)


# Register extractor
ExtractorFactory.register("azure_di", AzureDIExtractor)
