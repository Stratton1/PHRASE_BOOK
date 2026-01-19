"""
Script 3: Build the Knowledge Bank
Scans your USEFUL_DOCS folder and builds a JSON "Brain" from RICS/Building Regs files.

This creates a knowledge bank that provides context for the AI Report Miner.

Run: python 3_build_knowledge_bank.py

Ensure your reference documents (RICS rules, Building Regulations, etc.)
are in the USEFUL_DOCS folder.
"""

import os
import json
import pdfplumber
import re
from docx import Document

# DIRECTORY SETTINGS
DOCS_DIR = os.path.join(os.getcwd(), "USEFUL_DOCS")
OUTPUT_KB = "knowledge_bank.json"


def clean_text(text):
    """Clean up whitespace and weird characters."""
    if not text:
        return ""
    return re.sub(r'\s+', ' ', text).strip()


def extract_from_pdf(filepath):
    """Extract text from PDF."""
    print(f"   -> PDF: {os.path.basename(filepath)}")
    text = ""
    try:
        with pdfplumber.open(filepath) as pdf:
            for page in pdf.pages:
                extracted = page.extract_text()
                if extracted:
                    text += extracted + "\n"
    except Exception as e:
        print(f"      [Error] Could not read PDF: {e}")
    return text


def extract_from_docx(filepath):
    """Extract text from Word Doc."""
    print(f"   -> DOCX: {os.path.basename(filepath)}")
    try:
        doc = Document(filepath)
        return "\n".join([p.text for p in doc.paragraphs if p.text.strip()])
    except Exception as e:
        print(f"      [Error] Could not read DOCX: {e}")
        return ""


def build_knowledge_bank():
    """
    Main function to build knowledge bank from USEFUL_DOCS folder.
    """
    print("=" * 70)
    print("PHRASE LIBRARY ENGINE - KNOWLEDGE BANK BUILDER")
    print("=" * 70)
    print(f"\nScanning: {DOCS_DIR}\n")

    if not os.path.exists(DOCS_DIR):
        print(f"ERROR: Folder {DOCS_DIR} does not exist.")
        print(f"Please create the folder and add your reference documents:")
        print(f"  - RICS survey standards")
        print(f"  - Building Regulations guides")
        print(f"  - Other reference PDFs/DOCXs")
        return

    knowledge_store = {}
    file_count = 0

    # Iterate over files in USEFUL_DOCS
    for filename in os.listdir(DOCS_DIR):
        filepath = os.path.join(DOCS_DIR, filename)

        # Skip hidden files and non-files
        if filename.startswith("~") or filename.startswith("."):
            continue
        if not os.path.isfile(filepath):
            continue

        content = ""
        if filename.lower().endswith(".pdf"):
            content = extract_from_pdf(filepath)
        elif filename.lower().endswith(".docx"):
            content = extract_from_docx(filepath)
        elif filename.lower().endswith(".doc"):
            # .doc files are not easily supported by python-docx
            # but we include a note
            print(f"   -> DOC: {filename} (Note: .doc files not supported, use .docx)")
            continue
        else:
            # Skip unsupported formats
            continue

        if content:
            # Categorize by filename
            # e.g. Key="RICS_Module_A", Value="Full Text..."
            knowledge_store[filename] = clean_text(content)
            file_count += 1
            print(f"      ✓ Indexed: {len(content)} characters")

    # Save to JSON
    with open(OUTPUT_KB, 'w', encoding='utf-8') as f:
        json.dump(knowledge_store, f, ensure_ascii=False, indent=4)

    print("\n" + "=" * 70)
    print(f"✓ Knowledge Bank saved to '{OUTPUT_KB}'")
    print(f"✓ Indexed {file_count} documents")
    print("=" * 70)

    return knowledge_store


if __name__ == "__main__":
    build_knowledge_bank()
