function buildNormalizedEvent({
  doc_id,
  source,
  title,
  content,
  metadata = {},
}) {

  if (!doc_id || !source || !content) {
    throw new Error(
      `Normalization error: missing required fields`
    );
  }

  return {
    doc_id,

    source,

    title: title || "Untitled",

    content,

    metadata: {
      ...metadata,

      receivedAt: new Date().toISOString(),
    },
  };
}

module.exports = { buildNormalizedEvent };