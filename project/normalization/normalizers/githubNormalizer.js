const { buildNormalizedEvent } = require("../schema");

function extractChangedLines(patch) {
  if (!patch) return null;

  return patch
    .split("\n")
    .filter(line => line.startsWith("+") && !line.startsWith("+++"))
    .map(line => line.slice(1).trim())
    .filter(Boolean)
    .join(" ");
}

module.exports = function normalizeGithub({ payload, fullData }) {

  const changedFilesContent = (fullData.commits || [])
    .flatMap(commit => commit.files || [])
    .filter(file => file.patch)
    .map(file => {
      const changed = extractChangedLines(file.patch);
      return changed ? `FILE: ${file.filename}\n${changed}` : null;
    })
    .filter(Boolean)
    .join("\n\n");

  const contentParts = [
    fullData.description,
    changedFilesContent,
  ];

  const content = contentParts
    .filter(Boolean)
    .join("\n");

  return buildNormalizedEvent({
    doc_id: String(payload.repository?.id || fullData.repo),
    source: "github",
    title: fullData.name || fullData.repo || "GitHub Repository",
    content,
    metadata: {
      repo: fullData.repo,
      branch: payload.ref?.replace("refs/heads/", "") || null,
      features: fullData.features || [],
      commits: (fullData.commits || []).map(commit => ({
        id: commit.commitId,
        message: commit.message,
        author: commit.author,
        timestamp: commit.timestamp,
      })),
      files: (fullData.commits || [])
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