"""Registry for all extractors to support modular model discovery."""

from __future__ import annotations

from typing import TYPE_CHECKING, Type

if TYPE_CHECKING:
    from tax_parser.extractors.base import BaseExtractor
    from config.settings import Settings

class ExtractorFactory:
    """Central factory to register and instantiate extractors."""

    _extractors: dict[str, Type[BaseExtractor]] = {}

    @classmethod
    def register(cls, model_id: str, extractor_cls: Type[BaseExtractor]) -> None:
        """Register a new extractor class."""
        cls._extractors[model_id] = extractor_cls

    @classmethod
    def get_extractor(cls, model_id: str, settings: Settings) -> BaseExtractor | None:
        """Instantiate an extractor by model_id."""
        extractor_cls = cls._extractors.get(model_id)
        if not extractor_cls:
            return None
        return extractor_cls(settings)

    @classmethod
    def get_available_extractors(cls, settings: Settings) -> list[BaseExtractor]:
        """Return instances of all registered and available extractors."""
        available = []
        for model_id, extractor_cls in cls._extractors.items():
            instance = extractor_cls(settings)
            if instance.is_available(settings):
                available.append(instance)
        return available
