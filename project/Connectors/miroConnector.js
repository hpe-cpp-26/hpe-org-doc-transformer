const {pushToQueue} = require("../queue/rabitMQ");

const debounceMap = new Map();

module.exports = async function miroConnector(req , res) {
    try{
        const payload = req.body;
        const boardId = payload.boardId?.id;

        if(!boardId){
            return res.sendStataus(400);
        }

        if(debounceMap.has(boardId)){
            clearTimeout(debounceMap.get(boardId));
        }

        //here we are setting new timeout for next 5 seconds

        const timeout = setTimeout(async () =>{
            await pushToQueue({
                source:"miro",
                payload
            });

            debounceMap.delete(boardId);
        } , 5000);

        debounceMap.set(boardId , timeout);
    }
    catch(err){
        console.error("miro error:" , err);
        res.sendStatus(500);
    }
};