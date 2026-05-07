import json
import os
import google.generativeai as genai
from datetime import datetime
from dotenv import load_dotenv

# 1. Configuration
# Load environment variables from .env file
load_dotenv() 

API_KEY = os.getenv("GEMINI_API_KEY")

# Use absolute paths relative to this script's location
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(SCRIPT_DIR, "..", "dashboard_data.json")
OUTPUT_PATH = os.path.join(SCRIPT_DIR, "pending_sitrep.md")

if not API_KEY:
    print("Error: GEMINI_API_KEY not found in environment variables or .env file.")
    print("Please ensure you have a .env file with GEMINI_API_KEY='your_key'")
    exit(1)

# 2. Setup Gemini
# Try the latest flash model, fallback to pro if not available
try:
    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash-latest')
except Exception:
    model = genai.GenerativeModel('gemini-pro')

def load_data():
    try:
        with open(DATA_PATH, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: {DATA_PATH} not found. Ensure the dashboard pipeline has run.")
        return None

def generate_report(data):
    # We take the top 10 most critical countries by OOS rate or Hotspot ratio
    # for a concise situation report.
    critical_data = sorted(data, key=lambda x: x.get('hotspot_ratio') or 0, reverse=True)[:10]
    
    prompt = f"""
    SYSTEM INSTRUCTION: You are a Senior Education & Conflict Analyst for the Education Bridge Initiative (EBI).
    
    CONTEXT: EBI monitors educational continuity in 24 crisis-affected countries.
    
    TASK: Write a high-level "Situation Report" (SitRep) for the EBI field management team.
    
    DATASET (JSON):
    {json.dumps(critical_data, indent=2)}
    
    STRUCTURE YOUR RESPONSE AS FOLLOWS:
    
    1. **Strategic Overview**: A 2-sentence summary of the regional risk landscape.
    2. **Critical Hotspots**: Identify the 3 countries with the most alarming correlation between conflict (hotspot_ratio) and out-of-school populations. Explain WHY they are critical based on the data.
    3. **Data Quality Alerts**: Note any specific countries where missing data (null values) is preventing a full risk assessment.
    
    STYLE GUIDELINES:
    - Professional, direct, and actionable.
    - DO NOT hallucinate. Only use the provided metrics.
    - If a value is null, mention it as a 'reporting gap'.
    
    REQUIRED DISCLAIMER (At the end):
    "### 🤖 AI-GENERATED CONTENT NOTICE
    This report was automatically synthesized from the Analysis Hub dataset on {datetime.now().strftime('%Y-%m-%d')}. This summary MUST be reviewed and verified by a focal point before further distribution."
    """

    print("Generating report via Gemini API...")
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error generating report: {str(e)}"

def main():
    data = load_data()
    if data:
        report_text = generate_report(data)
        
        with open(OUTPUT_PATH, 'w') as f:
            f.write(report_text)
        
        print(f"Success! SitRep saved to: {OUTPUT_PATH}")
        print("\nNext Step: Review the .md file and verify the data accuracy.")

if __name__ == "__main__":
    main()
