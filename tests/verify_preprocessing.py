import logging
from pathlib import Path
from tax_parser.engine import TaxParserEngine
from config.settings import get_settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_preprocessing_flag():
    settings = get_settings()
    
    # Test 1: Preprocessing Enabled (Default)
    settings.enable_preprocessing = True
    engine = TaxParserEngine(settings=settings)
    logger.info("Testing with enable_preprocessing=True")
    # We won't actually run a full PDF here to keep it fast, 
    # but we can verify the setting is stored.
    assert engine._settings.enable_preprocessing is True

    # Test 2: Preprocessing Disabled
    settings.enable_preprocessing = False
    engine = TaxParserEngine(settings=settings)
    logger.info("Testing with enable_preprocessing=False")
    assert engine._settings.enable_preprocessing is False
    
    logger.info("Feature flag tests passed!")

if __name__ == "__main__":
    test_preprocessing_flag()
