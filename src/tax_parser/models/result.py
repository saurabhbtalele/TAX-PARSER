"""Core result models for the extraction pipeline."""

from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Form type enumeration
# ---------------------------------------------------------------------------

class FormType(str, Enum):
    """Supported IRS form types."""

    # Azure DI prebuilt-supported forms
    W2 = "W-2"
    FORM_1099_NEC = "1099-NEC"
    FORM_1099_R = "1099-R"
    FORM_1099_MISC = "1099-MISC"
    FORM_1040 = "1040"
    SCHEDULE_B = "Schedule B"
    SCHEDULE_C = "Schedule C"
    SCHEDULE_D = "Schedule D"
    SCHEDULE_E = "Schedule E"
    SCHEDULE_F = "Schedule F"

    # Custom LLM extraction forms
    SCHEDULE_K1_PARTNERSHIP = "Schedule K-1 (Partnership)"
    SCHEDULE_K1_SCORP = "Schedule K-1 (S-Corp)"
    FORM_1065 = "1065"
    FORM_1120S = "1120-S"
    FORM_1120 = "1120"

    UNKNOWN = "Unknown"


# Forms handled by Azure DI prebuilt models
AZURE_DI_FORMS: set[FormType] = {
    FormType.W2,
    FormType.FORM_1099_NEC,
    FormType.FORM_1099_R,
    FormType.FORM_1099_MISC,
    FormType.FORM_1040,
    FormType.SCHEDULE_B,
    FormType.SCHEDULE_C,
    FormType.SCHEDULE_D,
    FormType.SCHEDULE_E,
    FormType.SCHEDULE_F,
}

# Forms handled by custom LLM extraction
LLM_EXTRACTION_FORMS: set[FormType] = {
    FormType.SCHEDULE_K1_PARTNERSHIP,
    FormType.SCHEDULE_K1_SCORP,
    FormType.FORM_1065,
    FormType.FORM_1120S,
    FormType.FORM_1120,
}


# ---------------------------------------------------------------------------
# Field-level result
# ---------------------------------------------------------------------------

class FieldValue(BaseModel):
    """A single extracted field with confidence metadata."""

    value: Any = None
    confidence: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Extraction confidence 0..1",
    )
    source: str = Field(
        default="llm",
        description="Extraction source: 'azure_di' | 'llm' | 'manual'",
    )
    bounding_box: list[float] | None = Field(
        default=None,
        description="Bounding box [x0,y0,x1,y1] in normalized coords (0..1)",
    )
    needs_review: bool = False
    review_reason: str | None = None


# ---------------------------------------------------------------------------
# Review flags
# ---------------------------------------------------------------------------

class ReviewSeverity(str, Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


class ReviewFlag(BaseModel):
    """Signals a field or document requires human review."""

    field_name: str | None = None
    page: int | None = None
    severity: ReviewSeverity = ReviewSeverity.WARNING
    message: str = ""
    auto_resolved: bool = False


# ---------------------------------------------------------------------------
# Page-level and document-level results
# ---------------------------------------------------------------------------

class QualityMetrics(BaseModel):
    """Image quality assessment for a single page."""

    dpi: int = 300
    blur_score: float = Field(default=0.0, description="Laplacian variance – higher is sharper")
    is_skewed: bool = False
    has_watermark: bool = False
    overall_quality: str = Field(default="good", description="good | acceptable | poor")


class PageResult(BaseModel):
    """Extraction result for a single page."""

    page_number: int
    form_type: FormType = FormType.UNKNOWN
    quality: QualityMetrics = QualityMetrics()
    fields: dict[str, FieldValue] = Field(default_factory=dict)
    raw_text: str | None = None


class ExtractionResult(BaseModel):
    """Top-level result for a complete document."""

    source_file: str
    total_pages: int = 0
    form_type: FormType = FormType.UNKNOWN
    extraction_method: str = Field(
        default="",
        description="'azure_di' | 'llm' | 'hybrid'",
    )

    # Structured output – the fully parsed form data (Pydantic schema dict)
    structured_data: dict[str, Any] = Field(default_factory=dict)

    # Per-page detail
    pages: list[PageResult] = Field(default_factory=list)

    # Review
    review_flags: list[ReviewFlag] = Field(default_factory=list)
    needs_human_review: bool = False
    overall_confidence: float = 0.0

    # Timing
    processing_time_seconds: float = 0.0
