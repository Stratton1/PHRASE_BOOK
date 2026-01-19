"""
Script 4: The AI Report Miner
Reads your old PDF reports, anonymizes them, classifies by Age/Style,
and adds them to the database using Claude AI.

This script requires an API key for Claude (Anthropic).

Setup:
1. Set your API key: export ANTHROPIC_API_KEY="your-key-here"
   OR set it directly in this script below.
2. Create a REPORTS_TO_MINE folder and place PDF reports inside.
3. Run: python 4_mine_reports.py

The AI will:
- Extract observations from the PDF
- Remove specific addresses/names
- Classify by property age and style
- Check against RICS rules from knowledge_bank.json
- Save results to the Master Excel database
"""

import os
import json
import pandas as pd
import pdfplumber
import anthropic
from config import DB_COLUMNS, OUTPUT_FILE
from openpyxl import load_workbook

# --- CONFIGURATION ---
# Place your PDF REPORTS (the ones you want to mine) in this folder:
REPORTS_DIR = os.path.join(os.getcwd(), "REPORTS_TO_MINE")

# API KEY SETUP (Replace with your actual key if not in env variables)
API_KEY = os.environ.get("ANTHROPIC_API_KEY")
# if not API_KEY: API_KEY = "sk-ant-..."  # Uncomment and paste your key here if needed

# Model to use (Haiku is fast and cheap, Sonnet is more capable)
MODEL = "claude-3-5-haiku-20241022"


def load_knowledge_bank():
    """Loads the RICS rules we just indexed."""
    try:
        with open("knowledge_bank.json", "r") as f:
            kb = json.load(f)
            print(f"✓ Loaded knowledge bank with {len(kb)} reference documents")
            return kb
    except FileNotFoundError:
        print("⚠ Warning: knowledge_bank.json not found.")
        print("  Run 3_build_knowledge_bank.py first, or the AI will work without RICS context.")
        return {}


def extract_text_from_pdf(pdf_path):
    """Extract all text from a PDF file."""
    text = ""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page_num, page in enumerate(pdf.pages, 1):
                t = page.extract_text()
                if t:
                    text += f"\n--- Page {page_num} ---\n{t}"
    except Exception as e:
        print(f"   [Error] Could not extract from PDF: {e}")
    return text


def analyze_with_claude(report_text, knowledge_bank):
    """
    Sends text to Claude to extract and clean phrases.
    Returns a list of phrase dictionaries.
    """

    # Prepare knowledge bank context (truncate if massive)
    kb_context = json.dumps(knowledge_bank, ensure_ascii=False)[:50000]

    prompt = f"""
You are an expert RICS Surveyor building a comprehensive phrase library.

YOUR TASK:
1. Read the survey report text below
2. Extract all key observations about building elements and their condition
3. ANONYMIZE them (remove specific addresses, postcodes, client names, dates, property numbers)
4. GENERALIZE them (e.g., "12 High Street" → "the property", specific dates → "recently")
5. CLASSIFY each phrase (Section, Element, Condition Rating 1-3)
6. INFER property age and style from clues in the report
7. Cross-check against RICS rules to ensure accuracy

RICS REFERENCE MATERIAL (Building Standards):
{kb_context}

CLASSIFICATION GUIDE:
- Section: Choose ONE: "External", "Internal", "Services", "Grounds", "Overall"
- Element: What building part? "Roof", "Walls", "Windows", "Electrical", etc.
- Sub_Section: What aspect? "Condition", "Defects", "Materials", "Safety"
- Condition_Rating: 1=Good, 2=Fair, 3=Poor
- Property_Style: "Detached", "Semi-Detached", "Terrace", "Flat", "Bungalow"
- Property_Age: One of: "Pre-1850", "1850-1899", "1900-1918", "1919-1945", "1946-1979", "1980-1999", "2000-2010", "2011-Present"

OUTPUT INSTRUCTIONS:
Return ONLY a JSON array with NO markdown, NO explanation.
Each object must have all these keys:
[
    {{
        "Section": "External",
        "Element": "Chimney Stacks",
        "Sub_Section": "Defects",
        "Content": "The chimney stack shows signs of deterioration with mortar joints in poor condition.",
        "Condition_Rating": "2",
        "Property_Style": "Semi-Detached",
        "Property_Age": "1900-1918"
    }},
    {{
        "Section": "Internal",
        "Element": "Walls",
        "Sub_Section": "Condition",
        "Content": "Internal walls are finished with plaster and paint in reasonable condition.",
        "Condition_Rating": "2",
        "Property_Style": "Semi-Detached",
        "Property_Age": "1900-1918"
    }}
]

REPORT TEXT TO MINE:
{report_text[:100000]}

Remember: Return ONLY the JSON array. No other text.
"""

    print("   -> Sending to Claude AI (this may take 30s)...")

    try:
        client = anthropic.Anthropic(api_key=API_KEY)
        message = client.messages.create(
            model=MODEL,
            max_tokens=4000,
            temperature=0,
            system="You are a JSON-only output machine. Return only valid JSON arrays.",
            messages=[{"role": "user", "content": prompt}]
        )

        # Extract the response text
        response_text = message.content[0].text

        # Try to parse JSON
        try:
            result = json.loads(response_text)
            if isinstance(result, list):
                return result
            else:
                print(f"   [Error] AI returned JSON but not an array: {type(result)}")
                return []
        except json.JSONDecodeError as e:
            print(f"   [Error] AI output was not valid JSON: {e}")
            print(f"   Raw output (first 200 chars): {response_text[:200]}")
            return []

    except anthropic.APIError as e:
        print(f"   [Error] API Error: {e}")
        return []


