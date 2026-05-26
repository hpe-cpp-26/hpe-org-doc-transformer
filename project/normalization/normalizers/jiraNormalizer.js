const { buildNormalizedEvent } = require("../schema");

module.exports = function normalizeJira({ payload, fullData }) {

  
  const changelogText = (fullData.changelog || [])
    .map(change =>
      `${change.field}: ${change.fromString || "empty"} -> ${change.toString || "empty"}`
    )
    .join("\n");


  const contentParts = [
    fullData.summary,
    fullData.description,
    changelogText,
  ];

  const content = contentParts
    .filter(Boolean)
    .join("\n");

  return buildNormalizedEvent({

    doc_id:
      fullData.issueKey,

    source: "jira",

    title:
      fullData.summary ||
      fullData.issueKey ||
      "Jira Issue",

    content,

    metadata: {

      status:
        fullData.status || null,

      assignee:
        fullData.assignee || null,

      reporter:
        fullData.reporter || null,

      priority:
        fullData.priority || null,

      issueType:
        fullData.issueType || null,

      project:
        fullData.project || null,

      labels:
        fullData.labels || [],

      dueDate:
        fullData.dueDate || null,

      updatedBy:
        fullData.updatedBy || null,

      changelog:
        fullData.changelog || [],
    },
  });
};