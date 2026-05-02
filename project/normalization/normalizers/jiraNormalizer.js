const { buildNormalizedEvent } = require("../schema");

module.exports = function normalizeJira({ payload, fullData }) {
  const eventType =
    payload.webhookEvent ||
    payload.issue_event_type_name ||
    "issue_event";

  const jiraBaseUrl = payload.issue?.self
    ? new URL(payload.issue.self).origin
    : "";

  return buildNormalizedEvent({
    id: fullData.issueKey,
    source: "jira",
    type: eventType,
    title: fullData.summary || payload.issue?.fields?.summary || fullData.issueKey,
    url: jiraBaseUrl ? `${jiraBaseUrl}/browse/${fullData.issueKey}` : "",
    status: fullData.status || "unknown",
    meta: {
      priority: payload.issue?.fields?.priority?.name || null,
      assignee: payload.issue?.fields?.assignee?.displayName || null,
      reporter: payload.issue?.fields?.reporter?.displayName || null,
      issueType: payload.issue?.fields?.issuetype?.name || null,
      project: payload.issue?.fields?.project?.key || null,
    },
  });
};