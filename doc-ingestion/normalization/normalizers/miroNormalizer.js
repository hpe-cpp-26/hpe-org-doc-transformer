const { buildNormalizedEvent } = require("../schema");

module.exports = function normalizeMiro({ payload, fullData }) {

  const eventType =
    fullData.type ||
    payload.type ||
    "board_event";

  const contentParts = [
    payload.item?.title,
    payload.item?.text,
    payload.item?.data?.content,
  ];

  const content = contentParts
    .filter(Boolean)
    .join("\n");

  return buildNormalizedEvent({

    doc_id:
      String(fullData.boardId),

    source:
      "miro",

    title:
      payload.boardId?.name ||
      `Board ${fullData.boardId}`,

    content,

    metadata: {

      type:
        eventType,

      boardUrl:
        payload.boardId?.viewLink || "",

      createdBy: {
        id:
          payload.createdBy?.id || null,

        name:
          payload.createdBy?.name || null,

        email:
          payload.createdBy?.email || null,
      },

      item: payload.item
        ? {
            itemId:
              payload.item?.id || null,

            itemType:
              payload.item?.type || null,

            action:
              eventType.split(":")[1] || "updated",
          }
        : null,

      teamId:
        payload.teamId || null,

      boardType:
        payload.boardId?.type || null,
    },
  });
};