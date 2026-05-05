const axios = require("axios");
const { hasChanged } = require("../hashStore");

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
      const fullData = {
        issueKey,
        summary: issueDetails.fields.summary,
        description: issueDetails.fields.description,
        status: issueDetails.fields.status?.name,
        assignee: issueDetails.fields.assignee?.displayName,
        reporter: issueDetails.fields.reporter?.displayName,
        priority: issueDetails.fields.priority?.name,
        issueType: issueDetails.fields.issuetype?.name,
        project: issueDetails.fields.project?.key,
        labels: issueDetails.fields.labels || [],
        dueDate: issueDetails.fields.duedate || null,
        updatedBy: {
       accountId: payload.comment?.author?.accountId || payload.user?.accountId || null,
       displayName: payload.comment?.author?.displayName || payload.user?.displayName || null,
       email: payload.comment?.author?.emailAddress || payload.user?.emailAddress || null,
       
},
       comment: payload.comment ? {
       id: payload.comment.id,
       body: payload.comment.body,
       author: payload.comment.author?.displayName || null,
      created: payload.comment.created,
      } : null,

        changelog: payload.changelog?.items || [],  
      };

      console.log("Jira Full Data:", fullData);

      if(!hasChanged(issueKey , fullData)){
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