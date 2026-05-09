const {pushToQueue} = require("../queue/rabitMQ");

module.exports = async function githubConnector(req , res){
    try{
        await pushToQueue({
            source:"github",
            payload: req.body
        });

        res.sendStatus(200);
    }
    catch(err){
        console.error("Github Error:" , err);
        res.sendStatus(500);
    }
};