"""PDF pre-processing pipeline for tax document scans.

Converts multi-page PDFs into clean, LLM-ready PNG images using a 6-step
pipeline: Grayscale → Denoise → CLAHE → Sharpen → Deskew → Upscale.

Key design principles:
  - CPU-only (no CUDA dependency)
  - Denoise *before* CLAHE to avoid amplifying scanner noise
  - Output is lossless PNG (max compression) for smallest file size
  - Every step can be saved to disk for pipeline traceability
  - Supports single file, batch folder, and CLI usage

Usage as a class::

    from tax_parser.preprocessor import TaxDocPreprocessor
    proc = TaxDocPreprocessor()
    result = proc.process_file("scan.pdf", output_dir=Path("output"))

Usage via CLI::

    python -m tax_parser.preprocessor --input scan.pdf --output ./output
    python -m tax_parser.preprocessor --input ./scans/ --output ./output --batch
"""

from __future__ import annotations

import argparse
import base64
import io
import json
import logging
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import cv2
import numpy as np
from pdf2image import convert_from_path
from PIL import Image

from tax_parser.models.result import QualityMetrics

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Configuration dataclass
# ---------------------------------------------------------------------------

@dataclass
class PreprocessorConfig:
    """Tunable parameters for the TaxDocPreprocessor pipeline.

    Attributes:
        target_dpi: Target DPI for upscaling. Pages estimated below this are
            upscaled to match it. Typical good value: 300.
        denoise_h: Filter strength for fastNlMeansDenoising.
            Lower = more detail preserved. Range 1-10. Default: 2.
        clahe_clip_limit: Contrast threshold for CLAHE.
            Lower = more conservative contrast enhancement. Range 1.0-4.0.
        clahe_tile_grid_size: CLAHE tile grid size (width, height).
        sharpen_sigma: Gaussian sigma for unsharp mask base.
        sharpen_amount: Blend factor for sharpening (1.0 = no change, >1 = sharper).
        deskew_angle_threshold: Minimum angle (degrees) to trigger rotation correction.
        deskew_max_angle: Angles larger than this are ignored (non-skew lines).
        save_steps: If True, save each pipeline step to a 'steps/' subfolder.
        png_compression: PNG compression level (0=none, 9=max). Default: 9 (smallest).
        output_suffix: Suffix appended to output filenames.
    """
    target_dpi: int = 300
    denoise_h: int = 2
    clahe_clip_limit: float = 1.5
    clahe_tile_grid_size: tuple[int, int] = (8, 8)
    sharpen_sigma: float = 3.0
    sharpen_amount: float = 1.5
    deskew_angle_threshold: float = 0.3
    deskew_max_angle: float = 10.0
    save_steps: bool = False
    png_compression: int = 9
    output_suffix: str = "_preprocessed"


# ---------------------------------------------------------------------------
# Core preprocessing class
# ---------------------------------------------------------------------------

