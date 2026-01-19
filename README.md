# Phrase Library Engine - JBS Surveys

An automated system to build a searchable, AI-powered phrase library from your survey documents, legacy Word templates, and PDF reports.

## 📁 Project Structure

```
JBS_PHRASES_BOOK/
├── config.py                          # Central configuration (DO NOT EDIT)
├── Master_Phrase_Library.xlsx         # Main database (auto-generated)
├── knowledge_bank.json                # AI reference context (auto-generated)
│
├── 1_setup_database.py               # Initialize Excel database
├── 2_import_word_docs.py             # Import legacy Word documents
├── 3_build_knowledge_bank.py         # Index reference documents
├── 4_mine_reports.py                 # AI-powered PDF extraction
│
├── USEFUL_DOCS/                      # Reference documents for AI context
│   ├── RICS DOCUMENTS/               # RICS survey standards
│   ├── BUILDING PATHOLOGY/           # Technical guides
│   └── TEMPLATES/                    # Templates
│
└── REPORTS_TO_MINE/                  # Your old PDF reports
    └── [Place survey PDFs here]
```

## 🚀 Quick Start

### Step 1: Initialize Database
```bash
python 1_setup_database.py
```
Creates `Master_Phrase_Library.xlsx` with 7 worksheets:
- **Master**: Central repository
- **Section_D_External**: Roof, chimneys, walls, etc.
- **Section_E_Internal**: Floors, ceilings, plumbing
- **Section_F_Services**: Electrical, heating, water
- **Section_G_Grounds**: Gardens, drives, fencing
- **Sections_A-C_H_I_J_K**: General/legal/summary info
- **Building_Regulations**: Compliance notes

### Step 2: Import Legacy Word Documents
Place your Word documents in the project folder, then:
```bash
python 2_import_word_docs.py
```
The script automatically:
- Detects section headers (EXTERNAL, INTERNAL, etc.)
- Extracts elements (Chimney Stacks, Roof, etc.)
- Maps to correct Excel sheets
- Handles "Fast Texts" format (4.1 Chimney Stacks)
- Removes duplicates

### Step 3: Build AI Knowledge Bank
Place your reference documents in `USEFUL_DOCS/`:
```bash
python 3_build_knowledge_bank.py
```
This creates `knowledge_bank.json` containing indexed RICS rules and building standards. The AI uses this for context.

### Step 4: Mine PDF Reports (Requires API Key)
1. Get Anthropic API key: https://console.anthropic.com/
2. Set environment variable:
   ```bash
   export ANTHROPIC_API_KEY="sk-ant-..."
   ```
3. Place PDF reports in `REPORTS_TO_MINE/`
4. Run:
   ```bash
   python 4_mine_reports.py
   ```

The AI will:
- Extract observations from PDFs
- Anonymize (remove addresses, postcodes, names)
- Classify by age/style/condition
- Add to Master_Phrase_Library.xlsx

---

## 📊 Database Schema

All phrases are stored with these 9 columns:

| Column | Values | Example |
|--------|--------|---------|
| **Section** | External, Internal, Services, Grounds, Overall | External |
| **Element** | Property component | Chimney Stacks |
| **Sub_Section** | Aspect type | Defects |
| **Content** | Description (anonymized) | "The stack shows deterioration..." |
| **Condition_Rating** | 1 (Good), 2 (Fair), 3 (Poor) | 2 |
| **Property_Style** | Detached, Semi-Detached, Terrace, Flat, Bungalow | Semi-Detached |
| **Property_Type** | Traditional, Non-Traditional | Traditional |
| **Property_Age** | 8 bands from Pre-1850 to 2011-Present | 1900-1918 |
| **Source_File** | Original filename | Fast Texts.docx |

---

## 🔧 Configuration

Edit `config.py` to customize:
- Output file name
- Excel sheet names
- Validation domains (age bands, styles)
- Anonymization patterns
- LLM model and settings

---

## 🤖 AI Report Mining Details

### Models Available
- **claude-3-5-haiku-20241022**: Fast, cheap (default)
- **claude-3-5-sonnet-20241022**: More capable
- **claude-opus-4-5-20251101**: Most powerful

### What the AI Does
1. **Extracts** all observations from your PDF
2. **Anonymizes** (removes: addresses, postcodes, names, dates)
3. **Generalizes** ("12 High St" → "the property")
4. **Classifies** by Section, Element, Condition
5. **Infers** Property Age and Style from context
6. **Validates** against RICS standards from knowledge bank

### Example Anonymization
**Before**: "The roof at 23 Smith Lane, London SW1A 1AA, needs work. Mr. Jones reported..."
**After**: "The main roof covering requires attention due to deterioration."

---

## 📝 Troubleshooting

### No API Key Error
```
[ERROR] No API Key found!
```
**Solution**:
```bash
export ANTHROPIC_API_KEY="your-key-here"
```
Then run the script again.

### "knowledge_bank.json not found"
**Solution**: Run `python 3_build_knowledge_bank.py` first, or place reference documents in `USEFUL_DOCS/`

### PDF Extraction Fails
- Ensure PDF is not password-protected
- Check PDF is readable by Adobe/Preview
- Try a different PDF file

### Excel File Locked Error
- Close the Excel file
- Don't run multiple scripts simultaneously
- Wait 2 seconds before re-running

---

## 📚 Data Sources for USEFUL_DOCS

To maximize AI accuracy, add these to `USEFUL_DOCS/`:

1. **RICS Standards**
   - RICS Survey Report Content and Guidance Notes
   - Home Survey Report Standard

2. **Building Regulations**
   - Building Regulations Approved Documents
   - Building Safety Act guidance

3. **Technical Guides**
   - Defect definitions and classifications
   - Common problems by property age
   - Remedial action standards

---

## 🔒 Privacy & Anonymization

The AI automatically removes:
- Full addresses (keeps just building type)
- Postcodes
- Personal names
- Specific dates (replaces with "recently")
- Client/property-identifying information

**You control what goes in** - only send reports you own/manage.

---

## 📊 Next Steps

After building your phrase library, you can:
1. **Export to Streamlit dashboard** for searching/filtering
2. **Generate reports** by selecting phrases
3. **Train models** on your standardized language
4. **Integrate with survey software** for auto-population

---

## 🐛 Version Info

- Python: 3.9+
- Dependencies: pandas, openpyxl, python-docx, pdfplumber, anthropic
- Created: 2025-01-19
- Status: Production Ready

---

## 📧 Support

For issues or improvements, check:
- Script comments and docstrings
- config.py for adjustable parameters
- Knowledge bank content for AI accuracy

---
