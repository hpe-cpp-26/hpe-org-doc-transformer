const { buildNormalizedEvent } = require("../schema");

module.exports = function normalizeConfluence({ payload, fullData }) {
  const eventType = payload.webhookEvent || "page_event";

  const pageUrl =
    payload.page?.links?.base && payload.page?.links?.webui
      ? `${payload.page.links.base}${payload.page.links.webui}`
      : "";

  return buildNormalizedEvent({
    id: String(fullData.pageId),
    source: "confluence",
    type: eventType,
    title: fullData.title || payload.page?.title || String(fullData.pageId),
    url: pageUrl,
    status: "N/A",
    meta: {
      version: fullData.version,
      spaceKey: payload.page?.space?.key || null,
      authorDisplayName: payload.page?.version?.by?.displayName || null,
      lastModified: payload.page?.version?.when || null,
    },
  });
};