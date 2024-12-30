import pdfplumber
import logging
from typing import List, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class PDFParser:
    @staticmethod
    def parse_pdf(file_path: str) -> str:
        """Parse a PDF file and extract its text content.

        This function processes a PDF file page by page and extracts all text content,
        joining it with newlines between pages.

        Args:
            file_path (str): Path to the PDF file to be processed.

        Returns:
            str: Extracted text from all pages, joined with newlines.
                Returns empty string if no text could be extracted.

        Raises:
            FileNotFoundError: If the PDF file doesn't exist.
            PermissionError: If the PDF file can't be accessed.
            ValueError: If the file path is invalid or file is not a PDF.
            RuntimeError: If PDF parsing fails for any other reason.
        """
        # Validate input
        if not file_path:
            raise ValueError("File path cannot be empty")

        file_path_obj = Path(file_path)

        # Validate file existence and type
        if not file_path_obj.exists():
            raise FileNotFoundError(f"PDF file not found: {file_path}")

        if file_path_obj.suffix.lower() != ".pdf":
            raise ValueError(f"File must be a PDF: {file_path}")

        try:
            all_text: List[str] = []

            # Open and process PDF
            with pdfplumber.open(file_path) as pdf:
                # Validate PDF has pages
                if not pdf.pages:
                    logger.warning(f"PDF file contains no pages: {file_path}")
                    return ""

                # Process each page
                for page_num, page in enumerate(pdf.pages, 1):
                    try:
                        logger.debug(f"Processing page {page_num}/{len(pdf.pages)}")
                        text: Optional[str] = page.extract_text()

                        if text:
                            all_text.append(text)
                        else:
                            logger.warning(f"No text extracted from page {page_num}")

                    except Exception as e:
                        logger.error(f"Error processing page {page_num}: {e}")
                        # Continue with next page instead of failing completely
                        continue

            # Check if any text was extracted
            if not all_text:
                logger.warning("No text could be extracted from any page")
                return ""

            # Join all extracted text
            result = "\n".join(all_text)
            logger.info(
                f"Successfully extracted {len(result)} characters ",
                f"from {len(pdf.pages)} pages",
            )
            return result

        except pdfplumber.pdfminer.pdfparser.PDFSyntaxError as e:
            logger.error(f"Invalid or corrupted PDF file: {e}")
            raise ValueError(f"Invalid or corrupted PDF file: {str(e)}")

        except PermissionError as e:
            logger.error(f"Permission denied accessing file: {e}")
            raise

        except Exception as e:
            logger.error(f"Unexpected error parsing PDF: {e}")
            raise RuntimeError(f"Failed to parse PDF: {str(e)}")