class TaxDocPreprocessor:
    """Production-ready preprocessor for tax document scans.

    Implements a 6-step image enhancement pipeline optimized for feeding
    scanned tax forms (W-2, 1040, K-1, etc.) to vision LLMs.

    The pipeline order is:
        1. Grayscale  – reduce to single channel
        2. Denoise    – remove scanner noise (must run before CLAHE)
        3. CLAHE      – adaptive contrast normalization
        4. Sharpen    – restore text edge crispness via unsharp mask
        5. Deskew     – correct scan rotation via Hough line detection
        6. Upscale    – bicubic upscale if estimated DPI < target_dpi

    Example::

        proc = TaxDocPreprocessor(config=PreprocessorConfig(save_steps=True))
        result = proc.process_file(Path("w2_scan.pdf"), output_dir=Path("output"))
        print(result["quality"])
    """

    def __init__(self, config: Optional[PreprocessorConfig] = None) -> None:
        """Initialise the preprocessor with optional tunable config.

        Args:
            config: PreprocessorConfig instance. If None, defaults are used.
        """
        self.config = config or PreprocessorConfig()
        # Create CLAHE object once – reused for every page
        self._clahe = cv2.createCLAHE(
            clipLimit=self.config.clahe_clip_limit,
            tileGridSize=self.config.clahe_tile_grid_size,
        )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def process_file(
        self,
        input_path: str | Path,
        output_dir: str | Path,
    ) -> dict:
        """Process a single PDF or image file end-to-end.

        Converts all pages, runs the 6-step pipeline on each, and saves
        results to output_dir.

        Args:
            input_path: Path to a PDF or image file (.pdf, .png, .jpg).
            output_dir: Directory where output PNGs and quality report are saved.

        Returns:
            dict with keys:
                - "pages": list of processed PIL Images
                - "quality": list of QualityMetrics (one per page)
                - "output_files": list of Path to saved PNG files
                - "quality_report": Path to saved quality_report.json
        """
        input_path = Path(input_path)
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        # Steps subfolder (only created if save_steps=True)
        steps_dir = output_dir / "steps"

        logger.info("=== TaxDocPreprocessor: %s ===", input_path.name)
        start = time.time()

        # 1. Load pages
        raw_pages = self._load_pages(input_path)
        total = len(raw_pages)
        logger.info("Loaded %d page(s) from %s", total, input_path.name)

        processed_images: list[Image.Image] = []
        quality_list: list[QualityMetrics] = []
        output_files: list[Path] = []

        for i, raw_img in enumerate(raw_pages, start=1):
            logger.info("  Processing page %d / %d ...", i, total)
            page_steps_dir = (steps_dir / f"page_{i:03d}") if self.config.save_steps else None

            processed, quality = self._run_pipeline(raw_img, page_steps_dir)
            processed_images.append(processed)
            quality_list.append(quality)

            # Save output PNG (lossless, maximum compression)
            out_path = output_dir / f"page_{i:03d}{self.config.output_suffix}.png"
            self._save_png(processed, out_path)
            output_files.append(out_path)

            logger.info(
                "  Page %d → %s [DPI≈%d, blur=%.1f, quality=%s]",
                i, out_path.name, quality.dpi, quality.blur_score, quality.overall_quality,
            )

        # Save quality report JSON
        quality_report_path = output_dir / "quality_report.json"
        quality_data = [q.model_dump() for q in quality_list]
        quality_report_path.write_text(
            json.dumps(quality_data, indent=2, default=str),
            encoding="utf-8",
        )
        logger.info("Quality report → %s", quality_report_path)
        logger.info(
            "=== Done in %.1fs: %d page(s) saved to %s ===",
            time.time() - start, total, output_dir,
        )

        return {
            "pages": processed_images,
            "quality": quality_list,
            "output_files": output_files,
            "quality_report": quality_report_path,
        }

    def process_folder(
        self,
        input_folder: str | Path,
        output_root: str | Path,
        extensions: tuple[str, ...] = (".pdf", ".png", ".jpg", ".jpeg", ".tiff", ".tif"),
    ) -> list[dict]:
        """Batch-process all supported files in a folder.

        Each file gets its own subdirectory inside output_root named after
        the source file stem.

        Args:
            input_folder: Directory containing input files.
            output_root: Root directory where per-file output subfolders are created.
            extensions: Tuple of file extensions to process (case-insensitive).

        Returns:
            List of result dicts (one per file), same format as process_file().
        """
        input_folder = Path(input_folder)
        output_root = Path(output_root)

        # Discover files
        files = sorted(
            f for f in input_folder.iterdir()
            if f.is_file() and f.suffix.lower() in extensions
        )

        if not files:
            logger.warning("No supported files found in %s", input_folder)
            return []

        logger.info("Batch mode: %d file(s) found in %s", len(files), input_folder)
        results = []

        for idx, file_path in enumerate(files, start=1):
            logger.info("[%d/%d] Processing: %s", idx, len(files), file_path.name)
            out_dir = output_root / file_path.stem
            try:
                result = self.process_file(file_path, output_dir=out_dir)
                results.append(result)
            except Exception:
                logger.exception("Failed to process %s — skipping", file_path.name)
                results.append({"error": str(file_path), "output_files": []})

        logger.info("Batch complete: %d / %d succeeded", sum(1 for r in results if "error" not in r), len(files))
        return results

    def process_image(
        self,
        img: Image.Image,
        steps_dir: Optional[Path] = None,
    ) -> tuple[Image.Image, QualityMetrics]:
        """Process a single PIL Image through the full 6-step pipeline.

        This is the main integration point for TaxParserEngine, replacing
        the old `preprocess_page()` function.

        Args:
            img: Raw scanned page as PIL Image.
            steps_dir: If provided, save each pipeline step here as PNG.

        Returns:
            Tuple of (processed_image, quality_metrics).
        """
        return self._run_pipeline(img, steps_dir)

    # ------------------------------------------------------------------
    # Internal pipeline steps
    # ------------------------------------------------------------------

    def _run_pipeline(
        self,
        img: Image.Image,
        steps_dir: Optional[Path] = None,
    ) -> tuple[Image.Image, QualityMetrics]:
        """Execute the 6-step preprocessing pipeline on a single page.

        Pipeline order (critical — do not reorder):
            1. Grayscale  → reduce channels
            2. Denoise    → remove scanner/JPEG noise BEFORE contrast enhancement
            3. CLAHE      → adaptive local contrast (safe on clean input from step 2)
            4. Sharpen    → unsharp mask to restore edges softened by denoising
            5. Deskew     → correct scan angle
            6. Upscale    → raise resolution if too low for LLM quality

        Args:
            img: Input PIL Image (any mode).
            steps_dir: If set, intermediate result for each step is saved here.

        Returns:
            Tuple of (processed PIL Image, QualityMetrics).
        """
        if steps_dir:
            steps_dir.mkdir(parents=True, exist_ok=True)

        # ── Step 0: Assess input quality BEFORE any modification ──────────
        quality = assess_quality(img)

        # Convert to OpenCV grayscale (uint8, single channel)
        cv_img = _pil_to_cv2(img)

        # ── Step 1: Grayscale ─────────────────────────────────────────────
        gray = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY)
        if steps_dir:
            _save_cv_step(gray, steps_dir, "01_grayscale.png")
        logger.debug("  Step 1/6: Grayscale")

        # ── Step 2: Denoise ──────────────────────────────────────────────
        # MUST run before CLAHE. Denoising on a noisy image first prevents
        # CLAHE from amplifying scanner noise into visible artifacts.
        # h=2 is conservative: removes noise while preserving fine text strokes.
        denoised = cv2.fastNlMeansDenoising(
            gray,
            h=float(self.config.denoise_h),
            # Default block/search window sizes are fine for text documents
        )
        if steps_dir:
            _save_cv_step(denoised, steps_dir, "02_denoised.png")
        logger.debug("  Step 2/6: Denoise (h=%d)", self.config.denoise_h)

        # ── Step 3: CLAHE (Adaptive Contrast) ────────────────────────────
        # Normalises uneven lighting across the page (e.g. scan shadows at edges).
        # clipLimit=1.5 is mild — boosts local contrast without halation.
        enhanced = self._clahe.apply(denoised)
        if steps_dir:
            _save_cv_step(enhanced, steps_dir, "03_clahe.png")
        logger.debug("  Step 3/6: CLAHE (clip=%.1f)", self.config.clahe_clip_limit)

        # ── Step 4: Sharpen (Unsharp Mask) ───────────────────────────────
        # Denoising slightly softens edges. Sharpening restores text crispness.
        # Processed in float32 for accurate blending, then clipped back to uint8.
        sharpened = _unsharp_mask(
            enhanced,
            sigma=self.config.sharpen_sigma,
            amount=self.config.sharpen_amount,
        )
        if steps_dir:
            _save_cv_step(sharpened, steps_dir, "04_sharpened.png")
        logger.debug("  Step 4/6: Sharpen (σ=%.1f, amount=%.1f)", self.config.sharpen_sigma, self.config.sharpen_amount)

        # ── Step 5: Deskew ───────────────────────────────────────────────
        # Detect dominant angle from Hough lines and correct rotation.
        # Only rotates if angle > deskew_angle_threshold to avoid unnecessary transforms.
        deskewed = _deskew_gray(
            sharpened,
            angle_threshold=self.config.deskew_angle_threshold,
            max_angle=self.config.deskew_max_angle,
        )
        if steps_dir:
            _save_cv_step(deskewed, steps_dir, "05_deskewed.png")
        logger.debug("  Step 5/6: Deskew")

        # ── Step 6: Upscale ──────────────────────────────────────────────
        # If the page DPI is below target, upscale bicubically so the LLM can
        # confidently read fine print (box labels, line numbers, amounts).
        upscaled = _conditional_upscale(
            deskewed,
            estimated_dpi=quality.dpi,
            target_dpi=self.config.target_dpi,
        )
        if steps_dir:
            _save_cv_step(upscaled, steps_dir, "06_upscaled.png")
        logger.debug("  Step 6/6: Upscale (input DPI≈%d, target=%d)", quality.dpi, self.config.target_dpi)

        # Re-assess quality on the processed image for accurate output metrics
        final_pil = _gray_to_pil(upscaled)
        quality = assess_quality(final_pil)

        return final_pil, quality

    # ------------------------------------------------------------------
    # File I/O helpers
    # ------------------------------------------------------------------

    def _load_pages(self, path: Path) -> list[Image.Image]:
        """Load a PDF or image file into a list of PIL Images.

        PDFs are rendered at the DPI matching the target (default 300).
        Images are loaded as-is.

        Args:
            path: File to load.

        Returns:
            List of PIL Images (one per page).

        Raises:
            FileNotFoundError: If the file does not exist.
            ValueError: If the file extension is not supported.
        """
        if not path.exists():
            raise FileNotFoundError(f"Input file not found: {path}")

        ext = path.suffix.lower()

        if ext == ".pdf":
            logger.info("Rendering PDF at %d DPI ...", self.config.target_dpi)
            return convert_from_path(str(path), dpi=self.config.target_dpi)

        elif ext in (".png", ".jpg", ".jpeg", ".tiff", ".tif", ".bmp"):
            img = Image.open(path).convert("RGB")
            return [img]

        else:
            raise ValueError(f"Unsupported file type: {ext!r}")

    @staticmethod
    def _save_png(img: Image.Image, path: Path) -> None:
        """Save a PIL Image as a lossless PNG with maximum compression.

        Maximum compression (level 9) reduces file size significantly
        (often 60-80% smaller than raw) at a small encoding time cost.
        For LLM API calls, smaller payloads mean lower latency and cost.

        Args:
            img: PIL Image to save.
            path: Output file path (should have .png extension).
        """
        path.parent.mkdir(parents=True, exist_ok=True)
        img.save(str(path), format="PNG", optimize=True, compress_level=9)


