const { buildNormalizedEvent } = require("../schema");

module.exports = function normalizeMiro({ payload, fullData }) {
  const eventType = fullData.type || payload.type || "board_event";
  const boardUrl = payload.boardId?.viewLink || "";

  return buildNormalizedEvent({
    id: String(fullData.boardId),
    source: "miro",
    type: eventType,
    title: payload.boardId?.name || `Board ${fullData.boardId}`,
    url: boardUrl,
    status: "N/A",
    meta: {
      teamId: payload.teamId || null,
      itemId: payload.item?.id || null,
      itemType: payload.item?.type || null,
      createdBy: payload.createdBy?.id || null,
    },
  });
};