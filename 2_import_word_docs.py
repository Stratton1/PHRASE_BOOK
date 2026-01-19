"""
Module D: The Harvester - Word Document Parser
Imports historic "standard phrase" documents (Fast Texts, Paras 2, JBS Templates)
and sorts them into the clean Excel structure.

This script handles messy, inconsistent formatting from legacy Word docs.

Run: python 2_import_word_docs.py

Ensure your Word documents are in the same folder as this script.
"""

import os
import re
import pandas as pd
from docx import Document
from config import OUTPUT_FILE, DB_COLUMNS, SECTIONS

# --- Configuration for Pattern Matching ---
# This maps historic headers to the new "Section" names
SECTION_MAP = {
    "EXTERNAL": "Section_D_External",
    "OUTSIDE": "Section_D_External",
    "INTERNAL": "Section_E_Internal",
    "INSIDE": "Section_E_Internal",
    "SERVICES": "Section_F_Services",
    "GROUNDS": "Section_G_Grounds",
    "GENERAL": "Sections_A-C_H_I_J_K",
    "LEGAL": "Sections_A-C_H_I_J_K",
    "SUMMARY": "Sections_A-C_H_I_J_K",
    "BUILDING REG": "Building_Regulations"
}

# Regex to find headers like "4.1 Chimney Stacks" or "D1 - Roof"
HEADER_PATTERN = re.compile(r"^([A-Z]?\d+[\.\-]?\d*)\s+[:\-]?\s*(.*)", re.IGNORECASE)


def clean_text(text):
    """Removes extra whitespace and non-printable characters."""
    if not text:
        return ""
    return re.sub(r'\s+', ' ', text).strip()


def detect_section(header_text):
    """Guesses the Excel Sheet name based on a header keyword."""
    header_upper = header_text.upper()
    for key, sheet_name in SECTION_MAP.items():
        if key in header_upper:
            return sheet_name
    return None  # Default fallback if unsure


def parse_docx(file_path):
    """Reads a .docx file and extracts phrases by header."""
    print(f"Processing {os.path.basename(file_path)}...")

    try:
        doc = Document(file_path)
    except Exception as e:
        print(f"Skipping {file_path}: Not a valid .docx file ({e})")
        return []

    extracted_data = []
    current_section = "Sections_A-C_H_I_J_K"  # Default bucket
    current_element = "General"

    for paragraph in doc.paragraphs:
        text = clean_text(paragraph.text)
        if len(text) < 5:
            continue  # Skip empty/short lines

        # 1. Check if this line is a Header (e.g., "4.1 Chimney Stacks")
        match = HEADER_PATTERN.match(text)

        # Check if it looks like a bold header (often used in legacy docs)
        is_bold = any(run.bold for run in paragraph.runs)

        if (match or is_bold) and len(text) < 60:
            # It's likely a header
            raw_header = match.group(2) if match else text

            # Does this header switch the main Section? (e.g. "SECTION D EXTERNAL")
            new_section = detect_section(raw_header)
            if new_section:
                current_section = new_section

            # Update the Element (e.g. "Chimney Stacks")
            current_element = raw_header.title()
            print(f"  -> Found Element: {current_element} (Sheet: {current_section})")

        else:
            # It's content text
            entry = {
                "Section": current_section,  # This maps to the Sheet Name
                "Element": current_element,
                "Sub_Section": "Standard Phrase",
                "Content": text,
                "Condition_Rating": "",
                "Property_Style": "Any",
                "Property_Type": "Any",
                "Property_Age": "Any",
                "Source_File": os.path.basename(file_path)
            }
            extracted_data.append(entry)

    return extracted_data


def save_to_excel(all_data):
    """Appends the harvested data to the Master Excel file."""
    if not os.path.exists(OUTPUT_FILE):
        print(f"Error: {OUTPUT_FILE} not found. Run 1_setup_database.py first.")
        return

    print(f"\nSaving {len(all_data)} phrases to Excel...")

    # Load existing sheets
    try:
        # We need to read all sheets, append data, and write back
        with pd.ExcelWriter(OUTPUT_FILE, engine='openpyxl', mode='a', if_sheet_exists='overlay') as writer:

            # Group data by "Section" (which is the Sheet Name)
            df_all = pd.DataFrame(all_data)

            for sheet_name in df_all['Section'].unique():
                # Filter data for this sheet
                sheet_data = df_all[df_all['Section'] == sheet_name]

                # Align columns to match the DB format
                sheet_data = sheet_data.reindex(columns=DB_COLUMNS)

                # Determine where to write (find the last row)
                try:
                    start_row = writer.sheets[sheet_name].max_row
                except KeyError:
                    start_row = 0

                # Write to the specific sheet
                sheet_data.to_excel(writer, sheet_name=sheet_name, index=False, header=False, startrow=start_row)
                print(f"  -> Added {len(sheet_data)} rows to '{sheet_name}'")

    except Exception as e:
        print(f"Error saving to Excel: {e}")


def main():
    all_extracted_phrases = []

    # Look for all .docx files in the current folder
    for filename in os.listdir('.'):
        if filename.endswith(".docx") and not filename.startswith("~"):
            file_path = os.path.join('.', filename)
            phrases = parse_docx(file_path)
            all_extracted_phrases.extend(phrases)

    if all_extracted_phrases:
        save_to_excel(all_extracted_phrases)
        print("\nSuccess! Legacy phrases imported.")
    else:
        print("\nNo phrases found. Check your .docx files.")


if __name__ == "__main__":
    main()
