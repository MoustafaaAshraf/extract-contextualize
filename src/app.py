from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
import uvicorn
import tempfile

from src.pdf_parser import parse_pdf
from src.ner_model import NERModel

# Load the model at startup
# TODO: Is this model even good?
model_name = "dmis-lab/biobert-base-cased-v1.1"  
ner_model = NERModel(model_name)

app = FastAPI()

@app.post("/api/v1/extract")
async def extract_entities(file: UploadFile = File(...)):
    # TODO: Add proper exceptions 

    if not file.filename:
        return JSONResponse(status_code=400, content={"error": "No filename provided."})

    if not file.filename.lower().endswith('.pdf'):
        return JSONResponse(status_code=400, content={"error": "File must be a PDF"})

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp:
        temp.write(await file.read())
        temp.flush()
        pdf_text = parse_pdf(temp.name)

    # Now run NER extraction
    entities = ner_model.extract_entities(pdf_text)
    
    return JSONResponse(status_code=200, content=entities)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
