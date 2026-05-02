function buildNormalizedEvent({ id, source, type, title, url, status = "N/A", meta = {} }) {
  if (!id || !source || !type || !title) {
    throw new Error(
      `Normalization error: missing required fields — id=${id}, source=${source}, type=${type}, title=${title}`
    );
  }
 
  return {
    id,
    source,
    type,
    title,
    url: url || "",
    status,
    meta,
    receivedAt: new Date().toISOString(),
  };
}
 
module.exports = { buildNormalizedEvent };