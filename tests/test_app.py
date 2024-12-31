from pathlib import Path
import pytest
from fastapi.testclient import TestClient
from src.app import app
import os
from unittest.mock import patch

client = TestClient(app)

@pytest.fixture(autouse=True)
def mock_vertex_ai():
    with patch('vertexai.init') as mock:
        yield mock

@pytest.fixture
def mock_extractor():
    with patch('src.app.Extractor') as mock:
        yield mock

def test_extract_empty_file():
    # Test with no file
    response = client.post("/api/v1/extract")
    assert (
        response.status_code == 422
    )

def test_extract_invalid_file():
    # Test with non-PDF file
    test_pdf_path = Path(__file__).parent / "test_files" / "invalidExtention.txt"

    # Skip if test file doesn't exist
    if not os.path.exists(test_pdf_path):
        pytest.skip("Test PDF file not found")

    with open(test_pdf_path, "rb") as pdf_file:
        files = {"file": ("invalidExtension.txt", pdf_file, "text/plain")}
        response = client.post("/api/v1/extract", files=files)

    assert response.status_code == 415


def test_extract_valid_pdf():
    # Create a test PDF file path
    test_pdf_path = Path(__file__).parent / "test_files" / "valid.pdf"

    # Skip if test file doesn't exist
    if not os.path.exists(test_pdf_path):
        pytest.skip("Test PDF file not found")

    with open(test_pdf_path, "rb") as pdf_file:
        files = {"file": ("valid.pdf", pdf_file, "application/pdf")}
        response = client.post("/api/v1/extract", files=files)

        assert response.status_code == 200
        assert isinstance(response.json(), list)
