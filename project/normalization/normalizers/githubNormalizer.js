const { buildNormalizedEvent } = require("../schema");
module.exports = function normalizeGithub({ payload, fullData }) {
 
  const eventType =
    payload.action ||                     
    (payload.commits ? "push" : null) || 
    (payload.ref ? "ref_update" : null) ||
    "repository_event";

  return buildNormalizedEvent({
    id: String(fullData.id || payload.repository?.id),
    source: "github",
    type: eventType,
    title: fullData.full_name || payload.repository?.full_name,
    url: fullData.html_url || payload.repository?.html_url || "",
    status: fullData.archived
      ? "archived"
      : fullData.private
      ? "private"
      : "active",
    meta: {
      language: fullData.language,
      stars: fullData.stargazers_count,
      forks: fullData.forks_count,
      openIssues: fullData.open_issues_count,
      defaultBranch: fullData.default_branch,
      pusher: payload.pusher?.name || null,
      commitCount: payload.commits?.length ?? null,
    },
  });
};