# ---------------------------------------------------------------------------
# Low-level image operation helpers (module-private)
# ---------------------------------------------------------------------------

def _pil_to_cv2(img: Image.Image) -> np.ndarray:
    """Convert PIL Image to OpenCV BGR uint8 array."""
    rgb = np.array(img.convert("RGB"), dtype=np.uint8)
    return cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)


def _cv2_to_pil(arr: np.ndarray) -> Image.Image:
    """Convert OpenCV BGR uint8 array to PIL Image."""
    rgb = cv2.cvtColor(arr, cv2.COLOR_BGR2RGB)
    return Image.fromarray(rgb)


def _gray_to_pil(gray: np.ndarray) -> Image.Image:
    """Convert a single-channel grayscale array to PIL RGB Image."""
    rgb = cv2.cvtColor(gray, cv2.COLOR_GRAY2RGB)
    return Image.fromarray(rgb)


def _unsharp_mask(
    gray: np.ndarray,
    sigma: float = 3.0,
    amount: float = 1.5,
) -> np.ndarray:
    """Apply unsharp masking to sharpen text edges.

    Processed in float32 for precise blending, then clipped back to uint8.
    Formula: sharpened = original * amount + blurred * (1 - amount)
    Which simplifies to:   original + (original - blurred) * (amount - 1)

    Args:
        gray: Grayscale uint8 input image.
        sigma: Gaussian blur sigma for the base (larger = more effect).
        amount: Blending strength (1.0 = no change, 1.5 = moderate sharpen).

    Returns:
        Sharpened grayscale uint8 image.
    """
    # Work in float32 to avoid integer overflow during blending
    f = gray.astype(np.float32)
    blurred = cv2.GaussianBlur(f, (0, 0), sigma)
    # Classic unsharp mask: output = original * amount + blurred * (1 - amount)
    sharpened = f * amount + blurred * (1.0 - amount)
    # Clip and convert back to uint8
    return np.clip(sharpened, 0, 255).astype(np.uint8)


