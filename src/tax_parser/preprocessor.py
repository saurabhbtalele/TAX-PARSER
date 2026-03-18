"""PDF pre-processing: convert to images, deskew, watermark removal, quality assessment."""

from __future__ import annotations

import base64
import io
import logging
from pathlib import Path

import cv2
import numpy as np
from pdf2image import convert_from_path
from PIL import Image

from tax_parser.models.result import QualityMetrics

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# PDF → Images
# ---------------------------------------------------------------------------

def pdf_to_images(pdf_path: str | Path, dpi: int = 300) -> list[Image.Image]:
    """Convert all pages of a PDF to PIL Images at the given DPI."""
    pdf_path = Path(pdf_path)
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    logger.info("Converting %s to images at %d DPI", pdf_path.name, dpi)
    images = convert_from_path(str(pdf_path), dpi=dpi)
    logger.info("Converted %d pages", len(images))
    return images


# ---------------------------------------------------------------------------
# Image enhancement
# ---------------------------------------------------------------------------

def _pil_to_cv2(img: Image.Image) -> np.ndarray:
    """Convert PIL Image to OpenCV BGR array."""
    rgb = np.array(img.convert("RGB"))
    return cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)


def _cv2_to_pil(arr: np.ndarray) -> Image.Image:
    """Convert OpenCV BGR array to PIL Image."""
    rgb = cv2.cvtColor(arr, cv2.COLOR_BGR2RGB)
    return Image.fromarray(rgb)


