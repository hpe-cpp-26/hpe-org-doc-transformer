const { buildNormalizedEvent } = require("../schema");

module.exports = function normalizeGithub({ payload, fullData }) {
  const eventType =
    payload.action ||
    (payload.commits ? "push" : null) ||
    (payload.ref ? "ref_update" : null) ||
    "repository_event";

  // files from enriched commit details
  const files = (fullData.commits || []).flatMap(c =>
    (c.files || []).map(f => ({
      filename: f.filename,
      status: f.status,
      additions: f.additions ?? null,
      deletions: f.deletions ?? null,
      changes: f.changes ?? null,
      patch: f.patch || null,
    }))
  );

  // commits from enriched commit details
  const commits = (fullData.commits || []).map(c => ({
    sha: c.commitId,
    message: c.message,
    author: c.author || null,
    timestamp: c.timestamp || null,
  }));

  return buildNormalizedEvent({
    id: String(payload.repository?.id || fullData.repo),
    source: "github",
    type: eventType,
    resource: {
      id: String(payload.repository?.id || fullData.repo),
      name: fullData.repo,
      url: `https://github.com/${fullData.repo}`,
      status: "active",
    },
    actor: {
      id: String(payload.sender?.id || payload.pusher?.name || null),
      name: payload.pusher?.name || payload.sender?.login || null,
      email: payload.pusher?.email || null,
    },
    changes: {
      files,
      commits,
      fieldChanges: [],
      pageChanges: null,
      boardChanges: [],
    },
    meta: {
      branch: payload.ref?.replace("refs/heads/", "") || null,
      description: fullData.description || null,
      readmeSummary: fullData.readmeSummary || null,
      features: fullData.features || [],
    },
  });
};