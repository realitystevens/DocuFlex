from fastapi import FastAPI, File, UploadFile
from fastapi.responses import FileResponse, HTMLResponse
from pdf2docx import Converter
import os


app = FastAPI()


def pdf_to_docs(pdf, docs):
    cv_obj = Converter(pdf)
    cv_obj.convert(docs, start=0, end=None)

    cv_obj.close()


@app.get("/")
async def home():
    with open("templates/index.html", "r") as f:
        html_content = f.read()

    return HTMLResponse(content=html_content)


@app.post("/api/convert")
async def convert_pdf_to_docs(file: UploadFile = File(...)):
    pdfInput = f"temp_{file.filename}"
    docsOutput = pdfInput.replace(".pdf", ".docx")

    with open(pdfInput, "wb") as f:
        f.write(await file.read())

    pdf_to_docs(pdfInput, docsOutput)

    os.remove(pdfInput)


    return FileResponse(docsOutput, media_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document', filename=docsOutput)




if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
