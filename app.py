from fastapi import FastAPI, File, UploadFile, Request
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from http.client import HTTPException
from pdf2docx import Converter
import os



app = FastAPI()
templates = Jinja2Templates(directory="templates")


"""Home Page"""
@app.get("/", response_class = HTMLResponse)
async def home(request: Request):
    context = {"request": request}
    
    return templates.TemplateResponse("index.html", context)


def pdf_to_docs(pdf, docs):
    try:
        cv_obj = Converter(pdf)
        cv_obj.convert(docs, start=0, end=None)
        cv_obj.close()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


"""API Endpoint"""
@app.post("/api/convert")
async def convert_pdf_to_docs(file: UploadFile = File(...)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="File format not supported. Please upload a PDF file.")
    
    pdfInput = f"temp_{file.filename}"
    docsOutput = pdfInput.replace(".pdf", ".docx")

    try:
        with open(pdfInput, "wb") as f:
            f.write(await file.read())

        pdf_to_docs(pdfInput, docsOutput)

        return FileResponse(docsOutput, media_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document', filename=docsOutput)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if os.path.exists(pdfInput):
            os.remove(pdfInput)
        if os.path.exists(docsOutput):
            os.remove(docsOutput)    



app.mount("/static", StaticFiles(directory="static"), name="static")
