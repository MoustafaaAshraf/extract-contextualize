# Medical Entity Extraction API

A software solution that automatically extracts and contextualizes entities from provided scientific paper PDFs. Data should be processed and returned via an API endpoint.

## Overview

This API uses [specify model name/source] from HuggingFace to extract medical entities from scientific papers. It processes PDF documents and returns structured data about medical entities found within the text, including their context and position.

## Prerequisites

- Python 3.10+
- Poetry
- Google Cloud SDK
- Access to a GCP project

## API Specification

### POST /api/v1/extract

Extracts medical entities from a PDF document.

**Request:**
- Content-Type: multipart/form-data
- Body: PDF file

**Response:**
```json
[
  {
    "entity": "CCR5",
    "context": "... uses on the relief of symptoms rather than on a biological 'cure'. have identified rare mutations in CCR5 that confer resilience against ...",
    "start": 25,
    "end": 34
  }
]
```

**Status Codes:**
- 200: Successfully extracted entities
- 400: Bad request, file not included or empty filename
- 415: Unsupported file type
- 500: Server error

## Environment Variables

Required variables in `.env`:
```
GCP_PROJECT_ID=your-project-id
GCP_LOCATION=your-location
GCP_MODEL_NAME=your-model-name
```

## Local Setup

1. Install dependencies:
```bash
pip install poetry
poetry install
```

2. Local GCP auth:
```bash
gcloud auth application-default login
```

3. Copy the `.env.example` file to `.env` and update the values:
```bash
cp .env.example .env
```

Please note that this will create a new OAuth token and store it in the default location. Update the `.env` file with the correct path to the token.

4. Run the app:
```bash
make run
```

5. Test the API:
```bash
curl -X POST -F "file=@path/to/your/file.pdf" http://localhost:8000/extract
```

## Testing

1. Test files:
   - Place them in `tests/test_files/`

2. Run tests:
```bash
make test
```


## Architecture

TODO: Add a brief description or diagram of the system architecture

## Limitations

TODO: Add any limitations

## Contributing

TODO: Add contributing guidelines if applicable

## Deployment to GCP Cloud Run

1. Setting up GCP resources:
```bash
make setup-gcp
```

2. Setup GitHub Actions secrets:
- GCP_SA_KEY: The service account key for the GCP project.
- GCP_PROJECT_ID: The ID of the GCP project.
- GCP_LOCATION: The location of the GCP project.

3. Push to main branch:
```bash
git push origin main
```

4. The deployment will be triggered automatically.

5. The app will be available at the URL specified in the deployment.