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
    resource: {
      id: String(fullData.pageId),
      name: fullData.title || payload.page?.title || String(fullData.pageId),
      url: pageUrl,
      status: "N/A",
    },
    actor: {
      id: payload.page?.version?.by?.accountId || null,
      name: payload.page?.version?.by?.displayName || null,
      email: payload.page?.version?.by?.email || null,
    },
    changes: {
      files: [],
      commits: [],
      fieldChanges: [],
      pageChanges: {
        versionBefore: (fullData.version || 1) - 1,
        versionAfter: fullData.version || 1,
        spaceKey: payload.page?.space?.key || null,
        diffUrl: pageUrl ? `${pageUrl}?diff` : null,
      },
      boardChanges: [],
    },
    meta: {
      spaceKey: payload.page?.space?.key || null,
      parentPageId: payload.page?.ancestors?.[0]?.id || null,
      lastModified: payload.page?.version?.when || null,
    },
  });
};