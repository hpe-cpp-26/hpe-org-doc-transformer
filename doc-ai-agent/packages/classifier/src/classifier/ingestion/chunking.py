from langchain_text_splitters import RecursiveCharacterTextSplitter
from tokenizers import Tokenizer
from typing import Any

_tokenizer = Tokenizer.from_pretrained("nomic-ai/nomic-embed-text-v1")

def _count_tokens(text: str) -> int:
    return len(_tokenizer.encode(text, add_special_tokens=False))


def _make_splitter(chunk_size: int, overlap: int) -> RecursiveCharacterTextSplitter:
    return RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=overlap,
        length_function=_count_tokens,
        separators=["\n\n", "\n", ". ", "! ", "? ", " ", ""],
        keep_separator=True,
    )

_CHUNK_RULES: dict[str, tuple[int, int]] = {
    "prose":    (512, 64),
    "report":   (1024, 128),
    "code":     (384, 48),
    "list":     (256, 32),
    "short":    (0, 0), 
}

def chunk_document(text: str, doc_info: dict) -> list[dict[str, Any]]:
    doc_type = doc_info.get("doc_type") or "prose"
    title    = doc_info.get("title") or ""

    if doc_type == "short":
        chunk_text = f"{title}\n\n{text}" if title else text
        return [{
            "chunk_index": 0,
            "chunk_text":  chunk_text,
            "word_count":  len(chunk_text.split()),
            "token_count": _count_tokens(chunk_text),
        }]

    chunk_size, overlap = _CHUNK_RULES.get(doc_type, _CHUNK_RULES["prose"])
    splitter = _make_splitter(chunk_size, overlap)

    
    source = f"{title}\n\n{text}" if title else text
    raw_chunks = splitter.split_text(source)

    return [
        {
            "chunk_index": i,
            "chunk_text":  chunk,
            "word_count":  len(chunk.split()),
            "token_count": _count_tokens(chunk),
        }
        for i, chunk in enumerate(raw_chunks)
    ]
