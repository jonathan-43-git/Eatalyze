import google.generativeai as genai
from PIL import Image
import json
import re

# ======================
# ======================
genai.configure(api_key="AIzaSyAQj4gSaqyDYBDrJX2v62b1JnwpzOCzaLk")

# Load gambar
image = Image.open("y.png")

# Prompt ke Gemini
prompt = (
    "Transcribe the nutrition facts table in this image and output the data "
    "as a single JSON object. Use keys like 'serving-size', 'energy-kcal', 'fat', "
    "'carbohydrates', 'proteins', 'saturated-fat', 'trans-fat', 'sugars', "
    "'added-sugars', 'sodium', 'salt', 'fiber'. "
    "If no value exists, fill with 0. "
    "Convert mg to gram. Output only JSON."
)

# Call model Gemini
model = genai.GenerativeModel("gemini-2.5-flash")
result = model.generate_content([prompt, image])

data = result.text
print("\n===== Output Mentah Gemini =====")
print(data)

# ======================
# 🔧 Process JSON hasil OCR
# ======================
cleanedData = (
    data.replace("```json", "")
        .replace("```", "")
        .replace("\n", "")
        .strip()
)

cleanedData = re.sub(r"\s+", " ", cleanedData)
tempDict = {}

for i in cleanedData.split(","):
    try:
        key, value = i.split(":")
        key = key.replace('"', '').strip()
        value = value.replace('"', '').replace("}", "").strip()
        tempDict[key] = value
    except:
        pass

# Hitung per 1 gram
resDict = {}
divider = int(tempDict.get("serving-size", 1).replace("g", "").strip())

for i in tempDict:
    if i == "serving-size":
        continue
    try:
        num = float(tempDict[i])
    except:
        num = float(tempDict[i].replace("mg",""))/1000
    resDict[i + "_1g"] = round(num / divider, 3)

print("\n===== Hasil Normalisasi (1g) =====")
print(json.dumps(resDict, indent=2))
