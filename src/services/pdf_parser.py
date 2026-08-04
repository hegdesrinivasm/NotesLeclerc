from io import BytesIO

from pypdf import PdfReader


def extract_text_from_pdf(raw_content: bytes) -> str:
    reader = PdfReader(BytesIO(raw_content))
    pages = [page.extract_text() or "" for page in reader.pages]
    return "\n".join(pages).strip()
