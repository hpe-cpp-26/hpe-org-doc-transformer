from doc_types.state import ClassifierState
from agent.llm import get_llm
from agent.prompts.fingerprint_prompt import FINGERPRINT_PROMPT
import json
import re
import logging

logger = logging.getLogger(__name__)


def _strip_json_fences(text: str) -> str:
    """Strip markdown code fences"""
    match = re.search(r"```(?:json)?\s*([\s\S]*?)```", text)
    if match:
        return match.group(1).strip()
    return text.strip()


def generate_fingerprint(state: ClassifierState) -> ClassifierState:
    """Generates a semantic fingerprint for the document."""
    llm = get_llm(thinking=False)

    try:
        prompt_value = FINGERPRINT_PROMPT.invoke({
            "content": state["content"],
            "source": state["source"],
            "title": state["title"],
            "metadata": state["metadata"],
        })

        llm_response = llm.invoke(prompt_value)
        response_text = getattr(llm_response, "content", str(llm_response))
        cleaned = _strip_json_fences(response_text)
        
        try:
            parsed = json.loads(cleaned)
            if isinstance(parsed, dict):
                if isinstance(parsed.get("fingerprint"), str):
                    rich_elements = []
                    
                    if parsed.get("project_identity"):
                        rich_elements.append(f"Project Identity: {parsed['project_identity']}")
                    if parsed.get("functional_domain"):
                        rich_elements.append(f"Functional Domain: {parsed['functional_domain']}")
                    if parsed.get("doc_intent"):
                        rich_elements.append(f"Document Intent: {parsed['doc_intent']}")
                    if parsed.get("lifecycle_stage"):
                        rich_elements.append(f"Lifecycle Stage: {parsed['lifecycle_stage']}")
                        
                    tech_concepts = parsed.get("technical_concepts")
                    if isinstance(tech_concepts, list) and tech_concepts:
                        rich_elements.append(f"Technical Concepts: {', '.join(str(c) for c in tech_concepts)}")
                        
                    key_entities = parsed.get("key_entities")
                    if isinstance(key_entities, list) and key_entities:
                        rich_elements.append(f"Key Entities: {', '.join(str(e) for e in key_entities)}")
                        
                    aliases = parsed.get("cross_tool_aliases")
                    if isinstance(aliases, list) and aliases:
                        rich_elements.append(f"Cross-Tool Aliases: {', '.join(str(a) for a in aliases)}")
                        
                    rich_elements.append(f"Summary: {parsed['fingerprint']}")
                    
                    state["fingerprint"] = "\n".join(rich_elements)
                else:
                    state["fingerprint"] = cleaned
                
                doc_type = parsed.get("doc_type", "").strip().lower()
                valid_types = {"troubleshooting", "design", "requirements", "runbook", "reference"}
                if doc_type in valid_types:
                    state["doc_type"] = doc_type
                else:
                    logger.warning(f"Invalid doc_type '{doc_type}' generated, falling back to 'reference'")
                    state["doc_type"] = "reference"
            else:
                state["fingerprint"] = cleaned
                state["doc_type"] = "reference"
        except json.JSONDecodeError as e:
            logger.error(
                f"Fingerprint JSON parse failed for doc '{state.get('title', 'unknown')}': {e}\n"
                f"Raw response: {response_text[:500]}"
            )
            state["fingerprint"] = cleaned
            state["doc_type"] = "reference"
            state.setdefault("errors", []).append(f"JSON parse error: {str(e)}")

    except Exception as e:
        logger.error(f"Error generating fingerprint for doc '{state.get('title', 'unknown')}': {e}")
        state["fingerprint"] = None
        state["doc_type"] = "reference"
        state.setdefault("errors", []).append(f"Error generating fingerprint: {str(e)}")

    return state