def _deskew_gray(
    gray: np.ndarray,
    angle_threshold: float = 0.3,
    max_angle: float = 10.0,
) -> np.ndarray:
    """Detect and correct scan rotation using Hough line detection.

    Finds dominant angle of near-horizontal lines (text baselines),
    computes the median, and rotates if angle exceeds `angle_threshold`.

    Args:
        gray: Grayscale uint8 image.
        angle_threshold: Minimum angle (degrees) to apply rotation.
        max_angle: Angles larger than this are ignored (non-text lines).

    Returns:
        Deskewed grayscale uint8 image (or original if no angle detected).
    """
    # Detect edges
    edges = cv2.Canny(gray, 50, 150, apertureSize=3)

    # Find probabilistic Hough lines
    lines = cv2.HoughLinesP(
        edges,
        rho=1,
        theta=np.pi / 180,
        threshold=200,
        minLineLength=100,
        maxLineGap=10,
    )
    if lines is None:
        logger.debug("  Deskew: no lines detected, skipping")
        return gray

    # Collect angles from near-horizontal lines (text rows, form lines)
    angles: list[float] = []
    for line in lines:
        x1, y1, x2, y2 = line[0]
        if x2 == x1:
            continue  # vertical line — ignore
        angle = np.degrees(np.arctan2(float(y2 - y1), float(x2 - x1)))
        if abs(angle) <= max_angle:
            angles.append(angle)

    if not angles:
        logger.debug("  Deskew: no near-horizontal lines found, skipping")
        return gray

    median_angle = float(np.median(angles))

    if abs(median_angle) < angle_threshold:
        logger.debug("  Deskew: angle %.3f° < threshold %.2f°, skipping", median_angle, angle_threshold)
        return gray

    # Rotate image to correct the skew
    logger.debug("  Deskew: correcting %.3f°", median_angle)
    (h, w) = gray.shape[:2]
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, median_angle, 1.0)
    rotated = cv2.warpAffine(
        gray, M, (w, h),
        flags=cv2.INTER_CUBIC,
        borderMode=cv2.BORDER_REPLICATE,  # fill edges with nearest pixels (not black)
    )
    return rotated


