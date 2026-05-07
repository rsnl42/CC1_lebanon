# AI Narrative Synthesis Module

This module implements the **LLM-Generated Narrative Synthesis** capability described in the RFP response. It transforms structured JSON data from the Analysis Hub into human-readable Situation Reports (SitReps).

## Files
- `generate_sitreps.py`: The main Python script that connects to the Gemini API.
- `pending_sitrep.md`: The output file where the AI-generated report is saved for human review.

## Prerequisites
1. **Python 3.x** installed.
2. **Libraries**: Install the necessary Google and environment libraries:
   ```bash
   pip install -q -U google-generativeai python-dotenv
   ```
3. **API Key**: Obtain a free API key from [Google AI Studio](https://aistudio.google.com/).

## Configuration (.env)
Instead of exporting your key every time, you can store it in a `.env` file in the project root:
1. Create a file named `.env` in the root directory.
2. Add your key like this:
   ```text
   GEMINI_API_KEY='your_actual_key_here'
   ```

## How to Run
1. Run the script from anywhere in the project:
   ```bash
   python3 ai_synthesis/generate_sitreps.py
   ```

## Human-in-the-Loop Workflow
As per the project methodology, the output in `pending_sitrep.md` is considered a **draft**. 
1. Open `pending_sitrep.md`.
2. Verify the metrics against the dashboard.
3. Once approved, copy the content into your final report or dashboard UI.
