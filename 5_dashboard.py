"""
Module F: The Dashboard
Interactive Streamlit interface for searching and browsing the Phrase Library.

Run: streamlit run 5_dashboard.py
"""

import streamlit as st
import pandas as pd
import os
from config import OUTPUT_FILE, STANDARD_COLUMNS

# Page Configuration
st.set_page_config(
    page_title="STRUCTURA Dashboard",
    layout="wide",
    page_icon="🏗️",
    initial_sidebar_state="expanded"
)

# Custom Styling
st.markdown("""
    <style>
    .main {
        background-color: #f8f9fa;
    }
    .stTextInput > div > div > input {
        border-radius: 10px;
        padding: 12px;
    }
    h1 {
        color: #2c3e50;
        font-weight: 700;
    }
    h2 {
        color: #34495e;
        border-bottom: 2px solid #3498db;
        padding-bottom: 10px;
    }
    .stDataEditor {
        border: 1px solid #ddd;
        border-radius: 5px;
    }
    .metric-card {
        background-color: white;
        padding: 20px;
        border-radius: 8px;
        border-left: 4px solid #3498db;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    </style>
    """, unsafe_allow_html=True)


def load_data():
    """Load the Master Sheet from Excel database."""
    if not os.path.exists(OUTPUT_FILE):
        return None
    try:
        # Load the 'Master' sheet which contains all aggregated phrases
        df = pd.read_excel(OUTPUT_FILE, sheet_name='Master')
        # Ensure consistent string types for searching and fill NaNs
        df = df.fillna("")
        df = df.astype(str)
        return df
    except Exception as e:
        st.error(f"Error loading database: {e}")
        return None


def format_display_columns(df):
    """Reorder columns for better display."""
    display_order = [
        'Content',
        'Section',
        'Element',
        'Sub_Section',
        'Condition_Rating',
        'Property_Style',
        'Property_Age',
        'Source_File'
    ]
    # Keep only columns that exist
    display_cols = [col for col in display_order if col in df.columns]
    return df[display_cols]


