import streamlit as st
import google.generativeai as genai
from PIL import Image
import json, re

# 🔑 API KEY
genai.configure(api_key="AIzaSyAQj4gSaqyDYBDrJX2v62b1JnwpzOCzaLk")

st.title("🥣 OCR Nutrition Label Extractor")

uploaded = st.file_uploader("Upload Nutrition Label Image", type=["png","jpg","jpeg"])

if uploaded is not None:
    image = Image.open(uploaded)
    st.image(image, caption="Preview", use_column_width=True)

    prompt = (
        "Read the nutrition facts table in this image and return JSON. "
        "Keys: serving-size, energy-kcal, fat, carbohydrates, proteins, saturated-fat, "
        "trans-fat, sugars, added-sugars, sodium, salt, fiber. "
        "Fill missing values = 0. Convert mg → gram. Output JSON only."
    )

    model = genai.GenerativeModel("gemini-2.5-flash")
    result = model.generate_content([prompt, image])
    raw = result.text

    cleaned = (
        raw.replace("```json","")
           .replace("```","")
           .replace("\n","")
           .strip()
    )

    st.subheader("🔍 Raw Output")
    st.code(cleaned)

    # parsing JSON manual
    temp={}
    for i in cleaned.split(","):
        try:
            key,value=i.split(":")
            key=key.replace('"','').strip()
            value=value.replace('"','').replace("}","").strip()
            temp[key]=value
        except: pass

    # Hitung per 1g
    res={}
    divider=int(temp.get("serving-size","1").replace("g",""))
    for x in temp:
        if x=="serving-size": continue
        try: num=float(temp[x])
        except: num=float(temp[x].replace("mg",""))/1000
        res[x+"_1g"]=round(num/divider,3)

    st.subheader("📌 Normalized per 1 Gram")
    st.json(res)
else:
    st.info("Silakan upload gambar terlebih dahulu 👆")
