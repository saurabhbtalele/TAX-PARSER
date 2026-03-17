# Deep Dive: Extractor Factory & Modular AI

The TAX-PARSER uses a **Strategy Pattern** combined with a **Factory Registry** to handle multiple AI models. This document explains how it works and why this architecture was chosen.

## The Core Problem
Different documents (W-2 vs. 1065) require different AI capabilities (Vision, Prebuilt Models, LLM Reasoning). Hard-coding these into the `TaxParserEngine` leads to:
1.  **Complexity**: The engine becomes an unreadable "if/else" mess.
2.  **Fragility**: Adding a new model (e.g., Gemini) requires modifying the core processing loop.
3.  **Failure Mode**: If one model fails or is missing a key, the entire application crashes.

## The Solution: Modular Extractors

### 1. The Interface (`BaseExtractor`)
Every model (GPT-4o, Azure DI, etc.) must implement a common interface. This ensures the Engine treats them all exactly the same.

```python
class BaseExtractor(ABC):
    @property
    def model_id(self) -> str: ...
    @property
    def display_name(self) -> str: ...
    def is_available(self, settings) -> bool: ...
    def extract(self, ...) -> ExtractionResult: ...
```

### 2. The Registry (`ExtractorFactory`)
The factory acts as a central phonebook for AI models. Extractors "register" themselves when they are imported. This allows the system to find models by ID at runtime.

### 3. Graceful Availability Checks
Unlike traditional systems that fail if a configuration is missing, our factory uses the `is_available()` method. 
- **The Engine** asks the Factory: "Which models are ready to work?"
- **The Factory** checks the `.env` settings for each registered model.
- **The Result**: Only models with valid API keys used for comparison.

## Data Flow in Model Comparison

When a document is uploaded:
1.  **Primary Extraction**: The system identifies the "best" model for that form (e.g., Azure DI for W-2).
2.  **Comparison Orchestration**:
    - The Engine iterates over `active_comparison_models`.
    - It skips the primary model (already run).
    - It checks if comparison models are registered and have API keys.
3.  **Parallel Scoring**: Each run captures its own confidence, time, and quality metrics.
4.  **Aggregation**: All results are combined into the specialized `comparisons` list in the final JSON.

## Why Quality Scores Matter
We don't just rely on "AI Confidence" (which can be biased). Our `quality_score` is a hybrid metric:
- **70% Completeness**: Did the model actually find all the data required by the schema?
- **30% Confidence**: How sure was the model of the data it *did* find?

This provides a grounded, objective way to compare GPT-4o against Azure Document Intelligence.
