import os

import streamlit as st

from src.graph.builder import build_graph

ALLOWED_EXTENSIONS = (".pdf", ".txt", ".srt", ".md", ".vtt", ".mp3", ".wav", ".m4a", ".ogg", ".flac")

SUMMARY_FORMATS = {
    "topic_grouped": "Topic-Grouped Bullets",
    "sequential": "Sequential Bullets",
    "structured": "Structured Sections",
}

st.set_page_config(page_title="NotesLeclerc", page_icon="📝", layout="wide")

st.title("📝 NotesLeclerc")
st.caption("Convert lectures, transcripts, and PDFs into structured bullet summaries.")

sidebar = st.sidebar
sidebar.header("Configuration")

azure_configured = all(
    os.getenv(var)
    for var in ("AZURE_OPENAI_ENDPOINT", "AZURE_OPENAI_KEY", "AZURE_OPENAI_DEPLOYMENT")
)
sidebar.success("Azure OpenAI configured ✓") if azure_configured else sidebar.warning(
    "Azure OpenAI not configured. Create a `.env` file with AZURE_OPENAI_* variables."
)

summary_format = sidebar.selectbox(
    "Summary format",
    options=list(SUMMARY_FORMATS.keys()),
    format_func=lambda key: SUMMARY_FORMATS[key],
)

uploaded_file = st.file_uploader(
    "Upload a lecture file",
    type=[ext.lstrip(".") for ext in ALLOWED_EXTENSIONS],
    help="PDF, text transcript, or audio recording",
)

if uploaded_file is not None:
    filename = uploaded_file.name
    raw_content = uploaded_file.getvalue()
    st.info(f"File loaded: **{filename}** ({len(raw_content) / 1024:.1f} KB)")

    if st.button("Generate Summary", type="primary"):
        graph = build_graph()
        with st.status("Processing…", expanded=True) as status:
            st.write("Starting pipeline…")
            result = graph.invoke(
                {
                    "filename": filename,
                    "raw_content": raw_content,
                    "summary_format": summary_format,
                }
            )
            status.update(label="Done!", state="complete", expanded=False)

        st.subheader("Summary")
        st.markdown(result["summary"])

        st.download_button(
            "Download as Markdown",
            data=result["summary"],
            file_name=f"{os.path.splitext(filename)[0]}-summary.md",
            mime="text/markdown",
        )
        st.download_button(
            "Download as Text",
            data=result["summary"],
            file_name=f"{os.path.splitext(filename)[0]}-summary.txt",
            mime="text/plain",
        )
