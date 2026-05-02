const {pushToQueue} = require("../queue/rabitMQ");

module.exports = async function jiraConnector(req, res){
    console.log("JIRA hit");

    try{
        await pushToQueue({
            source:"jira", 
            payload: req.body
        });

        console.log("Jira sent to Queue");

        res.sendStatus(200);
    }
    catch(err){
        console.log("Jira Error:", err);
        res.sendStatus(500);
    }
};