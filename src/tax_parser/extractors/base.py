"""Abstract base extractor interface."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from PIL import Image

from tax_parser.models.result import ExtractionResult, FormType


class BaseExtractor(ABC):
    """Interface that all extractors must implement."""

    @abstractmethod
    def extract(
        self,
        form_type: FormType,
        page_images: list[Image.Image],
        pdf_bytes: bytes | None = None,
    ) -> ExtractionResult:
        """Extract structured data from page images.

        Args:
            form_type: The identified form type.
            page_images: Pre-processed page images.
            pdf_bytes: Optional raw PDF bytes (needed by Azure DI).

        Returns:
            ExtractionResult with structured_data and per-page details.
        """
        ...

    @property
    @abstractmethod
    def supported_forms(self) -> set[FormType]:
        """Set of FormType values this extractor can handle."""
        ...
