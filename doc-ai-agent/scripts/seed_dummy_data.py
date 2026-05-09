from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Sequence

from db.connection import get_connection
from db.vector_queries import insert_chunks, insert_document, update_centroid
from embedding.embedder import generate_embedding


@dataclass(frozen=True)
class SeedDoc:
    path: str
    title: str
    source: str
    body: str


@dataclass(frozen=True)
class SeedGroup:
    group_id: str
    name: str
    docs: Sequence[SeedDoc]


def _compose_content(group_name: str, doc: SeedDoc) -> str:
    return (
        f"Title: {doc.title}\n"
        f"Group: {group_name}\n"
        f"Source: {doc.source}\n\n"
        f"{doc.body}\n"
    )


def _avg_embedding(embeddings: Sequence[Sequence[float]]) -> list[float]:
    if not embeddings:
        raise ValueError("Cannot average empty embeddings")
    size = len(embeddings[0])
    totals = [0.0] * size
    for emb in embeddings:
        if len(emb) != size:
            raise ValueError("Embedding sizes do not match")
        for i, value in enumerate(emb):
            totals[i] += float(value)
    return [value / len(embeddings) for value in totals]


def _chunk_text(text: str, max_chars: int = 800) -> list[str]:
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    if not paragraphs:
        return [text]
    chunks: list[str] = []
    current: list[str] = []
    current_len = 0
    for para in paragraphs:
        if current_len + len(para) + 2 > max_chars and current:
            chunks.append("\n\n".join(current))
            current = [para]
            current_len = len(para)
        else:
            current.append(para)
            current_len += len(para) + 2
    if current:
        chunks.append("\n\n".join(current))
    return chunks


def _insert_groups(groups: Iterable[SeedGroup]) -> None:
    with get_connection() as connection:
        with connection.transaction():
            with connection.cursor() as cursor:
                for group in groups:
                    cursor.execute(
                        """
                        INSERT INTO groups (id, name, centroid, doc_count)
                        VALUES (%s, %s, NULL, 0)
                        ON CONFLICT (id) DO UPDATE SET
                            name = EXCLUDED.name
                        """,
                        [group.group_id, group.name],
                    )


def _seed_data(groups: Sequence[SeedGroup]) -> None:
    _insert_groups(groups)

    for group in groups:
        doc_embeddings: list[list[float]] = []
        chunk_rows: list[dict[str, object]] = []

        for doc in group.docs:
            content = _compose_content(group.name, doc)
            embedding = list(generate_embedding(content))
            doc_embeddings.append(embedding)

            document_id = f"{group.group_id}:{doc.path}"
            insert_document(
                document_id=document_id,
                path=doc.path,
                group_id=group.group_id,
                content=content,
                embedding=embedding,
            )

            for chunk in _chunk_text(content):
                chunk_rows.append(
                    {
                        "doc_id": document_id,
                        "group_id": group.group_id,
                        "chunk_text": chunk,
                        "embedding": list(generate_embedding(chunk)),
                    }
                )

        if doc_embeddings:
            centroid = _avg_embedding(doc_embeddings)
            update_centroid(group.group_id, centroid, doc_count=len(doc_embeddings))

        insert_chunks(chunk_rows)


def build_seed_groups() -> list[SeedGroup]:
    return [
        SeedGroup(
            group_id="payment-system",
            name="payment-system",
            docs=[
                SeedDoc(
                    path="root/payment-system/confluence/tech-stack.md",
                    title="Payment Tech Stack",
                    source="confluence",
                    body=(
                        "Services run on Python and Postgres with pgvector for embeddings. "
                        "The gateway integrates with card processors, wallet providers, and internal risk checks. "
                        "Async workers handle retries, idempotency, and webhook delivery. "
                        "Observability uses structured logs, trace IDs, and metrics for payment latency. "
                        "Key libraries: httpx for outbound calls, psycopg for database access."
                    ),
                ),
                SeedDoc(
                    path="root/payment-system/github/plan.md",
                    title="Payment Platform Plan",
                    source="github",
                    body=(
                        "Plan includes webhook hardening, idempotency keys, and improved failure handling "
                        "for settlement jobs. The roadmap adds per-merchant throttling, automatic payout "
                        "retries, and a daily reconciliation report. Short term focus is on reducing chargebacks "
                        "and improving fraud signals from device telemetry."
                    ),
                ),
                SeedDoc(
                    path="root/payment-system/jira/ticket1.md",
                    title="Payment Issue: Retry Logic",
                    source="jira",
                    body=(
                        "Ticket tracks retry backoff for transient gateway errors and alerts for repeated declines. "
                        "Acceptance criteria: exponential backoff with jitter, a max of 5 retries, and logging of "
                        "final failure states. Include metrics for retry count and duration per processor."
                    ),
                ),
            ],
        ),
        SeedGroup(
            group_id="self-healing-system",
            name="self-healing-system",
            docs=[
                SeedDoc(
                    path="root/self-healing-system/confluence/plan.md",
                    title="Self Healing Plan",
                    source="confluence",
                    body=(
                        "Plan focuses on incident classification, action routing, and safe rollback automation. "
                        "Phase 1 targets high-volume services with clear runbooks. "
                        "Phase 2 adds RCA enrichment and change correlation. "
                        "Success metrics: reduced MTTR and fewer on-call escalations."
                    ),
                ),
                SeedDoc(
                    path="root/self-healing-system/github/docs.md",
                    title="Self Healing Docs",
                    source="github",
                    body=(
                        "Documents health checks, alert thresholds, and remediation scripts for key services. "
                        "Includes expected signals for CPU saturation, memory leaks, and queue backlogs. "
                        "Runbooks cover restart procedures, feature flag toggles, and dependency failover."
                    ),
                ),
                SeedDoc(
                    path="root/self-healing-system/jira/issue.md",
                    title="Self Healing Issue: Noise Reduction",
                    source="jira",
                    body=(
                        "Issue covers reducing false positives in alerting and improving signal quality for automation triggers. "
                        "Tasks: remove flaky alerts, tune thresholds, and add a suppression window during deploys. "
                        "Outcome should reduce action loops caused by noisy signals."
                    ),
                ),
            ],
        ),
        SeedGroup(
            group_id="travel-planner-system",
            name="travel-planner-system",
            docs=[
                SeedDoc(
                    path="root/travel-planner-system/confluence/plan.md",
                    title="Travel Planner Plan",
                    source="confluence",
                    body=(
                        "Plan includes destination scoring, budget constraints, and calendar integration. "
                        "Phase 1 focuses on flight and hotel search. Phase 2 adds activities and routing. "
                        "KPIs: conversion rate, itinerary completion rate, and average planning time."
                    ),
                ),
                SeedDoc(
                    path="root/travel-planner-system/github/design.md",
                    title="Travel Planner Design",
                    source="github",
                    body=(
                        "Design outlines itinerary ranking, recommendation models, and caching strategies. "
                        "Ranking blends price, duration, and preference fit. "
                        "Caching includes provider responses with TTLs and invalidation on price changes."
                    ),
                ),
                SeedDoc(
                    path="root/travel-planner-system/jira/issue.md",
                    title="Travel Planner Issue: Provider Sync",
                    source="jira",
                    body=(
                        "Issue describes sync delays from providers and a plan for incremental updates. "
                        "Tasks include delta sync, retry policies, and alerting on provider failures. "
                        "Goal is to reduce stale inventory and booking errors."
                    ),
                ),
            ],
        ),
    ]


def main() -> None:
    groups = build_seed_groups()
    _seed_data(groups)


if __name__ == "__main__":
    main()
