# Testing Guide - Phrase Library Engine

Complete testing instructions for all 4 core scripts.

---

## ✅ Test 1: Database Setup

**What it does:** Creates the Excel database with 7 worksheets and validation rules.

**Command:**
```bash
python 1_setup_database.py
```

**Expected Output:**
```
============================================================
PHRASE LIBRARY ENGINE - DATABASE SETUP
============================================================
Creating new workbook...
Creating Master sheet...
Added validation for 'Condition_Rating' (Column E)
Added validation for 'Property_Style' (Column F)
Added validation for 'Property_Type' (Column G)
Added validation for 'Property_Age' (Column H)
Master sheet created successfully
Creating 6 section sheets...
[... more sheet creation ...]
✓ Database file saved: /path/to/Master_Phrase_Library.xlsx
✓ File size: 11.01 KB
✓ Sheets created: Master, Section_D_External, Section_E_Internal, Section_F_Services, Section_G_Grounds, Sections_A-C_H_I_J_K, Building_Regulations
============================================================
DATABASE SETUP COMPLETE
============================================================
```

**Verify Success:**
```bash
# Check file was created
ls -lh Master_Phrase_Library.xlsx

# Open in Excel and verify:
# - 7 worksheets exist (tabs at bottom)
# - Headers are in row 1: Section, Element, Sub_Section, Content, etc.
# - Try typing in a cell under "Property_Style" - dropdown should appear
```

---

## ✅ Test 2: Word Document Import

**What it does:** Parses Word documents and extracts phrases into the database.

**Setup:**
```bash
# Create a test Word document (or use the sample)
# Place it in the project root folder
```

**Command:**
```bash
python 2_import_word_docs.py
```

**Expected Output:**
```
Processing sample_survey.docx...
  -> Found Element: Chimney Stacks (Sheet: Section_D_External)
  -> Found Element: Roof (Sheet: Section_D_External)
  -> Found Element: Walls (Sheet: Section_E_Internal)
  [... more elements ...]

Saving 12 phrases to Excel...
  -> Added 12 rows to 'Sections_A-C_H_I_J_K'

Success! Legacy phrases imported.
```

**Verify Success:**
```bash
# Open Master_Phrase_Library.xlsx
# Go to the sheet that matches the document content
# Check that rows were added with:
# - Section, Element, Sub_Section populated
# - Content contains the extracted text
# - Source_File shows the filename

# Example in Section_D_External:
# Row 2: Section=External | Element=Chimney Stacks | Content="The chimney stack..." | Source=sample.docx
```

**Test with Your Own Word Doc:**
```bash
# 1. Create/provide a Word document with headers like:
#    "External:" or "4.1 Chimney Stacks" or "D1 - Roof"
#    followed by descriptive text

# 2. Place it in /Users/Joe/JBS_PHRASES_BOOK/

# 3. Run:
python 2_import_word_docs.py --file "Your Document.docx"

# 4. Check Master_Phrase_Library.xlsx for new rows
```

---

## ✅ Test 3: Knowledge Bank Builder

**What it does:** Indexes reference documents (RICS, Building Regs) into JSON.

**Setup:**
```bash
# Add reference PDFs/DOCXs to USEFUL_DOCS/ folder
# Example files:
#   USEFUL_DOCS/RICS_Survey_Standard.pdf
#   USEFUL_DOCS/Building_Regulations.docx
#   USEFUL_DOCS/Technical_Guide.pdf
```

**Command:**
```bash
python 3_build_knowledge_bank.py
```

**Expected Output:**
```
======================================================================
PHRASE LIBRARY ENGINE - KNOWLEDGE BANK BUILDER
======================================================================

Scanning: /Users/Joe/JBS_PHRASES_BOOK/USEFUL_DOCS

   -> PDF: RICS_Survey_Standard.pdf
      ✓ Indexed: 45238 characters
   -> DOCX: Building_Regulations.docx
      ✓ Indexed: 32156 characters
   -> PDF: Technical_Guide.pdf
      ✓ Indexed: 28945 characters

======================================================================
✓ Knowledge Bank saved to 'knowledge_bank.json'
✓ Indexed 3 documents
======================================================================
```

