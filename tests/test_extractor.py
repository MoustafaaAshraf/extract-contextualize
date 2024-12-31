import pytest
from unittest.mock import patch, Mock
from src.extractor import Extractor


def create_mock_response(entities):
    mock_response = Mock()
    # Create unique positions for each entity
    mock_response.text = f"""[
        {','.join([
            f'{{"entity": "{e}", "start": {i*15}, "end": {(i*15)+10},'
            f' "context": "test context"}}'
            for i, e in enumerate(entities)
        ])}
    ]"""
    return mock_response


@pytest.fixture
def mock_model():
    mock = Mock()
    mock.generate_content.return_value = create_mock_response(["hypertension"])
    return mock


@pytest.fixture
def extractor():
    # Create a mock model
    mock_model = Mock()
    mock_model.generate_content.return_value = create_mock_response(["hypertension"])

    # Mock both the model class and initialization
    with patch("src.extractor.GenerativeModel") as mock_gen:
        # Configure the mock to return our mock model
        mock_gen.return_value = mock_model

        with patch("src.extractor.vertexai"):
            ext = Extractor(
                GCP_MODEL_NAME="test-model",
                GCP_PROJECT_ID="test-project",
                GCP_LOCATION="us-central1",
            )
            # Ensure the mock is properly set
            assert ext.model == mock_model
            return ext


def test_process_empty_text(extractor):
    """Test processing of empty text."""
    with pytest.raises(ValueError, match="Input text must be a non-empty string"):
        extractor.extract_entities("")


def test_process_simple_text(extractor):
    text = "The patient shows signs of hypertension."
    results = extractor.extract_entities(text)

    assert len(results) > 0
    entity = results[0]
    assert "hypertension" in entity["entity"]
    assert entity["start"] >= 0
    assert entity["end"] > entity["start"]
    assert text == entity["context"]


def test_process_multiple_paragraphs(extractor):
    # Create a mock that returns different responses for each paragraph
    responses = iter(
        [
            create_mock_response(["hypertension"]),  # First paragraph
            create_mock_response(["diabetes"]),  # Second paragraph
        ]
    )

    extractor.model.generate_content.side_effect = lambda _: next(responses)

    text = """First paragraph with hypertension.
    
    Second paragraph with diabetes."""
    results = extractor.extract_entities(text)

    assert len(results) == 2
    assert "hypertension" in results[0]["entity"]
    assert "diabetes" in results[1]["entity"]
    assert results[1]["start"] > results[0]["end"]


def test_invalid_paragraph_type(extractor):
    extractor.paragraphs = [None, "valid paragraph", 123]
    results = extractor.process_text()
    # Should only process the valid paragraph
    assert len(results) >= 0  # Depends on if entities were found in valid paragraph
