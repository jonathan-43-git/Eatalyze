import streamlit as st
from google import genai
from PIL import Image
import json, re, io

st.title("📦 Nutrition Facts OCR + Gemini Parser")
st.write("Upload gambar *Nutrition Facts*, app akan mengekstrak lalu menghitung nutrisi per 1 gram.")

# ===== Input API Key =====
api_key = st.text_input("Masukkan API Key Google AI (tidak disimpan):", type="password")

uploaded_file = st.file_uploader("Upload gambar (JPEG/PNG):", type=["jpg","jpeg","png"])

# ================== PROSES ==================
if st.button("Proses OCR & Ekstraksi"):

    if not api_key:
        st.error("❗ API KEY belum diisi.")
        st.stop()

    if uploaded_file is None:
        st.error("❗ Upload gambar terlebih dahulu.")
        st.stop()

    client = genai.Client(api_key=api_key)

    # Baca gambar
    image = Image.open(uploaded_file)

    # Prompt ke Gemini
    prompt = (
        "Extract nutrition facts from this image and output in JSON only. "
        "Keys: 'serving-size','energy-kcal','fat','carbohydrates','proteins',"
        "'saturated-fat','trans-fat','sugars','added-sugars','sodium','salt','fiber'. "
        "Missing values = 0. Convert mg → g."
    )

    try:
        result = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[prompt, image]
        )

        raw = result.text
        st.subheader("📄 Raw Output Gemini:")
        st.code(raw)

        # Bersihkan format kode
        clean = raw.replace("```json","").replace("```","").strip()

        # Ambil JSON saja
        try:
            data = json.loads(clean)
        except:
            data = json.loads(re.search(r"\{.*\}", clean).group(0))

        st.subheader("📌 Nutrition Extracted JSON")
        st.json(data)

        # ==============================
        # Hitung per 1 gram
        # ==============================
        serving = data.get("serving-size","0")
        serving_num = float(re.findall(r"[\d\.]+", str(serving))[0])

        result_1g = {}

        for key,val in data.items():
            if key == "serving-size": continue
            
            # Ambil angka numerik
            number = float(re.findall(r"[\d\.]+", str(val))[0])

            # Convert mg → g
            if "mg" in str(val).lower():
                number = number / 1000

            result_1g[key+"_per_1g"] = round(number/serving_num,3)

        st.subheader("⚖ Hasil Per 1 Gram")
        st.json(result_1g)

        # ====== Download JSON ======
        json_bytes = json.dumps(result_1g, indent=2).encode('utf-8')
        st.download_button(
            "⬇ Download JSON per 1g",
            data=json_bytes,
            file_name="nutrition_per_1g.json",
            mime="application/json"
        )

    except Exception as e:
        st.error(f"Terjadi error saat proses ❗\n{e}")