def deskew_image(img: Image.Image) -> Image.Image:
    """Correct minor rotation in a scanned page.

    Uses Hough line detection on edges to estimate the dominant angle
    and rotates to correct it.
    """
    cv_img = _pil_to_cv2(img)
    gray = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 50, 150, apertureSize=3)

    lines = cv2.HoughLinesP(edges, 1, np.pi / 180, threshold=200, minLineLength=100, maxLineGap=10)
    if lines is None:
        return img

    angles: list[float] = []
    for line in lines:
        x1, y1, x2, y2 = line[0]
        angle = np.degrees(np.arctan2(y2 - y1, x2 - x1))
        # Only consider near-horizontal lines (within ±10°)
        if abs(angle) < 10:
            angles.append(angle)

    if not angles:
        return img

    median_angle = float(np.median(angles))
    if abs(median_angle) < 0.3:
        return img  # Already straight enough

    logger.debug("Deskewing by %.2f degrees", median_angle)
    (h, w) = cv_img.shape[:2]
    center = (w // 2, h // 2)
    rotation_matrix = cv2.getRotationMatrix2D(center, median_angle, 1.0)
    rotated = cv2.warpAffine(cv_img, rotation_matrix, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
    return _cv2_to_pil(rotated)


def remove_watermark(img: Image.Image, method: str = "color") -> Image.Image:
    """Attempt to remove semi-transparent watermarks (e.g. 'Client Copy').

    The 'color' method targets gray/red tones typical of watermarks and
    replaces them with the background color.
    """
    cv_img = _pil_to_cv2(img)
    hsv = cv2.cvtColor(cv_img, cv2.COLOR_BGR2HSV)

    if method == "color":
        # Target grayish watermark text (slightly tighter range)
        lower_gray = np.array([0, 0, 150])
        upper_gray = np.array([180, 40, 210])
        mask_gray = cv2.inRange(hsv, lower_gray, upper_gray)

        # Target reddish watermark tones
        lower_red1 = np.array([0, 30, 140])
        upper_red1 = np.array([15, 180, 240])
        mask_red1 = cv2.inRange(hsv, lower_red1, upper_red1)

        lower_red2 = np.array([160, 30, 140])
        upper_red2 = np.array([180, 180, 240])
        mask_red2 = cv2.inRange(hsv, lower_red2, upper_red2)

        mask = mask_gray | mask_red1 | mask_red2

        # Dilate the mask to cover edges of watermark characters
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
        mask = cv2.dilate(mask, kernel, iterations=1)

        # Only affect large connected components (watermarks are big, form text is small)
        num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(mask, connectivity=8)
        filtered_mask = np.zeros_like(mask)
        for i in range(1, num_labels):
            area = stats[i, cv2.CC_STAT_AREA]
            if area > 500:  # Large blobs are likely watermark fragments
                filtered_mask[labels == i] = 255

        # Replace watermark pixels with white
        cv_img[filtered_mask > 0] = [255, 255, 255]

    return _cv2_to_pil(cv_img)


def sharpen_image(img: np.ndarray) -> np.ndarray:
    """Apply a mild sharpening filter to enhance text edges."""
    # Using a mild unsharp mask approach
    blurred = cv2.GaussianBlur(img, (0, 0), 3)
    return cv2.addWeighted(img, 1.5, blurred, -0.5, 0)


def enhance_image(img: Image.Image) -> Image.Image:
    """Apply general image enhancement: light denoising + contrast normalization + sharpening."""
    cv_img = _pil_to_cv2(img)

    # Convert to grayscale for processing
    gray = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY)

    # Adaptive histogram equalization (CLAHE) for contrast
    # Reduced clipLimit from 2.0 to 1.5 to be less aggressive
    clahe = cv2.createCLAHE(clipLimit=1.5, tileGridSize=(8, 8))
    enhanced = clahe.apply(gray)

    # Very light denoising (reduced h from 4 to 2 to preserve fine text details)
    enhanced = cv2.fastNlMeansDenoising(enhanced, h=2)

    # Sharpening to bring back text crispness
    enhanced = sharpen_image(enhanced)

    # Convert back to 3-channel for consistency
    enhanced_bgr = cv2.cvtColor(enhanced, cv2.COLOR_GRAY2BGR)
    return _cv2_to_pil(enhanced_bgr)


# ---------------------------------------------------------------------------
# Quality assessment
# ---------------------------------------------------------------------------

def assess_quality(img: Image.Image) -> QualityMetrics:
    """Evaluate image quality for extraction suitability."""
    cv_img = _pil_to_cv2(img)
    gray = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY)

    # Blur detection via Laplacian variance
    laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()

    # Estimate DPI from image dimensions (letter = 8.5 x 11 inches)
    h, w = gray.shape
    estimated_dpi = int(w / 8.5) if w > 0 else 0

    # Skew detection (simplified – check via Hough lines)
    edges = cv2.Canny(gray, 50, 150, apertureSize=3)
    lines = cv2.HoughLinesP(edges, 1, np.pi / 180, threshold=200, minLineLength=100, maxLineGap=10)
    is_skewed = False
    if lines is not None:
        angles = []
        for line in lines:
            x1, y1, x2, y2 = line[0]
            angle = np.degrees(np.arctan2(y2 - y1, x2 - x1))
            if abs(angle) < 10:
                angles.append(angle)
        if angles:
            median_angle = abs(float(np.median(angles)))
            is_skewed = median_angle > 0.5

    # Watermark detection: check for large low-saturation blobs
    hsv = cv2.cvtColor(cv_img, cv2.COLOR_BGR2HSV)
    lower = np.array([0, 0, 140])
    upper = np.array([180, 50, 220])
    mask = cv2.inRange(hsv, lower, upper)
    watermark_pixel_ratio = np.count_nonzero(mask) / mask.size
    has_watermark = watermark_pixel_ratio > 0.02  # >2% of pixels

    # Overall quality rating
    if laplacian_var > 500 and estimated_dpi >= 250:
        quality_label = "good"
    elif laplacian_var > 100 and estimated_dpi >= 150:
        quality_label = "acceptable"
    else:
        quality_label = "poor"

    return QualityMetrics(
        dpi=estimated_dpi,
        blur_score=round(laplacian_var, 2),
        is_skewed=is_skewed,
        has_watermark=has_watermark,
        overall_quality=quality_label,
    )


# ---------------------------------------------------------------------------
# Encoding helpers
# ---------------------------------------------------------------------------

def image_to_base64(img: Image.Image, fmt: str = "PNG") -> str:
    """Encode a PIL Image to a base64 string for API calls."""
    buffer = io.BytesIO()
    img.save(buffer, format=fmt)
    return base64.b64encode(buffer.getvalue()).decode("utf-8")


def image_to_bytes(img: Image.Image, fmt: str = "PNG") -> bytes:
    """Encode a PIL Image to bytes."""
    buffer = io.BytesIO()
    img.save(buffer, format=fmt)
    return buffer.getvalue()


# ---------------------------------------------------------------------------
# Full preprocessing pipeline
# ---------------------------------------------------------------------------

def preprocess_page(
    img: Image.Image,
    do_deskew: bool = True,
    do_watermark_removal: bool = True,
    do_enhance: bool = False,
) -> tuple[Image.Image, QualityMetrics]:
    """Run the full preprocessing pipeline on a single page image.

    Returns the processed image and its quality metrics.
    """
    quality = assess_quality(img)

    if do_deskew and quality.is_skewed:
        img = deskew_image(img)

    if do_watermark_removal and quality.has_watermark:
        img = remove_watermark(img)

    if do_enhance and quality.overall_quality != "good":
        img = enhance_image(img)

    return img, quality
