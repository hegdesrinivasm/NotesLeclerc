# NotesLeclerc Design Spec

## Overview

NotesLeclerc is a Streamlit web application that converts lecture transcripts, PDFs, and audio recordings into structured bullet-point summaries. It uses local Whisper for audio transcription, pypdf for PDF parsing, and Azure OpenAI for LLM-powered summarization — all orchestrated via a LangGraph state graph.

## Goals

- Accept multiple input types: audio (mp3, wav, m4a), PDF, and plain text (txt, srt)
- Transcribe audio locally using OpenAI Whisper (no cloud transcription dependency)
- Extract text from PDFs via pypdf
- Summarize content into bullet points using Azure OpenAI (GPT-4o)
- Let users choose their preferred summary format at upload time
- Provide a clean Streamlit UI with progress indicators and export options

## Non-Goals (YAGNI)

- User authentication or multi-user support
- Database-backed history of summaries
- Real-time streaming of LLM output
- Support for video input (audio only)
- Custom prompt engineering UI

## Tech Stack

| Layer | Tool | Purpose |
|---|---|---|
| UI | Streamlit | Web interface |
| Orchestration | LangGraph + LangChain | Pipeline state graph |
| LLM | Azure OpenAI (GPT-4o) | Summarization |
| Audio transcription | openai-whisper (local) | Speech-to-text |
| PDF parsing | pypdf | Text extraction from PDFs |
| Config | python-dotenv | .env file loading |

## Project Structure

```
NotesLeclerc/
├── app.py                       # Streamlit entry point
├── .env                         # Azure credentials (gitignored)
├── .gitignore
├── requirements.txt
├── src/
│   ├── __init__.py
│   ├── graph/
│   │   ├── __init__.py
│   │   ├── state.py             # TypedDict state definition
│   │   ├── nodes.py             # Graph node functions
│   │   └── builder.py           # LangGraph graph construction
│   ├── services/
│   │   ├── __init__.py
│   │   ├── audio.py             # Whisper transcription service
│   │   ├── pdf_parser.py        # PDF text extraction
│   │   └── llm.py               # Azure OpenAI LLM wrapper
│   └── utils/
│       ├── __init__.py
│       └── chunking.py          # Text chunking logic
├── docs/
│   └── superpowers/
│       └── specs/
│           └── 2026-07-24-notesleclerc-design.md  (this file)
└── tests/                       # (future)
```

## LangGraph Pipeline

### State Definition

```python
from typing import TypedDict, Literal

class NotesState(TypedDict):
    file_type: Literal["audio", "pdf", "text"]
    raw_content: bytes
    filename: str
    text: str
    chunks: list[str]
    summary: str
    summary_format: Literal["topic_grouped", "sequential", "structured"]
```

### Graph Flow

```
[Start]
   │
   ▼
route_input ─────────────────────────────┐
   │                                     │
   ├── file_type == "audio" ──► transcribe
   │                                     │
   ├── file_type == "pdf" ────► parse_pdf
   │                                     │
   └── file_type == "text" ───► (skip to chunk)
                                         │
                                         ▼
                                      chunk
                                         │
                                         ▼
                                    summarize
                                         │
                                         ▼
                                       [End]
```

### Node Descriptions

| Node | Input | Output | Description |
|---|---|---|---|
| `route_input` | `raw_content`, `filename` | `file_type` | Inspects file extension to determine pipeline path |
| `transcribe` | `raw_content` | `text` | Runs local Whisper on audio bytes; returns transcribed text |
| `parse_pdf` | `raw_content` | `text` | Extracts text from PDF using pypdf |
| `chunk` | `text` | `chunks` | Splits text into ~3000-token segments with overlap |
| `summarize` | `chunks`, `summary_format` | `summary` | Sends chunks to Azure OpenAI with format-specific prompt; returns formatted bullet summary |

### Conditional Edges

```python
def route_after_input(state: NotesState) -> str:
    if state["file_type"] == "audio":
        return "transcribe"
    elif state["file_type"] == "pdf":
        return "parse_pdf"
    else:
        return "chunk"
```

## Streamlit UI

### Layout

1. **Sidebar** — Azure config status, summary format selector
2. **Main area** — File upload widget → Generate button → Progress → Results

### File Upload

- Accepts: `.pdf`, `.txt`, `.srt`, `.mp3`, `.wav`, `.m4a`
- Shows file name and size after upload

### Summary Format Options

| Key | Label | Description |
|---|---|---|
| `topic_grouped` | Topic-Grouped Bullets | Grouped by topic with nested bullets |
| `sequential` | Sequential Bullets | Key points in order of appearance |
| `structured` | Structured Sections | Sections: Key Concepts, Definitions, Examples, Takeaways |

### Progress Display

- Use `st.spinner` or `st.status` to show current pipeline stage
- Stages: "Uploading..." → "Transcribing..." / "Parsing PDF..." → "Chunking..." → "Summarizing..." → "Done!"

### Output

- Rendered as markdown via `st.markdown`
- Download as `.md` or `.txt`

## Azure OpenAI Configuration

Stored in `.env` file (gitignored):

```
AZURE_OPENAI_ENDPOINT=https://<resource>.openai.azure.com/
AZURE_OPENAI_KEY=<key>
AZURE_OPENAI_DEPLOYMENT=gpt-4o
AZURE_OPENAI_API_VERSION=2024-02-15-preview
```

LangChain integration via `langchain-openai`:

```python
from langchain_openai import AzureChatOpenAI

llm = AzureChatOpenAI(
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_key=os.getenv("AZURE_OPENAI_KEY"),
    deployment_name=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
)
```

## Summarization Prompts

### Topic-Grouped

```
You are a lecture notes summarizer. Given the following transcript,
produce a summary organized by topic. Use bullet points with nested
sub-bullets for details. Group related points under clear headings.

Transcript:
{chunk}

Summary:
```

### Sequential Bullets

```
You are a lecture notes summarizer. Given the following transcript,
produce a sequential list of key points as bullet points. Maintain the
order they appear in the lecture. Be concise — one line per bullet.

Transcript:
{chunk}

Summary:
```

### Structured Sections

```
You are a lecture notes summarizer. Given the following transcript,
produce structured notes with these sections:
- Key Concepts (main ideas discussed)
- Definitions (important terms defined)
- Examples (examples or illustrations given)
- Takeaways (most important points to remember)

Transcript:
{chunk}

Summary:
```

## Error Handling

| Error | Behavior |
|---|---|
| Unsupported file type | Show error in Streamlit, reject upload |
| Empty PDF (no extractable text) | Show warning, suggest OCR in future |
| Whisper transcription failure | Show error with details |
| Azure OpenAI API failure | Show error, suggest checking .env config |
| Text too long for single prompt | Chunking handles this; if chunks > 50, warn user |

## Dependencies (requirements.txt update)

```
pypdf
streamlit
langchain
langchain-openai
langgraph
openai-whisper
python-dotenv
```
