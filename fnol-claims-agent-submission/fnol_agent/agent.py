from typing import Union, Dict, Any
from pathlib import Path
from fnol_agent.models import ClaimProcessingResult
from fnol_agent.document_loader import DocumentLoader
from fnol_agent.extractor import FNOLExtractor
from fnol_agent.router import ClaimRouter

class ClaimsProcessingAgent:
    """
    Autonomous Insurance Claims Processing Agent.
    Ingests FNOL documents (PDF/TXT), extracts key fields, identifies missing fields,
    routes claims based on business rules, and provides natural language reasoning.
    """

    def __init__(self):
        self.loader = DocumentLoader()
        self.extractor = FNOLExtractor()
        self.router = ClaimRouter()

    def process_file(self, file_path: str) -> ClaimProcessingResult:
        """Process an FNOL document file (.pdf or .txt) and return structured result."""
        text = self.loader.load_document(file_path)
        return self.process_text(text)

    def process_text(self, text: str) -> ClaimProcessingResult:
        """Process raw text of an FNOL document and return structured result."""
        extracted_fields = self.extractor.extract(text)
        result = self.router.evaluate(extracted_fields)
        return result
