import tempfile

import whisper

_model = None


def _get_model() -> whisper.Whisper:
    global _model
    if _model is None:
        _model = whisper.load_model("base")
    return _model


def transcribe_audio(raw_content: bytes) -> str:
    model = _get_model()
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp:
        tmp.write(raw_content)
        tmp_path = tmp.name
    try:
        result = model.transcribe(tmp_path)
        return result["text"].strip()
    finally:
        import os

        os.unlink(tmp_path)
