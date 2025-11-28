import streamlit as st
import numpy as np
import pandas as pd
from PIL import Image
import pytesseract

# ==============================
# APP TITLE
# ==============================
st.set_page_config(page_title="OCR App", layout="wide")
st.title("📄 Optical Character Recognition (OCR) Web App")
st.write("Upload gambar, dan sistem akan membaca teks secara otomatis.")

# ==============================
# FILE UPLOADER
# ==============================
uploaded_file = st.file_uploader("Upload file gambar", type=["png", "jpg", "jpeg"])

if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, caption="📌 Gambar yang diupload", use_column_width=True)
    st.subheader("🔍 Hasil OCR:")

    # ==============================
    # OCR PROCESS
    # ==============================
    try:
        extracted_text = pytesseract.image_to_string(image)
        st.text_area("Teks yang terbaca:", extracted_text, height=300)

        # Convert to dataframe if needed
        df = pd.DataFrame({"Recognized Text":[extracted_text]})
        st.download_button("⬇ Download sebagai TXT", extracted_text, "ocr_output.txt")
        st.download_button("⬇ Download sebagai CSV", df.to_csv(index=False), "ocr_output.csv")

    except Exception as e:
        st.error("Terjadi error saat memproses OCR ❗")
        st.write(e)
else:
    st.info("Silakan upload gambar terlebih dahulu untuk mulai OCR.")
