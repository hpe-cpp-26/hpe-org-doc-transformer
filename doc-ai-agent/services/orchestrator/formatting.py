from __future__ import annotations

from doc_types.documents import NormalisedDocument

SEPARATOR = "=" * 70
THIN_SEP = "-" * 70
SECTION = "·" * 70


def format_candidates(candidates: list[dict] | None, limit: int = 5) -> list[dict]:
    if not candidates:
        return []
    return [
        {
            "id": item.get("id") or item.get("group_id"),
            "name": item.get("name"),
            "similarity": round(item.get("similarity") or item.get("score") or 0.0, 4),
        }
        for item in candidates[:limit]
    ]


def badge(route: str | None) -> str:
    return {
        "AUTO_ASSIGN": "OK  AUTO_ASSIGN",
        "REVIEW_BY_AGENT": "AI  REVIEW_BY_AGENT",
        "CREATE_NEW_GROUP": "NEW CREATE_NEW_GROUP",
    }.get(route or "", f"??  {route}")


def print_doc_header(doc: NormalisedDocument) -> None:
    print(f"\n{SEPARATOR}")
    print(f"  DOC    : {doc.doc_id}")
    print(f"  TITLE  : {doc.title or '-'}")
    print(f"  SOURCE : {doc.source}")
    print(SEPARATOR)


def print_result(state: dict) -> None:
    route = state.get("classification_route")
    score = state.get("top_similarity_score")
    candidates = format_candidates(state.get("similar_group_candidates"))
    decision = state.get("agent_decision")
    errors = state.get("errors") or []
    
    print(f"\n  {'is_valid':<22}: {state.get('is_valid')}")
    print(f"  {'is_duplicate':<22}: {state.get('is_duplicate')}")
    if state.get("fingerprint") is not None:
        print(f"  {'fingerprint':<22}: {state.get('fingerprint')}")
    if state.get("existing_group_id"):
        print(f"  {'existing_group_id':<22}: {state['existing_group_id']}")

    print(f"\n{THIN_SEP}")
    print("  VECTOR SEARCH")
    print(THIN_SEP)
    score_str = f"{score:.4f}" if score is not None else "-"
    print(f"  {'top_similarity_score':<22}: {score_str}")
    if candidates:
        print(f"  {'candidates':<22}:")
        for c in candidates:
            print(f"    - {c['id']:<30} score={c['similarity']}")
    else:
        print(f"  {'candidates':<22}: none")

    print(f"\n{THIN_SEP}")
    print("  CLASSIFICATION")
    print(THIN_SEP)
    print(f"  route      : {badge(route)}")
    print(f"  decision   : {state.get('decision_path') or '-'}")
    print(f"  assigned   : {state.get('assigned_group_id') or '-'}")
    print(f"  create_new : {state.get('create_new_group')}")

    if decision:
        print(f"\n{THIN_SEP}")
        print("  AGENT DECISION")
        print(THIN_SEP)
        print(f"  decision   : {decision.get('decision')}")
        print(f"  group      : {decision.get('assigned_group_id') or '-'}")
        print(f"  confidence : {decision.get('confidence', 0.0):.2f}")
        print("  reasoning  :")
        reasoning = decision.get("reasoning", "-")
        for line in reasoning.split(". "):
            if line:
                print(f"    {line.strip()}.")

    if errors:
        print(f"\n{THIN_SEP}")
        print("  ERRORS")
        print(THIN_SEP)
        for err in errors:
            print(f"    - {err}")

    print(f"\n{SEPARATOR}\n")