def _conditional_upscale(
    gray: np.ndarray,
    estimated_dpi: int,
    target_dpi: int = 300,
) -> np.ndarray:
    """Upscale image bicubically if its estimated DPI is below the target.

    For scans below 250 DPI, fine details (box labels, amounts in small font)
    become blurry and hard for vision LLMs to parse. Upscaling to 300 DPI
    equivalent restores legibility without enhancing noise (already denoised).

    Args:
        gray: Grayscale uint8 image.
        estimated_dpi: Estimated DPI of the input (from width / 8.5 for letter).
        target_dpi: Target DPI to upscale to if needed.

    Returns:
        Upscaled (or original) grayscale uint8 image.
    """
    # Only upscale if significantly below target
    if estimated_dpi >= int(target_dpi * 0.85):  # within 15% of target → skip
        logger.debug("  Upscale: DPI≈%d >= threshold, skipping", estimated_dpi)
        return gray

    if estimated_dpi <= 0:
        logger.debug("  Upscale: DPI unknown, skipping")
        return gray

    scale = target_dpi / estimated_dpi
    new_w = int(gray.shape[1] * scale)
    new_h = int(gray.shape[0] * scale)
    logger.debug(
        "  Upscale: %.1fx (DPI %d → %d), %dx%d → %dx%d",
        scale, estimated_dpi, target_dpi, gray.shape[1], gray.shape[0], new_w, new_h,
    )
    # cv2.INTER_CUBIC is best for upscaling document text (preserves sharp edges)
    return cv2.resize(gray, (new_w, new_h), interpolation=cv2.INTER_CUBIC)


