from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
import fitz  # PyMuPDF
import os
import shutil
import logging

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_FOLDER = 'uploads'
PROCESSED_FOLDER = 'processed'

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

if not os.path.exists(PROCESSED_FOLDER):
    os.makedirs(PROCESSED_FOLDER)

logging.basicConfig(level=logging.INFO)

@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return {"file_path": file_path}

@app.post("/preview")
async def preview_pdf(file_path: str = Form(...)):
    logging.info(f"Previewing file: {file_path}")
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    doc = fitz.open(file_path)
    previews = []
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        pix = page.get_pixmap()
        image_path = os.path.join(UPLOAD_FOLDER, f'preview_{page_num}.png')
        pix.save(image_path)
        previews.append(image_path)
    return {"previews": previews}

@app.post("/process")
async def process_pdf(file_path: str = Form(...), selected_pages: str = Form(...)):
    logging.info(f"Processing file: {file_path} with pages: {selected_pages}")
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    selected_pages = list(map(int, selected_pages.split(',')))
    # Your backend code here
    pdf = PDF(src=file_path)
    output_path = os.path.join(PROCESSED_FOLDER, 'tesseact_ocr4.xlsx')
    pdf.to_xlsx(output_path, ocr=tesseract_ocr, implicit_rows=False, borderless_tables=False, min_confidence=50)
    return FileResponse(output_path)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