**Verify Success:**
```bash
# Check knowledge_bank.json was created
ls -lh knowledge_bank.json

# Check contents
cat knowledge_bank.json | head -20

# Verify it's valid JSON
python -m json.tool knowledge_bank.json > /dev/null && echo "✓ Valid JSON"
```

---

## ✅ Test 4: AI Report Miner (Requires API Key)

**What it does:** Reads PDF reports, sends to Claude AI for extraction and anonymization.

### Prerequisites

1. **Get API Key:**
   - Go to https://console.anthropic.com/
   - Create/copy your API key
   - Keep it secure

2. **Set Environment Variable:**
   ```bash
   export ANTHROPIC_API_KEY="sk-ant-..."
   ```

3. **Verify API Key Works:**
   ```bash
   python << 'EOF'
   import anthropic
   client = anthropic.Anthropic()
   msg = client.messages.create(
       model="claude-3-5-haiku-20241022",
       max_tokens=100,
       messages=[{"role": "user", "content": "Say 'API works!'"}]
   )
   print(msg.content[0].text)
   EOF
   ```

   Should output: `API works!`

### Test the Miner

**Command:**
```bash
python 4_mine_reports.py
```

**Expected Output (First Run - No PDFs):**
```
======================================================================
PHRASE LIBRARY ENGINE - AI REPORT MINER
======================================================================

✓ Loaded knowledge bank with 3 reference documents

Created folder: /Users/Joe/JBS_PHRASES_BOOK/REPORTS_TO_MINE

Next steps:
1. Place your PDF reports in: /Users/Joe/JBS_PHRASES_BOOK/REPORTS_TO_MINE
2. Run this script again: python 4_mine_reports.py
```

**Test with Sample PDF:**

1. **Create a test PDF** (or use an existing survey report):
   ```bash
   # Copy a sample report to REPORTS_TO_MINE/
   cp ~/Documents/my_survey.pdf REPORTS_TO_MINE/test_survey.pdf
   ```

2. **Run the miner:**
   ```bash
   python 4_mine_reports.py
   ```

3. **Expected Output:**
   ```
   Mining: test_survey.pdf
      -> Extracting text from PDF...
      -> Extracted 12543 characters
      -> Sending to Claude AI (this may take 30s)...
      -> AI extracted 8 phrases
      ✓ Saved 8 phrases to Master Database

   ============================================================
   ✓ AI Report Mining Complete
   ============================================================
   ```

4. **Verify Success:**
   ```bash
   # Open Master_Phrase_Library.xlsx
   # Go to "Master" sheet
   # Check new rows with:
   # - AI-extracted content (should be generalized/anonymized)
   # - Property_Style, Property_Age auto-filled
   # - Condition_Rating filled (1, 2, or 3)
   # - Source_File shows "test_survey.pdf"
   ```

---

## 🧪 Full Integration Test

**Complete workflow test (5 minutes):**

```bash
# 1. Setup database
python 1_setup_database.py
# ✓ Creates Master_Phrase_Library.xlsx

# 2. Import a Word document
python 2_import_word_docs.py
# ✓ Adds phrases from legacy docs

# 3. Build knowledge bank
python 3_build_knowledge_bank.py
# ✓ Creates knowledge_bank.json

# 4. Mine a PDF (if you have API key)
export ANTHROPIC_API_KEY="your-key"
python 4_mine_reports.py
# ✓ Adds AI-extracted phrases

# 5. Verify the database
python << 'EOF'
import pandas as pd
df = pd.read_excel("Master_Phrase_Library.xlsx", sheet_name="Master")
print(f"Total phrases: {len(df)}")
print(f"\nColumns: {list(df.columns)}")
print(f"\nFirst entry:\n{df.iloc[0]}")
EOF
```

---

## ❌ Troubleshooting

### Script 1 (Database Setup)

**Error:** `No module named 'openpyxl'`
```bash
pip3 install openpyxl
```

**Error:** `Permission denied` when saving
```bash
# Make sure you're in a writable directory
cd /Users/Joe/JBS_PHRASES_BOOK
```

---

### Script 2 (Word Import)

**Error:** `No phrases found`
- Check document has text content
- Verify headers match patterns: "4.1 Chimney", "EXTERNAL:", "D1 - Roof"
- Ensure file is `.docx` (not `.doc` or `.docm`)

