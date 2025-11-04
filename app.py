import streamlit as st
import fitz  # PyMuPDF
import re
import pandas as pd

st.set_page_config(page_title="Analytical Reviewer", layout="wide")

st.title("🧪 Analytical Reviewer Assistant (Offline)")
st.write("Upload a research article PDF and get analytical review checks for HPLC, LC-MS, FTIR, and DSC.")

uploaded_file = st.file_uploader("Upload PDF file", type=["pdf"])

def extract_text(pdf_bytes):
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text("text")
    return text

def section_extract(text):
    # extract methods/experimental section roughly
    pattern = r"(?is)(materials and methods|methodology|experimental)(.*?)(results|discussion|conclusion)"
    match = re.search(pattern, text)
    return match.group(2) if match else text

def run_checks(method_text):
    checks = []

    # ---------- HPLC ----------
    if "hplc" in method_text.lower():
        if not re.search(r"column", method_text, re.I):
            checks.append(["HPLC", "Major", "Column details missing"])
        if not re.search(r"mobile phase", method_text, re.I):
            checks.append(["HPLC", "Major", "Mobile phase composition not reported"])
        if not re.search(r"flow", method_text, re.I):
            checks.append(["HPLC", "Minor", "Flow rate not specified"])
        if not re.search(r"wavelength", method_text, re.I):
            checks.append(["HPLC", "Minor", "Detection wavelength not specified"])
        if not re.search(r"system suitability", method_text, re.I):
            checks.append(["HPLC", "Critical", "System suitability not discussed"])

    # ---------- LC-MS ----------
    if "lc-ms" in method_text.lower() or "lc/ms" in method_text.lower():
        if not re.search(r"ionization", method_text, re.I):
            checks.append(["LC-MS", "Major", "Ionization mode not mentioned"])
        if not re.search(r"internal standard", method_text, re.I):
            checks.append(["LC-MS", "Critical", "Internal standard not used or reported"])
        if not re.search(r"matrix", method_text, re.I):
            checks.append(["LC-MS", "Major", "Matrix effect evaluation missing"])

    # ---------- FTIR ----------
    if "ftir" in method_text.lower():
        if not re.search(r"range", method_text, re.I):
            checks.append(["FTIR", "Minor", "Spectral range not specified"])
        if not re.search(r"peak", method_text, re.I):
            checks.append(["FTIR", "Major", "Peak assignment missing or incomplete"])

    # ---------- DSC ----------
    if "dsc" in method_text.lower():
        if not re.search(r"heating rate", method_text, re.I):
            checks.append(["DSC", "Minor", "Heating rate not specified"])
        if not re.search(r"melting", method_text, re.I):
            checks.append(["DSC", "Major", "Melting point/transition not reported"])

    df = pd.DataFrame(checks, columns=["Technique", "Severity", "Issue"])
    return df if not df.empty else None

if uploaded_file:
    with st.spinner("Extracting and analyzing..."):
        text = extract_text(uploaded_file.read())
        method_text = section_extract(text)
        results = run_checks(method_text)

    st.subheader("📄 Extracted Methods Section (preview)")
    st.text_area("Methods Section", method_text[:3000] + "...", height=300)

    st.subheader("🧩 Analytical Review Findings")
    if results is not None:
        st.dataframe(results)
        csv = results.to_csv(index=False).encode("utf-8")
        st.download_button("⬇️ Download Findings (CSV)", csv, "review_findings.csv", "text/csv")
    else:
        st.success("No major issues detected with the basic rule set ✅")

st.markdown("---")
st.caption("Offline Analytical Reviewer • Version 1.0")

