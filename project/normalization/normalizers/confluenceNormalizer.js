const { buildNormalizedEvent } = require("../schema");

module.exports = function normalizeConfluence({ payload, fullData }) {
  const eventType = payload.eventType || "page_event";

  return buildNormalizedEvent({
    id: String(fullData.pageId),
    source: "confluence",
    type: eventType,

    resource: {
      id: String(fullData.pageId),
      name: fullData.title || String(fullData.pageId),
      url: fullData.url || "",
      status: "active",
    },

    actor: {
      id: fullData.updatedBy?.accountId || null,
      name: fullData.updatedBy?.displayName || null,
      email: null,
    },

    changes: {
      files: [],
      commits: [],
      fieldChanges: [],
      pageChanges: {
        versionBefore: fullData.change?.versionBefore,
        versionAfter: fullData.change?.versionAfter,
        spaceKey: fullData.space || null,
        diffUrl: fullData.url ? `${fullData.url}?diff` : null,
      },
      boardChanges: [],
    },

    meta: {
      spaceKey: fullData.space || null,
      parentPageId: null,
      lastModified: payload.timestamp || null,
    },
  });
};