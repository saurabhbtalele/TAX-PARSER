"""Tests for the preprocessor module."""

import numpy as np
import pytest
from PIL import Image

from tax_parser.preprocessor import (
    assess_quality,
    deskew_image,
    enhance_image,
    image_to_base64,
    preprocess_page,
    remove_watermark,
)


def _make_test_image(width=2550, height=3300, color=(255, 255, 255)):
    """Create a blank letter-size image at 300 DPI."""
    return Image.new("RGB", (width, height), color)


def _add_text_block(img: Image.Image, x=100, y=100, w=200, h=30, color=(0, 0, 0)):
    """Simulate a block of text by drawing a dark rectangle."""
    arr = np.array(img)
    arr[y : y + h, x : x + w] = color
    return Image.fromarray(arr)


class TestAssessQuality:
    def test_good_quality_page_with_content(self):
        """A high-res page with text-like content should report as 'good' quality."""
        img = _make_test_image()
        # Add several text-like blocks to create edge content for blur detection
        for y in range(100, 3000, 100):
            img = _add_text_block(img, x=100, y=y, w=800, h=10)
        quality = assess_quality(img)
        assert quality.dpi >= 250
        assert quality.overall_quality in ("good", "acceptable")
        assert not quality.has_watermark

    def test_low_res_image(self):
        """A low-resolution image should be flagged as poor."""
        img = _make_test_image(width=425, height=550)  # ~50 DPI
        quality = assess_quality(img)
        assert quality.dpi < 100

    def test_watermark_detection(self):
        """An image with gray mid-tone areas should flag watermark."""
        img = _make_test_image()
        arr = np.array(img)
        # Add a large gray region simulating a watermark
        arr[500:2500, 300:2000] = (180, 180, 180)
        img = Image.fromarray(arr)
        quality = assess_quality(img)
        assert quality.has_watermark


class TestImageToBase64:
    def test_encodes_to_string(self):
        img = _make_test_image(width=100, height=100)
        b64 = image_to_base64(img)
        assert isinstance(b64, str)
        assert len(b64) > 100

    def test_roundtrip(self):
        """Base64 should decode back to a valid image."""
        import base64
        import io

        img = _make_test_image(width=100, height=100)
        b64 = image_to_base64(img, fmt="PNG")
        decoded = base64.b64decode(b64)
        restored = Image.open(io.BytesIO(decoded))
        assert restored.size == (100, 100)


class TestPreprocessPage:
    def test_returns_image_and_quality(self):
        img = _make_test_image()
        processed, quality = preprocess_page(img, do_deskew=False, do_watermark_removal=False)
        assert isinstance(processed, Image.Image)
        assert quality.dpi > 0

    def test_deskew_on_straight_image_is_noop(self):
        """A perfectly straight image should not be changed by deskew."""
        img = _make_test_image()
        processed, quality = preprocess_page(img, do_deskew=True, do_watermark_removal=False)
        # Image dimensions should be unchanged
        assert processed.size == img.size
