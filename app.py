import streamlit as st
from google.genai import Client
from PIL import Image
import os, json, re

st.title("🍽 Eatalyze — Nutrition OCR Analyzer")
st.write("Upload label makanan → Extract → Output JSON → Hitung nutrisi per 1g")

# 🔥 AUTO LOAD API KEY DARI RAILWAY
API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    st.error("❌ ENV `GEMINI_API_KEY` tidak ditemukan di Railway!")
    st.stop()

client = Client(api_key=API_KEY)

# ======================================================
#  UPLOAD GAMBAR
# ======================================================
uploaded_file = st.file_uploader("Upload Gambar Nutrition Label", type=["jpg","jpeg","png"])

if uploaded_file:
    st.subheader("📸 Preview Gambar")
    st.image(uploaded_file, use_column_width=True)

    try:
        img = Image.open(uploaded_file)

        prompt = (
            "Extract nutrition from the image and output ONLY a JSON object.\n"
            "Keys: serving-size, energy-kcal, fat, saturated-fat, trans-fat, carbohydrates,"
            "sugars, added-sugars, protein, fiber, sodium, salt.\n"
            "If a value is not available return 0.\n"
            "Convert mg to g automatically.\n"
        )

        result = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[prompt, img]
        )

        raw = result.text.strip().replace("```json","").replace("```","").strip()

        st.subheader("📥 OCR JSON Output")
        st.code(raw, language="json")

        data = json.loads(raw)

        # ========== Extract Serving Size ==========
        sv = re.findall(r"\d+", str(data.get("serving-size","0")))
        serving = int(sv[0]) if sv else 1

        # ========== Nutrition per 1 gram ==========
        nutr_per_gram = {}
        for k,v in data.items():
            if k == "serving-size":
                continue
            try:
                txt = str(v).lower()
                val = float(txt.replace("mg",""))/1000 if "mg" in txt else float(txt)
                nutr_per_gram[k+"_per_1g"] = round(val/serving,3)
            except:
                nutr_per_gram[k+"_per_1g"] = 0

        st.subheader("📊 Nutrition Value per 1g")
        st.json(nutr_per_gram)

    except Exception as e:
        st.error(f"❌ Error saat proses OCR: {e}")

else:
    st.info("Upload gambar nutrition label untuk mulai analisis.")
