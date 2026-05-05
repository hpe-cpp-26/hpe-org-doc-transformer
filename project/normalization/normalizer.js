const normalizeGithub = require("./normalizers/githubNormalizer.js");
const normalizeJira = require("./normalizers/jiraNormalizer.js");
const normalizeConfluence = require("./normalizers/confluenceNormalizer");
const normalizeMiro = require("./normalizers/miroNormalizer");

const normalizers = {
  github: normalizeGithub,
  jira: normalizeJira,
  confluence: normalizeConfluence,
  miro: normalizeMiro,
};

function normalize(data) {
  const { source } = data;
  const normalizer = normalizers[source];

  if (!normalizer) {
    throw new Error(`No normalizer registered for source: "${source}"`);
  }

  return normalizer(data);
}

module.exports = { normalize };