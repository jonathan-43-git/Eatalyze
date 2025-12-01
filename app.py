import streamlit as st
from google.genai import Client
from PIL import Image
import os, json, re

st.title("🍽 Eatalyze — Nutrition OCR Analyzer")
st.write("Upload → Extract → JSON → Hitung nutrisi per 1g")

# ======================================================
# 🔥 Auto Ambil API KEY dari Railway
# ======================================================
API_KEY = os.getenv("GEMINI_API_KEY") 

if not API_KEY:
    st.error("❌ ENV GEMINI_API_KEY tidak ditemukan di Railway!")
    st.stop()
else:
    st.success("🔑 API Key Loaded from Railway ✔")

# ======================================================
# Upload Gambar
# ======================================================
uploaded_file = st.file_uploader("Upload Nutrition Label", type=["jpg","jpeg","png"])

if uploaded_file:
    st.image(uploaded_file, use_column_width=True)

if uploaded_file:
    try:
        img = Image.open(uploaded_file)
        client = Client(api_key=API_KEY)

        prompt = (
            "Extract nutrition from the image and output ONLY a JSON object.\n"
            "Keys: serving-size, energy-kcal, fat, saturated-fat, trans-fat, carbohydrates,"
            "sugars, added-sugars, protein, fiber, sodium, salt.\n"
            "If missing return 0.\nConvert mg > g correctly.\n"
        )

        result = client.models.generate_content(model="gemini-2.5-flash", contents=[prompt, img])

        raw = result.text.strip().replace("```json","").replace("```","").strip()
        st.code(raw, language="json")

        data = json.loads(raw)

        sv = re.findall(r"\d+", str(data.get("serving-size","0")))
        serving = int(sv[0]) if sv else 1

        nutr_per_gram = {}
        for k,v in data.items():
            if k!="serving-size":
                val = str(v).lower()
                val = float(val.replace("mg",""))/1000 if "mg" in val else float(val)
                nutr_per_gram[k+"_per_1g"] = round(val/serving,3)

        st.subheader("📊 Nutrisi per 1g")
        st.json(nutr_per_gram)

    except Exception as e:
        st.error(f"❌ Error OCR: {e}")
else:
    st.info("Upload gambar untuk mulai analisis.")