def main():
    # Header
    st.title("🏗️ STRUCTURA | Intelligent Survey Engine")
    st.markdown("**Searchable Phrase Library for Survey Reports**")
    st.divider()

    # Load Data
    df = load_data()

    if df is None:
        st.error(f"❌ Database ({OUTPUT_FILE}) not found!")
        st.warning("Please run `python 1_setup_database.py` first to create the database.")
        st.info("""
        Quick start:
        1. Run: `python 1_setup_database.py`
        2. Run: `python 2_import_word_docs.py`
        3. Then come back here!
        """)
        return

    # Create layout: Sidebar + Main
    with st.sidebar:
        st.header("🔍 Search & Filter")

        # Search Box (Primary Interface)
        search_query = st.text_input(
            "🔎 Search Phrases",
            placeholder="e.g., 'Chimney lean', 'Roof defects', 'Damp'",
            help="Search across all phrase content"
        )

        st.divider()

        # Filter Dropdowns
        st.subheader("Filters")

        # Extract unique values and sort
        sections = sorted([x for x in df['Section'].unique() if x and str(x).lower() != 'nan'])
        selected_section = st.selectbox(
            "📋 Section",
            ["All"] + sections,
            help="Filter by survey section"
        )

        elements = sorted([x for x in df['Element'].unique() if x and str(x).lower() != 'nan'])
        selected_element = st.selectbox(
            "🏠 Element",
            ["All"] + elements,
            help="Filter by building element"
        )

        ages = sorted([x for x in df['Property_Age'].unique() if x and str(x).lower() != 'nan'])
        selected_age = st.selectbox(
            "📅 Property Age",
            ["All"] + ages,
            help="Filter by property age band"
        )

        styles = sorted([x for x in df['Property_Style'].unique() if x and str(x).lower() != 'nan'])
        selected_style = st.selectbox(
            "🏘️  Property Style",
            ["All"] + styles,
            help="Filter by property style"
        )

        st.divider()

        # Statistics
        st.subheader("📊 Statistics")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Phrases", len(df))
        with col2:
            unique_sources = len(df['Source_File'].unique())
            st.metric("Source Files", unique_sources)

        st.caption("STRUCTURA v1.0")
        st.caption("Phrase Library Engine")

    # Apply Filters
    df_filtered = df.copy()

    # Search filter (primary)
    if search_query:
        # Search across multiple columns
        mask = (
            df_filtered['Content'].str.contains(search_query, case=False, na=False) |
            df_filtered['Element'].str.contains(search_query, case=False, na=False) |
            df_filtered['Sub_Section'].str.contains(search_query, case=False, na=False)
        )
        df_filtered = df_filtered[mask]

    # Dimension filters
    if selected_section != "All":
        df_filtered = df_filtered[df_filtered['Section'] == selected_section]

    if selected_element != "All":
        df_filtered = df_filtered[df_filtered['Element'] == selected_element]

    if selected_age != "All":
        df_filtered = df_filtered[df_filtered['Property_Age'] == selected_age]

    if selected_style != "All":
        df_filtered = df_filtered[df_filtered['Property_Style'] == selected_style]

    # Main Content Area
    st.subheader(f"📄 Results ({len(df_filtered)} phrases)")

    if not df_filtered.empty:
        # Reorder columns for display
        df_display = format_display_columns(df_filtered)

        # Display table
        st.dataframe(
            df_display,
            column_config={
                "Content": st.column_config.TextColumn(
                    "Phrase Content",
                    width="large",
                    help="The extracted/written phrase"
                ),
                "Section": st.column_config.TextColumn(
                    "Section",
                    width="small"
                ),
                "Element": st.column_config.TextColumn(
                    "Element",
                    width="medium"
                ),
                "Sub_Section": st.column_config.TextColumn(
                    "Sub-Section",
                    width="small"
                ),
                "Condition_Rating": st.column_config.TextColumn(
                    "Rating",
                    width="small",
                    help="1=Good, 2=Fair, 3=Poor"
                ),
                "Property_Style": st.column_config.TextColumn(
                    "Style",
                    width="small"
                ),
                "Property_Age": st.column_config.TextColumn(
                    "Age",
                    width="medium"
                ),
                "Source_File": st.column_config.TextColumn(
                    "Source",
                    width="small"
                ),
            },
            hide_index=True,
            use_container_width=True,
            height=600,
            disabled=True  # Set to False if you want to edit cells directly
        )

        # Export options
        st.divider()
        col1, col2, col3 = st.columns(3)

        with col1:
            csv = df_display.to_csv(index=False)
            st.download_button(
                label="📥 Download CSV",
                data=csv,
                file_name="phrases_export.csv",
                mime="text/csv"
            )

        with col2:
            excel_buffer = pd.ExcelWriter(index=False)
            df_display.to_excel(excel_buffer, index=False)
            st.download_button(
                label="📥 Download Excel",
                data=excel_buffer.to_csv(),
                file_name="phrases_export.xlsx"
            )

        with col3:
            st.info(f"**{len(df_filtered)}** phrases selected")

    else:
        # No results
        st.warning("⚠️  No phrases match your search criteria.")
        st.info("""
        **Try:**
        - Using different keywords
        - Removing some filters
        - Checking the database has been populated with phrases

        **To add phrases:**
        1. Run: `python 2_import_word_docs.py`
        2. Run: `python 4_mine_reports.py` (requires API key)
        """)

    # Footer
    st.divider()
    st.markdown("""
    ---
    **STRUCTURA Dashboard** | Survey Phrase Library Engine
    [GitHub](https://github.com/Stratton1/PHRASE_BOOK) |
    [Documentation](https://github.com/Stratton1/PHRASE_BOOK/blob/main/README.md)
    """)


if __name__ == "__main__":
    main()
