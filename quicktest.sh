#!/bin/bash
# Quick Test Script for Phrase Library Engine

echo "========================================================================"
echo "PHRASE LIBRARY ENGINE - QUICK TEST"
echo "========================================================================"
echo ""

# Test 1: Database Setup
echo "TEST 1: Database Setup"
echo "Running: python3 1_setup_database.py"
echo ""
python3 1_setup_database.py
if [ $? -eq 0 ]; then
    echo "✅ TEST 1 PASSED: Database created successfully"
else
    echo "❌ TEST 1 FAILED"
    exit 1
fi

echo ""
echo "========================================================================"
echo ""

# Test 2: Word Document Import (using sample)
echo "TEST 2: Word Document Import"
echo "Checking for sample documents..."
echo ""

if [ -f "sample_survey.docx" ]; then
    echo "Running: python3 2_import_word_docs.py --file sample_survey.docx"
    echo ""
    python3 2_import_word_docs.py --file sample_survey.docx
    if [ $? -eq 0 ]; then
        echo "✅ TEST 2 PASSED: Word import successful"
    else
        echo "❌ TEST 2 FAILED"
        exit 1
    fi
else
    echo "⚠️  TEST 2 SKIPPED: sample_survey.docx not found"
    echo "To test: Place a .docx file in the project folder and run:"
    echo "  python3 2_import_word_docs.py"
fi

echo ""
echo "========================================================================"
echo ""

# Test 3: Knowledge Bank Builder
echo "TEST 3: Knowledge Bank Builder"
echo "Checking USEFUL_DOCS folder..."
echo ""

doc_count=$(find USEFUL_DOCS -type f \( -name "*.pdf" -o -name "*.docx" \) 2>/dev/null | wc -l)
echo "Found $doc_count documents in USEFUL_DOCS/"
echo ""

if [ $doc_count -gt 0 ]; then
    echo "Running: python3 3_build_knowledge_bank.py"
    echo ""
    python3 3_build_knowledge_bank.py
    if [ $? -eq 0 ]; then
        echo "✅ TEST 3 PASSED: Knowledge bank built"
    else
        echo "❌ TEST 3 FAILED"
        exit 1
    fi
else
    echo "⚠️  TEST 3 SKIPPED: No documents in USEFUL_DOCS/"
    echo "To test: Add PDFs or Word documents to USEFUL_DOCS/ folder"
fi

echo ""
echo "========================================================================"
echo ""

# Test 4: AI Report Miner (requires API key)
echo "TEST 4: AI Report Miner"
echo "Checking for API Key..."
echo ""

if [ -z "$ANTHROPIC_API_KEY" ]; then
    echo "⚠️  TEST 4 SKIPPED: ANTHROPIC_API_KEY not set"
    echo ""
    echo "To test AI mining:"
    echo "  1. Get API key from: https://console.anthropic.com/"
    echo "  2. Set environment: export ANTHROPIC_API_KEY='sk-ant-...'"
    echo "  3. Place PDF reports in: REPORTS_TO_MINE/"
    echo "  4. Run: python3 4_mine_reports.py"
else
    echo "API Key detected!"
    echo ""
    echo "Running: python3 4_mine_reports.py"
    echo ""
    python3 4_mine_reports.py
    if [ $? -eq 0 ]; then
        echo "✅ TEST 4 PASSED: AI report mining ready"
    else
        echo "❌ TEST 4 FAILED"
        exit 1
    fi
fi

echo ""
echo "========================================================================"
echo ""

# Summary
echo "VERIFICATION: Check the database"
echo ""
python3 << 'PYEOF'
import pandas as pd
from pathlib import Path

xls_file = Path("Master_Phrase_Library.xlsx")
if xls_file.exists():
    df = pd.read_excel(xls_file, sheet_name="Master")
    print(f"✓ Database file exists: {xls_file.stat().st_size / 1024:.1f} KB")
    print(f"✓ Phrases in Master sheet: {len(df)} rows")
    print(f"✓ Columns: {list(df.columns)}")
    print("")
    if len(df) > 0:
        print("Sample data (first row):")
        print(f"  Section: {df.iloc[0]['Section']}")
        print(f"  Element: {df.iloc[0]['Element']}")
        print(f"  Content: {df.iloc[0]['Content'][:60]}...")
else:
    print("Database file not found")
PYEOF

echo ""
echo "========================================================================"
echo "✅ BASIC TESTS COMPLETE"
echo "========================================================================"
echo ""
echo "Next steps:"
echo "1. Check Master_Phrase_Library.xlsx to see imported phrases"
echo "2. Add your own Word documents and run test 2 again"
echo "3. For AI mining, set ANTHROPIC_API_KEY and add PDF reports"
echo ""
echo "See TESTING_GUIDE.md for detailed instructions"
echo ""
