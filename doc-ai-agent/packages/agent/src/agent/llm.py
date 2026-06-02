from __future__ import annotations

import threading
from functools import lru_cache
from typing import Iterable

from langchain_groq import ChatGroq
from langchain_ollama import ChatOllama
from config.settings import get_settings

settings = get_settings(service_name="agent")
USE_LOCAL =False


def split_keys(raw_keys: str | None) -> list[str]:
    if not raw_keys:
        return []
    parts = [item.strip() for item in raw_keys.replace("\n", ",").split(",")]
    return [item for item in parts if item]


class GroqPool:
    """
    Every call (invoke / ainvoke / stream) goes to the NEXT key.
    Call 1 → key[0], Call 2 → key[1], ..., Call N+1 → key[0]
    """

    def __init__(self, models: list[ChatGroq]) -> None:
        self._models = models
        self._counter = 0
        self._lock = threading.Lock()

    def _next(self) -> ChatGroq:
        with self._lock:
            idx = self._counter % len(self._models)
            self._counter += 1
        return self._models[idx]

  
    def invoke(self, *args, **kwargs):
        return self._next().invoke(*args, **kwargs)

    async def ainvoke(self, *args, **kwargs):
        return await self._next().ainvoke(*args, **kwargs)

    def stream(self, *args, **kwargs):
        return self._next().stream(*args, **kwargs)

    def bind(self, **kwargs) -> "GroqPool":
        return GroqPool([m.bind(**kwargs) for m in self._models])

    def bind_tools(self, tools: Iterable, **kwargs) -> "GroqPool":
        return GroqPool([m.bind_tools(tools, **kwargs) for m in self._models])

    def __getattr__(self, name: str):
        return getattr(self._models[0], name)


@lru_cache(maxsize=4)
def get_llm(thinking: bool = False) -> ChatOllama | ChatGroq | GroqPool:
    if USE_LOCAL:
        return ChatOllama(model="qwen3:14b", temperature=0, num_ctx=16384)

    raw_keys = settings.groq_api_keys or settings.groq_api_key
    api_keys = split_keys(raw_keys)
    if not api_keys:
        raise ValueError("Set groq_api_key or groq_api_keys.")

    models = [
        ChatGroq(model="qwen/qwen3-32b", api_key=k, temperature=0, reasoning_effort="none")
        for k in api_keys
    ]

    return models[0] if len(models) == 1 else GroqPool(models)