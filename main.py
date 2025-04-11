# ✅ Python FastAPI Boilerplate for Document Parsing
# Supports PDF, Word, Excel, CSV, and Images (with Tesseract)

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import PlainTextResponse
import os
import pytesseract
from PIL import Image
import io
import pandas as pd
import docx2txt
import fitz  # PyMuPDF
import openpyxl

app = FastAPI()

@app.post("/parse", response_class=PlainTextResponse)
async def parse_file(request: Request):
    filename = request.headers.get("X-Filename", "unknown").lower()
    content = await request.body()

    try:
        if filename.endswith(".pdf"):
            return parse_pdf(content)
        elif filename.endswith(".csv"):
            return parse_csv(content)
        elif filename.endswith(".xlsx"):
            return parse_excel(content)
        elif filename.endswith(".docx"):
            return parse_docx(content)
        elif filename.endswith((".jpg", ".jpeg", ".png")):
            return parse_image(content)
        else:
            raise HTTPException(status_code=400, detail="Unsupported file format")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def parse_pdf(content):
    with fitz.open(stream=content, filetype="pdf") as doc:
        return "\n".join([page.get_text() for page in doc])

def parse_excel(content):
    df = pd.read_excel(io.BytesIO(content))
    return df.to_csv(index=False)

def parse_docx(content):
    with open("temp.docx", "wb") as out:
        out.write(content)
    text = docx2txt.process("temp.docx")
    os.remove("temp.docx")
    return text

def parse_csv(content):
    return content.decode("utf-8", errors="ignore")

def parse_image(content):
    image = Image.open(io.BytesIO(content))
    return pytesseract.image_to_string(image)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
