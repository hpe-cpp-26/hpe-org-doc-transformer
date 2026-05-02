const githubHandler = require("./handlers/githubHandler");
const jiraHandler = require("./handlers/jiraHandler");
const confluenceHandler = require("./handlers/confluenceHandler");
const miroHandler = require("./handlers/miroHandler");

module.exports = async function dispatch(data, channel) {
  const { source } = data;

  switch (source) {
    case "github":
      await githubHandler(data, channel);
      break;
    case "jira":
      await jiraHandler(data, channel);
      break;
    case "confluence":
      await confluenceHandler(data, channel);
      break;
    case "miro":
      await miroHandler(data, channel);
      break;
    default:
      console.log("Unknown source:", source);
  }
};