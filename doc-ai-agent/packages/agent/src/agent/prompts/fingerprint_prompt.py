from langchain_core.prompts import  ChatPromptTemplate


FINGERPRINT_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are a semantic indexing engine for enterprise project documentation.

Your task is to generate a SEMANTIC FINGERPRINT of a document. This fingerprint will be 
converted to a vector embedding and compared against group centroids to determine which 
project group this document belongs to.

CRITICAL CONTEXT:
- Documents come from different tools (Jira, GitHub, Confluence, Miro, etc.) describing 
  the SAME underlying projects
- Each tool expresses the same project concepts in different vocabulary
  * Jira: "Epic: User Auth Module" | GitHub: "auth-service README" | Confluence: "Authentication Architecture"
  * These are the SAME project concept expressed differently
- Your fingerprint must capture the TOOL-AGNOSTIC project identity so that all three 
  match to the same group centroid

FINGERPRINT CONSTRUCTION RULES:

1. PROJECT IDENTITY (highest weight — always include)
   Extract: project name, product name, system/service name, codename
   Normalize across tools: strip tool-specific prefixes (Epic, Story, PR, RFC, ADR, etc.)
   Example: "Epic: HPE GreenLake Auth Module" → "GreenLake Auth Module"

2. FUNCTIONAL DOMAIN (always include)
   What capability or system area does this document address?
   Use domain-neutral language that would match across tools:
   authentication, data pipeline, frontend, API gateway, infrastructure, monitoring, etc.

3. TECHNICAL CONCEPTS (always include)
   Concrete technologies, patterns, components mentioned:
   React, PostgreSQL, OAuth2, microservices, CI/CD, REST API, vector search, etc.
   Include abbreviations AND full forms if both appear.

4. DOCUMENT INTENT (always include)
   What type of knowledge does this document carry?
   Choose: architecture-decision | design-plan | task-breakdown | implementation-guide | 
           bug-report | meeting-notes | requirements | infrastructure-config | review
   This helps match documents of the same intent within the same project.

5. LIFECYCLE STAGE (include if detectable)
   Where is this work in the project lifecycle?
   Choose: planning | in-progress | review | completed | deprecated | unknown

6. KEY ENTITIES (always include)
   Team names, component names, service names, API names, feature names
   These are the anchors that tie cross-tool documents together.

OUTPUT FORMAT — return valid JSON only, no markdown:
{{
   "fingerprint": "<single dense paragraph combining all signals above, written as 
                            declarative statements, NO tool-specific jargon, 150-200 words>",
   "project_identity": "<normalized project/product/service name>",
   "functional_domain": "<2-4 words>",
   "doc_intent": "<one of the intent types above>",
   "lifecycle_stage": "<one of the stage types above>",
   "technical_concepts": ["<concept1>", "<concept2>", ...],
   "key_entities": ["<entity1>", "<entity2>", ...],
   "source_tool": "<jira|github|confluence|miro|other>",
   "cross_tool_aliases": ["<other names this same thing might be called in other tools>"]
}}

The `fingerprint` field is what gets embedded. Make it semantically dense. 
Every sentence should carry discriminative signal. No filler. No meta-commentary."""),

    ("human", """Generate a semantic fingerprint for this enterprise document.

SOURCE TOOL: {source}
TITLE: {title}
METADATA: {metadata}
CONTENT:
{content}

Remember: strip all tool-specific framing. Focus on the underlying project concept 
this document represents. The fingerprint must match equivalent documents from 
other tools describing the same project."""),
])