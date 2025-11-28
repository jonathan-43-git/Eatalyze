FROM python:3.11-slim

# Install dependensi sistem + tesseract OCR
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    libtesseract-dev \
    && apt-get clean

# Set folder kerja
WORKDIR /app

# Copy semua file app
COPY . .

# Install dependensi Python
RUN pip install --no-cache-dir -r requirements.txt

# Jalankan streamlit
CMD ["streamlit", "run", "app.py", "--server.port=8000", "--server.address=0.0.0.0"]
