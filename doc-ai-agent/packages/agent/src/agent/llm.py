from __future__ import annotations

import threading
from functools import lru_cache
from typing import Iterable

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
from config.settings import get_settings
from langchain_ollama import ChatOllama

settings = get_settings(service_name="agent")

USE_LOCAL = settings.use_local


def split_keys(raw_keys: str | None) -> list[str]:
    if not raw_keys:
        return []
    parts = [item.strip() for item in raw_keys.replace("\n", ",").split(",")]
    return [item for item in parts if item]


class GroqPool:
    def __init__(
        self,
        models: list[ChatGroq],
    ) -> None:
        self.models = models
        self._index = 0
        self.lock = threading.Lock()

    def _next_index(self) -> int:
        with self.lock:
            idx = self._index
            self._index = (self._index + 1) % len(self.models)
            return idx

    def invoke(self, *args, **kwargs):
        idx = self._next_index()
        return self.models[idx].invoke(*args, **kwargs)

    async def ainvoke(self, *args, **kwargs):
        idx = self._next_index()
        return await self.models[idx].ainvoke(*args, **kwargs)

    def stream(self, *args, **kwargs):
        idx = self._next_index()
        return self.models[idx].stream(*args, **kwargs)

    
    def bind(self, **kwargs):
        bound_models = [model.bind(**kwargs) for model in self.models]
        return GroqPool(bound_models)

    def bind_tools(self, tools: Iterable, **kwargs):
        bound_models = [model.bind_tools(tools, **kwargs) for model in self.models]
        return GroqPool(bound_models)

    def __getattr__(self, name: str):
        return getattr(self.models[0], name)


@lru_cache(maxsize=4)
def get_llm(thinking: bool = False) -> ChatGoogleGenerativeAI | ChatGroq | ChatOllama | GroqPool:
    
    if USE_LOCAL:
        return ChatOllama(
            model="qwen3:14b",
            temperature=0,   
            num_ctx=16384,
        )

    raw_keys = settings.groq_api_keys or settings.groq_api_key
    api_keys = split_keys(raw_keys)
    if not api_keys:
        raise ValueError("Groq API key not configured. Set groq_api_key or groq_api_keys.")

    models = [
        ChatGroq(
            model="qwen/qwen3-32b",
            api_key=key,
            temperature=0,
            reasoning_effort="none",
        )
        for key in api_keys
    ]

    if len(models) == 1:
        return models[0]

    return GroqPool(models)

    
    # return ChatGoogleGenerativeAI(
    #     model=settings.agent_model,
    #     google_api_key=settings.google_api_key,
    #     temperature=0 if not thinking else 1,
    #     model_kwargs={"thinking_budget": 1024 if thinking else 0},
    # )