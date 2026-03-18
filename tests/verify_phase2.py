"""Quick verification script for Phase 2 enhancements."""
import sys
sys.path.insert(0, r"d:\TAX_LLM_BASED\TAX-PARSER\src")
sys.path.insert(0, r"d:\TAX_LLM_BASED\TAX-PARSER")

from tax_parser.extractors.factory import ExtractorFactory
from config.settings import get_settings

settings = get_settings()

print("=== Phase 2 Verification ===")
print(f"Active comparison models: {settings.active_comparison_models}")
print(f"Gemini API key set: {bool(settings.gemini_api_key)}")
print(f"Case output dir: {settings.case_output_dir}")
print(f"Gemini model name: {settings.gemini_model_name}")

# Check factory registrations
print("\n--- Factory Registrations ---")
for mid, cls in ExtractorFactory._extractors.items():
    inst = cls(settings)
    print(f"  {mid}: {inst.display_name} (available: {inst.is_available(settings)})")

# Verify engine loads
from tax_parser.engine import TaxParserEngine
engine = TaxParserEngine()
print("\n[OK] TaxParserEngine loaded successfully!")
print("=== All checks passed ===")
