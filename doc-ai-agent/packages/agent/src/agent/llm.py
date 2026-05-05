from functools import lru_cache
from langchain_google_genai import ChatGoogleGenerativeAI
from config.settings import get_settings

settings = get_settings(service_name="agent")

@lru_cache(maxsize=4)
def get_llm(thinking: bool = False) -> ChatGoogleGenerativeAI:
    """"""
    model = settings.agent_model
    extra = {}
    if thinking:
        extra["thinking_budget"] = 1024
    else:
        extra["thinking_budget"] = 0

    return ChatGoogleGenerativeAI(
        model=model,
        google_api_key=settings.google_api_key,
        temperature=0 if not thinking else 1, 
        model_kwargs=extra if extra else {},
    )
