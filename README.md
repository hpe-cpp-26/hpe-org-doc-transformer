# HPE CPP — Weekly Progress
**Transforming Organisational Docs using Doc AI Agent**

---

## Table of Contents

- [Phase 1 — Exploration & Learning](#phase-1--exploration--learning)
- [Week 2 — PoC: Content Comparison](#week-2--poc-content-comparison)
- [Week 3 — PoC: AI Document Agent](#week-3--poc-ai-document-agent)
- [Week 4 — Team PoC: Travel Planner Agent (Planning)](#week-4--team-poc-travel-planner-agent-planning)
- [Week 5 — Team PoC: Travel Planner Agent (Build) + Project Kickoff](#week-5--team-poc-travel-planner-agent-build--main-project-kickoff)
- [Week 6 — Project: Architecture & Design](#week-6--transforming-organisational-docs-using-doc-ai-agent)
- [Week 7 — Project: Implementation and Review ](#week-7--transforming-organisational-docs-using-doc-ai-agent)
- [Week 8 — Project: Implementation and Review](#week-8--transforming-organisational-docs-using-doc-ai-agent)
- [Week 9 — Project: Implementation and Review](#week-9--transforming-organisational-docs-using-doc-ai-agent)
- [Week 10 — Project: Implementation and Review](#week-10--transforming-organisational-docs-using-doc-ai-agent)
- [Week 11 — Project: Implementation and Review](#week-11--transforming-organisational-docs-using-doc-ai-agent)
- [Week 12 — Project: Implementation and Review](#week-12--transforming-organisational-docs-using-doc-ai-agent)

---

## Phase 1 — Exploration & Learning

**`2/18/2026 – 3/4/2026`**

### What We Did

- Explored and understood the core technologies involved in the project.
- Mentor shared curated resources and links to get familiar with the stack.

### Technologies Covered

| Area        | Topics                           |
| ----------- | -------------------------------- |
| AI/ML       | LLMs, Agentic AI Development     |
| Language    | Python                           |
| Integration | API Clients, MCP Servers & Tools |

### Expected Outcome

> Build foundational understanding of all key technologies before starting hands-on work.

---

## Week 2 — PoC: Content Comparison

**`3/5/2026 – 3/11/2026`**

### Mentor Discussion

- Reviewed and discussed topics from Phase 1.

### Task Assigned

Build a small PoC that **compares content from two sources** and lists similar content using an LLM.

**Requirements:**

- Use **Gemini** and **Ollama** based LLM models
- Each team member builds independently

### What We Built

Each team member individually implemented a **RAG-based project** for content comparison using sources such as:

- GitHub repositories
- Jira tickets
- Local file documents

---

## Week 3 — PoC: AI Document Agent

**`3/12/2026 – 3/18/2026`**

### Mentor Discussion

- Reviewed and discussed the content comparison PoC from Week 2.

### Task Assigned

Build a small PoC for an **AI Agent that reads documents from various sources**.

**Requirements:**

- Use **LangChain Framework**
- Integrate tools with an LLM

### What We Built

Each team member independently built an AI Agent with access to multiple tools, including:

- GitHub document reader
- Jira document reader
- Document summarisation tool

### Expected Outcome

> Understand tool integration with LLM agents using the LangChain framework.

---

## Week 4 — Team PoC: Travel Planner Agent (Planning)

**`3/18/2026 – 3/25/2026`**

### Mentor Discussion

- Reviewed Week 3 agents — discussed how agents work and what tools are.
- Kicked off first **team project**.

### Task Assigned

Build a **Travel Planner AI Agent** using an MCP Server.

**Agent Capabilities:**

1. Search Flights
2. Search Hotels
3. Search Places
4. Get Weather Information
5. Optimise results based on Budget

---

## Week 5 — Team PoC: Travel Planner Agent (Build) + Main Project Kickoff

**`3/25/2026 – 4/1/2026`**

### What We Built

Collaborated as a team and delivered the Travel Planner Agent.

**Team Split:**

| Sub-team | Responsibility  |
| -------- | --------------- |
| Team A   | Travel AI Agent |
| Team B   | MCP Server      |

- Used **FastMCP** to build the MCP server.

**Architecture Diagram:**
![Project Architecture](https://github.com/user-attachments/assets/4eb8d107-6a4e-43d9-8d72-96896c62e397)
**Repo:** `https://github.com/Dharshansk16/travel-planner`

### Main Project Kickoff

After completing the travel agent PoC, the mentor introduced the **main project**.

#### Problem Statement

In large organisations like HPE, different teams use different documentation tools, leading to:

**1. Data Fragmentation**

- Docs scattered across multiple tools
  - **Miro** → Diagrams & Architectures
  - **Figma** → UI Designs
  - **WikiFlex** → Project Docs
  - Other internal documents

**2. No Single Source of Truth**
Teams struggle with:

- Knowing what has recently changed
- Identifying which version of a document is current
- Locating all documents related to a project

#### Task for Next Week

Come up with a **project plan and architecture** for solving this problem.

> **Project:** Event-Driven Knowledge Integration System using a Doc AI Agent

---

## Week 6 — Transforming Organisational Docs Using Doc AI Agent

**`4/1/2026 – 4/8/2026`**

### Our Solution — Event-Driven Knowledge Integration System

**Architecture Diagram:**
![Project Architecture](https://github.com/user-attachments/assets/499f5a7e-5c86-4f89-a179-4bcd588ec594)

#### Component Breakdown

**1. Webhook Integrations**

- Miro (Webhook + REST API)
- Figma (Webhook)
- Confluence (Webhook)

**2. Connectors Layer**

- Each tool has a dedicated connector.
- Connectors publish only **metadata** (not full content) to the message broker — avoids queue overload.
- Webhooks signal that a specific entity has changed and needs to be updated.

**3. Message Broker / Event Bus**

- RabbitMQ or Kafka
- Pub/Sub model

**4. Knowledge Service Layer**

- Subscribes to events from the message queue.
- Fetches full content via REST APIs.
- Scheduled fetching to avoid API rate limits.

**5. Data Normalisation**

- Fetched data is normalised into a standard format before storage.

**6. GitHub Integration**

- Used as the **central repository**.
- Handles **versioning** of all normalised documents.

**7. AI Agent + MCP Server** 

- **AI Agent** correlates similar documents and groups them together.
- **MCP Server** exposes tools to the agent:
  - Fetch existing documents
  - Perform similarity search
  - Get similarity score
  - If similar — update the path of the new/updated document to the relevant group

  ### First Phase of Project Implementation

![Project Architecture](https://raw.githubusercontent.com/nihalshetty3/Hpe-mini-project/main/FirstPhaseArch.png)

This image represents the initial working implementation of our proposed architecture.  
It focuses on the first phase of the pipeline where webhook events are captured, processed, and routed through queues.  
The objective was to validate real-time document sync, event flow, and service communication.  
This serves as the foundation for the complete AI-powered knowledge integration system.


## Week 7 — Transforming Organisational Docs Using Doc AI Agent

**`4/8/2026 – 4/22/2026`**
The meeting focused on planning and beginning implementation of the first project phase, specifically knowledge ingestion. The team discussed webhooks, connectors, message queues, normalization, and finalized the tech stack. The mentor advised starting implementation and presenting progress in the next meeting.

## Week 8 — Transforming Organisational Docs Using Doc AI Agent

**`4/22/2026 – 4/29/2026`**

In Week 8, we presented the architecture for the classification component of the project to our mentor. The proposed approach begins by receiving normalized data and checking whether the document ID already exists. If it does, the system retrieves the corresponding group path and updates the existing document in the central GitHub repository.

For new documents, a vector search is performed against group centroids to identify relevant groups. Based on the confidence score:

High confidence leads to assigning the document to an existing group.
Low confidence results in creating a new group for the document.
Medium confidence (ambiguous cases) is handled using an agent with MCP for further resolution.

If the ambiguity persists even after LLM-based processing, the system falls back to human review.
<img width="1023" height="871" alt="Screenshot 2026-04-30 at 10 47 57 AM" src="https://github.com/user-attachments/assets/9b3d54d4-e63c-430f-909d-3d0e5d30bec2" />

## Week 9 — Transforming Organisational Docs Using Doc AI Agent

**`4/29/2026 – 5/6/2026`**

This week focused on a checkpoint demo to showcase the progress made so far. Each team presented their respective contributions.
Team 1 demonstrated the knowledge ingestion pipeline, covering the flow from webhooks to connectors, message queue handling, knowledge extraction via REST API, and the normalization process.
Team 2 presented progress on the classification component, including project setup, logging configuration, database setup using PostgreSQL with pgvector, embedding model integration, and implementation of duplication checks along with vector search using confidence scores.
The mentor reviewed and recorded the demos. Feedback for the next week included improving the normalization logic and presenting progress on MCP and agent development.

## Week 10 — Transforming Organisational Docs Using Doc AI Agent

**`5/6/2026 – 5/13/2026`**

The core agent and workflow pipeline were successfully implemented and demonstrated. At this stage, MCP tools had been integrated and were functioning as expected within the workflow.
We also demonstrated the progress made in the data ingestion pipeline. An example demo was shown to explain how documents with high correlation are directly classified using normal vector search. For documents with lower confidence scores, the agent takes over the classification process by leveraging MCP tools.
One of the MCP tools demonstrated was the fetch_group_readme tool. Based on the identified group, this tool fetches the corresponding group README from the central GitHub store. The README contains a summary of the group, providing the LLM with additional context to improve document classification accuracy and determine the most relevant group for the document.
The mentor reviewed the progress and advised us to complete the integration between the data ingestion pipeline and the agent workflow by next week.

## Week 11 — Transforming Organisational Docs Using Doc AI Agent

**`5/13/2026 – 5/29/2026`**

### Similarity Search Optimisation 
Identified a key limitation in the current approach: as the number of documents in a group grows, the single centroid drifts toward the geometric centre of the embedding space and no longer represents the actual meaning of the group's documents. This makes cosine similarity search less accurate.

> Current Implementation
  - For every new normalised document, we first convert this to embedding and then do a cosine
    similarity search against the group centroids (mean of all doc embeddings of that group)
  - fetch k similar groups that are closest and return to the llm for classification 


> Problem with the approach
   - This above solution works well when number of docs in a group are less
   - But if the number of docs in a group increases the centroid does not really reflect the actual meaning 
     of the docs  it comes down to the geometric centre
   - During cosine similarity search the doc is not actually representing the correct meaning of the group
   - Also having just one centroid per group will compress all the information into a 756 dim embedding.

<img width="1204" height="401" alt="image" src="https://github.com/user-attachments/assets/9d433522-9e96-4755-bcf1-055995691ddc" />

> Planned solution to the above problem
 - Instead of having one centroid per group, we can have multiple medoids per group
 - Plan here is to implement kmeans clustering across a group
 - this approach will significantly improve the precision since the medoids will always be at the centre
   of the cluster representing the actual meaning of ther documents
   
<img width="1334" height="493" alt="image" src="https://github.com/user-attachments/assets/acbd4f09-f346-46cd-bfc3-64efc36443f8" />

## Week 12 — Transforming Organisational Docs Using Doc AI Agent

**`5/29/2026 – 6/4/2026`**

> What Was Done
- Presented a complete end-to-end demo of the project to the mentor.
The demo used GitHub and Confluence as the two classification targets, walking through the full pipeline from document ingestion to classification.
Explained the system architecture end-to-end, covering how documents are normalised, embedded, clustered using medoids, and classified via cosine similarity search.
> 
<img width="1181" height="585" alt="image" src="https://github.com/user-attachments/assets/02c784f8-f4ad-43af-b9f9-d47c78617cfd" />

> Mentor Feedback
- Build a search interface using RAG on top of the current system, allowing users to query across the classified documents.
Extend the classification to a higher-level folder structure — currently documents are only classified by source (GitHub / Confluence). The new requirement is to also classify each document by type:
Requirements
Design
Troubleshooting

> Next Steps
- Implement the higher-level document type classification layer (Requirements / Design / Troubleshooting) on top of the existing source-level  classification.
Build out the RAG-based search interface

_Last updated: June 2026_
