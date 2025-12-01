from flask import Flask, request, jsonify
from PIL import Image
import io, os, google.genai as genai

app = Flask(__name__)

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def process_image(image_bytes):
    img = Image.open(io.BytesIO(image_bytes))

    prompt = """
    Extract nutrition facts and return ONLY JSON.
    Convert units to grams. Missing values = 0.
    Keys:
    serving-size, energy-kcal, fat, saturated-fat, trans-fat,
    carbohydrates, sugars, added-sugars, fiber, proteins,
    sodium, salt
    """

    model = genai.GenerativeModel("gemini-2.0-flash")
    result = model.generate_content([prompt, img])
    raw = result.text.strip()
    raw = raw.replace("```json","").replace("```","").strip()

    return raw

@app.route("/analyze", methods=["POST"])
def analyze():
    if "image" not in request.files:
        return jsonify({"error": "No image uploaded"}), 400
    
    file = request.files["image"].read()

    try:
        json_output = process_image(file)
        return jsonify({"status":"success","data":json_output})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/")
def home():
    return "Nutrition OCR API Running ✔"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
