const { buildNormalizedEvent } = require("../schema");

module.exports = function normalizeJira({ payload, fullData }) {
  // 1. Identify the event type from the original webhook payload
  const eventType =
    payload.webhookEvent ||
    payload.issue_event_type_name ||
    "issue_event";

  // 2. Construct the Jira base URL from the payload
  const jiraBaseUrl = payload.issue?.self
    ? new URL(payload.issue.self).origin
    : "";

  // 3. Map changes using the changelog you attached to fullData in the handler
  const fieldChanges = (fullData.changelog || []).map(item => ({
    field: item.field,
    from: item.fromString || null,
    to: item.toString || null,
  }));

  // 4. Return the normalized schema using fullData as the primary source
  return buildNormalizedEvent({
    id: fullData.issueKey,
    source: "jira",
    type: eventType,
    resource: {
      id: fullData.issueKey,
      name: fullData.summary, // From enrichment
      url: jiraBaseUrl ? `${jiraBaseUrl}/browse/${fullData.issueKey}` : "",
      status: fullData.status || "unknown", // From enrichment
    },
    actor: {
      id: fullData.updatedBy?.accountId, // Using the updatedBy object you built in handler
      name: fullData.updatedBy?.displayName,
      email: fullData.updatedBy?.email,
    },
    changes: {
      files: [],
      commits: [],
      fieldChanges,
      pageChanges: null,
      boardChanges: [],
    },
    meta: {
  priority: fullData.priority,
  assignee: fullData.assignee,
  reporter: fullData.reporter,
  issueType: fullData.issueType,
  project: fullData.project,
  comment: fullData.comment || null,   // ← add this
}
  });
};