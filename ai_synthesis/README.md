# AI Narrative Synthesis Module

This module implements the **LLM-Generated Narrative Synthesis** capability described in the RFP response. It transforms structured JSON data from the Analysis Hub into human-readable Situation Reports (SitReps).

## Files
- `generate_sitreps.py`: The main Python script that connects to the Gemini API.
- `pending_sitrep.md`: The output file where the AI-generated report is saved for human review.

## Prerequisites
1. **Python 3.x** installed.
2. **Library**: Install the Google Generative AI library:
   ```bash
   pip install -q -U google-generativeai
   ```
3. **API Key**: Obtain a free API key from [Google AI Studio](https://aistudio.google.com/).

## How to Run
1. Navigate to this folder:
   ```bash
   cd ai_synthesis
   ```
2. Set your API key as an environment variable:
   ```bash
   export GEMINI_API_KEY='your_actual_key_here'
   ```
3. Run the script:
   ```bash
   python3 generate_sitreps.py
   ```

## Human-in-the-Loop Workflow
As per the project methodology, the output in `pending_sitrep.md` is considered a **draft**. 
1. Open `pending_sitrep.md`.
2. Verify the metrics against the dashboard.
3. Once approved, copy the content into your final report or dashboard UI.
