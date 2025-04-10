# ✅ Python FastAPI Boilerplate for Document Parsing
# Supports PDF, Word, Excel, CSV, and Images (with Tesseract)

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import PlainTextResponse
from PIL import Image
import pytesseract, io, fitz, pandas as pd, docx2txt, os
import openpyxl

app = FastAPI()

@app.post("/parse", response_class=PlainTextResponse)
async def parse_file(request: Request):
    content_type = request.headers.get("Content-Type")
    content = await request.body()

    try:
        # Fallback if no header sent
        if content_type is None:
            content_type = "application/octet-stream"

        if content_type == "application/pdf":
            return parse_pdf(content)
        elif content_type in ["image/png", "image/jpeg", "image/jpg"]:
            return parse_image(content)
        elif content_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            return parse_docx(content)
        elif content_type == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet":
            return parse_excel(content)
        elif content_type == "text/csv":
            return parse_csv(content)
        else:
            # Heuristic fallback (for Apex)
            if b'%PDF' in content[:10]:
                return parse_pdf(content)
            elif content.startswith(b'PK') and b'[Content_Types].xml' in content:
                return parse_docx(content)
            elif content.startswith(b'PK') and b'xl/' in content:
                return parse_excel(content)
            elif b',' in content[:100]:
                return parse_csv(content)
            elif content[1:4] in [b'PNG', b'JFI', b'JFIF']:
                return parse_image(content)
            else:
                return "Unsupported or unknown file format."

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def parse_pdf(content):
    with fitz.open(stream=content, filetype="pdf") as doc:
        return "\n".join([page.get_text() for page in doc])

def parse_docx(content):
    with open("temp.docx", "wb") as f:
        f.write(content)
    text = docx2txt.process("temp.docx")
    os.remove("temp.docx")
    return text

def parse_excel(content):
    df = pd.read_excel(io.BytesIO(content))
    return df.to_csv(index=False)

def parse_csv(content):
    return content.decode("utf-8", errors="ignore")

def parse_image(content):
    image = Image.open(io.BytesIO(content))
    return pytesseract.image_to_string(image)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
