import streamlit as st
from google.genai import Client
from PIL import Image
import json, re

st.title("🍽 Eatalyze — Nutrition OCR Analyzer")
st.write("Upload label → Preview → Extract → Convert to JSON → Hitung per 1g")

# ==========================================
# Input API Key dari User (aman tidak hardcode)
# ==========================================
api_key = st.text_input("Masukkan Google Gemini API Key", type="password")

# ==========================================
# Upload Gambar
# ==========================================
uploaded_file = st.file_uploader("Upload Gambar Label", type=["png","jpg","jpeg"])

if uploaded_file:
    st.subheader("📸 Preview Gambar")
    st.image(uploaded_file, use_column_width=True)

# Run OCR jika API key dan gambar sudah masuk
if api_key and uploaded_file:
    try:
        img = Image.open(uploaded_file)
        client = Client(api_key=api_key)

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

        # =============================
        # Output JSON mentahan
        # =============================
        st.subheader("📥 JSON Nutrition (OCR Result)")
        st.code(raw, language="json")

        # Load JSON ke python dict
        data = json.loads(raw)

        # Ambil serving size untuk normalisasi
        serving_value = re.findall(r"\d+", str(data.get("serving-size","0")))
        serving = int(serving_value[0]) if serving_value else 1

        # =============================
        # Perhitungan nilai per gram
        # =============================
        nutr_per_gram = {}
        for k,v in data.items():
            if k=="serving-size":
                continue
            try:
                # Convert mg → g jika perlu
                txt = str(v).lower()
                val = float(txt.replace("mg",""))/1000 if "mg" in txt else float(txt)
                nutr_per_gram[k+"_per_1g"] = round(val/serving,3)
            except:
                nutr_per_gram[k+"_per_1g"]=0

        st.subheader("📊 Nutrition Converted Per 1g")
        st.json(nutr_per_gram)

    except Exception as e:
        st.error(f"❌ Error: {e}")

else:
    st.info("Masukkan API Key & upload gambar untuk mulai.")
