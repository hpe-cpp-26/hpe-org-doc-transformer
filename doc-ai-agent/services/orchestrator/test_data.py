from doc_types.documents import NormalisedDocument

doc_auto_assign_payment = NormalisedDocument(
    doc_id="test-auto-assign-001",
    source="github",
    title="Payment Gateway Webhook Hardening",
    content="""
    Summary
    -------
    This document covers webhook hardening for the payment gateway service.
    It defines idempotency key handling, retry backoff strategies, and 
    failure state logging for settlement jobs.

    Implementation Notes
    --------------------
    All outbound webhook calls use exponential backoff with jitter.
    Maximum 5 retries per event. Final failure states are logged with
    trace IDs and forwarded to the reconciliation queue.

    Fraud signals from device telemetry are attached to each payment event
    for downstream risk evaluation. Per-merchant throttling is applied at
    the gateway layer to prevent abuse during high-volume windows.

    Metrics
    -------
    - retry_count per processor
    - chargeback rate per merchant
    - settlement job duration
    - webhook delivery latency (P95, P99)

    Dependencies
    ------------
    httpx for outbound calls, psycopg for Postgres access, pgvector for
    embedding-based fraud pattern matching.
    """,
    metadata={
        "author": "payments-team",
        "created_at": "2024-02-10",
        "project": "payment-system",
        "team": "backend",
        "status": "in-review",
        "tool": "github",
        "tags": ["payments", "webhook", "idempotency", "retry", "fraud"],
    },
)



doc_review_agent_self_healing = NormalisedDocument(
    doc_id="test-review-agent-001",
    source="confluence",
    title="Autonomous Fault Recovery — Design Notes",
    content="""
    Overview
    --------
    This document captures early design notes for an automated fault response
    capability being explored by the platform reliability team. The goal is to
    reduce manual intervention during production degradations by introducing
    programmatic corrective actions triggered by telemetry signals.

    Problem Statement
    -----------------
    On-call engineers currently spend significant time responding to alerts that
    follow predictable patterns — high CPU causing request queuing, memory pressure
    leading to OOM kills, downstream timeouts causing cascade failures. These
    scenarios have known resolution steps but no automated execution path.

    Proposed Approach
    -----------------
    Introduce a signal aggregation layer that consumes metrics, logs, and trace
    anomalies and maps them to a catalogue of corrective procedures. Each procedure
    has a risk classification (safe / supervised / manual-only). Safe procedures
    execute automatically; supervised ones page the engineer with a one-click
    approval flow before execution.

    Signal Sources
    --------------
    - Prometheus alerting rules (threshold breaches)
    - Log anomaly patterns (error rate spikes, repeated exception classes)
    - Distributed trace latency outliers (P99 degradation per service)

    Corrective Procedure Examples
    -----------------------------
    - Scale out: increase replica count when CPU saturation persists > 3 minutes
    - Circuit open: disable a flapping downstream dependency temporarily
    - Restart: pod restart for services showing memory growth without release
    - Flag toggle: disable a feature causing elevated error rates

    Open Questions
    --------------
    1. How do we prevent action loops when a corrective step itself causes signals?
    2. What is the right suppression window post-deployment to avoid false triggers?
    3. Should RCA enrichment happen before or after the corrective action fires?
    4. How do we correlate recent change events with incoming fault signals?

    Success Criteria
    ----------------
    Reduction in mean time to recovery for in-scope incident classes.
    Fewer escalations to senior engineers for routine fault patterns.
    Audit trail of every automated action with rollback capability.
    """,
    metadata={
        "author": "platform-reliability-team",
        "created_at": "2024-03-15",
        "project": "autonomous-fault-recovery",
        "team": "SRE",
        "status": "draft",
        "tool": "confluence",
        "tags": ["reliability", "automation", "fault-tolerance", "observability"],
    },
)


doc_create_new_group = NormalisedDocument(
    doc_id="test-create-new-001",
    source="confluence",
    title="ML Training Pipeline — Experiment Tracking Design",
    content="""
    Purpose
    -------
    This document defines the architecture for the internal ML training pipeline,
    covering dataset versioning, experiment tracking, model registry, and 
    promotion workflows for production deployment.

    Dataset Management
    ------------------
    Training datasets are versioned using DVC and stored in object storage (S3).
    Each dataset version is tagged with a schema hash to detect silent drift.
    Splits (train / val / test) are fixed per version to ensure reproducibility
    across experiment runs.

    Experiment Tracking
    -------------------
    MLflow is used to log hyperparameters, metrics, and artefacts per run.
    Each experiment is associated with a Git commit SHA and a dataset version tag.
    Runs are grouped by model family (classification, ranking, embedding).

    Training Infrastructure
    -----------------------
    GPU jobs run on Kubernetes using the training operator. Resource quotas are
    enforced per team. Spot instance interruptions are handled via checkpoint
    resumption — jobs save state every 500 steps.

    Model Registry and Promotion
    ----------------------------
    Trained models are registered in MLflow Model Registry with stage labels:
    Staging → Canary → Production. Promotion requires sign-off from a model
    reviewer and passing evaluation against a held-out benchmark dataset.

    Serving
    -------
    Production models are served via Triton Inference Server behind an internal
    gRPC gateway. Latency SLOs: P50 < 10ms, P99 < 50ms for embedding models.
    Model versions are shadowed before full cutover to detect regression.

    Monitoring
    ----------
    Feature drift is detected using PSI scores computed daily against the
    training distribution. Alerts fire when PSI > 0.2 for any top-20 feature.
    Prediction confidence histograms are logged per model per hour.
    """,
    metadata={
        "author": "ml-platform-team",
        "created_at": "2024-04-01",
        "project": "ml-training-pipeline",
        "team": "ml-platform",
        "status": "active",
        "tool": "confluence",
        "tags": ["ml", "training", "mlflow", "model-registry", "experiment-tracking"],
    },
)

