# Architecture Overview: Tax Parser

## Vision
The Tax Parser is built to be an elite, enterprise-grade document extraction engine. It moves beyond simple OCR by combining state-of-the-art Generative AI with rigid domain validation rules.

## Design Philosophy

### 1. Hybrid Extraction Strategy (The "Why")
We use a dual-model approach:
- **Azure Document Intelligence**: Used for high-volume, standardized forms (W-2, 1040, 1099s). It provides ultra-consistent results and pixel-perfect bounding boxes.
- **Azure OpenAI (GPT-4o Vision)**: Used for complex, multi-page business tax returns (1120-S, 1065). These forms are too varied for traditional templates, requiring the "reasoning" capabilities of a Large Language Model.

### 2. Modularity & SOLID Principles
The system is built around the **Strategy Pattern** via the `Extractor` interface. 
- **Extensibility**: New models (Gemini, Mistral) can be added by implementing a new class and registering it in the `ExtractorFactory`.
- **Decoupling**: The core engine doesn't know *how* a model extracts data; it only knows that it receives a standardized `ExtractionResult`.

### 3. Verification & Trust
AI can hallucinate. To solve this, we implement a **Validation Layer**:
- **Arithmetic Consistency**: If total income doesn't equal the sum of its parts, a flag is raised.
- **Confidence Scoring**: We track confidence at the field level.
- **Human-in-the-Loop**: The system is designed to identify *when* it's unsure, proactively flagging documents for human review rather than silently failing.

### 4. Zero-Break Configuration
Using `pydantic-settings`, the application validates its environment at startup. It gracefully handles missing API keys—if you don't have a Gemini key, the system just skips that model comparison rather than crashing.

## Component Interaction

1. **API**: Receives the file and manages the async state.
2. **Preprocessor**: Cleans the images (deskew, watermark removal) to maximize capture accuracy.
3. **Classifier**: Identifies the form type to route it to the correct specialized extractor.
4. **Engine**: Orchestrates multiple extraction runs (for comparison) and aggregates metrics.
5. **Validator**: Runs tax-specific logic checks on the output.
6. **Web UI**: Provides a premium visualization of the results, metrics, and flags.