def save_to_excel(data, report_filename):
    """Append extracted phrases to the Master Excel sheet."""
    if not data:
        print("   No phrases to save.")
        return

    df_new = pd.DataFrame(data)

    # Ensure all columns exist
    for col in DB_COLUMNS:
        if col not in df_new.columns:
            df_new[col] = ""

    # Reorder columns
    df_new = df_new[DB_COLUMNS]

    # Append to Master Excel
    try:
        with pd.ExcelWriter(OUTPUT_FILE, engine='openpyxl', mode='a', if_sheet_exists='overlay') as writer:
            # Check if Master sheet exists
            try:
                ws = writer.sheets['Master']
                start_row = ws.max_row
            except KeyError:
                print(f"   [Error] Master sheet not found in {OUTPUT_FILE}")
                return

            # Write without headers (append to existing data)
            df_new.to_excel(
                writer,
                sheet_name='Master',
                index=False,
                header=False,
                startrow=start_row
            )
            print(f"   ✓ Saved {len(df_new)} phrases to Master Database")

    except Exception as e:
        print(f"   [Error] Could not save to Excel: {e}")


def main():
    """Main execution function."""
    print("=" * 70)
    print("PHRASE LIBRARY ENGINE - AI REPORT MINER")
    print("=" * 70)

    # Check API Key
    if not API_KEY:
        print("\n[ERROR] No API Key found!")
        print("\nSetup Instructions:")
        print("1. Get your API key from: https://console.anthropic.com/")
        print("2. Set environment variable: export ANTHROPIC_API_KEY='your-key'")
        print("3. Or edit this script and uncomment the line 'if not API_KEY: API_KEY = ...'")
        return

    # Check for reports folder
    if not os.path.exists(REPORTS_DIR):
        os.makedirs(REPORTS_DIR)
        print(f"\n✓ Created folder: {REPORTS_DIR}")
        print(f"\nNext steps:")
        print(f"1. Place your PDF reports in: {REPORTS_DIR}")
        print(f"2. Run this script again: python 4_mine_reports.py")
        return

    # Load knowledge bank
    print("\n")
    kb = load_knowledge_bank()

    # Find PDF reports
    pdf_files = [f for f in os.listdir(REPORTS_DIR) if f.lower().endswith(".pdf")]

    if not pdf_files:
        print(f"\n⚠ No PDF files found in {REPORTS_DIR}")
        print(f"Please add PDF reports to this folder and run again.")
        return

    print(f"\nFound {len(pdf_files)} report(s) to mine:\n")

    # Process each report
    for filename in pdf_files:
        print(f"Mining: {filename}")

        pdf_path = os.path.join(REPORTS_DIR, filename)

        # 1. Extract Text
        print("   -> Extracting text from PDF...")
        full_text = extract_text_from_pdf(pdf_path)

        if not full_text:
            print("   [Error] Could not extract text from PDF")
            continue

        print(f"   -> Extracted {len(full_text)} characters")

        # 2. Analyze with AI
        extracted_phrases = analyze_with_claude(full_text, kb)

        if not extracted_phrases:
            print(f"   [Warning] No phrases extracted")
            continue

        print(f"   -> AI extracted {len(extracted_phrases)} phrases")

        # 3. Add Source File tag
        for phrase in extracted_phrases:
            phrase['Source_File'] = filename

        # 4. Save to Excel
        save_to_excel(extracted_phrases, filename)
        print()

    print("=" * 70)
    print("✓ AI Report Mining Complete")
    print("=" * 70)


if __name__ == "__main__":
    main()
