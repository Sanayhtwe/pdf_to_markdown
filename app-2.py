import streamlit as st
import fitz  # PyMuPDF
import os
import pytesseract
from PIL import Image
from pdf2image import convert_from_path
import tempfile

st.set_page_config(page_title="PDF to Markdown Converter", page_icon="📄")

st.title("📄 PDF to Markdown Converter")
st.markdown("""
ဒီ app က PDF ဖိုင်တွေထဲက text တွေကို Markdown ဖိုင်အဖြစ် ပြောင်းလဲပေးမှာ ဖြစ်ပါတယ်။
""")

# Sidebar settings
st.sidebar.header("Settings")
use_ocr = st.sidebar.checkbox("Use OCR (For scanned PDFs)", value=False)
lang = st.sidebar.text_input("Tesseract Language (e.g., eng, mya)", value="eng")

uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")

def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text()
    return text

def extract_text_with_ocr(pdf_path, lang):
    images = convert_from_path(pdf_path)
    text = ""
    for i, image in enumerate(images):
        page_text = pytesseract.image_to_string(image, lang=lang)
        text += f"## Page {i+1}\n\n" + page_text + "\n\n"
    return text

if uploaded_file is not None:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        tmp_file.write(uploaded_file.getvalue())
        tmp_path = tmp_file.name

    st.info("Processing PDF...")
    
    try:
        if use_ocr:
            extracted_text = extract_text_with_ocr(tmp_path, lang)
        else:
            extracted_text = extract_text_from_pdf(tmp_path)
        
        if not extracted_text.strip():
            st.warning("No text found. Try enabling OCR in the settings.")
        else:
            st.subheader("Extracted Text Preview")
            st.text_area("Preview", extracted_text, height=300)
            
            # Create markdown content
            md_filename = os.path.splitext(uploaded_file.name)[0] + ".md"
            
            st.download_button(
                label="Download Markdown File",
                data=extracted_text,
                file_name=md_filename,
                mime="text/markdown"
            )
            st.success(f"Successfully processed {uploaded_file.name}!")

    except Exception as e:
        st.error(f"An error occurred: {e}")
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

st.sidebar.markdown("---")
st.sidebar.info("Note: Text-based PDFs are processed faster. OCR might take longer depending on the file size.")
