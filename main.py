# ✅ Python FastAPI Boilerplate for Document Parsing
# Supports PDF, Word, Excel, CSV, and Images (with Tesseract)

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import PlainTextResponse
import os, io, fitz, openpyxl, pandas as pd, docx2txt, pytesseract
from PIL import Image
from tempfile import NamedTemporaryFile

app = FastAPI()

@app.post("/parse", response_class=PlainTextResponse)
async def parse_file(request: Request):
    content = await request.body()
    
    # Save to temp file to detect type
    with NamedTemporaryFile(delete=False) as tmp:
        tmp.write(content)
        tmp.flush()
        tmp_path = tmp.name

    try:
        if tmp_path.endswith('.pdf') or b'%PDF' in content:
            return parse_pdf(content)
        elif content.startswith(b'PK') and b'[Content_Types].xml' in content:
            return parse_docx(content)
        elif content.startswith(b'PK') and b'xl/' in content:
            return parse_excel(content)
        elif b',' in content[:500]:  # naive CSV check
            return parse_csv(content)
        elif content[0:2] == b'\xFF\xD8' or content[1:4] == b'PNG':
            return parse_image(content)
        else:
            raise HTTPException(status_code=400, detail="Unsupported or unrecognized file format")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def parse_pdf(content):
    text = ""
    with fitz.open(stream=content, filetype="pdf") as doc:
        for page in doc:
            text += page.get_text()
    return text

def parse_docx(content):
    with io.BytesIO(content) as f:
        with open("temp.docx", "wb") as out:
            out.write(f.read())
        text = docx2txt.process("temp.docx")
        os.remove("temp.docx")
    return text

def parse_excel(content):
    with io.BytesIO(content) as excel_io:
        df = pd.read_excel(excel_io)
        return df.to_csv(index=False)

def parse_csv(content):
    decoded = content.decode("utf-8", errors="ignore")
    return decoded

def parse_image(content):
    image = Image.open(io.BytesIO(content))
    return pytesseract.image_to_string(image)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
