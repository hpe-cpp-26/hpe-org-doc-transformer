const { buildNormalizedEvent } = require("../schema");

module.exports = function normalizeGithub({ payload, fullData }) {

  
  const commitMessages = (fullData.commits || [])
    .map(commit => commit.message)
    .join("\n");

  
  const changedFiles = (fullData.commits || [])
    .flatMap(commit => commit.files || [])
    .map(file => file.filename)
    .join("\n");

  
  const contentParts = [
    fullData.description,
    fullData.readmeSummary,
    ...(fullData.features || []),
    commitMessages,
    changedFiles,
  ];

  const content = contentParts
    .filter(Boolean)
    .join("\n");

  return buildNormalizedEvent({

    doc_id:
      String(payload.repository?.id || fullData.repo),

    source: "github",

    title:
      fullData.name ||
      fullData.repo ||
      "GitHub Repository",

    content,

    metadata: {
      repo: fullData.repo,

      branch:
        payload.ref?.replace("refs/heads/", "") || null,

      features:
        fullData.features || [],

      commits:
        (fullData.commits || []).map(commit => ({
          id: commit.commitId,
          message: commit.message,
          author: commit.author,
          timestamp: commit.timestamp,
        })),

      files:
        (fullData.commits || [])
          .flatMap(commit => commit.files || [])
          .map(file => ({
            filename: file.filename,
            status: file.status,
            additions: file.additions,
            deletions: file.deletions,
          })),
    },
  });
};