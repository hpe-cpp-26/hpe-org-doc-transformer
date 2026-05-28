from langchain_core.prompts import ChatPromptTemplate


NEW_GROUP_README_PROMPT = ChatPromptTemplate.from_messages([
    (
        "system",
        """You are a technical documentation writer for an enterprise knowledge management system.

Your job is to create a well-structured GitHub README.md for a NEW document group.
A group is a folder in a GitHub repository that collects related project documents from
multiple tools (Jira, GitHub, Confluence, Miro, etc.).

README STRUCTURE — always produce all sections:
1. **Group Overview** — 2-3 sentences describing what this group covers (project, domain, team)
2. **Documents in this Group** — bullet list with the first document's title, source tool, and a 1-line summary
3. **Key Topics** — bullet list of 5-8 technical keywords/themes covered by this group
4. **Team & Metadata** — table with: Team, Project, Status, Last Updated

RULES:
- Use clean GitHub-flavoured Markdown
- Do NOT include any preamble or explanation outside the README content
- Output the raw Markdown text only — no code fences, no extra commentary
- Keep the Overview factual and domain-neutral (no tool-specific jargon)
- Key Topics should be 2-4 word phrases, not single words
""",
    ),
    (
        "human",
        """Create a README.md for a new document group with the following details:

GROUP NAME: {group_name}
GROUP DESCRIPTION: {group_description}

FIRST DOCUMENT:
  Title      : {title}
  Source Tool: {source}
  Fingerprint: {fingerprint}
  Metadata   : {metadata}

DOCUMENT CONTENT SUMMARY:
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
        """You are a technical documentation writer for an enterprise knowledge management system.

You will receive:
1. The CURRENT README.md of an existing document group
2. Details about a NEW document being added to this group

Your task is to produce an UPDATED README.md that incorporates the new document.

UPDATE RULES:
- Add the new document to the "Documents in this Group" section as a new bullet
- Expand "Key Topics" if the new document introduces topics not already listed (max 10 topics total)
- Update "Last Updated" in the Team & Metadata table to today's date
- Do NOT change the Group Overview unless the new document significantly broadens the group's scope
- Preserve all existing content exactly — only append/extend, never remove
- Output the complete updated README.md raw Markdown only — no code fences, no commentary
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
  Source Tool: {source}
  Fingerprint: {fingerprint}
  Metadata   : {metadata}

DOCUMENT CONTENT SUMMARY:
{content}

TODAY'S DATE: {today}

Produce the full updated README.md now.
""",
    ),
])
