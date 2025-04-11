# ✅ Base image with Python
FROM python:3.10-slim

# ✅ Install Tesseract and dependencies
RUN apt-get update && apt-get install -y tesseract-ocr poppler-utils libglib2.0-0 libsm6 libxext6 libxrender-dev

# ✅ Set working directory
WORKDIR /app

# ✅ Copy project files into the image
COPY . .

# ✅ Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# ✅ Expose the port FastAPI runs on
EXPOSE 8000

# ✅ Start the FastAPI app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
