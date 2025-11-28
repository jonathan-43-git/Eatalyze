import streamlit as st
import google.genai as genai
from PIL import Image
import json, re, io

# ==============================
#        UI STREAMLIT
# ==============================
st.title("🍽 Nutrition OCR - Eatalyze")
st.write("Upload label makanan → sistem ekstrak tulisan → hasil dalam JSON")

# Input API Key aman (tidak ditulis di kode)
api_key = st.text_input("Masukkan Google Gemini API Key", type="password")

# Upload image
uploaded_file = st.file_uploader("Upload Gambar Label", type=["png", "jpg", "jpeg"])

if api_key and uploaded_file:
    try:
        img = Image.open(uploaded_file)

        # ==============================
        #        PROSES OCR + JSON
        # ==============================
        client = genai.Client(api_key=api_key)

        prompt = (
            "Extract nutrition facts from the image and return as a JSON object only.\n"
            "Keys: serving-size, energy-kcal, fat, saturated-fat, trans-fat, carbohydrates,"
            "sugars, added-sugars, protein, fiber, sodium, salt.\n"
            "If missing, value = 0. Convert mg → g."
        )

        result = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[prompt, img]
        )

        raw = result.text.strip()
        raw = raw.replace("```json", "").replace("```", "").strip()

        st.subheader("📥 Hasil OCR (Raw JSON)")
        st.code(raw, language="json")

        # ==============================
        #      Normalisasi + per-gram
        # ==============================
        data = json.loads(raw)
        result_per_gram = {}

        serving_text = str(data.get("serving-size","0")).lower()
        serving_num = re.findall(r"(\d+)", serving_text)
        serving = int(serving_num[0]) if serving_num else 1  # avoid crash

        for key,value in data.items():
            if key=="serving-size": 
                continue
            try:
                v=str(value).replace("mg","")
                v=float(v)/1000 if "mg" in str(value) else float(v)
                result_per_gram[key+"_per_1g"]=round(v/serving,3)
            except:
                result_per_gram[key+"_per_1g"]=0

        st.subheader("📊 Nutrition per 1g")
        st.json(result_per_gram)

    except Exception as e:
        st.error(f"Gagal memproses: {e}")

else:
    st.info("Masukkan API key & upload gambar untuk mulai")
