import os
import requests
from google import genai
from .prompts import RAG_PROMPT_TEMPLATE

client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))


def call_ollama(prompt: str):
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "llama3",
                "prompt": prompt,
                "stream": False
            },
            timeout=60
        )
        response.raise_for_status()
        return response.json().get("response", "")
    except requests.exceptions.HTTPError as e:
        error_msg = e.response.text if e.response else str(e)
        print(f"Ollama HTTP error: {error_msg}")
        return "Sorry, unable to generate answer. Both Gemini and Ollama are unavailable."
    except Exception as e:
        print(f"Ollama fallback failed: {e}")
        return "Sorry, unable to generate answer. Both Gemini and Ollama are unavailable."


def generate_answer(query: str, retrieval_output: dict):
    #build the context string
    context_str = "\n\n".join(
        f"[Source {b['source_index']}] {b['doc_path']}\n{b['text']}"
        for b in retrieval_output["context_blocks"]
    )


    sources_str = "\n".join(
        f"[{idx}] {path}"
        for idx, path in retrieval_output["citation_map"].items()
    )

    ret_conf = retrieval_output["retrieval_confidence"]
    retrieval_confidence_str = (
        f"**Retrieval Confidence: {ret_conf['band']} ({ret_conf['score']}%)** "
        f"— {ret_conf['reason']}"
    )

    full_context = f"{retrieval_confidence_str}\n\n{context_str}\n\nSources:\n{sources_str}"

    prompt = RAG_PROMPT_TEMPLATE.format(query=query, context=full_context)
    try:
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key or api_key.strip() == "":
            print("Google API Key not found or empty, falling back to Ollama")
            return f"{retrieval_confidence_str}\n\n{call_ollama(prompt)}"
            
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        return f"{retrieval_confidence_str}\n\n{response.text}"
    except Exception as e:
        print(f"Gemini generation failed: {e}. Falling back to Ollama.")
        return f"{retrieval_confidence_str}\n\n{call_ollama(prompt)}"