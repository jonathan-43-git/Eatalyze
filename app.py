import streamlit as st
from google import genai
from PIL import Image
import re
import json

# ============= STREAMLIT UI =============
st.title("Nutrition OCR Analyzer")
st.write("Upload gambar tabel nutrisi → sistem akan membaca & mengubahnya ke JSON + per gram result.")

api_key = st.text_input("Masukkan API Key kamu", type="password")

uploaded_file = st.file_uploader("Upload Gambar Nutrisi (.jpg/.png/.jpeg)", type=["png", "jpg", "jpeg"])


# ============= RUN ONLY IF IMAGE & API FILLED =============
if uploaded_file and api_key:

    # Load image
    image = Image.open(uploaded_file)
    st.image(image, caption="Gambar yang dianalisis", use_column_width=True)

    # === Gemini Client ===
    client = genai.Client(api_key=api_key)

    prompt = (
        "Transcribe the nutrition facts table in this image and output the data "
        "as a single JSON object. Use keys like 'serving-size', 'energy-kcal', 'fat', 'carbohydrates', 'proteins', 'saturated-fat', 'trans-fat', 'sugars', 'added-sugars', 'sodium', 'salt', and 'fiber'. "
        "Do not include any text outside of the JSON object."
        "If the values are not in the image, fill the values with 0."
        "Normalize units → convert mg to grams (mg / 1000)."
    )

    st.info("⏳ Processing OCR...")

    # === Generate text result ===
    result = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[prompt, image]
    )

    # Raw model output preview
    data = result.text
    st.subheader("📄 Raw OCR Output")
    st.code(data)

    # ============= CLEAN JSON =============
    cleanedData = data.strip().replace("```json", "").replace("```", "").replace("\n","").strip()
    cleanedData = re.sub(r'\s+', ' ', cleanedData).strip()

    # parse value
    tempDict = {}
    for item in cleanedData.split(','):
        try:
            key = re.search(r'"(.*?)"', item).group(1)
            val = re.findall(r":\s*([^,{}]+)", item)[0]
            tempDict[key] = val.replace('"', '')
        except:
            pass

    # ============= Convert per 1 gram =============
    resDict = {}
    try:
        divider = int(tempDict["serving-size"].replace("g","").strip())
        for key,val in tempDict.items():
            if key != "serving-size":
                try:
                    resDict[f"{key}_per1g"] = round(float(val)/divider, 3)
                except:
                    resDict[f"{key}_per1g"] = 0
    except:
        st.error("⚠ Tidak menemukan 'serving-size' pada data!")
        divider = None

    # Output JSON final
    st.subheader("📌 Hasil JSON Nutrisi")
    st.json(tempDict)

    if divider:
        st.subheader("📌 Nutrisi dalam 1 gram")
        st.json(resDict)

else:
    st.warning("Silakan upload gambar + isi API key dulu 🔑")