**No elements detected:**
```bash
# Add bold headers to your Word document
# Or text matching section names: EXTERNAL, INTERNAL, SERVICES
```

---

### Script 3 (Knowledge Bank)

**Error:** `No documents found`
```bash
# Make sure files are in USEFUL_DOCS/
ls USEFUL_DOCS/
```

**File not processed:**
- Only `.pdf` and `.docx` files supported
- `.doc` files need conversion to `.docx`

---

### Script 4 (AI Report Miner)

**Error:** `[ERROR] No API Key found!`
```bash
export ANTHROPIC_API_KEY="sk-ant-v..."
python 4_mine_reports.py
```

**Error:** `[Error] AI output was not valid JSON`
- Script sometimes returns non-JSON response
- Ensure PDF is text-based (not scanned image)
- Check API key is valid

**Timeout after 30 seconds:**
- API is slow (normal)
- Large PDFs take longer
- Check your internet connection

---

## 📊 Quick Validation Script

Run this to verify everything works:

```bash
python << 'EOF'
import os
import pandas as pd
from pathlib import Path

print("=" * 60)
print("PHRASE LIBRARY ENGINE - VALIDATION CHECK")
print("=" * 60)

# 1. Check Python files
scripts = [
    "1_setup_database.py",
    "2_import_word_docs.py",
    "3_build_knowledge_bank.py",
    "4_mine_reports.py",
    "config.py"
]

print("\n✓ Python Scripts:")
for script in scripts:
    if Path(script).exists():
        lines = len(open(script).readlines())
        print(f"  ✓ {script:30} ({lines} lines)")
    else:
        print(f"  ✗ {script:30} NOT FOUND")

# 2. Check database
print("\n✓ Database Files:")
if Path("Master_Phrase_Library.xlsx").exists():
    size = Path("Master_Phrase_Library.xlsx").stat().st_size / 1024
    print(f"  ✓ Master_Phrase_Library.xlsx ({size:.1f} KB)")
else:
    print("  ✗ Master_Phrase_Library.xlsx NOT FOUND")

# 3. Check folders
print("\n✓ Directories:")
for folder in ["USEFUL_DOCS", "REPORTS_TO_MINE"]:
    if Path(folder).exists():
        print(f"  ✓ {folder}")
    else:
        print(f"  ✗ {folder} NOT FOUND")

# 4. Check dependencies
print("\n✓ Dependencies:")
deps = ["pandas", "openpyxl", "python-docx", "pdfplumber"]
try:
    import anthropic
    deps.append("anthropic")
except:
    print("  ⚠ anthropic (optional, for AI mining)")

for dep in deps:
    try:
        __import__(dep.replace("-", "_"))
        print(f"  ✓ {dep}")
    except:
        print(f"  ✗ {dep} NOT INSTALLED")

print("\n" + "=" * 60)
print("✅ System Ready" if all(Path(s).exists() for s in scripts) else "⚠ Missing files")
print("=" * 60)
EOF
```

---

## 🎯 Success Criteria

| Test | Success Criteria |
|------|------------------|
| **Setup Database** | Master_Phrase_Library.xlsx created with 7 sheets, dropdowns work |
| **Word Import** | Phrases added to Excel with Section, Element, Content populated |
| **Knowledge Bank** | knowledge_bank.json created and contains indexed documents |
| **AI Report Miner** | Phrases extracted from PDF, anonymized, and added to Excel |
| **Full Integration** | Database grows with each script, no errors |

---

## 📝 Next Steps After Testing

1. **Add your real data:**
   - Place legacy Word documents in root folder
   - Add RICS/Building Regs to USEFUL_DOCS/
   - Add PDF reports to REPORTS_TO_MINE/

2. **Run in production:**
   ```bash
   python 2_import_word_docs.py  # Import your docs
   python 3_build_knowledge_bank.py  # Index your refs
   python 4_mine_reports.py  # Mine your PDFs
   ```

3. **Monitor the database:**
   - Open Master_Phrase_Library.xlsx
   - Check phrase count growing
   - Verify data quality

---

**Questions?** Check README.md or DEPLOYMENT_CHECKLIST.md for more details.
