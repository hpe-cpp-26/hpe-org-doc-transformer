const { buildNormalizedEvent } = require("../schema");

module.exports = function normalizeConfluence({ payload, fullData }) {
  const eventType = payload.eventType || "page_event";

  return buildNormalizedEvent({
    doc_id: String(fullData.pageId),

    source: "confluence",

    title: fullData.title || "Untitled",

    content: fullData.content || "",

    metadata: {
      eventType,

      url: fullData.url || "",

      spaceKey: fullData.space || null,

      versionBefore: fullData.change?.versionBefore || null,

      versionAfter: fullData.change?.versionAfter || null,

      updatedBy: {
        id: fullData.updatedBy?.accountId || null,
        name: fullData.updatedBy?.displayName || null,
      },

      lastModified: payload.timestamp || null,
    },
  });
};