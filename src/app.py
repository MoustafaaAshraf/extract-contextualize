from src import PDFParser
from src import Extractor

from fastapi import FastAPI, File, UploadFile, HTTPException
from typing import List
from pydantic import BaseModel
import uvicorn
import tempfile
from loguru import logger
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()


# Hardcoded configuration
GCP_PROJECT_ID = os.getenv("GCP_PROJECT_ID")
GCP_MODEL_NAME = "gemini-1.0-pro-001"  # Hardcoded instead of using env var
GCP_LOCATION = os.getenv("GCP_LOCATION")

extractor = Extractor(GCP_MODEL_NAME, GCP_PROJECT_ID, GCP_LOCATION)
logger.info("Model initialized")


# Define the Entity model
class Entity(BaseModel):
    entity: str
    context: str
    start: int
    end: int


app = FastAPI(
    title="Medical Entity Extraction API",
    description=(
        "This API allows users to extract medically relevant "
        "entities from PDF documents using a pre-trained gen-ai model."
    ),
    version="1.0.0",
)


@app.post(
    "/api/v1/extract",
    response_model=List[Entity],
    responses={
        200: {"description": "Successfully extracted entities."},
        400: {"description": "Bad request, file not included or empty filename."},
        415: {"description": "Unsupported file type."},
        500: {"description": "Server error."},
    },
)
async def extract_entities(file: UploadFile = File(...)) -> List[Entity]:
    """Extract medical entities from a PDF file.

    Args:
        file (UploadFile): The uploaded PDF file to process.

    Returns:
        List[Entity]: A list of extracted medical entities with their
            context and positions.

    Raises:
        HTTPException:
            - 400: If file is missing or empty
            - 413: If file size exceeds limit
            - 415: If file is not a PDF
            - 422: If PDF parsing fails
            - 500: For unexpected server errors
    """
    try:
        # Validate file existence and name
        if not file:
            raise HTTPException(status_code=400, detail="No file provided")
        if not file.filename:
            raise HTTPException(status_code=400, detail="No filename provided")

        # Validate file type
        if not file.filename.lower().endswith(".pdf"):
            raise HTTPException(
                status_code=415,
                detail="Unsupported file type. Only PDF files are accepted",
            )

        # Read file content
        try:
            content = await file.read()
            # Check file size (e.g., 10MB limit)
            if len(content) > 10 * 1024 * 1024:
                raise HTTPException(
                    status_code=413, detail="File size too large. Maximum size is 10MB"
                )
        except Exception as e:
            logger.error(f"Error reading file: {e}")
            raise HTTPException(status_code=400, detail="Error reading file content")

        # Process PDF file
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp:
                logger.info(f"Writing file '{file.filename}' to temporary storage")
                temp.write(content)
                temp.flush()

                logger.info("Parsing PDF content")
                parser = PDFParser()
                pdf_text = parser.parse_pdf(temp.name)

                if not pdf_text:
                    raise HTTPException(
                        status_code=422,
                        detail=(
                            "Unable to extract text from PDF. "
                            "File may be empty or corrupted"
                        ),
                    )
        except Exception as e:
            logger.error(f"PDF parsing error: {e}")
            raise HTTPException(status_code=422, detail="Failed to parse PDF content")
        finally:
            # Clean up temporary file
            try:
                os.unlink(temp.name)
            except Exception as e:
                logger.warning(f"Failed to delete temporary file: {e}")

        # Extract entities from text
        try:
            logger.info("Extracting medical entities from text")
            # Note: Currently processing first 1000 chars only - might need adjustment
            entities = extractor.extract_entities(pdf_text[:1000])

            if not entities:
                logger.warning("No entities found in document")
                return []

            logger.info(f"Successfully extracted {len(entities)} entities")
            return entities

        except Exception as e:
            logger.error(f"Entity extraction error: {e}")
            raise HTTPException(
                status_code=500, detail="Failed to extract entities from document"
            )

    except HTTPException:
        # Re-raise HTTP exceptions without modification
        raise
    except Exception as e:
        # Log unexpected errors and return generic error message
        logger.exception(f"Unexpected error processing file '{file.filename}': {e}")
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred while processing the file",
        )


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
