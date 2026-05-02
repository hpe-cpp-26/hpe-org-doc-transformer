const axios = require("axios");
const {hasChanged} = require("../hashStore");
const {extractReadmeData} = require("../utils/readmeParser");

module.exports = async function (data , channel){
  const {payload} = data;

  const repo = payload.repository?.full_name;
  console.log("Repo received:", repo);
  if(!repo) {
    console.log("Invalid Github payload");
    return;
  }

  try{
    console.log("Calling API for full details");

    const response = await axios.post("http://localhost:4000/enrich/github" , {
      repo
    });

    console.log("ENRICHMENT RESPONSE:", Object.keys(response.data));

    const repoDetails = response.data.repoDetails;
    const readme = response.data.readme;

    console.log("=================================");
    console.log("README RECEIVED IN HANDLER:", readme?.slice(0, 100));
    console.log("=================================");



    const parsed = extractReadmeData(readme);

    console.log("PARSED README:", parsed);

    const commits = payload.commits || [];
    let commitDetails = [];

    for(const commit of commits){
      try{
         console.log("Fetching commit:", commit.id);

         const commitRes = await axios.get(
          `https://api.github.com/repos/${repo}/commits/${commit.id}`,
          {
            headers: process.env.GITHUB_TOKEN
          ? { Authorization: `Bearer ${process.env.GITHUB_TOKEN}` }
          : {},
          }
         );

         const files = (commitRes.data.files || []).map((file) => ({
          filename : file.filename,
          status : file.status,
          additions : file.additions,
          deletions : file.deletions,
          changes : file.changes,
          patch : file.patch || null , 
         }));

         commitDetails.push({
          commitId : commit.id,
          message : commit.message,
          author : commit.author?.name,
          timestamp : commit.timestamp,
          files,
         });
      }

      catch(err){
        console.log("Commit fetch failed:", err.message);
      }
    }
     
    console.log("Commit Details:" , JSON.stringify(commitDetails , null , 2));

      const fullData ={
        repo,
        name : repoDetails.name,
        description: repoDetails.description,
        readmeSummary : parsed.description,
        features : parsed.features,
        commits: commitDetails,
      };

      console.log("FINAL DATA GOING TO QUEUE:", JSON.stringify(fullData , null , 2));


      if(!hasChanged(repo , fullData)){
        console.log("Github data has not changed");
        return;
      }

      channel.sendToQueue(
        "normalization_queue" , 
        Buffer.from(
          JSON.stringify({
            source:"github", 
            payload ,
            fullData
          })
        ), 
        {persistent : true}
      );

      console.log("Github sent to Normalization_Queue");
  }
  catch(err){
    console.log("Github error:" , err.message);
  }
};