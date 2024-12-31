import pdfplumber
from loguru import logger
from typing import List, Optional
from pathlib import Path

logger = logger.bind(name="pdf_parser")


class PDFParser:
    def __init__(self) -> None:
        self.last_parsed = None

    def parse_pdf(self, file_path: Path | str) -> str:
        """Parse a PDF file and extract its text content.

        This function processes a PDF file page by page and extracts all text content,
        joining it with newlines between pages.

        Args:
            file_path (str): Path to the PDF file to be processed.

        Returns:
            str: Extracted text from all pages, joined with newlines.
                Returns empty string if no text could be extracted.

        Raises:
            PermissionError: If the PDF file can't be accessed.
            ValueError: If the file path is invalid or file is not a PDF.
            RuntimeError: If PDF parsing fails for any other reason.
        """
        self.last_parsed = file_path

        try:
            return self._extract_text(file_path)
        except FileNotFoundError as e:
            logger.error(f"PDF file not found: {e}")
            raise ValueError(f"PDF file not found: {str(e)}")
        except pdfplumber.pdfminer.pdfparser.PDFSyntaxError as e:
            logger.error(f"Invalid or corrupted PDF file: {e}")
            raise ValueError(f"Invalid or corrupted PDF file: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error parsing PDF: {e}")
            raise RuntimeError(f"Failed to parse PDF: {str(e)}")

    def _extract_text(self, file_path: Path) -> str:
        """Extract text from PDF file page by page.

        Args:
            file_path (Path): Path to the PDF file

        Returns:
            str: Extracted text from all pages
        """
        all_text: List[str] = []

        with pdfplumber.open(file_path) as pdf:
            if not pdf.pages:
                logger.warning(f"PDF file contains no pages: {file_path}")
                return ""

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
                    continue

        if not all_text:
            logger.warning("No text could be extracted from any page")
            return ""

        result = "\n".join(all_text)
        logger.info(
            f"Successfully extracted {len(result)} characters "
            f"from {len(pdf.pages)} pages"
        )
        return result