def _save_cv_step(arr: np.ndarray, steps_dir: Path, filename: str) -> None:
    """Save an OpenCV array as PNG to the steps folder (for pipeline traceability).

    Args:
        arr: Grayscale or BGR uint8 OpenCV array.
        steps_dir: Directory to write the step image.
        filename: Output filename (e.g. '01_grayscale.png').
    """
    steps_dir.mkdir(parents=True, exist_ok=True)
    out = steps_dir / filename
    cv2.imwrite(str(out), arr, [cv2.IMWRITE_PNG_COMPRESSION, 9])


# ---------------------------------------------------------------------------
# Quality assessment
# ---------------------------------------------------------------------------

def assess_quality(img: Image.Image) -> QualityMetrics:
    """Evaluate image quality for extraction suitability.

    Checks:
    - DPI estimate (from image width assuming 8.5in letter paper)
    - Blur level (Laplacian variance — higher is sharper)
    - Skew detection (Hough lines)
    - Watermark detection (large low-saturation blobs)

    Args:
        img: PIL Image to assess.

    Returns:
        QualityMetrics with dpi, blur_score, is_skewed, has_watermark, overall_quality.
    """
    cv_img = _pil_to_cv2(img)
    gray = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY)

    # ── Blur detection via Laplacian variance ────────────────────────────
    # Higher variance = sharper edges = more focused text
    laplacian_var = float(cv2.Laplacian(gray, cv2.CV_64F).var())

    # ── DPI estimate ─────────────────────────────────────────────────────
    # Assumes US Letter paper (8.5 inches wide). Typical good scan = 300 DPI.
    h, w = gray.shape
    estimated_dpi = int(w / 8.5) if w > 0 else 0

    # ── Skew detection ───────────────────────────────────────────────────
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
            is_skewed = abs(float(np.median(angles))) > 0.5

    # ── Watermark detection ───────────────────────────────────────────────
    # Large low-saturation blobs (gray text overlays) are likely watermarks
    hsv = cv2.cvtColor(cv_img, cv2.COLOR_BGR2HSV)
    lower = np.array([0, 0, 140])
    upper = np.array([180, 50, 220])
    mask = cv2.inRange(hsv, lower, upper)
    watermark_pixel_ratio = float(np.count_nonzero(mask)) / mask.size
    has_watermark = watermark_pixel_ratio > 0.02  # >2% of pixels

    # ── Overall quality rating ────────────────────────────────────────────
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
# Watermark removal (unchanged — used by TaxParserEngine)
# ---------------------------------------------------------------------------

def remove_watermark(img: Image.Image, method: str = "color") -> Image.Image:
    """Attempt to remove semi-transparent watermarks (e.g. 'Client Copy').

    The 'color' method targets gray/red tones typical of watermarks and
    replaces them with the background color.

    Args:
        img: PIL Image with potential watermark.
        method: Only 'color' supported currently.

    Returns:
        PIL Image with watermark pixels replaced by white.
    """
    cv_img = _pil_to_cv2(img)
    hsv = cv2.cvtColor(cv_img, cv2.COLOR_BGR2HSV)

    if method == "color":
        # Grayish watermark text
        lower_gray, upper_gray = np.array([0, 0, 150]), np.array([180, 40, 210])
        mask_gray = cv2.inRange(hsv, lower_gray, upper_gray)

        # Reddish watermark tones (two hue ranges for red wraparound in HSV)
        lower_red1, upper_red1 = np.array([0, 30, 140]), np.array([15, 180, 240])
        mask_red1 = cv2.inRange(hsv, lower_red1, upper_red1)
        lower_red2, upper_red2 = np.array([160, 30, 140]), np.array([180, 180, 240])
        mask_red2 = cv2.inRange(hsv, lower_red2, upper_red2)

        mask = mask_gray | mask_red1 | mask_red2

        # Dilate mask to catch anti-aliased edges of watermark characters
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
        mask = cv2.dilate(mask, kernel, iterations=1)

        # Only remove large blobs — small components are likely form text
        num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(mask, connectivity=8)
        filtered_mask = np.zeros_like(mask)
        for i in range(1, num_labels):
            if stats[i, cv2.CC_STAT_AREA] > 500:  # Large = likely watermark fragment
                filtered_mask[labels == i] = 255

        cv_img[filtered_mask > 0] = [255, 255, 255]

    return _cv2_to_pil(cv_img)


