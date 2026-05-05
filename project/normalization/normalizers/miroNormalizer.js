const { buildNormalizedEvent } = require("../schema");

module.exports = function normalizeMiro({ payload, fullData }) {
  const eventType = fullData.type || payload.type || "board_event";
  const boardUrl = payload.boardId?.viewLink || "";

  return buildNormalizedEvent({
    id: String(fullData.boardId),
    source: "miro",
    type: eventType,
    resource: {
      id: String(fullData.boardId),
      name: payload.boardId?.name || `Board ${fullData.boardId}`,
      url: boardUrl,
      status: "N/A",
    },
    actor: {
      id: payload.createdBy?.id || null,
      name: payload.createdBy?.name || null,
      email: payload.createdBy?.email || null,
    },
    changes: {
      files: [],
      commits: [],
      fieldChanges: [],
      pageChanges: null,
      boardChanges: payload.item
        ? [
            {
              itemId: payload.item?.id || null,
              itemType: payload.item?.type || null,
              action: eventType.split(":")[1] || "updated",
            },
          ]
        : [],
    },
    meta: {
      teamId: payload.teamId || null,
      boardType: payload.boardId?.type || null,
    },
  });
};