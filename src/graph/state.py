from typing import Literal, TypedDict


class NotesState(TypedDict, total=False):
    file_type: Literal["audio", "pdf", "text"]
    raw_content: bytes
    filename: str
    text: str
    chunks: list[str]
    summary: str
    summary_format: Literal["topic_grouped", "sequential", "structured"]