# ---------------------------------------------------------------------------
# Encoding helpers (unchanged API — used throughout the codebase)
# ---------------------------------------------------------------------------

def image_to_base64(img: Image.Image, fmt: str = "PNG") -> str:
    """Encode a PIL Image to a base64 string for LLM API calls.

    Args:
        img: PIL Image to encode.
        fmt: Image format ('PNG' recommended for lossless encoding).

    Returns:
        Base64-encoded string of the image bytes.
    """
    buffer = io.BytesIO()
    img.save(buffer, format=fmt)
    return base64.b64encode(buffer.getvalue()).decode("utf-8")


def image_to_bytes(img: Image.Image, fmt: str = "PNG") -> bytes:
    """Encode a PIL Image to raw bytes.

    Args:
        img: PIL Image to encode.
        fmt: Image format.

    Returns:
        Image as bytes.
    """
    buffer = io.BytesIO()
    img.save(buffer, format=fmt)
    return buffer.getvalue()


# ---------------------------------------------------------------------------
# Backward-compatible functional API
# ---------------------------------------------------------------------------

def pdf_to_images(pdf_path: str | Path, dpi: int = 300) -> list[Image.Image]:
    """Convert all pages of a PDF to PIL Images at the given DPI.

    This is a thin backward-compatible wrapper. New code should use
    TaxDocPreprocessor.process_file() instead.

    Args:
        pdf_path: Path to the PDF file.
        dpi: Rendering resolution in DPI (default 300).

    Returns:
        List of PIL Images (one per page).
    """
    pdf_path = Path(pdf_path)
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")
    logger.info("Converting %s to images at %d DPI", pdf_path.name, dpi)
    images = convert_from_path(str(pdf_path), dpi=dpi)
    logger.info("Converted %d pages", len(images))
    return images


def deskew_image(img: Image.Image) -> Image.Image:
    """Correct minor rotation in a scanned page.

    Backward-compatible wrapper around the internal deskew logic.

    Args:
        img: PIL Image to deskew.

    Returns:
        Deskewed PIL Image.
    """
    cv_img = _pil_to_cv2(img)
    gray = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY)
    deskewed = _deskew_gray(gray)
    return _gray_to_pil(deskewed)


def enhance_image(img: Image.Image) -> Image.Image:
    """Apply the full 4-step enhancement sub-pipeline (grayscale→denoise→CLAHE→sharpen).

    Backward-compatible wrapper. For the full 6-step pipeline including
    deskew and upscale, use TaxDocPreprocessor.process_image() instead.

    Args:
        img: PIL Image to enhance.

    Returns:
        Enhanced PIL Image (grayscale converted back to RGB).
    """
    proc = TaxDocPreprocessor()
    # Run only steps 1-4 (no deskew, no upscale)
    cv_img = _pil_to_cv2(img)
    gray = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY)
    denoised = cv2.fastNlMeansDenoising(gray, h=2.0)
    clahe = cv2.createCLAHE(clipLimit=1.5, tileGridSize=(8, 8))
    enhanced = clahe.apply(denoised)
    sharpened = _unsharp_mask(enhanced)
    return _gray_to_pil(sharpened)


def sharpen_image(img: np.ndarray) -> np.ndarray:
    """Apply mild sharpening to a cv2 grayscale array.

    Backward-compatible wrapper.

    Args:
        img: Grayscale uint8 OpenCV array.

    Returns:
        Sharpened array.
    """
    return _unsharp_mask(img)


