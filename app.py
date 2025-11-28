import streamlit as st
import google.generativeai as genai
from PIL import Image
import re, json

st.set_page_config(page_title="Nutrition OCR Analyzer", page_icon="🍽", layout="centered")
st.title("Nutrition OCR Analyzer using Gemini AI")
st.write("Upload nutrition facts image → Extract values → Auto normalize / calculate per 1g")

# ========================= UI INPUT =========================
api_key = st.text_input("Masukkan API Key", type="password")
uploaded_file = st.file_uploader("Upload gambar nutrisi (jpg/png)", type=["png","jpg","jpeg"])

# ========================= PROCESS =========================
if uploaded_file and api_key:
    image = Image.open(uploaded_file)
    st.image(image, caption="Gambar yang dianalisis", use_column_width=True)

    genai.configure(api_key=api_key)

    prompt = (
        "Transcribe the nutrition facts table in this image and output the data "
        "as a single JSON object. Keys must include 'serving-size', 'energy-kcal', "
        "'fat', 'carbohydrates', 'proteins', 'saturated-fat', 'trans-fat', 'sugars', "
        "'added-sugars', 'sodium', 'salt', and 'fiber'. "
        "Missing values = 0. Convert mg → g so all values are grams."
    )

    st.info("Processing OCR with Gemini...")

    try:
        response = genai.GenerativeModel("gemini-2.5-flash").generate_content([prompt, image])
        data_raw = response.text

        # ==================== CLEAN JSON ====================
        cleaned = (
            data_raw.replace("```json", "")
                    .replace("```", "")
                    .strip()
        )

        # tampilkan output JSON mentah
        st.subheader("Hasil Ekstraksi Raw JSON")
        st.code(cleaned, language="json")

        # convert to dict
        nutrition = json.loads(cleaned)

        # ==================== NORMALIZE PER 1 GRAM ====================
        serving = float(re.findall(r"[0-9]+", str(nutrition.get("serving-size", "1")))[0])

        result_per_gram = {
            key + "_1g": round(float(value) / serving, 3) if key != "serving-size" else serving
            for key, value in nutrition.items()
        }

        st.subheader("Nilai Nutrisi per 1 gram")
        st.json(result_per_gram)

    except Exception as e:
        st.error(f"Error saat memproses OCR: {e}")

else:
    st.warning("Masukkan API Key + Upload gambar dulu ya")
