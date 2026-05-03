const axios = require("axios");
const {hasChaned} = require("../hashStore");

module.exports = async function (data , channel) {
  const {payload} = data;

  const issue = payload.issue;
  const issueKey = issue?.key;

  if(!issue || !issueKey)
  {
    console.log("Invalid Jira payload");
    return;
  }
   
    try{
      console.log("Calling Jira enrichment API");

      const response = await axios.post(
        "http://localhost:5000/enrich/jira",
        {issueKey}
      );

      const issueDetails = response.data.issueDetails;
      const fullData =  {
           issueKey,
           summary : issueDetails.fields.summary,
           description : issueDetails.fields.description,
           status : issueDetails.fields.status?.name,
           assignee : issueDetails.fields.assignee?.displayName,
           reporter : issueDetails.fields.reporter?.displayName,
           priority : issueDetails.fields.priority?.name,
           issueType : issueDetails.fields.issueType?.name,
           project : issueDetails.fields.project?.key,
      };

      console.log("Jira Full Data:", fullData);

      if(!hasChaned(issueKey , fullData)){
        console.log("jira no change");
        return;
      }

        channel.sendToQueue(
          "normalization_queue",
          Buffer.from(
            JSON.stringify({
              source:"jira",
              payload,
              fullData
            })
          ),
          {persistent : true}
        );

        console.log("jira send to Normalization_Queue");
    }
    catch(err){
      console.error("jira error:", err.message);
    }
};