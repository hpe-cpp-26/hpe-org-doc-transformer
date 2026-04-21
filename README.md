# HPE CPP — Weekly Progress
**Transforming Organisational Docs using Doc AI Agent**

---

## Table of Contents

- [Phase 1 — Exploration & Learning](#phase-1--exploration--learning)
- [Week 2 — PoC: Content Comparison](#week-2--poc-content-comparison)
- [Week 3 — PoC: AI Document Agent](#week-3--poc-ai-document-agent)
- [Week 4 — Team PoC: Travel Planner Agent (Planning)](#week-4--team-poc-travel-planner-agent-planning)
- [Week 5 — Team PoC: Travel Planner Agent (Build) + Project Kickoff](#week-5--team-poc-travel-planner-agent-build--main-project-kickoff)
- [Week 6 — Project: Architecture & Design](#week-6--main-project-architecture--design)

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


_Last updated: April 2026_
