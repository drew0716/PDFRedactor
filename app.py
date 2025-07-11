
import streamlit as st
import fitz  # PyMuPDF
import re
import tempfile
from io import BytesIO
from claude_helper import get_sensitive_terms_with_claude
import os
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode

APP_TITLE = "🛡️ RedactIQ"
THEME_COLOR = "#175177"
LOGO_URL = "https://upload.wikimedia.org/wikipedia/commons/thumb/1/17/Font_Awesome_5_regular_user-shield.svg/512px-Font_Awesome_5_regular_user-shield.svg.png"

st.set_page_config(page_title=APP_TITLE, layout="wide")

CLAUDE_API_KEY = st.secrets.get("claude_api_key")

def find_pii(text, page_num):
    patterns = {
        "Email address": r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+",
        "Phone number": r"\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}",
        "SSN": r"\b\d{3}-\d{2}-\d{4}\b",
        "Credit card": r"\b(?:\d[ -]*?){13,16}\b"
    }
    results = []
    for reason, pattern in patterns.items():
        matches = re.findall(pattern, text)
        for match in matches:
            results.append({"Text": match, "Reason": reason, "Page": page_num})
    return results

def extract_pages(pdf_path):
    doc = fitz.open(pdf_path)
    pages = []
    for i, page in enumerate(doc):
        text = page.get_text()
        pages.append({
            "page_num": i + 1,
            "text": text,
            "fitz_page": page
        })
    return pages

def classify_risk(reason: str) -> str:
    reason = reason.lower()
    if "ssn" in reason or "credit" in reason or "account" in reason:
        return "🔴 High"
    elif "phone" in reason or "email" in reason:
        return "🟡 Medium"
    else:
        return "🟢 Low"

def redact_terms(pdf_path, redactions):
    doc = fitz.open(pdf_path)
    for i, page in enumerate(doc):
        try:
            page_redactions = [r["Text"] for r in redactions if int(float(r["Page"])) == i + 1]
        except Exception:
            continue
        for term in set(page_redactions):
            areas = page.search_for(term)
            for area in areas:
                page.add_redact_annot(area, fill=(0, 0, 0))
        page.apply_redactions()
    redacted_bytes = BytesIO()
    doc.save(redacted_bytes)
    redacted_bytes.seek(0)
    doc.close()
    return redacted_bytes

@st.cache_data(show_spinner=False)
def cached_claude_redactions(text, page_num):
    return get_sensitive_terms_with_claude(text, page_num)

st.markdown(f"<div style='display: flex; align-items: center; gap: 15px;'>"
            f"<h1 style='color:{THEME_COLOR}; margin-bottom: 0;'>{APP_TITLE}</h1></div>", unsafe_allow_html=True)
st.markdown("<p style='font-size:1.2em; color:gray;'>Your AI-powered privacy assistant for clean, compliant documents</p>", unsafe_allow_html=True)
st.markdown("---")

st.markdown("""
**Instructions:**
1. Upload a PDF containing potentially sensitive information.
2. Optionally enable AI-enhanced redaction detection.
3. Review all detected items in the interactive table.
4. Confirm redactions and download the cleaned PDF.
""")

st.markdown("### 📄 Upload Your PDF")
uploaded_file = st.file_uploader("Drag & drop or click to upload", type=["pdf"])
use_claude = st.checkbox("🤖 Use Claude AI for deeper redaction suggestions")

if uploaded_file:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(uploaded_file.read())
        temp_path = tmp.name

    st.success("✅ File uploaded successfully")
    pages = extract_pages(temp_path)

    all_redactions = []

    for page in pages:
        page_num = page["page_num"]
        text = page["text"]

        regex_results = find_pii(text, page_num)
        claude_results = []
        if use_claude and CLAUDE_API_KEY:
            with st.spinner(f"Claude scanning page {page_num}..."):
                try:
                    raw_claude = cached_claude_redactions(text, page_num)
                    claude_results = [{"Text": r["Text"], "Reason": r["Reason"], "Page": int(page_num)} for r in raw_claude]
                except Exception as e:
                    st.error(f"Claude error on page {page_num}: {e}")

        all_redactions.extend(regex_results + claude_results)

    if not all_redactions:
        st.warning("No sensitive terms were detected.")
    else:
        st.markdown("### 🔍 Redaction Review")

        df = pd.DataFrame(all_redactions)
        df = df[["Text", "Reason", "Page"]].copy()
        df["Page"] = pd.to_numeric(df["Page"], errors="coerce").fillna(-1).astype(int)
        df.drop_duplicates(inplace=True)
        df["Risk"] = df["Reason"].apply(classify_risk)

        # Add column for AgGrid selection
        df["Selected"] = True

        # Reorder columns
        df = df[["Text", "Page", "Risk", "Reason", "Selected"]]

        gb = GridOptionsBuilder.from_dataframe(df)
        gb.configure_column("Selected", headerCheckboxSelection=True, checkboxSelection=True, editable=True, width=90, pinned="left")
        gb.configure_column("Text", width=300)
        gb.configure_column("Page", header_name="Page #", width=100)
        gb.configure_column("Reason", width=200)
        gb.configure_column("Risk", width=100)
        gb.configure_default_column(filterable=True, sortable=True, resizable=True)
        gb.configure_pagination(enabled=True, paginationAutoPageSize=True)
        grid_options = gb.build()

        grid_response = AgGrid(
            df,
            gridOptions=grid_options,
            update_mode=GridUpdateMode.VALUE_CHANGED,
            height=600,
            theme="alpine",
            fit_columns_on_grid_load=True,
            allow_unsafe_jscode=True,
        )

        updated_df = grid_response["data"]
        selected_redactions = updated_df[updated_df["Selected"] == True].copy()

        st.markdown("### 🔏 Apply and Download")
        if st.button("Apply Redactions", type="primary"):
            if selected_redactions.empty:
                st.warning("Please select at least one item to redact.")
            else:
                redacted_pdf = redact_terms(temp_path, selected_redactions.to_dict(orient="records"))
                st.success("✅ Redactions applied successfully!")
                st.download_button("⬇️ Download Redacted PDF", data=redacted_pdf, file_name="redacted_output.pdf")

    try:
        os.remove(temp_path)
    except Exception:
        pass
