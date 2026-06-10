const { hasChanged } = require("../hashStore");

module.exports = async function (data, channel) {
  const { payload } = data;

  const boardId = payload.boardId?.id;
  if (!boardId) return console.log("Invalid Miro payload");

  const fullData = {
    boardId,
    type: payload.type
  };

  if (!hasChanged(boardId, fullData)) {
    console.log("Miro no change");
    return;
  }

  channel.sendToQueue(
    "normalization_queue",
    Buffer.from(JSON.stringify({ ...data, fullData })),
    { persistent: true }
  );

  console.log("Miro sent");
};