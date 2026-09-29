import os
from pathlib import Path
import pypdf

class DocumentLoader:
    """Utility class to read text content from PDF and TXT FNOL documents."""

    @staticmethod
    def load_document(file_path: str) -> str:
        """
        Reads text content from a given file (.txt or .pdf).
        Returns plain text string.
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Document file not found: {file_path}")

        ext = path.suffix.lower()
        if ext in ['.txt', '.text', '.log']:
            return DocumentLoader._load_txt(path)
        elif ext == '.pdf':
            return DocumentLoader._load_pdf(path)
        else:
            # Attempt plain text read as fallback
            try:
                return DocumentLoader._load_txt(path)
            except Exception as e:
                raise ValueError(f"Unsupported file format '{ext}'. Only .pdf and .txt are supported.") from e

    @staticmethod
    def _load_txt(path: Path) -> str:
        with open(path, 'r', encoding='utf-8', errors='replace') as f:
            return f.read().strip()

    @staticmethod
    def _load_pdf(path: Path) -> str:
        text_content = []
        try:
            reader = pypdf.PdfReader(str(path))
            for i, page in enumerate(reader.pages):
                page_text = page.extract_text()
                if page_text:
                    text_content.append(page_text)
            return "\n\n".join(text_content).strip()
        except Exception as e:
            raise RuntimeError(f"Error reading PDF file '{path}': {str(e)}") from e
