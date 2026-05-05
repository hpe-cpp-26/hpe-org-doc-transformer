const { hasChanged } = require("../hashStore");

module.exports = async function (data, channel) {
  const { payload } = data;

  const pageId = payload.page?.id;
  if (!pageId) return console.log("Invalid Confluence payload");

  const fullData = {
    pageId,
    title: payload.page?.title,
    version: payload.page?.version?.number
  };

  if (!hasChanged(pageId, fullData)) {
    console.log("Confluence no change");
    return;
  }

  channel.sendToQueue(
    "normalization_queue",
    Buffer.from(JSON.stringify({ ...data, fullData })),
    { persistent: true }
  );

  console.log("Confluence sent");
};