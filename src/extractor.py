import json
import re
from loguru import logger
import vertexai
from vertexai.preview.generative_models import GenerativeModel
from typing import List, Dict, Any, Optional, Iterator

logger = logger.bind(name="extractor")

class Extractor:
    """Class to extract entities from a text using a pre-trained model from Vertex AI model garden.

    Attributes:
        model: The GenerativeModel instance from Vertex AI
        text: The input text to process
        paragraphs: List of paragraphs extracted from the text
        entities: List of extracted entities
    """
    def __init__(self, GCP_MODEL_NAME: str, GCP_PROJECT_ID: str, GCP_LOCATION: str) -> None:
        """Initialize the Extractor with GCP credentials and model.

        Args:
            gcp_model_name (str): Name of the Vertex AI model to use
            GCP_PROJECT_ID (str): GCP project identifier
            gcp_location (str): GCP region/location for the service

        Raises:
            ValueError: If any of the GCP parameters are empty or invalid
            RuntimeError: If Vertex AI initialization fails
        """
        # Validate input parameters
        if not all([GCP_MODEL_NAME, GCP_PROJECT_ID, GCP_LOCATION]):
            raise ValueError("All GCP parameters must be provided")

        try:
            # Initialize Vertex AI with GCP credentials
            vertexai.init(project=GCP_PROJECT_ID, location=GCP_LOCATION)
            # Initialize the generative model
            self.model = GenerativeModel(GCP_MODEL_NAME)
            logger.info(f"Successfully initialized Vertex AI model: {GCP_MODEL_NAME}")
        except Exception as e:
            logger.error(f"Failed to initialize Vertex AI: {e}")
            raise RuntimeError(f"Vertex AI initialization failed: {str(e)}")

        self.text: Optional[str] = None
        self.paragraphs: List[str] = []
        self.entities: List[Dict[str, Any]] = []

    def extract_entities(self, text: str) -> List[Dict[str, Any]]:
        """Extracts entities from a text using the model.

        Args:
            text (str): The text to extract entities from.

        Returns:
            List[Dict[str, Any]]: A list of dictionaries containing entities and their metadata.
                Each dictionary includes:
                - entity: The extracted entity text
                - context: Surrounding context of the entity
                - start: Starting position in the text
                - end: Ending position in the text

        Raises:
            ValueError: If input text is empty or invalid
            RuntimeError: If entity extraction process fails
        """
        # Validate input text
        if not text or not isinstance(text, str):
            logger.error("Invalid input text provided")
            raise ValueError("Input text must be a non-empty string")

        try:
            # Store the input text
            self.text = text
            # Split the text into manageable paragraphs as a list of strings
            self.paragraphs = self.split_into_paragraphs(self.text)
            # Process text to extract entities and return them as 
            # a list of dictionaries
            self.entities = self.process_text()

            # Handle JSON string response
            if isinstance(self.entities, str):
                try:
                    logger.debug(f"Parsing JSON response: {self.entities}")
                    return json.loads(self.entities)
                except json.JSONDecodeError as e:
                    # Just in-case, I think gemini is good at this
                    # The initial plan was to find/finetune a model for this
                    # but I think this is good enough for now, time is not
                    # my friend right now and I want to get the job
                    # quickly :D
                    logger.error(f"Failed to parse JSON response: {e}")
                    raise RuntimeError("Invalid JSON response from model")
            
            return self.entities

        except Exception as e:
            logger.error(f"Entity extraction failed: {e}")
            raise RuntimeError(f"Entity extraction process failed: {str(e)}")

    def split_into_paragraphs(self, text: str) -> List[str]:
        """Splits the input text into paragraphs based on newline characters.

        Args:
            text (str): The input text string, typically a PDF file converted to text

        Returns:
            List[str]: A list of strings, where each string is a cleaned paragraph

        Raises:
            ValueError: If input text is empty or invalid
        """
        # Validate input
        if not text or not isinstance(text, str):
            logger.error("Invalid input for paragraph splitting")
            raise ValueError("Input text must be a non-empty string")

        try:
            # Split text on multiple newlines and clean each paragraph
            # I'm not sure if this is the best way to do it, but it's good enough for now
            # It's not optimal, as research paper have this weird format where they
            # have a lot of newlines and it's not always clear where one paragraph ends
            # and another begins.

            # If I have time, I'll try to find a way to improve this
            # TODO: Improve paragraph splitting
            paragraphs = [p.strip() for p in re.split(r"\n+", text) if p.strip()]
            
            # Validate result
            if not paragraphs:
                logger.warning("No valid paragraphs found in text")
                return []

            logger.info(f"Successfully split text into {len(paragraphs)} paragraphs")
            return paragraphs

        except Exception as e:
            logger.error(f"Error during paragraph splitting: {e}")
            raise RuntimeError(f"Failed to split text into paragraphs: {str(e)}")

    def extract_entities_from_paragraph(self, paragraph: str) -> List[Dict[str, Any]]:
        """Extracts entities from a single paragraph using the model.

        Args:
            paragraph (str): The paragraph to extract entities from.

        Returns:
            List[Dict[str, Any]]: A list of dictionaries containing extracted entities.
                Each dictionary includes:
                - entity: The extracted entity text
                - context: The context where the entity appears
                - start: Starting position in paragraph
                - end: Ending position in paragraph

        Raises:
            ValueError: If paragraph is empty or invalid
            RuntimeError: If model generation fails
        """
        # Validate input
        # We are doing checks prior to this, so this should never happen
        # in this case, but just for re-usability
        if not paragraph or not isinstance(paragraph, str):
            logger.warning("Invalid paragraph provided")
            return []

        # Define the prompt template for entity extraction
        # TODO: Remove this into a config file, not hardcoded inside the code.
        prompt = f"""
        You are a medical entity extraction system.
        Identify and extract medically relevant entities from the following paragraph.
        Provide the context where the entity was found along with its start and end position within the paragraph.
        The output should strictly adhere to this JSON format, no explanation is required:

        [
        {{
            "entity": "entity1",
            "context": "context of entity1 within the paragraph",
            "start": start_position,
            "end": end_position
        }},
        {{
            "entity": "entity2",
            "context": "context of entity2 within the paragraph",
            "start": start_position,
            "end": end_position
        }}
        ]

        Paragraph:
        {paragraph}

        Entities:
        """

        try:
            # Generate response from the model
            response = self.model.generate_content(prompt)
            
            # Validate response
            if not response or not response.text:
                logger.warning("Empty response from model")
                return []

            # Parse the JSON response
            json_string = response.text
            extracted_entities = json.loads(json_string)
            
            # Validate extracted entities
            if not isinstance(extracted_entities, list):
                logger.warning("Invalid response format from model")
                return []

            logger.debug(f"Successfully extracted {len(extracted_entities)} entities from paragraph")
            return extracted_entities

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse model response: {e}")
            logger.debug(f"Raw response from model: {response.text if 'response' in locals() else 'No response'}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error during entity extraction: {e}")
            return []
    
    def process_text(self) -> List[Dict[str, Any]]:
        """Processes the entire text, splitting it into paragraphs and extracting entities from each.

        Returns:
            List[Dict[str, Any]]: A list of dictionaries containing extracted entities and their metadata.
                Each dictionary contains:
                - entity (str): The extracted medical entity
                - context (str): The full paragraph where the entity was found
                - start (int): Character position where entity starts in the full text
                - end (int): Character position where entity ends in the full text

        Raises:
            ValueError: If self.paragraphs is None or empty
            TypeError: If entity positions are not valid integers
        """
        # Validate that we have paragraphs to process
        if not self.paragraphs:
            logger.error("No paragraphs found to process")
            raise ValueError("Text must be initialized and split into paragraphs before processing")

        # Initialize collection for all entities and tracking of character positions
        all_entities = []
        start_position_offset = 0  # Keeps track of character position in full text

        try:
            # Process each paragraph sequentially
            for i, paragraph in enumerate(self.paragraphs):
                logger.debug(f"Processing paragraph {i+1}/{len(self.paragraphs)}")
                
                # Ensure paragraph is a valid string
                if not isinstance(paragraph, str):
                    logger.warning(f"Skipping paragraph {i+1}: Invalid type {type(paragraph)}")
                    continue

                # Extract entities from current paragraph
                paragraph_entities = self.extract_entities_from_paragraph(paragraph)
                
                # Adjust entity positions to be relative to the full text
                for entity in paragraph_entities:
                    try:
                        # Ensure entity has required position fields
                        if not all(key in entity for key in ["start", "end"]):
                            logger.warning(f"Skipping entity: Missing required position fields")
                            continue
                        
                        # Convert positions to integers and adjust for full text position
                        entity["start"] = int(entity["start"]) + start_position_offset
                        entity["end"] = int(entity["end"]) + start_position_offset
                        
                        # Validate position values are logical
                        if entity["start"] < 0 or entity["end"] < entity["start"]:
                            logger.warning(f"Skipping entity: Invalid position values")
                            continue
                        
                        # Store full paragraph as context
                        entity["context"] = paragraph
                        all_entities.append(entity)
                        
                    except (TypeError, ValueError) as e:
                        logger.error(f"Error processing entity in paragraph {i+1}: {e}")
                        continue

                # Update offset for next paragraph (add 1 for the newline character)
                start_position_offset += len(paragraph) + 1

            logger.info(f"Successfully processed {len(all_entities)} entities from {len(self.paragraphs)} paragraphs")
            return all_entities

        except Exception as e:
            logger.error(f"Unexpected error during text processing: {e}")
            raise  # Re-raise the exception after logging
