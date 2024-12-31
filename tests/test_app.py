from pathlib import Path
import os
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

# 1. Mock Configuration
mock_config = MagicMock()
mock_config.project = "test-project"
mock_config.location = "test-location"

# 3. Patch Definitions
patches = [
    # Prevents actual VertexAI initialization
    patch("vertexai.init"),
    # Provides a mock model instead of real VertexAI model
    patch("vertexai.generative_models.GenerativeModel", return_value=MagicMock()),
    # Replaces VertexAI global configuration
    patch("google.cloud.aiplatform.initializer.global_config", mock_config),
    # Prevents actual GCP authentication
    patch("google.auth.default", return_value=(MagicMock(), "test-project")),
]

# 4. Apply Patches Before Import
for p in patches:
    p.start()

# 5. Import App Under Test
from src.app import app

# 6. Clean Up Patches
for p in patches:
    p.stop()

client = TestClient(app)


# 7. Test Fixtures
@pytest.fixture
def mock_extractor():
    with patch("src.app.Extractor") as mock:
        yield mock


# 8. Test Cases
def test_extract_empty_file():
    response = client.post("/api/v1/extract")
    assert response.status_code == 422


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
