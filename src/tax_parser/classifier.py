"""Form type classification using Azure OpenAI GPT-4o Vision."""

from __future__ import annotations

import json
import logging
from typing import TYPE_CHECKING

from openai import AzureOpenAI
from PIL import Image

from tax_parser.models.result import FormType
from tax_parser.preprocessor import image_to_base64

if TYPE_CHECKING:
    from config.settings import Settings

logger = logging.getLogger(__name__)

CLASSIFICATION_PROMPT = """\
You are a tax document classifier. Examine this scanned image of a US tax form page \
and identify the exact IRS form type.

The form_type MUST be one of:
- "W-2" (Look for "Wage and Tax Statement", "Employer identification number", Box 1 "Wages, tips, other compensation")
- "1099-NEC" (Look for "Nonemployee Compensation", "Payer's TIN", "Recipient's TIN", Box 1 "Nonemployee compensation")
- "1099-R" (Look for "Distributions From Pensions, Annuities, Retirement...")
- "1099-MISC" (Look for "Miscellaneous Income", Box 1 "Rents", Box 3 "Other income")
- "1040" (Look for "U.S. Individual Income Tax Return", "Name", "SSN")
- "Schedule B", "Schedule C", "Schedule D", "Schedule E", "Schedule F"
- "Schedule K-1 (Partnership)" (Form 1065)
- "Schedule K-1 (S-Corp)" (Form 1120-S)
- "1065", "1120-S", "1120"
- "Unknown"

Differentiating W-2 vs 1099-NEC:
- A W-2 almost always has the text "W-2" in a large font, often in the bottom-left or top-left, and mentions "Social security wages".
- A 1099-NEC has "1099-NEC" and focuses on "Nonemployee compensation".

Return ONLY a JSON object with these fields:
{
  "form_type": "<exact form type>",
  "confidence": <0.0 to 1.0>,
  "page_description": "<brief description of what this page contains>"
}

Return valid JSON only, no markdown fences.
"""


class FormClassifier:
    """Classify tax form pages using GPT-4o vision."""

    def __init__(self, settings: Settings) -> None:
        self._client = AzureOpenAI(
            azure_endpoint=settings.azure_openai_endpoint,
            api_key=settings.azure_openai_key,
            api_version=settings.azure_openai_api_version,
        )
        self._deployment = settings.azure_openai_deployment

    def classify_page(self, page_image: Image.Image) -> tuple[FormType, float, str]:
        """Classify a single page image.

        Returns:
            (form_type, confidence, page_description)
        """
        b64 = image_to_base64(page_image, fmt="PNG")

        response = self._client.chat.completions.create(
            model=self._deployment,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": CLASSIFICATION_PROMPT},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{b64}",
                                "detail": "low",  # Low detail is sufficient for classification
                            },
                        },
                    ],
                }
            ],
            max_tokens=300,
            temperature=0.0,
        )

        raw = response.choices[0].message.content or "{}"
        raw = raw.strip()

        # Strip markdown fences if present
        if raw.startswith("```"):
            raw = raw.split("\n", 1)[-1]
            if raw.endswith("```"):
                raw = raw[: raw.rfind("```")]
            raw = raw.strip()

        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            logger.warning("Failed to parse classifier response: %s", raw)
            return FormType.UNKNOWN, 0.0, ""

        form_type_str = data.get("form_type", "Unknown")
        confidence = float(data.get("confidence", 0.0))
        description = data.get("page_description", "")

        # Map string to enum
        form_type = FormType.UNKNOWN
        for ft in FormType:
            if ft.value == form_type_str:
                form_type = ft
                break

        logger.info(
            "Classified page as %s (confidence=%.2f): %s",
            form_type.value,
            confidence,
            description,
        )
        return form_type, confidence, description

    def classify_document(
        self, page_images: list[Image.Image]
    ) -> tuple[FormType, list[tuple[FormType, float, str]]]:
        """Classify all pages and determine the primary document form type.

        Returns:
            (primary_form_type, [(page_form_type, confidence, description), ...])
        """
        page_classifications: list[tuple[FormType, float, str]] = []

        for i, img in enumerate(page_images):
            logger.info("Classifying page %d / %d ...", i + 1, len(page_images))
            ft, conf, desc = self.classify_page(img)
            page_classifications.append((ft, conf, desc))

        # Determine primary form type by majority vote (weighted by confidence)
        type_scores: dict[FormType, float] = {}
        for ft, conf, _ in page_classifications:
            if ft != FormType.UNKNOWN:
                type_scores[ft] = type_scores.get(ft, 0.0) + conf

        if type_scores:
            primary = max(type_scores, key=type_scores.get)  # type: ignore[arg-type]
        else:
            primary = FormType.UNKNOWN

        logger.info("Primary document type: %s", primary.value)
        return primary, page_classifications
