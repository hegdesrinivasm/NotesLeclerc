from src.graph.state import NotesState
from src.services.audio import transcribe_audio
from src.services.llm import summarize_chunk
from src.services.pdf_parser import extract_text_from_pdf
from src.utils.chunking import chunk_text

AUDIO_EXTENSIONS = {".mp3", ".wav", ".m4a", ".ogg", ".flac"}
PDF_EXTENSIONS = {".pdf"}
TEXT_EXTENSIONS = {".txt", ".srt", ".md", ".vtt"}


def route_input(state: NotesState) -> NotesState:
    filename = state["filename"].lower()
    for ext in AUDIO_EXTENSIONS:
        if filename.endswith(ext):
            return {"file_type": "audio"}
    for ext in PDF_EXTENSIONS:
        if filename.endswith(ext):
            return {"file_type": "pdf"}
    return {"file_type": "text", "text": state["raw_content"].decode("utf-8", errors="replace")}


def transcribe(state: NotesState) -> NotesState:
    text = transcribe_audio(state["raw_content"])
    return {"text": text}


def parse_pdf(state: NotesState) -> NotesState:
    text = extract_text_from_pdf(state["raw_content"])
    return {"text": text}


def chunk(state: NotesState) -> NotesState:
    return {"chunks": chunk_text(state["text"])}


def summarize(state: NotesState) -> NotesState:
    summary_format = state.get("summary_format", "sequential")
    parts = [summarize_chunk(c, summary_format) for c in state["chunks"]]
    return {"summary": "\n\n".join(parts)}
