const { hasChanged } = require("../hashStore");

module.exports = async function (data, channel) {
  const { payload } = data;

  const issueKey = payload.issue?.key;
  if (!issueKey) return console.log("Invalid Jira payload");

  const fullData = {
    issueKey,
    summary: payload.issue?.fields?.summary,
    status: payload.issue?.fields?.status?.name
  };

  if (!hasChanged(issueKey, fullData)) {
    console.log("Jira no change");
    return;
  }

  channel.sendToQueue(
    "normalization_queue",
    Buffer.from(JSON.stringify({ ...data, fullData })),
    { persistent: true }
  );

  console.log("Jira sent");
};