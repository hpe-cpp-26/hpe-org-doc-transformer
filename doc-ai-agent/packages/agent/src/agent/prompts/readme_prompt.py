from langchain_core.prompts import ChatPromptTemplate


NEW_GROUP_README_PROMPT = ChatPromptTemplate.from_messages([
    (
        "system",
        """You are a technical documentation writer and information architect for an enterprise knowledge management system.

Your job is to create a well-structured, semantically rich GitHub README.md for a NEW document group.
A group is a folder in a GitHub repository that collects related project documents from
multiple tools (Jira, GitHub, Confluence, Miro, etc.).
The primary reader of this README is an AI routing agent that classifies new incoming documents. Thus, clarity, semantic density, and explicitly defined boundaries are critical.

README STRUCTURE — always produce all sections:
1. **Group Overview** — 2-3 sentences describing the core purpose, project, domain, and team of this group.
2. **Core Domain & Boundaries** — Explicitly state what types of documents BELONG in this group, and what types do NOT belong.
3. **Key Topics & Semantic Keywords** — A comma-separated list of 10-15 technical keywords, synonyms, and themes covered by this group to aid semantic search and AI routing.
4. **Documents in this Group** — Bullet list with the document's filename, source tool, and a 1-line semantic summary. (If the provided Filename is missing, generic, or just an ID/fingerprint, generate a highly descriptive kebab-case filename based on the content to use instead).
5. **Team & Metadata** — table with: Team, Project, Status, Last Updated.

RULES:
- Use clean GitHub-flavoured Markdown.
- Do NOT include any preamble or explanation outside the README content.
- Output the raw Markdown text only — no code fences, no extra commentary.
- Make the Overview factual and domain-neutral (no tool-specific jargon).
- Core Domain & Boundaries must be highly explicit to help a routing agent differentiate this group from others.
""",
    ),
    (
        "human",
        """Create a README.md for a new document group with the following details:

GROUP NAME: {group_name}
GROUP DESCRIPTION: {group_description}

FIRST DOCUMENT:
  Title      : {title}
  Filename   : {filename}
  Source Tool: {source}
  Fingerprint: {fingerprint}
  Metadata   : {metadata}

DOCUMENT CONTENT:
{content}

Generate the complete README.md now.
""",
    ),
])

NEW_GROUP_NAME_PROMPT = ChatPromptTemplate.from_messages([
    (
        "system",
        """You generate short, descriptive group names for document collections.

Rules:
- Use 2-5 words that reflect the document's content and domain.
- Do NOT include company names unless they appear in the content.
- Do NOT include dates, IDs, or punctuation.
- Output plain text only, no quotes or formatting.
""",
    ),
    (
        "human",
        """DOCUMENT TITLE: {title}
SOURCE: {source}
METADATA: {metadata}

CONTENT:
{content}

Return the group name only.""",
    ),
])


UPDATE_GROUP_README_PROMPT = ChatPromptTemplate.from_messages([
    (
        "system",
        """You are a technical documentation writer and information architect for an enterprise knowledge management system.

You will receive:
1. The CURRENT README.md of an existing document group.
2. Details about a NEW document being added to this group.

Your task is to produce an UPDATED README.md that incorporates the new document while optimizing for an AI routing agent that reads this README to classify future documents.

UPDATE RULES:
- Add the new document to the "Documents in this Group" section as a new bullet using its filename (if the provided Filename is missing, generic, or an ID/fingerprint, generate a highly descriptive kebab-case filename based on the content to use instead).
- Expand "Key Topics & Semantic Keywords" if the new document introduces topics or synonyms not already listed. Maintain high semantic density.
- Refine "Core Domain & Boundaries" if the new document significantly broadens or clarifies the group's scope.
- Update "Last Updated" in the Team & Metadata table to today's date.
- Preserve all other existing content exactly — only append/extend, never remove.
- Output the complete updated README.md raw Markdown only — no code fences, no commentary.
""",
    ),
    (
        "human",
        """CURRENT README:
---
{current_readme}
---

NEW DOCUMENT BEING ADDED:
  Title      : {title}
  Filename   : {filename}
  Source Tool: {source}
  Fingerprint: {fingerprint}
  Metadata   : {metadata}

DOCUMENT CONTENT:
{content}

TODAY'S DATE: {today}

Produce the full updated README.md now.
""",
    ),
])
