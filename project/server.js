const express = require("express");
const app = express();

const {connectQueue} = require("./queue/rabitMQ");

const githubConnector = require("./Connectors/githubConnector");
const jiraConnector = require("./Connectors/jiraConnector");
const confluenceConnector = require("./Connectors/confluenceConnector");
const miroConnector = require("./Connectors/miroConnector");

app.use(express.json());

app.post("/webhook/github", githubConnector);
app.post("/webhook/jira", jiraConnector);
app.post("/webhook/confluence", confluenceConnector);
app.post("/webhook/miro", miroConnector);

connectQueue().then(() => {
    app.listen(3000 , () => {
        console.log("Server running on posrt 3000");
    });
});