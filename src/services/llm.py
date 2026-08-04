import os

from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI

load_dotenv()

SUMMARY_PROMPTS = {
    "topic_grouped": (
        "You are a lecture notes summarizer. Given the following transcript, "
        "produce a summary organized by topic. Use bullet points with nested "
        "sub-bullets for details. Group related points under clear headings.\n\n"
        "Transcript:\n{chunk}\n\nSummary:"
    ),
    "sequential": (
        "You are a lecture notes summarizer. Given the following transcript, "
        "produce a sequential list of key points as bullet points. Maintain the "
        "order they appear in the lecture. Be concise - one line per bullet.\n\n"
        "Transcript:\n{chunk}\n\nSummary:"
    ),
    "structured": (
        "You are a lecture notes summarizer. Given the following transcript, "
        "produce structured notes with these sections:\n"
        "- Key Concepts (main ideas discussed)\n"
        "- Definitions (important terms defined)\n"
        "- Examples (examples or illustrations given)\n"
        "- Takeaways (most important points to remember)\n\n"
        "Transcript:\n{chunk}\n\nSummary:"
    ),
}


def get_llm() -> AzureChatOpenAI:
    return AzureChatOpenAI(
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        api_key=os.getenv("AZURE_OPENAI_KEY"),
        deployment_name=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
        api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
        temperature=0.3,
    )


def summarize_chunk(chunk: str, summary_format: str) -> str:
    llm = get_llm()
    prompt = SUMMARY_PROMPTS[summary_format].format(chunk=chunk)
    response = llm.invoke(prompt)
    return response.content
