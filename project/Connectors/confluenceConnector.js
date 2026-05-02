const {pushToQueue} = require("../queue/rabitMQ");

module.exports = async function confluenceConnector(req, res){
    try{
        await pushToQueue({
            source:"confluence", 
            payload: req.body
        });

        res.sendStatus(200);
    }
    catch(err){
        console.log("Confluence error:", err);
        res.sendStatus(500);
    }
}