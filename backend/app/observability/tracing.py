import os
from app.core.config import get_settings


def configure_langsmith() -> None:
    """Configure LangSmith using standard LangChain/LangGraph environment variables.

    LangGraph emits traces automatically when tracing is enabled. No secrets are logged.
    """
    s = get_settings()
    if s.langchain_tracing_v2 and s.langchain_api_key:
        os.environ["LANGCHAIN_TRACING_V2"] = "true"
        os.environ["LANGCHAIN_API_KEY"] = s.langchain_api_key
        os.environ["LANGCHAIN_PROJECT"] = s.langchain_project
