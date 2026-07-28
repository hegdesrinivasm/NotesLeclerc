# NotesLeclerc

A lecture notes summarizer that converts PDFs, text transcripts, and audio recordings into structured bullet-point summaries. Built with Streamlit, LangGraph, and Azure OpenAI.

## Features

- **Multiple input types** — Upload PDFs, text files (.txt, .srt), or audio recordings (.mp3, .wav, .m4a)
- **Local audio transcription** — Transcribes audio on-device using OpenAI Whisper (no cloud STT needed)
- **PDF text extraction** — Extracts text directly from lecture slides and PDFs
- **LLM-powered summarization** — Uses Azure OpenAI (GPT-4o) for intelligent summarization
- **Multiple summary formats** — Choose between Topic-Grouped, Sequential, or Structured Notes
- **Export** — Download summaries as Markdown or plain text

## Tech Stack

| Component | Tool |
|---|---|
| UI | Streamlit |
| Pipeline orchestration | LangGraph + LangChain |
| LLM | Azure OpenAI (GPT-4o) |
| Audio transcription | OpenAI Whisper (local) |
| PDF parsing | pypdf |

## Setup

### Prerequisites

- Python 3.9+
- An Azure OpenAI resource with a GPT-4o deployment

### Installation

```bash
git clone https://github.com/<your-username>/NotesLeclerc.git
cd NotesLeclerc
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Configuration

Create a `.env` file in the project root:

```
AZURE_OPENAI_ENDPOINT=https://<your-resource>.openai.azure.com/
AZURE_OPENAI_KEY=<your-key>
AZURE_OPENAI_DEPLOYMENT=gpt-4o
AZURE_OPENAI_API_VERSION=2024-02-15-preview
```

### Running

```bash
streamlit run app.py
```

## Project Structure

```
NotesLeclerc/
├── app.py                  # Streamlit entry point
├── src/
│   ├── graph/              # LangGraph pipeline
│   ├── services/           # Whisper, PDF parser, LLM wrapper
│   └── utils/              # Text chunking
└── docs/
    └── superpowers/specs/  # Design specifications
```
