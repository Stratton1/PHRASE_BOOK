"""
Configuration file for the Phrase Library Engine.
Contains all constants, schema definitions, and validation rules.
"""

# ============================================================================
# DATABASE CONFIGURATION
# ============================================================================

MASTER_DB_FILE = "Master_Phrase_Library.xlsx"
OUTPUT_FILE = MASTER_DB_FILE  # Alias for compatibility
MASTER_DB_SHEET_NAME = "Master"

# Sheet names for legacy document ingestion (as per JBS structure)
SECTIONS = [
    "Section_D_External",
    "Section_E_Internal",
    "Section_F_Services",
    "Section_G_Grounds",
    "Sections_A-C_H_I_J_K",
    "Building_Regulations"
]

# Original survey sections for reference
SURVEY_SECTIONS = [
    "External",
    "Internal",
    "Services",
    "Grounds",
    "Overall"
]

# ============================================================================
# COLUMN DEFINITIONS
# ============================================================================

STANDARD_COLUMNS = [
    "Section",
    "Element",
    "Sub_Section",
    "Content",
    "Condition_Rating",
    "Property_Style",
    "Property_Type",
    "Property_Age",
    "Source_File"
]

# Database columns (alias for compatibility with import scripts)
DB_COLUMNS = STANDARD_COLUMNS

# Column order for Excel export
COLUMN_ORDER = {col: idx for idx, col in enumerate(STANDARD_COLUMNS)}

# ============================================================================
# VALIDATION DOMAINS
# ============================================================================

# Condition ratings (severity levels)
CONDITION_RATINGS = [1, 2, 3]

# Property styles
PROPERTY_STYLES = [
    "Detached",
    "Semi-Detached",
    "Terrace",
    "Flat",
    "Bungalow"
]

# Property construction types
PROPERTY_TYPES = [
    "Traditional",
    "Non-Traditional"
]

# Property age bands (chronological)
PROPERTY_AGE_BANDS = [
    "Pre-1850",
    "1850-1899",
    "1900-1918",
    "1919-1945",
    "1946-1979",
    "1980-1999",
    "2000-2010",
    "2011-Present"
]

# ============================================================================
# FILE PROCESSING SETTINGS
# ============================================================================

# Supported document formats
SUPPORTED_WORD_FORMATS = [".doc", ".docx"]
SUPPORTED_PDF_FORMATS = [".pdf"]

# Regex patterns for parsing
HEADER_PATTERN = r"^#+\s+(.+)$"  # Markdown-style headers
SECTION_PATTERN = r"^(External|Internal|Services|Grounds|Overall):\s*(.+)$"

# ============================================================================
# LLM SETTINGS
# ============================================================================

# Anthropic API configuration (for PDF anonymization)
LLM_MODEL = "claude-3-5-sonnet-20241022"
LLM_TEMPERATURE = 0.3  # Lower temperature for consistency
LLM_MAX_TOKENS = 1000

# Anonymization patterns to remove
ANONYMIZATION_PATTERNS = {
    "address": r"\d+\s+[A-Za-z]+\s+(Street|Road|Avenue|Lane|Court|Close|Drive|Way)",
    "postcode": r"\b[A-Z]{1,2}\d{1,2}[A-Z]?\s?\d[A-Z]{2}\b",
    "phone": r"\b\d{4}\s?\d{6,7}\b|\b\d{10,11}\b",
    "name": r"\b[A-Z][a-z]+\s+[A-Z][a-z]+\b"  # Simple name pattern
}

# ============================================================================
# DATABASE CONSTRAINTS
# ============================================================================

# Maximum length for content fields (Excel limitation consideration)
MAX_CONTENT_LENGTH = 32767

# Minimum content length before adding to DB
MIN_CONTENT_LENGTH = 20

# ============================================================================
# LOGGING & ERROR HANDLING
# ============================================================================

LOG_LEVEL = "INFO"
VERBOSE_MODE = True