def preprocess_page(
    img: Image.Image,
    do_deskew: bool = True,
    do_watermark_removal: bool = True,
    do_enhance: bool = True,
) -> tuple[Image.Image, QualityMetrics]:
    """Run the full preprocessing pipeline on a single page image.

    Backward-compatible wrapper around the new TaxDocPreprocessor class.
    New code should prefer TaxDocPreprocessor.process_image() directly.

    Args:
        img: Raw scanned page as PIL Image.
        do_deskew: Whether to apply deskew correction.
        do_watermark_removal: Whether to attempt watermark removal.
        do_enhance: Whether to run the enhancement sub-pipeline.

    Returns:
        Tuple of (processed_image, quality_metrics).
    """
    quality = assess_quality(img)

    if do_watermark_removal and quality.has_watermark:
        img = remove_watermark(img)

    if do_enhance:
        # Use the full TaxDocPreprocessor pipeline (all 6 steps respecting do_deskew)
        config = PreprocessorConfig(
            deskew_angle_threshold=0.3 if do_deskew else 9999.0,  # disable deskew if not requested
        )
        proc = TaxDocPreprocessor(config=config)
        img, quality = proc.process_image(img)
    elif do_deskew and quality.is_skewed:
        img = deskew_image(img)

    return img, quality


# ---------------------------------------------------------------------------
# CLI entrypoint
# ---------------------------------------------------------------------------

def _build_cli_parser() -> argparse.ArgumentParser:
    """Build the argparse parser for CLI usage."""
    parser = argparse.ArgumentParser(
        prog="python -m tax_parser.preprocessor",
        description=(
            "Tax document PDF/image preprocessor — cleans scanned tax forms "
            "for vision LLM consumption using a 6-step pipeline: "
            "Grayscale → Denoise → CLAHE → Sharpen → Deskew → Upscale."
        ),
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    # Input/output
    parser.add_argument("--input", "-i", required=True, help="Input PDF/image file or folder (for --batch)")
    parser.add_argument("--output", "-o", required=True, help="Output directory (created if missing)")
    parser.add_argument("--batch", "-b", action="store_true", help="Process all PDFs/images in --input folder")

    # Pipeline tuning
    parser.add_argument("--dpi", type=int, default=300, help="Target DPI for rendering and upscaling")
    parser.add_argument("--denoise-h", type=int, default=2, help="Denoising filter strength (1-10)")
    parser.add_argument("--clahe-clip", type=float, default=1.5, help="CLAHE clip limit (1.0-4.0)")
    parser.add_argument("--no-deskew", action="store_true", help="Disable deskew step")
    parser.add_argument("--no-upscale", action="store_true", help="Disable upscale step")
    parser.add_argument("--save-steps", action="store_true", help="Save each pipeline step to output/steps/")
    parser.add_argument("--log-level", default="INFO", choices=["DEBUG", "INFO", "WARNING", "ERROR"])

    return parser


def main() -> None:
    """CLI entrypoint. Run with: python -m tax_parser.preprocessor --help"""
    parser = _build_cli_parser()
    args = parser.parse_args()

    # Configure logging
    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%H:%M:%S",
    )

    config = PreprocessorConfig(
        target_dpi=args.dpi,
        denoise_h=args.denoise_h,
        clahe_clip_limit=args.clahe_clip,
        deskew_angle_threshold=9999.0 if args.no_deskew else 0.3,  # disable by huge threshold
        save_steps=args.save_steps,
    )

    proc = TaxDocPreprocessor(config=config)
    output_dir = Path(args.output)

    if args.batch:
        results = proc.process_folder(args.input, output_dir)
        total = len(results)
        ok = sum(1 for r in results if "error" not in r)
        print(f"\n✅ Batch complete: {ok}/{total} files processed → {output_dir}")
    else:
        result = proc.process_file(args.input, output_dir)
        pages = len(result["output_files"])
        print(f"\n✅ Done: {pages} page(s) saved to {output_dir}")
        for path in result["output_files"]:
            size_kb = path.stat().st_size / 1024
            print(f"   {path.name} ({size_kb:.1f} KB)")


if __name__ == "__main__":
    main()

# Alias for specific user request
W2Preprocessor = TaxDocPreprocessor

